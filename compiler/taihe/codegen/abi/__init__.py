from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from taihe.driver.backend import Backend, BackendConfig

if TYPE_CHECKING:
    from taihe.driver.contexts import CompilerInstance


@dataclass
class AbiHeaderBackendConfig(BackendConfig):
    NAME = "abi-header"

    @classmethod
    def create(cls):
        return AbiHeaderBackendConfig()

    def construct(self, instance: "CompilerInstance"):
        from taihe.codegen.abi.gen_abi import AbiHeadersGenerator

        class AbiHeaderBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance"):
                self._ci = ci

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

    @classmethod
    def create(cls):
        return AbiSourcesBackendConfig()

    def construct(self, instance: "CompilerInstance"):
        from taihe.codegen.abi.gen_abi import AbiSourcesGenerator

        class AbiSourcesBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance"):
                self._ci = ci

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                AbiSourcesGenerator(om, am).generate(pg)

        return AbiSourcesBackendImpl(instance)


@dataclass
class CAuthorBackendConfig(BackendConfig):
    NAME = "c-author"
    DEPS: ClassVar = ["abi-source"]

    @classmethod
    def create(cls):
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
