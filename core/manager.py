from __future__ import annotations

import asyncio
import time
from typing import Dict, Set

import httpx
from rich.console import Console

from config import MAX_CONNECTIONS, MAX_KEEPALIVE, REQUEST_TIMEOUT, USER_AGENT
from core.models import ScanSession, SubdomainRecord
from core.registry import SourceRegistry

console = Console()


class SourceManager:
    def __init__(self, registry: SourceRegistry) -> None:
        self.registry = registry
        self.session_data = ScanSession(target_domain="")

    async def run(self, domain: str) -> Dict[str, SubdomainRecord]:
        self.session_data = ScanSession(target_domain=domain)

        limits = httpx.Limits(
            max_connections=MAX_CONNECTIONS,
            max_keepalive_connections=MAX_KEEPALIVE,
        )
        timeout = httpx.Timeout(float(REQUEST_TIMEOUT))

        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            limits=limits,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            tasks = []
            for source_cls in self.registry.all():
                source = source_cls(client)
                tasks.append(asyncio.create_task(self._execute(source, domain)))

            await asyncio.gather(*tasks)

        self.session_data.end_time = time.perf_counter()
        self.render_summary()
        return self.session_data.records

    async def _execute(self, source, domain: str):
        try:
            console.print(f"[cyan][{source.name}][/cyan] Searching...")
            discovered = await source.run(domain)

            count = 0
            for item in discovered:
                if isinstance(item, tuple):
                    hostname, proof = item[0], item[1]
                else:
                    hostname, proof = item, ""

                hostname = hostname.lower().strip(".")
                if not hostname.endswith(domain.lower()):
                    continue

                if hostname not in self.session_data.records:
                    self.session_data.records[hostname] = SubdomainRecord(hostname=hostname)

                self.session_data.records[hostname].add_discovery(source.name, proof)
                count += 1

            self.session_data.stats[source.name] = count
            console.print(f"[green][{source.name}][/green] Found: {count}")

        except Exception as exc:
            self.session_data.errors[source.name] = str(exc)
            console.print(f"[red][{source.name}] Failed[/red] {exc}")

    def render_summary(self):
        elapsed = self.session_data.end_time - self.session_data.start_time
        console.print()
        console.print("=" * 50)
        for source_name, count in self.session_data.stats.items():
            console.print(f"{source_name:<25} {count}")
        console.print("-" * 50)
        console.print(f"Total Unique      {len(self.session_data.records)}")
        console.print(f"Execution Time    {elapsed:.2f}s")
        console.print("=" * 50)