from __future__ import annotations

from typing import Set, Tuple
from core.base import BaseSource
from utils.helpers import extract_subdomains


class AnubisSource(BaseSource):
    name = "Anubis"

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        url = f"https://jldc.me/anubis/subdomains/{domain}"

        try:
            data = await self.fetch_json(url)
            if isinstance(data, list):
                for hostname in data:
                    for sub in extract_subdomains(hostname, domain):
                        results.add((sub, "Anubis DB"))
        except Exception:
            pass

        return results