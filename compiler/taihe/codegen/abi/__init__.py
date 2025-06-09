from dataclasses import dataclass
from typing import ClassVar

from taihe.driver.backend import Backend, BackendConfig
from taihe.driver.contexts import CompilerInstance


@dataclass
class AbiHeaderBackendConfig(BackendConfig):
    NAME = "abi-header"

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.abi.gen_abi import ABIHeadersGenerator

        class ABIHeaderBackendImpl(Backend):
            def __init__(self, ci: CompilerInstance):
                super().__init__(ci)
                self._ci = ci

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                ABIHeadersGenerator(om, am).generate(pg)

        return ABIHeaderBackendImpl(instance)


@dataclass
class AbiSourcesBackendConfig(BackendConfig):
    NAME = "abi-source"
    DEPS: ClassVar = ["abi-header"]

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.abi.gen_abi import ABISourcesGenerator

        class ABISourcesBackendImpl(Backend):
            def __init__(self, ci: CompilerInstance):
                super().__init__(ci)
                self._ci = ci

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                ABISourcesGenerator(om, am).generate(pg)

        return ABISourcesBackendImpl(instance)


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
                super().__init__(ci)
                self._ci = ci

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                CImplSourcesGenerator(om, am).generate(pg)
                CImplHeadersGenerator(om, am).generate(pg)

        return CImplBackendImpl(instance)
