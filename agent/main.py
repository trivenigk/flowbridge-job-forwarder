"""Job Forwarder Agent — main entry point.

Polls a Google Sheet for PENDING jobs and forwards them to WhatsApp groups.
Runs continuously on a configurable interval using the `schedule` library.
"""

import logging
import signal
import sys
import time

import schedule

from config import CHECK_INTERVAL_SECONDS, LOG_FILE
from sheets import get_pending_jobs, mark_sent, mark_failed, get_groups
from whatsapp import WhatsAppSender, format_message

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("job-forwarder")

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------

sender: WhatsAppSender | None = None
_shutdown = False


def _handle_signal(signum, _frame):
    """Set the shutdown flag on SIGINT / SIGTERM."""
    global _shutdown
    logger.info("Received signal %s — shutting down after current cycle", signum)
    _shutdown = True


# ---------------------------------------------------------------------------
# Core loop
# ---------------------------------------------------------------------------


def process_jobs() -> None:
    """Fetch pending jobs from the sheet and send each to all WhatsApp groups."""
    try:
        jobs = get_pending_jobs()
    except Exception:
        logger.exception("Failed to fetch jobs from Google Sheet")
        return

    if not jobs:
        logger.info("No pending jobs — sleeping")
        return

    # Build one combined message from all pending jobs
    separator = "\n\n" + "=" * 40 + "\n\n"
    combined = separator.join(format_message(job) for job in jobs)
    header = f"*{len(jobs)} Job Alert(s) - {time.strftime('%B %d, %Y')}*\n\n"
    full_message = header + combined

    # Read groups dynamically from the Sheet each cycle
    groups = get_groups()
    logger.info("Sending %d job(s) as a single message to %d group(s)", len(jobs), len(groups))

    all_sent = True
    for group in groups:
        ok = sender.send_to_group(group, full_message)
        if not ok:
            all_sent = False
        time.sleep(3)

    # Mark all rows based on result
    for job in jobs:
        if all_sent:
            try:
                mark_sent(job["row"])
            except Exception:
                logger.exception("Failed to mark row %d as SENT", job["row"])
        else:
            try:
                mark_failed(job["row"], job["retry_count"])
            except Exception:
                logger.exception("Failed to mark row %d as FAILED", job["row"])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    global sender

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    logger.info("=== Job Forwarder Agent starting ===")
    logger.info("Check interval: %d seconds", CHECK_INTERVAL_SECONDS)
    logger.info("Groups: loaded dynamically from Sheet")

    # Start the browser once and keep it open
    sender = WhatsAppSender()
    try:
        sender.start()
    except Exception:
        logger.exception("Could not start WhatsApp Web — exiting")
        sys.exit(1)

    # Schedule the job
    schedule.every(CHECK_INTERVAL_SECONDS).seconds.do(process_jobs)

    # Run once immediately on startup
    process_jobs()

    # Poll loop
    try:
        while not _shutdown:
            schedule.run_pending()
            time.sleep(1)
    finally:
        logger.info("Shutting down browser...")
        sender.close()
        logger.info("=== Job Forwarder Agent stopped ===")


if __name__ == "__main__":
    main()
