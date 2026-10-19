# CyberSafe Desktop Application (Electron)

## 🎯 Standalone Desktop App - Like Chrome or Claude!

This is the **Electron-based desktop application** for CyberSafe. Double-click to launch - no command line needed!

## 📦 Installation & Build

### Step 1: Install Dependencies

```bash
cd electron-app
npm install
```

### Step 2: Run in Development Mode

```bash
npm start
```

### Step 3: Build Standalone Application

**Windows:**
```bash
npm run build-win
```
Creates: `dist/CyberSafe Network Monitor Setup.exe`

**macOS:**
```bash
npm run build-mac
```
Creates: `dist/CyberSafe Network Monitor.dmg`

**Linux:**
```bash
npm run build-linux
```
Creates: `dist/CyberSafe Network Monitor.AppImage`

## 🚀 Usage

### Development Mode:
```bash
npm start
```

### Production (After Build):
- **Windows**: Double-click `CyberSafe Network Monitor.exe`
- **macOS**: Open `CyberSafe Network Monitor.app`
- **Linux**: Run `CyberSafe-Network-Monitor.AppImage`

## ✨ Features

✅ **Standalone executable** - Just double-click!
✅ **Auto-starts Python backend** - No manual server start
✅ **System tray integration** - Runs in background
✅ **Native feel** - Like Chrome/VS Code/Claude
✅ **Cross-platform** - Windows, macOS, Linux
✅ **Auto-updates** - Can add update mechanism
✅ **Desktop shortcuts** - Creates icons automatically
✅ **Start menu integration** - Professional installation

## 📁 What Gets Created

### After npm run build-win:
```
dist/
└── CyberSafe Network Monitor Setup.exe   (Installer)
    └── Installs to: C:\Program Files\CyberSafe Network Monitor\
        ├── CyberSafe Network Monitor.exe  (Main app)
        ├── Desktop Shortcut
        └── Start Menu Entry
```

### User Experience:
1. Double-click installer
2. Install like any Windows app
3. Desktop icon appears
4. Double-click icon → App opens
5. Automatically starts monitoring backend
6. Clean, native UI

## 🎨 UI Features

- **Modern dark theme**
- **Real-time updates**
- **Multiple views** (Dashboard, Packets, Threats, Ports)
- **Charts and graphs**
- **System tray support**
- **Keyboard shortcuts**
- **Responsive design**

## ⚙️ Configuration

The app automatically:
- Starts Python backend on port 5000
- Manages backend lifecycle
- Handles errors gracefully
- Shows connection status

## 🔧 Building for Distribution

### Windows Requirements:
- Node.js 16+
- npm or yarn

### Build Commands:
```bash
# Install dependencies
npm install

# Build for Windows (creates installer)
npm run build-win

# Build for all platforms
npm run build
```

### Output:
- **Windows**: `.exe` installer + portable
- **macOS**: `.dmg` disk image
- **Linux**: `.AppImage` + `.deb` package

## 📦 Package Size

- Installer: ~50-80 MB
- Installed: ~120-150 MB
- Includes: Electron runtime + your app

## 🎯 Distribution

Share the installer with anyone:
1. They download `CyberSafe Network Monitor Setup.exe`
2. Double-click to install
3. No Python/Node.js needed (for users)
4. Works like any desktop app!

## 🔐 Requirements

### For Building:
- Node.js
- npm
- Python (for backend)

### For Users (After build):
- Just the installer!
- Python backend bundled (optional)
- Or requires Python installed

## 🚀 Quick Start for Users

1. Download installer
2. Double-click to install
3. Launch from desktop/start menu
4. Done! App opens and works

No command line, no setup, just works! 🎉
