from __future__ import annotations

import re
from pathlib import Path
from typing import Set

SUBDOMAIN_REGEX = re.compile(r"(?:[a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,}")


def extract_subdomains(text: str, domain: str) -> Set[str]:
    results = set()
    for match in SUBDOMAIN_REGEX.findall(text):
        match = match.lower().strip(".")
        if match.endswith(domain.lower()):
            results.add(match)
    return results


def ensure_output_directory() -> Path:
    output = Path("output")
    output.mkdir(parents=True, exist_ok=True)
    return output