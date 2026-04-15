# Job Forwarder — Detailed Setup Guide

## Prerequisites

- Docker Desktop installed ([download](https://www.docker.com/products/docker-desktop/))
- A Google account (Gmail)
- A phone with WhatsApp installed
- A VNC viewer (e.g., [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/) — free)

## Step 1: Clone the Repository

```bash
git clone https://github.com/trivenigk/job-forwarder.git
cd job-forwarder
```

## Step 2: Create a Google Cloud OAuth Client

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or use existing) — name it `job-forwarder`
3. Enable APIs:
   - Go to **APIs & Services > Library**
   - Search and enable **Google Sheets API**
   - Search and enable **Google Drive API**
4. Configure OAuth consent screen:
   - Go to **APIs & Services > OAuth consent screen**
   - User type: **External**
   - App name: `Job Forwarder`
   - Add your email as a test user
   - Save
5. Create OAuth client:
   - Go to **APIs & Services > Credentials**
   - Click **Create Credentials > OAuth client ID**
   - Application type: **Desktop app**
   - Name: `job-forwarder-desktop`
   - Click **Create**
   - Click **Download JSON**
   - Save as `setup/credentials.json`

## Step 3: Create the Google Sheet

1. Go to [Google Sheets](https://sheets.google.com) and create a new spreadsheet
2. Name it `Job Forwarder Queue`
3. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
   ```

## Step 4: Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env`:
```
GOOGLE_SHEET_ID=your-sheet-id-here
CHROME_PROFILE_PATH=C:\Users\YourName\projects\job-forwarder\chrome-profile
```

## Step 5: Authenticate with Google (First Time Only)

```bash
cd agent
pip install -r requirements.txt
python -c "from sheets import _get_creds; _get_creds()"
```

This opens your browser for Google login. After authorizing, a `setup/token.json` file is created. Subsequent runs use this token automatically.

## Step 6: Set Up the Sheet

Run the setup script to create Queue and Groups tabs:

```bash
python -c "
from sheets import _get_creds
from config import GOOGLE_SHEET_ID
import gspread

creds = _get_creds()
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID)

# Create Queue tab
ws = sheet.sheet1
ws.update_title('Queue')
ws.update('A1:I1', [['ID', 'Status', 'Subject', 'Body', 'Company', 'Source', 'DateReceived', 'DateSent', 'RetryCount']])

# Create Groups tab
gs = sheet.add_worksheet(title='Groups', rows=20, cols=1)
gs.update('A1:A2', [['GroupName'], ['Your WhatsApp Group Name Here']])

print('Sheet setup complete!')
"
```

## Step 7: Build and Run with Docker

```bash
cd ..   # back to project root
docker compose build
docker compose up -d
```

## Step 8: Scan WhatsApp QR Code (First Time Only)

1. Open your VNC viewer
2. Connect to `localhost:5900` (no password)
3. You'll see Chrome with WhatsApp Web QR code
4. Open WhatsApp on your phone > Settings > Linked Devices > Link a Device
5. Scan the QR code
6. Close the VNC viewer — you won't need it again

## Step 9: Add Jobs to the Queue

Add rows to the Queue tab in your Google Sheet with Status = `PENDING`:

| Column | Description | Example |
|--------|-------------|---------|
| A: ID | Unique identifier | 20260414_120000_001 |
| B: Status | Must be `PENDING` | PENDING |
| C: Subject | Job title | Senior Data Engineer - Remote |
| D: Body | Full job description | Requirements, responsibilities... |
| E: Company | Company name | Google (via Recruiter) |
| F: Source | Recruiter email | recruiter@example.com |
| G: DateReceived | When received | 2026-04-14 12:00:00 |
| H: DateSent | Leave empty | |
| I: RetryCount | Set to 0 | 0 |

The agent polls every 2 hours and sends all PENDING jobs as one combined message.

## Step 10: Manage Groups

Edit the **Groups** tab in your Google Sheet:
- Add a row with the exact WhatsApp group name to add a group
- Delete a row to remove a group
- Changes take effect on the next poll cycle (no restart needed)

## Common Commands

```bash
# View logs
docker compose logs -f

# Stop the agent
docker compose down

# Restart after config changes
docker compose down && docker compose build && docker compose up -d

# View WhatsApp via VNC
# Connect VNC viewer to localhost:5900
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Chrome crashes on start | Run `docker compose down`, delete `chrome-profile/SingletonLock`, restart |
| WhatsApp asks for QR again | Connect VNC to localhost:5900 and re-scan |
| OAuth token expired | Run `python -c "from sheets import _get_creds; _get_creds()"` locally |
| Jobs not sending | Check `docker compose logs` for errors |
| Group not found | Ensure group name in Sheet matches WhatsApp exactly (case-sensitive) |
