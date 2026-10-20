"""
Database Models and Management
Store packet captures, threats, and statistics
"""

import sqlite3
import threading
import queue
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import json


class DatabaseManager:
    """
    Manage database operations for network monitoring data
    """
    
    def __init__(self, db_path: str = "data/network_monitor.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.lock = threading.Lock()
        self.packet_queue = queue.Queue(maxsize=1000)
        self.batch_size = 100
        
        self._init_database()
        
        # Start background writer thread
        self.writer_active = True
        self.writer_thread = threading.Thread(target=self._batch_writer, daemon=True)
        self.writer_thread.start()
        
        print(f"Database initialized: {self.db_path.absolute()}")
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Packets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS packets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    number INTEGER,
                    protocol TEXT,
                    src_ip TEXT,
                    dst_ip TEXT,
                    src_port INTEGER,
                    dst_port INTEGER,
                    src_mac TEXT,
                    dst_mac TEXT,
                    length INTEGER,
                    tcp_flags INTEGER,
                    summary TEXT,
                    data TEXT
                )
            ''')
            
            # Threats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    type TEXT NOT NULL,
                    severity TEXT,
                    source_ip TEXT,
                    target_ip TEXT,
                    description TEXT,
                    data TEXT
                )
            ''')
            
            # Connections table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    local_ip TEXT,
                    local_port INTEGER,
                    remote_ip TEXT,
                    remote_port INTEGER,
                    protocol TEXT,
                    status TEXT,
                    pid INTEGER,
                    process_name TEXT,
                    bytes_sent INTEGER DEFAULT 0,
                    bytes_received INTEGER DEFAULT 0
                )
            ''')
            
            # Statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    total_packets INTEGER,
                    tcp_packets INTEGER,
                    udp_packets INTEGER,
                    icmp_packets INTEGER,
                    total_bytes INTEGER,
                    threats_detected INTEGER,
                    active_connections INTEGER
                )
            ''')
            
            # Create indices
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_packets_timestamp ON packets(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_packets_src_ip ON packets(src_ip)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_packets_dst_ip ON packets(dst_ip)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threats_timestamp ON threats(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threats_type ON threats(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_connections_timestamp ON connections(timestamp)')
            
            conn.commit()
    
    def queue_packet(self, packet_info: dict):
        """Queue packet for batch insertion"""
        try:
            self.packet_queue.put_nowait(packet_info)
        except queue.Full:
            # Queue full, skip packet
            pass
    
    def _batch_writer(self):
        """Background thread for batch database writes"""
        while self.writer_active:
            packets = []
            
            try:
                # Collect packets for batch
                while len(packets) < self.batch_size:
                    try:
                        packet = self.packet_queue.get(timeout=1.0)
                        packets.append(packet)
                    except queue.Empty:
                        break
                
                if packets:
                    self._insert_packets_batch(packets)
            
            except Exception as e:
                print(f"Batch writer error: {e}")
    
    def _insert_packets_batch(self, packets: List[dict]):
        """Insert multiple packets in a single transaction"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                packet_data = []
                for p in packets:
                    packet_data.append((
                        p.get('timestamp', datetime.now()).isoformat() if isinstance(p.get('timestamp'), datetime) else p.get('timestamp'),
                        p.get('number'),
                        p.get('protocol_name'),
                        p.get('src_ip'),
                        p.get('dst_ip'),
                        p.get('src_port'),
                        p.get('dst_port'),
                        p.get('src_mac'),
                        p.get('dst_mac'),
                        p.get('length'),
                        p.get('tcp_flags'),
                        p.get('summary'),
                        json.dumps({k: str(v) if isinstance(v, datetime) else v for k, v in p.items() if k not in ['timestamp', 'number', 'raw']})
                    ))
                
                cursor.executemany('''
                    INSERT INTO packets (timestamp, number, protocol, src_ip, dst_ip, src_port, dst_port,
                                       src_mac, dst_mac, length, tcp_flags, summary, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', packet_data)
                
                conn.commit()
    
    def insert_threat(self, threat: dict):
        """Insert a threat record"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO threats (timestamp, type, severity, source_ip, target_ip, description, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    threat.get('timestamp', datetime.now()).isoformat() if isinstance(threat.get('timestamp'), datetime) else threat.get('timestamp'),
                    threat.get('type'),
                    threat.get('severity'),
                    threat.get('source_ip'),
                    threat.get('target_ip'),
                    threat.get('description'),
                    json.dumps({k: str(v) if isinstance(v, datetime) else v for k, v in threat.items()})
                ))
                
                conn.commit()
    
    def insert_connection(self, connection: dict):
        """Insert a connection record"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO connections (timestamp, local_ip, local_port, remote_ip, remote_port,
                                           protocol, status, pid, process_name, bytes_sent, bytes_received)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    connection.get('local_ip'),
                    connection.get('local_port'),
                    connection.get('remote_ip'),
                    connection.get('remote_port'),
                    connection.get('type'),
                    connection.get('status'),
                    connection.get('pid'),
                    connection.get('process_name'),
                    connection.get('bytes_sent', 0),
                    connection.get('bytes_received', 0)
                ))
                
                conn.commit()
    
    def get_packets(self, limit: int = 100, offset: int = 0, 
                   filter_protocol: str = None, filter_ip: str = None) -> List[dict]:
        """Retrieve packets with optional filtering"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = 'SELECT * FROM packets WHERE 1=1'
                params = []
                
                if filter_protocol:
                    query += ' AND protocol = ?'
                    params.append(filter_protocol)
                
                if filter_ip:
                    query += ' AND (src_ip = ? OR dst_ip = ?)'
                    params.extend([filter_ip, filter_ip])
                
                query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                
                return [dict(row) for row in cursor.fetchall()]
    
    def get_threats(self, limit: int = 100, severity: str = None) -> List[dict]:
        """Retrieve threats"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = 'SELECT * FROM threats WHERE 1=1'
                params = []
                
                if severity:
                    query += ' AND severity = ?'
                    params.append(severity)
                
                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                
                return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self, time_range: int = 3600) -> dict:
        """Get statistics for the last time_range seconds"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff = (datetime.now() - timedelta(seconds=time_range)).isoformat()
                
                # Packet statistics
                cursor.execute('''
                    SELECT COUNT(*) as count, SUM(length) as bytes, protocol
                    FROM packets
                    WHERE timestamp >= ?
                    GROUP BY protocol
                ''', (cutoff,))
                
                protocol_stats = {}
                for row in cursor.fetchall():
                    protocol_stats[row[2] or 'Unknown'] = {
                        'count': row[0],
                        'bytes': row[1] or 0
                    }
                
                # Threat statistics
                cursor.execute('''
                    SELECT COUNT(*) as count, type, severity
                    FROM threats
                    WHERE timestamp >= ?
                    GROUP BY type, severity
                ''', (cutoff,))
                
                threat_stats = {}
                for row in cursor.fetchall():
                    key = f"{row[1]}_{row[2]}"
                    threat_stats[key] = row[0]
                
                return {
                    'time_range': time_range,
                    'protocols': protocol_stats,
                    'threats': threat_stats
                }
    
    def cleanup_old_data(self, retention_days: int = 30):
        """Remove data older than retention period"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff = (datetime.now() - timedelta(days=retention_days)).isoformat()
                
                cursor.execute('DELETE FROM packets WHERE timestamp < ?', (cutoff,))
                packets_deleted = cursor.rowcount
                
                cursor.execute('DELETE FROM threats WHERE timestamp < ?', (cutoff,))
                threats_deleted = cursor.rowcount
                
                cursor.execute('DELETE FROM connections WHERE timestamp < ?', (cutoff,))
                connections_deleted = cursor.rowcount
                
                conn.commit()
                
                print(f"Cleaned up old data: {packets_deleted} packets, {threats_deleted} threats, {connections_deleted} connections")
    
    def vacuum(self):
        """Optimize database"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('VACUUM')
                print("Database vacuumed")
    
    def close(self):
        """Close database and cleanup"""
        self.writer_active = False
        if self.writer_thread.is_alive():
            self.writer_thread.join(timeout=5)


# Testing
if __name__ == "__main__":
    print("CyberSafe Database Manager Test")
    print("=" * 50)
    
    db = DatabaseManager("data/test_network_monitor.db")
    
    # Test packet insertion
    packet = {
        'timestamp': datetime.now(),
        'number': 1,
        'protocol_name': 'TCP',
        'src_ip': '192.168.1.100',
        'dst_ip': '93.184.216.34',
        'src_port': 54321,
        'dst_port': 443,
        'length': 60,
        'summary': 'TCP 54321 > 443 [SYN]'
    }
    
    db.queue_packet(packet)
    
    # Test threat insertion
    threat = {
        'timestamp': datetime.now(),
        'type': 'PORT_SCAN',
        'severity': 'HIGH',
        'source_ip': '192.168.1.100',
        'description': 'Port scan detected'
    }
    
    db.insert_threat(threat)
    
    import time
    time.sleep(2)  # Wait for batch writer
    
    # Query data
    packets = db.get_packets(limit=10)
    print(f"\nPackets in database: {len(packets)}")
    
    threats = db.get_threats()
    print(f"Threats in database: {len(threats)}")
    
    stats = db.get_statistics()
    print(f"\nStatistics: {stats}")
    
    db.close()
    print("\nDatabase test completed")
