# Use Cases — Beyond Job Forwarding

FlowBridge is a **generalized email-to-messaging pipeline**. Job forwarding is just one application. Here's how to adapt it for your use case.

---

## ⚠️ Before Any Use Case: Get Consent

We learned this the hard way. Before you add FlowBridge to any group:

1. **Ask admin permission** first
2. **Announce to group** that a bot will post
3. **Start low volume** — e.g. daily digest not hourly
4. **Give them an opt-out** — remove group from Sheet anytime
5. **Pause if people complain** — this is a tool, not spam

---

## Use Case 1: Personal Job Digest (Safest)

**Forward to yourself only.** No group risk.

Setup:
- Set `WHATSAPP_GROUPS` to a group with just you
- Or use WhatsApp "Message Yourself" feature
- Get clean digest, no spam concerns

---

## Use Case 2: Sales Lead Alerts

**Email source:** CRM notifications, form submissions, lead magnet signups

**Changes needed:**
```python
# agent/config.py
GMAIL_SEARCH_QUERY = "newer_than:1d from:(hubspot.com OR salesforce.com OR typeform.com)"
```

**Groups:** Sales team Slack group (WhatsApp group for sales reps)

**Message template:** Edit `format_message` in `agent/whatsapp.py` → make it "New Lead" instead of "Job Alert"

---

## Use Case 3: Security Alerts (SOC)

**Email source:** SIEM alerts, CloudWatch, PagerDuty

**Changes:**
```python
GMAIL_SEARCH_QUERY = "newer_than:1h from:(alerts@ OR pagerduty.com) subject:(critical OR high OR warning)"
CHECK_INTERVAL_SECONDS = 300  # check every 5 min for urgency
```

**Groups:** SOC incident response channel

**Note:** For true urgency use a paid service (Opsgenie, PagerDuty). FlowBridge is a best-effort tool.

---

## Use Case 4: Research Paper Alerts

**Email source:** Google Scholar alerts, arXiv digests, conference notifications

**Changes:**
```python
GMAIL_SEARCH_QUERY = "newer_than:1d (from:scholaralerts-noreply@google.com OR from:no-reply@arxiv.org)"
```

**Groups:** Lab research group

**Tip:** Add AI summary layer — see AI integration section below.

---

## Use Case 5: Real Estate Listings

**Email source:** MLS alerts, Zillow/Redfin saved searches

**Changes:**
```python
GMAIL_SEARCH_QUERY = "newer_than:1d from:(zillow.com OR redfin.com OR realtor.com)"
```

**Groups:** Buyer WhatsApp group (with consent!)

---

## Use Case 6: Deal/Price Drop Alerts

**Email source:** Retailer emails, camelcamelcamel, Honey

**Changes:**
```python
GMAIL_SEARCH_QUERY = "newer_than:6h subject:(deal OR price drop OR sale OR discount)"
```

**Groups:** Family/friends deal group (consent!)

---

## Use Case 7: Event Notifications

**Email source:** Meetup, Eventbrite, conference newsletters

**Changes:**
```python
GMAIL_SEARCH_QUERY = "newer_than:1d (from:meetup.com OR from:eventbrite.com)"
```

---

## Use Case 8: Newsletter Digest (Opt-in)

**Group admin runs FlowBridge as a paid/free digest.** Members know it's a bot.

Position as a feature, not a nuisance:
- Daily 9 AM digest only (1 message/day, not hourly)
- Clear "digest" branding
- Opt-in members

---

## Adapting Code For Your Use Case

### 1. Change the search query
`agent/config.py` → `GMAIL_SEARCH_QUERY`

Use Gmail search syntax. Test in Gmail first.

### 2. Change message format
`agent/whatsapp.py` → `format_message()`

Replace emoji headers, labels, disclaimer text.

### 3. Change the skip filters
`agent/gmail_ingest.py` → `_is_job_email()`

Rename function + update `skip_senders` and `skip_subjects` for your domain.

### 4. Change polling interval
`agent/config.py` → `CHECK_INTERVAL_SECONDS`

| Use case | Interval |
|----------|----------|
| Critical alerts | 300 (5 min) |
| Jobs | 3600 (1 hour) |
| Daily digest | 86400 (24 hours) |

### 5. Change max body length
`agent/config.py` → `MESSAGE_MAX_LENGTH`

Longer messages = more chance of WhatsApp truncating.

---

## Adding AI (Optional)

Zero-cost AI for smart filtering/summarization:

### Option A: Local LLM (Ollama)
1. Install Ollama: https://ollama.ai
2. `ollama pull mistral`
3. Add Python call in `gmail_ingest.py`:
   ```python
   import ollama
   response = ollama.chat(model='mistral', messages=[
     {'role': 'user', 'content': f'Is this a real job posting? Yes or No.\n\n{email_body}'}
   ])
   ```

### Option B: Cloud API (paid)
- OpenAI, Claude, Gemini — all have Python SDKs
- Usage is low — few pennies per day

See `docs/PAPER.md` for full comparison.

---

## Multi-Platform (Advanced)

FlowBridge uses WhatsApp Web. Port to other platforms:

| Platform | Approach |
|----------|----------|
| **Telegram** | Use Telegram Bot API (free, official) — replace Selenium entirely |
| **Slack** | Use Incoming Webhooks (free, official) |
| **Discord** | Use Webhooks (free, official) |
| **Teams** | Use Incoming Webhook (free) |

**Recommendation:** If your platform has an official API, use it. WhatsApp Web automation is only because there's no free WhatsApp API for groups.

---

## Cost at Scale

| Users | Volume | Infrastructure cost |
|-------|--------|--------------------|
| 1 (personal) | 20 emails/day | $0 |
| 10 (team) | 200 emails/day | $0 (if self-hosted) |
| 100 (community) | 2000 emails/day | ~$5/month for VPS |
| 1000+ | 20K+ emails/day | Rewrite with message queue (Kafka/Redis), drop WhatsApp Web, use Telegram Bot API |

---

## When NOT to Use FlowBridge

- You need **guaranteed delivery** (use official APIs)
- You need **<1 min latency** (use webhooks)
- You need **millions of messages/day** (use message queues + official APIs)
- You need to send from **business account** (use WhatsApp Business API, $)
- You can't tolerate **account ban risk** (avoid WhatsApp entirely)

---

**Back to:** [README.md](../README.md) | [QUICKSTART.md](QUICKSTART.md)
