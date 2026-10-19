# CyberSafe Analytics & User Tracking

## Overview

CyberSafe includes built-in analytics to help us understand how users are using the application and to improve features. All data collection is transparent and minimal.

## What We Track

### First Launch
- **When**: When the application is launched for the first time
- **What**: User ID, machine identifiers, system info, timestamp
- **Purpose**: Understand user base and demographics

### App Launch
- **When**: Every time the app is launched
- **What**: User ID, session ID, system info, timestamp
- **Purpose**: Track usage patterns and active users

### Feature Usage
- **When**: Features are used (packet capture, threat detection, etc.)
- **What**: Feature name, action taken, timestamp
- **Purpose**: Understand which features are most valuable

### Errors
- **When**: Errors occur in the application
- **What**: Error type, error message, system info
- **Purpose**: Identify and fix bugs

### Session End
- **When**: User closes the application
- **What**: Session duration, user ID
- **Purpose**: Understand engagement levels

## Data Privacy

### What We DON'T Collect
- **Network Traffic Data**: We never send captured packets or network data
- **Personal Information**: Names, emails, or any PII
- **File Contents**: We don't access or send file data
- **Application Secrets**: API keys or credentials

### Data Security
- All tracking data is sent over HTTPS
- Data is sent asynchronously and doesn't block the application
- No cookies or persistent identifiers beyond machine-level tracking
- Data is stored securely on our backend

### User Control
Users can disable analytics by:

1. **Deleting the tracking file**:
   ```bash
   rm ~/.cybersafe/tracking.json
   ```

2. **Disabling in configuration** (coming soon):
   - Edit `config.yaml`
   - Set `analytics.enabled: false`

3. **Running in offline mode**:
   - Analytics only work with internet connection
   - If offline, tracking fails silently

## Analytics Backend

### API Endpoints

#### POST /api/track
Track user events

**Request**:
```json
{
  "eventType": "page_view|download|feature_selection|app_launch|session_end",
  "userId": "user_abc123_1697",
  "timestamp": "2024-10-19T14:32:15.000Z",
  "userAgent": "CyberSafe/2.5.1",
  "platform": "Windows 11 (x64)"
}
```

**Response**:
```json
{
  "success": true,
  "eventId": "evt_1697803935000_abc123def",
  "message": "Event tracked successfully"
}
```

#### GET /api/stats
Get analytics statistics (admin only)

**Response**:
```json
{
  "period": "7d",
  "totalDownloads": 2458,
  "activeUsers": 1247,
  "pageViews": 8932,
  "averageSessionDuration": 204,
  "topCountries": [...],
  "topFeatures": [...]
}
```

#### GET /api/admin/users
Get active users (admin only)

#### GET /api/admin/downloads
Get download history (admin only)

#### GET /api/admin/events
Get event log (admin only)

## Admin Dashboard

The admin dashboard at `https://cybersafe-website.vercel.app/admin` provides:

- **Overview**: Key metrics and charts
- **Active Users**: Real-time user tracking
- **Download History**: Installation records
- **Events**: User activity log
- **Settings**: API configuration and data export

### Admin Access

**Default Credentials**:
- Email: `admin@cybersafe.com`
- Password: `password` (change in production!)

## User Tracking Data Format

### User ID Structure
```
user_{hash}_{timestamp}
user_abc123def456_1697803935
```

### Session Tracking
- Unique session ID per app launch
- Duration tracked from open to close
- Includes system info for support

### System Information Tracked
```python
{
  'platform': 'Windows',
  'release': '11',
  'version': 'Windows 11 (22H2)',
  'machine': 'AMD64',
  'processor': 'AMD Ryzen 9 5900X',
  'python_version': '3.11.0'
}
```

## Integration with Desktop App

### Automatic Tracking

The desktop app automatically tracks:

1. **First launch** - When user runs app for the first time
2. **Subsequent launches** - Each time app is opened
3. **Feature usage** - When features are accessed
4. **Errors** - When errors occur
5. **Session end** - When app is closed

### Manual Tracking

You can manually track events in your code:

```python
from core.user_tracker import track_feature, track_error

# Track feature usage
track_feature('packet_capture', 'started')

# Track errors
track_error('capture_error', 'Failed to initialize packet capture')
```

## Integration with Website

The marketing website tracks:

1. **Page views** - Which pages users visit
2. **Feature selections** - Which monitoring options users choose
3. **Downloads** - When users click download button
4. **User activity** - Periodic pings while browsing
5. **Session end** - When user leaves

## Backend Database Schema

### Events Collection

```javascript
{
  _id: ObjectId,
  eventType: String,           // 'page_view', 'download', etc.
  userId: String,              // Unique user identifier
  sessionId: String,           // Session identifier
  timestamp: ISODate,          // Event timestamp
  userAgent: String,           // Client user agent
  platform: String,            // OS/platform info
  ipAddress: String,           // IP address
  page: String,                // Page URL (for web)
  feature: String,             // Feature name
  downloadUrl: String,         // Download details
  sessionDuration: Number,     // Session duration in seconds
  errorType: String,           // Error type
  errorMessage: String,        // Error message
  systemInfo: Object,          // Detailed system info
  createdAt: ISODate           // Server timestamp
}
```

### Users Collection

```javascript
{
  _id: ObjectId,
  userId: String,              // Unique identifier
  firstSeen: ISODate,          // First user seen
  lastSeen: ISODate,           // Last activity
  sessionCount: Number,        // Total sessions
  platform: String,            // Primary platform
  version: String,             // App version
  status: String               // 'active', 'inactive'
}
```

## Analytics Endpoints Configuration

Set these environment variables in Vercel:

```bash
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/cybersafe
ADMIN_EMAIL=admin@cybersafe.com
ADMIN_PASSWORD=secure_password_here
JWT_SECRET=your_jwt_secret_key
```

## Future Improvements

- [ ] Opt-in/opt-out UI
- [ ] GDPR compliance data export
- [ ] Anonymization options
- [ ] Real-time dashboard notifications
- [ ] Custom alerts for administrators
- [ ] Machine learning insights
- [ ] Predictive analytics

## Questions & Support

For questions about analytics:
1. Check the [Privacy Policy](https://github.com/bala641/cybersafe)
2. Contact: support@cybersafe.com
3. File an issue on GitHub

---

**Last Updated**: October 2024
**Version**: 2.5.1
