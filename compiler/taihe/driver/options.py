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

"""Backend-specific configuration options framework.

This module provides a type-safe, extensible framework for backend-specific
compiler configuration options. Unlike attributes (which attach to declarations),
config options are global settings that affect code generation behavior.

## Architecture

The system follows a simple design:

```
AbstractConfigOption (ABC)
└── Concrete options defined by backends

ConfigRegistry
└── Temporary registry for parsing raw config dict

OptionStore
└── Storage for parsed config options (dict[type[AbstractConfigOption], list[AbstractConfigOption]])
```

## Lifecycle

1. **Backend Collection**: `BackendRegistry.collect_required_backends()` gathers all
   required backends
2. **Option Registration**: Each backend's `BackendConfig.register()` registers its
   option types into `OptionRegistry`
3. **Parsing**: `OptionRegistry.parse_args()` validates and parses raw config strings
   into an `OptionStore`
4. **Consumption**: `BackendConfig.create(options)` reads the `OptionStore` and stores
   resolved values as fields on the config
5. **Seeding**: During `Backend.register()`, resolved config is seeded into the
   `AnalysisManager` for access by analyses and code generators via the standard
   `Analysis.get()` API
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from difflib import get_close_matches
from typing import TYPE_CHECKING, ClassVar, TypeVar, cast

from typing_extensions import Self

from taihe.utils.exceptions import AdhocError

if TYPE_CHECKING:
    from taihe.utils.diagnostics import DiagnosticsManager


@dataclass
class AbstractConfigOption(ABC):
    """Base class for all backend-specific configuration options.

    Subclasses should define:
    - NAME: The option name as it appears on command line
    - parse(): Class method to construct an instance from raw value
    """

    NAME: ClassVar[str]
    """The option name (without -C prefix) as it appears on command line."""

    @classmethod
    @abstractmethod
    def parse(cls, value: str | None, dm: "DiagnosticsManager") -> Self | None:
        """Parse the option value from command line.

        Args:
            value: The value string, or None for flag-style options
            dm: DiagnosticsManager for reporting errors during parsing

        Returns:
            A new instance of this config option
        """


ConfigOptionT = type[AbstractConfigOption]
_C = TypeVar("_C", bound=AbstractConfigOption)


class OptionStore:
    """Storage for parsed configuration options.

    Similar to how Decl stores attributes, OptionStore uses a multimap
    (dict[type[AbstractConfigOption], list[AbstractConfigOption]]) to allow the same
    option to appear multiple times if needed.
    """

    def __init__(self) -> None:
        self._options: dict[ConfigOptionT, list[AbstractConfigOption]] = {}

    def add(self, option: AbstractConfigOption) -> None:
        """Add a parsed config option to the store."""
        self._options.setdefault(type(option), []).append(option)

    def get(self, option_type: type[_C]) -> _C | None:
        """Get a single config option by type.

        Returns the first option of the given type, or None if not present.
        Use this for options that should appear at most once.
        """
        options = self._options.get(option_type)
        if options:
            return cast(_C, options[0])
        return None

    def get_all(self, option_type: type[_C]) -> list[_C]:
        """Get all config options of a given type.

        Returns a list of options, which may be empty.
        Use this for options that can appear multiple times.
        """
        return cast(list[_C], self._options.get(option_type, []))


class OptionRegistry:
    """Registry for mapping option names to their implementation classes.

    This registry is used during the parsing phase to validate and construct
    typed config options from raw command-line values.
    """

    def __init__(self) -> None:
        self._name_to_option: dict[str, ConfigOptionT] = {}

    def register(self, *option_types: ConfigOptionT) -> None:
        """Register one or more config option types.

        Args:
            *option_types: ConfigOption subclasses to register

        Raises:
            ValueError: If an option with the same name is already registered
        """
        for option_type in option_types:
            name = option_type.NAME
            if name in self._name_to_option:
                existing = self._name_to_option[name]
                raise ValueError(
                    f"config option {name!r} cannot be registered as {option_type.__name__} "
                    f"because it is already registered as {existing.__name__}"
                )
            self._name_to_option[name] = option_type

    def parse(
        self,
        name: str,
        value: str | None,
        dm: "DiagnosticsManager",
    ) -> AbstractConfigOption | None:
        """Parse raw config list into a OptionStore.

        Args:
            name: The option name from command line -C flags
            value: The option value string, or None for flag-style options
            dm: DiagnosticsManager for reporting errors during parsing

        Returns:
            A parsed ConfigOption instance

        Raises:
            ValueError: If an unknown option name is encountered
        """
        option_type = self._name_to_option.get(name)
        if option_type is None:
            suggestions = get_close_matches(name, self._name_to_option.keys())
            msg = f"unknown config option {name!r}"
            if suggestions:
                suggestions_str = ", ".join(suggestions)
                msg += f", did you mean: {suggestions_str}?"
            dm.emit(AdhocError(msg))
            return None

        return option_type.parse(value, dm)

    def parse_args(self, args: list[str], dm: "DiagnosticsManager") -> OptionStore:
        """Parse a list of raw config strings into an OptionStore.

        Args:
            args: List of config strings from command line
            dm: DiagnosticsManager for reporting errors during parsing

        Returns:
            An OptionStore containing all parsed options

        Raises:
            ValueError: If any unknown option name is encountered
        """
        store = OptionStore()
        for arg in args:
            name, *values = arg.split("=", 1)
            value = values[0] if values else None
            option = self.parse(name, value, dm)
            if option is not None:
                store.add(option)
        return store

    def get_option_names(self) -> list[str]:
        """Get all registered option names."""
        return list(self._name_to_option.keys())
