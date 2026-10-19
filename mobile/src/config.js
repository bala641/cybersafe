/**
 * CyberSafe Mobile Configuration
 */

export const API_URL = 'http://192.168.1.100:5000'; // Change to your backend IP
export const WS_URL = 'ws://192.168.1.100:5000';

export const CONFIG = {
  // API endpoints
  api: {
    status: '/api/status',
    packets: '/api/packets',
    threats: '/api/threats',
    ports: '/api/ports',
    stats: '/api/stats',
    start: '/api/start',
    stop: '/api/stop',
  },
  
  // Update intervals (ms)
  refreshIntervals: {
    dashboard: 2000,
    packets: 3000,
    threats: 5000,
    stats: 5000,
  },
  
  // Display limits
  limits: {
    packets: 100,
    threats: 50,
    ports: 50,
  },
  
  // Theme
  theme: {
    dark: {
      background: '#1a1a1a',
      surface: '#2d2d2d',
      primary: '#2196F3',
      accent: '#FF9800',
      text: '#ffffff',
      textSecondary: '#b0b0b0',
      success: '#4CAF50',
      warning: '#FF9800',
      error: '#F44336',
    },
    light: {
      background: '#f5f5f5',
      surface: '#ffffff',
      primary: '#2196F3',
      accent: '#FF9800',
      text: '#212121',
      textSecondary: '#757575',
      success: '#4CAF50',
      warning: '#FF9800',
      error: '#F44336',
    },
  },
};

export default CONFIG;
