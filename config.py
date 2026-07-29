from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# تحديد مسار إعدادات المستخدم الدائم
CONFIG_DIR = Path.home() / ".config" / "subdomain-al-sinwar"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

ENV_FILE = CONFIG_DIR / ".env"

# إنشاء ملف إعدادات افتراضي لو مش موجود
if not ENV_FILE.exists():
    default_env_content = """# Subdomain-Al-Sinwar API Keys Configuration
GITHUB_TOKEN=
SECURITYTRAILS_API_KEY=
VIRUSTOTAL_API_KEY=
SHODAN_API_KEY=
URLSCAN_API_KEY=
FOFA_EMAIL=
FOFA_KEY=
CENSYS_ID=
CENSYS_SECRET=
"""
    ENV_FILE.write_text(default_env_content, encoding="utf-8")

# تحميل المفاتيح من ملف إعدادات المستخدم
load_dotenv(ENV_FILE)

# باقي المتغيرات كما هي
APP_NAME = "Subdomain-Al-Sinwar"
VERSION = "1.0"

OUTPUT_DIR = Path("output")
LOG_DIR = Path("logs")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))
MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", "100"))
MAX_KEEPALIVE = int(os.getenv("MAX_KEEPALIVE", "20"))

USER_AGENT = os.getenv("USER_AGENT", f"{APP_NAME}/{VERSION}")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
SECURITYTRAILS_API_KEY = os.getenv("SECURITYTRAILS_API_KEY", "")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")
URLSCAN_API_KEY = os.getenv("URLSCAN_API_KEY", "")
FOFA_EMAIL = os.getenv("FOFA_EMAIL", "")
FOFA_KEY = os.getenv("FOFA_KEY", "")