#!/bin/bash
# CyberSafe Network Monitor - Linux/macOS Installation Script

set -e  # Exit on error

echo "================================================================"
echo "CyberSafe Network Monitor - Installation"
echo "================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}WARNING: Running as root${NC}"
fi

# Check Python installation
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Install Python 3.9+ from your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

# Check Python version
python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Python 3.9 or higher is required${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"

# Install pip if needed
echo ""
echo "[2/5] Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Upgrade pip
python3 -m pip install --upgrade pip

# Install dependencies
echo ""
echo "[3/5] Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create directories
echo ""
echo "[4/5] Creating directories..."
mkdir -p data logs exports

# Check for libpcap (Linux) or install instructions
echo ""
echo "[5/5] Checking packet capture libraries..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if dpkg -l | grep -q libpcap; then
        echo -e "${GREEN}✓ libpcap is installed${NC}"
    else
        echo -e "${YELLOW}WARNING: libpcap not detected${NC}"
        echo ""
        echo "Install with:"
        echo "  Ubuntu/Debian: sudo apt install libpcap-dev"
        echo "  Fedora/RHEL: sudo dnf install libpcap-devel"
        echo "  Arch: sudo pacman -S libpcap"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo -e "${GREEN}✓ libpcap is built into macOS${NC}"
fi

# Make scripts executable
chmod +x main.py

echo ""
echo "================================================================"
echo -e "${GREEN}Installation Complete!${NC}"
echo "================================================================"
echo ""
echo "Next Steps:"
echo "================================================================"
echo ""
echo "1. Packet capture requires root/sudo privileges"
echo ""
echo "2. Start with GUI:"
echo "   sudo python3 main.py --gui"
echo ""
echo "3. Start with CLI:"
echo "   sudo python3 main.py --cli"
echo ""
echo "4. Start API server:"
echo "   sudo python3 main.py --api"
echo ""
echo "5. List network interfaces:"
echo "   sudo python3 main.py --list-interfaces"
echo ""
echo "For all options:"
echo "   python3 main.py --help"
echo ""
echo "Documentation: README.md"
echo ""
echo "================================================================"
echo ""

# Check if user wants to run now
read -p "Start CyberSafe now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting CyberSafe..."
    sudo python3 main.py --gui
fi
