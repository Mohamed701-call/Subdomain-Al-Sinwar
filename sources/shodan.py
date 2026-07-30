"""Shodan — requires a Shodan API key (free tier available, limited query
credits). Also exposes `shodan_search()`, a shared helper used by
sources/favicon_shodan.py to run arbitrary Shodan search queries."""

import json
import os
import sys
from typing import List, Optional, Set

import requests

from core import USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains


def shodan_search(query: str, api_key: str, max_pages: int = 3, timeout: int = 20) -> List[dict]:
    """Run a Shodan host search (api.shodan.io/shodan/host/search) and return
    the raw list of match dicts (each has 'ip_str', 'hostnames', etc.)."""
    matches: List[dict] = []
    for page in range(1, max_pages + 1):
        try:
            resp = requests.get(
                "https://api.shodan.io/shodan/host/search",
                params={"key": api_key, "query": query, "page": page},
                headers={"User-Agent": USER_AGENT}, timeout=timeout,
            )
        except requests.RequestException as e:
            print(f"[!] Shodan search request error: {e}", file=sys.stderr)
            break

        if resp.status_code == 401:
            print("[!] Shodan: invalid API key.", file=sys.stderr)
            break
        if resp.status_code != 200:
            print(f"[!] Shodan search returned {resp.status_code}: {resp.text[:200]}",
                  file=sys.stderr)
            break

        try:
            data = resp.json()
        except (json.JSONDecodeError, ValueError):
            break

        page_matches = data.get("matches", [])
        matches.extend(page_matches)
        if len(page_matches) == 0 or len(matches) >= data.get("total", 0):
            break
    return matches


@register
class ShodanSource(BaseSource):
    name = "shodan"
    display_name = "Shodan (DNS domain)"
    requires_key = "SHODAN_API_KEY"

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        api_key = os.environ.get("SHODAN_API_KEY")
        url = f"https://api.shodan.io/dns/domain/{domain}"
        try:
            resp = requests.get(url, params={"key": api_key},
                                 headers={"User-Agent": USER_AGENT}, timeout=20)
        except requests.RequestException as e:
            print(f"[!] Shodan request error: {e}", file=sys.stderr)
            return results

        if resp.status_code == 401:
            print("[!] Shodan: invalid API key.", file=sys.stderr)
            return results
        if resp.status_code != 200:
            print(f"[!] Shodan returned {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
            return results

        try:
            data = resp.json()
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[!] Shodan: couldn't parse response: {e}", file=sys.stderr)
            return results

        for label in data.get("subdomains", []):
            candidate = f"{label}.{domain}".lower()
            results |= extract_subdomains(candidate, domain, bundle.host)
        return results