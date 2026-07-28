from __future__ import annotations

from typing import Set, Tuple
from config import SECURITYTRAILS_API_KEY
from core.base import BaseSource


class SecurityTrailsSource(BaseSource):
    name = "SecurityTrails"
    requires_key = True

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        if not SECURITYTRAILS_API_KEY:
            return results

        url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
        headers = {"APIKEY": SECURITYTRAILS_API_KEY}

        try:
            data = await self.fetch_json(url, headers=headers)
            if isinstance(data, dict) and "subdomains" in data:
                for sub in data["subdomains"]:
                    full_hostname = f"{sub}.{domain}".lower()
                    results.add((full_hostname, "SecurityTrails API"))
        except Exception:
            pass

        return results