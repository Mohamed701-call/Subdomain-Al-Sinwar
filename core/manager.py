"""Runs sources and collects results. Independent sources (the vast
majority — anything that just hits an API) run in parallel via a thread
pool. Sources that need OTHER sources' results first (currently just
bruteforce, which seeds permutations from what's already been found) are
flagged with `depends_on_others = True` on the class and run afterward,
sequentially, with a `context` dict of everything found so far."""

import concurrent.futures
import time
from typing import Dict, List, Optional, Set

from core.base import BaseSource
from core.events import SOURCE_COMPLETED, SOURCE_FAILED, SOURCE_SKIPPED, SOURCE_STARTED, EventBus
from core.models import SourceResult
from core.registry import all_sources
from extractors.regex import RegexBundle


class SourceManager:
    def __init__(self, domain: str, bundle: RegexBundle, event_bus: Optional[EventBus] = None):
        self.domain = domain
        self.bundle = bundle
        self.events = event_bus or EventBus()

    def _run_one(self, source_cls, context: Dict[str, SourceResult]) -> SourceResult:
        instance = source_cls()
        start = time.time()

        if not instance.is_available():
            self.events.emit(SOURCE_SKIPPED, instance.name, instance.requires_key)
            return SourceResult(
                name=instance.name, skipped=True,
                skip_reason=f"missing required key: {instance.requires_key}",
            )

        self.events.emit(SOURCE_STARTED, instance.name)
        try:
            if getattr(instance, "depends_on_others", False):
                subs = instance.run(self.domain, self.bundle, context=context)
            else:
                subs = instance.run(self.domain, self.bundle)
            result = SourceResult(
                name=instance.name, subdomains=subs or set(),
                duration_seconds=time.time() - start,
            )
            self.events.emit(SOURCE_COMPLETED, result)
            return result
        except Exception as e:
            result = SourceResult(
                name=instance.name, error=str(e), duration_seconds=time.time() - start,
            )
            self.events.emit(SOURCE_FAILED, result)
            return result

    def run(self, selected: List[str], max_workers: int = 12) -> Dict[str, SourceResult]:
        registry = all_sources()
        classes = [registry[name] for name in selected if name in registry]

        independent = [c for c in classes if not getattr(c, "depends_on_others", False)]
        dependent = [c for c in classes if getattr(c, "depends_on_others", False)]

        results: Dict[str, SourceResult] = {}

        if independent:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._run_one, cls, results): cls.name for cls in independent
                }
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    results[result.name] = result

        # dependent sources run after, so they can see everything found so far
        for cls in dependent:
            result = self._run_one(cls, results)
            results[result.name] = result

        return results

    @staticmethod
    def merge(results: Dict[str, SourceResult]) -> Set[str]:
        merged: Set[str] = set()
        for r in results.values():
            merged |= r.subdomains
        return merged