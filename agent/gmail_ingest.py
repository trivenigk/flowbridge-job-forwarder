"""Gmail auto-ingestion for FlowBridge.

Scans Gmail for job-related emails, extracts structured data,
and queues them to the Google Sheet as PENDING rows.
Uses the same OAuth 2.0 credentials as the Sheet module.
"""

import base64
import logging
import re
from datetime import datetime
from email.utils import parsedate_to_datetime

from googleapiclient.discovery import build

from config import GMAIL_SEARCH_QUERY, GMAIL_MAX_RESULTS, MESSAGE_MAX_LENGTH
from sheets import _get_creds, _get_worksheet

logger = logging.getLogger(__name__)


def _get_gmail_service():
    """Build and return a Gmail API service using existing OAuth creds."""
    creds = _get_creds()
    return build("gmail", "v1", credentials=creds)


def _extract_company(from_header: str) -> str:
    """Extract company/sender name from a From header.

    "Acme Jobs <jobs@acme.com>" -> "Acme Jobs"
    "jobs@acme.com"             -> "acme.com"
    """
    match = re.match(r'^(.+?)\s*<.+>$', from_header)
    if match:
        return match.group(1).replace('"', '').strip()
    domain_match = re.search(r'@([\w.-]+)', from_header)
    return domain_match.group(1) if domain_match else from_header


def _strip_html(text: str) -> str:
    """Strip HTML tags, CSS, scripts, and decode entities. Clean for WhatsApp."""
    # Remove entire <head>, <style>, <script> blocks first
    text = re.sub(r'<head[^>]*>.*?</head>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Convert structural tags to newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<li[^>]*>', '- ', text, flags=re.IGNORECASE)
    text = re.sub(r'</?(p|div|tr|td|th|h[1-6])[^>]*>', '\n', text, flags=re.IGNORECASE)
    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&bull;', '* ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&#39;', "'", text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&ndash;', '-', text)
    text = re.sub(r'&mdash;', '-', text)
    text = re.sub(r'&rsquo;', "'", text)
    text = re.sub(r'&lsquo;', "'", text)
    text = re.sub(r'&rdquo;', '"', text)
    text = re.sub(r'&ldquo;', '"', text)
    text = re.sub(r'&hellip;', '...', text)
    text = re.sub(r'&[a-zA-Z]+;', '', text)  # catch any remaining entities
    # Remove URLs (tracking links, unsubscribe links, LinkedIn links)
    text = re.sub(r'https?://\S+', '', text)
    # Remove email boilerplate / footers
    text = re.sub(r'(To unsubscribe|If you would like to unsubscribe|click here to unsubscribe|Email opt-out).*', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'(This email was intended for|You are receiving|LinkedIn and the LinkedIn logo).*', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'(Confidentiality Notice|The information contained in this|This e-mail and any files).*', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'(We respect your online privacy|To remove your email address permanently).*', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'-{5,}', '', text)  # remove long dashes (separators)
    # Collapse whitespace: max 2 consecutive newlines, trim spaces per line
    lines = text.split('\n')
    cleaned = []
    blank_count = 0
    for line in lines:
        line = line.strip()
        if not line:
            blank_count += 1
            if blank_count <= 1:  # allow max 1 blank line
                cleaned.append('')
        else:
            blank_count = 0
            cleaned.append(line)
    text = '\n'.join(cleaned)
    # Remove leading/trailing whitespace
    return text.strip()


def _get_body(payload: dict) -> str:
    """Extract plain text body from Gmail message payload."""
    # Try plain text first
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    # Try HTML and strip tags
    if payload.get("mimeType") == "text/html" and payload.get("body", {}).get("data"):
        html = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        return _strip_html(html)

    # Multipart — recurse into parts
    parts = payload.get("parts", [])
    for part in parts:
        mime = part.get("mimeType", "")
        if mime == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")

    # Fallback: try HTML parts
    for part in parts:
        mime = part.get("mimeType", "")
        if mime == "text/html" and part.get("body", {}).get("data"):
            html = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
            return _strip_html(html)

    # Nested multipart
    for part in parts:
        if part.get("parts"):
            result = _get_body(part)
            if result:
                return result

    return ""


def _is_job_email(subject: str, from_addr: str) -> bool:
    """Filter out non-job emails that slip through the search query.

    Skips: newsletters, SaaS listings, generic career tips, course promotions.
    """
    skip_senders = [
        "acquire.com", "genai.works", "pinkcareers.com", "beehiiv.com",
        "substack.com", "indeed.com", "jobalerts-noreply@linkedin.com",
        "donotreply@", "noreply@", "talent@ibm.com",
        "careers@talentintelligence", "newsletter@",
        "databricks.com", "snowflake.com", "atlan.com",
        "grandhomes.com", "info@grandhomes", "realestate",
        "bullhornstaffing.com",
        "aws.amazon.com", "aws-educate", "amazonses.com",
        "talent@ibm.com", "careers@", "alerts@",
        "notifications@", "no-reply@", "noreply@",
    ]
    from_lower = from_addr.lower()
    for skip in skip_senders:
        if skip in from_lower:
            return False

    # Skip reply threads (Re:) — these are conversations, not new postings
    if subject.lower().startswith("re:"):
        return False

    # Skip webinars, events, newsletters, courses
    skip_subjects = [
        "webinar", "virtual event", "reminder:", "register now",
        "masterclass", "workshop:", "sign up for", "course:",
        "newsletter", "weekly digest", "daily digest",
        "you're invited", "grand opening", "open house",
        "free ai course", "recession proof",
        "action required", "verify your", "update your",
        "aws builder id", "aws educate", "password reset",
        "this role looks like a match", "jobs for you",
        "this job is a match",
    ]
    subj_lower = subject.lower()
    for skip in skip_subjects:
        if skip in subj_lower:
            return False

    return True


def ingest_gmail_jobs() -> int:
    """Scan Gmail for new job emails and queue them to the Google Sheet.

    Returns the number of new jobs queued.
    """
    logger.info("Scanning Gmail for job emails...")

    try:
        service = _get_gmail_service()
    except Exception:
        logger.exception("Failed to build Gmail service")
        return 0

    # Search for matching emails
    try:
        result = service.users().messages().list(
            userId="me",
            q=GMAIL_SEARCH_QUERY,
            maxResults=GMAIL_MAX_RESULTS,
        ).execute()
    except Exception:
        logger.exception("Gmail search failed")
        return 0

    messages = result.get("messages", [])
    if not messages:
        logger.info("No new job emails found in Gmail")
        return 0

    logger.info("Found %d potential job email(s) in Gmail", len(messages))

    # Get existing IDs from the Sheet to avoid re-ingesting
    ws = _get_worksheet()
    existing_rows = ws.get_all_values()
    existing_ids = set()
    existing_subjects = set()
    for row in existing_rows[1:]:  # skip header
        if len(row) > 0 and row[0]:
            existing_ids.add(row[0])
        if len(row) > 2 and row[2]:
            existing_subjects.add(row[2].lower().strip())

    queued = 0
    for msg_ref in messages:
        try:
            msg = service.users().messages().get(
                userId="me", id=msg_ref["id"], format="full"
            ).execute()

            # Extract headers
            headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
            subject = headers.get("Subject", "(No Subject)")
            from_addr = headers.get("From", "")
            date_str = headers.get("Date", "")

            # Filter non-job emails
            if not _is_job_email(subject, from_addr):
                continue

            # Skip if subject already exists in Sheet (quick dedup)
            if subject.lower().strip() in existing_subjects:
                continue

            # Extract body
            body = _get_body(msg["payload"])
            if len(body) > MESSAGE_MAX_LENGTH * 2:
                body = body[:MESSAGE_MAX_LENGTH * 2]

            # Parse date
            try:
                dt = parsedate_to_datetime(date_str)
                date_received = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                date_received = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Generate ID from message timestamp
            timestamp = int(msg.get("internalDate", "0")) // 1000
            dt_id = datetime.fromtimestamp(timestamp)
            job_id = dt_id.strftime("%Y%m%d_%H%M%S") + f"_{queued:03d}"

            # Skip if ID already exists
            if job_id in existing_ids:
                continue

            # Extract company
            company = _extract_company(from_addr)

            # Append to Sheet
            row = [
                job_id,
                "PENDING",
                subject,
                body,
                company,
                from_addr,
                date_received,
                "",  # DateSent
                "0",  # RetryCount
            ]
            ws.append_row(row)
            existing_subjects.add(subject.lower().strip())
            queued += 1

            # Mark email as read in Gmail
            try:
                service.users().messages().modify(
                    userId="me",
                    id=msg_ref["id"],
                    body={"removeLabelIds": ["UNREAD"]},
                ).execute()
            except Exception:
                pass  # non-critical

        except Exception:
            logger.exception("Failed to process email %s", msg_ref.get("id", "?"))
            continue

    logger.info("Queued %d new job(s) from Gmail", queued)
    return queued
