"""AlienVault OTX — free passive DNS, no key needed."""

import json
import sys
from typing import Set

import requests

from core import USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains


@register
class AlienVaultSource(BaseSource):
    name = "alienvault"
    display_name = "AlienVault OTX"
    requires_key = None

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"[!] AlienVault OTX error: {e}", file=sys.stderr)
            return results

        for entry in data.get("passive_dns", []):
            hostname = entry.get("hostname", "")
            if hostname:
                results |= extract_subdomains(hostname, domain, bundle.host)
        return results