"""Central logger + event-bus wiring. Sources never call print() directly —
they raise/return, and this module turns manager events into console output.
Keeps logging concerns out of source code entirely."""

import logging
import sys

from core.events import SOURCE_COMPLETED, SOURCE_FAILED, SOURCE_SKIPPED, SOURCE_STARTED, EventBus


def get_logger(verbose: bool = True) -> logging.Logger:
    logger = logging.getLogger("subdomain_al_sinwar")
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    return logger


def wire_logging(event_bus: EventBus, logger: logging.Logger) -> None:
    """Attach console-output listeners to the event bus."""

    def on_started(name):
        logger.info(f"[*] Running {name}...")

    def on_completed(result):
        logger.info(f"[+] {result.name}: {result.count} subdomains found "
                     f"({result.duration_seconds:.1f}s)")

    def on_failed(result):
        logger.warning(f"[!] {result.name} failed: {result.error}")

    def on_skipped(name, missing_key):
        if missing_key:
            logger.warning(f"[!] {name} skipped — missing {missing_key} (set it in your "
                            f"config file or export it as an env var).")
        else:
            logger.warning(f"[!] {name} skipped.")

    event_bus.on(SOURCE_STARTED, on_started)
    event_bus.on(SOURCE_COMPLETED, on_completed)
    event_bus.on(SOURCE_FAILED, on_failed)
    event_bus.on(SOURCE_SKIPPED, on_skipped)