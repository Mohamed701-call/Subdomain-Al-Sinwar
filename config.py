"""Config-file loading (like subfinder's provider-config.yaml, but a simple
KEY=VALUE format so no extra dependency like PyYAML is required)."""

import os
import sys
from typing import Optional

# API keys this tool understands, in both config-file and env-var form.
CONFIG_KEYS = [
    "GITHUB_TOKEN",
    "SECURITYTRAILS_API_KEY",
    "URLSCAN_API_KEY",
    "VIRUSTOTAL_API_KEY",
    "SHODAN_API_KEY",
    "FOFA_EMAIL",
    "FOFA_KEY",
]

DEFAULT_CONFIG_PATHS = [
    os.path.expanduser("~/.config/subdomain-al-sinwar/config"),
    os.path.join(os.getcwd(), "config.env"),
    os.path.join(os.getcwd(), ".env"),
]


def load_config(explicit_path: Optional[str] = None) -> dict:
    """
    Simple KEY=VALUE config file holding API keys, so you don't have to
    `export` env vars every session. Precedence (lowest to highest):
    config file  <  existing environment variables  <  CLI flags.

        GITHUB_TOKEN=ghp_xxx
        SECURITYTRAILS_API_KEY=xxx
        URLSCAN_API_KEY=xxx
        VIRUSTOTAL_API_KEY=xxx
        SHODAN_API_KEY=xxx
        FOFA_EMAIL=you@example.com
        FOFA_KEY=xxx

    Search order if --config isn't given:
        ~/.config/subdomain-al-sinwar/config
        ./config.env
        ./.env
    """
    candidates = [explicit_path] if explicit_path else DEFAULT_CONFIG_PATHS
    loaded_from = None
    values = {}

    for path in candidates:
        if not path or not os.path.isfile(path):
            continue
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key = key.strip().upper()
                    val = val.strip().strip('"').strip("'")
                    if key in CONFIG_KEYS and val:
                        values[key] = val
            loaded_from = path
            break
        except OSError:
            continue

    for key, val in values.items():
        os.environ.setdefault(key, val)

    if loaded_from:
        print(f"[*] Loaded API keys from config file: {loaded_from}", file=sys.stderr)
    elif explicit_path:
        print(f"[!] Config file not found: {explicit_path}", file=sys.stderr)

    return values