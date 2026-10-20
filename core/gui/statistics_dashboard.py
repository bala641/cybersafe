import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import threading
import time
from datetime import datetime
from collections import deque

class StatisticsDashboard:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        
        # Data storage (keep last 60 seconds)
        self.max_points = 60
        self.timestamps = deque(maxlen=self.max_points)
        self.packet_counts = deque(maxlen=self.max_points)
        self.threat_counts = deque(maxlen=self.max_points)
        self.bandwidth_data = deque(maxlen=self.max_points)
        
        # Statistics
        self.total_packets = 0
        self.total_threats = 0
        self.active_connections = 0
        self.bandwidth_usage = 0
        
        self.setup_ui()
        self.start_data_thread()
    
    def setup_ui(self):
        """Create the dashboard UI"""
        
        # Title
        title = ctk.CTkLabel(
            self.frame,
            text="Network Statistics Dashboard",
            font=("Arial", 24, "bold"),
            text_color="#00d4ff"
        )
        title.pack(pady=20, padx=20)
        
        # Stats Row
        stats_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.create_stat_card(stats_frame, "Total Packets", "0", "#00d4ff", 0)
        self.create_stat_card(stats_frame, "Threats Detected", "0", "#ff4444", 1)
        self.create_stat_card(stats_frame, "Active Connections", "0", "#44ff44", 2)
        self.create_stat_card(stats_frame, "Bandwidth", "0 MB/s", "#ffaa00", 3)
        
        # Store labels for updates
        self.label_packets = None
        self.label_threats = None
        self.label_connections = None
        self.label_bandwidth = None
        
        # Graph Frame
        graph_frame = ctk.CTkFrame(self.frame, fg_color="#0a0a0a", corner_radius=10)
        graph_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 5), dpi=100, facecolor='#0a0a0a')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1a1a1a')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Initialize graph
        self.update_graph()
    
    def create_stat_card(self, parent, title, value, color, column):
        """Create a statistic card"""
        card = ctk.CTkFrame(parent, fg_color="#0a0a0a", corner_radius=10, border_width=2, border_color=color)
        card.grid(row=0, column=column, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 12),
            text_color="#888888"
        )
        title_label.pack(pady=(10, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 18, "bold"),
            text_color=color
        )
        value_label.pack(pady=(5, 10))
        
        # Store reference to update later
        if "Packets" in title:
            self.label_packets = value_label
        elif "Threats" in title:
            self.label_threats = value_label
        elif "Connections" in title:
            self.label_connections = value_label
        elif "Bandwidth" in title:
            self.label_bandwidth = value_label
    
    def update_graph(self):
        """Update the matplotlib graph"""
        self.ax.clear()
        
        # Set up grid
        self.ax.grid(True, alpha=0.2, color='#444444')
        self.ax.set_facecolor('#1a1a1a')
        
        # Plot data
        if len(self.timestamps) > 0:
            x = list(range(len(self.packet_counts)))
            
            # Plot packet counts
            self.ax.plot(x, list(self.packet_counts), 
                        color='#00d4ff', linewidth=2, label='Packets', marker='o')
            self.ax.fill_between(x, self.packet_counts, alpha=0.2, color='#00d4ff')
            
            # Plot threat counts
            self.ax.plot(x, list(self.threat_counts), 
                        color='#ff4444', linewidth=2, label='Threats', marker='s')
            self.ax.fill_between(x, self.threat_counts, alpha=0.2, color='#ff4444')
            
            # Plot bandwidth
            self.ax.plot(x, list(self.bandwidth_data), 
                        color='#ffaa00', linewidth=2, label='Bandwidth (MB/s)', marker='^')
            self.ax.fill_between(x, self.bandwidth_data, alpha=0.2, color='#ffaa00')
        
        # Style
        self.ax.set_xlabel('Time (seconds)', color='#888888')
        self.ax.set_ylabel('Count / Usage', color='#888888')
        self.ax.legend(loc='upper left', facecolor='#1a1a1a', edgecolor='#888888', labelcolor='#ffffff')
        self.ax.tick_params(colors='#888888')
        
        self.canvas.draw()
    
    def generate_sample_data(self):
        """Generate realistic sample data"""
        import random
        
        # Simulate network activity
        packets = random.randint(100, 500)
        threats = random.randint(0, 10)
        bandwidth = random.uniform(0.1, 5.0)
        connections = random.randint(5, 50)
        
        self.total_packets += packets
        self.total_threats += threats
        self.active_connections = connections
        self.bandwidth_usage = bandwidth
        
        # Add to data
        self.timestamps.append(len(self.timestamps))
        self.packet_counts.append(packets)
        self.threat_counts.append(threats)
        self.bandwidth_data.append(bandwidth)
    
    def data_thread(self):
        """Background thread to update data"""
        while True:
            try:
                self.generate_sample_data()
                self.parent.after(0, self.update_display)
                time.sleep(1)  # Update every second
            except:
                break
    
    def update_display(self):
        """Update UI with new data"""
        if self.label_packets:
            self.label_packets.configure(text=str(int(sum(self.packet_counts) / max(1, len(self.packet_counts)))))
        if self.label_threats:
            self.label_threats.configure(text=str(self.total_threats))
        if self.label_connections:
            self.label_connections.configure(text=str(self.active_connections))
        if self.label_bandwidth:
            self.label_bandwidth.configure(text=f"{self.bandwidth_usage:.2f} MB/s")
        
        self.update_graph()
    
    def start_data_thread(self):
        """Start background data collection"""
        thread = threading.Thread(target=self.data_thread, daemon=True)
        thread.start()
    
    def get_frame(self):
        """Return the frame"""
        return self.frame
