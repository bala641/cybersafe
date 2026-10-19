"""
Threat Detection Engine
Inspired by Suricata and Zeek's threat detection capabilities
"""

from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Set, Optional
import threading
import re


class ThreatDetector:
    """
    Advanced threat detection engine with multiple detection strategies
    """
    
    # Known malicious patterns
    MALICIOUS_USER_AGENTS = [
        'sqlmap', 'nikto', 'nmap', 'masscan', 'metasploit',
        'havij', 'acunetix', 'nessus', 'openvas'
    ]
    
    SUSPICIOUS_PORTS = {
        23: 'Telnet',
        135: 'MS RPC',
        139: 'NetBIOS',
        445: 'SMB',
        1433: 'MS SQL',
        3306: 'MySQL',
        3389: 'RDP',
        5432: 'PostgreSQL',
        5900: 'VNC',
        6379: 'Redis',
        27017: 'MongoDB'
    }
    
    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        
        # Detection state tracking
        self.lock = threading.Lock()
        
        # Port scan detection
        self.port_scan_tracker = defaultdict(lambda: {
            'ports': set(),
            'timestamps': deque(maxlen=100)
        })
        
        # SYN flood detection
        self.syn_tracker = defaultdict(lambda: deque(maxlen=1000))
        
        # Connection tracking
        self.connection_tracker = defaultdict(lambda: {
            'count': 0,
            'bytes': 0,
            'timestamps': deque(maxlen=100)
        })
        
        # Failed authentication tracking
        self.auth_failure_tracker = defaultdict(lambda: deque(maxlen=100))
        
        # Data exfiltration tracking
        self.data_transfer_tracker = defaultdict(lambda: {
            'bytes_sent': 0,
            'bytes_received': 0,
            'connections': set()
        })
        
        # Detected threats
        self.threats = deque(maxlen=1000)
        self.threat_stats = defaultdict(int)
        
    def _default_config(self) -> dict:
        """Default threat detection configuration"""
        return {
            'port_scan': {
                'enabled': True,
                'threshold': 20,
                'time_window': 10
            },
            'syn_flood': {
                'enabled': True,
                'threshold': 100,
                'time_window': 1
            },
            'ddos': {
                'enabled': True,
                'packet_threshold': 1000,
                'connection_threshold': 100
            },
            'brute_force': {
                'enabled': True,
                'failed_attempts': 5,
                'time_window': 60
            },
            'exfiltration': {
                'enabled': True,
                'data_threshold': 100 * 1024 * 1024,  # 100 MB
                'connection_threshold': 10
            }
        }
    
    def analyze_packet(self, packet_info: dict) -> List[dict]:
        """
        Analyze a packet for threats
        Returns list of detected threats
        """
        threats = []
        
        with self.lock:
            # Port scan detection
            if self.config['port_scan']['enabled']:
                threat = self._detect_port_scan(packet_info)
                if threat:
                    threats.append(threat)
            
            # SYN flood detection
            if self.config['syn_flood']['enabled']:
                threat = self._detect_syn_flood(packet_info)
                if threat:
                    threats.append(threat)
            
            # DDoS detection
            if self.config['ddos']['enabled']:
                threat = self._detect_ddos(packet_info)
                if threat:
                    threats.append(threat)
            
            # Brute force detection
            if self.config['brute_force']['enabled']:
                threat = self._detect_brute_force(packet_info)
                if threat:
                    threats.append(threat)
            
            # Data exfiltration
            if self.config['exfiltration']['enabled']:
                threat = self._detect_exfiltration(packet_info)
                if threat:
                    threats.append(threat)
            
            # Suspicious port access
            threat = self._detect_suspicious_port(packet_info)
            if threat:
                threats.append(threat)
            
            # Malicious user agent
            threat = self._detect_malicious_user_agent(packet_info)
            if threat:
                threats.append(threat)
            
            # Store detected threats
            for threat in threats:
                self.threats.append(threat)
                self.threat_stats[threat['type']] += 1
        
        return threats
    
    def _detect_port_scan(self, packet_info: dict) -> Optional[dict]:
        """Detect port scanning attempts"""
        if 'src_ip' not in packet_info or 'dst_port' not in packet_info:
            return None
        
        src_ip = packet_info['src_ip']
        dst_port = packet_info['dst_port']
        timestamp = packet_info['timestamp']
        
        tracker = self.port_scan_tracker[src_ip]
        tracker['ports'].add(dst_port)
        tracker['timestamps'].append(timestamp)
        
        # Check if threshold exceeded
        config = self.config['port_scan']
        time_window = timedelta(seconds=config['time_window'])
        
        # Remove old timestamps
        cutoff = timestamp - time_window
        while tracker['timestamps'] and tracker['timestamps'][0] < cutoff:
            tracker['timestamps'].popleft()
        
        # Check threshold
        if len(tracker['ports']) >= config['threshold']:
            unique_ports = len(tracker['ports'])
            if unique_ports >= config['threshold']:
                return {
                    'type': 'PORT_SCAN',
                    'severity': 'HIGH',
                    'timestamp': timestamp,
                    'source_ip': src_ip,
                    'target_ports': list(tracker['ports'])[:50],  # Limit output
                    'port_count': unique_ports,
                    'description': f'Port scan detected from {src_ip}: {unique_ports} ports scanned'
                }
        
        return None
    
    def _detect_syn_flood(self, packet_info: dict) -> Optional[dict]:
        """Detect SYN flood attacks"""
        if packet_info.get('protocol_name') != 'TCP':
            return None
        
        tcp_flags = packet_info.get('tcp_flags', 0)
        # Check for SYN flag (0x02)
        if not (tcp_flags & 0x02):
            return None
        
        src_ip = packet_info.get('src_ip')
        if not src_ip:
            return None
        
        timestamp = packet_info['timestamp']
        tracker = self.syn_tracker[src_ip]
        tracker.append(timestamp)
        
        # Check threshold
        config = self.config['syn_flood']
        time_window = timedelta(seconds=config['time_window'])
        cutoff = timestamp - time_window
        
        # Count recent SYN packets
        recent_syns = sum(1 for ts in tracker if ts >= cutoff)
        
        if recent_syns >= config['threshold']:
            return {
                'type': 'SYN_FLOOD',
                'severity': 'CRITICAL',
                'timestamp': timestamp,
                'source_ip': src_ip,
                'syn_count': recent_syns,
                'time_window': config['time_window'],
                'description': f'SYN flood detected from {src_ip}: {recent_syns} SYN packets in {config["time_window"]}s'
            }
        
        return None
    
    def _detect_ddos(self, packet_info: dict) -> Optional[dict]:
        """Detect DDoS attacks"""
        dst_ip = packet_info.get('dst_ip')
        src_ip = packet_info.get('src_ip')
        
        if not dst_ip or not src_ip:
            return None
        
        timestamp = packet_info['timestamp']
        key = f"{src_ip}->{dst_ip}"
        
        tracker = self.connection_tracker[key]
        tracker['count'] += 1
        tracker['bytes'] += packet_info.get('length', 0)
        tracker['timestamps'].append(timestamp)
        
        # Check for excessive connections
        config = self.config['ddos']
        time_window = timedelta(seconds=1)
        cutoff = timestamp - time_window
        
        recent_packets = sum(1 for ts in tracker['timestamps'] if ts >= cutoff)
        
        if recent_packets >= config['packet_threshold']:
            return {
                'type': 'DDOS',
                'severity': 'CRITICAL',
                'timestamp': timestamp,
                'source_ip': src_ip,
                'target_ip': dst_ip,
                'packet_rate': recent_packets,
                'description': f'DDoS attack detected: {src_ip} -> {dst_ip} ({recent_packets} pkt/s)'
            }
        
        return None
    
    def _detect_brute_force(self, packet_info: dict) -> Optional[dict]:
        """Detect brute force attacks"""
        # This would need application layer inspection
        # Placeholder for now - would integrate with protocol analyzers
        return None
    
    def _detect_exfiltration(self, packet_info: dict) -> Optional[dict]:
        """Detect data exfiltration attempts"""
        src_ip = packet_info.get('src_ip')
        dst_ip = packet_info.get('dst_ip')
        
        if not src_ip or not dst_ip:
            return None
        
        # Track outbound data
        key = f"{src_ip}->{dst_ip}"
        tracker = self.data_transfer_tracker[key]
        
        # Assume outbound if source is private IP
        if self._is_private_ip(src_ip) and not self._is_private_ip(dst_ip):
            tracker['bytes_sent'] += packet_info.get('length', 0)
            tracker['connections'].add(dst_ip)
            
            config = self.config['exfiltration']
            
            if tracker['bytes_sent'] >= config['data_threshold']:
                return {
                    'type': 'DATA_EXFILTRATION',
                    'severity': 'HIGH',
                    'timestamp': packet_info['timestamp'],
                    'source_ip': src_ip,
                    'destination_ip': dst_ip,
                    'bytes_sent': tracker['bytes_sent'],
                    'description': f'Possible data exfiltration: {src_ip} sent {tracker["bytes_sent"]/1024/1024:.2f} MB to {dst_ip}'
                }
        
        return None
    
    def _detect_suspicious_port(self, packet_info: dict) -> Optional[dict]:
        """Detect access to suspicious ports"""
        dst_port = packet_info.get('dst_port')
        
        if dst_port in self.SUSPICIOUS_PORTS:
            return {
                'type': 'SUSPICIOUS_PORT',
                'severity': 'MEDIUM',
                'timestamp': packet_info['timestamp'],
                'source_ip': packet_info.get('src_ip'),
                'destination_ip': packet_info.get('dst_ip'),
                'port': dst_port,
                'service': self.SUSPICIOUS_PORTS[dst_port],
                'description': f'Access to suspicious port {dst_port} ({self.SUSPICIOUS_PORTS[dst_port]})'
            }
        
        return None
    
    def _detect_malicious_user_agent(self, packet_info: dict) -> Optional[dict]:
        """Detect malicious user agents (requires HTTP inspection)"""
        # Would need deep packet inspection
        # Placeholder for integration with protocol analyzer
        return None
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private"""
        if not ip:
            return False
        
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        try:
            first = int(parts[0])
            second = int(parts[1])
            
            # 10.0.0.0/8
            if first == 10:
                return True
            
            # 172.16.0.0/12
            if first == 172 and 16 <= second <= 31:
                return True
            
            # 192.168.0.0/16
            if first == 192 and second == 168:
                return True
            
            # 127.0.0.0/8
            if first == 127:
                return True
        
        except ValueError:
            return False
        
        return False
    
    def get_threats(self, count: int = 100, threat_type: str = None) -> List[dict]:
        """Get recent threats"""
        with self.lock:
            threats = list(self.threats)
            
            if threat_type:
                threats = [t for t in threats if t['type'] == threat_type]
            
            return threats[-count:]
    
    def get_stats(self) -> dict:
        """Get threat detection statistics"""
        with self.lock:
            return {
                'total_threats': len(self.threats),
                'by_type': dict(self.threat_stats),
                'active_trackers': {
                    'port_scans': len(self.port_scan_tracker),
                    'syn_floods': len(self.syn_tracker),
                    'connections': len(self.connection_tracker)
                }
            }
    
    def clear_threats(self):
        """Clear threat history"""
        with self.lock:
            self.threats.clear()
            self.threat_stats.clear()
    
    def reset(self):
        """Reset all tracking data"""
        with self.lock:
            self.port_scan_tracker.clear()
            self.syn_tracker.clear()
            self.connection_tracker.clear()
            self.auth_failure_tracker.clear()
            self.data_transfer_tracker.clear()
            self.threats.clear()
            self.threat_stats.clear()


# Testing
if __name__ == "__main__":
    print("CyberSafe Threat Detection Engine")
    print("=" * 50)
    
    detector = ThreatDetector()
    
    # Simulate port scan
    print("\nSimulating port scan...")
    for port in range(20, 45):
        packet = {
            'timestamp': datetime.now(),
            'src_ip': '192.168.1.100',
            'dst_ip': '192.168.1.1',
            'dst_port': port,
            'protocol_name': 'TCP',
            'length': 60
        }
        threats = detector.analyze_packet(packet)
        if threats:
            for threat in threats:
                print(f"  THREAT: {threat['type']} - {threat['description']}")
    
    # Get stats
    print("\nThreat Statistics:")
    stats = detector.get_stats()
    print(f"  Total threats: {stats['total_threats']}")
    print(f"  By type: {stats['by_type']}")
    
    print("\nRecent threats:")
    for threat in detector.get_threats(10):
        print(f"  [{threat['severity']}] {threat['type']}: {threat['description']}")
