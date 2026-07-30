"""SecurityTrails API — historical DNS data. Requires a paid API key."""

import json
import os
import sys
from typing import Set

import requests

from core import USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains


@register
class SecurityTrailsSource(BaseSource):
    name = "securitytrails"
    display_name = "SecurityTrails"
    requires_key = "SECURITYTRAILS_API_KEY"

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        api_key = os.environ.get("SECURITYTRAILS_API_KEY")
        url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
        headers = {"APIKEY": api_key, "Accept": "application/json", "User-Agent": USER_AGENT}
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"[!] SecurityTrails error: {e}", file=sys.stderr)
            return results

        for sub in data.get("subdomains", []):
            results |= extract_subdomains(f"{sub}.{domain}".lower(), domain, bundle.host)
        return results