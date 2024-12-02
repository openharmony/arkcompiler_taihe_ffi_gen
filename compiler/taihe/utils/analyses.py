"""This module provides a framework for managing and caching instances of analysis objects.

Key classes and their responsibilities:
- `AbstractAnalysis`: Defines the base class for all analysis types, enforcing the use of
  hashable arguments for unique identification and caching.
- `AnalysisManager`: Manages caching and retrieval of analysis objects.
- `CacheKey`: Represents a unique key for identifying cached analysis instances.

The framework ensures that analyses are uniquely identified by their type and arguments,
avoiding redundant computation or memory usage.
"""

from abc import ABC, abstractmethod
from collections.abc import Hashable
from dataclasses import dataclass
from typing import Final, Generic, TypeVar

A = TypeVar("A", bound="AbstractAnalysis")


@dataclass(frozen=True)
class CacheKey(Generic[A]):
    analysis_type: type[A]
    iderntifier: Hashable


class AbstractAnalysis(ABC):
    """Base class for all analyses with enforced hashable arguments."""

    @abstractmethod
    def __init__(self, am: "AnalysisManager", *args) -> None:
        """Initialize analysis with hashable arguments."""

    @classmethod
    def get(cls: type[A], am: "AnalysisManager", *args) -> A:
        """Get or create a cached analysis instance."""
        return am.get_or_create(cls, *args)


class AnalysisManager:
    """Manages caching and retrieval of analysis instances."""

    def __init__(self) -> None:
        self._cache: Final[dict[CacheKey, AbstractAnalysis]] = {}

    def get_or_create(self, analysis_type: type[A], *args) -> A:
        """Get existing analysis or create new one if not cached."""
        key = CacheKey(analysis_type, args)

        if cached := self._cache.get(key):
            assert isinstance(cached, analysis_type)
            return cached

        new_instance = analysis_type(self, *args)
        self._cache[key] = new_instance
        return new_instance

    def clear(self) -> None:
        """Clear the analysis cache."""
        self._cache.clear()
