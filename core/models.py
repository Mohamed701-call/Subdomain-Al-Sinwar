from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class SubdomainRecord:
    hostname: str
    sources: Set[str] = field(default_factory=set)
    evidence: Dict[str, str] = field(default_factory=dict)
    confidence_score: int = 0

    def add_discovery(self, source_name: str, proof: str = "") -> None:
        self.sources.add(source_name)
        if proof:
            self.evidence[source_name] = proof
        self.update_score()

    def update_score(self) -> None:
        count = len(self.sources)
        if count == 1:
            self.confidence_score = 40
        elif count == 2:
            self.confidence_score = 70
        else:
            self.confidence_score = min(100, 70 + (count - 2) * 15)


@dataclass
class ScanSession:
    target_domain: str
    start_time: float = field(default_factory=time.perf_counter)
    end_time: float = 0.0
    records: Dict[str, SubdomainRecord] = field(default_factory=dict)
    stats: Dict[str, int] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)