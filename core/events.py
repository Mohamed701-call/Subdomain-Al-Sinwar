from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SourceStarted:
    source: str


@dataclass(slots=True)
class SourceFinished:
    source: str
    found: int


@dataclass(slots=True)
class SourceFailed:
    source: str
    error: str