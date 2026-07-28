from __future__ import annotations

from typing import Set, Tuple
from config import GITHUB_TOKEN
from core.base import BaseSource
from utils.helpers import extract_subdomains


class GitHubSource(BaseSource):
    name = "GitHub Search"
    requires_key = True

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        if not GITHUB_TOKEN:
            return results

        url = f"https://api.github.com/search/code?q={domain}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            data = await self.fetch_json(url, headers=headers)
            if isinstance(data, dict) and "items" in data:
                for item in data["items"]:
                    html_url = item.get("html_url", "")
                    for sub in extract_subdomains(html_url, domain):
                        results.add((sub, f"Repo: {item.get('repository', {}).get('full_name')}"))
        except Exception:
            pass

        return results