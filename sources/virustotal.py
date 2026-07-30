"""VirusTotal — free community API key works, rate-limited to 4 req/min on
the free tier (respected automatically via the delay between pages)."""

import json
import os
import sys
import time
from typing import Set

import requests

from core import USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains


@register
class VirusTotalSource(BaseSource):
    name = "virustotal"
    display_name = "VirusTotal"
    requires_key = "VIRUSTOTAL_API_KEY"

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        api_key = os.environ.get("VIRUSTOTAL_API_KEY")
        headers = {"x-apikey": api_key, "User-Agent": USER_AGENT}
        url = f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains"
        params = {"limit": 40}

        for _ in range(3):  # max 3 pages by default, keeps free-tier rate limit sane
            try:
                resp = requests.get(url, headers=headers, params=params, timeout=20)
            except requests.RequestException as e:
                print(f"[!] VirusTotal request error: {e}", file=sys.stderr)
                break

            if resp.status_code == 401:
                print("[!] VirusTotal: invalid API key.", file=sys.stderr)
                break
            if resp.status_code == 429:
                print("[!] VirusTotal: rate limit hit (free tier is 4 req/min). Stopping.",
                      file=sys.stderr)
                break
            if resp.status_code != 200:
                print(f"[!] VirusTotal returned {resp.status_code}: {resp.text[:200]}",
                      file=sys.stderr)
                break

            try:
                data = resp.json()
            except (json.JSONDecodeError, ValueError) as e:
                print(f"[!] VirusTotal: couldn't parse response: {e}", file=sys.stderr)
                break

            items = data.get("data", [])
            if not items:
                break
            for item in items:
                hostname = item.get("id", "")
                if hostname:
                    results |= extract_subdomains(hostname, domain, bundle.host)

            next_url = data.get("links", {}).get("next")
            if not next_url:
                break
            url, params = next_url, {}
            time.sleep(15)  # respect the free-tier 4 req/min rate limit

        return results