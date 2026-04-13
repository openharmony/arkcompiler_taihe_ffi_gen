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

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from taihe.driver.backend import Backend, BackendConfig
from taihe.driver.options import AbstractConfigOption, OptionRegistry
from taihe.utils.exceptions import AdhocError
from taihe.utils.outputs import DebugOutputConfig

if TYPE_CHECKING:
    from taihe.driver.contexts import CompilerInstance
    from taihe.driver.options import OptionStore
    from taihe.utils.diagnostics import DiagnosticsManager


@dataclass
class DebugOutputTargetOption(AbstractConfigOption):
    """Specify the output target for pretty-print backend."""

    NAME = "debug:output-target"

    target_desc: Literal["stderr", "stdout"]

    @classmethod
    def try_parse(cls, value: str | None, dm: "DiagnosticsManager"):
        if value is None:
            dm.emit(AdhocError("debug:output-target requires a value"))
            return None
        if value not in ("stderr", "stdout"):
            dm.emit(AdhocError(f"invalid value for debug:output-target"))
            return None
        return cls(value)


@dataclass
class DebugShowInternalOption(AbstractConfigOption):
    """Specify whether to show standard library files in pretty-print backend."""

    NAME = "debug:show-internal"

    @classmethod
    def try_parse(cls, value: str | None, dm: "DiagnosticsManager"):
        return cls()


@dataclass
class DebugShowResolvedOption(AbstractConfigOption):
    """Specify whether to show resolved types in pretty-print backend."""

    NAME = "debug:show-resolved"

    @classmethod
    def try_parse(cls, value: str | None, dm: "DiagnosticsManager"):
        return cls()


@dataclass
class PrettyPrintBackendConfig(BackendConfig):
    NAME = "pretty-print"

    show_resolved: bool = field(kw_only=True, default=False)
    show_internal: bool = field(kw_only=True, default=False)
    target_desc: Literal["stderr", "stdout"] | None = field(kw_only=True, default=None)

    @classmethod
    def register_options_to(cls, option_registry: OptionRegistry):
        option_registry.register(DebugOutputTargetOption)
        option_registry.register(DebugShowResolvedOption)
        option_registry.register(DebugShowInternalOption)

    @classmethod
    def from_options(cls, options: "OptionStore", dm: "DiagnosticsManager"):
        output_target_opt = options.get(DebugOutputTargetOption)
        show_resolved_opt = options.get(DebugShowResolvedOption)
        show_internal_opt = options.get(DebugShowInternalOption)
        return PrettyPrintBackendConfig(
            target_desc=output_target_opt.target_desc if output_target_opt else None,
            show_resolved=show_resolved_opt is not None,
            show_internal=show_internal_opt is not None,
        )

    def build(self, instance: "CompilerInstance"):
        from taihe.semantics.format import TaiheGenerator

        class PrettyPrintBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance", config: BackendConfig):
                assert isinstance(config, PrettyPrintBackendConfig)
                self._ci = ci
                self._config = config
                if config.target_desc is None:
                    self._om = ci.output_manager
                else:
                    self._om = DebugOutputConfig(config.target_desc).build()

            def generate(self):
                generator = TaiheGenerator(
                    self._om,
                    show_resolved=self._config.show_resolved,
                    show_internal=self._config.show_internal,
                )
                generator.generate(self._ci.package_group)

        return PrettyPrintBackendImpl(instance, self)
