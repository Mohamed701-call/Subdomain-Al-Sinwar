from __future__ import annotations

import asyncio
import sys

from cli import build_parser
from core.manager import SourceManager
from core.registry import SourceRegistry
from utils.banner import show_banner
from utils.logger import logger
from utils.output import save_results


def start():
    parser = build_parser()
    args = parser.parse_args()

    show_banner()

    registry = SourceRegistry()

    if args.list_sources:
        print("Registered Passive Sources:")
        for src in registry.all():
            print(f" - {src.name}")
        sys.exit(0)

    if not args.domain:
        parser.print_help()
        sys.exit(1)

    manager = SourceManager(registry)

    try:
        results = asyncio.run(manager.run(args.domain))
        save_results(
            records=results,
            domain=args.domain,
            filename=args.output,
            json_output=args.json,
            csv_output=args.csv,
        )
    except KeyboardInterrupt:
        print("\n[!] KeyboardInterrupt detected. Saving collected results...")
        save_results(
            records=manager.session_data.records,
            domain=args.domain,
            filename=args.output,
            json_output=args.json,
            csv_output=args.csv,
        )
        print("Done. Interrupted gracefully.")

    logger.info(f"Enumeration completed for {args.domain}")


if __name__ == "__main__":
    start()