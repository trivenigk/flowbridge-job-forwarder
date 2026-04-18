# FlowBridge — Job Forwarder

**Zero-cost automated pipeline that forwards job postings from Gmail to WhatsApp groups using browser automation in Docker.**

*Built on the FlowBridge framework — a generalized email-to-messaging automation system.*

No APIs to pay for. No manual copy-paste. No screen blocking. Just Docker + a Google Sheet.

---

## ⚠️ Before You Install — Know This

FlowBridge runs **on YOUR machine**, not in the cloud. For it to keep working:

- 🖥️ **Docker Desktop must stay running** — close it, bot stops
- 🔌 **Computer must stay awake + online** — sleep/wifi-drop = pause
- 🔐 **Google account must stay authorized** — revoke = bot breaks
- 📱 **WhatsApp phone must open once per 14 days** — Meta policy
- 📊 **Google Sheet must exist** — delete it = lose queue
- ⚡ **Unofficial WhatsApp Web automation** — account ban risk exists
- 👥 **Get group consent before adding bot** — people treat it as spam

**Full details:** [HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md) — read before install

---

## Features

- **Zero cost** — Uses only free-tier Google APIs, open-source tools, and Docker
- **Fully containerized** — Runs in Docker with virtual display, no screen needed
- **Smart deduplication** — Never sends the same job twice (subject-line matching)
- **Batch messaging** — Combines all jobs into one clean message per group
- **Dynamic groups** — Add/remove WhatsApp groups via a Google Sheet tab (no restart)
- **Emoji-rich formatting** — Structured alerts with headers, contact info, disclaimer
- **Auto-retry** — Failed sends retry up to 3 times across poll cycles
- **Self-healing** — Recovers from Chrome crashes without manual intervention

## Architecture

```
Gmail Inbox --> Google Sheet (Queue) --> Docker Agent --> WhatsApp Groups
                     |                       |
               Groups Tab              Xvfb + Chrome
            (dynamic config)          (virtual display)
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full system design.

## Quick Start — One-Command Setup

**Windows (PowerShell):**
```powershell
git clone https://github.com/trivenigk/flowbridge-job-forwarder.git
cd flowbridge-job-forwarder
.\scripts\setup-windows.ps1
```

**macOS / Linux:**
```bash
git clone https://github.com/trivenigk/flowbridge-job-forwarder.git
cd flowbridge-job-forwarder
bash scripts/setup-macos.sh   # or setup-linux.sh
```

The script handles Docker build, `.env` creation, folder setup, and starts the container.

**Need details?** See full docs below ↓

## Google Sheet Structure

### Queue Tab

| Column | Purpose |
|--------|---------|
| A: ID | Unique timestamp-based ID |
| B: Status | PENDING / SENT / FAILED / DUPLICATE |
| C: Subject | Job title |
| D: Body | Full description |
| E: Company | Company name |
| F: Source | Recruiter email/contact |
| G: DateReceived | When the email arrived |
| H: DateSent | When forwarded (auto-filled) |
| I: RetryCount | Send attempt counter |

### Groups Tab

| Column | Purpose |
|--------|---------|
| A: GroupName | WhatsApp group name (exact match) |

Add or remove groups anytime — changes take effect on the next poll cycle.

## Message Format

```
*3 Job Alert(s) - April 14, 2026*

[clipboard] *Job Alert*
[building] *Company:* Google (via Recruiter)
[pin] *Senior Data Engineer - Remote*

Full job description with requirements...

Contact: recruiter@example.com | 555-0123

[email] Source: recruiter@example.com
[calendar] 2026-04-14 12:00:00

[warning] Disclaimer: If interested, please reach out
to the contact provided above. Do not contact me
regarding this posting.

========================================

[next job...]
```

## Commands

```bash
docker compose up -d          # Start
docker compose down            # Stop
docker compose logs -f         # Watch logs
docker compose restart         # Restart
```

## Documentation

### Getting Started (Read in Order)
| Document | Time | Description |
|----------|------|-------------|
| [HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md) | 5 min | **Operational warnings — read first** |
| [PREREQUISITES.md](docs/PREREQUISITES.md) | 5 min | Hardware, accounts, software, warnings |
| [QUICKSTART.md](docs/QUICKSTART.md) | 25 min | Step-by-step beginner-friendly setup |
| [GOOGLE_CLOUD_SETUP.md](docs/GOOGLE_CLOUD_SETUP.md) | 10 min | OAuth walkthrough with visual guides |

### Reference
| Document | Description |
|----------|-------------|
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common errors and fixes |
| [USE_CASES.md](docs/USE_CASES.md) | Beyond jobs — sales, alerts, research, more |
| [FAQ.md](docs/FAQ.md) | Safety, privacy, technical, cost questions |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, data flow, components |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [PAPER.md](docs/PAPER.md) | Academic paper with AI vs rule-based analysis |

## FlowBridge Subsystems

| Name | What it does |
|------|-------------|
| **DedupGuard** | Multi-signal deduplication — sender fingerprint + body similarity + ID matching. Zero duplicates. |
| **ClipCast** | Clipboard-based Unicode injection — bypasses ChromeDriver BMP limitation for emoji-rich messages |
| **SessionHeal** | Self-healing Chrome sessions — auto-recovers from crashes in Docker without re-authentication |
| **SheetConfig** | Spreadsheet-as-configuration — manage groups via Google Sheet tab, no restart needed |
| **BatchForge** | Batch message combiner — N jobs in 1 message, reducing group noise |

## Tech Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| Language | Python 3.11 | Free |
| Browser automation | Selenium + ChromeDriver | Free |
| Virtual display | Xvfb + x11vnc | Free |
| Container | Docker + Docker Compose | Free |
| Queue/Config | Google Sheets API | Free |
| Auth | OAuth 2.0 | Free |

**Total: $0/month**


## License

MIT License. See [LICENSE](LICENSE).

## Author

**Triveni Ganta** — [LinkedIn](https://www.linkedin.com/in/trivenigk/) | [GitHub](https://github.com/trivenigk)

**Paper:** [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19638039.svg)](https://doi.org/10.5281/zenodo.19638039)

If you use FlowBridge in your work, please cite:
```
Ganta, T. (2026). FlowBridge: A Zero-Cost Generalized Framework for Cross-Platform
Email-to-Messaging Automation Using Browser Automation in Containerized Virtual
Display Environments. Zenodo. https://doi.org/10.5281/zenodo.19638039
```
