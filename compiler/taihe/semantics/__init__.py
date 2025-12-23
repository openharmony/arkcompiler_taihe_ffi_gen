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
from typing import TYPE_CHECKING

from taihe.driver.backend import Backend, BackendConfig
from taihe.utils.outputs import DebugOutputConfig, OutputConfig

if TYPE_CHECKING:
    from taihe.driver.contexts import CompilerInstance


@dataclass
class PrettyPrintBackendConfig(BackendConfig):
    NAME = "pretty-print"

    show_resolved = True
    colorize = True

    output_config: OutputConfig = field(default_factory=DebugOutputConfig)

    @classmethod
    def create(cls):
        return PrettyPrintBackendConfig()

    def construct(self, instance: "CompilerInstance"):
        from taihe.semantics.format import TaiheGenerator

        class PrettyPrintBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance", config: BackendConfig):
                assert isinstance(config, PrettyPrintBackendConfig)
                self._ci = ci
                self._config = config
                self._om = self._config.output_config.construct()

            def generate(self):
                generator = TaiheGenerator(
                    self._om,
                    show_resolved=self._config.show_resolved,
                    colorize=self._config.colorize,
                )
                generator.generate(self._ci.package_group)

        return PrettyPrintBackendImpl(instance, self)
