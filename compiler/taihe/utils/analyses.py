# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Huawei Device Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module provides a framework for managing and caching instances of analysis objects.

The framework ensures that analyses are uniquely identified by their type and arguments,
avoiding redundant computation or memory usage.
"""

from abc import ABC, abstractmethod
from collections.abc import Hashable
from dataclasses import dataclass
from typing import Any, Generic, ParamSpec, TypeVar, cast

_P = ParamSpec("_P")
_A = TypeVar("_A", bound="AbstractAnalysis[Any]")


class AbstractAnalysis(Generic[_P], ABC):
    """Abstract Base class for all analyses.

    Enforcing the use of hashable argument for unique identification and caching.
    """

    @classmethod
    def get(
        cls: type[_A],
        am: "AnalysisManager",
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _A:
        """Get or create an analysis instance using the factory."""
        return am.get_or_create(cls, *args, **kwargs)

    @classmethod
    @abstractmethod
    def _create(
        cls: type[_A],
        am: "AnalysisManager",
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _A:
        """Create an instance of an analysis with the given arguments."""


@dataclass(frozen=True)
class CacheKey:
    """Represents a unique key for identifying cached analysis instances."""

    analysis_type: type[AbstractAnalysis[Any]]
    args: tuple[Hashable, ...]
    kwargs: tuple[tuple[str, Hashable], ...]


class AnalysisManager:
    """Manages caching and retrieval of analysis instances."""

    def __init__(self) -> None:
        self._cache: dict[CacheKey, AbstractAnalysis[Any]] = {}

    def get_or_create(
        self,
        analysis_type: type[_A],
        *args: Any,
        **kwargs: Any,
    ) -> _A:
        """Get existing analysis or create new one if not cached.

        The analysis is uniquely identified by its type and the provided arguments.
        """
        hashable_args = tuple(args)
        hashable_kwargs = tuple(sorted(kwargs.items()))
        key = CacheKey(analysis_type, hashable_args, hashable_kwargs)

        if cached_analysis := self._cache.get(key):
            return cast(_A, cached_analysis)

        created_analysis = analysis_type._create(self, *args, **kwargs)  # type: ignore
        self._cache[key] = created_analysis
        return created_analysis

    def provide(
        self,
        analysis: _A,
        analysis_type: type[_A],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Pre-populate the cache with an externally-constructed analysis instance.

        This can be used to seed the cache with analyses that are constructed
        outside of the standard factory mechanism, such as by backends.
        """
        hashable_args = tuple(args)
        hashable_kwargs = tuple(sorted(kwargs.items()))
        key = CacheKey(analysis_type, hashable_args, hashable_kwargs)

        if self._cache.setdefault(key, analysis) != analysis:
            raise ValueError(f"Analysis for {key} already exists in cache.")

    def clear(self) -> None:
        """Clear the analysis cache."""
        self._cache.clear()
