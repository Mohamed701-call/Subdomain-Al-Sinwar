"""Every source implements this interface. The manager only ever talks to
sources through this contract — it doesn't know or care whether a source
hits a REST API, scrapes a page, or shells out to a binary."""

from abc import ABC, abstractmethod
from typing import Optional, Set

from extractors.regex import RegexBundle


class BaseSource(ABC):
    #: short machine name used in --sources, output, and the registry key
    name: str = "base"
    #: human-readable label for logs/output
    display_name: str = "Base Source"
    #: env var / config key this source needs, or None if no key required
    requires_key: Optional[str] = None

    def is_available(self) -> bool:
        """Whether this source can actually run (has any key it needs)."""
        if not self.requires_key:
            return True
        import os
        return bool(os.environ.get(self.requires_key))

    @abstractmethod
    def run(self, domain: str, bundle: RegexBundle) -> Set[str]:
        """Fetch data, extract subdomains, return the set. Raise on hard
        failure — the manager catches exceptions per-source so one failing
        source never takes down the whole scan."""
        raise NotImplementedError