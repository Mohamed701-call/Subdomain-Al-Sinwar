from __future__ import annotations

from typing import Set, Tuple
from config import URLSCAN_API_KEY
from core.base import BaseSource
from utils.helpers import extract_subdomains


class URLScanSource(BaseSource):
    name = "URLScan"

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        headers = {}
        if URLSCAN_API_KEY:
            headers["API-Key"] = URLSCAN_API_KEY

        url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}"

        try:
            data = await self.fetch_json(url, headers=headers)
            if isinstance(data, dict) and "results" in data:
                for item in data["results"]:
                    page_domain = item.get("page", {}).get("domain", "")
                    for sub in extract_subdomains(page_domain, domain):
                        results.add((sub, f"Scan ID: {item.get('_id')}"))
        except Exception:
            pass

        return results