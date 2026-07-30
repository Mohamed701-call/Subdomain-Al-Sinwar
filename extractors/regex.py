"""
Multi-regex extraction system.

A single generic regex misses a lot of real-world leakage patterns —
wildcard cert entries, CNAME zone dumps, URLs buried in JS bundles, etc.
So instead of one regex we build FOUR, each tuned to a different way a
subdomain shows up in the wild, then run every one of them over any given
blob of text and merge + normalize + validate + dedupe the results.

    HOST      -> bare hostname anywhere in text: api.example.com
    URL       -> only matches when preceded by a scheme: https://api.example.com/path
    WILDCARD  -> cert/DNS wildcard entries: *.example.com  ->  normalized to example.com's wildcard label stripped
    CNAME     -> DNS-zone-style lines: "sub  IN  CNAME  target.example.com."  or  "CNAME sub.example.com"
"""

import re
from dataclasses import dataclass
from typing import Set


@dataclass
class RegexBundle:
    domain: str
    host: re.Pattern
    url: re.Pattern
    wildcard: re.Pattern
    cname: re.Pattern


def _label_pattern() -> str:
    # one DNS label: alnum/underscore/hyphen, 1-63 chars, no leading/trailing hyphen
    return r"[a-zA-Z0-9_](?:[a-zA-Z0-9_-]{0,61}[a-zA-Z0-9_])?"


def build_regex_bundle(domain: str) -> RegexBundle:
    escaped = re.escape(domain)
    label = _label_pattern()

    host = re.compile(rf"\b(?:{label}\.)+{escaped}\b", re.IGNORECASE)
    url = re.compile(rf"https?://(?:{label}\.)+{escaped}\b", re.IGNORECASE)
    wildcard = re.compile(rf"\*\.(?:{label}\.)*{escaped}\b", re.IGNORECASE)
    cname = re.compile(
        rf"(?:CNAME\s+|^\s*{label}\s+(?:IN\s+)?CNAME\s+)((?:{label}\.)+{escaped})\.?",
        re.IGNORECASE | re.MULTILINE,
    )
    return RegexBundle(domain=domain, host=host, url=url, wildcard=wildcard, cname=cname)


# kept for callers that only need the plain host regex (most sources)
def build_domain_regex(domain: str) -> re.Pattern:
    return build_regex_bundle(domain).host


def normalize_hostname(raw: str) -> str:
    return raw.strip().strip(".").lower().lstrip("*.")


def is_valid_subdomain(candidate: str, domain: str) -> bool:
    if not candidate or len(candidate) > 253:
        return False
    if not candidate.endswith(domain):
        return False
    labels = candidate.split(".")
    label_re = re.compile(rf"^{_label_pattern()}$")
    return all(label_re.match(lbl) for lbl in labels)


def extract_subdomains(text: str, domain: str, rx: re.Pattern) -> Set[str]:
    """Single-regex extraction — kept for simple sources that only need the
    plain host pattern (most passive-DNS style sources)."""
    found = set()
    for match in rx.findall(text):
        candidate = normalize_hostname(match)
        if is_valid_subdomain(candidate, domain) or candidate == domain:
            found.add(candidate)
    return found


def extract_all(text: str, bundle: RegexBundle) -> Set[str]:
    """Full multi-regex pass: host + URL + wildcard + CNAME, normalized,
    validated, and deduplicated into one set. Use this for sources that pull
    in messy/mixed content (code repos, configs, HTML pages)."""
    found: Set[str] = set()

    for match in bundle.host.findall(text):
        found.add(normalize_hostname(match))

    for match in bundle.url.findall(text):
        # url regex captures the whole scheme+host; strip the scheme back off
        hostname = re.sub(r"^https?://", "", match, flags=re.IGNORECASE)
        found.add(normalize_hostname(hostname))

    for match in bundle.wildcard.findall(text):
        found.add(normalize_hostname(match))

    for match in bundle.cname.findall(text):
        found.add(normalize_hostname(match))

    return {c for c in found if is_valid_subdomain(c, bundle.domain) or c == bundle.domain}