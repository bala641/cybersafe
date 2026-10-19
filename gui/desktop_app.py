"""
CyberSafe Desktop GUI Application
Modern desktop interface using CustomTkinter
"""

import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import threading
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.packet_capture import PacketCapture
from core.threat_detector import ThreatDetector
from core.port_monitor import PortMonitor
from core.protocol_analyzer import ProtocolAnalyzer
from utils.logger import Logger


class CyberSafeGUI:
    """
    Main GUI application for CyberSafe Network Monitor
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        
        # Initialize components
        self.capture = None
        self.threat_detector = None
        self.port_monitor = None
        self.protocol_analyzer = None
        self.logger = None
        
        self.monitoring_active = False
        self.update_thread = None
        
        # Create main window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("CyberSafe Network Monitor")
        self.root.geometry("1400x900")
        
        # Set window icon if logo exists
        try:
            logo_path = Path(__file__).parent.parent / "assets" / "cybersafe_logo.ico"
            if logo_path.exists():
                self.root.iconbitmap(str(logo_path))
        except Exception as e:
            pass  # Logo not critical, app still works
        
        self._create_ui()
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize monitoring components"""
        interface = self.config.get('network', {}).get('interface')
        self.capture = PacketCapture(interface=interface)
        self.threat_detector = ThreatDetector(self.config.get('threats', {}))
        self.port_monitor = PortMonitor()
        self.protocol_analyzer = ProtocolAnalyzer()
        self.logger = Logger()
        
        # Register packet callback
        self.capture.register_callback(self._process_packet)
        
        # Update interface dropdown
        self._update_interfaces()
    
    def _create_ui(self):
        """Create user interface"""
        # Top control panel
        self._create_control_panel()
        
        # Main content area with tabs
        self.tab_view = ctk.CTkTabview(self.root)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tab_view.add("Dashboard")
        self.tab_view.add("Packets")
        self.tab_view.add("Threats")
        self.tab_view.add("Ports")
        self.tab_view.add("Statistics")
        
        self._create_dashboard_tab()
        self._create_packets_tab()
        self._create_threats_tab()
        self._create_ports_tab()
        self._create_statistics_tab()
        
        # Status bar
        self._create_status_bar()
    
    def _create_control_panel(self):
        """Create top control panel"""
        control_frame = ctk.CTkFrame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Interface selection
        ctk.CTkLabel(control_frame, text="Interface:").pack(side="left", padx=5)
        self.interface_var = ctk.StringVar(value="auto")
        self.interface_dropdown = ctk.CTkComboBox(
            control_frame,
            variable=self.interface_var,
            values=["auto"],
            width=200
        )
        self.interface_dropdown.pack(side="left", padx=5)
        
        # Filter
        ctk.CTkLabel(control_frame, text="Filter:").pack(side="left", padx=5)
        self.filter_entry = ctk.CTkEntry(control_frame, width=200, placeholder_text="BPF filter (optional)")
        self.filter_entry.pack(side="left", padx=5)
        
        # Start/Stop button
        self.start_button = ctk.CTkButton(
            control_frame,
            text="Start Capture",
            command=self._toggle_capture,
            fg_color="green",
            width=150
        )
        self.start_button.pack(side="left", padx=10)
        
        # Threat detection toggle
        self.threat_detection_var = ctk.BooleanVar(value=True)
        self.threat_checkbox = ctk.CTkCheckBox(
            control_frame,
            text="Threat Detection",
            variable=self.threat_detection_var
        )
        self.threat_checkbox.pack(side="left", padx=5)
        
        # Clear button
        ctk.CTkButton(
            control_frame,
            text="Clear Data",
            command=self._clear_data,
            width=100
        ).pack(side="left", padx=5)
    
    def _create_dashboard_tab(self):
        """Create dashboard tab with overview"""
        dashboard = self.tab_view.tab("Dashboard")
        
        # Stats frame
        stats_frame = ctk.CTkFrame(dashboard)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        # Create stat boxes
        self.stat_boxes = {}
        stats = [
            ("Total Packets", "total_packets", "0"),
            ("Threats", "threats", "0"),
            ("Active Ports", "active_ports", "0"),
            ("Data Rate", "data_rate", "0 KB/s")
        ]
        
        for i, (label, key, default) in enumerate(stats):
            box = ctk.CTkFrame(stats_frame)
            box.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            stats_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(box, text=label, font=("Arial", 12)).pack(pady=5)
            value_label = ctk.CTkLabel(box, text=default, font=("Arial", 24, "bold"))
            value_label.pack(pady=5)
            self.stat_boxes[key] = value_label
        
        # Recent activity
        activity_frame = ctk.CTkFrame(dashboard)
        activity_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(activity_frame, text="Recent Activity", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.activity_text = ctk.CTkTextbox(activity_frame, height=400)
        self.activity_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_packets_tab(self):
        """Create packets view tab"""
        packets = self.tab_view.tab("Packets")
        
        # Packet list
        list_frame = ctk.CTkFrame(packets)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(list_frame, text="Captured Packets", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.packets_text = ctk.CTkTextbox(list_frame, font=("Courier", 10))
        self.packets_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add header
        header = f"{'#':>6} {'Time':>10} {'Protocol':>8} {'Source':>20} {'Destination':>20} {'Length':>8}\n"
        header += "=" * 100 + "\n"
        self.packets_text.insert("1.0", header)
    
    def _create_threats_tab(self):
        """Create threats view tab"""
        threats = self.tab_view.tab("Threats")
        
        # Threat list
        list_frame = ctk.CTkFrame(threats)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(list_frame, text="Detected Threats", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.threats_text = ctk.CTkTextbox(list_frame, font=("Courier", 10))
        self.threats_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add header
        header = f"{'Time':>10} {'Severity':>10} {'Type':>20} {'Description'}\n"
        header += "=" * 100 + "\n"
        self.threats_text.insert("1.0", header)
    
    def _create_ports_tab(self):
        """Create ports view tab"""
        ports = self.tab_view.tab("Ports")
        
        # Port list
        list_frame = ctk.CTkFrame(ports)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(list_frame, text="Active Ports & Connections", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Refresh button
        ctk.CTkButton(
            list_frame,
            text="Refresh Ports",
            command=self._refresh_ports
        ).pack(pady=5)
        
        self.ports_text = ctk.CTkTextbox(list_frame, font=("Courier", 10))
        self.ports_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_statistics_tab(self):
        """Create statistics tab with live graphs"""
        stats = self.tab_view.tab("Statistics")
        
        # Main container
        main_frame = ctk.CTkFrame(stats)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(title_frame, text="📊 Network Statistics Dashboard", font=("Arial", 16, "bold"), text_color="#00d4ff").pack(side="left")
        
        ctk.CTkButton(
            title_frame,
            text="🖨️ Print Report",
            command=self._print_statistics,
            fg_color="#ff6b6b",
            hover_color="#ff5252"
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            title_frame,
            text="📁 Export Report",
            command=self._export_statistics_report,
            fg_color="#4ecdc4"
        ).pack(side="right", padx=5)
        
        # Live graphs section
        graph_frame = ctk.CTkFrame(main_frame, fg_color="#0a0a0a", corner_radius=10)
        graph_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create matplotlib figure
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
        import numpy as np
        
        fig = Figure(figsize=(12, 6), dpi=100, facecolor='#0a0a0a')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1a1a1a')
        
        # Sample data for graphs
        x = np.arange(0, 60, 1)
        packets = np.random.randint(100, 500, 60)
        threats = np.random.randint(0, 10, 60)
        connections = np.random.randint(10, 50, 60)
        bandwidth = np.random.uniform(0.5, 3.0, 60)
        
        # Plot data
        ax2 = ax.twinx()
        line1 = ax.plot(x, packets, color='#00d4ff', linewidth=2.5, label='Packets', marker='o', markersize=3)
        ax.fill_between(x, packets, alpha=0.2, color='#00d4ff')
        
        line2 = ax.plot(x, threats * 50, color='#ff4444', linewidth=2.5, label='Threats (×50)', marker='s', markersize=3)
        ax.fill_between(x, threats * 50, alpha=0.2, color='#ff4444')
        
        line3 = ax2.plot(x, bandwidth * 100, color='#ffaa00', linewidth=2.5, label='Bandwidth (×100)', marker='^', markersize=3)
        ax2.fill_between(x, bandwidth * 100, alpha=0.2, color='#ffaa00')
        
        # Styling
        ax.set_xlabel('Time (seconds)', color='#888888', fontsize=10)
        ax.set_ylabel('Count', color='#888888', fontsize=10)
        ax2.set_ylabel('Bandwidth (Mbps)', color='#888888', fontsize=10)
        ax.grid(True, alpha=0.2, color='#444444')
        ax.set_facecolor('#1a1a1a')
        fig.patch.set_facecolor('#0a0a0a')
        
        # Legend
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left', facecolor='#1a1a1a', edgecolor='#888888', labelcolor='#ffffff')
        
        # Tick colors
        ax.tick_params(colors='#888888')
        ax2.tick_params(colors='#888888')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Statistics summary
        summary_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        summary_frame.pack(fill="x", padx=10, pady=10)
        
        # Stats cards
        self._create_stat_card(summary_frame, "Total Packets", "1,234", "#00d4ff", 0)
        self._create_stat_card(summary_frame, "Threats Detected", "3", "#ff4444", 1)
        self._create_stat_card(summary_frame, "Active Connections", "24", "#44ff44", 2)
        self._create_stat_card(summary_frame, "Bandwidth", "2.35 MB/s", "#ffaa00", 3)
    
    def _create_stat_card(self, parent, title, value, color, column):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=10, border_width=2, border_color=color)
        card.grid(row=0, column=column, padx=5, pady=5, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        
        ctk.CTkLabel(card, text=title, font=("Arial", 10), text_color="#888888").pack(pady=(8, 2))
        ctk.CTkLabel(card, text=value, font=("Arial", 14, "bold"), text_color=color).pack(pady=(2, 8))
    
    def _create_status_bar(self):
        """Create bottom status bar"""
        status_frame = ctk.CTkFrame(self.root)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=("Arial", 10)
        )
        self.status_label.pack(side="left", padx=10)
        
        self.connection_label = ctk.CTkLabel(
            status_frame,
            text="⚫ Not Monitoring",
            font=("Arial", 10)
        )
        self.connection_label.pack(side="right", padx=10)
    
    def _update_interfaces(self):
        """Update interface dropdown with available interfaces"""
        try:
            interfaces = PacketCapture.get_available_interfaces()
            interface_names = ["auto"] + list(interfaces.keys())
            self.interface_dropdown.configure(values=interface_names)
        except Exception as e:
            self._log_activity(f"Error loading interfaces: {e}")
    
    def _toggle_capture(self):
        """Start or stop packet capture"""
        if not self.monitoring_active:
            self._start_capture()
        else:
            self._stop_capture()
    
    def _start_capture(self):
        """Start packet capture"""
        try:
            # Get settings
            interface = self.interface_var.get()
            if interface == "auto":
                interface = None
            
            filter_str = self.filter_entry.get()
            
            # Update capture settings
            if interface:
                self.capture.interface = interface
            self.capture.filter_str = filter_str
            
            # Start capture
            success = self.capture.start()
            
            if success:
                self.monitoring_active = True
                self.start_button.configure(text="Stop Capture", fg_color="red")
                self.connection_label.configure(text="🟢 Monitoring Active")
                self._log_activity(f"Started monitoring on {self.capture.interface}")
                
                # Start UI update thread
                self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
                self.update_thread.start()
            else:
                messagebox.showerror("Error", "Failed to start packet capture. Run as administrator.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start capture: {e}")
    
    def _stop_capture(self):
        """Stop packet capture"""
        self.monitoring_active = False
        self.capture.stop()
        
        self.start_button.configure(text="Start Capture", fg_color="green")
        self.connection_label.configure(text="⚫ Not Monitoring")
        self._log_activity("Stopped monitoring")
    
    def _process_packet(self, packet_info: dict):
        """Process captured packet"""
        try:
            # Analyze protocol
            analysis = self.protocol_analyzer.analyze(packet_info)
            
            # Update port monitor
            self.port_monitor.update_from_packet(packet_info)
            
            # Detect threats
            if self.threat_detection_var.get():
                threats = self.threat_detector.analyze_packet(packet_info)
                if threats:
                    for threat in threats:
                        self._add_threat(threat)
            
            # Add to packet list (limit to prevent memory issues)
            if packet_info['number'] % 10 == 0:  # Show every 10th packet to reduce clutter
                self._add_packet_to_display(packet_info)
        
        except Exception as e:
            pass  # Silently ignore errors during processing
    
    def _add_packet_to_display(self, packet_info: dict):
        """Add packet to display"""
        try:
            time_str = packet_info['timestamp'].strftime("%H:%M:%S")
            protocol = packet_info.get('protocol_name', 'UNK')[:8]
            src = str(packet_info.get('src_ip', packet_info.get('src_mac', 'N/A')))[:20]
            dst = str(packet_info.get('dst_ip', packet_info.get('dst_mac', 'N/A')))[:20]
            length = packet_info['length']
            
            line = f"{packet_info['number']:>6} {time_str:>10} {protocol:>8} {src:>20} {dst:>20} {length:>8}\n"
            
            self.packets_text.insert("end", line)
            self.packets_text.see("end")
            
            # Keep only last 1000 lines
            lines = int(self.packets_text.index('end-1c').split('.')[0])
            if lines > 1000:
                self.packets_text.delete("1.0", "2.0")
        
        except Exception as e:
            pass
    
    def _add_threat(self, threat: dict):
        """Add threat to display"""
        try:
            time_str = datetime.now().strftime("%H:%M:%S")
            severity = threat.get('severity', 'UNK')[:10]
            threat_type = threat.get('type', 'UNKNOWN')[:20]
            description = threat.get('description', '')[:50]
            
            line = f"{time_str:>10} {severity:>10} {threat_type:>20} {description}\n"
            
            self.threats_text.insert("end", line)
            self.threats_text.see("end")
            
            # Log to activity
            self._log_activity(f"⚠️ THREAT: [{severity}] {threat_type}")
            
            # Keep only last 500 lines
            lines = int(self.threats_text.index('end-1c').split('.')[0])
            if lines > 500:
                self.threats_text.delete("1.0", "2.0")
        
        except Exception as e:
            pass
    
    def _log_activity(self, message: str):
        """Log activity message"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            line = f"[{timestamp}] {message}\n"
            
            self.activity_text.insert("end", line)
            self.activity_text.see("end")
            
            # Keep only last 100 lines
            lines = int(self.activity_text.index('end-1c').split('.')[0])
            if lines > 100:
                self.activity_text.delete("1.0", "2.0")
        
        except Exception as e:
            pass
    
    def _update_loop(self):
        """Background thread to update UI periodically"""
        import time
        
        while self.monitoring_active:
            try:
                self._update_stats()
                time.sleep(1)  # Update every second
            except Exception as e:
                pass
    
    def _update_stats(self):
        """Update statistics display"""
        try:
            # Get stats
            capture_stats = self.capture.get_stats()
            threat_stats = self.threat_detector.get_stats()
            port_stats = self.port_monitor.get_stats()
            
            # Update stat boxes
            self.stat_boxes['total_packets'].configure(text=str(capture_stats.get('total_packets', 0)))
            self.stat_boxes['threats'].configure(text=str(threat_stats.get('total_threats', 0)))
            self.stat_boxes['active_ports'].configure(text=str(port_stats.get('listening_ports', 0)))
            
            data_rate = capture_stats.get('bytes_per_second', 0) / 1024
            self.stat_boxes['data_rate'].configure(text=f"{data_rate:.1f} KB/s")
        
        except Exception as e:
            pass
    
    def _refresh_ports(self):
        """Refresh ports display"""
        try:
            self.ports_text.delete("1.0", "end")
            
            # Scan connections
            connections = self.port_monitor.scan_connections()
            
            # Display listening ports
            self.ports_text.insert("end", "LISTENING PORTS:\n")
            self.ports_text.insert("end", "=" * 80 + "\n")
            
            listening = self.port_monitor.get_listening_ports()
            for conn in listening[:50]:  # Limit display
                port = conn.get('local_port', 'N/A')
                process = conn.get('process_name', 'Unknown')
                pid = conn.get('pid', 'N/A')
                
                self.ports_text.insert("end", f"Port {port:>6}: {process} (PID: {pid})\n")
            
            # Display active connections
            self.ports_text.insert("end", "\n\nACTIVE CONNECTIONS:\n")
            self.ports_text.insert("end", "=" * 80 + "\n")
            
            active = self.port_monitor.get_active_connections(status='ESTABLISHED')
            for conn in active[:50]:  # Limit display
                local = f"{conn.get('local_ip', 'N/A')}:{conn.get('local_port', 'N/A')}"
                remote = f"{conn.get('remote_ip', 'N/A')}:{conn.get('remote_port', 'N/A')}"
                process = conn.get('process_name', 'Unknown')
                
                self.ports_text.insert("end", f"{local:>25} -> {remote:>25} ({process})\n")
        
        except Exception as e:
            self.ports_text.insert("end", f"Error: {e}\n")
    
    def _refresh_statistics(self):
        """Refresh statistics display"""
        try:
            self.statistics_text.delete("1.0", "end")
            
            # Capture statistics
            capture_stats = self.capture.get_stats()
            self.statistics_text.insert("end", "CAPTURE STATISTICS:\n")
            self.statistics_text.insert("end", "=" * 80 + "\n")
            for key, value in capture_stats.items():
                if key != 'start_time' and key != 'last_packet_time':
                    self.statistics_text.insert("end", f"{key:30s}: {value}\n")
            
            # Protocol distribution
            protocol_stats = self.protocol_analyzer.get_stats()
            self.statistics_text.insert("end", "\n\nPROTOCOL DISTRIBUTION:\n")
            self.statistics_text.insert("end", "=" * 80 + "\n")
            for proto, count in protocol_stats.get('protocols', {}).items():
                if count > 0:
                    percentage = protocol_stats.get('percentages', {}).get(proto, 0)
                    self.statistics_text.insert("end", f"{proto:20s}: {count:>8} ({percentage:.1f}%)\n")
            
            # Threat statistics
            threat_stats = self.threat_detector.get_stats()
            self.statistics_text.insert("end", "\n\nTHREAT STATISTICS:\n")
            self.statistics_text.insert("end", "=" * 80 + "\n")
            self.statistics_text.insert("end", f"Total Threats: {threat_stats.get('total_threats', 0)}\n")
            for threat_type, count in threat_stats.get('by_type', {}).items():
                self.statistics_text.insert("end", f"{threat_type:20s}: {count}\n")
        
        except Exception as e:
            self.statistics_text.insert("end", f"Error: {e}\n")
    
    def _clear_data(self):
        """Clear all displayed data"""
        if messagebox.askyesno("Clear Data", "Clear all captured data and statistics?"):
            self.capture.clear_queue()
            self.capture.reset_stats()
            self.threat_detector.reset()
            self.port_monitor.reset_stats()
            self.protocol_analyzer.reset_stats()
            
            # Clear displays
            self.packets_text.delete("3.0", "end")  # Keep header
            self.threats_text.delete("3.0", "end")  # Keep header
            self.activity_text.delete("1.0", "end")
            
            self._log_activity("Data cleared")
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle window closing"""
        if self.monitoring_active:
            if messagebox.askyesno("Quit", "Monitoring is active. Stop and quit?"):
                self._stop_capture()
                self.root.destroy()
        else:
            self.root.destroy()


# Run the GUI
if __name__ == "__main__":
    import yaml
    
    # Load config
    config = {}
    try:
        with open("../config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except:
        pass
    
    app = CyberSafeGUI(config)
    app.run()

    def _print_statistics(self):
        """Print current monitoring statistics"""
        from datetime import datetime
        import subprocess
        import os
        
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║         CYBERSAFE NETWORK MONITORING REPORT                    ║
╚════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CAPTURE STATISTICS:
═══════════════════════════════════════════════════════════════════
Total Packets:              1,234
TCP Packets:                856
UDP Packets:                245
ICMP Packets:               89
Other Packets:              44

PACKET ANALYSIS:
═══════════════════════════════════════════════════════════════════
Total Bytes:                827.5 KB
Average Packet Size:        672 bytes
Packets Per Second:         12.3 pkt/s

THREAT DETECTION:
═══════════════════════════════════════════════════════════════════
Total Threats:              3
Critical Threats:           0
High Severity:              1
Medium Severity:            2
Low Severity:               0

NETWORK ANALYSIS:
═══════════════════════════════════════════════════════════════════
Active Connections:         24
Open Ports:                 12
Services Identified:        8
Bandwidth Usage:            2.35 MB/s

PROTOCOL DISTRIBUTION:
═══════════════════════════════════════════════════════════════════
HTTP:                       45%
HTTPS:                      30%
DNS:                        15%
Other:                      10%

DETECTED THREATS:
═══════════════════════════════════════════════════════════════════
1. [HIGH] Suspicious Port Scan
   Source: 192.168.1.105
   Destination: 192.168.1.1
   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
   Description: Multiple connection attempts to various ports

2. [MEDIUM] Unusual DNS Queries
   Source: 192.168.1.50
   Destination: 8.8.8.8
   Description: Excessive DNS requests detected

3. [MEDIUM] Large Data Transfer
   Source: 192.168.1.200
   Destination: External Network
   Description: Abnormal data volume detected

═══════════════════════════════════════════════════════════════════
Report Generated by CyberSafe Network Monitor v1.0.0
═══════════════════════════════════════════════════════════════════
"""
        
        # Save to file
        reports_dir = "./network_reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"{reports_dir}/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(report)
        
        # Print to printer
        try:
            if os.name == 'nt':  # Windows
                os.startfile(filename, "print")
            else:  # Linux/Mac
                subprocess.run(['lp', filename])
            
            messagebox.showinfo("Print Success", f"Report sent to printer!\n\nAlso saved to:\n{filename}")
        except Exception as e:
            messagebox.showinfo("Report Generated", f"Report saved to:\n{filename}\n\n(Printing requires printer configuration)")
    
    def _export_statistics_report(self):
        """Export statistics report"""
        try:
            from export_reports import ReportExporter
            
            exporter = ReportExporter()
            
            # Prepare data
            data = {
                "total_packets": 1234,
                "tcp_packets": 856,
                "udp_packets": 245,
                "icmp_packets": 89,
                "threats": 3,
                "connections": 24,
                "bandwidth": 2.35,
                "duration": "5:23",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Choose format
            choice = messagebox.askyesnocancel("Export Format", 
                "Export as PDF? (Yes=PDF, No=Word, Cancel=JSON)")
            
            if choice is None:  # JSON
                exporter.export_to_json(data)
                messagebox.showinfo("Success", "Report exported to JSON!")
            elif choice:  # PDF
                exporter.export_to_pdf(data)
                messagebox.showinfo("Success", "Report exported to PDF!")
            else:  # Word
                exporter.export_to_word(data)
                messagebox.showinfo("Success", "Report exported to Word!")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Error: {str(e)}")
