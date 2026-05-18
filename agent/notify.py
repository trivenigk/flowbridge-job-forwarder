"""Email and SMS alerting for the job-forwarder agent.

Sends email via SMTP. If ALERT_SMS_TO is set (e.g. carrier email-to-SMS
gateway like 5551234567@tmomail.net), critical alerts are also sent as
short SMS through the same SMTP connection.

All alerts are throttled per key: the same key cannot be re-sent within
ALERT_THROTTLE_SECONDS to prevent flooding.

Never raises — alert delivery failure must not crash the main loop.
"""

import logging
import smtplib
import time
from email.message import EmailMessage

from config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    ALERT_EMAIL_TO,
    ALERT_SMS_TO,
    ALERT_THROTTLE_SECONDS,
)

logger = logging.getLogger(__name__)

_last_sent: dict[str, float] = {}

SMS_MAX_LENGTH = 140


def _smtp_configured() -> bool:
    """Return True only if all required SMTP env vars are set."""
    return all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL_TO])


def _smtp_send(to_addr: str, subject: str, body: str) -> bool:
    """Send a single email via SMTP+STARTTLS. Returns True on success."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_addr
    msg.set_content(body)

    for attempt in (1, 2):
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(SMTP_USER, SMTP_PASSWORD)
                smtp.send_message(msg)
            return True
        except (smtplib.SMTPException, OSError) as exc:
            if attempt == 1:
                logger.warning("SMTP send to %s attempt 1 failed (%s), retrying", to_addr, exc)
                time.sleep(2)
            else:
                logger.error("SMTP send to %s failed permanently: %s", to_addr, exc)
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
    if not _smtp_configured():
        logger.debug("SMTP not configured — alert '%s' skipped", key)
        return

    now = time.time()
    last = _last_sent.get(key, 0)
    if now - last < ALERT_THROTTLE_SECONDS:
        logger.debug("Alert '%s' throttled (last sent %.0fs ago)", key, now - last)
        return

    email_ok = _smtp_send(ALERT_EMAIL_TO, subject, body)
    if email_ok:
        logger.info("Alert email sent: %s", subject)
        _last_sent[key] = now

    if critical and ALERT_SMS_TO:
        sms_body = body.replace("\n", " ").strip()
        if len(sms_body) > SMS_MAX_LENGTH:
            sms_body = sms_body[: SMS_MAX_LENGTH - 3] + "..."
        sms_ok = _smtp_send(ALERT_SMS_TO, "", sms_body)
        if sms_ok:
            logger.info("Alert SMS sent to gateway")
