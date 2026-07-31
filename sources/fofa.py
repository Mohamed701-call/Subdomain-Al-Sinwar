"""FOFA — requires FOFA_EMAIL + FOFA_KEY (free tier has very limited query
credits; paid tiers get much more)."""

import base64
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
class FofaSource(BaseSource):
    name = "fofa"
    display_name = "FOFA"
    requires_key = "FOFA_KEY"  # FOFA_EMAIL also required, checked separately below

    def is_available(self) -> bool:
        return bool(os.environ.get("FOFA_EMAIL")) and bool(os.environ.get("FOFA_KEY"))

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        email = os.environ.get("FOFA_EMAIL")
        key = os.environ.get("FOFA_KEY")

        query = f'domain="{domain}"'
        qbase64 = base64.b64encode(query.encode()).decode()

        try:
            resp = requests.get(
                "https://fofa.info/api/v1/search/all",
                params={"email": email, "key": key, "qbase64": qbase64,
                        "fields": "host,domain", "size": 1000},
                headers={"User-Agent": USER_AGENT}, timeout=20,
            )
        except requests.RequestException as e:
            print(f"[!] FOFA request error: {e}", file=sys.stderr)
            return results

        try:
            data = resp.json()
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[!] FOFA: couldn't parse response: {e}", file=sys.stderr)
            return results

        if data.get("error"):
            print(f"[!] FOFA error: {data.get('errmsg', 'unknown error')}", file=sys.stderr)
            return results

        for row in data.get("results", []):
            for val in row:
                if val:
                    results |= extract_subdomains(str(val), domain, bundle.host)
        return results