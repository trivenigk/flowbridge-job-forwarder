# Troubleshooting — Common Issues and Fixes

If your issue isn't here, open a GitHub issue.

---

## Docker Won't Start

| Error | Fix |
|-------|-----|
| `docker: command not found` | Install Docker Desktop, reboot |
| `Cannot connect to Docker daemon` | Start Docker Desktop (tray icon) |
| `permission denied` (Linux) | `sudo usermod -aG docker $USER` then logout/login |

---

## Chrome/WhatsApp Won't Load

### Symptom: "Could not start WhatsApp Web — exiting"

**Cause 1:** Chrome crashed, left lock files
```bash
docker compose down
rm chrome-profile/SingletonLock chrome-profile/SingletonCookie chrome-profile/SingletonSocket
docker compose up -d
```

**Cause 2:** Chrome version mismatch (auto-updates can break driver cache)
```bash
docker compose build --no-cache
docker compose up -d
```

**Cause 3:** Not enough shared memory
Edit `docker-compose.yml`, increase: `shm_size: "4gb"`

---

## QR Code Keeps Appearing

### Symptom: Every restart asks to scan QR

**Cause:** Chrome profile not persisting

Check `docker-compose.yml` has:
```yaml
volumes:
  - ./chrome-profile:/app/chrome-profile
```

Check the folder has data:
```bash
ls chrome-profile/
# Should see: Default, Local State, etc.
```

**If folder is empty:** Permission issue. Run:
```bash
chmod -R 755 chrome-profile/
```

---

## OAuth / Google Errors

### "Access denied" when authorizing

**Cause:** Your email not added as test user

Fix:
1. https://console.cloud.google.com → APIs & Services → OAuth consent screen
2. Scroll to Test users
3. Add your email

### "Gmail API has not been used"

**Cause:** Gmail API not enabled

Fix: Console → APIs & Services → Library → search "Gmail API" → Enable

### Token keeps expiring

```bash
rm setup/token.json
docker compose restart
# Re-authorize via browser popup
```

### "Scope has changed" error

**Cause:** Added new OAuth scopes after first auth

Fix:
```bash
rm setup/token.json
docker compose restart
# Re-authorize with new scopes
```

---

## Sheet Errors

### "WorksheetNotFound: Queue"

**Cause:** Tab named wrong

Fix: Rename your sheet tab to exactly **Queue** (case-sensitive)

### "APIError: PERMISSION_DENIED"

**Cause:** OAuth doesn't have Sheets access

Fix:
```bash
rm setup/token.json
docker compose restart
# Re-authorize
```

### Rows not being picked up

Check:
- Status column = exactly `PENDING` (all caps)
- Subject is not empty
- Previously sent? Check if DedupGuard marked it `DUPLICATE`

---

## Gmail Ingestion Issues

### No emails being picked up

Check your search query matches:
```bash
# Edit agent/config.py GMAIL_SEARCH_QUERY
# Test your query in Gmail search bar first
```

Too narrow? Remove `is:unread` or broaden keywords.

### Webinar/newsletter emails slipping through

Add to skip list in `agent/gmail_ingest.py`:
```python
skip_senders = [..., "yournewsender.com"]
skip_subjects = [..., "your unwanted phrase"]
```

Rebuild: `docker compose up -d --build`

---

## WhatsApp Delivery Issues

### Messages not sending

**Check selectors still match.** WhatsApp updates UI occasionally.

Use VNC to watch live:
1. Connect VNC to `localhost:5900`
2. Restart: `docker compose restart`
3. Watch Chrome — see where it gets stuck

**If search box can't be found:**
- WhatsApp changed their DOM
- Need to update `_find_search_box` selectors in `agent/whatsapp.py`

### Wrong group getting message

**Cause:** Group name mismatch

Fix: Copy exact group name from WhatsApp header (case + spaces + punctuation must match)

### Emoji not rendering

**Check `format_message` uses ClipCast paste**, not `send_keys`. Already implemented — should work.

---

## Network / Connectivity

### "Failed to fetch jobs from Google Sheet"

**Cause 1:** Laptop slept, Docker network broke

Fix: Agent auto-retries 3x with backoff. Usually self-heals next cycle.

**Cause 2:** Docker Desktop network issue

Fix:
```bash
docker compose down
docker network prune -f
docker compose up -d
```

**Cause 3:** Corporate proxy/firewall blocking Google APIs

Fix: Use a different network or configure Docker proxy settings.

---

## Disk Space

### Docker eating disk

```bash
# Check
docker system df

# Clean unused
docker system prune -a --volumes
```

On Windows, compact the WSL2 VHDX:
```powershell
# Close Docker Desktop first
wsl --shutdown
# Then use Optimize-VHD (requires Hyper-V feature) or DiskPart
```

---

## WhatsApp Session Banned

**If your WhatsApp account gets banned:**

1. **Don't panic** — usually temporary (24-48 hrs)
2. **Stop FlowBridge immediately:** `docker compose down`
3. **Switch to less-aggressive settings:**
   - Increase `CHECK_INTERVAL_SECONDS` (e.g. 7200 = 2 hours)
   - Reduce `GMAIL_MAX_RESULTS`
4. **Consider using a secondary number**
5. **Ask group consent before resuming**

---

## Still Stuck?

1. Check logs: `docker compose logs --tail 100`
2. Search existing issues: https://github.com/trivenigk/flowbridge-job-forwarder/issues
3. Open a new issue with:
   - OS + Docker version
   - Full error log
   - What you tried
