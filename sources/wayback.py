from __future__ import annotations

from typing import Set, Tuple
from core.base import BaseSource
from utils.helpers import extract_subdomains


class WaybackSource(BaseSource):
    name = "Wayback Machine"

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&fl=original&collapse=urlkey"

        try:
            data = await self.fetch_json(url)
            if isinstance(data, list) and len(data) > 1:
                for row in data[1:]:
                    if row:
                        for sub in extract_subdomains(row[0], domain):
                            results.add((sub, f"Archived URL: {row[0][:80]}"))
        except Exception:
            pass

        return results