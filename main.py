"""Orchestration: wires config -> manager -> sources -> output together."""

import os
import sys

from cli import build_parser
from config import load_config
from core import TOOL_NAME
from core.events import EventBus
from core.manager import SourceManager
from extractors.regex import build_regex_bundle
from sources.bruteforce import BruteforceSource
from sources.search_engines import generate_dorks
from utils.banner import print_banner
from utils.dns_resolver import detect_wildcard_ips, resolve_candidates
from utils.helpers import is_valid_domain
from utils.logger import get_logger, wire_logging
from utils.output import DEFAULT_SOURCE_ORDER, order_by_source, write_json, write_text


def main() -> None:
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        print(
            "[!] Warning: running as root/sudo. Output files will be root-owned, which "
            "causes 'Permission denied' next time you run as a normal user.",
            file=sys.stderr,
        )

    parser = build_parser()
    args = parser.parse_args()

    load_config(args.config)

    domain = args.domain.strip().lower()
    if not is_valid_domain(domain):
        print(f"[!] '{domain}' doesn't look like a valid domain.", file=sys.stderr)
        sys.exit(1)

    if not args.no_banner:
        print_banner()

    logger = get_logger()
    event_bus = EventBus()
    wire_logging(event_bus, logger)

    bundle = build_regex_bundle(domain)
    sources = [s.strip().lower() for s in args.sources.split(",") if s.strip()]

    # Configure the brute-force source's tunables (it's a normal registered
    # source, but its behavior is CLI-configurable, so set attributes on the
    # class before the manager instantiates it).
    BruteforceSource.wordlist_path = args.wordlist
    BruteforceSource.permutations_enabled = not args.no_permutations
    BruteforceSource.max_workers = args.dns_workers
    BruteforceSource.dns_timeout = args.dns_timeout
    BruteforceSource.http_verify = args.http_verify
    BruteforceSource.http_timeout = args.http_timeout

    print(f"\n{TOOL_NAME} — enumerating subdomains for {domain}\n", file=sys.stderr)

    manager = SourceManager(domain, bundle, event_bus)
    per_source = manager.run(sources)
    all_subdomains = SourceManager.merge(per_source)

    dork_results = list(generate_dorks(domain))  # cheap/local; only printed if --show-dorks

    if args.resolve:
        print(f"\n[*] Verifying all {len(all_subdomains)} results via DNS resolution "
              f"({args.dns_workers} workers)...", file=sys.stderr)
        wildcard_ips = detect_wildcard_ips(domain, timeout=args.dns_timeout)
        live_map = resolve_candidates(all_subdomains, max_workers=args.dns_workers,
                                       timeout=args.dns_timeout, wildcard_ips=wildcard_ips or None)
        live = set(live_map.keys())
        dead = all_subdomains - live
        if dead:
            print(f"[!] Dropped {len(dead)} non-resolving/wildcard-only subdomains.",
                  file=sys.stderr)
        all_subdomains = live
        for result in per_source.values():
            result.subdomains &= live

    sorted_subs = sorted(all_subdomains)
    source_order = [s.strip().lower() for s in args.source_order.split(",") if s.strip()]
    ordered_subs = order_by_source(per_source, source_order)

    print("\n" + "=" * 60)
    print(f"{TOOL_NAME} — Results for {domain}")
    print("=" * 60)

    print("\n[+] Subdomains found per source:")
    for name, result in per_source.items():
        if result.skipped:
            print(f"    {name}: skipped ({result.skip_reason})")
        elif result.error:
            print(f"    {name}: error ({result.error})")
        else:
            print(f"    {name}: {result.count}")
    print(f"    TOTAL (deduplicated across all sources): {len(sorted_subs)}")

    print(f"\n[+] {len(sorted_subs)} unique subdomains:\n")
    for s in sorted_subs:
        print(s)

    if args.breakdown:
        print("\n" + "-" * 60)
        print("Source breakdown")
        print("-" * 60)
        for name, result in per_source.items():
            if not result.subdomains:
                continue
            print(f"\n  {name} ({result.count}):")
            for s in sorted(result.subdomains):
                print(f"    {s}")

    if args.show_dorks:
        print(f"\n[+] Search-engine dork queries (open manually or use a SERP API):\n")
        for engine, query, url in dork_results:
            print(f"  [{engine}] {query}\n    -> {url}")

    if args.output:
        write_text(args.output, ordered_subs, source_order)

    if args.json_out:
        dork_pairs = [(q, u) for _, q, u in dork_results]
        write_json(args.json_out, domain, per_source, sorted_subs, ordered_subs,
                   source_order, dork_pairs, TOOL_NAME)


def run() -> None:
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    run()