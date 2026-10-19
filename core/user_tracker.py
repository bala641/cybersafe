"""
User tracking module for CyberSafe
Tracks user information and sends data to the analytics backend on first launch
"""

import os
import json
import socket
import platform
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
import threading
import requests
from utils.logger import logger


class UserTracker:
    """Track user data and send to analytics backend"""

    TRACKING_FILE = Path.home() / '.cybersafe' / 'tracking.json'
    API_ENDPOINT = 'https://cybersafe-website.vercel.app/api/track'
    
    def __init__(self):
        """Initialize user tracker"""
        self.tracking_file = self.TRACKING_FILE
        self.user_id = self._get_or_create_user_id()
        self.session_id = str(uuid.uuid4())
        self.install_time = None
        
    def _get_or_create_user_id(self):
        """Get existing user ID or create new one"""
        try:
            # Ensure directory exists
            self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Try to load existing user ID
            if self.tracking_file.exists():
                with open(self.tracking_file, 'r') as f:
                    data = json.load(f)
                    if 'user_id' in data:
                        return data['user_id']
            
            # Generate new user ID
            user_id = self._generate_user_id()
            self._save_user_id(user_id)
            return user_id
            
        except Exception as e:
            logger.error(f"Error creating user ID: {e}")
            return self._generate_user_id()
    
    def _generate_user_id(self):
        """Generate unique user ID based on machine and random data"""
        try:
            # Get machine identifier
            machine_name = socket.gethostname()
            mac_address = uuid.getnode()
            
            # Create hash
            identifier = f"{machine_name}_{mac_address}_{uuid.uuid4()}"
            user_hash = hashlib.sha256(identifier.encode()).hexdigest()[:12]
            
            return f"user_{user_hash}_{int(datetime.now().timestamp())}"
        except Exception as e:
            logger.error(f"Error generating user ID: {e}")
            return f"user_{uuid.uuid4().hex[:12]}"
    
    def _save_user_id(self, user_id):
        """Save user ID to tracking file"""
        try:
            data = {
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'version': '2.5.1'
            }
            
            with open(self.tracking_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"User ID saved: {user_id}")
        except Exception as e:
            logger.error(f"Error saving user ID: {e}")
    
    def get_system_info(self):
        """Get system information"""
        try:
            return {
                'platform': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def track_first_launch(self):
        """Track first launch of the application"""
        event_data = {
            'eventType': 'first_launch',
            'userId': self.user_id,
            'sessionId': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'systemInfo': self.get_system_info(),
            'version': '2.5.1'
        }
        
        self._send_tracking_data(event_data)
    
    def track_app_launch(self):
        """Track app launch"""
        event_data = {
            'eventType': 'app_launch',
            'userId': self.user_id,
            'sessionId': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'systemInfo': self.get_system_info()
        }
        
        self._send_tracking_data(event_data)
    
    def track_download(self, file_name='CyberSafe-Installer.exe'):
        """Track application download"""
        event_data = {
            'eventType': 'download',
            'userId': self.user_id,
            'downloadUrl': file_name,
            'timestamp': datetime.now().isoformat(),
            'userAgent': f"CyberSafe/{self._get_app_version()}",
            'platform': platform.system()
        }
        
        self._send_tracking_data(event_data)
    
    def track_feature_usage(self, feature_name, action='used'):
        """Track feature usage"""
        event_data = {
            'eventType': 'feature_usage',
            'userId': self.user_id,
            'feature': feature_name,
            'action': action,
            'timestamp': datetime.now().isoformat()
        }
        
        self._send_tracking_data(event_data)
    
    def track_error(self, error_type, error_message):
        """Track error occurrence"""
        event_data = {
            'eventType': 'error',
            'userId': self.user_id,
            'errorType': error_type,
            'errorMessage': error_message,
            'timestamp': datetime.now().isoformat(),
            'systemInfo': self.get_system_info()
        }
        
        self._send_tracking_data(event_data)
    
    def track_session_end(self, session_duration=0):
        """Track end of session"""
        event_data = {
            'eventType': 'session_end',
            'userId': self.user_id,
            'sessionId': self.session_id,
            'sessionDuration': session_duration,
            'timestamp': datetime.now().isoformat()
        }
        
        self._send_tracking_data(event_data)
    
    def _send_tracking_data(self, event_data):
        """Send tracking data to backend (async to not block UI)"""
        def send():
            try:
                response = requests.post(
                    self.API_ENDPOINT,
                    json=event_data,
                    timeout=5,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    logger.debug(f"Tracking event sent: {event_data['eventType']}")
                else:
                    logger.debug(f"Tracking response: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.debug("Tracking request timeout (expected for slow connections)")
            except requests.exceptions.ConnectionError:
                logger.debug("Tracking connection error (no internet)")
            except Exception as e:
                logger.debug(f"Tracking error: {e}")
        
        # Send tracking data in background thread to not block UI
        thread = threading.Thread(target=send, daemon=True)
        thread.start()
    
    def _get_app_version(self):
        """Get app version"""
        try:
            # Try to read from version file
            version_file = Path(__file__).parent.parent / 'VERSION'
            if version_file.exists():
                return version_file.read_text().strip()
        except:
            pass
        
        return '2.5.1'


# Global tracker instance
_tracker = None


def get_tracker():
    """Get global tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = UserTracker()
    return _tracker


def track_first_launch():
    """Track first application launch"""
    try:
        tracker = get_tracker()
        tracker.track_first_launch()
        logger.info(f"First launch tracked for user: {tracker.user_id}")
    except Exception as e:
        logger.error(f"Error tracking first launch: {e}")


def track_app_launch():
    """Track application launch"""
    try:
        tracker = get_tracker()
        tracker.track_app_launch()
    except Exception as e:
        logger.error(f"Error tracking app launch: {e}")


def track_feature(feature_name, action='used'):
    """Track feature usage"""
    try:
        tracker = get_tracker()
        tracker.track_feature_usage(feature_name, action)
    except Exception as e:
        logger.error(f"Error tracking feature: {e}")


def track_error(error_type, error_message):
    """Track error"""
    try:
        tracker = get_tracker()
        tracker.track_error(error_type, error_message)
    except Exception as e:
        logger.error(f"Error tracking error: {e}")


def track_session_end(duration=0):
    """Track session end"""
    try:
        tracker = get_tracker()
        tracker.track_session_end(duration)
    except Exception as e:
        logger.error(f"Error tracking session end: {e}")
