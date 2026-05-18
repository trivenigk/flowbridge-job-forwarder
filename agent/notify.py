"""Email and SMS alerting via the Gmail API.

Reuses the same OAuth credentials as Gmail ingestion and Sheets access.
If ALERT_SMS_TO is set (e.g. carrier email-to-SMS gateway like
5551234567@tmomail.net), critical alerts are also sent as a short SMS
through the same Gmail API call.

Requires the gmail.send scope on the OAuth token. If the token was
issued before this scope was added, delete setup/token.json and re-auth.

All alerts are throttled per key: the same key cannot be re-sent within
ALERT_THROTTLE_SECONDS to prevent flooding.

Never raises — alert delivery failure must not crash the main loop.
"""

import base64
import logging
import time
from email.message import EmailMessage

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import (
    ALERT_EMAIL_TO,
    ALERT_SMS_TO,
    ALERT_THROTTLE_SECONDS,
)
from sheets import _get_creds

logger = logging.getLogger(__name__)

_last_sent: dict[str, float] = {}

SMS_MAX_LENGTH = 140


def _gmail_service():
    """Build a Gmail API service using existing OAuth creds."""
    return build("gmail", "v1", credentials=_get_creds(), cache_discovery=False)


def _gmail_send(to_addr: str, subject: str, body: str) -> bool:
    """Send a single email via Gmail API. Returns True on success."""
    msg = EmailMessage()
    msg.set_content(body)
    msg["To"] = to_addr
    msg["Subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    for attempt in (1, 2):
        try:
            _gmail_service().users().messages().send(
                userId="me", body={"raw": raw}
            ).execute()
            return True
        except HttpError as exc:
            status = getattr(exc, "status_code", None) or getattr(getattr(exc, "resp", None), "status", None)
            if status == 403:
                logger.error(
                    "Gmail API send rejected (403) — token likely missing gmail.send scope. "
                    "Delete setup/token.json and re-auth."
                )
                return False
            if attempt == 1:
                logger.warning("Gmail API send to %s attempt 1 failed (%s), retrying", to_addr, exc)
                time.sleep(2)
            else:
                logger.error("Gmail API send to %s failed permanently: %s", to_addr, exc)
                return False
        except Exception as exc:
            if attempt == 1:
                logger.warning("Gmail API send to %s attempt 1 failed (%s), retrying", to_addr, exc)
                time.sleep(2)
            else:
                logger.exception("Gmail API send to %s failed permanently", to_addr)
                return False
    return False


def send_alert(key: str, subject: str, body: str, critical: bool = False) -> None:
    """Send an alert email; if critical and SMS configured, also send SMS.

    Args:
        key: stable identifier used for throttling (e.g. "session_dead").
        subject: email subject line. SMS gateways usually drop this.
        body: alert body. Truncated to SMS_MAX_LENGTH for SMS.
        critical: if True and ALERT_SMS_TO is set, also send SMS.
    """
    if not ALERT_EMAIL_TO:
        logger.debug("ALERT_EMAIL_TO not set — alert '%s' skipped", key)
        return

    now = time.time()
    last = _last_sent.get(key, 0)
    if now - last < ALERT_THROTTLE_SECONDS:
        logger.debug("Alert '%s' throttled (last sent %.0fs ago)", key, now - last)
        return

    email_ok = _gmail_send(ALERT_EMAIL_TO, subject, body)
    if email_ok:
        logger.info("Alert email sent: %s", subject)
        _last_sent[key] = now

    if critical and ALERT_SMS_TO:
        sms_body = body.replace("\n", " ").strip()
        if len(sms_body) > SMS_MAX_LENGTH:
            sms_body = sms_body[: SMS_MAX_LENGTH - 3] + "..."
        sms_ok = _gmail_send(ALERT_SMS_TO, "", sms_body)
        if sms_ok:
            logger.info("Alert SMS sent to gateway")
