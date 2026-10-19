"""
CyberSafe Network Monitor - Main Entry Point
Cross-platform network traffic monitoring and threat detection
"""

import sys
import argparse
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(
        description='CyberSafe - Network Traffic Monitoring and Threat Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Start with GUI
  python main.py --gui

  # Start with CLI monitoring
  python main.py --cli

  # Start API server
  python main.py --api

  # Monitor specific interface
  python main.py --interface eth0 --gui

  # Enable threat detection
  python main.py --threats --gui

  # Capture to file
  python main.py --output capture.pcap

For more information: https://github.com/cybersafe-monitor
        '''
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--gui', action='store_true', 
                           help='Start with graphical user interface')
    mode_group.add_argument('--cli', action='store_true',
                           help='Start with command-line interface')
    mode_group.add_argument('--api', action='store_true',
                           help='Start API server only')
    
    # Network configuration
    parser.add_argument('-i', '--interface', type=str, default=None,
                       help='Network interface to monitor (default: auto-detect)')
    parser.add_argument('-f', '--filter', type=str, default='',
                       help='BPF packet filter (e.g., "tcp port 80")')
    
    # Features
    parser.add_argument('--threats', action='store_true',
                       help='Enable threat detection')
    parser.add_argument('--no-threats', action='store_true',
                       help='Disable threat detection')
    
    # Output
    parser.add_argument('-o', '--output', type=str,
                       help='Output file for packet capture (PCAP format)')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Logging level')
    
    # API server settings
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='API server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                       help='API server port (default: 5000)')
    
    # Configuration
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Configuration file path')
    
    # Utility commands
    parser.add_argument('--list-interfaces', action='store_true',
                       help='List available network interfaces and exit')
    parser.add_argument('--version', action='store_true',
                       help='Show version and exit')
    
    args = parser.parse_args()
    
    # Handle utility commands
    if args.version:
        print("CyberSafe Network Monitor v1.0.0")
        print("Advanced network traffic monitoring and threat detection")
        return 0
    
    if args.list_interfaces:
        from core.packet_capture import PacketCapture
        print("Available Network Interfaces:")
        print("=" * 60)
        interfaces = PacketCapture.get_available_interfaces()
        for name, info in interfaces.items():
            print(f"\n{name}:")
            print(f"  IP: {info.get('ip', 'N/A')}")
            print(f"  MAC: {info.get('mac', 'N/A')}")
            print(f"  Netmask: {info.get('netmask', 'N/A')}")
            print(f"  Status: {info.get('status', 'N/A')}")
        return 0
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command-line arguments
    if args.interface:
        config['network']['interface'] = args.interface
    if args.filter:
        config['capture']['capture_filter'] = args.filter
    if args.threats:
        config['threats']['enabled'] = True
    if args.no_threats:
        config['threats']['enabled'] = False
    if args.log_level:
        config['logging']['level'] = args.log_level
    
    # Determine mode
    if args.api:
        return run_api_server(config, args.host, args.port)
    elif args.gui:
        return run_gui(config, args)
    elif args.cli:
        return run_cli(config, args)
    else:
        # Default to GUI if available, otherwise CLI
        try:
            return run_gui(config, args)
        except ImportError:
            print("GUI not available, starting CLI mode...")
            return run_cli(config, args)


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    try:
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Config file '{config_path}' not found, using defaults")
        return get_default_config()
    except Exception as e:
        print(f"Warning: Error loading config: {e}, using defaults")
        return get_default_config()


def get_default_config() -> dict:
    """Get default configuration"""
    return {
        'network': {'interface': 'auto', 'promiscuous_mode': True},
        'capture': {'max_packets': 10000, 'capture_filter': ''},
        'threats': {'enabled': True, 'sensitivity': 'medium'},
        'logging': {'level': 'INFO'},
        'api': {'enabled': True, 'host': '0.0.0.0', 'port': 5000}
    }


def run_api_server(config: dict, host: str, port: int):
    """Run API server"""
    print("Starting CyberSafe API Server...")
    print(f"Server will be available at http://{host}:{port}")
    
    from api.server import run_server
    run_server(host=host, port=port, debug=False)
    return 0


def run_gui(config: dict, args):
    """Run GUI application"""
    print("Starting CyberSafe GUI...")
    
    try:
        from gui.desktop_app import CyberSafeGUI
        
        app = CyberSafeGUI(config)
        app.run()
        return 0
    
    except ImportError as e:
        print(f"Error: GUI dependencies not installed: {e}")
        print("Install with: pip install customtkinter pillow")
        return 1


def run_cli(config: dict, args):
    """Run CLI application"""
    print("=" * 70)
    print("CyberSafe Network Monitor - CLI Mode")
    print("=" * 70)
    
    from core.packet_capture import PacketCapture
    from core.threat_detector import ThreatDetector
    from core.port_monitor import PortMonitor
    from utils.logger import Logger
    
    # Initialize components
    logger = Logger(level=config['logging']['level'])
    capture = PacketCapture(
        interface=config['network'].get('interface'),
        filter_str=config['capture'].get('capture_filter', ''),
        promiscuous=config['network'].get('promiscuous_mode', True)
    )
    
    threat_detector = None
    if config['threats']['enabled']:
        threat_detector = ThreatDetector(config['threats'])
        print("Threat detection: ENABLED")
    
    port_monitor = PortMonitor()
    
    # Packet callback
    def packet_callback(packet_info):
        protocol = packet_info.get('protocol_name', 'UNKNOWN')
        src = packet_info.get('src_ip', packet_info.get('src_mac', 'N/A'))
        dst = packet_info.get('dst_ip', packet_info.get('dst_mac', 'N/A'))
        
        # Display packet
        print(f"[{packet_info['number']:6d}] {protocol:6s} {src:15s} -> {dst:15s} ({packet_info['length']} bytes)")
        
        # Update monitors
        port_monitor.update_from_packet(packet_info)
        
        # Check for threats
        if threat_detector:
            threats = threat_detector.analyze_packet(packet_info)
            for threat in threats:
                print(f"  ⚠️  THREAT: [{threat['severity']}] {threat['type']} - {threat['description']}")
                logger.log_threat(threat)
    
    capture.register_callback(packet_callback)
    
    print(f"\nInterface: {capture.interface}")
    if config['capture'].get('capture_filter'):
        print(f"Filter: {config['capture']['capture_filter']}")
    print("\nStarting packet capture... (Press Ctrl+C to stop)\n")
    
    try:
        capture.start()
        
        # Keep running and display stats periodically
        import time
        last_stats_time = time.time()
        
        while capture.is_active():
            time.sleep(1)
            
            # Display stats every 10 seconds
            if time.time() - last_stats_time >= 10:
                stats = capture.get_stats()
                print(f"\n{'='*70}")
                print(f"Stats: {stats['total_packets']} packets, "
                      f"{stats['bytes_total']/1024:.2f} KB, "
                      f"{stats.get('packets_per_second', 0):.2f} pkt/s")
                
                if threat_detector:
                    threat_stats = threat_detector.get_stats()
                    if threat_stats['total_threats'] > 0:
                        print(f"Threats: {threat_stats['total_threats']} detected")
                        for threat_type, count in threat_stats['by_type'].items():
                            print(f"  {threat_type}: {count}")
                
                print(f"{'='*70}\n")
                last_stats_time = time.time()
    
    except KeyboardInterrupt:
        print("\n\nStopping capture...")
    
    finally:
        capture.stop()
        
        # Final statistics
        print("\n" + "=" * 70)
        print("Final Statistics")
        print("=" * 70)
        
        stats = capture.get_stats()
        print(f"Total Packets: {stats['total_packets']}")
        print(f"  TCP: {stats['tcp_packets']}")
        print(f"  UDP: {stats['udp_packets']}")
        print(f"  ICMP: {stats['icmp_packets']}")
        print(f"  Other: {stats['other_packets']}")
        print(f"Total Bytes: {stats['bytes_total']:,}")
        print(f"Duration: {stats.get('duration_seconds', 0):.2f}s")
        print(f"Avg Rate: {stats.get('packets_per_second', 0):.2f} pkt/s")
        
        if threat_detector:
            threat_stats = threat_detector.get_stats()
            print(f"\nThreats Detected: {threat_stats['total_threats']}")
            if threat_stats['by_type']:
                for threat_type, count in threat_stats['by_type'].items():
                    print(f"  {threat_type}: {count}")
        
        print("\nLogs saved to ./logs/")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


def run_demo_mode():
    """Run application in demo mode with simulated data"""
    print("Starting CyberSafe in Demo Mode...")
    print("This mode uses simulated data - no admin/Npcap required!\n")
    
    try:
        import demo_mode
        demo_mode.run_modern_demo()
        return 0
    except ImportError as e:
        print(f"Error: Could not start demo mode: {e}")
        return 1
