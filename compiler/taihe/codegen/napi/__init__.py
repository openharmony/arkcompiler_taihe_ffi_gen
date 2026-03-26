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

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from taihe.driver.backend import Backend, BackendConfig

if TYPE_CHECKING:
    from taihe.driver.contexts import CompilerInstance
    from taihe.driver.options import OptionStore
    from taihe.utils.diagnostics import DiagnosticsManager


@dataclass
class NapiBridgeBackendConfig(BackendConfig):
    NAME = "napi-bridge"
    DEPS: ClassVar = ["cpp-user"]

    @classmethod
    def create(cls, options: "OptionStore", dm: "DiagnosticsManager"):
        return NapiBridgeBackendConfig()

    def construct(self, instance: "CompilerInstance"):
        from taihe.codegen.napi.attributes import all_napi_attr_types
        from taihe.codegen.napi.gen_dts import DtsCodeGenerator
        from taihe.codegen.napi.gen_napi import NapiCodeGenerator
        from taihe.codegen.napi.gen_ts import TsCodeGenerator

        class NapiBridgeBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance"):
                self._ci = ci

            def register(self):
                self._ci.attribute_registry.register(*all_napi_attr_types)

            def generate(self):
                self._ci.output_manager.register_runtime_cxx_src("runtime_napi.cpp")
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                NapiCodeGenerator(om, am).generate(pg)
                DtsCodeGenerator(om, am).generate(pg)
                TsCodeGenerator(om, am).generate(pg)

        return NapiBridgeBackendImpl(instance)
