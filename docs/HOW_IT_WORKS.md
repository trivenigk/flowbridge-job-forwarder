# How FlowBridge Works — Operational Warnings

**Read before running.** FlowBridge is not a cloud service. It runs on YOUR machine. If your machine stops, it stops.

---

## ⚠️ Critical Requirements

FlowBridge needs these **running continuously** to work:

### 1. Docker Desktop Must Be Running

- **Windows/Mac:** Docker Desktop app must be open (tray icon)
- **Linux:** Docker daemon must be running (`systemctl status docker`)
- **If Docker stops → FlowBridge stops**

**Implication:** Don't quit Docker Desktop to save RAM. Don't reboot without restarting it.

### 2. Your Computer Must Be Awake

- **Laptop sleeping → container paused**
- **Laptop off → nothing happens**
- **Laptop hibernating → network dies**

**Options:**
- Leave laptop plugged in, screen off, don't sleep
- Or run FlowBridge on a desktop / home server / VPS
- Or accept gaps (runs when you're at computer)

### 3. Internet Connection Required

- **Gmail API calls** — to scan emails
- **Google Sheets API** — to queue + mark sent
- **WhatsApp Web** — to send messages
- **All three must reach the internet**

**If offline:**
- Agent retries 3x with backoff
- After 3 failures: skips cycle, tries again next hour
- Won't lose data — Sheet state preserved

### 4. Google Account Access Must Stay Valid

- OAuth token (`setup/token.json`) refreshes automatically
- **Token expires if:**
  - You revoke access at myaccount.google.com/permissions
  - Google Cloud project is deleted
  - OAuth consent screen app is suspended
  - Password changed + 2FA triggered re-consent

**If token breaks:** Delete `setup/token.json`, restart — browser opens for re-auth.

### 5. WhatsApp Web Session Must Stay Linked

- First-time QR scan links your phone as "Linked Device"
- Session persists in `chrome-profile/` volume
- **Session breaks if:**
  - You unlink manually (Phone → Settings → Linked Devices)
  - Phone disconnects from WhatsApp for 14+ days (Meta policy)
  - You log out from phone
  - WhatsApp detects automation and forces re-login

**If session breaks:** Scan QR again via VNC (localhost:5900).

### 6. Google Sheet Must Exist and Be Accessible

- **Don't delete the Sheet** — FlowBridge loses its queue
- **Don't rename tabs** from `Queue` or `Groups` — selectors break
- **Don't change column order** in Queue tab — data goes wrong column
- **Don't remove your own access** to the Sheet

---

## ⚠️ What Happens When...

| Scenario | Effect |
|----------|--------|
| Laptop sleeps mid-cycle | Cycle pauses, resumes on wake |
| Wi-Fi drops | Retries 3x, skips if still down, next cycle retries |
| Docker Desktop quit | Container stops, no more sends until restart |
| Chrome crashes | SessionHeal auto-recovers < 5 sec |
| WhatsApp phone dies 14+ days | Session expires, needs QR re-scan |
| OAuth token expires | Auto-refresh, no action needed |
| OAuth consent revoked | Delete token.json, restart, re-authorize |
| Sheet deleted | FATAL — recreate Sheet + re-init |
| Gmail quota exceeded | Unlikely (1B queries/day free), waits next quota window |
| WhatsApp rate-limits you | Temporary — slow down interval |
| WhatsApp bans your number | 24-48hr cooldown usually — stop bot immediately |

---

## ⚠️ Resource Usage

Running 24/7 on your machine:

| Resource | Usage | Impact |
|----------|-------|--------|
| RAM | 400–600 MB | Noticeable on 4GB machine |
| CPU | ~2% idle, ~15% when sending | Mostly idle between cycles |
| Disk | ~2 GB Docker image + 400MB profile | One-time |
| Network | ~10 MB/hour | Negligible |
| Battery | Medium drain (Chrome running) | Keep laptop plugged in |

---

## ⚠️ Long-Term Considerations

### Google Cloud Project

- **Don't delete** the `flowbridge` Cloud project
- OAuth client stays valid indefinitely
- Free tier quotas are massive — you won't hit them

### OAuth Consent Screen

- App stays in "Testing" mode = **max 100 users** (no concern for personal use)
- After 6 months in Testing, Google may email verification reminder
- You can ignore it for personal use

### WhatsApp "Linked Device" Expiration

Per Meta policy:
- If your phone doesn't open WhatsApp for **14 consecutive days**, linked devices disconnect
- Solution: open WhatsApp on your phone at least once every 2 weeks

### Chrome Updates

- Chrome in container stays on the version that was in Docker image
- Auto-rebuild when WhatsApp Web breaks: `docker compose build --no-cache`

---

## ⚠️ Multi-User Caution

**Each user = separate FlowBridge instance.**

- Do NOT share OAuth tokens
- Do NOT share Chrome profile (WhatsApp session)
- Do NOT share the Sheet (unless trusted co-owner)

Each person should run their own container with their own credentials.

---

## ⚠️ Production / Always-On Setup

If you want 24/7 without your laptop:

### Option A: Home Server / Raspberry Pi
- Runs 24/7, no sleep
- Uses ~5W power
- Setup same as laptop

### Option B: Cloud VPS
- DigitalOcean, Hetzner, Linode: $5-10/mo
- Always on, always connected
- Chrome profile persists in cloud volume
- Scan QR once via VNC tunnel (SSH forwarding)

### Option C: Home Desktop
- Leave it on
- Configure Windows/Mac to not sleep
- Cheapest if you already have one running

---

## ⚠️ Final Reality Check

FlowBridge is **personal automation**, not enterprise infrastructure.

**Good fit:**
- Personal use, low volume
- Small community, with consent
- Learning project
- Zero-cost automation

**Bad fit:**
- Mission-critical delivery (use paid APIs)
- High volume (thousands/day)
- Commercial product (use official WhatsApp Business API)
- Anywhere WhatsApp account ban = disaster

---

**Next:** [PREREQUISITES.md](PREREQUISITES.md) | [QUICKSTART.md](QUICKSTART.md)
