"""
Logging System
Centralized logging for packets, threats, and system events
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
import os


class Logger:
    """
    Multi-purpose logger for CyberSafe
    """
    
    def __init__(self, log_dir: str = "logs", level: str = "INFO"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.level = getattr(logging, level.upper(), logging.INFO)
        
        # Create separate loggers for different purposes
        self.packet_logger = self._create_logger('packets', 'packet_capture.log')
        self.threat_logger = self._create_logger('threats', 'threats.log')
        self.system_logger = self._create_logger('system', 'system.log')
        self.alert_logger = self._create_logger('alerts', 'alerts.log')
        
        print(f"Logger initialized: {self.log_dir.absolute()}")
    
    def _create_logger(self, name: str, filename: str) -> logging.Logger:
        """Create a logger with file and console handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(self.level)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # File handler
        file_handler = logging.FileHandler(
            self.log_dir / filename,
            encoding='utf-8'
        )
        file_handler.setLevel(self.level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_packet(self, packet_info: dict, level: str = "INFO"):
        """Log captured packet"""
        try:
            log_entry = {
                'timestamp': packet_info.get('timestamp', datetime.now()).isoformat(),
                'number': packet_info.get('number'),
                'protocol': packet_info.get('protocol_name'),
                'src_ip': packet_info.get('src_ip'),
                'dst_ip': packet_info.get('dst_ip'),
                'src_port': packet_info.get('src_port'),
                'dst_port': packet_info.get('dst_port'),
                'length': packet_info.get('length'),
                'summary': packet_info.get('summary')
            }
            
            log_level = getattr(logging, level.upper(), logging.INFO)
            self.packet_logger.log(log_level, json.dumps(log_entry))
        
        except Exception as e:
            self.system_logger.error(f"Error logging packet: {e}")
    
    def log_threat(self, threat: dict):
        """Log detected threat"""
        try:
            log_entry = {
                'timestamp': threat.get('timestamp', datetime.now()).isoformat() if isinstance(threat.get('timestamp'), datetime) else threat.get('timestamp'),
                'type': threat.get('type'),
                'severity': threat.get('severity'),
                'description': threat.get('description'),
                'source_ip': threat.get('source_ip'),
                'target_ip': threat.get('target_ip'),
                'details': {k: v for k, v in threat.items() if k not in ['timestamp', 'type', 'severity', 'description', 'source_ip', 'target_ip']}
            }
            
            # Log based on severity
            if threat.get('severity') == 'CRITICAL':
                self.threat_logger.critical(json.dumps(log_entry))
            elif threat.get('severity') == 'HIGH':
                self.threat_logger.error(json.dumps(log_entry))
            elif threat.get('severity') == 'MEDIUM':
                self.threat_logger.warning(json.dumps(log_entry))
            else:
                self.threat_logger.info(json.dumps(log_entry))
        
        except Exception as e:
            self.system_logger.error(f"Error logging threat: {e}")
    
    def log_alert(self, alert: dict):
        """Log alert"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'alert_type': alert.get('type'),
                'message': alert.get('message'),
                'data': alert.get('data', {})
            }
            
            self.alert_logger.warning(json.dumps(log_entry))
        
        except Exception as e:
            self.system_logger.error(f"Error logging alert: {e}")
    
    def log_system(self, message: str, level: str = "INFO"):
        """Log system message"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.system_logger.log(log_level, message)
    
    def info(self, message: str):
        """Log info message"""
        self.system_logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.system_logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.system_logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.system_logger.critical(message)
    
    def get_recent_threats(self, count: int = 100) -> list:
        """Read recent threat logs"""
        threats = []
        threat_log_file = self.log_dir / 'threats.log'
        
        try:
            if threat_log_file.exists():
                with open(threat_log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    for line in lines[-count:]:
                        try:
                            # Parse log line
                            # Format: timestamp - name - level - json_data
                            parts = line.split(' - ', 3)
                            if len(parts) == 4:
                                threat_data = json.loads(parts[3])
                                threats.append(threat_data)
                        except:
                            continue
        
        except Exception as e:
            self.system_logger.error(f"Error reading threat logs: {e}")
        
        return threats
    
    def clear_logs(self, log_type: str = None):
        """Clear log files"""
        try:
            if log_type:
                log_file = self.log_dir / f"{log_type}.log"
                if log_file.exists():
                    log_file.unlink()
                    self.system_logger.info(f"Cleared {log_type} logs")
            else:
                # Clear all logs
                for log_file in self.log_dir.glob("*.log"):
                    log_file.unlink()
                self.system_logger.info("Cleared all logs")
        
        except Exception as e:
            self.system_logger.error(f"Error clearing logs: {e}")


# Testing
if __name__ == "__main__":
    print("CyberSafe Logger Test")
    print("=" * 50)
    
    logger = Logger()
    
    # Test system logging
    logger.info("System started")
    logger.warning("This is a warning")
    logger.error("This is an error")
    
    # Test threat logging
    threat = {
        'timestamp': datetime.now(),
        'type': 'PORT_SCAN',
        'severity': 'HIGH',
        'source_ip': '192.168.1.100',
        'description': 'Port scan detected',
        'port_count': 25
    }
    logger.log_threat(threat)
    
    # Test packet logging
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
    logger.log_packet(packet)
    
    print("\nLog files created in ./logs/")
    print("  - packet_capture.log")
    print("  - threats.log")
    print("  - system.log")
    print("  - alerts.log")
