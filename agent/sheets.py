"""Google Sheet queue reader/writer for the job-forwarder agent.

Uses OAuth 2.0 (user credentials) instead of service account keys.
First run opens a browser for Google login; token is cached for future runs.

Sheet columns:
  A: ID            — timestamp-based unique ID (e.g. "20260414_153012_001")
  B: Status        — PENDING | SENT | FAILED
  C: Subject       — email subject / job title
  D: Body          — email body text
  E: Company       — company name extracted from email
  F: Source         — sender email address
  G: DateReceived  — when the email was received
  H: DateSent      — when the message was forwarded (filled by agent)
  I: RetryCount    — number of send attempts (for retry logic)
"""

import json
import logging
import os
from datetime import datetime

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import (
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_NAME,
    CREDENTIALS_PATH,
    TOKEN_PATH,
    MAX_RETRIES,
)

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _get_creds() -> Credentials:
    """Get valid OAuth 2.0 user credentials.

    On first run, opens a browser for Google login.
    Saves token to TOKEN_PATH for subsequent runs.
    """
    creds = None

    # Load existing token
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # Refresh or re-auth if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired OAuth token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"OAuth credentials not found at {CREDENTIALS_PATH}. "
                    "Download from Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client ID."
                )
            logger.info("No valid token found — opening browser for Google login...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next run
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        logger.info("Token saved to %s", TOKEN_PATH)

    return creds


def _get_spreadsheet():
    """Authenticate and return the spreadsheet object."""
    creds = _get_creds()
    client = gspread.authorize(creds)
    return client.open_by_key(GOOGLE_SHEET_ID)


def _get_worksheet() -> gspread.Worksheet:
    """Authenticate and return the queue worksheet."""
    return _get_spreadsheet().worksheet(GOOGLE_SHEET_NAME)


def get_groups() -> list[str]:
    """Read WhatsApp group names from the 'Groups' tab in the Sheet.

    Falls back to config.WHATSAPP_GROUPS if the tab doesn't exist.
    Column A = GroupName (skip header row, skip empty rows).
    """
    from config import WHATSAPP_GROUPS

    try:
        sheet = _get_spreadsheet()
        ws = sheet.worksheet("Groups")
        rows = ws.get_all_values()
        groups = [row[0].strip() for row in rows[1:] if row and row[0].strip()]
        if groups:
            logger.info("Loaded %d group(s) from Groups tab: %s", len(groups), groups)
            return groups
        else:
            logger.warning("Groups tab is empty — falling back to config")
            return WHATSAPP_GROUPS
    except gspread.WorksheetNotFound:
        logger.warning("No 'Groups' tab found — falling back to config")
        return WHATSAPP_GROUPS


def _safe_get(row: list, index: int, default: str = "") -> str:
    """Safely get a value from a row list by index."""
    return row[index].strip() if index < len(row) and row[index] else default


def _make_fingerprint(subject: str, source: str, body: str) -> str:
    """Create a dedup fingerprint from subject + sender email domain.

    This catches: same subject from same recruiter = definite duplicate.
    """
    import re
    subj = subject.lower().strip()
    # Extract email domain from source (e.g. "John <john@acme.com>" -> "acme.com")
    email_match = re.search(r'[\w.-]+@([\w.-]+)', source)
    domain = email_match.group(1).lower() if email_match else ""
    return f"{subj}||{domain}"


def _body_similarity(body1: str, body2: str) -> float:
    """Compute similarity ratio between two job bodies (0.0 to 1.0).

    Uses difflib SequenceMatcher on first 500 chars for speed.
    """
    from difflib import SequenceMatcher
    # Compare first 500 chars — enough to detect same job description
    a = body1[:500].lower().strip()
    b = body2[:500].lower().strip()
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


# Threshold: bodies with >70% similarity are considered duplicates
BODY_SIMILARITY_THRESHOLD = 0.70


def get_pending_jobs() -> list[dict]:
    """Return all rows with Status == PENDING, or FAILED with retry_count < MAX_RETRIES.

    Multi-signal deduplication:
      1. Exact match on subject + sender domain (fingerprint)
      2. Exact match on job ID
      3. Body similarity >70% against any previously SENT job

    Duplicates are auto-marked DUPLICATE and skipped.

    Each dict has keys: row, id, status, subject, body, company, source,
    date_received, retry_count.
    """
    ws = _get_worksheet()
    rows = ws.get_all_values()

    # Build dedup indexes from all SENT rows
    sent_fingerprints: set[str] = set()
    sent_ids: set[str] = set()
    sent_bodies: list[str] = []

    for i, row in enumerate(rows):
        if i == 0:
            continue
        status = _safe_get(row, 1).upper()
        if status == "SENT":
            # Fingerprint: subject + sender domain
            fp = _make_fingerprint(_safe_get(row, 2), _safe_get(row, 5), "")
            sent_fingerprints.add(fp)
            # ID
            job_id = _safe_get(row, 0)
            if job_id:
                sent_ids.add(job_id)
            # Body for similarity check
            body = _safe_get(row, 3)
            if body:
                sent_bodies.append(body)

    jobs = []
    batch_fingerprints: set[str] = set()
    batch_bodies: list[str] = []
    dup_count = 0

    for i, row in enumerate(rows):
        if i == 0:
            continue

        status = _safe_get(row, 1).upper()
        retry_count = int(_safe_get(row, 8, "0") or "0")

        if status == "PENDING" or (status == "FAILED" and retry_count < MAX_RETRIES):
            job_id = _safe_get(row, 0)
            subject = _safe_get(row, 2)
            body = _safe_get(row, 3)
            source = _safe_get(row, 5)
            fp = _make_fingerprint(subject, source, body)

            # Check 1: exact ID match
            if job_id and job_id in sent_ids:
                logger.info("Row %d DUPLICATE (same ID '%s'): '%s'", i + 1, job_id, subject[:50])
                ws.update_cell(i + 1, 2, "DUPLICATE")
                dup_count += 1
                continue

            # Check 2: subject + sender fingerprint (historical + batch)
            if fp in sent_fingerprints or fp in batch_fingerprints:
                logger.info("Row %d DUPLICATE (subject+sender): '%s'", i + 1, subject[:50])
                ws.update_cell(i + 1, 2, "DUPLICATE")
                dup_count += 1
                continue

            # Check 3: body similarity against sent jobs
            is_body_dup = False
            for sent_body in sent_bodies:
                if _body_similarity(body, sent_body) >= BODY_SIMILARITY_THRESHOLD:
                    logger.info("Row %d DUPLICATE (body %.0f%% similar): '%s'",
                                i + 1, _body_similarity(body, sent_body) * 100, subject[:50])
                    ws.update_cell(i + 1, 2, "DUPLICATE")
                    dup_count += 1
                    is_body_dup = True
                    break
            if is_body_dup:
                continue

            # Check 4: body similarity within current batch
            for batch_body in batch_bodies:
                if _body_similarity(body, batch_body) >= BODY_SIMILARITY_THRESHOLD:
                    logger.info("Row %d DUPLICATE (batch body similar): '%s'", i + 1, subject[:50])
                    ws.update_cell(i + 1, 2, "DUPLICATE")
                    dup_count += 1
                    is_body_dup = True
                    break
            if is_body_dup:
                continue

            # Not a duplicate — add to batch
            batch_fingerprints.add(fp)
            if body:
                batch_bodies.append(body)
            jobs.append({
                "row": i + 1,
                "id": job_id,
                "status": status,
                "subject": subject,
                "body": body,
                "company": _safe_get(row, 4),
                "source": source,
                "date_received": _safe_get(row, 6),
                "retry_count": retry_count,
            })

    logger.info("Found %d actionable job(s) (%d duplicates skipped)", len(jobs), dup_count)
    return jobs


def mark_sent(row_number: int) -> None:
    """Set status to SENT and write the current timestamp to DateSent."""
    ws = _get_worksheet()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.update_cell(row_number, 2, "SENT")       # column B
    ws.update_cell(row_number, 8, now)           # column H — DateSent
    logger.info("Row %d marked SENT at %s", row_number, now)


def mark_failed(row_number: int, retry_count: int) -> None:
    """Increment retry count. If max retries reached, keep FAILED permanently."""
    ws = _get_worksheet()
    new_count = retry_count + 1
    ws.update_cell(row_number, 2, "FAILED")      # column B
    ws.update_cell(row_number, 9, str(new_count)) # column I — RetryCount

    if new_count >= MAX_RETRIES:
        logger.error("Row %d permanently FAILED after %d retries", row_number, new_count)
    else:
        logger.warning("Row %d FAILED (attempt %d/%d, will retry)", row_number, new_count, MAX_RETRIES)
