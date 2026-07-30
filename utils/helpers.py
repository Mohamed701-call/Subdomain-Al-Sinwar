"""Small generic helpers used across the codebase."""

import re
from typing import Iterable, Iterator, List, TypeVar

T = TypeVar("T")

_DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)


def is_valid_domain(domain: str) -> bool:
    return bool(_DOMAIN_RE.match(domain.strip().lower()))


def chunked(items: List[T], size: int) -> Iterator[List[T]]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


def dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out