from dataclasses import dataclass
from typing import ClassVar

from taihe.driver.backend import Backend, BackendConfig
from taihe.driver.contexts import CompilerInstance


@dataclass
class CppCommonHeadersBackendConfig(BackendConfig):
    NAME = "cpp-common"
    DEPS: ClassVar = ["abi-header"]

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.cpp.gen_common import CppHeadersGenerator

        return CppHeadersGenerator(instance)


@dataclass
class CppAuthorBackendConfig(BackendConfig):
    NAME = "cpp-author"
    DEPS: ClassVar = ["cpp-common", "abi-source"]

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.cpp.gen_impl import (
            CppImplHeadersGenerator,
            CppImplSourcesGenerator,
        )

        # TODO: unify CppImpl{Headers,Sources}Generator
        class CppImplBackendImpl(Backend):
            def __init__(self, ci: CompilerInstance):
                super().__init__(ci)
                self._ci = ci

            def generate(self):
                tm = self._ci.target_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                CppImplSourcesGenerator(tm, am).generate(pg)
                CppImplHeadersGenerator(tm, am).generate(pg)

        return CppImplBackendImpl(instance)


@dataclass
class CppUserHeadersBackendConfig(BackendConfig):
    NAME = "cpp-user"
    DEPS: ClassVar = ["cpp-common"]

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.cpp.gen_user import CppUserHeadersGenerator

        return CppUserHeadersGenerator(instance)
