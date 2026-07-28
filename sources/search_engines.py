from __future__ import annotations

from typing import Set, Tuple
from core.base import BaseSource
from utils.helpers import extract_subdomains


class DuckDuckGoSource(BaseSource):
    name = "DuckDuckGo"

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        url = f"https://html.duckduckgo.com/html/?q=site:.{domain}"

        try:
            html = await self.fetch_text(url)
            if html:
                for sub in extract_subdomains(html, domain):
                    results.add((sub, "Search Engine Index"))
        except Exception:
            pass

        return results