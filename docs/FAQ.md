# Frequently Asked Questions

---

## Safety & Privacy

### Will my WhatsApp account get banned?

**Possibly.** FlowBridge uses WhatsApp Web automation (unofficial). WhatsApp's ToS discourages this. Mitigations:
- 1 combined message per hour max (low volume)
- Human-like delays
- Uses your own browser session (not API impersonation)

Use a **secondary number** if you are worried. Or switch to Telegram (has free Bot API).

### Is my data safe?

**Yes — everything runs on your machine.**
- No external servers
- No telemetry, no phone-home
- Your credentials, Chrome session, emails — all local
- Docker container is isolated

### Who can see my OAuth credentials?

Only you. `credentials.json` and `token.json` are in `.gitignore`. They never leave your computer unless you commit them by mistake (don't).

### Can the author see my Gmail?

No. You download your own OAuth credentials from **your own** Google Cloud project. I never see them.

### Does FlowBridge store my emails?

**Only inside your Google Sheet.** That's your own storage. FlowBridge does not copy emails anywhere else.

### Can I revoke access?

Yes, anytime:
1. https://myaccount.google.com/permissions
2. Find FlowBridge → Remove Access
3. Delete local `setup/token.json`

---

## Technical

### How often does it check for new emails?

Default: **every 1 hour**. Change `CHECK_INTERVAL_SECONDS` in `agent/config.py`.

### How does deduplication work?

4 signals (DedupGuard):
1. Job ID exact match
2. Sender domain + subject fingerprint
3. Body text similarity ≥70% against any previously sent
4. Batch dedup within current poll cycle

### What happens if Chrome crashes?

SessionHeal auto-recovers:
1. Docker restarts container
2. Stale lock files removed
3. Chrome launches fresh
4. WhatsApp session restored from persistent volume
5. No QR re-scan needed

### Can I run it 24/7?

Yes. Set `restart: unless-stopped` in `docker-compose.yml` (already default).

### Does it work if laptop sleeps?

When laptop sleeps, Docker pauses. Resumes on wake. May miss one cycle but catches up next run.

### What about phone without WhatsApp linked?

Linked device (via QR) stays linked even if your phone is off. It will stop working only if you:
- Log out from your phone
- Don't open WhatsApp for 14 days (Meta policy)

---

## Setup

### Do I need coding skills?

**No.** Setup scripts handle everything. You paste commands and fill in forms.

### How long does setup take?

~25 minutes first time. Most of it is Google Cloud clicks.

### Can I skip Docker and run Python directly?

Yes, but Docker is the supported path. If you insist:
```bash
cd agent
pip install -r requirements.txt
python main.py
```
Needs Chrome installed locally. Chrome profile conflicts with your regular Chrome.

### Can I run multiple instances?

Yes. Clone the repo multiple times, each with its own `.env` and Google Sheet.

### Can it work with multiple Gmail accounts?

One per instance. Run multiple Docker containers on different ports.

---

## Groups

### Can I add unlimited groups?

Yes. Just add rows to the Groups tab in your Sheet.

### How do I find the exact group name?

Open WhatsApp → tap group → the header shows the exact name. Copy-paste it into the Sheet.

### What if group name has special characters?

Should work. If search fails, check for trailing spaces or invisible unicode.

### Can I filter which jobs go to which group?

Not in base version. Would require extending `main.py` with a rules engine. See `USE_CASES.md` for tips.

---

## Gmail

### Does it mark emails as read?

Yes — after ingesting to the Sheet. Prevents reprocessing.

### Will it scan archived emails?

No. Default query uses `newer_than:1d` which only looks at recent Gmail.

### Can I scan specific labels?

Yes. Edit `GMAIL_SEARCH_QUERY`:
```python
GMAIL_SEARCH_QUERY = "newer_than:1d label:Jobs"
```

### What if my search query is too broad?

- Add filters: `-from:spam@` or `-category:promotions`
- Adjust `skip_senders` and `skip_subjects` in `agent/gmail_ingest.py`

---

## Cost

### Is this really free?

Yes. Zero recurring cost. You provide:
- Your computer (runs Docker)
- Your internet
- Your Google account (free)
- Your WhatsApp number (free)

### What if I run on cloud VPS?

~$5-10/month for a small VPS (DigitalOcean, Hetzner, Linode).

### Are there usage limits on Google APIs?

Free quotas are massive:
- Gmail: 1 billion queries/day
- Sheets: 300 requests/minute
- Far more than FlowBridge ever uses

---

## Legal & Ethical

### Is this legal?

- **Your own Gmail:** Yes, it's your data
- **Your own Sheet:** Yes, your data
- **WhatsApp Web automation:** Technically against ToS. Rare enforcement for low-volume personal use. Use at own risk.
- **Commercial use:** Gray area. Use official APIs instead.

### Ethical considerations

- Get consent before adding to groups
- Don't spam — keep volume low
- Respect unsubscribes
- Don't use for marketing without opt-in
- Don't impersonate humans

---

## Open Source

### Can I modify FlowBridge?

Yes. MIT license. Fork, edit, redistribute.

### Can I use it commercially?

MIT allows commercial use. But:
- WhatsApp ToS is your problem
- No warranty
- No support guarantee

### How can I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Getting Help

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Search issues: https://github.com/trivenigk/flowbridge-job-forwarder/issues
3. Open new issue with logs + OS + steps tried
