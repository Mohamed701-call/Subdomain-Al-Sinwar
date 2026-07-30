"""Argument parsing. Orchestration logic lives in main.py — this module
only builds and returns the parser."""

import argparse

from config import CONFIG_KEYS
from core import TOOL_NAME
from utils.output import DEFAULT_SOURCE_ORDER


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description=f"{TOOL_NAME} — passive + active subdomain enumeration: crt.sh, GitHub "
                     "(code/commits/issues+PRs), SecurityTrails, VirusTotal, Shodan, FOFA, "
                     "favicon-hash+Shodan, ProjectDiscovery Cloud DNS, Anubis, Wayback Machine, "
                     "urlscan.io, HackerTarget, AlienVault OTX, RapidDNS, ThreatCrowd, "
                     "DNS/HTTP-verified brute-force, and search-engine dorks.",
    )
    parser.add_argument("domain", help="Target root domain, e.g. example.com")
    parser.add_argument(
        "--sources",
        default="crtsh,github,securitytrails,virustotal,shodan,fofa,favicon_shodan,"
                 "projectdiscovery_cloud,anubis,wayback,urlscan,hackertarget,alienvault,"
                 "rapiddns,threatcrowd,bruteforce",
        help="Comma-separated list of sources. Default: all (sources missing a required "
             "API key are skipped automatically, no error).",
    )
    parser.add_argument("-o", "--output", help="Write plain-text subdomain list to this file")
    parser.add_argument("--json", dest="json_out", help="Write full JSON results to this file")
    parser.add_argument(
        "--config",
        help="Path to a config file with API keys (KEY=VALUE per line). If not given, "
             "auto-searches ~/.config/subdomain-al-sinwar/config, ./config.env, ./.env. "
             f"Recognized keys: {', '.join(CONFIG_KEYS)}.",
    )
    parser.add_argument("--wordlist", help="Custom wordlist file for brute-force "
                                            "(one label per line). Falls back to a built-in list.")
    parser.add_argument("--no-permutations", action="store_true",
                         help="Skip permutation generation during brute-force")
    parser.add_argument("--http-verify", action="store_true",
                         help="Extra confirmation pass for brute-force: real HTTP(S) request "
                              "against each DNS-confirmed candidate, keep only real responses.")
    parser.add_argument("--dns-workers", type=int, default=50,
                         help="Parallel DNS resolution workers for brute-force (default: 50)")
    parser.add_argument("--dns-timeout", type=float, default=3.0,
                         help="Per-lookup DNS resolution timeout in seconds (default: 3.0)")
    parser.add_argument("--http-timeout", type=float, default=5.0,
                         help="Per-request HTTP verification timeout in seconds (default: 5.0)")
    parser.add_argument("--resolve", action="store_true",
                         help="DNS-verify ALL final results (wildcard-aware) and drop any "
                              "that don't hold up")
    parser.add_argument("--breakdown", action="store_true",
                         help="Show which source(s) found each subdomain")
    parser.add_argument("--show-dorks", action="store_true",
                         help="Print search-engine dork queries to stdout (off by default). "
                              "Always included in --json output regardless.")
    parser.add_argument(
        "--source-order",
        default=",".join(DEFAULT_SOURCE_ORDER),
        help="Comma-separated source priority for file output ordering/dedup.",
    )
    parser.add_argument("--no-banner", action="store_true", help="Skip the startup banner")
    return parser