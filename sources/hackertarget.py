"""HackerTarget hostsearch — free, no key, small daily rate limit."""

import sys
from typing import Set

import requests

from core import USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains


@register
class HackerTargetSource(BaseSource):
    name = "hackertarget"
    display_name = "HackerTarget"
    requires_key = None

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        try:
            resp = requests.get(
                "https://api.hackertarget.com/hostsearch/", params={"q": domain},
                headers={"User-Agent": USER_AGENT}, timeout=20,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[!] HackerTarget error: {e}", file=sys.stderr)
            return results

        if "API count exceeded" in resp.text or "error" in resp.text.lower()[:50]:
            print(f"[!] HackerTarget: {resp.text.strip()[:150]}", file=sys.stderr)
            return results

        for line in resp.text.splitlines():
            results |= extract_subdomains(line, domain, bundle.host)
        return results