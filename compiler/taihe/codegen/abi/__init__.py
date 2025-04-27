from dataclasses import dataclass
from typing import ClassVar

from taihe.driver.backend import Backend, BackendConfig
from taihe.driver.contexts import CompilerInstance


@dataclass
class AbiHeaderBackendConfig(BackendConfig):
    NAME = "abi-header"

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.abi.gen_abi import ABIHeadersGenerator

        return ABIHeadersGenerator(instance)


@dataclass
class AbiSourcesBackendConfig(BackendConfig):
    NAME = "abi-source"
    DEPS: ClassVar = ["abi-header"]

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.abi.gen_abi import ABISourcesGenerator

        return ABISourcesGenerator(instance)


@dataclass
class CAuthorBackendConfig(BackendConfig):
    NAME = "c-author"
    DEPS: ClassVar = ["abi-source"]

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.abi.gen_impl import (
            CImplHeadersGenerator,
            CImplSourcesGenerator,
        )

        # TODO: unify CImpl{Headers,Sources}Generator
        class CImplBackendImpl(Backend):
            def __init__(self, ci: CompilerInstance):
                self._ci = ci

            def generate(self):
                tm = self._ci.target_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                CImplSourcesGenerator(tm, am).generate(pg)
                CImplHeadersGenerator(tm, am).generate(pg)

        return CImplBackendImpl(instance)
