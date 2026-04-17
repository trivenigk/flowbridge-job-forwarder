# Quick Start — Step-by-Step (for Beginners)

**Total time: ~25 minutes.** Follow in order. Don't skip steps.

If stuck: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Step 0: Before You Start

Read [PREREQUISITES.md](PREREQUISITES.md) first. Install Docker Desktop.

---

## Step 1: Create Your Google Sheet (2 min)

1. Open https://sheets.google.com
2. Click **+ Blank** to create new sheet
3. Rename it to **FlowBridge Queue**
4. Look at the URL. It looks like:
   ```
   https://docs.google.com/spreadsheets/d/ABC123XYZ456.../edit
                                          ^^^^^^^^^^^^^^^
                                          this is your Sheet ID
   ```
5. **Copy the Sheet ID.** Save it in a text file — you'll paste it soon.

---

## Step 2: Set Up Google Cloud OAuth (10 min)

This is the scariest part but just clicking. Follow [GOOGLE_CLOUD_SETUP.md](GOOGLE_CLOUD_SETUP.md) for the detailed visual walkthrough.

**Short version:**
1. Go to https://console.cloud.google.com
2. Create a new project → name it `flowbridge`
3. Enable **Google Sheets API**, **Google Drive API**, **Gmail API**
4. Configure OAuth consent screen (External, add your email as test user)
5. Create Credentials → OAuth 2.0 Client ID → **Desktop app**
6. Download the JSON file
7. Save it as `credentials.json` in a safe place

---

## Step 3: Download FlowBridge (2 min)

### Option A: With Git
```bash
git clone https://github.com/trivenigk/flowbridge-job-forwarder.git
cd flowbridge-job-forwarder
```

### Option B: Without Git
1. Go to https://github.com/trivenigk/flowbridge-job-forwarder
2. Click **Code** → **Download ZIP**
3. Extract the ZIP
4. Open terminal/PowerShell inside the extracted folder

---

## Step 4: Move credentials.json (1 min)

1. Inside the FlowBridge folder, find the **setup** folder (create it if missing)
2. Move your downloaded `credentials.json` into `setup/`
3. Path should be: `flowbridge-job-forwarder/setup/credentials.json`

---

## Step 5: Run the Setup Script (3 min)

### Windows (PowerShell)
```powershell
.\scripts\setup-windows.ps1
```

If blocked: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` then retry.

### macOS
```bash
bash scripts/setup-macos.sh
```

### Linux
```bash
bash scripts/setup-linux.sh
```

**When prompted:** paste your Google Sheet ID from Step 1.

The script will:
- Check Docker is running
- Create folders
- Create `.env` config file
- Build the Docker image (takes 2–3 min first time)
- Start the container

---

## Step 6: First-Time WhatsApp Login (1 min)

1. **Install VNC Viewer:** https://www.realvnc.com/en/connect/download/viewer/ (free)
2. **Open VNC Viewer**
3. In the address bar type: `localhost:5900`
4. Press Enter (no password)
5. You see Chrome with a **WhatsApp QR code**
6. Open WhatsApp on your phone:
   - Tap **⋮** (menu) → **Linked Devices** → **Link a Device**
   - Scan the QR code
7. Close the VNC viewer window
8. **Done.** Session is saved — you won't need VNC again.

---

## Step 7: Set Up Your Sheet Tabs (2 min)

Open your Google Sheet (from Step 1).

### Queue tab
Rename Sheet1 to **Queue**. In row 1 paste these headers:

| A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|
| ID | Status | Subject | Body | Company | Source | DateReceived | DateSent | RetryCount |

### Groups tab
Click **+** at bottom → new sheet → rename to **Groups**. In row 1:

| A |
|---|
| GroupName |

Row 2: paste your WhatsApp group name **exactly as it appears in WhatsApp** (case-sensitive).

Add more rows for more groups.

---

## Step 8: Verify It's Running (1 min)

```bash
docker compose logs --tail 20
```

You should see:
```
[INFO] job-forwarder — === Job Forwarder Agent starting ===
[INFO] whatsapp — WhatsApp Web loaded successfully
[INFO] sheets — Found 0 actionable job(s)
[INFO] job-forwarder — No pending jobs — sleeping
```

**That's it.** Every hour it scans Gmail and forwards new jobs.

---

## Daily Commands

| What | Command |
|------|---------|
| See logs live | `docker compose logs -f` |
| Stop | `docker compose down` |
| Start | `docker compose up -d` |
| Restart | `docker compose restart` |
| Status | `docker compose ps` |

---

## What Now?

- Add groups to Groups tab anytime — no restart needed
- Tune which emails get forwarded: edit `agent/config.py` → `GMAIL_SEARCH_QUERY`
- Tune how often: edit `CHECK_INTERVAL_SECONDS`
- Run other use cases: see [USE_CASES.md](USE_CASES.md)

**Problems?** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
