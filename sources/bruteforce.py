"""
Brute-force + permutation — usually the single biggest source of NEW
subdomains, since most subdomains never appear in certificates, code, or
archives at all.

Runs AFTER every other source (depends_on_others = True) so it can seed
permutations from whatever's already been found (e.g. if "api.example.com"
is known, it also tries "api-dev.example.com", "dev-api.example.com", etc.)

Every candidate is verified before being counted:
  1. Must resolve via DNS.
  2. Wildcard-DNS false positives are filtered automatically.
  3. Optional --http-verify pass confirms an actual HTTP(S) response.
"""

import os
import sys
from typing import Dict, Optional, Set

from core.base import BaseSource
from core.models import SourceResult
from core.registry import register
from extractors.regex import RegexBundle, extract_subdomains
from utils.dns_resolver import detect_wildcard_ips, http_verify_candidates, resolve_candidates

DEFAULT_WORDLIST = [
    "www", "mail", "ftp", "webmail", "smtp", "pop", "ns1", "ns2", "ns3", "ns4",
    "api", "dev", "staging", "stage", "test", "testing", "qa", "uat", "demo",
    "admin", "administrator", "portal", "dashboard", "panel", "cpanel",
    "app", "apps", "mobile", "m", "web", "beta", "alpha", "preview",
    "shop", "store", "cdn", "static", "assets", "media", "images", "img",
    "blog", "news", "forum", "community", "support", "help", "helpdesk",
    "docs", "documentation", "wiki", "kb",
    "vpn", "remote", "secure", "ssl", "auth", "login", "sso", "id", "accounts",
    "git", "gitlab", "github", "jenkins", "ci", "cd", "build", "jira", "confluence",
    "db", "database", "sql", "mysql", "postgres", "redis", "mongo",
    "internal", "intranet", "private", "corp", "office", "extranet",
    "old", "new", "legacy", "backup", "bak", "archive",
    "mail1", "mail2", "email", "exchange", "owa", "autodiscover",
    "cloud", "aws", "s3", "storage", "files", "upload", "download",
    "monitor", "monitoring", "grafana", "kibana", "elastic", "prometheus",
    "status", "health", "metrics", "logs", "logging",
    "payment", "payments", "pay", "billing", "checkout", "cart",
    "video", "stream", "live", "tv", "chat", "im",
    "ns", "mx", "dns", "proxy", "gateway", "gw", "lb", "loadbalancer",
    "prod", "production", "sandbox", "local",
    "partner", "partners", "affiliate", "vendor", "vendors",
    "career", "careers", "jobs", "hr",
    "events", "event", "training", "learn", "learning", "academy",
]

PERMUTATION_AFFIXES = ["dev", "staging", "stage", "test", "qa", "uat", "prod",
                        "old", "new", "internal", "backup", "beta", "v1", "v2", "01", "02"]


def generate_permutations(domain: str, seeds: Set[str], limit: int = 3000) -> Set[str]:
    candidates: Set[str] = set()
    labels = set()
    for sub in seeds:
        prefix = sub[: -len(domain) - 1] if sub.endswith(domain) else sub
        first_label = prefix.split(".")[0] if prefix else ""
        if first_label and first_label not in PERMUTATION_AFFIXES:
            labels.add(first_label)

    for label in labels:
        for affix in PERMUTATION_AFFIXES:
            candidates.add(f"{affix}-{label}.{domain}")
            candidates.add(f"{label}-{affix}.{domain}")
            candidates.add(f"{affix}.{label}.{domain}")
            candidates.add(f"{label}.{affix}.{domain}")
        for n in ("1", "2", "01", "02", "-1", "-2"):
            candidates.add(f"{label}{n}.{domain}")
        if len(candidates) >= limit:
            break
    return set(list(candidates)[:limit])


@register
class BruteforceSource(BaseSource):
    name = "bruteforce"
    display_name = "Brute-force + Permutation (DNS/HTTP-verified)"
    requires_key = None
    depends_on_others = True

    # tunable via env so the CLI can override without changing the signature
    wordlist_path: Optional[str] = None
    permutations_enabled: bool = True
    max_workers: int = 50
    dns_timeout: float = 3.0
    http_verify: bool = False
    http_timeout: float = 5.0

    def run(self, domain: str, bundle: RegexBundle,
            context: Optional[Dict[str, SourceResult]] = None) -> Set[str]:
        print("[*] Brute-forcing + verifying candidate subdomains...", file=sys.stderr)

        wildcard_ips = detect_wildcard_ips(domain, timeout=self.dns_timeout)
        if wildcard_ips:
            print(f"[!] {domain} has WILDCARD DNS ({len(wildcard_ips)} IP(s)). "
                  f"Candidates fully explained by the wildcard will be discarded "
                  f"automatically.", file=sys.stderr)

        words = list(DEFAULT_WORDLIST)
        if self.wordlist_path:
            try:
                with open(self.wordlist_path) as f:
                    words = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            except OSError as e:
                print(f"[!] Couldn't read wordlist '{self.wordlist_path}': {e}. Using built-in list.",
                      file=sys.stderr)

        candidates = {f"{w}.{domain}" for w in words}

        if self.permutations_enabled and context:
            seeds: Set[str] = set()
            for result in context.values():
                seeds |= result.subdomains
            if seeds:
                perms = generate_permutations(domain, seeds)
                print(f"[*] Generated {len(perms)} permutation candidates from prior results",
                      file=sys.stderr)
                candidates |= perms

        print(f"[*] Resolving {len(candidates)} candidates ({self.max_workers} workers)...",
              file=sys.stderr)
        live = resolve_candidates(candidates, max_workers=self.max_workers,
                                   timeout=self.dns_timeout, wildcard_ips=wildcard_ips or None)
        confirmed = set(live.keys())

        if self.http_verify and confirmed:
            print(f"[*] HTTP-verifying {len(confirmed)} DNS-confirmed candidates...",
                  file=sys.stderr)
            http_confirmed = http_verify_candidates(confirmed, max_workers=self.max_workers,
                                                      timeout=self.http_timeout)
            dropped = confirmed - http_confirmed
            if dropped:
                print(f"[i] Dropped {len(dropped)} DNS-only hit(s) with no HTTP(S) response.",
                      file=sys.stderr)
            confirmed = http_confirmed

        results: Set[str] = set()
        for host in confirmed:
            results |= extract_subdomains(host, domain, bundle.host)
        return results