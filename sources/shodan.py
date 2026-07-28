from __future__ import annotations

from typing import Set, Tuple
from config import SHODAN_API_KEY
from core.base import BaseSource


class ShodanSource(BaseSource):
    name = "Shodan"
    requires_key = True

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        if not SHODAN_API_KEY:
            return results

        url = f"https://api.shodan.io/dns/domain/{domain}?key={SHODAN_API_KEY}"

        try:
            data = await self.fetch_json(url)
            if isinstance(data, dict) and "subdomains" in data:
                for sub in data["subdomains"]:
                    full_hostname = f"{sub}.{domain}".lower()
                    results.add((full_hostname, "Shodan DNS Engine"))
        except Exception:
            pass

        return results