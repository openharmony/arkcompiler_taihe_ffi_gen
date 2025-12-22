from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from taihe.driver.backend import Backend, BackendConfig

if TYPE_CHECKING:
    from taihe.driver.contexts import CompilerInstance


@dataclass
class CppCommonHeadersBackendConfig(BackendConfig):
    NAME = "cpp-common"
    DEPS: ClassVar = ["abi-header"]

    @classmethod
    def create(cls):
        return CppCommonHeadersBackendConfig()

    def construct(self, instance: "CompilerInstance"):
        from taihe.codegen.cpp.gen_common import CppHeadersGenerator

        class CppCommonHeadersBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance"):
                self._ci = ci

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                CppHeadersGenerator(om, am).generate(pg)

        return CppCommonHeadersBackendImpl(instance)


@dataclass
class CppAuthorBackendConfig(BackendConfig):
    NAME = "cpp-author"
    DEPS: ClassVar = ["cpp-common", "abi-source"]

    @classmethod
    def create(cls):
        return CppAuthorBackendConfig()

    def construct(self, instance: "CompilerInstance"):
        from taihe.codegen.cpp.gen_impl import (
            CppImplHeadersGenerator,
            CppImplSourcesGenerator,
        )

        # TODO: unify CppImpl{Headers,Sources}Generator
        class CppImplBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance"):
                self._ci = ci

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                CppImplSourcesGenerator(om, am).generate(pg)
                CppImplHeadersGenerator(om, am).generate(pg)

        return CppImplBackendImpl(instance)


@dataclass
class CppUserHeadersBackendConfig(BackendConfig):
    NAME = "cpp-user"
    DEPS: ClassVar = ["cpp-common"]

    @classmethod
    def create(cls):
        return CppUserHeadersBackendConfig()

    def construct(self, instance: "CompilerInstance"):
        from taihe.codegen.cpp.gen_user import CppUserHeadersGenerator

        class CppUserHeadersBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance"):
                self._ci = ci

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                CppUserHeadersGenerator(om, am).generate(pg)

        return CppUserHeadersBackendImpl(instance)
