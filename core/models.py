"""Shared data models passed between sources, the manager, and output."""

from dataclasses import dataclass, field
from typing import Optional, Set


@dataclass
class SourceResult:
    """What every source returns after running."""
    name: str
    subdomains: Set[str] = field(default_factory=set)
    error: Optional[str] = None
    duration_seconds: float = 0.0
    skipped: bool = False
    skip_reason: Optional[str] = None

    @property
    def count(self) -> int:
        return len(self.subdomains)


@dataclass
class ScanResult:
    """Aggregated result of an entire scan across all sources."""
    domain: str
    per_source: dict  # name -> SourceResult
    all_subdomains: Set[str] = field(default_factory=set)
    dork_results: list = field(default_factory=list)

    @property
    def total_count(self) -> int:
        return len(self.all_subdomains)