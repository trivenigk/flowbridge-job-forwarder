# I Built a Zero-Cost Bot That Forwards Job Postings to WhatsApp Groups — Here's the Architecture

**By Triveni Ganta | April 2026**

---

Every day, I receive 15-20 job emails from recruiters. Every day, I manually forward the good ones to two WhatsApp groups with 500+ members.

Copy. Paste. Format. Repeat.

I got tired of it. So I built **FlowBridge** — an automated pipeline that reads my Gmail, deduplicates job postings, and sends structured alerts to WhatsApp groups. All running in a Docker container. Total cost: **$0/month**.

Here's how it works.

## The Problem Nobody Talks About

Job communities live on WhatsApp and Telegram. Job postings arrive via email. Someone has to bridge the gap — and that someone is usually doing it manually.

The obvious solutions don't work:
- **WhatsApp Business API**: $0.005-0.08 per message + business verification
- **Zapier/Make.com**: $20-100/month for what should be a simple pipe
- **Custom bots**: Break when WhatsApp updates their UI

I needed something that costs nothing and runs without my attention.

## The FlowBridge Architecture

```
Gmail --> Google Sheet (Queue) --> Docker Container --> WhatsApp Groups
              |                        |
         Groups Tab              Chrome + Xvfb
       (dynamic config)        (virtual display)
```

Five stages, five named subsystems:

1. **Email Ingestion** — Jobs arrive in Gmail from recruiters, LinkedIn, job boards
2. **DedupGuard** — Multi-signal deduplication catches duplicates before they reach your groups
3. **BatchForge** — Combines all pending jobs into one clean message (no notification spam)
4. **ClipCast** — Delivers the message using a clipboard trick that bypasses a ChromeDriver limitation
5. **SessionHeal** — Self-heals Chrome crashes inside Docker without human intervention

## The Three Technical Problems I Solved

### 1. Emoji Broke Everything

ChromeDriver can only type characters in the Basic Multilingual Plane (U+0000-U+FFFF). Every emoji I wanted in the message format caused a crash.

The fix: I inject text via a synthetic JavaScript ClipboardEvent — the browser handles the full Unicode range natively, bypassing ChromeDriver entirely.

### 2. Same Job, Sent Twice

Recruiters resend. Job boards re-notify. LinkedIn sends duplicates. Without deduplication, groups get spammed.

DedupGuard checks four signals:
- Sender email domain + subject (fingerprint match)
- Job ID (exact match)
- Body text similarity >70% against all previously sent jobs
- Intra-batch comparison

Result: **Zero duplicates in production. Zero false positives.**

### 3. Chrome Crashes at 3 AM

Inside Docker, Chrome crashes leave lock files that prevent restart. WhatsApp then needs a QR re-scan.

SessionHeal auto-cleans locks, kills orphaned processes, and restores the session from a persistent volume. Mean recovery time: under 5 seconds, no human needed.

## The Numbers

| Metric | Value |
|--------|-------|
| Jobs processed | 11 (first day) |
| Delivery success | 100% |
| Duplicates caught | 100% |
| False positives | 0% |
| Infrastructure cost | **$0/month** |
| Self-healing recoveries | 3 |

## Why Google Sheets as the Database?

This might seem hacky. It's actually the best design decision in the system.

The Google Sheet serves as both the message queue AND the configuration layer. A "Groups" tab lets anyone add or remove WhatsApp groups by typing a name — no code, no restart, no deployment.

Non-technical community managers can run this. That's the point.

## Open Source

FlowBridge is open source. The full paper is published on Zenodo.

If you run a job community, a sales team, or any group that needs email-to-messaging bridging — FlowBridge is a generalized framework. Job forwarding is just one application.

---

**Paper:** [DOI link — to be added after Zenodo publish]
**GitHub:** [Link — to be added after repo goes public]

#OpenSource #Automation #Python #Docker #WhatsApp #DataEngineering #JobSearch #ZeroCost #FlowBridge
