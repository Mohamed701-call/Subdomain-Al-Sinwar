"""urlscan.io — free, API key optional (higher rate limit with one)."""

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
class UrlscanSource(BaseSource):
    name = "urlscan"
    display_name = "urlscan.io"
    requires_key = None  # optional — works without a key at lower rate limits

    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        results: Set[str] = set()
        api_key = os.environ.get("URLSCAN_API_KEY")
        headers = {"User-Agent": USER_AGENT}
        if api_key:
            headers["API-Key"] = api_key

        try:
            resp = requests.get(
                "https://urlscan.io/api/v1/search/",
                params={"q": f"domain:{domain}", "size": "10000"},
                headers=headers, timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"[!] urlscan.io error: {e}", file=sys.stderr)
            return results

        for entry in data.get("results", []):
            page = entry.get("page", {})
            for field in ("domain", "url", "apexDomain"):
                val = page.get(field, "")
                if val:
                    results |= extract_subdomains(str(val), domain, bundle.host)
        return results