# FER Live Calendar

Automatically sync your FER calendar to Google Calendar. This service periodically downloads your FER calendar ICS file and updates a Google Calendar, adding new events and removing deleted ones.

## Prerequisites

- Docker (or Docker-compatible runtime)
- Google Cloud Platform account
- FER student/staff account with calendar access

## Setup

### 1. Get Your FER Calendar Download URL

1. Go to [FER Calendar](https://www.fer.unizg.hr/kalendar)
2. Log in with your FER credentials
3. Find and copy the ICS download link for your calendar
   - The URL will look like: `https://www.fer.unizg.hr/_download/calevent/mycal.ics?user=YOUR_USERNAME&auth=LONG_AUTH_TOKEN`

### 2. Set Up Google Calendar API

#### Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **Google Calendar API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

#### Create a Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details and create
4. Click on the newly created service account
5. Go to the "Keys" tab
6. Click "Add Key" > "Create new key"
7. Choose "JSON" format and download the key file

#### Encode the Service Account JSON

The service account JSON needs to be base64 encoded:

```bash
# On Linux/Mac:
base64 -i path/to/your-service-account-key.json

# On Windows (PowerShell):
[Convert]::ToBase64String([IO.File]::ReadAllBytes("path\to\your-service-account-key.json"))
```

Save this base64 string - you'll need it for the `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64` environment variable.

#### Create and Share Google Calendar

1. Open [Google Calendar](https://calendar.google.com/)
2. Create a new calendar for your FER events
3. Go to calendar settings > "Integrate calendar"
4. Copy the **Calendar ID** (looks like: `abc123...@group.calendar.google.com`)
5. Go to "Share with specific people"
6. Add your service account email (found in the JSON key file as `client_email`)
7. Give it "Make changes to events" permission

## Deployment

### Option 1: Build Docker Image Yourself

```bash
# Clone the repository
git clone <repository-url>
cd fer-live-calendar

# Build the image
docker build -t fer-live-calendar .

# Run the container
docker run -d \
  --name fer-live-calendar \
  -e CALENDAR_DOWNLOAD_URL="https://www.fer.unizg.hr/_download/calevent/mycal.ics?user=YOUR_USER&auth=YOUR_AUTH_TOKEN" \
  -e CALENDAR_ID="your-calendar-id@group.calendar.google.com" \
  -e DATA_DIR="/app/data" \
  -e GOOGLE_SERVICE_ACCOUNT_JSON_BASE64="YOUR_BASE64_ENCODED_JSON" \
  -v fer-calendar-data:/app/data \
  fer-live-calendar
```

### Option 2: Use Pre-built ARM64 Image

If you're deploying on ARM64 architecture (e.g., Raspberry Pi, Apple Silicon):

```bash
docker run -d \
  --name fer-live-calendar \
  -e CALENDAR_DOWNLOAD_URL="https://www.fer.unizg.hr/_download/calevent/mycal.ics?user=YOUR_USER&auth=YOUR_AUTH_TOKEN" \
  -e CALENDAR_ID="your-calendar-id@group.calendar.google.com" \
  -e DATA_DIR="/app/data" \
  -e GOOGLE_SERVICE_ACCOUNT_JSON_BASE64="YOUR_BASE64_ENCODED_JSON" \
  -v fer-calendar-data:/app/data \
  lukaznj/fer-live-calendar-arm64
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CALENDAR_DOWNLOAD_URL` | Your FER calendar ICS download URL | `https://www.fer.unizg.hr/_download/calevent/mycal.ics?user=lr55978&auth=abc123...` |
| `CALENDAR_ID` | Google Calendar ID where events will be synced | `abc123...@group.calendar.google.com` |
| `DATA_DIR` | Directory for storing ICS files (should match volume mount) | `/app/data` |
| `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64` | Base64-encoded Google service account JSON key | See setup instructions above |

## How It Works

1. On startup and every hour, the service downloads your FER calendar ICS file
2. It compares the current calendar with the previous version
3. New events are added to your Google Calendar
4. Removed events are deleted from your Google Calendar
5. The calendar state is persisted in the `/app/data` directory

## Troubleshooting

### Container logs

```bash
docker logs fer-live-calendar
```

### Verify environment variables

```bash
docker exec fer-live-calendar env | grep -E "CALENDAR_DOWNLOAD_URL|CALENDAR_ID|DATA_DIR"
```

### Common issues

- **Authentication errors**: Verify your service account has access to the Google Calendar
- **Download errors**: Check if your FER calendar download URL is still valid
- **No events syncing**: Ensure the service account has "Make changes to events" permission on the calendar

## License

MIT License
