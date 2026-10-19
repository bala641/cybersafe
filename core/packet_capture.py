"""
Core packet capture engine using Scapy
Similar to Wireshark's packet capture capabilities
"""

import threading
import queue
from datetime import datetime
from typing import Callable, Optional, List, Dict
import psutil

try:
    from scapy.all import sniff, get_if_list, get_if_hwaddr, conf
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    from scapy.layers.dns import DNS
    from scapy.layers.http import HTTP
    from scapy.layers.l2 import Ether, ARP
except ImportError:
    print("Warning: Scapy not installed. Install with: pip install scapy")


class PacketCapture:
    """
    High-performance packet capture engine
    """
    
    def __init__(self, interface: str = None, filter_str: str = "", 
                 promiscuous: bool = True, buffer_size: int = 65536):
        self.interface = interface or self._get_default_interface()
        self.filter_str = filter_str
        self.promiscuous = promiscuous
        self.buffer_size = buffer_size
        
        self.capture_active = False
        self.capture_thread = None
        self.packet_queue = queue.Queue(maxsize=10000)
        
        self.callbacks: List[Callable] = []
        self.packet_count = 0
        self.bytes_captured = 0
        
        self.stats = {
            'total_packets': 0,
            'tcp_packets': 0,
            'udp_packets': 0,
            'icmp_packets': 0,
            'other_packets': 0,
            'bytes_total': 0,
            'start_time': None,
            'last_packet_time': None
        }
    
    def _get_default_interface(self) -> str:
        """Get the default network interface"""
        try:
            # Try to get network interfaces with psutil
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            
            # Find first active interface with an IP
            for iface_name, iface_stats in stats.items():
                if iface_stats.isup and iface_name in addrs:
                    # Check if it has an IPv4 address
                    for addr in addrs[iface_name]:
                        if addr.family == 2:  # AF_INET (IPv4)
                            # Skip loopback
                            if not addr.address.startswith('127.'):
                                return iface_name
        except Exception as e:
            print(f"Error detecting interface with psutil: {e}")
        
        # Fallback to Scapy's interface list
        try:
            interfaces = get_if_list()
            if interfaces:
                # Filter out loopback
                for iface in interfaces:
                    if 'loop' not in iface.lower() and 'loopback' not in iface.lower():
                        return iface
                return interfaces[0]
        except:
            pass
        
        return conf.iface  # Scapy default
    
    @staticmethod
    def get_available_interfaces() -> Dict[str, dict]:
        """Get all available network interfaces with details"""
        interfaces = {}
        
        try:
            # Get interface info from psutil
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            
            for iface in get_if_list():
                try:
                    info = {
                        'name': iface,
                        'mac': get_if_hwaddr(iface),
                        'ip': None,
                        'netmask': None,
                        'status': 'up' if iface in stats and stats[iface].isup else 'down'
                    }
                    
                    # Get IP and netmask from psutil
                    if iface in addrs:
                        for addr in addrs[iface]:
                            if addr.family == 2:  # AF_INET (IPv4)
                                info['ip'] = addr.address
                                info['netmask'] = addr.netmask
                                break
                    
                    interfaces[iface] = info
                except Exception as e:
                    print(f"Error getting info for {iface}: {e}")
        except Exception as e:
            print(f"Error enumerating interfaces: {e}")
        
        return interfaces
    
    def register_callback(self, callback: Callable):
        """Register a callback function to be called for each packet"""
        self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _packet_handler(self, packet):
        """Internal packet handler"""
        try:
            timestamp = datetime.now()
            
            # Extract packet information
            packet_info = self._extract_packet_info(packet, timestamp)
            
            # Update statistics
            self._update_stats(packet_info)
            
            # Add to queue
            try:
                self.packet_queue.put_nowait(packet_info)
            except queue.Full:
                # Queue full, remove oldest and add new
                try:
                    self.packet_queue.get_nowait()
                    self.packet_queue.put_nowait(packet_info)
                except:
                    pass
            
            # Call registered callbacks
            for callback in self.callbacks:
                try:
                    callback(packet_info)
                except Exception as e:
                    print(f"Callback error: {e}")
        
        except Exception as e:
            print(f"Packet handler error: {e}")
    
    def _extract_packet_info(self, packet, timestamp) -> dict:
        """Extract relevant information from a packet"""
        info = {
            'timestamp': timestamp,
            'number': self.packet_count,
            'length': len(packet),
            'raw': bytes(packet),
            'layers': [],
            'summary': packet.summary()
        }
        
        # Ethernet layer
        if packet.haslayer(Ether):
            ether = packet[Ether]
            info['src_mac'] = ether.src
            info['dst_mac'] = ether.dst
            info['layers'].append('Ethernet')
        
        # IP layer
        if packet.haslayer(IP):
            ip = packet[IP]
            info['src_ip'] = ip.src
            info['dst_ip'] = ip.dst
            info['ttl'] = ip.ttl
            info['protocol'] = ip.proto
            info['ip_version'] = ip.version
            info['layers'].append('IP')
        
        # TCP layer
        if packet.haslayer(TCP):
            tcp = packet[TCP]
            info['src_port'] = tcp.sport
            info['dst_port'] = tcp.dport
            info['tcp_flags'] = tcp.flags
            info['seq'] = tcp.seq
            info['ack'] = tcp.ack
            info['window'] = tcp.window
            info['protocol_name'] = 'TCP'
            info['layers'].append('TCP')
            
            # Application layer protocols
            if tcp.dport == 80 or tcp.sport == 80:
                info['app_protocol'] = 'HTTP'
            elif tcp.dport == 443 or tcp.sport == 443:
                info['app_protocol'] = 'HTTPS'
            elif tcp.dport == 22 or tcp.sport == 22:
                info['app_protocol'] = 'SSH'
            elif tcp.dport == 21 or tcp.sport == 21:
                info['app_protocol'] = 'FTP'
        
        # UDP layer
        elif packet.haslayer(UDP):
            udp = packet[UDP]
            info['src_port'] = udp.sport
            info['dst_port'] = udp.dport
            info['length'] = udp.len
            info['protocol_name'] = 'UDP'
            info['layers'].append('UDP')
            
            # DNS
            if packet.haslayer(DNS):
                dns = packet[DNS]
                info['app_protocol'] = 'DNS'
                info['dns_query'] = dns.qd.qname.decode() if dns.qd else None
                info['layers'].append('DNS')
        
        # ICMP layer
        elif packet.haslayer(ICMP):
            icmp = packet[ICMP]
            info['icmp_type'] = icmp.type
            info['icmp_code'] = icmp.code
            info['protocol_name'] = 'ICMP'
            info['layers'].append('ICMP')
        
        # ARP layer
        if packet.haslayer(ARP):
            arp = packet[ARP]
            info['arp_op'] = arp.op
            info['arp_hwsrc'] = arp.hwsrc
            info['arp_psrc'] = arp.psrc
            info['arp_hwdst'] = arp.hwdst
            info['arp_pdst'] = arp.pdst
            info['protocol_name'] = 'ARP'
            info['layers'].append('ARP')
        
        return info
    
    def _update_stats(self, packet_info: dict):
        """Update capture statistics"""
        self.packet_count += 1
        self.bytes_captured += packet_info['length']
        
        self.stats['total_packets'] += 1
        self.stats['bytes_total'] += packet_info['length']
        self.stats['last_packet_time'] = packet_info['timestamp']
        
        if not self.stats['start_time']:
            self.stats['start_time'] = packet_info['timestamp']
        
        protocol = packet_info.get('protocol_name', 'OTHER')
        if protocol == 'TCP':
            self.stats['tcp_packets'] += 1
        elif protocol == 'UDP':
            self.stats['udp_packets'] += 1
        elif protocol == 'ICMP':
            self.stats['icmp_packets'] += 1
        else:
            self.stats['other_packets'] += 1
    
    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        try:
            print(f"Starting packet capture on {self.interface}")
            if self.filter_str:
                print(f"Using filter: {self.filter_str}")
            
            sniff(
                iface=self.interface,
                prn=self._packet_handler,
                filter=self.filter_str,
                store=False,
                promisc=self.promiscuous,
                stop_filter=lambda x: not self.capture_active
            )
        except PermissionError:
            print("ERROR: Permission denied. Run as administrator/root.")
            self.capture_active = False
        except Exception as e:
            print(f"Capture error: {e}")
            self.capture_active = False
    
    def start(self):
        """Start packet capture"""
        if self.capture_active:
            print("Capture already active")
            return False
        
        self.capture_active = True
        self.stats['start_time'] = datetime.now()
        
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        print(f"Packet capture started on {self.interface}")
        return True
    
    def stop(self):
        """Stop packet capture"""
        if not self.capture_active:
            return False
        
        print("Stopping packet capture...")
        self.capture_active = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        
        print("Packet capture stopped")
        return True
    
    def is_active(self) -> bool:
        """Check if capture is active"""
        return self.capture_active
    
    def get_packet(self, timeout: float = 1) -> Optional[dict]:
        """Get a packet from the queue"""
        try:
            return self.packet_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_packets_batch(self, max_packets: int = 100) -> List[dict]:
        """Get multiple packets from queue"""
        packets = []
        try:
            while len(packets) < max_packets:
                packet = self.packet_queue.get_nowait()
                packets.append(packet)
        except queue.Empty:
            pass
        return packets
    
    def get_stats(self) -> dict:
        """Get capture statistics"""
        stats = self.stats.copy()
        
        if stats['start_time']:
            duration = (datetime.now() - stats['start_time']).total_seconds()
            stats['duration_seconds'] = duration
            stats['packets_per_second'] = stats['total_packets'] / duration if duration > 0 else 0
            stats['bytes_per_second'] = stats['bytes_total'] / duration if duration > 0 else 0
        
        return stats
    
    def clear_queue(self):
        """Clear the packet queue"""
        while not self.packet_queue.empty():
            try:
                self.packet_queue.get_nowait()
            except queue.Empty:
                break
    
    def reset_stats(self):
        """Reset statistics"""
        self.packet_count = 0
        self.bytes_captured = 0
        self.stats = {
            'total_packets': 0,
            'tcp_packets': 0,
            'udp_packets': 0,
            'icmp_packets': 0,
            'other_packets': 0,
            'bytes_total': 0,
            'start_time': None,
            'last_packet_time': None
        }


# Testing function
if __name__ == "__main__":
    print("CyberSafe Packet Capture Engine")
    print("=" * 50)
    
    # List available interfaces
    print("\nAvailable interfaces:")
    interfaces = PacketCapture.get_available_interfaces()
    for name, info in interfaces.items():
        print(f"  {name}: {info['ip']} ({info['mac']})")
    
    # Create capture instance
    capture = PacketCapture()
    
    # Register callback
    def packet_callback(packet_info):
        protocol = packet_info.get('protocol_name', 'UNKNOWN')
        src = packet_info.get('src_ip', packet_info.get('src_mac', 'N/A'))
        dst = packet_info.get('dst_ip', packet_info.get('dst_mac', 'N/A'))
        print(f"[{packet_info['number']}] {protocol}: {src} -> {dst} ({packet_info['length']} bytes)")
    
    capture.register_callback(packet_callback)
    
    # Start capture
    print(f"\nStarting capture on {capture.interface}")
    print("Press Ctrl+C to stop\n")
    
    try:
        capture.start()
        
        # Keep running and display stats
        import time
        while capture.is_active():
            time.sleep(5)
            stats = capture.get_stats()
            print(f"\nStats: {stats['total_packets']} packets, "
                  f"{stats['bytes_total']/1024:.2f} KB, "
                  f"{stats.get('packets_per_second', 0):.2f} pkt/s")
    
    except KeyboardInterrupt:
        print("\n\nStopping capture...")
        capture.stop()
        
        # Final stats
        stats = capture.get_stats()
        print("\n" + "=" * 50)
        print("Final Statistics:")
        print(f"  Total Packets: {stats['total_packets']}")
        print(f"  TCP: {stats['tcp_packets']}")
        print(f"  UDP: {stats['udp_packets']}")
        print(f"  ICMP: {stats['icmp_packets']}")
        print(f"  Other: {stats['other_packets']}")
        print(f"  Total Bytes: {stats['bytes_total']:,}")
        print(f"  Duration: {stats.get('duration_seconds', 0):.2f}s")
        print(f"  Avg Rate: {stats.get('packets_per_second', 0):.2f} pkt/s")
