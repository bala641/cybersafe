"""
REST API Server
Provides HTTP API for network monitoring data and control
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.packet_capture import PacketCapture
from core.threat_detector import ThreatDetector
from core.port_monitor import PortMonitor
from core.protocol_analyzer import ProtocolAnalyzer
from utils.logger import Logger
from database.models import DatabaseManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cybersafe-secret-key-change-in-production'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances
capture = None
threat_detector = None
port_monitor = None
protocol_analyzer = None
logger = None
db_manager = None

# Monitoring state
monitoring_active = False
monitoring_thread = None


def initialize_components(config: dict = None):
    """Initialize all monitoring components"""
    global capture, threat_detector, port_monitor, protocol_analyzer, logger, db_manager
    
    capture = PacketCapture()
    threat_detector = ThreatDetector(config)
    port_monitor = PortMonitor()
    protocol_analyzer = ProtocolAnalyzer()
    logger = Logger()
    db_manager = DatabaseManager()
    
    # Register packet callback
    capture.register_callback(process_packet)
    
    print("Components initialized")


def process_packet(packet_info: dict):
    """Process captured packet"""
    global threat_detector, port_monitor, protocol_analyzer, socketio
    
    try:
        # Analyze protocol
        protocol_info = protocol_analyzer.analyze(packet_info)
        packet_info['analysis'] = protocol_info
        
        # Update port monitor
        port_monitor.update_from_packet(packet_info)
        
        # Detect threats
        threats = threat_detector.analyze_packet(packet_info)
        if threats:
            packet_info['threats'] = threats
            
            # Emit threat alerts via WebSocket
            for threat in threats:
                socketio.emit('threat_detected', threat, broadcast=True)
                logger.log_threat(threat)
        
        # Emit packet via WebSocket
        socketio.emit('packet_captured', {
            'number': packet_info['number'],
            'timestamp': packet_info['timestamp'].isoformat(),
            'protocol': packet_info.get('protocol_name'),
            'src': packet_info.get('src_ip', packet_info.get('src_mac')),
            'dst': packet_info.get('dst_ip', packet_info.get('dst_mac')),
            'length': packet_info['length'],
            'summary': packet_info.get('summary', '')
        }, broadcast=True)
        
        # Log to database (in batches for performance)
        db_manager.queue_packet(packet_info)
    
    except Exception as e:
        print(f"Error processing packet: {e}")


# ============================================================================
# API Routes
# ============================================================================

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'monitoring_active': monitoring_active,
        'capture_active': capture.is_active() if capture else False,
        'interface': capture.interface if capture else None,
        'stats': capture.get_stats() if capture else {}
    })


@app.route('/api/interfaces', methods=['GET'])
def get_interfaces():
    """Get available network interfaces"""
    interfaces = PacketCapture.get_available_interfaces()
    return jsonify(interfaces)


@app.route('/api/start', methods=['POST'])
def start_monitoring():
    """Start packet capture and monitoring"""
    global monitoring_active
    
    if monitoring_active:
        return jsonify({'error': 'Monitoring already active'}), 400
    
    data = request.json or {}
    interface = data.get('interface')
    filter_str = data.get('filter', '')
    
    if interface:
        capture.interface = interface
    
    capture.filter_str = filter_str
    
    success = capture.start()
    
    if success:
        monitoring_active = True
        return jsonify({'message': 'Monitoring started', 'interface': capture.interface})
    else:
        return jsonify({'error': 'Failed to start monitoring'}), 500


@app.route('/api/stop', methods=['POST'])
def stop_monitoring():
    """Stop packet capture"""
    global monitoring_active
    
    if not monitoring_active:
        return jsonify({'error': 'Monitoring not active'}), 400
    
    capture.stop()
    monitoring_active = False
    
    return jsonify({'message': 'Monitoring stopped'})


@app.route('/api/packets', methods=['GET'])
def get_packets():
    """Get captured packets"""
    count = request.args.get('count', 100, type=int)
    packets = capture.get_packets_batch(count)
    
    # Convert to JSON-serializable format
    packet_list = []
    for p in packets:
        packet_list.append({
            'number': p['number'],
            'timestamp': p['timestamp'].isoformat(),
            'protocol': p.get('protocol_name'),
            'src_ip': p.get('src_ip'),
            'dst_ip': p.get('dst_ip'),
            'src_port': p.get('src_port'),
            'dst_port': p.get('dst_port'),
            'length': p['length'],
            'summary': p.get('summary', '')
        })
    
    return jsonify(packet_list)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get comprehensive statistics"""
    return jsonify({
        'capture': capture.get_stats() if capture else {},
        'threats': threat_detector.get_stats() if threat_detector else {},
        'ports': port_monitor.get_stats() if port_monitor else {},
        'protocols': protocol_analyzer.get_stats() if protocol_analyzer else {},
        'network_io': port_monitor.get_network_io_stats() if port_monitor else {}
    })


@app.route('/api/threats', methods=['GET'])
def get_threats():
    """Get detected threats"""
    count = request.args.get('count', 100, type=int)
    threat_type = request.args.get('type')
    
    threats = threat_detector.get_threats(count, threat_type)
    
    # Convert to JSON-serializable
    threat_list = []
    for t in threats:
        threat_dict = t.copy()
        if 'timestamp' in threat_dict:
            threat_dict['timestamp'] = threat_dict['timestamp'].isoformat()
        threat_list.append(threat_dict)
    
    return jsonify(threat_list)


@app.route('/api/ports', methods=['GET'])
def get_ports():
    """Get port information"""
    # Scan current connections
    port_monitor.scan_connections()
    
    return jsonify({
        'listening': [
            {
                'port': p.get('local_port'),
                'process': p.get('process_name'),
                'pid': p.get('pid'),
                'ip': p.get('local_ip')
            }
            for p in port_monitor.get_listening_ports()
        ],
        'connections': [
            {
                'local_port': c.get('local_port'),
                'remote_ip': c.get('remote_ip'),
                'remote_port': c.get('remote_port'),
                'status': c.get('status'),
                'process': c.get('process_name')
            }
            for c in port_monitor.get_active_connections()[:50]  # Limit results
        ]
    })


@app.route('/api/ports/<int:port>', methods=['GET'])
def get_port_info(port):
    """Get information about specific port"""
    connections = port_monitor.get_connection_by_port(port)
    stats = port_monitor.get_port_stats(port)
    
    return jsonify({
        'port': port,
        'in_use': port_monitor.is_port_in_use(port),
        'process': port_monitor.get_process_by_port(port),
        'connections': connections[:10],  # Limit
        'stats': stats
    })


@app.route('/api/protocols', methods=['GET'])
def get_protocols():
    """Get protocol distribution"""
    return jsonify(protocol_analyzer.get_protocol_distribution())


@app.route('/api/export', methods=['POST'])
def export_data():
    """Export captured data"""
    data = request.json or {}
    format_type = data.get('format', 'json')  # json, csv, pcap
    
    # TODO: Implement export functionality
    return jsonify({'message': 'Export functionality coming soon'}), 501


@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get or update configuration"""
    if request.method == 'GET':
        # Return current config
        return jsonify({
            'interface': capture.interface if capture else None,
            'filter': capture.filter_str if capture else '',
            'threat_detection': threat_detector.config if threat_detector else {}
        })
    else:
        # Update config
        data = request.json or {}
        # TODO: Implement config update
        return jsonify({'message': 'Configuration updated'})


@app.route('/api/reset', methods=['POST'])
def reset_stats():
    """Reset statistics"""
    if capture:
        capture.reset_stats()
        capture.clear_queue()
    
    if threat_detector:
        threat_detector.reset()
    
    if port_monitor:
        port_monitor.reset_stats()
    
    if protocol_analyzer:
        protocol_analyzer.reset_stats()
    
    return jsonify({'message': 'Statistics reset'})


# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to CyberSafe API'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')


@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to specific events"""
    print(f'Client subscribed: {data}')
    emit('subscribed', {'status': 'success'})


# ============================================================================
# Main
# ============================================================================

def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the API server"""
    initialize_components()
    
    print("=" * 50)
    print("CyberSafe API Server")
    print("=" * 50)
    print(f"Server: http://{host}:{port}")
    print(f"API Docs: http://{host}:{port}/api/status")
    print("=" * 50)
    
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='CyberSafe API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port, debug=args.debug)
