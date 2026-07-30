"""ThreatCrowd — free, no key needed. WARNING: ThreatCrowd's public API has
been unreliable/frequently offline for years (the project is effectively
unmaintained). Kept as a best-effort source — if it's down, it just returns
nothing without breaking the rest of the scan."""

import json
import sys
from typing import Set

import requests

from core import USER_AGENT
from core.base import BaseSource
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains


@register
class ThreatCrowdSource(BaseSource):
    name = "threatcrowd"
    display_name = "ThreatCrowd"
    requires_key = None

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        url = "https://www.threatcrowd.org/searchApi/v2/domain/report/"
        try:
            resp = requests.get(url, params={"domain": domain},
                                 headers={"User-Agent": USER_AGENT}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"[!] ThreatCrowd error: {e} (this API is known to be frequently "
                  f"unreliable/offline — not necessarily a problem with this tool).",
                  file=sys.stderr)
            return results

        for hostname in data.get("subdomains", []) or []:
            results |= extract_subdomains(str(hostname), domain, bundle.host)
        return results