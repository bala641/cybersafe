# CyberSafe Network Monitor

Professional network traffic monitoring application with packet capture, threat detection, and port monitoring capabilities.

## Quick Start

### Windows Users

**Option 1: Automatic Installation (Easiest)**
```
1. Double-click INSTALL.bat
2. Wait for Python and dependencies to install
3. CyberSafe GUI launches automatically
4. Start monitoring your network!
```

**Option 2: Manual Setup (If needed)**
```
pip install -r requirements.txt
python main.py --gui
```

## Features

- 📊 **Packet Capture** - Real-time network packet analysis
- 🛡️ **Threat Detection** - Port scans, SYN floods, DDoS, data exfiltration
- 🔌 **Port Monitoring** - Track active connections and services
- 📈 **Analytics** - Detailed traffic statistics and reports
- 🖥️ **Professional GUI** - Easy-to-use desktop interface

## System Requirements

- Windows 10 or later
- 2GB RAM minimum
- 500MB disk space
- Administrator privileges (for network monitoring)

## Project Structure

```
Cyber safe/
├── main.py                 # Entry point
├── INSTALL.bat            # Auto-installer
├── requirements.txt       # Python dependencies
├── core/                  # Core modules
│   ├── packet_capture.py
│   ├── threat_detector.py
│   ├── port_monitor.py
│   └── protocol_analyzer.py
├── gui/                   # GUI interface
│   └── desktop_app.py
├── api/                   # REST API
│   └── server.py
├── database/              # Database models
│   └── models.py
└── utils/                 # Utilities
    └── logger.py
```

## Available Commands

```bash
# Run GUI application
python main.py --gui

# Run API server
python main.py --api

# Run command line interface
python main.py --cli
```

## Installation Details

### What Gets Installed

- Python 3.11 runtime
- Flask (web framework)
- Scapy (packet capture)
- psutil (system monitoring)
- CustomTkinter (GUI framework)

### First Time Setup

First run will:
1. Check for Python installation
2. Download and install Python if needed
3. Install all dependencies
4. Launch CyberSafe

Total time: 5-7 minutes (first time only)
Subsequent launches: Instant

## Support

For issues or questions:
1. Check the help menu in CyberSafe GUI
2. Review the logs in the application
3. Restart and try again

## License

See LICENSE file for details.

## Website

Visit: https://cybersafe.site for more information, downloads, and documentation.
