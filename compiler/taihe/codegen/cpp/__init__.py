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

        class CppCommonHeadersBackendImpl(Backend):
            def __init__(self, ci: CompilerInstance):
                super().__init__(ci)
                self._ci = ci

            def generate(self):
                oc = self._ci.output_config
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                CppHeadersGenerator(oc, am).generate(pg)

        return CppCommonHeadersBackendImpl(instance)


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
                oc = self._ci.output_config
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                CppImplSourcesGenerator(oc, am).generate(pg)
                CppImplHeadersGenerator(oc, am).generate(pg)

        return CppImplBackendImpl(instance)


@dataclass
class CppUserHeadersBackendConfig(BackendConfig):
    NAME = "cpp-user"
    DEPS: ClassVar = ["cpp-common"]

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.cpp.gen_user import CppUserHeadersGenerator

        class CppUserHeadersBackendImpl(Backend):
            def __init__(self, ci: CompilerInstance):
                super().__init__(ci)
                self._ci = ci

            def generate(self):
                oc = self._ci.output_config
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                CppUserHeadersGenerator(oc, am).generate(pg)

        return CppUserHeadersBackendImpl(instance)
