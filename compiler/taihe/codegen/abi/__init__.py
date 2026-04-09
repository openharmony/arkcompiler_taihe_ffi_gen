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
    from taihe.driver.options import OptionRegistry, OptionStore
    from taihe.utils.diagnostics import DiagnosticsManager


@dataclass
class AbiHeaderBackendConfig(BackendConfig):
    NAME = "abi-header"

    @classmethod
    def create(cls, options: "OptionStore", dm: "DiagnosticsManager"):
        return AbiHeaderBackendConfig()

    def construct(self, instance: "CompilerInstance"):
        from taihe.codegen.abi.attributes import all_attr_types
        from taihe.codegen.abi.gen_abi import AbiHeadersGenerator

        class AbiHeaderBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance"):
                self._ci = ci

            def register(self):
                self._ci.attribute_registry.register(*all_attr_types)

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                AbiHeadersGenerator(om, am).generate(pg)

        return AbiHeaderBackendImpl(instance)


@dataclass
class AbiSourcesBackendConfig(BackendConfig):
    NAME = "abi-source"
    DEPS: ClassVar = ["abi-header"]

    noexcept_all: bool = False

    @classmethod
    def register(cls, option_registry: "OptionRegistry"):
        from taihe.codegen.abi.options import all_abi_config_options

        option_registry.register(*all_abi_config_options)

    @classmethod
    def create(cls, options: "OptionStore", dm: "DiagnosticsManager"):
        from taihe.codegen.abi.options import NoexceptAllOption

        noexcept_all_opt = options.get(NoexceptAllOption)
        return AbiSourcesBackendConfig(
            noexcept_all=noexcept_all_opt is not None,
        )

    def construct(self, instance: "CompilerInstance"):
        from taihe.codegen.abi.attributes import NoexceptAttr
        from taihe.codegen.abi.gen_abi import AbiSourcesGenerator
        from taihe.semantics.declarations import CallbackTypeRefDecl

        class AbiSourcesBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance", config: AbiSourcesBackendConfig):
                self._ci = ci
                self._config = config

            def post_process(self):
                if self._config.noexcept_all:
                    self._add_noexcept_all()

            def _add_noexcept_all(self):
                """Helper method to add @noexcept to all applicable declarations."""
                from taihe.semantics.declarations import (
                    GlobFuncDecl,
                    IfaceMethodDecl,
                )
                from taihe.semantics.visitor import RecursiveDeclVisitor

                class NoexceptCallbackVisitor(RecursiveDeclVisitor):
                    """Visitor that adds @noexcept to all callback types."""

                    def __init__(self):
                        super().__init__()

                    def visit_glob_func(self, d: GlobFuncDecl) -> None:
                        """Visit global function and add @noexcept if needed."""
                        if NoexceptAttr.get(d) is None:
                            d.add_attribute(NoexceptAttr(loc=d.loc))
                        super().visit_glob_func(d)

                    def visit_iface_method(self, d: IfaceMethodDecl) -> None:
                        """Visit interface method and add @noexcept if needed."""
                        if NoexceptAttr.get(d) is None:
                            d.add_attribute(NoexceptAttr(loc=d.loc))
                        super().visit_iface_method(d)

                    def visit_callback_type_ref(self, d: CallbackTypeRefDecl) -> None:
                        """Visit callback type reference and add @noexcept."""
                        if NoexceptAttr.get(d) is None:
                            d.add_attribute(NoexceptAttr(loc=d.loc))
                        # Recurse into parameters and return type
                        super().visit_callback_type_ref(d)

                # Apply visitor to all packages
                visitor = NoexceptCallbackVisitor()
                for p in self._ci.package_group.iterate():
                    p.accept(visitor)

            def generate(self):
                self._ci.output_manager.register_runtime_cxx_src("string.cpp")
                self._ci.output_manager.register_runtime_cxx_src("object.cpp")
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                AbiSourcesGenerator(om, am).generate(pg)

        return AbiSourcesBackendImpl(instance, self)


@dataclass
class CAuthorBackendConfig(BackendConfig):
    NAME = "c-author"
    DEPS: ClassVar = ["abi-source"]

    @classmethod
    def create(cls, options: "OptionStore", dm: "DiagnosticsManager"):
        return CAuthorBackendConfig()

    def construct(self, instance: "CompilerInstance"):
        from taihe.codegen.abi.gen_impl import (
            CImplHeadersGenerator,
            CImplSourcesGenerator,
        )

        # TODO: unify CImpl{Headers,Sources}Generator
        class CImplBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance"):
                self._ci = ci

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                CImplSourcesGenerator(om, am).generate(pg)
                CImplHeadersGenerator(om, am).generate(pg)

        return CImplBackendImpl(instance)
