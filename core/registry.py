"""Source registry. Every source module registers itself with @register on
import, so `sources/__init__.py` just has to import every module once and
the registry fills itself in — no manual list to maintain in the manager."""

from typing import Dict, Type

from core.base import BaseSource

_REGISTRY: Dict[str, Type[BaseSource]] = {}


def register(cls: Type[BaseSource]) -> Type[BaseSource]:
    if not getattr(cls, "name", None):
        raise ValueError(f"{cls.__name__} must set a 'name' class attribute")
    _REGISTRY[cls.name] = cls
    return cls


def get_source(name: str) -> Type[BaseSource]:
    return _REGISTRY[name]


def all_sources() -> Dict[str, Type[BaseSource]]:
    return dict(_REGISTRY)


def source_names() -> list:
    return sorted(_REGISTRY.keys())