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
CHECK_INTERVAL_SECONDS = 7200  # check every 2 hours
LOG_FILE = "agent.log"
MAX_RETRIES = 3
MESSAGE_MAX_LENGTH = 2000

# Credentials (OAuth 2.0 — user login, no service account key needed)
_base = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", os.path.join(_base, "..", "setup", "credentials.json"))
TOKEN_PATH = os.getenv("TOKEN_PATH", os.path.join(_base, "..", "setup", "token.json"))
