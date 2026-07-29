from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Set, Tuple

import httpx


class BaseSource(ABC):
    name: str = "Unknown"
    requires_key: bool = False

    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    @abstractmethod
    async def run(self, domain: str) -> Set[Tuple[str, str]]:
        raise NotImplementedError

    async def fetch_text(self, url: str, headers: Dict[str, str] | None = None, params: Dict[str, str] | None = None) -> str:
        try:
            response = await self.client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.text
        except Exception:
            pass
        return ""

    async def fetch_json(self, url: str, headers: Dict[str, str] | None = None, params: Dict[str, str] | None = None) -> dict | list:
        try:
            response = await self.client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return {}