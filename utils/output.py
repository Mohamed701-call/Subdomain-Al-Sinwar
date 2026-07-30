"""Turns a dict of {source_name: SourceResult} into ordered output and
writes it to disk (plain text and/or JSON), with permission-error handling."""

import json
import sys
from typing import Dict, List

from core.models import SourceResult

DEFAULT_SOURCE_ORDER = [
    "github", "securitytrails", "virustotal", "shodan", "fofa",
    "projectdiscovery_cloud", "favicon_shodan", "crtsh", "anubis",
    "wayback", "urlscan", "hackertarget", "alienvault", "rapiddns",
    "threatcrowd", "bruteforce",
]


def order_by_source(per_source: Dict[str, SourceResult], priority: List[str]) -> List[str]:
    """A subdomain found by multiple sources is listed once, under the
    first source (by priority) that found it."""
    seen = set()
    ordered: List[str] = []
    remaining = [n for n in per_source if n not in priority]
    for name in priority + remaining:
        result = per_source.get(name)
        if not result or not result.subdomains:
            continue
        for s in sorted(result.subdomains):
            if s not in seen:
                seen.add(s)
                ordered.append(s)
    return ordered


def write_text(path: str, subdomains: List[str], source_order: List[str]) -> bool:
    try:
        with open(path, "w") as f:
            f.write("\n".join(subdomains) + "\n")
        print(f"\n[+] Subdomain list written to {path} "
              f"(ordered by source: {', '.join(source_order)}, deduplicated)", file=sys.stderr)
        return True
    except PermissionError:
        print(
            f"\n[!] Permission denied writing to '{path}'. Usually means a file with that "
            f"name already exists and is owned by another user (e.g. leftover from a 'sudo' "
            f"run). Try:\n    ls -l {path}\n    sudo rm {path}   # if safe\n  or use a "
            f"different filename.", file=sys.stderr,
        )
        return False
    except OSError as e:
        print(f"\n[!] Couldn't write to '{path}': {e}", file=sys.stderr)
        return False


def write_json(path: str, domain: str, per_source: Dict[str, SourceResult],
                sorted_subs: List[str], ordered_subs: List[str],
                source_order: List[str], dork_results: list, tool_name: str) -> bool:
    payload = {
        "tool": tool_name,
        "domain": domain,
        "subdomains_alphabetical": sorted_subs,
        "subdomains_by_source_order": ordered_subs,
        "source_order_used": source_order,
        "count": len(sorted_subs),
        "counts_by_source": {n: r.count for n, r in per_source.items()},
        "by_source": {n: sorted(r.subdomains) for n, r in per_source.items()},
        "errors_by_source": {n: r.error for n, r in per_source.items() if r.error},
        "skipped_sources": {n: r.skip_reason for n, r in per_source.items() if r.skipped},
        "google_dorks": [{"query": q, "url": u} for q, u in dork_results],
    }
    try:
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"[+] JSON results written to {path}", file=sys.stderr)
        return True
    except PermissionError:
        print(f"[!] Permission denied writing to '{path}'. Check ownership with "
              f"'ls -l {path}' and remove/rename as needed.", file=sys.stderr)
        return False
    except OSError as e:
        print(f"[!] Couldn't write to '{path}': {e}", file=sys.stderr)
        return False