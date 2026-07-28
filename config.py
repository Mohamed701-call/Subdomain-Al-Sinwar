from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

APP_NAME = "Subdomain-Al-Sinwar"
VERSION = "1.0"

OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))
MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", "100"))
MAX_KEEPALIVE = int(os.getenv("MAX_KEEPALIVE", "20"))
RETRIES = int(os.getenv("RETRIES", "3"))

USER_AGENT = os.getenv("USER_AGENT", f"{APP_NAME}/{VERSION}")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
SECURITYTRAILS_API_KEY = os.getenv("SECURITYTRAILS_API_KEY", "")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")
URLSCAN_API_KEY = os.getenv("URLSCAN_API_KEY", "")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "")
BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME", "")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD", "")
CENSYS_ID = os.getenv("CENSYS_ID", "")
CENSYS_SECRET = os.getenv("CENSYS_SECRET", "")
FOFA_EMAIL = os.getenv("FOFA_EMAIL", "")
FOFA_KEY = os.getenv("FOFA_KEY", "")
ZOOMEYE_API_KEY = os.getenv("ZOOMEYE_API_KEY", "")
FULLHUNT_API_KEY = os.getenv("FULLHUNT_API_KEY", "")
BINARYEDGE_API_KEY = os.getenv("BINARYEDGE_API_KEY", "")

HEADERS = {
    "User-Agent": USER_AGENT
}