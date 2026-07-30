"""Minimal event bus so sources/manager don't need to know about logging or
printing directly — they just emit events, and whatever's listening (the CLI
logger, a future GUI, tests...) decides what to do with them."""

from collections import defaultdict
from typing import Callable, DefaultDict, List


class EventBus:
    def __init__(self):
        self._listeners: DefaultDict[str, List[Callable]] = defaultdict(list)

    def on(self, event: str, callback: Callable) -> None:
        self._listeners[event].append(callback)

    def emit(self, event: str, *args, **kwargs) -> None:
        for callback in self._listeners.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                # a broken listener should never crash the scan
                pass


# Standard event names emitted by core.manager.SourceManager
SOURCE_STARTED = "source_started"
SOURCE_COMPLETED = "source_completed"
SOURCE_FAILED = "source_failed"
SOURCE_SKIPPED = "source_skipped"