from __future__ import annotations

from typing import Set, Tuple
from core.base import BaseSource


class ThreatCrowdSource(BaseSource):
    name = "ThreatCrowd"

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={domain}"

        try:
            data = await self.fetch_json(url)
            if isinstance(data, dict) and "subdomains" in data:
                for sub in data["subdomains"]:
                    sub_clean = sub.lower().strip()
                    if sub_clean.endswith(domain.lower()):
                        results.add((sub_clean, "ThreatCrowd Report"))
        except Exception:
            pass

        return results