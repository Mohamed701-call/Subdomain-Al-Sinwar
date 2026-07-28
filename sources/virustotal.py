from __future__ import annotations

from typing import Set, Tuple
from config import VIRUSTOTAL_API_KEY
from core.base import BaseSource


class VirusTotalSource(BaseSource):
    name = "VirusTotal"
    requires_key = True

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        if not VIRUSTOTAL_API_KEY:
            return results

        url = f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains?limit=40"
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}

        try:
            data = await self.fetch_json(url, headers=headers)
            if isinstance(data, dict) and "data" in data:
                for item in data["data"]:
                    subdomain = item.get("id", "")
                    if subdomain.lower().endswith(domain.lower()):
                        results.add((subdomain, "VT Domain Endpoint"))
        except Exception:
            pass

        return results