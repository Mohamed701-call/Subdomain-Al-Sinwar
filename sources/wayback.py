"""Wayback Machine (archive.org CDX API) — free, no key needed. Surfaces
old/retired subdomains that no longer show up in current DNS or certs."""

import sys
from typing import Set

import requests

from core import USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains


@register
class WaybackSource(BaseSource):
    name = "wayback"
    display_name = "Wayback Machine"
    requires_key = None

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        url = "https://web.archive.org/cdx/search/cdx"
        params = {"url": f"*.{domain}/*", "output": "text", "fl": "original",
                  "collapse": "urlkey", "limit": "100000"}
        try:
            resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[!] Wayback Machine error: {e}", file=sys.stderr)
            return results

        for line in resp.text.splitlines():
            results |= extract_subdomains(line, domain, bundle.host)
        return results