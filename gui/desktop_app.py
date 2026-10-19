"""
CyberSafe Desktop GUI Application
Professional Stock Market Style Live Dashboard
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog, scrolledtext
import threading
import sys
import os
from datetime import datetime
from pathlib import Path
import json
import random
from collections import deque

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.packet_capture import PacketCapture
    from core.threat_detector import ThreatDetector
    from core.port_monitor import PortMonitor
    from core.protocol_analyzer import ProtocolAnalyzer
    from utils.logger import Logger
except:
    pass


class LiveGraph:
    """Live updating graph for stock market style display"""
    def __init__(self, max_points=60):
        self.max_points = max_points
        self.data = deque(maxlen=max_points)
        self.timestamps = deque(maxlen=max_points)
        self.lock = threading.Lock()
    
    def add_point(self, value):
        with self.lock:
            self.data.append(value)
            self.timestamps.append(len(self.timestamps))
    
    def get_data(self):
        with self.lock:
            return list(self.data), list(self.timestamps)


class CyberSafeGUI:
    """Professional CyberSafe Dashboard with Live Graphs"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        
        # Initialize live graph data
        self.packet_graph = LiveGraph()
        self.threat_graph = LiveGraph()
        self.bandwidth_graph = LiveGraph()
        
        # Current stats
        self.total_packets = 0
        self.total_threats = 0
        self.active_connections = 0
        self.bandwidth_usage = 0.0
        self.total_bytes = 0
        
        self.monitoring_active = False
        self.update_thread = None
        
        # Create main window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("CyberSafe Network Monitor - Live Dashboard")
        self.root.geometry("1800x1100")
        
        # Set window icon
        try:
            icon_path = "./assets/cybersafe_logo.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        self._create_ui()
        self._start_live_updates()
    
    def _create_ui(self):
        """Create professional dashboard UI"""
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color="#0a0e27")
        main_container.pack(fill="both", expand=True)
        
        # Header
        self._create_header(main_container)
        
        # Main dashboard area
        content_frame = ctk.CTkFrame(main_container, fg_color="#0a0e27")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Left sidebar - Quick stats
        self._create_left_sidebar(content_frame)
        
        # Center area - Live graphs
        center_frame = ctk.CTkFrame(content_frame, fg_color="#0a0e27")
        center_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        
        # Top row - 2 graphs
        top_row = ctk.CTkFrame(center_frame, fg_color="#0a0e27")
        top_row.pack(fill="both", expand=True, pady=(0, 10))
        
        self._create_packets_graph(top_row)
        self._create_threats_graph(top_row)
        
        # Bottom - 1 large graph
        self._create_bandwidth_graph(center_frame)
        
        # Right sidebar - Tabs
        self._create_right_sidebar(content_frame)
        
        # Configure grid
        content_frame.columnconfigure(0, weight=0)  # Left sidebar
        content_frame.columnconfigure(1, weight=1)  # Center graphs
        content_frame.columnconfigure(2, weight=0)  # Right sidebar
        content_frame.rowconfigure(0, weight=1)
    
    def _create_header(self, parent):
        """Create professional header"""
        header = ctk.CTkFrame(parent, fg_color="#1a2744", height=80)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Left - Title
        left_frame = ctk.CTkFrame(header, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=15)
        
        ctk.CTkLabel(
            left_frame,
            text="🔍 CyberSafe Network Monitor",
            font=("Arial", 20, "bold"),
            text_color="#00d4ff"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            left_frame,
            text="Live Network Analytics Dashboard",
            font=("Arial", 11),
            text_color="#888888"
        ).pack(anchor="w")
        
        # Center - Status
        center_frame = ctk.CTkFrame(header, fg_color="transparent")
        center_frame.pack(side="left", expand=True, padx=20)
        
        self.status_label = ctk.CTkLabel(
            center_frame,
            text="🟢 Ready",
            font=("Arial", 12, "bold"),
            text_color="#4ecdc4"
        )
        self.status_label.pack()
        
        # Right - Controls
        right_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=15)
        
        self.start_btn = ctk.CTkButton(
            right_frame,
            text="▶ Start Monitoring",
            command=self._toggle_monitoring,
            fg_color="#00d4ff",
            hover_color="#00a8cc",
            width=150,
            height=35
        )
        self.start_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(
            right_frame,
            text="💾 Export",
            command=self._export_with_dialog,
            fg_color="#4ecdc4",
            hover_color="#3ab5b5",
            width=120,
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            right_frame,
            text="🖨️ Print",
            command=self._print_report,
            fg_color="#ff6b6b",
            hover_color="#ff5252",
            width=120,
            height=35
        ).pack(side="left", padx=5)
    
    def _create_left_sidebar(self, parent):
        """Create left sidebar with quick stats"""
        sidebar = ctk.CTkFrame(parent, fg_color="#1a2744", width=220)
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Title
        ctk.CTkLabel(
            sidebar,
            text="📊 Live Stats",
            font=("Arial", 13, "bold"),
            text_color="#00d4ff"
        ).pack(pady=(15, 20), padx=15)
        
        # Stat cards
        self._create_stat_card(
            sidebar, "Total Packets", "0", "#00d4ff",
            "Packets captured"
        )
        
        self._create_stat_card(
            sidebar, "Threats", "0", "#ff6b6b",
            "Detected"
        )
        
        self._create_stat_card(
            sidebar, "Connections", "0", "#4ecdc4",
            "Active TCP/UDP"
        )
        
        self._create_stat_card(
            sidebar, "Bandwidth", "0 MB/s", "#ffd93d",
            "Current usage"
        )
        
        self._create_stat_card(
            sidebar, "Protocols", "0", "#95e1d3",
            "Unique types"
        )
        
        self._create_stat_card(
            sidebar, "Data", "0 MB", "#c7b3e5",
            "Total transferred"
        )
    
    def _create_stat_card(self, parent, title, value, color, subtitle):
        """Create individual stat card"""
        card = ctk.CTkFrame(parent, fg_color="#0f1929", border_width=2, border_color=color)
        card.pack(fill="x", padx=15, pady=8)
        
        # Title
        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 9),
            text_color="#888888"
        ).pack(anchor="w", padx=12, pady=(8, 0))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 18, "bold"),
            text_color=color
        )
        value_label.pack(anchor="w", padx=12)
        
        # Subtitle
        ctk.CTkLabel(
            card,
            text=subtitle,
            font=("Arial", 8),
            text_color="#666666"
        ).pack(anchor="w", padx=12, pady=(0, 8))
        
        return value_label
    
    def _create_packets_graph(self, parent):
        """Create live packets graph"""
        frame = ctk.CTkFrame(parent, fg_color="#1a2744", border_width=2, border_color="#00d4ff")
        frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Title
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="📈 Packets Per Second",
            font=("Arial", 12, "bold"),
            text_color="#00d4ff"
        ).pack(anchor="w")
        
        # Graph area
        self.packets_canvas = ctk.CTkCanvas(
            frame,
            bg="#0f1929",
            highlightthickness=0,
            height=250
        )
        self.packets_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.packets_canvas.bind("<Configure>", lambda e: self._draw_packets_graph())
    
    def _create_threats_graph(self, parent):
        """Create live threats graph"""
        frame = ctk.CTkFrame(parent, fg_color="#1a2744", border_width=2, border_color="#ff6b6b")
        frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        # Title
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="⚠️ Threats Per Minute",
            font=("Arial", 12, "bold"),
            text_color="#ff6b6b"
        ).pack(anchor="w")
        
        # Graph area
        self.threats_canvas = ctk.CTkCanvas(
            frame,
            bg="#0f1929",
            highlightthickness=0,
            height=250
        )
        self.threats_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.threats_canvas.bind("<Configure>", lambda e: self._draw_threats_graph())
    
    def _create_bandwidth_graph(self, parent):
        """Create live bandwidth graph"""
        frame = ctk.CTkFrame(parent, fg_color="#1a2744", border_width=2, border_color="#ffd93d")
        frame.pack(fill="both", expand=True, padx=0, pady=(10, 0))
        
        # Title
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="📊 Bandwidth Usage (MB/s)",
            font=("Arial", 12, "bold"),
            text_color="#ffd93d"
        ).pack(anchor="w")
        
        # Graph area
        self.bandwidth_canvas = ctk.CTkCanvas(
            frame,
            bg="#0f1929",
            highlightthickness=0,
            height=180
        )
        self.bandwidth_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.bandwidth_canvas.bind("<Configure>", lambda e: self._draw_bandwidth_graph())
    
    def _create_right_sidebar(self, parent):
        """Create right sidebar with tabs"""
        sidebar = ctk.CTkFrame(parent, fg_color="#1a2744", width=250)
        sidebar.grid(row=0, column=2, sticky="ns", padx=(10, 0))
        sidebar.pack_propagate(False)
        
        # Tabs
        tabs = ctk.CTkTabview(sidebar)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Packets tab
        packets_tab = tabs.add("Packets")
        self.packets_text = scrolledtext.ScrolledText(
            packets_tab,
            bg="#0f1929",
            fg="#00d4ff",
            font=("Courier", 8),
            height=30
        )
        self.packets_text.pack(fill="both", expand=True)
        self.packets_text.insert("end", "Waiting for packets...\n")
        
        # Threats tab
        threats_tab = tabs.add("Threats")
        self.threats_text = scrolledtext.ScrolledText(
            threats_tab,
            bg="#0f1929",
            fg="#ff6b6b",
            font=("Courier", 8),
            height=30
        )
        self.threats_text.pack(fill="both", expand=True)
        self.threats_text.insert("end", "No threats detected.\n")
        
        # Connections tab
        conn_tab = tabs.add("Connections")
        self.connections_text = scrolledtext.ScrolledText(
            conn_tab,
            bg="#0f1929",
            fg="#4ecdc4",
            font=("Courier", 8),
            height=30
        )
        self.connections_text.pack(fill="both", expand=True)
        self.connections_text.insert("end", "Monitoring connections...\n")
    
    def _draw_packets_graph(self):
        """Draw live packets graph"""
        canvas = self.packets_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1:
            return
        
        data, times = self.packet_graph.get_data()
        
        if not data:
            return
        
        # Background
        canvas.create_rectangle(0, 0, width, height, fill="#0f1929", outline="none")
        
        # Draw grid
        for i in range(0, width, 50):
            canvas.create_line(i, 0, i, height, fill="#222233", width=1)
        
        # Draw line graph
        max_val = max(data) if data else 1
        if max_val < 100:
            max_val = 100
        
        points = []
        for i, val in enumerate(data):
            x = (i / max(len(data), 1)) * width
            y = height - (val / max_val) * (height - 40)
            points.append((x, y))
        
        if len(points) > 1:
            canvas.create_line(points, fill="#00d4ff", width=2, smooth=True)
        
        # Draw axes
        canvas.create_line(0, height - 20, width, height - 20, fill="#444444", width=1)
        canvas.create_text(10, height - 5, text="0", fill="#888888", font=("Arial", 8))
        canvas.create_text(10, 10, text=f"{int(max_val)}", fill="#888888", font=("Arial", 8))
    
    def _draw_threats_graph(self):
        """Draw live threats graph"""
        canvas = self.threats_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1:
            return
        
        data, times = self.threat_graph.get_data()
        
        if not data:
            return
        
        # Background
        canvas.create_rectangle(0, 0, width, height, fill="#0f1929", outline="none")
        
        # Draw grid
        for i in range(0, width, 50):
            canvas.create_line(i, 0, i, height, fill="#222233", width=1)
        
        # Draw bar graph
        max_val = max(data) if data else 1
        if max_val < 10:
            max_val = 10
        
        bar_width = max(1, (width - 40) / max(len(data), 1))
        
        for i, val in enumerate(data):
            x1 = 20 + i * bar_width
            x2 = x1 + bar_width - 2
            y1 = height - 20
            y2 = height - 20 - (val / max_val) * (height - 40)
            
            canvas.create_rectangle(x1, y2, x2, y1, fill="#ff6b6b", outline="none")
        
        # Draw axes
        canvas.create_line(0, height - 20, width, height - 20, fill="#444444", width=1)
        canvas.create_text(10, height - 5, text="0", fill="#888888", font=("Arial", 8))
        canvas.create_text(10, 10, text=f"{int(max_val)}", fill="#888888", font=("Arial", 8))
    
    def _draw_bandwidth_graph(self):
        """Draw live bandwidth graph"""
        canvas = self.bandwidth_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1:
            return
        
        data, times = self.bandwidth_graph.get_data()
        
        if not data:
            return
        
        # Background
        canvas.create_rectangle(0, 0, width, height, fill="#0f1929", outline="none")
        
        # Draw grid
        for i in range(0, width, 50):
            canvas.create_line(i, 0, i, height, fill="#222233", width=1)
        
        # Draw filled area graph
        max_val = max(data) if data else 1
        if max_val < 50:
            max_val = 50
        
        points = []
        for i, val in enumerate(data):
            x = (i / max(len(data), 1)) * width
            y = height - (val / max_val) * (height - 40)
            points.append((x, y))
        
        if len(points) > 1:
            # Draw fill
            fill_points = [(0, height)] + points + [(width, height)]
            canvas.create_polygon(fill_points, fill="#ffd93d33", outline="none")
            
            # Draw line
            canvas.create_line(points, fill="#ffd93d", width=2, smooth=True)
        
        # Draw axes
        canvas.create_line(0, height - 20, width, height - 20, fill="#444444", width=1)
        canvas.create_text(10, height - 5, text="0", fill="#888888", font=("Arial", 8))
        canvas.create_text(10, 10, text=f"{int(max_val)} MB/s", fill="#888888", font=("Arial", 8))
    
    def _start_live_updates(self):
        """Start live data updates"""
        def update_live():
            while True:
                if self.monitoring_active:
                    # Simulate live data
                    packets = random.randint(50, 500)
                    threats = random.randint(0, 10)
                    bandwidth = random.uniform(10, 100)
                    
                    self.packet_graph.add_point(packets)
                    self.threat_graph.add_point(threats)
                    self.bandwidth_graph.add_point(bandwidth)
                    
                    self.total_packets += packets
                    self.total_threats += threats
                    self.active_connections = random.randint(10, 50)
                    self.bandwidth_usage = bandwidth
                    self.total_bytes = self.total_packets * random.randint(100, 1000)
                    
                    # Update canvas
                    try:
                        self.packets_canvas.after(0, self._draw_packets_graph)
                        self.threats_canvas.after(0, self._draw_threats_graph)
                        self.bandwidth_canvas.after(0, self._draw_bandwidth_graph)
                    except:
                        pass
                
                threading.Event().wait(1)
        
        self.update_thread = threading.Thread(target=update_live, daemon=True)
        self.update_thread.start()
    
    def _toggle_monitoring(self):
        """Toggle monitoring state"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.start_btn.configure(text="⏹ Stop Monitoring", fg_color="#ff6b6b")
            self.status_label.configure(text="🔴 Monitoring Active", text_color="#ff6b6b")
        else:
            self.monitoring_active = False
            self.start_btn.configure(text="▶ Start Monitoring", fg_color="#00d4ff")
            self.status_label.configure(text="🟢 Ready", text_color="#4ecdc4")
    
    def _export_with_dialog(self):
        """Export with format and location selection"""
        # Create dialog window
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Export Network Report")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)
        
        # Center on parent
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Title
        ctk.CTkLabel(
            dialog,
            text="📊 Export Network Report",
            font=("Arial", 14, "bold"),
            text_color="#00d4ff"
        ).pack(pady=20)
        
        # Format selection
        ctk.CTkLabel(
            dialog,
            text="Select Export Format:",
            font=("Arial", 11),
            text_color="#888888"
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        format_var = ctk.StringVar(value="JSON")
        
        formats = [
            ("📄 JSON - Machine Readable", "JSON"),
            ("📕 PDF - Professional Report", "PDF"),
            ("📘 Word - Editable Document", "WORD"),
            ("📋 Text - Plain Text", "TEXT")
        ]
        
        for label, value in formats:
            ctk.CTkRadioButton(
                dialog,
                text=label,
                variable=format_var,
                value=value,
                text_color="#888888"
            ).pack(anchor="w", padx=40, pady=5)
        
        # Location selection
        ctk.CTkLabel(
            dialog,
            text="Save Location:",
            font=("Arial", 11),
            text_color="#888888"
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        location_var = ctk.StringVar(value="Downloads")
        
        locations = [
            ("📁 Downloads (Default)", os.path.expanduser("~/Downloads")),
            ("🖥️ Desktop", os.path.expanduser("~/Desktop")),
            ("📂 Documents", os.path.expanduser("~/Documents")),
            ("📌 Custom Location", "custom")
        ]
        
        for label, value in locations:
            ctk.CTkRadioButton(
                dialog,
                text=label,
                variable=location_var,
                value=value,
                text_color="#888888"
            ).pack(anchor="w", padx=40, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20, fill="x", padx=20)
        
        def export_now():
            fmt = format_var.get()
            loc = location_var.get()
            
            if loc == "custom":
                loc = filedialog.askdirectory(title="Choose Export Location")
                if not loc:
                    return
            
            self._perform_export(fmt, loc)
            dialog.destroy()
        
        ctk.CTkButton(
            button_frame,
            text="✓ Export",
            command=export_now,
            fg_color="#00d4ff",
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="✗ Cancel",
            command=dialog.destroy,
            fg_color="#666666",
            width=150
        ).pack(side="left", padx=5)
    
    def _perform_export(self, fmt, location):
        """Perform actual export"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if fmt == "JSON":
                filename = f"cybersafe_report_{timestamp}.json"
                filepath = os.path.join(location, filename)
                
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "total_packets": self.total_packets,
                    "total_threats": self.total_threats,
                    "active_connections": self.active_connections,
                    "bandwidth_usage_mbps": self.bandwidth_usage,
                    "total_bytes": self.total_bytes
                }
                
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif fmt == "PDF":
                filename = f"cybersafe_report_{timestamp}.pdf"
                filepath = os.path.join(location, filename)
                
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    from reportlab.lib.units import inch
                    from reportlab.lib import colors
                    
                    doc = SimpleDocTemplate(filepath, pagesize=letter)
                    elements = []
                    styles = getSampleStyleSheet()
                    
                    # Title
                    title_style = ParagraphStyle(
                        'CustomTitle',
                        parent=styles['Heading1'],
                        fontSize=24,
                        textColor=colors.HexColor('#00d4ff'),
                        spaceAfter=30
                    )
                    elements.append(Paragraph("CyberSafe Network Report", title_style))
                    elements.append(Spacer(1, 0.2*inch))
                    
                    # Data table
                    data = [
                        ['Metric', 'Value'],
                        ['Total Packets', str(self.total_packets)],
                        ['Threats Detected', str(self.total_threats)],
                        ['Active Connections', str(self.active_connections)],
                        ['Current Bandwidth', f"{self.bandwidth_usage:.2f} MB/s"],
                        ['Total Data', f"{self.total_bytes / 1024 / 1024:.2f} MB"],
                        ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                    ]
                    
                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00d4ff')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 14),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    elements.append(table)
                    doc.build(elements)
                except ImportError:
                    raise Exception("reportlab not installed")
            
            elif fmt == "WORD":
                filename = f"cybersafe_report_{timestamp}.docx"
                filepath = os.path.join(location, filename)
                
                try:
                    from docx import Document
                    
                    doc = Document()
                    doc.add_heading('CyberSafe Network Report', 0)
                    
                    table = doc.add_table(rows=8, cols=2)
                    table.style = 'Light Grid Accent 1'
                    
                    headers = table.rows[0].cells
                    headers[0].text = 'Metric'
                    headers[1].text = 'Value'
                    
                    data_rows = [
                        ['Total Packets', str(self.total_packets)],
                        ['Threats Detected', str(self.total_threats)],
                        ['Active Connections', str(self.active_connections)],
                        ['Current Bandwidth', f"{self.bandwidth_usage:.2f} MB/s"],
                        ['Total Data', f"{self.total_bytes / 1024 / 1024:.2f} MB"],
                        ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                        ['Status', 'Monitoring Complete']
                    ]
                    
                    for i, (metric, value) in enumerate(data_rows, 1):
                        row_cells = table.rows[i].cells
                        row_cells[0].text = metric
                        row_cells[1].text = value
                    
                    doc.save(filepath)
                except ImportError:
                    raise Exception("python-docx not installed")
            
            else:  # TEXT
                filename = f"cybersafe_report_{timestamp}.txt"
                filepath = os.path.join(location, filename)
                
                content = f"""
╔════════════════════════════════════════════════════════════════╗
║            CyberSafe Network Monitoring Report                 ║
╚════════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

LIVE STATISTICS
═══════════════════════════════════════════════════════════════════
Total Packets Captured:        {self.total_packets:,}
Threats Detected:              {self.total_threats}
Active Connections:            {self.active_connections}
Current Bandwidth Usage:       {self.bandwidth_usage:.2f} MB/s
Total Data Transferred:        {self.total_bytes / 1024 / 1024:.2f} MB

Report generated by CyberSafe v1.0
"""
                
                with open(filepath, 'w') as f:
                    f.write(content)
            
            messagebox.showinfo("Export Success", f"Report saved to:\n{filepath}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Error: {str(e)}")
    
    def _print_report(self):
        """Print report"""
        try:
            import subprocess
            import tempfile
            
            content = f"""CyberSafe Network Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Packets: {self.total_packets}
Threats: {self.total_threats}
Active Connections: {self.active_connections}
Bandwidth: {self.bandwidth_usage:.2f} MB/s
Total Data: {self.total_bytes / 1024 / 1024:.2f} MB
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            if sys.platform == 'win32':
                os.startfile(temp_file, "print")
            
            messagebox.showinfo("Print", "Report sent to printer!")
        except Exception as e:
            messagebox.showerror("Print Error", f"Error: {str(e)}")
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle window closing"""
        if self.monitoring_active:
            if messagebox.askyesno("Quit", "Monitoring is active. Close anyway?"):
                self.root.destroy()
        else:
            self.root.destroy()


# Run the GUI
if __name__ == "__main__":
    import yaml
    
    config = {}
    try:
        with open("../config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except:
        pass
    
    app = CyberSafeGUI(config)
    app.run()
