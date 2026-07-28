from __future__ import annotations

import base64
from typing import Set, Tuple
from config import FOFA_EMAIL, FOFA_KEY
from core.base import BaseSource


class FofaSource(BaseSource):
    name = "FOFA"
    requires_key = True

    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        results = set()
        if not FOFA_EMAIL or not FOFA_KEY:
            return results

        query = f'domain="{domain}"'
        qbase64 = base64.b64encode(query.encode("utf-8")).decode("utf-8")
        url = f"https://fofa.info/api/v1/search/all?email={FOFA_EMAIL}&key={FOFA_KEY}&qbase64={qbase64}"

        try:
            data = await self.fetch_json(url)
            if isinstance(data, dict) and "results" in data:
                for row in data["results"]:
                    target = row[0] if isinstance(row, list) else row
                    if domain.lower() in target.lower():
                        clean_host = target.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
                        if clean_host.endswith(domain.lower()):
                            results.add((clean_host, "FOFA Search"))
        except Exception:
            pass

        return results