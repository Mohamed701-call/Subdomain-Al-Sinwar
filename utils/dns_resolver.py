"""
DNS resolution, wildcard-DNS detection/filtering, and optional HTTP-level
verification — used to confirm that a brute-forced/permuted subdomain
candidate actually, really exists rather than just "looks plausible".

  1. DNS resolution (always) — candidate must resolve to an A/AAAA record.
  2. Wildcard filtering (always, automatic) — fingerprint the wildcard's IP
     set via random-label probes, discard any candidate whose IPs are
     entirely explained by that wildcard (i.e. not real evidence on its own).
  3. HTTP verification (optional) — extra confirmation pass, only keeps
     candidates that get an actual HTTP(S) response.
"""

import concurrent.futures
import random
import socket
import string
from typing import Dict, FrozenSet, Optional, Set

import requests

from core import USER_AGENT


def resolve_host_ips(hostname: str, timeout: float = 3.0) -> Optional[FrozenSet[str]]:
    try:
        socket.setdefaulttimeout(timeout)
        infos = socket.getaddrinfo(hostname, None)
        ips = frozenset(info[4][0] for info in infos)
        return ips if ips else None
    except (socket.gaierror, socket.timeout, UnicodeError, OSError):
        return None


def resolve_host(hostname: str, timeout: float = 3.0) -> bool:
    return resolve_host_ips(hostname, timeout) is not None


def detect_wildcard_ips(domain: str, timeout: float = 3.0, probes: int = 3) -> FrozenSet[str]:
    resolved_sets = []
    for _ in range(probes):
        label = "".join(random.choices(string.ascii_lowercase + string.digits, k=24))
        ips = resolve_host_ips(f"{label}.{domain}", timeout)
        if ips:
            resolved_sets.append(ips)
    if not resolved_sets:
        return frozenset()
    return frozenset().union(*resolved_sets)


def resolve_candidates(
    candidates: Set[str],
    max_workers: int = 50,
    timeout: float = 3.0,
    wildcard_ips: Optional[FrozenSet[str]] = None,
) -> Dict[str, FrozenSet[str]]:
    """Returns {hostname: ip_set} for candidates that resolve AND aren't
    fully explained by wildcard_ips."""
    live: Dict[str, FrozenSet[str]] = {}
    if not candidates:
        return live

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(resolve_host_ips, host, timeout): host for host in candidates}
        for future in concurrent.futures.as_completed(futures):
            host = futures[future]
            try:
                ips = future.result()
            except Exception:
                continue
            if not ips:
                continue
            if wildcard_ips and ips <= wildcard_ips:
                continue
            live[host] = ips

    return live


def http_verify_host(hostname: str, timeout: float = 5.0) -> bool:
    headers = {"User-Agent": USER_AGENT}
    for scheme in ("https", "http"):
        try:
            resp = requests.head(f"{scheme}://{hostname}", headers=headers,
                                  timeout=timeout, allow_redirects=True)
            if resp.status_code:
                return True
        except requests.RequestException:
            continue
    return False


def http_verify_candidates(candidates: Set[str], max_workers: int = 30,
                            timeout: float = 5.0) -> Set[str]:
    verified: Set[str] = set()
    if not candidates:
        return verified
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(http_verify_host, host, timeout): host for host in candidates}
        for future in concurrent.futures.as_completed(futures):
            host = futures[future]
            try:
                if future.result():
                    verified.add(host)
            except Exception:
                pass
    return verified