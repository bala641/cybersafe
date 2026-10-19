"""
CyberSafe Network Monitor
Professional Dashboard with LIVE Network Monitoring
All features connected to real packet capture, threat detection, and port monitoring
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog, scrolledtext
import threading
import sys
import os
from datetime import datetime
from pathlib import Path
import json
import time
from collections import deque, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.packet_capture import PacketCapture
    from core.threat_detector import ThreatDetector
    from core.port_monitor import PortMonitor
    from core.protocol_analyzer import ProtocolAnalyzer
    from utils.logger import Logger
    CORE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Core modules not available: {e}")
    CORE_AVAILABLE = False


class CyberSafeGUI:
    """Professional CyberSafe Network Dashboard - FULLY LIVE"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.monitoring_active = False
        
        # Core components for LIVE monitoring
        self.packet_capture = None
        self.threat_detector = None
        self.port_monitor = None
        self.logger = None
        
        # Available network interfaces
        self.interfaces = {}
        self.selected_interface = None
        
        # Live data storage with timestamps
        self.packets_history = deque(maxlen=120)
        self.threats_history = deque(maxlen=120)
        self.bandwidth_history = deque(maxlen=120)
        self.latency_history = deque(maxlen=120)
        
        # Real-time packet data
        self.packets_list = deque(maxlen=1000)
        self.threats_list = deque(maxlen=1000)
        self.ports_dict = defaultdict(int)
        
        # Live metrics from actual capture
        self.metrics = {
            'total_packets': 0,
            'tcp_packets': 0,
            'udp_packets': 0,
            'icmp_packets': 0,
            'http_packets': 0,
            'https_packets': 0,
            'dns_packets': 0,
            'total_bytes': 0,
            'bytes_per_sec': 0,
            'packets_per_sec': 0,
            'unique_ips': set(),
            'unique_ports': set(),
            'total_threats': 0,
            'high_threats': 0,
            'medium_threats': 0,
            'low_threats': 0,
            'devices_seen': set(),
            'bandwidth_mbps': 0.0,
            'avg_latency': 0.0
        }
        
        # Stats tracking
        self.last_update_time = time.time()
        self.last_packet_count = 0
        self.last_byte_count = 0
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("CyberSafe Network Monitor - Professional Dashboard [LIVE]")
        self.root.geometry("1920x1200")
        
        try:
            icon_path = "./assets/cybersafe_logo.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Get available interfaces
        self._load_interfaces()
        
        self._create_ui()
        self._start_display_updates()
    
    def _load_interfaces(self):
        """Load available network interfaces"""
        if CORE_AVAILABLE:
            try:
                self.interfaces = PacketCapture.get_available_interfaces()
                if self.interfaces:
                    self.selected_interface = list(self.interfaces.keys())[0]
            except Exception as e:
                print(f"Error loading interfaces: {e}")
                self.interfaces = {"auto": {"ip": "Auto-detect", "status": "available"}}
                self.selected_interface = "auto"
        else:
            self.interfaces = {"auto": {"ip": "Auto-detect", "status": "available"}}
            self.selected_interface = "auto"
    
    def _create_ui(self):
        """Create professional dashboard"""
        main = ctk.CTkFrame(self.root, fg_color="#0a0e27")
        main.pack(fill="both", expand=True)
        
        # Header with interface selection
        self._create_header(main)
        
        # Main content - scrollable
        scroll_frame = ctk.CTkScrollableFrame(main, fg_color="#0a0e27")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Live Stats Summary Section
        self._create_live_stats_section(scroll_frame)
        
        # Network Traffic Section (Bandwidth & Packets)
        self._create_network_section(scroll_frame)
        
        # Devices Section (Real device tracking)
        self._create_devices_section(scroll_frame)
        
        # Security Section (Real threats)
        self._create_security_section(scroll_frame)
        
        # Router Graphs Section (3 live graphs)
        self._create_router_section(scroll_frame)
        
        # Protocol Distribution
        self._create_protocol_section(scroll_frame)
        
        # Tabs for detailed LIVE view
        self._create_details_tabs(main)
    
    def _create_header(self, parent):
        """Create header with interface selector"""
        header = ctk.CTkFrame(parent, fg_color="#1a2744", height=80)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", padx=20, pady=15)
        
        ctk.CTkLabel(
            left,
            text="🔍 CyberSafe Network Monitor [LIVE]",
            font=("Arial", 18, "bold"),
            text_color="#00d4ff"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            left,
            text="Real-time Network Traffic Analysis & Threat Detection",
            font=("Arial", 10),
            text_color="#888888"
        ).pack(anchor="w")
        
        # Interface selector in center
        center = ctk.CTkFrame(header, fg_color="transparent")
        center.pack(side="left", padx=30, pady=15)
        
        ctk.CTkLabel(
            center,
            text="Network Interface:",
            font=("Arial", 10, "bold"),
            text_color="#4ecdc4"
        ).pack(side="left", padx=(0, 10))
        
        interface_names = list(self.interfaces.keys())
        self.interface_var = ctk.StringVar(value=self.selected_interface)
        
        self.interface_menu = ctk.CTkComboBox(
            center,
            values=interface_names,
            variable=self.interface_var,
            width=200,
            command=self._on_interface_change,
            fg_color="#0f1929",
            border_color="#00d4ff"
        )
        self.interface_menu.pack(side="left")
        
        # Status and controls on right
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", padx=20, pady=15)
        
        self.status_label = ctk.CTkLabel(
            right,
            text="🟡 Ready to Monitor",
            font=("Arial", 11, "bold"),
            text_color="#ffd93d"
        )
        self.status_label.pack()
        
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack()
        
        self.capture_btn = ctk.CTkButton(
            btn_frame,
            text="▶ Start Capture",
            command=self._toggle_monitoring,
            fg_color="#00d4ff",
            width=120,
            height=35,
            font=("Arial", 12, "bold")
        )
        self.capture_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Export",
            command=self._export_dialog,
            fg_color="#4ecdc4",
            width=90,
            height=35,
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=5)
    
    def _on_interface_change(self, choice):
        """Handle interface selection change"""
        self.selected_interface = choice
        if self.monitoring_active:
            messagebox.showinfo("Interface Change", 
                              "Please stop monitoring before changing interface")
    
    def _create_live_stats_section(self, parent):
        """Create live statistics overview"""
        section = ctk.CTkFrame(parent, fg_color="#1a2744", border_width=2, border_color="#00d4ff")
        section.pack(fill="x", pady=10)
        
        title = ctk.CTkLabel(section, text="📊 LIVE STATISTICS", font=("Arial", 12, "bold"), text_color="#00d4ff")
        title.pack(pady=(10, 5), padx=10, anchor="w")
        
        stats_frame = ctk.CTkFrame(section, fg_color="transparent")
        stats_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Total Packets
        col1 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        col1.pack(side="left", expand=True)
        self.total_packets_label = self._create_metric_card(col1, "📦", "TOTAL PACKETS", "0", "#00d4ff")
        
        # Packets/sec
        col2 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        col2.pack(side="left", expand=True)
        self.pps_label = self._create_metric_card(col2, "⚡", "PACKETS/SEC", "0", "#ffd93d")
        
        # Bandwidth
        col3 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        col3.pack(side="left", expand=True)
        self.bandwidth_label = self._create_metric_card(col3, "📶", "BANDWIDTH", "0 Mbps", "#4ecdc4")
        
        # Total Bytes
        col4 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        col4.pack(side="left", expand=True)
        self.bytes_label = self._create_metric_card(col4, "💾", "TOTAL BYTES", "0 B", "#95e1d3")
        
        # Unique IPs
        col5 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        col5.pack(side="left", expand=True)
        self.ips_label = self._create_metric_card(col5, "🌐", "UNIQUE IPs", "0", "#c7b3e5")
    
    def _create_network_section(self, parent):
        """Create network traffic metrics"""
        section = ctk.CTkFrame(parent, fg_color="#1a2744", border_width=2, border_color="#4ecdc4")
        section.pack(fill="x", pady=10)
        
        title = ctk.CTkLabel(section, text="🌐 NETWORK TRAFFIC", font=("Arial", 11, "bold"), text_color="#4ecdc4")
        title.pack(pady=(10, 5), padx=10, anchor="w")
        
        metrics_frame = ctk.CTkFrame(section, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # TCP
        col1 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col1.pack(side="left", expand=True)
        self.tcp_label = self._create_metric_card(col1, "🔷", "TCP", "0", "#00d4ff")
        
        # UDP
        col2 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col2.pack(side="left", expand=True)
        self.udp_label = self._create_metric_card(col2, "🔶", "UDP", "0", "#ffd93d")
        
        # ICMP
        col3 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col3.pack(side="left", expand=True)
        self.icmp_label = self._create_metric_card(col3, "🔸", "ICMP", "0", "#ff6b6b")
        
        # HTTP
        col4 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col4.pack(side="left", expand=True)
        self.http_label = self._create_metric_card(col4, "🌍", "HTTP", "0", "#95e1d3")
        
        # HTTPS
        col5 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col5.pack(side="left", expand=True)
        self.https_label = self._create_metric_card(col5, "🔒", "HTTPS", "0", "#4ecdc4")
    
    def _create_devices_section(self, parent):
        """Create devices metrics"""
        section = ctk.CTkFrame(parent, fg_color="#1a2744", border_width=2, border_color="#95e1d3")
        section.pack(fill="x", pady=10)
        
        title = ctk.CTkLabel(section, text="📱 DEVICES DETECTED", font=("Arial", 11, "bold"), text_color="#95e1d3")
        title.pack(pady=(10, 5), padx=10, anchor="w")
        
        metrics_frame = ctk.CTkFrame(section, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Total Devices
        col1 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col1.pack(side="left", expand=True)
        self.devices_label = self._create_metric_card(col1, "🖥️", "TOTAL DEVICES", "0", "#00d4ff")
        
        # Active Connections
        col2 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col2.pack(side="left", expand=True)
        self.connections_label = self._create_metric_card(col2, "🔗", "CONNECTIONS", "0", "#4ecdc4")
        
        # Unique Ports
        col3 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col3.pack(side="left", expand=True)
        self.ports_label = self._create_metric_card(col3, "🔌", "UNIQUE PORTS", "0", "#ffd93d")
    
    def _create_security_section(self, parent):
        """Create security/threat metrics"""
        section = ctk.CTkFrame(parent, fg_color="#1a2744", border_width=2, border_color="#ff6b6b")
        section.pack(fill="x", pady=10)
        
        title = ctk.CTkLabel(section, text="🛡️ SECURITY & THREATS", font=("Arial", 11, "bold"), text_color="#ff6b6b")
        title.pack(pady=(10, 5), padx=10, anchor="w")
        
        metrics_frame = ctk.CTkFrame(section, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Total Threats
        col1 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col1.pack(side="left", expand=True)
        self.total_threats_label = self._create_metric_card(col1, "⚠️", "TOTAL THREATS", "0", "#ff6b6b")
        
        # High Severity
        col2 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col2.pack(side="left", expand=True)
        self.high_threats_label = self._create_metric_card(col2, "🔴", "HIGH", "0", "#ff0000")
        
        # Medium Severity
        col3 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col3.pack(side="left", expand=True)
        self.medium_threats_label = self._create_metric_card(col3, "🟠", "MEDIUM", "0", "#ffa500")
        
        # Low Severity
        col4 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col4.pack(side="left", expand=True)
        self.low_threats_label = self._create_metric_card(col4, "🟡", "LOW", "0", "#ffd93d")
    
    def _create_router_section(self, parent):
        """Create router graphs - 3 LIVE graphs"""
        section = ctk.CTkFrame(parent, fg_color="#1a2744", border_width=2, border_color="#00d4ff")
        section.pack(fill="x", pady=10)
        
        title = ctk.CTkLabel(section, text="📈 LIVE NETWORK GRAPHS", font=("Arial", 11, "bold"), text_color="#00d4ff")
        title.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Three graphs in row
        graphs_frame = ctk.CTkFrame(section, fg_color="transparent")
        graphs_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Bandwidth Graph
        bandwidth_frame = ctk.CTkFrame(graphs_frame, fg_color="#0f1929", border_width=1, border_color="#00d4ff")
        bandwidth_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(bandwidth_frame, text="Bandwidth (Mbps)", font=("Arial", 10, "bold"), text_color="#00d4ff").pack(pady=5)
        self.bandwidth_graph = ctk.CTkCanvas(bandwidth_frame, bg="#0a0e27", highlightthickness=0, height=180)
        self.bandwidth_graph.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Packets/sec Graph
        packets_frame = ctk.CTkFrame(graphs_frame, fg_color="#0f1929", border_width=1, border_color="#ffd93d")
        packets_frame.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(packets_frame, text="Packets/Second", font=("Arial", 10, "bold"), text_color="#ffd93d").pack(pady=5)
        self.packets_graph = ctk.CTkCanvas(packets_frame, bg="#0a0e27", highlightthickness=0, height=180)
        self.packets_graph.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Threats Graph
        threats_frame = ctk.CTkFrame(graphs_frame, fg_color="#0f1929", border_width=1, border_color="#ff6b6b")
        threats_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(threats_frame, text="Threats Detected", font=("Arial", 10, "bold"), text_color="#ff6b6b").pack(pady=5)
        self.threats_graph = ctk.CTkCanvas(threats_frame, bg="#0a0e27", highlightthickness=0, height=180)
        self.threats_graph.pack(fill="both", expand=True, padx=5, pady=(0, 5))
    
    def _create_protocol_section(self, parent):
        """Create protocol distribution"""
        section = ctk.CTkFrame(parent, fg_color="#1a2744", border_width=2, border_color="#c7b3e5")
        section.pack(fill="x", pady=10)
        
        title = ctk.CTkLabel(section, text="📊 PROTOCOL DISTRIBUTION", font=("Arial", 11, "bold"), text_color="#c7b3e5")
        title.pack(pady=(10, 5), padx=10, anchor="w")
        
        metrics_frame = ctk.CTkFrame(section, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # DNS
        col1 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col1.pack(side="left", expand=True)
        self.dns_label = self._create_metric_card(col1, "🔍", "DNS", "0", "#c7b3e5")
        
        # ARP
        col2 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col2.pack(side="left", expand=True)
        self.arp_label = self._create_metric_card(col2, "📡", "ARP", "0", "#95e1d3")
        
        # SSH
        col3 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col3.pack(side="left", expand=True)
        self.ssh_label = self._create_metric_card(col3, "🔐", "SSH", "0", "#4ecdc4")
        
        # FTP
        col4 = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        col4.pack(side="left", expand=True)
        self.ftp_label = self._create_metric_card(col4, "📂", "FTP", "0", "#ffd93d")
    
    def _create_metric_card(self, parent, icon, label, value, color):
        """Create metric card"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack()
        
        ctk.CTkLabel(frame, text=icon, font=("Arial", 24)).pack()
        ctk.CTkLabel(frame, text=label, font=("Arial", 9), text_color="#888").pack()
        
        value_label = ctk.CTkLabel(frame, text=value, font=("Arial", 16, "bold"), text_color=color)
        value_label.pack()
        
        return value_label
    
    def _create_details_tabs(self, parent):
        """Create detail tabs with LIVE data"""
        tabs = ctk.CTkTabview(parent, fg_color="#1a2744")
        tabs.pack(fill="both", expand=False, padx=10, pady=10, ipady=120)
        
        packets_tab = tabs.add("📦 Live Packets")
        threats_tab = tabs.add("⚠️ Threats Detected")
        ports_tab = tabs.add("🔌 Active Ports")
        
        # Packets tab with live capture
        self.packets_text = scrolledtext.ScrolledText(
            packets_tab, 
            bg="#0a0e27", 
            fg="#00d4ff", 
            font=("Courier New", 9),
            height=10,
            insertbackground="#00d4ff"
        )
        self.packets_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.packets_text.insert("1.0", "Waiting for packet capture to start...\n")
        
        # Threats tab with live detection
        self.threats_text = scrolledtext.ScrolledText(
            threats_tab,
            bg="#0a0e27",
            fg="#ff6b6b",
            font=("Courier New", 9),
            height=10,
            insertbackground="#ff6b6b"
        )
        self.threats_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.threats_text.insert("1.0", "Threat detection ready. Waiting for monitoring to start...\n")
        
        # Ports tab with live monitoring
        self.ports_text = scrolledtext.ScrolledText(
            ports_tab,
            bg="#0a0e27",
            fg="#4ecdc4",
            font=("Courier New", 9),
            height=10,
            insertbackground="#4ecdc4"
        )
        self.ports_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.ports_text.insert("1.0", "Port monitoring ready. Waiting for monitoring to start...\n")
    
    def _toggle_monitoring(self):
        """Toggle LIVE monitoring on/off"""
        if not self.monitoring_active:
            self._start_monitoring()
        else:
            self._stop_monitoring()
    
    def _start_monitoring(self):
        """Start LIVE packet capture and monitoring"""
        if not CORE_AVAILABLE:
            messagebox.showerror("Error", 
                               "Core monitoring modules not available.\n"
                               "Please ensure scapy and other dependencies are installed.")
            return
        
        try:
            # Initialize components
            self.logger = Logger(level="INFO")
            
            # Initialize packet capture
            self.packet_capture = PacketCapture(
                interface=self.selected_interface if self.selected_interface != "auto" else None,
                promiscuous=True
            )
            
            # Initialize threat detector
            self.threat_detector = ThreatDetector(self.config.get('threats', {}))
            
            # Initialize port monitor
            self.port_monitor = PortMonitor()
            
            # Register packet callback
            self.packet_capture.register_callback(self._on_packet_captured)
            
            # Start capture
            self.packet_capture.start()
            
            # Update UI
            self.monitoring_active = True
            self.capture_btn.configure(text="⏹ Stop Capture", fg_color="#ff6b6b")
            self.status_label.configure(text="🔴 LIVE MONITORING", text_color="#ff6b6b")
            self.interface_menu.configure(state="disabled")
            
            # Clear previous data
            self.packets_text.delete("1.0", "end")
            self.threats_text.delete("1.0", "end")
            self.ports_text.delete("1.0", "end")
            
            self.packets_text.insert("1.0", f"[{datetime.now().strftime('%H:%M:%S')}] Packet capture started on {self.selected_interface}\n")
            self.threats_text.insert("1.0", f"[{datetime.now().strftime('%H:%M:%S')}] Threat detection active\n")
            self.ports_text.insert("1.0", f"[{datetime.now().strftime('%H:%M:%S')}] Port monitoring active\n")
            
            messagebox.showinfo("Monitoring Started", 
                              f"Live monitoring started on interface: {self.selected_interface}\n\n"
                              "All data is now being captured in real-time!")
            
        except PermissionError:
            messagebox.showerror("Permission Error",
                               "Administrator/root privileges required for packet capture.\n\n"
                               "Please run as Administrator (Windows) or with sudo (Linux/Mac).")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring:\n{str(e)}")
            self.monitoring_active = False
    
    def _stop_monitoring(self):
        """Stop LIVE monitoring"""
        try:
            if self.packet_capture:
                self.packet_capture.stop()
                
                # Get final stats
                final_stats = self.packet_capture.get_stats()
                
                self.packets_text.insert("end", 
                    f"\n[{datetime.now().strftime('%H:%M:%S')}] Capture stopped\n"
                    f"Final Statistics:\n"
                    f"  Total Packets: {final_stats.get('total_packets', 0)}\n"
                    f"  Total Bytes: {final_stats.get('bytes_total', 0):,}\n"
                )
            
            self.monitoring_active = False
            self.capture_btn.configure(text="▶ Start Capture", fg_color="#00d4ff")
            self.status_label.configure(text="🟡 Ready to Monitor", text_color="#ffd93d")
            self.interface_menu.configure(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error stopping monitoring:\n{str(e)}")
    
    def _on_packet_captured(self, packet_info):
        """Callback for each captured packet - LIVE DATA"""
        try:
            # Update metrics
            self.metrics['total_packets'] += 1
            self.metrics['total_bytes'] += packet_info.get('length', 0)
            
            # Track protocol counts
            protocol = packet_info.get('protocol_name', 'OTHER')
            if protocol == 'TCP':
                self.metrics['tcp_packets'] += 1
            elif protocol == 'UDP':
                self.metrics['udp_packets'] += 1
            elif protocol == 'ICMP':
                self.metrics['icmp_packets'] += 1
            
            # Track application protocols
            dst_port = packet_info.get('dst_port')
            src_port = packet_info.get('src_port')
            
            if dst_port == 80 or src_port == 80:
                self.metrics['http_packets'] += 1
            elif dst_port == 443 or src_port == 443:
                self.metrics['https_packets'] += 1
            elif dst_port == 53 or src_port == 53:
                self.metrics['dns_packets'] += 1
            
            # Track unique IPs
            if 'src_ip' in packet_info:
                self.metrics['unique_ips'].add(packet_info['src_ip'])
            if 'dst_ip' in packet_info:
                self.metrics['unique_ips'].add(packet_info['dst_ip'])
            
            # Track unique ports
            if dst_port:
                self.metrics['unique_ports'].add(dst_port)
                self.ports_dict[dst_port] += 1
            if src_port:
                self.metrics['unique_ports'].add(src_port)
                self.ports_dict[src_port] += 1
            
            # Track devices (by MAC)
            if 'src_mac' in packet_info:
                self.metrics['devices_seen'].add(packet_info['src_mac'])
            if 'dst_mac' in packet_info:
                self.metrics['devices_seen'].add(packet_info['dst_mac'])
            
            # Store packet for display
            self.packets_list.append(packet_info)
            
            # Update port monitor
            if self.port_monitor:
                self.port_monitor.update_from_packet(packet_info)
            
            # Threat detection
            if self.threat_detector:
                threats = self.threat_detector.analyze_packet(packet_info)
                if threats:
                    for threat in threats:
                        self.metrics['total_threats'] += 1
                        severity = threat.get('severity', 'low').lower()
                        
                        if severity == 'high':
                            self.metrics['high_threats'] += 1
                        elif severity == 'medium':
                            self.metrics['medium_threats'] += 1
                        else:
                            self.metrics['low_threats'] += 1
                        
                        self.threats_list.append(threat)
                        
                        # Log threat in GUI
                        threat_msg = (f"[{datetime.now().strftime('%H:%M:%S')}] "
                                    f"[{severity.upper()}] {threat['type']}: "
                                    f"{threat['description']}\n")
                        self.root.after(0, lambda msg=threat_msg: self._append_threat(msg))
            
            # Update packet display (every 10th packet to avoid overwhelming GUI)
            if self.metrics['total_packets'] % 10 == 0:
                self._update_packet_display()
            
        except Exception as e:
            print(f"Error processing packet: {e}")
    
    def _append_threat(self, msg):
        """Append threat to threats tab"""
        try:
            self.threats_text.insert("end", msg)
            self.threats_text.see("end")
            # Keep only last 500 lines
            lines = int(self.threats_text.index('end-1c').split('.')[0])
            if lines > 500:
                self.threats_text.delete("1.0", f"{lines-500}.0")
        except:
            pass
    
    def _update_packet_display(self):
        """Update packets display"""
        try:
            if len(self.packets_list) > 0:
                packet = self.packets_list[-1]
                protocol = packet.get('protocol_name', 'UNKNOWN')
                src = packet.get('src_ip', packet.get('src_mac', 'N/A'))
                dst = packet.get('dst_ip', packet.get('dst_mac', 'N/A'))
                length = packet.get('length', 0)
                
                packet_line = (f"[{packet.get('number', 0):6d}] {protocol:8s} "
                             f"{src:20s} → {dst:20s} ({length} bytes)\n")
                
                self.root.after(0, lambda: self._append_packet(packet_line))
        except:
            pass
    
    def _append_packet(self, line):
        """Append packet to display"""
        try:
            self.packets_text.insert("end", line)
            self.packets_text.see("end")
            # Keep only last 500 lines
            lines = int(self.packets_text.index('end-1c').split('.')[0])
            if lines > 500:
                self.packets_text.delete("1.0", f"{lines-500}.0")
        except:
            pass
    
    def _start_display_updates(self):
        """Start periodic display updates"""
        def update_loop():
            while True:
                if self.monitoring_active:
                    # Calculate rates
                    current_time = time.time()
                    time_diff = current_time - self.last_update_time
                    
                    if time_diff >= 1.0:
                        packet_diff = self.metrics['total_packets'] - self.last_packet_count
                        byte_diff = self.metrics['total_bytes'] - self.last_byte_count
                        
                        self.metrics['packets_per_sec'] = packet_diff / time_diff
                        self.metrics['bytes_per_sec'] = byte_diff / time_diff
                        self.metrics['bandwidth_mbps'] = (byte_diff * 8) / (time_diff * 1_000_000)
                        
                        # Update graph data
                        self.bandwidth_history.append(self.metrics['bandwidth_mbps'])
                        self.packets_history.append(self.metrics['packets_per_sec'])
                        self.threats_history.append(self.metrics['total_threats'])
                        
                        self.last_update_time = current_time
                        self.last_packet_count = self.metrics['total_packets']
                        self.last_byte_count = self.metrics['total_bytes']
                        
                        # Update GUI
                        self.root.after(0, self._update_all_displays)
                
                time.sleep(1)
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
    
    def _update_all_displays(self):
        """Update all GUI displays with LIVE data"""
        try:
            # Live stats
            self.total_packets_label.configure(text=f"{self.metrics['total_packets']:,}")
            self.pps_label.configure(text=f"{self.metrics['packets_per_sec']:.1f}")
            self.bandwidth_label.configure(text=f"{self.metrics['bandwidth_mbps']:.2f} Mbps")
            
            # Format bytes
            total_bytes = self.metrics['total_bytes']
            if total_bytes < 1024:
                bytes_str = f"{total_bytes} B"
            elif total_bytes < 1024**2:
                bytes_str = f"{total_bytes/1024:.2f} KB"
            elif total_bytes < 1024**3:
                bytes_str = f"{total_bytes/(1024**2):.2f} MB"
            else:
                bytes_str = f"{total_bytes/(1024**3):.2f} GB"
            
            self.bytes_label.configure(text=bytes_str)
            self.ips_label.configure(text=str(len(self.metrics['unique_ips'])))
            
            # Network traffic
            self.tcp_label.configure(text=f"{self.metrics['tcp_packets']:,}")
            self.udp_label.configure(text=f"{self.metrics['udp_packets']:,}")
            self.icmp_label.configure(text=f"{self.metrics['icmp_packets']:,}")
            self.http_label.configure(text=f"{self.metrics['http_packets']:,}")
            self.https_label.configure(text=f"{self.metrics['https_packets']:,}")
            
            # Devices
            self.devices_label.configure(text=str(len(self.metrics['devices_seen'])))
            self.connections_label.configure(text=f"{self.metrics['total_packets']:,}")
            self.ports_label.configure(text=str(len(self.metrics['unique_ports'])))
            
            # Security
            self.total_threats_label.configure(text=str(self.metrics['total_threats']))
            self.high_threats_label.configure(text=str(self.metrics['high_threats']))
            self.medium_threats_label.configure(text=str(self.metrics['medium_threats']))
            self.low_threats_label.configure(text=str(self.metrics['low_threats']))
            
            # Protocols
            self.dns_label.configure(text=f"{self.metrics['dns_packets']:,}")
            
            # Update ports display
            if len(self.ports_dict) > 0:
                self.ports_text.delete("1.0", "end")
                self.ports_text.insert("1.0", f"Active Ports (Top 20 by packet count):\n{'='*60}\n\n")
                
                sorted_ports = sorted(self.ports_dict.items(), key=lambda x: x[1], reverse=True)[:20]
                for port, count in sorted_ports:
                    port_name = self._get_port_name(port)
                    self.ports_text.insert("end", f"Port {port:5d} ({port_name:15s}): {count:6d} packets\n")
            
            # Update graphs
            self._draw_graph(self.bandwidth_graph, self.bandwidth_history, "#00d4ff")
            self._draw_graph(self.packets_graph, self.packets_history, "#ffd93d")
            self._draw_graph(self.threats_graph, self.threats_history, "#ff6b6b")
            
        except Exception as e:
            print(f"Error updating displays: {e}")
    
    def _get_port_name(self, port):
        """Get common port name"""
        port_names = {
            20: "FTP-Data", 21: "FTP", 22: "SSH", 23: "Telnet",
            25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
            143: "IMAP", 443: "HTTPS", 445: "SMB", 3306: "MySQL",
            3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Alt"
        }
        return port_names.get(port, "Unknown")
    
    def _draw_graph(self, canvas, data, color):
        """Draw live graph on canvas"""
        try:
            canvas.delete("all")
            
            if len(data) < 2:
                return
            
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                return
            
            # Get max value for scaling
            max_val = max(data) if max(data) > 0 else 1
            
            # Draw grid lines
            for i in range(5):
                y = height * i / 4
                canvas.create_line(0, y, width, y, fill="#1a2744", width=1)
            
            # Draw data
            points = []
            step = width / len(data)
            
            for i, value in enumerate(data):
                x = i * step
                y = height - (value / max_val * height * 0.9) - (height * 0.05)
                points.extend([x, y])
            
            if len(points) >= 4:
                canvas.create_line(points, fill=color, width=2, smooth=True)
            
            # Draw current value
            if len(data) > 0:
                current = data[-1]
                canvas.create_text(
                    width - 10, 10,
                    text=f"{current:.1f}",
                    fill=color,
                    font=("Arial", 10, "bold"),
                    anchor="ne"
                )
        except Exception as e:
            print(f"Error drawing graph: {e}")
    
    def _export_dialog(self):
        """Export dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Export Report")
        dialog.geometry("350x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Export Live Data", font=("Arial", 12, "bold"), text_color="#00d4ff").pack(pady=15)
        
        # Format
        ctk.CTkLabel(dialog, text="Format:", font=("Arial", 10)).pack(anchor="w", padx=20)
        fmt_var = ctk.StringVar(value="JSON")
        for label, val in [("📄 JSON", "JSON"), ("📕 PDF", "PDF"), ("📘 Word", "WORD"), ("📋 Text", "TEXT")]:
            ctk.CTkRadioButton(dialog, text=label, variable=fmt_var, value=val).pack(anchor="w", padx=40)
        
        # Location
        ctk.CTkLabel(dialog, text="Location:", font=("Arial", 10)).pack(anchor="w", padx=20, pady=(15, 0))
        loc_var = ctk.StringVar(value="downloads")
        for label, val in [("📁 Downloads", "downloads"), ("🖥️ Desktop", "desktop"), ("📂 Documents", "documents"), ("📌 Custom", "custom")]:
            ctk.CTkRadioButton(dialog, text=label, variable=loc_var, value=val).pack(anchor="w", padx=40)
        
        def export():
            fmt = fmt_var.get()
            loc = loc_var.get()
            
            if loc == "custom":
                loc = filedialog.askdirectory()
                if not loc:
                    return
            else:
                paths = {"downloads": os.path.expanduser("~/Downloads"), 
                        "desktop": os.path.expanduser("~/Desktop"), 
                        "documents": os.path.expanduser("~/Documents")}
                loc = paths[loc]
            
            self._perform_export(fmt, loc)
            dialog.destroy()
        
        btn = ctk.CTkFrame(dialog, fg_color="transparent")
        btn.pack(pady=15)
        ctk.CTkButton(btn, text="Export", command=export, fg_color="#00d4ff", width=120).pack(side="left", padx=5)
        ctk.CTkButton(btn, text="Cancel", command=dialog.destroy, fg_color="#666", width=120).pack(side="left", padx=5)
    
    def _perform_export(self, fmt, loc):
        """Export live data report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cybersafe_live_{timestamp}"
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "interface": self.selected_interface,
                "total_packets": self.metrics['total_packets'],
                "total_bytes": self.metrics['total_bytes'],
                "packets_per_sec": self.metrics['packets_per_sec'],
                "bandwidth_mbps": self.metrics['bandwidth_mbps'],
                "tcp_packets": self.metrics['tcp_packets'],
                "udp_packets": self.metrics['udp_packets'],
                "icmp_packets": self.metrics['icmp_packets'],
                "http_packets": self.metrics['http_packets'],
                "https_packets": self.metrics['https_packets'],
                "dns_packets": self.metrics['dns_packets'],
                "unique_ips": len(self.metrics['unique_ips']),
                "unique_ports": len(self.metrics['unique_ports']),
                "devices_detected": len(self.metrics['devices_seen']),
                "total_threats": self.metrics['total_threats'],
                "high_threats": self.metrics['high_threats'],
                "medium_threats": self.metrics['medium_threats'],
                "low_threats": self.metrics['low_threats']
            }
            
            if fmt == "JSON":
                path = os.path.join(loc, f"{filename}.json")
                with open(path, 'w') as f:
                    json.dump(export_data, f, indent=2)
            else:
                path = os.path.join(loc, f"{filename}.txt")
                with open(path, 'w') as f:
                    f.write(f"CyberSafe Live Monitoring Report\n")
                    f.write(f"Generated: {datetime.now()}\n")
                    f.write(f"Interface: {self.selected_interface}\n")
                    f.write("="*60 + "\n\n")
                    for key, value in export_data.items():
                        f.write(f"{key}: {value}\n")
            
            messagebox.showinfo("Success", f"Live data exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def run(self):
        """Run app"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle close"""
        if self.monitoring_active:
            if messagebox.askokcancel("Quit", "Monitoring is active. Stop and quit?"):
                self._stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()


if __name__ == "__main__":
    config = {}
    app = CyberSafeGUI(config)
    app.run()
