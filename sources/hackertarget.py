from __future__ import annotations

from typing import Set, Tuple
from core.base import BaseSource
from utils.helpers import extract_subdomains


class HackerTargetSource(BaseSource):
    name = "HackerTarget"

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"

        try:
            text = await self.fetch_text(url)
            if text and "error" not in text.lower():
                for line in text.splitlines():
                    parts = line.split(",")
                    if parts:
                        for sub in extract_subdomains(parts[0], domain):
                            results.add((sub, f"IP: {parts[1]}" if len(parts) > 1 else "HostSearch"))
        except Exception:
            pass

        return results