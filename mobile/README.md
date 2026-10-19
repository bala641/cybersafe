# CyberSafe Mobile App (Android)

React Native application for network monitoring on Android devices.

## Features

- Real-time network traffic monitoring
- Threat detection and alerts
- Port scanning and connection tracking
- Dark/Light theme support
- Connect to desktop backend via API

## Prerequisites

- Node.js 16+ and npm
- React Native CLI
- Android Studio and Android SDK
- Java Development Kit (JDK) 11+

## Installation

```bash
cd mobile
npm install
```

## Configuration

Edit `src/config.js` to set your backend API URL:

```javascript
export const API_URL = 'http://YOUR_DESKTOP_IP:5000';
```

## Running

### Development Mode

```bash
# Start Metro bundler
npm start

# Run on Android
npm run android
```

### Build APK

```bash
cd android
./gradlew assembleRelease

# APK will be at: android/app/build/outputs/apk/release/app-release.apk
```

## Project Structure

```
mobile/
├── src/
│   ├── screens/          # App screens
│   ├── components/       # Reusable components
│   ├── api/             # API client
│   ├── utils/           # Utilities
│   └── config.js        # Configuration
├── android/             # Android native code
├── ios/                 # iOS native code (future)
└── package.json         # Dependencies
```

## Permissions

The app requires the following Android permissions:

- `INTERNET` - Connect to backend API
- `ACCESS_WIFI_STATE` - Get WiFi information
- `ACCESS_NETWORK_STATE` - Get network information

## Notes

- For full packet capture functionality, the device needs to be rooted
- Non-rooted devices can monitor connections via the backend API
- Use VPN service for on-device packet inspection (requires additional implementation)

## Future Features

- On-device packet capture using VPN service
- Offline threat detection
- Network performance monitoring
- Custom threat rules
