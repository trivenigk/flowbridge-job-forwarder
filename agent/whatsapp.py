"""WhatsApp Web sender using Selenium.

Automates Chrome with an existing profile so WhatsApp Web stays logged in.
Sends structured job alert messages to configured groups.
"""

import glob
import logging
import os
import subprocess
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager

from config import (
    WHATSAPP_WEB_URL,
    CHROME_PROFILE_PATH,
    MESSAGE_MAX_LENGTH,
    FAILURE_THRESHOLD,
)
from notify import send_alert

logger = logging.getLogger(__name__)

# Timeouts (seconds)
PAGE_LOAD_TIMEOUT = 60
ELEMENT_WAIT = 20
SEND_DELAY = 2


class WhatsAppSender:
    """Controls Chrome + WhatsApp Web to send messages to groups."""

    def __init__(self):
        self.driver = None
        self._consecutive_failures = 0

    @staticmethod
    def _cleanup_profile_locks():
        """Remove stale Chrome lock files so a fresh session can start."""
        if not CHROME_PROFILE_PATH:
            return
        for name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
            path = os.path.join(CHROME_PROFILE_PATH, name)
            try:
                os.remove(path)
            except OSError:
                pass
        # Kill any orphaned chromedriver processes
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "chromedriver.exe"],
                capture_output=True, timeout=5,
            )
        except Exception:
            pass

    def start(self) -> None:
        """Launch Chrome with a dedicated bot profile and open WhatsApp Web.

        Uses a separate profile directory so it doesn't conflict with
        the user's already-running Chrome instance. Auto-cleans stale locks.
        Detects Docker (DISPLAY env) and adjusts settings accordingly.
        """
        self._cleanup_profile_locks()
        time.sleep(1)

        in_docker = os.environ.get("DISPLAY") == ":99"

        opts = Options()
        if CHROME_PROFILE_PATH:
            opts.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--window-size=1920,1080")
        # Auto-accept beforeunload/alert/confirm dialogs that WhatsApp Web throws
        opts.set_capability("unhandledPromptBehavior", "accept")

        if in_docker:
            # In Docker: use system-installed Chrome, no window manager
            opts.binary_location = "/usr/bin/google-chrome"
            opts.add_argument("--disable-software-rasterizer")
            logger.info("Running in Docker with virtual display")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=opts)
        self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

        logger.info("Opening WhatsApp Web...")
        self.driver.get(WHATSAPP_WEB_URL)

        # Wait until the main chat pane is loaded (user must already be logged in)
        try:
            WebDriverWait(self.driver, PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-tab="3"]'))
            )
            logger.info("WhatsApp Web loaded successfully")
            self._suppress_beforeunload()
        except TimeoutException:
            logger.error(
                "WhatsApp Web did not load in time. "
                "Make sure you are logged in with the Chrome profile."
            )
            raise

    def _suppress_beforeunload(self) -> None:
        """Disable WhatsApp Web's beforeunload dialog at the DOM level."""
        try:
            self.driver.execute_script(
                "window.onbeforeunload = null;"
                "window.addEventListener('beforeunload', function(e){"
                "  e.stopImmediatePropagation(); delete e['returnValue'];"
                "}, true);"
            )
            logger.info("Injected beforeunload suppressor")
        except WebDriverException:
            logger.warning("Could not inject beforeunload suppressor")

    def _restart_driver(self) -> bool:
        """Fully close and re-open the Chrome driver. Returns True on success."""
        logger.warning("Restarting Chrome driver")
        try:
            if self.driver:
                self.driver.quit()
        except WebDriverException:
            pass
        self.driver = None
        try:
            self.start()
            return True
        except Exception:
            logger.exception("Driver restart failed")
            return False

    def _escalate(self) -> None:
        """Inspect the consecutive failure counter and trigger recovery/alerts.

        Ladder (FAILURE_THRESHOLD defaults to 3):
          n == THRESHOLD    -> email alert: sends failing
          n == THRESHOLD*2  -> driver restart + email alert
          n == THRESHOLD*3  -> critical alert (email + SMS): session dead
        """
        n = self._consecutive_failures
        t = FAILURE_THRESHOLD

        if n == t:
            send_alert(
                "send_failures",
                "[Job Forwarder] WhatsApp sends failing",
                f"{n} consecutive WhatsApp send failures.\n"
                "Auto-recovery will reload the page on the next attempt.\n"
                "Check container logs for details.",
                critical=False,
            )
        elif n == t * 2:
            logger.warning("Failure count %d hit %d — attempting driver restart", n, t * 2)
            restart_ok = self._restart_driver()
            send_alert(
                "driver_restart",
                "[Job Forwarder] Chrome driver restarted",
                f"{n} consecutive failures. Driver restart "
                f"{'succeeded' if restart_ok else 'FAILED'}.",
                critical=False,
            )
        elif n >= t * 3:
            send_alert(
                "session_dead",
                "[Job Forwarder] WhatsApp session dead — action required",
                f"{n} consecutive failures, driver restart did not recover.\n"
                "Action: open http://localhost:6080 (noVNC) or "
                "vnc://localhost:5900 and re-scan the WhatsApp Web QR code.\n"
                "Agent will resume automatically on the next cycle.",
                critical=True,
            )

    def _ensure_chat_pane(self) -> bool:
        """Verify the chat pane is present; reload WA Web if missing.

        Returns True if pane available after check/reload, False if session is dead.
        """
        try:
            self.driver.find_element(By.CSS_SELECTOR, 'div[data-tab="3"]')
            return True
        except NoSuchElementException:
            pass

        logger.warning("Chat pane missing, reloading WhatsApp Web")
        try:
            self.driver.get(WHATSAPP_WEB_URL)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-tab="3"]'))
            )
            self._suppress_beforeunload()
            return True
        except (TimeoutException, WebDriverException):
            logger.error(
                "Session dead — scan QR at vnc://localhost:5900 "
                "(or http://localhost:6080) to re-link WhatsApp Web"
            )
            return False

    def _find_search_box(self):
        """Find the WhatsApp search input (it's an <input>, not contenteditable)."""
        selectors = [
            (By.CSS_SELECTOR, 'input[data-tab="3"]'),
            (By.CSS_SELECTOR, 'input[aria-label*="Search"]'),
            (By.CSS_SELECTOR, '[data-tab="3"][role="textbox"]'),
        ]
        for by, sel in selectors:
            try:
                el = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((by, sel))
                )
                return el
            except (TimeoutException, NoSuchElementException):
                continue
        raise NoSuchElementException("Could not find WhatsApp search box")

    def _find_message_box(self):
        """Find the WhatsApp message input (appears after opening a chat)."""
        selectors = [
            (By.CSS_SELECTOR, 'div[data-tab="10"] div[contenteditable="true"]'),
            (By.CSS_SELECTOR, 'div[data-tab="10"] p'),
            (By.CSS_SELECTOR, 'div[role="textbox"][data-tab="10"]'),
            (By.CSS_SELECTOR, 'input[data-tab="10"]'),
            (By.CSS_SELECTOR, 'footer div[contenteditable="true"]'),
            (By.CSS_SELECTOR, 'footer input[role="textbox"]'),
        ]
        for by, sel in selectors:
            try:
                el = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((by, sel))
                )
                return el
            except (TimeoutException, NoSuchElementException):
                continue
        raise NoSuchElementException("Could not find WhatsApp message box")

    def send_to_group(self, group_name: str, message: str) -> bool:
        """Search for a group by name and send a message.

        Returns True on success, False on failure.
        """
        if not self._ensure_chat_pane():
            self._consecutive_failures += 1
            self._escalate()
            return False
        try:
            # Click and type in the search box
            search_box = self._find_search_box()
            search_box.click()
            time.sleep(0.5)
            search_box.clear()
            time.sleep(0.3)
            search_box.send_keys(group_name)
            time.sleep(SEND_DELAY)

            # Click the matching group in search results
            group_el = WebDriverWait(self.driver, ELEMENT_WAIT).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//span[@title="{group_name}"]')
                )
            )
            group_el.click()
            time.sleep(1)

            # Find the message input box
            msg_box = self._find_message_box()
            msg_box.click()
            time.sleep(0.3)

            # Use JavaScript clipboard API to paste the message (supports emojis)
            # This avoids ChromeDriver's BMP-only limitation with send_keys
            escaped = message.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
            self.driver.execute_script(
                f"""
                const el = arguments[0];
                const dt = new DataTransfer();
                dt.setData('text/plain', `{escaped}`);
                const paste = new ClipboardEvent('paste', {{
                    clipboardData: dt,
                    bubbles: true,
                    cancelable: true,
                }});
                el.dispatchEvent(paste);
                """,
                msg_box,
            )
            time.sleep(1)

            # Press Enter to send
            msg_box.send_keys(Keys.ENTER)
            time.sleep(SEND_DELAY)

            logger.info("Message sent to '%s'", group_name)
            self._consecutive_failures = 0
            return True

        except (TimeoutException, NoSuchElementException) as exc:
            logger.error("Failed to send to '%s': %s", group_name, exc)
            self._consecutive_failures += 1
            self._escalate()
            return False

        except WebDriverException as exc:
            logger.error("Browser error sending to '%s': %s", group_name, exc)
            self._consecutive_failures += 1
            self._escalate()
            return False

        finally:
            # Press Escape to close search and reset state
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                time.sleep(0.5)
            except WebDriverException:
                pass

    def close(self) -> None:
        """Quit the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Browser closed")


def format_message(job: dict) -> str:
    """Format a job dict into a structured WhatsApp message.

    Args:
        job: dict with keys subject, body, company, source, date_received.

    Returns:
        Formatted message string, body truncated to MESSAGE_MAX_LENGTH.
    """
    import re
    body = job.get("body", "").strip()
    # Clean body: collapse multiple blank lines, strip CSS/HTML remnants
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.IGNORECASE | re.DOTALL)
    body = re.sub(r'<[^>]+>', '', body)
    body = re.sub(r'@import\s+url\([^)]*\);?', '', body)
    body = re.sub(r'\{[^}]*\}', '', body)  # remove CSS blocks { ... }
    body = re.sub(r'https?://\S+', '', body)  # remove URLs
    body = re.sub(r'&[a-zA-Z]+;', ' ', body)  # remove HTML entities
    body = re.sub(r'-{5,}', '', body)  # remove long dashes
    # Remove personal name references
    body = re.sub(r'\bTriveni\b\s*(Ganta|Gopala Krishna Ganta)?', '', body, flags=re.IGNORECASE)
    body = re.sub(r'(Hi|Hello|Dear|Hey)\s*,?\s*\n?', '', body, count=2)  # strip greetings
    # Collapse whitespace
    lines = [line.strip() for line in body.split('\n')]
    cleaned = []
    blank_count = 0
    for line in lines:
        if not line:
            blank_count += 1
            if blank_count <= 1:
                cleaned.append('')
        else:
            blank_count = 0
            cleaned.append(line)
    body = '\n'.join(cleaned).strip()
    if len(body) > MESSAGE_MAX_LENGTH:
        body = body[:MESSAGE_MAX_LENGTH] + "..."

    company = job.get("company", "N/A")
    subject = job.get("subject", "No Subject")
    source = job.get("source", "N/A")
    date_received = job.get("date_received", "")

    msg = (
        f"\U0001f4cb *Job Alert*\n"
        f"\U0001f3e2 *Company:* {company}\n"
        f"\U0001f4cc *{subject}*\n"
        f"\n"
        f"{body}\n"
        f"\n"
        f"\U0001f4e7 Source: {source}\n"
        f"\U0001f4c5 {date_received}\n"
        f"\n"
        f"\u26a0\ufe0f _Disclaimer: If interested, please reach out to the contact provided above. "
        f"Do not contact me regarding this posting._"
    )
    return msg
