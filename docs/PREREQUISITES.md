# Prerequisites — What You Need Before Starting

**Read this first.** Everything in this list is free.

## 1. Hardware

| Need | Minimum | Why |
|------|---------|-----|
| Computer | Any Windows/Mac/Linux | Runs Docker |
| RAM | 4 GB free | Chrome + container |
| Disk | 5 GB free | Docker image + data |
| Internet | Always on | WhatsApp Web + Gmail poll |
| Phone | With WhatsApp installed | Scan QR code once |

## 2. Accounts (Free)

| Account | Purpose | Link |
|---------|---------|------|
| Google (Gmail) | Source of job emails | https://mail.google.com |
| Google Cloud | OAuth for Sheets+Gmail API | https://console.cloud.google.com |
| WhatsApp | Your phone already has it | — |
| GitHub (optional) | Clone repo | https://github.com |

## 3. Software to Install

### Windows
| Tool | Purpose | Download |
|------|---------|----------|
| **Docker Desktop** | Runs container | https://www.docker.com/products/docker-desktop/ |
| **Git** | Clone repo | https://git-scm.com/download/win |
| **VNC Viewer** | Scan QR once | https://www.realvnc.com/en/connect/download/viewer/ |
| PowerShell | Already built-in | — |

### macOS
| Tool | Purpose | Install Command |
|------|---------|-----------------|
| **Docker Desktop** | Runs container | Download from Docker website |
| **Git** | Clone repo | `brew install git` or Xcode CLT |
| **VNC** | Scan QR once | Built-in: Finder → Go → Connect to Server |

### Linux
| Tool | Purpose | Install Command |
|------|---------|-----------------|
| **Docker** | Runs container | `curl -fsSL https://get.docker.com \| sudo sh` |
| **Git** | Clone repo | `sudo apt install git` |
| **VNC** | Scan QR once | `sudo apt install tigervnc-viewer` |

## 4. What You'll Create During Setup

These get created as you go — **don't need beforehand**:

- Google Sheet (empty, 2 tabs: Queue + Groups)
- Google Cloud Project (free tier)
- OAuth 2.0 Desktop client (`credentials.json`)
- `.env` file (config)
- Chrome profile (WhatsApp session)

## 5. Important Warnings Before You Start

### ⚠️ WhatsApp Terms of Service

FlowBridge uses **WhatsApp Web** through browser automation. This is **unofficial** — not using WhatsApp's paid Business API.

**Risks you accept:**
- WhatsApp could detect automation and **ban your number**
- No official support from WhatsApp
- Message limits unclear (go slow)
- Violates WhatsApp ToS technically (enforcement rare but real)

**Mitigation built-in:**
- Low volume (1 combined message per hour max)
- Human-like delays between sends
- Uses your real browser session (not API)
- Deduplication prevents repeat sends

**Recommendation:** Use a secondary WhatsApp number if you are worried.

### ⚠️ Google Account Access

FlowBridge reads **your own Gmail** and writes to **your own Sheet**. Uses OAuth — never stores password.

**What FlowBridge can do:**
- Read Gmail messages matching search query
- Mark emails as read
- Read/write to your Google Sheet

**What FlowBridge cannot do:**
- Send emails
- Delete emails
- Access other Google services
- Share data externally

**Revoke anytime:** https://myaccount.google.com/permissions

### ⚠️ Privacy

- **No telemetry.** FlowBridge does not phone home.
- **No external servers.** Everything runs on your machine.
- **No data sharing.** Your emails stay in your Docker container.
- **Self-hosted.** You control everything.

### ⚠️ Group Consent

**Get permission before adding to group.** Group members should know a bot is posting. We learned this the hard way — see USE_CASES.md.

## 6. Time Estimate

| Step | Time |
|------|------|
| Install Docker + Git + VNC | 10–15 min |
| Create Google Cloud OAuth client | 5–10 min |
| Create Google Sheet | 2 min |
| Run setup script | 3 min |
| Scan WhatsApp QR | 1 min |
| **Total first-time setup** | **~25 min** |

## 7. Skill Level

**None required.** If you can:
- Download files
- Paste commands into terminal
- Follow numbered steps

You can run FlowBridge. No coding needed for basic use.

**Next:** [QUICKSTART.md](QUICKSTART.md)
