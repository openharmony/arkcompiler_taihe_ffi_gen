"""This module provides a framework for managing and caching instances of analysis objects.

Key classes and their responsibilities:
- `AbstractAnalysis`: Defines the base class for all analysis types, enforcing the use of
  hashable arguments for unique identification and caching.
- `AnalysisManager`: Manages caching and retrieval of analysis objects.
- `CacheKey`: Represents a unique key for identifying cached analysis instances.

The framework ensures that analyses are uniquely identified by their type and arguments,
avoiding redundant computation or memory usage.
"""

from abc import ABC
from collections.abc import Hashable
from dataclasses import dataclass
from typing import Final, Generic, ParamSpec, TypeVar

P = ParamSpec("P")
A = TypeVar("A", bound="AbstractAnalysis")


@dataclass(frozen=True)
class CacheKey(Generic[A]):
    analysis_type: type[A]
    args: Hashable
    kwargs: Hashable


class AbstractAnalysis(ABC, Generic[P]):
    """Base class for all analyses with enforced hashable arguments."""

    def __init__(
        self,
        am: "AnalysisManager",
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        """Initialize analysis with hashable arguments."""

    @classmethod
    def get(
        cls: type[A],
        am: "AnalysisManager",
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> A:
        """Get or create a cached analysis instance."""
        return am.get_or_create(cls, *args, **kwargs)


class AnalysisManager:
    """Manages caching and retrieval of analysis instances."""

    def __init__(self) -> None:
        self._cache: Final[dict[CacheKey, AbstractAnalysis]] = {}

    def get_or_create(
        self,
        analysis_type: type[A],
        *args,
        **kwargs,
    ) -> A:
        """Get existing analysis or create new one if not cached."""
        key = CacheKey(analysis_type, tuple(args), frozenset(kwargs))

        if cached := self._cache.get(key):
            assert isinstance(cached, analysis_type)
            return cached

        new_instance = analysis_type(self, *args, **kwargs)
        self._cache[key] = new_instance
        return new_instance

    def clear(self) -> None:
        """Clear the analysis cache."""
        self._cache.clear()
