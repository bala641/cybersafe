# CyberSafe Network Monitor - Quick Start Guide

## 🚀 Installation

### Windows

1. **Install Python 3.9+**
   - Download from [python.org](https://www.python.org/)
   - Check "Add Python to PATH" during installation

2. **Install Npcap (Required for packet capture)**
   - Download from [npcap.com](https://npcap.com/)
   - Install with "WinPcap API-compatible Mode" enabled

3. **Run Installation Script**
   ```cmd
   install.bat
   ```

4. **Start CyberSafe**
   ```cmd
   # Right-click Command Prompt and "Run as Administrator"
   python main.py --gui
   ```

### Linux

1. **Install Dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip libpcap-dev

   # Fedora/RHEL
   sudo dnf install python3 python3-pip libpcap-devel

   # Arch
   sudo pacman -S python python-pip libpcap
   ```

2. **Run Installation Script**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Start CyberSafe**
   ```bash
   sudo python3 main.py --gui
   ```

### macOS

1. **Install Python via Homebrew**
   ```bash
   brew install python3
   ```

2. **Run Installation Script**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Start CyberSafe**
   ```bash
   sudo python3 main.py --gui
   ```

## 📱 Mobile App (Android)

1. **Install Node.js and React Native CLI**
   ```bash
   npm install -g react-native-cli
   ```

2. **Setup Mobile App**
   ```bash
   cd mobile
   npm install
   ```

3. **Configure Backend URL**
   Edit `mobile/src/config.js`:
   ```javascript
   export const API_URL = 'http://YOUR_DESKTOP_IP:5000';
   ```

4. **Run on Android**
   ```bash
   npm run android
   ```

## 🎯 Basic Usage

### Desktop GUI

1. **Select Network Interface**
   - Choose your network adapter from the dropdown
   - Or leave as "auto" for automatic detection

2. **Start Monitoring**
   - Click "Start Capture"
   - Requires administrator/root privileges

3. **View Captured Data**
   - **Dashboard**: Real-time overview
   - **Packets**: Detailed packet list
   - **Threats**: Security alerts
   - **Ports**: Active connections
   - **Statistics**: Network analytics

### Command Line

```bash
# Basic monitoring
sudo python main.py --cli

# Monitor specific interface
sudo python main.py --cli --interface eth0

# Apply packet filter
sudo python main.py --cli --filter "tcp port 80"

# Save to file
sudo python main.py --cli --output capture.pcap
```

### API Server

```bash
# Start API server
sudo python main.py --api

# Access at http://localhost:5000
# API documentation: http://localhost:5000/api/status
```

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
# Network interface
network:
  interface: "auto"  # or eth0, wlan0, etc.

# Threat detection sensitivity
threats:
  enabled: true
  sensitivity: "medium"  # low, medium, high

# API server
api:
  host: "0.0.0.0"
  port: 5000
```

## 📊 API Endpoints

```bash
# Get status
curl http://localhost:5000/api/status

# Start monitoring
curl -X POST http://localhost:5000/api/start

# Get packets
curl http://localhost:5000/api/packets?count=50

# Get threats
curl http://localhost:5000/api/threats

# Get statistics
curl http://localhost:5000/api/stats
```

## ⚠️ Common Issues

### Permission Denied

**Problem**: "Permission denied" error when starting capture

**Solution**: Run with administrator/root privileges
```bash
# Windows: Run Command Prompt as Administrator
# Linux/macOS:
sudo python3 main.py --gui
```

### No Packets Captured

**Problem**: Monitoring starts but no packets appear

**Solutions**:
1. Check if Npcap/libpcap is installed
2. Verify network interface is active
3. Try different interface from dropdown
4. Check firewall settings

### Cannot Connect (Mobile App)

**Problem**: Mobile app cannot connect to backend

**Solutions**:
1. Verify backend is running: `python main.py --api`
2. Check IP address in mobile config
3. Ensure devices are on same network
4. Check firewall allows port 5000

### High CPU Usage

**Problem**: Application uses too much CPU

**Solutions**:
1. Apply packet filters to reduce traffic
2. Lower threat detection sensitivity
3. Reduce display update rate in config

## 🔐 Security Notes

- **Run Responsibly**: Only monitor networks you own or have permission to monitor
- **Root/Admin Required**: Packet capture requires elevated privileges
- **API Security**: Enable authentication in production environments
- **Data Privacy**: Captured data may contain sensitive information

## 📚 Next Steps

- Read [FEATURES.md](FEATURES.md) for detailed feature documentation
- See [API.md](API.md) for complete API reference
- Check [THREAT_DETECTION.md](THREAT_DETECTION.md) for threat detection rules
- Join community discussions on GitHub

## 🆘 Getting Help

- **Documentation**: See `/docs` directory
- **GitHub Issues**: Report bugs and request features
- **Examples**: Check `/examples` directory for scripts

## 🎓 Tutorials

1. [Basic Network Monitoring](tutorials/01-basic-monitoring.md)
2. [Threat Detection Setup](tutorials/02-threat-detection.md)
3. [API Integration](tutorials/03-api-integration.md)
4. [Custom Filters](tutorials/04-custom-filters.md)
5. [Mobile App Setup](tutorials/05-mobile-setup.md)
