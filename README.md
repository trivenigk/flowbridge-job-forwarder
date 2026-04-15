# FlowBridge — Job Forwarder

**Zero-cost automated pipeline that forwards job postings from Gmail to WhatsApp groups using browser automation in Docker.**

*Built on the FlowBridge framework — a generalized email-to-messaging automation system.*

No APIs to pay for. No manual copy-paste. No screen blocking. Just Docker + a Google Sheet.

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

## Quick Start (Docker)

### 1. Clone and configure

```bash
git clone https://github.com/trivenigk/job-forwarder.git
cd job-forwarder
cp .env.example .env
# Edit .env with your Google Sheet ID
```

### 2. Set up Google OAuth

- Create an OAuth 2.0 Desktop client in [Google Cloud Console](https://console.cloud.google.com)
- Enable Google Sheets API and Google Drive API
- Download credentials to `setup/credentials.json`
- Run `cd agent && python -c "from sheets import _get_creds; _get_creds()"` to authenticate

### 3. Build and run

```bash
docker compose build
docker compose up -d
```

### 4. Scan WhatsApp QR code (one time)

Connect a VNC viewer to `localhost:5900` and scan the QR code with your phone.

### 5. Add jobs to the Queue tab, manage groups in the Groups tab

That's it. The agent polls every 2 hours, deduplicates, and sends.

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

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System design, data flow, components |
| [Setup Guide](docs/SETUP_GUIDE.md) | Detailed step-by-step setup instructions |
| [Research Paper](docs/PAPER.md) | Academic paper with AI vs non-AI comparison |
| [Patent Claims](docs/PATENT_CLAIMS.md) | Provisional patent claims |

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

## Support

If FlowBridge saves you time, consider buying me a coffee:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/trivenigk)

## License

MIT License. See [LICENSE](LICENSE).

## Author

**Triveni Ganta** — [LinkedIn](https://www.linkedin.com/in/trivenigk/) | [GitHub](https://github.com/trivenigk)

**Paper:** [Zenodo DOI — to be added]

If you use FlowBridge in your work, please cite:
```
Ganta, T. (2026). FlowBridge: A Zero-Cost Generalized Framework for Cross-Platform
Email-to-Messaging Automation. Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
```
