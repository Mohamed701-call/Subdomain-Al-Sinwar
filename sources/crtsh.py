"""crt.sh — Certificate Transparency logs. Free, no API key needed."""

import json
import sys
from typing import Set

import requests

from core import USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains
from utils.retry import retry


@register
class CrtShSource(BaseSource):
    name = "crtsh"
    display_name = "crt.sh"
    requires_key = None

    @retry(times=3, delay=3.0, exceptions=(requests.exceptions.Timeout,))
    def _fetch(self, domain: str, timeout: int = 60) -> dict:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        try:
            data = self._fetch(domain)
        except requests.exceptions.Timeout:
            print("[!] crt.sh gave up after 3 attempts (often just an overloaded free "
                  "service — try again later).", file=sys.stderr)
            return results
        except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"[!] crt.sh error: {e}", file=sys.stderr)
            return results

        for entry in data:
            for line in entry.get("name_value", "").splitlines():
                line = line.strip().lstrip("*.")
                if line:
                    results |= extract_subdomains(line, domain, bundle.host)
        return results