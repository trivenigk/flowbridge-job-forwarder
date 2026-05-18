"""Configuration settings for the job-forwarder agent."""

import os
from dotenv import load_dotenv

load_dotenv()

# Google Sheets
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")  # to be filled
GOOGLE_SHEET_NAME = "Queue"

# WhatsApp
WHATSAPP_GROUPS = ["Submissions : DATA ENGINEER", "AAA Job Alerts"]
WHATSAPP_WEB_URL = "https://web.whatsapp.com"
CHROME_PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH", "")  # path to existing Chrome profile so WA stays logged in

# Agent
CHECK_INTERVAL_SECONDS = 3600  # check every 1 hour
LOG_FILE = "agent.log"
MAX_RETRIES = 3
MESSAGE_MAX_LENGTH = 2000
CLEANUP_DAYS = int(os.getenv("CLEANUP_DAYS", "7"))  # delete SENT/DUPLICATE/FAILED rows older than this

# Alerts (SMTP email + optional SMS via carrier email-to-SMS gateway)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587") or "587")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
ALERT_SMS_TO = os.getenv("ALERT_SMS_TO", "")  # e.g. 5551234567@tmomail.net (T-Mobile)
FAILURE_THRESHOLD = int(os.getenv("FAILURE_THRESHOLD", "3") or "3")
ALERT_THROTTLE_SECONDS = int(os.getenv("ALERT_THROTTLE_SECONDS", "3600") or "3600")

# Gmail ingestion
GMAIL_SEARCH_QUERY = os.getenv(
    "GMAIL_SEARCH_QUERY",
    "newer_than:1d -from:me -category:social "
    "subject:(engineer OR developer OR data OR hiring OR opportunity OR position "
    "OR role OR consultant OR architect OR python OR azure OR AWS OR GCP OR cloud "
    "OR SQL OR spark OR analyst OR remote OR onsite OR hybrid OR contract OR perm "
    "OR fullstack OR backend OR frontend OR devops OR manager OR lead OR urgent "
    "OR immediate OR job OR opening)"
)
GMAIL_MAX_RESULTS = 30

# Credentials (OAuth 2.0 — user login, no service account key needed)
_base = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", os.path.join(_base, "..", "setup", "credentials.json"))
TOKEN_PATH = os.getenv("TOKEN_PATH", os.path.join(_base, "..", "setup", "token.json"))
