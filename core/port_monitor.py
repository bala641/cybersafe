"""
Port and Connection Monitoring Module
Track active ports, connections, and network statistics
"""

import psutil
import threading
from datetime import datetime
from collections import defaultdict, deque
from typing import Dict, List, Optional, Set
import socket


class PortMonitor:
    """
    Monitor active ports and network connections
    Similar to netstat/ss functionality with enhanced tracking
    """
    
    def __init__(self):
        self.lock = threading.Lock()
        
        # Active connections tracking
        self.connections = {}
        self.connection_history = deque(maxlen=10000)
        
        # Port usage tracking
        self.listening_ports = {}
        self.port_stats = defaultdict(lambda: {
            'packets': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'connections': 0,
            'first_seen': None,
            'last_seen': None
        })
        
        # Process-port mapping
        self.process_ports = defaultdict(set)
        self.port_processes = {}
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'listening_ports': 0,
            'established_connections': 0,
            'closed_connections': 0
        }
    
    def scan_connections(self) -> List[dict]:
        """
        Scan all active network connections
        Returns list of connection information
        """
        connections = []
        
        try:
            # Get all network connections
            for conn in psutil.net_connections(kind='inet'):
                try:
                    conn_info = self._parse_connection(conn)
                    if conn_info:
                        connections.append(conn_info)
                except Exception as e:
                    continue
            
            with self.lock:
                self._update_connection_tracking(connections)
        
        except psutil.AccessDenied:
            print("Warning: Access denied. Run as administrator for full connection info.")
        except Exception as e:
            print(f"Error scanning connections: {e}")
        
        return connections
    
    def _parse_connection(self, conn) -> Optional[dict]:
        """Parse psutil connection object"""
        try:
            conn_info = {
                'fd': conn.fd,
                'family': self._get_family_name(conn.family),
                'type': self._get_socket_type(conn.type),
                'status': conn.status,
                'timestamp': datetime.now()
            }
            
            # Local address
            if conn.laddr:
                conn_info['local_ip'] = conn.laddr.ip if hasattr(conn.laddr, 'ip') else conn.laddr[0]
                conn_info['local_port'] = conn.laddr.port if hasattr(conn.laddr, 'port') else conn.laddr[1]
            
            # Remote address
            if conn.raddr:
                conn_info['remote_ip'] = conn.raddr.ip if hasattr(conn.raddr, 'ip') else conn.raddr[0]
                conn_info['remote_port'] = conn.raddr.port if hasattr(conn.raddr, 'port') else conn.raddr[1]
            
            # Process information
            if conn.pid:
                try:
                    process = psutil.Process(conn.pid)
                    conn_info['pid'] = conn.pid
                    conn_info['process_name'] = process.name()
                    conn_info['process_exe'] = process.exe()
                    conn_info['process_cmdline'] = ' '.join(process.cmdline())
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    conn_info['pid'] = conn.pid
                    conn_info['process_name'] = 'Unknown'
            
            return conn_info
        
        except Exception as e:
            return None
    
    def _get_family_name(self, family) -> str:
        """Get address family name"""
        family_map = {
            socket.AF_INET: 'IPv4',
            socket.AF_INET6: 'IPv6',
        }
        return family_map.get(family, f'Unknown({family})')
    
    def _get_socket_type(self, sock_type) -> str:
        """Get socket type name"""
        type_map = {
            socket.SOCK_STREAM: 'TCP',
            socket.SOCK_DGRAM: 'UDP',
        }
        return type_map.get(sock_type, f'Unknown({sock_type})')
    
    def _update_connection_tracking(self, connections: List[dict]):
        """Update internal connection tracking"""
        current_time = datetime.now()
        active_conn_ids = set()
        
        for conn in connections:
            # Create connection ID
            conn_id = self._get_connection_id(conn)
            active_conn_ids.add(conn_id)
            
            # Update or create connection record
            if conn_id not in self.connections:
                conn['first_seen'] = current_time
                conn['packet_count'] = 0
                conn['bytes_sent'] = 0
                conn['bytes_received'] = 0
                self.connections[conn_id] = conn
                self.stats['total_connections'] += 1
            else:
                # Update existing connection
                self.connections[conn_id].update(conn)
            
            self.connections[conn_id]['last_seen'] = current_time
            
            # Track listening ports
            if conn.get('status') == 'LISTEN' and 'local_port' in conn:
                port = conn['local_port']
                self.listening_ports[port] = conn
                
                # Update port-process mapping
                if 'pid' in conn:
                    self.port_processes[port] = conn['pid']
                    self.process_ports[conn['pid']].add(port)
        
        # Remove closed connections
        closed_connections = set(self.connections.keys()) - active_conn_ids
        for conn_id in closed_connections:
            closed_conn = self.connections.pop(conn_id)
            self.connection_history.append(closed_conn)
            self.stats['closed_connections'] += 1
        
        # Update stats
        self.stats['active_connections'] = len(self.connections)
        self.stats['listening_ports'] = len(self.listening_ports)
        self.stats['established_connections'] = sum(
            1 for conn in self.connections.values() 
            if conn.get('status') == 'ESTABLISHED'
        )
    
    def _get_connection_id(self, conn: dict) -> str:
        """Generate unique connection ID"""
        parts = [
            conn.get('type', ''),
            conn.get('local_ip', ''),
            str(conn.get('local_port', '')),
            conn.get('remote_ip', ''),
            str(conn.get('remote_port', ''))
        ]
        return '-'.join(parts)
    
    def update_from_packet(self, packet_info: dict):
        """Update port statistics from captured packet"""
        with self.lock:
            timestamp = packet_info.get('timestamp', datetime.now())
            
            # Update destination port stats
            if 'dst_port' in packet_info:
                port = packet_info['dst_port']
                stats = self.port_stats[port]
                
                stats['packets'] += 1
                stats['bytes_received'] += packet_info.get('length', 0)
                
                if not stats['first_seen']:
                    stats['first_seen'] = timestamp
                stats['last_seen'] = timestamp
            
            # Update source port stats
            if 'src_port' in packet_info:
                port = packet_info['src_port']
                stats = self.port_stats[port]
                
                stats['packets'] += 1
                stats['bytes_sent'] += packet_info.get('length', 0)
                
                if not stats['first_seen']:
                    stats['first_seen'] = timestamp
                stats['last_seen'] = timestamp
    
    def get_listening_ports(self) -> List[dict]:
        """Get all listening ports"""
        with self.lock:
            return list(self.listening_ports.values())
    
    def get_active_connections(self, status: str = None) -> List[dict]:
        """Get active connections, optionally filtered by status"""
        with self.lock:
            connections = list(self.connections.values())
            
            if status:
                connections = [c for c in connections if c.get('status') == status]
            
            return connections
    
    def get_connection_by_port(self, port: int) -> List[dict]:
        """Get connections using specific port"""
        with self.lock:
            return [
                conn for conn in self.connections.values()
                if conn.get('local_port') == port or conn.get('remote_port') == port
            ]
    
    def get_process_connections(self, pid: int) -> List[dict]:
        """Get all connections for a specific process"""
        with self.lock:
            return [
                conn for conn in self.connections.values()
                if conn.get('pid') == pid
            ]
    
    def get_port_stats(self, port: int = None) -> dict:
        """Get statistics for specific port or all ports"""
        with self.lock:
            if port:
                return self.port_stats.get(port, {})
            else:
                return dict(self.port_stats)
    
    def get_top_ports(self, limit: int = 10, by: str = 'packets') -> List[tuple]:
        """
        Get top ports by traffic
        by: 'packets', 'bytes_sent', 'bytes_received', or 'connections'
        """
        with self.lock:
            items = list(self.port_stats.items())
            items.sort(key=lambda x: x[1].get(by, 0), reverse=True)
            return items[:limit]
    
    def get_stats(self) -> dict:
        """Get overall statistics"""
        with self.lock:
            return self.stats.copy()
    
    def get_network_io_stats(self) -> dict:
        """Get network I/O statistics"""
        try:
            io_counters = psutil.net_io_counters()
            return {
                'bytes_sent': io_counters.bytes_sent,
                'bytes_recv': io_counters.bytes_recv,
                'packets_sent': io_counters.packets_sent,
                'packets_recv': io_counters.packets_recv,
                'errin': io_counters.errin,
                'errout': io_counters.errout,
                'dropin': io_counters.dropin,
                'dropout': io_counters.dropout
            }
        except Exception as e:
            return {}
    
    def get_interface_stats(self) -> Dict[str, dict]:
        """Get per-interface statistics"""
        try:
            stats = {}
            io_counters = psutil.net_io_counters(pernic=True)
            
            for interface, counters in io_counters.items():
                stats[interface] = {
                    'bytes_sent': counters.bytes_sent,
                    'bytes_recv': counters.bytes_recv,
                    'packets_sent': counters.packets_sent,
                    'packets_recv': counters.packets_recv,
                    'errin': counters.errin,
                    'errout': counters.errout,
                    'dropin': counters.dropin,
                    'dropout': counters.dropout
                }
            
            return stats
        except Exception as e:
            return {}
    
    def is_port_in_use(self, port: int) -> bool:
        """Check if port is in use"""
        with self.lock:
            return port in self.listening_ports
    
    def get_process_by_port(self, port: int) -> Optional[int]:
        """Get process ID using specific port"""
        with self.lock:
            return self.port_processes.get(port)
    
    def reset_stats(self):
        """Reset statistics"""
        with self.lock:
            self.port_stats.clear()
            self.stats = {
                'total_connections': 0,
                'active_connections': 0,
                'listening_ports': 0,
                'established_connections': 0,
                'closed_connections': 0
            }


# Standalone monitoring function
def monitor_ports_realtime(duration: int = 60, interval: float = 1.0):
    """Monitor ports in real-time"""
    import time
    
    monitor = PortMonitor()
    
    print("CyberSafe Port Monitor")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            # Scan connections
            connections = monitor.scan_connections()
            
            # Display stats
            stats = monitor.get_stats()
            io_stats = monitor.get_network_io_stats()
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Active Connections: {stats['active_connections']}")
            print(f"  Listening: {stats['listening_ports']} | "
                  f"Established: {stats['established_connections']} | "
                  f"Total: {stats['total_connections']}")
            
            if io_stats:
                print(f"  Network I/O: ↑ {io_stats['bytes_sent']/1024/1024:.2f} MB | "
                      f"↓ {io_stats['bytes_recv']/1024/1024:.2f} MB")
            
            # Show top listening ports
            listening = monitor.get_listening_ports()
            if listening:
                print("\n  Top Listening Ports:")
                for conn in listening[:5]:
                    port = conn.get('local_port', 'N/A')
                    process = conn.get('process_name', 'Unknown')
                    print(f"    Port {port}: {process}")
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    
    # Final summary
    print("\n" + "=" * 80)
    print("Final Statistics:")
    stats = monitor.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


# Testing
if __name__ == "__main__":
    import sys
    
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    monitor_ports_realtime(duration=duration, interval=2.0)
