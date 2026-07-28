from __future__ import annotations

from typing import Set, Tuple
from core.base import BaseSource
from utils.helpers import extract_subdomains


class RapidDNSSource(BaseSource):
    name = "RapidDNS"

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        url = f"https://rapiddns.io/subdomain/{domain}?full=1"

        try:
            html = await self.fetch_text(url)
            if html:
                for sub in extract_subdomains(html, domain):
                    results.add((sub, "HTML Response"))
        except Exception:
            pass

        return results