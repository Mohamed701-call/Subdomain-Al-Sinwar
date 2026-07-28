from __future__ import annotations

from typing import Set, Tuple
from core.base import BaseSource
from utils.helpers import extract_subdomains


class AlienVaultSource(BaseSource):
    name = "AlienVault OTX"

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"

        try:
            data = await self.fetch_json(url)
            if isinstance(data, dict) and "passive_dns" in data:
                for entry in data["passive_dns"]:
                    hostname = entry.get("hostname", "")
                    for sub in extract_subdomains(hostname, domain):
                        results.add((sub, f"Record: {entry.get('record_type')}"))
        except Exception:
            pass

        return results