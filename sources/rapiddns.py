"""RapidDNS.io — free passive DNS scrape, no key needed."""

import sys
from typing import Set

import requests

from core import USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains


@register
class RapidDnsSource(BaseSource):
    name = "rapiddns"
    display_name = "RapidDNS.io"
    requires_key = None

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        try:
            resp = requests.get(
                f"https://rapiddns.io/subdomain/{domain}", params={"full": "1"},
                headers={"User-Agent": USER_AGENT}, timeout=30,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[!] RapidDNS.io error: {e}", file=sys.stderr)
            return results

        results |= extract_subdomains(resp.text, domain, bundle.host)
        return results