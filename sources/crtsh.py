from __future__ import annotations

from typing import Set, Tuple
from core.base import BaseSource
from utils.helpers import extract_subdomains


class CrtShSource(BaseSource):
    name = "crt.sh"

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    name_value = entry.get("name_value", "")
                    for name in name_value.split("\n"):
                        extracted = extract_subdomains(name, domain)
                        for sub in extracted:
                            results.add((sub, f"Cert ID: {entry.get('id')}"))
        except Exception:
            pass

        return results