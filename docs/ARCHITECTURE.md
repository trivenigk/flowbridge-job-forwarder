# FlowBridge — System Architecture

## Overview

Job Forwarder is a zero-cost, containerized pipeline that automatically monitors Gmail for job postings, deduplicates them, and forwards structured alerts to multiple WhatsApp groups via browser automation.

## System Diagram

```
+-------------------+       +-------------------+       +--------------------+
|                   |       |                   |       |                    |
|   Gmail Inbox     +------>+  Google Sheet     +------>+  WhatsApp Groups   |
|                   |       |  (Queue + Groups) |       |                    |
+-------------------+       +--------+----------+       +--------------------+
                                     |
                    +----------------+----------------+
                    |                                 |
            +-------v--------+              +---------v--------+
            |  Queue Tab     |              |  Groups Tab      |
            |                |              |                  |
            | ID | Status    |              | GroupName        |
            | Subject | Body |              | Group 1          |
            | Company | Src  |              | Group 2          |
            | DateRecv/Sent  |              | ...              |
            | RetryCount     |              +------------------+
            +-------+--------+
                    |
          +---------v-----------+
          |                     |
          |  Python Agent       |
          |  (Docker Container) |
          |                     |
          |  +---------------+  |
          |  | sheets.py     |  |   Google Sheets API (OAuth 2.0)
          |  | - get_pending  |  |
          |  | - get_groups   |  |
          |  | - mark_sent    |  |
          |  | - dedup check  |  |
          |  +-------+-------+  |
          |          |          |
          |  +-------v-------+  |
          |  | whatsapp.py   |  |   Selenium + Chrome + Xvfb
          |  | - search group|  |
          |  | - paste msg   |  |   (JS ClipboardEvent for emoji)
          |  | - send        |  |
          |  +---------------+  |
          |                     |
          |  +---------------+  |
          |  | Xvfb + VNC    |  |   Virtual display (port 5900)
          |  +---------------+  |
          +---------------------+
```

## Component Details

### 1. Email Source (Gmail)
- Job emails arrive from recruiters, LinkedIn InMail, job boards
- Can be populated manually or via Apps Script trigger
- No Gmail API cost — uses OAuth 2.0 user credentials

### 2. Google Sheet (Queue + Groups)
- **Queue tab**: 9-column job queue (ID, Status, Subject, Body, Company, Source, DateReceived, DateSent, RetryCount)
- **Groups tab**: Single-column list of WhatsApp group names — editable anytime
- Acts as both message queue and configuration store
- Zero cost — Google Sheets API is free

### 3. Python Agent (Docker)
- Polls the Queue tab every 2 hours
- Deduplication: checks subject against all previously SENT rows
- Combines all pending jobs into a single structured message
- Sends to each group listed in the Groups tab
- Auto-retries FAILED jobs up to 3 times

### 4. WhatsApp Web Automation
- Selenium controls Chrome inside Docker
- Xvfb provides virtual display (no physical screen needed)
- x11vnc exposes port 5900 for one-time QR code scanning
- Chrome profile persisted via Docker volume
- JS ClipboardEvent paste bypasses ChromeDriver BMP limitation for emoji support

## Data Flow

1. Job email arrives in Gmail
2. Email content is extracted and added to Queue tab as `PENDING`
3. Agent polls Queue tab on 2-hour interval
4. Dedup engine compares subject against all `SENT` rows
5. Duplicates auto-marked `DUPLICATE` and skipped
6. Remaining jobs formatted into structured message with emoji headers
7. Groups tab read dynamically — supports add/remove without restart
8. Combined message sent to each group via WhatsApp Web
9. Successful sends marked `SENT` with timestamp
10. Failed sends marked `FAILED` with retry counter

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Google Sheet as queue | Zero cost, editable, auditable, no database needed |
| Sheet-based group config | Non-technical users can add/remove groups |
| Docker + Xvfb | No screen blocking, works on any server |
| JS ClipboardEvent paste | ChromeDriver cannot type emoji (BMP limit) |
| Subject-based dedup | Simple, effective, covers 95%+ of duplicate cases |
| Combined batch messages | 1 message per group instead of N, reduces noise |
| Chrome profile volume | WhatsApp session survives container restarts |
| OAuth 2.0 over service account | Works when org blocks SA key creation |

## Security Considerations

- OAuth tokens stored in mounted volume (not baked into image)
- `credentials.json` excluded from git via `.gitignore`
- Chrome profile contains WhatsApp session — protect the volume
- VNC has no password by default — bind to localhost only in production
