from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="subdomain-al-sinwar",
        description="Subdomain-Al-Sinwar: High-Performance Passive Subdomain Enumeration",
    )

    parser.add_argument(
        "domain",
        nargs="?",
        default="",
        help="Target domain (e.g., example.com)",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output filepath",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Export output in JSON format",
    )

    parser.add_argument(
        "--csv",
        action="store_true",
        help="Export output in CSV format",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="HTTP request timeout in seconds",
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=100,
        help="Max async connections limit",
    )

    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="List all registered modules",
    )

    return parser