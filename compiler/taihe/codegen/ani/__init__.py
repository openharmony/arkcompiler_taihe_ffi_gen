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
from taihe.utils.resources import StandardLibrary
from taihe.utils.sources import SourceFile

if TYPE_CHECKING:
    from taihe.driver.contexts import CompilerInstance
    from taihe.driver.options import OptionRegistry, OptionStore
    from taihe.utils.diagnostics import DiagnosticsManager


@dataclass
class AniBridgeBackendConfig(BackendConfig):
    NAME = "ani-bridge"
    DEPS: ClassVar = ["cpp-user"]

    keep_name: bool = False
    module_prefix: str | None = None
    path_prefix: str | None = None

    @classmethod
    def register_options_to(cls, option_registry: "OptionRegistry"):
        from taihe.codegen.ani.options import all_ani_config_options

        option_registry.register(*all_ani_config_options)

    @classmethod
    def from_options(cls, options: "OptionStore", dm: "DiagnosticsManager"):
        from taihe.codegen.ani.options import (
            ArktsKeepNameOption,
            ArktsModulePrefixOption,
            ArktsPathPrefixOption,
        )

        keep_name_opt = options.get(ArktsKeepNameOption)
        module_prefix_opt = options.get(ArktsModulePrefixOption)
        path_prefix_opt = options.get(ArktsPathPrefixOption)
        return AniBridgeBackendConfig(
            keep_name=keep_name_opt is not None,
            module_prefix=module_prefix_opt.prefix if module_prefix_opt else None,
            path_prefix=path_prefix_opt.prefix if path_prefix_opt else None,
        )

    def build(self, instance: "CompilerInstance"):
        from taihe.codegen.ani.analyses import ArkTsOutDir
        from taihe.codegen.ani.attributes import StsKeepNameAttr, all_attr_types
        from taihe.codegen.ani.gen_ani import AniCodeGenerator
        from taihe.codegen.ani.gen_sts import StsCodeGenerator

        # TODO: unify {Ani,Sts}CodeGenerator
        class AniBridgeBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance", config: AniBridgeBackendConfig):
                self._ci = ci
                self._config = config

            def setup(self):
                self._ci.attribute_registry.register(*all_attr_types)

            def add_sources(self):
                self._ci.source_manager.add_source(
                    SourceFile(
                        StandardLibrary.resolve_path() / "taihe.platform.ani.taihe",
                        is_stdlib=True,
                    )
                )

            def post_process(self):
                ArkTsOutDir.provide(
                    self._ci.analysis_manager,
                    self._ci.package_group,
                    ArkTsOutDir(self._config.module_prefix, self._config.path_prefix),
                )
                if self._config.keep_name:
                    for p in self._ci.package_group.iterate():
                        if StsKeepNameAttr.get(p) is None:
                            p.add_attribute(StsKeepNameAttr(loc=p.loc))

            def generate(self):
                self._ci.output_manager.record_runtime_cxx_src("runtime_ani.cpp")
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                AniCodeGenerator(om, am).generate(pg)
                StsCodeGenerator(om, am).generate(pg)

        return AniBridgeBackendImpl(instance, self)
