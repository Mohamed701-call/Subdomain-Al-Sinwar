from __future__ import annotations

from typing import List, Type
from core.base import BaseSource

from sources.crtsh import CrtShSource
from sources.virustotal import VirusTotalSource
from sources.alienvault import AlienVaultSource
from sources.rapiddns import RapidDNSSource
from sources.wayback import WaybackSource
from sources.urlscan import URLScanSource
from sources.securitytrails import SecurityTrailsSource
from sources.anubis import AnubisSource
from sources.hackertarget import HackerTargetSource
from sources.shodan import ShodanSource
from sources.threatcrowd import ThreatCrowdSource
from sources.fofa import FofaSource
from sources.github import GitHubSource
from sources.search_engines import DuckDuckGoSource


class SourceRegistry:
    def __init__(self) -> None:
        self._sources: List[Type[BaseSource]] = []
        self._register_defaults()

    def register(self, source: Type[BaseSource]) -> None:
        if source not in self._sources:
            self._sources.append(source)

    def _register_defaults(self) -> None:
        defaults = [
            CrtShSource,
            VirusTotalSource,
            AlienVaultSource,
            RapidDNSSource,
            WaybackSource,
            URLScanSource,
            SecurityTrailsSource,
            AnubisSource,
            HackerTargetSource,
            ShodanSource,
            ThreatCrowdSource,
            FofaSource,
            GitHubSource,
            DuckDuckGoSource,
        ]
        for src in defaults:
            self.register(src)

    def all(self) -> List[Type[BaseSource]]:
        return list(self._sources)

    def count(self) -> int:
        return len(self._sources)