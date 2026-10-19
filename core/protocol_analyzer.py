"""
Protocol Analyzer - Deep packet inspection for various protocols
Inspired by Wireshark's protocol dissectors
"""

from typing import Dict, Optional, List
import struct
import re
from datetime import datetime


class ProtocolAnalyzer:
    """
    Analyze and dissect various network protocols
    """
    
    def __init__(self):
        self.protocol_stats = {
            'HTTP': 0,
            'HTTPS': 0,
            'DNS': 0,
            'FTP': 0,
            'SSH': 0,
            'SMTP': 0,
            'POP3': 0,
            'IMAP': 0,
            'TELNET': 0,
            'SMB': 0,
            'RDP': 0,
            'Other': 0
        }
    
    def analyze(self, packet_info: dict) -> dict:
        """
        Perform deep packet inspection
        Returns enhanced packet information with protocol details
        """
        analysis = {
            'timestamp': packet_info.get('timestamp', datetime.now()),
            'protocol': packet_info.get('protocol_name', 'UNKNOWN'),
            'app_protocol': packet_info.get('app_protocol'),
            'details': {}
        }
        
        # Analyze based on protocol
        protocol = packet_info.get('protocol_name')
        
        if protocol == 'TCP':
            analysis['details'].update(self._analyze_tcp(packet_info))
            
            # Check for application protocols
            src_port = packet_info.get('src_port')
            dst_port = packet_info.get('dst_port')
            
            if src_port or dst_port:
                app_protocol = self._identify_app_protocol(src_port, dst_port, packet_info)
                if app_protocol:
                    analysis['app_protocol'] = app_protocol
                    self.protocol_stats[app_protocol] = self.protocol_stats.get(app_protocol, 0) + 1
                    
                    # Deep inspection for specific protocols
                    if app_protocol == 'HTTP':
                        analysis['details'].update(self._analyze_http(packet_info))
                    elif app_protocol == 'HTTPS':
                        analysis['details'].update(self._analyze_https(packet_info))
                    elif app_protocol == 'FTP':
                        analysis['details'].update(self._analyze_ftp(packet_info))
                    elif app_protocol == 'SSH':
                        analysis['details'].update(self._analyze_ssh(packet_info))
                    elif app_protocol == 'SMTP':
                        analysis['details'].update(self._analyze_smtp(packet_info))
        
        elif protocol == 'UDP':
            analysis['details'].update(self._analyze_udp(packet_info))
            
            # DNS is usually over UDP
            if 'dns_query' in packet_info:
                analysis['app_protocol'] = 'DNS'
                analysis['details'].update(self._analyze_dns(packet_info))
                self.protocol_stats['DNS'] += 1
        
        elif protocol == 'ICMP':
            analysis['details'].update(self._analyze_icmp(packet_info))
        
        elif protocol == 'ARP':
            analysis['details'].update(self._analyze_arp(packet_info))
        
        return analysis
    
    def _analyze_tcp(self, packet_info: dict) -> dict:
        """Analyze TCP packet"""
        details = {
            'transport': 'TCP',
            'src_port': packet_info.get('src_port'),
            'dst_port': packet_info.get('dst_port'),
            'flags': self._parse_tcp_flags(packet_info.get('tcp_flags', 0)),
            'seq': packet_info.get('seq'),
            'ack': packet_info.get('ack'),
            'window': packet_info.get('window')
        }
        
        # Connection state
        flags = packet_info.get('tcp_flags', 0)
        if flags & 0x02:  # SYN
            details['connection_state'] = 'SYN' if not (flags & 0x10) else 'SYN-ACK'
        elif flags & 0x01:  # FIN
            details['connection_state'] = 'FIN'
        elif flags & 0x04:  # RST
            details['connection_state'] = 'RST'
        elif flags & 0x10:  # ACK
            details['connection_state'] = 'ESTABLISHED'
        
        return details
    
    def _parse_tcp_flags(self, flags: int) -> List[str]:
        """Parse TCP flags"""
        flag_names = []
        flag_map = {
            0x01: 'FIN',
            0x02: 'SYN',
            0x04: 'RST',
            0x08: 'PSH',
            0x10: 'ACK',
            0x20: 'URG',
            0x40: 'ECE',
            0x80: 'CWR'
        }
        
        for bit, name in flag_map.items():
            if flags & bit:
                flag_names.append(name)
        
        return flag_names
    
    def _analyze_udp(self, packet_info: dict) -> dict:
        """Analyze UDP packet"""
        return {
            'transport': 'UDP',
            'src_port': packet_info.get('src_port'),
            'dst_port': packet_info.get('dst_port'),
            'length': packet_info.get('length')
        }
    
    def _analyze_icmp(self, packet_info: dict) -> dict:
        """Analyze ICMP packet"""
        icmp_types = {
            0: 'Echo Reply',
            3: 'Destination Unreachable',
            4: 'Source Quench',
            5: 'Redirect',
            8: 'Echo Request',
            11: 'Time Exceeded',
            12: 'Parameter Problem',
            13: 'Timestamp',
            14: 'Timestamp Reply'
        }
        
        icmp_type = packet_info.get('icmp_type', 0)
        
        return {
            'transport': 'ICMP',
            'type': icmp_type,
            'type_name': icmp_types.get(icmp_type, f'Unknown ({icmp_type})'),
            'code': packet_info.get('icmp_code', 0)
        }
    
    def _analyze_arp(self, packet_info: dict) -> dict:
        """Analyze ARP packet"""
        arp_ops = {
            1: 'Request',
            2: 'Reply'
        }
        
        return {
            'protocol': 'ARP',
            'operation': arp_ops.get(packet_info.get('arp_op', 0), 'Unknown'),
            'sender_mac': packet_info.get('arp_hwsrc'),
            'sender_ip': packet_info.get('arp_psrc'),
            'target_mac': packet_info.get('arp_hwdst'),
            'target_ip': packet_info.get('arp_pdst')
        }
    
    def _identify_app_protocol(self, src_port: int, dst_port: int, packet_info: dict) -> Optional[str]:
        """Identify application layer protocol based on port"""
        port_protocols = {
            20: 'FTP-DATA',
            21: 'FTP',
            22: 'SSH',
            23: 'TELNET',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            445: 'SMB',
            587: 'SMTP',
            993: 'IMAPS',
            995: 'POP3S',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            5900: 'VNC',
            6379: 'Redis',
            8080: 'HTTP-ALT',
            27017: 'MongoDB'
        }
        
        # Check destination port first (usually the service port)
        if dst_port in port_protocols:
            return port_protocols[dst_port]
        
        # Check source port (for server responses)
        if src_port in port_protocols:
            return port_protocols[src_port]
        
        return None
    
    def _analyze_http(self, packet_info: dict) -> dict:
        """Analyze HTTP traffic"""
        details = {
            'protocol': 'HTTP',
            'encrypted': False
        }
        
        # Would need payload inspection to extract:
        # - HTTP method (GET, POST, etc.)
        # - URL/URI
        # - Headers
        # - User-Agent
        # - Status code (for responses)
        
        # Placeholder for deep inspection
        details['note'] = 'Deep inspection requires payload analysis'
        
        return details
    
    def _analyze_https(self, packet_info: dict) -> dict:
        """Analyze HTTPS/TLS traffic"""
        details = {
            'protocol': 'HTTPS',
            'encrypted': True
        }
        
        # For TLS, could extract:
        # - TLS version
        # - Cipher suite
        # - Server Name Indication (SNI)
        # - Certificate details
        
        details['note'] = 'TLS handshake analysis available with payload'
        
        return details
    
    def _analyze_dns(self, packet_info: dict) -> dict:
        """Analyze DNS traffic"""
        details = {
            'protocol': 'DNS'
        }
        
        if 'dns_query' in packet_info:
            details['query'] = packet_info['dns_query']
            details['type'] = 'Query'
        
        return details
    
    def _analyze_ftp(self, packet_info: dict) -> dict:
        """Analyze FTP traffic"""
        return {
            'protocol': 'FTP',
            'encrypted': False,
            'note': 'Command/Response analysis requires payload'
        }
    
    def _analyze_ssh(self, packet_info: dict) -> dict:
        """Analyze SSH traffic"""
        return {
            'protocol': 'SSH',
            'encrypted': True,
            'note': 'Encrypted tunnel - limited analysis'
        }
    
    def _analyze_smtp(self, packet_info: dict) -> dict:
        """Analyze SMTP traffic"""
        return {
            'protocol': 'SMTP',
            'encrypted': False,
            'note': 'Email command analysis requires payload'
        }
    
    def get_protocol_distribution(self) -> dict:
        """Get distribution of protocols seen"""
        return self.protocol_stats.copy()
    
    def get_stats(self) -> dict:
        """Get analyzer statistics"""
        total = sum(self.protocol_stats.values())
        
        stats = {
            'total_packets': total,
            'protocols': self.protocol_stats.copy()
        }
        
        if total > 0:
            stats['percentages'] = {
                proto: (count / total * 100)
                for proto, count in self.protocol_stats.items()
                if count > 0
            }
        
        return stats
    
    def reset_stats(self):
        """Reset statistics"""
        for key in self.protocol_stats:
            self.protocol_stats[key] = 0


class HTTPAnalyzer:
    """
    Specialized HTTP/HTTPS analyzer
    """
    
    @staticmethod
    def parse_http_request(payload: bytes) -> Optional[dict]:
        """Parse HTTP request from payload"""
        try:
            data = payload.decode('utf-8', errors='ignore')
            lines = data.split('\r\n')
            
            if not lines:
                return None
            
            # Parse request line
            request_line = lines[0].split(' ')
            if len(request_line) < 3:
                return None
            
            method, uri, version = request_line[0], request_line[1], request_line[2]
            
            # Parse headers
            headers = {}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
            
            return {
                'type': 'request',
                'method': method,
                'uri': uri,
                'version': version,
                'headers': headers,
                'host': headers.get('Host'),
                'user_agent': headers.get('User-Agent')
            }
        
        except Exception as e:
            return None
    
    @staticmethod
    def parse_http_response(payload: bytes) -> Optional[dict]:
        """Parse HTTP response from payload"""
        try:
            data = payload.decode('utf-8', errors='ignore')
            lines = data.split('\r\n')
            
            if not lines:
                return None
            
            # Parse status line
            status_line = lines[0].split(' ', 2)
            if len(status_line) < 3:
                return None
            
            version, status_code, reason = status_line
            
            # Parse headers
            headers = {}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
            
            return {
                'type': 'response',
                'version': version,
                'status_code': int(status_code),
                'reason': reason,
                'headers': headers,
                'content_type': headers.get('Content-Type'),
                'content_length': headers.get('Content-Length')
            }
        
        except Exception as e:
            return None


# Testing
if __name__ == "__main__":
    print("CyberSafe Protocol Analyzer")
    print("=" * 50)
    
    analyzer = ProtocolAnalyzer()
    
    # Test TCP packet
    tcp_packet = {
        'timestamp': datetime.now(),
        'protocol_name': 'TCP',
        'src_ip': '192.168.1.100',
        'dst_ip': '93.184.216.34',
        'src_port': 54321,
        'dst_port': 443,
        'tcp_flags': 0x12,  # SYN-ACK
        'seq': 1000,
        'ack': 2000,
        'window': 65535,
        'length': 60
    }
    
    result = analyzer.analyze(tcp_packet)
    print("\nTCP Packet Analysis:")
    print(f"  Protocol: {result['protocol']}")
    print(f"  App Protocol: {result.get('app_protocol')}")
    print(f"  Flags: {result['details'].get('flags')}")
    print(f"  State: {result['details'].get('connection_state')}")
    
    # Test DNS packet
    dns_packet = {
        'timestamp': datetime.now(),
        'protocol_name': 'UDP',
        'src_port': 12345,
        'dst_port': 53,
        'dns_query': 'example.com',
        'length': 64
    }
    
    result = analyzer.analyze(dns_packet)
    print("\nDNS Packet Analysis:")
    print(f"  Protocol: {result.get('app_protocol')}")
    print(f"  Query: {result['details'].get('query')}")
    
    # Show stats
    print("\nProtocol Statistics:")
    stats = analyzer.get_stats()
    for proto, count in stats['protocols'].items():
        if count > 0:
            print(f"  {proto}: {count}")
