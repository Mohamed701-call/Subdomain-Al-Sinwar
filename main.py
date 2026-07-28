from __future__ import annotations

import asyncio
import sys
from cli import build_parser
from core.manager import SourceManager
from core.registry import SourceRegistry

from sources.crtsh import CrtShSource
from sources.virustotal import VirusTotalSource

from utils.banner import show_banner
from utils.logger import logger
from utils.output import save_results


def get_default_registry() -> SourceRegistry:
    registry = SourceRegistry()
    registry.register(CrtShSource)
    registry.register(VirusTotalSource)
    return registry


async def start():
    parser = build_parser()
    args = parser.parse_args()

    show_banner()

    registry = get_default_registry()

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
        results = await manager.run(args.domain)
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


def start_cli():
    asyncio.run(start())

if __name__ == "__main__":
    start_cli()