"""Anubis (jldc.me) — free public subdomain dataset, no key needed."""

import json
import sys
from typing import Set

import requests

from core import USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains


@register
class AnubisSource(BaseSource):
    name = "anubis"
    display_name = "Anubis (jldc.me)"
    requires_key = None

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        url = f"https://jldc.me/anubis/subdomains/{domain}"
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"[!] Anubis error: {e}", file=sys.stderr)
            return results

        for hostname in data if isinstance(data, list) else []:
            results |= extract_subdomains(str(hostname), domain, bundle.host)
        return results