from dataclasses import dataclass
from typing import ClassVar

from taihe.driver.backend import Backend, BackendConfig
from taihe.driver.contexts import CompilerInstance


@dataclass
class NapiBridgeBackendConfig(BackendConfig):
    NAME = "napi-bridge"
    DEPS: ClassVar = ["cpp-user"]

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.napi.gen_dts import DTSCodeGenerator
        from taihe.codegen.napi.gen_napi import NAPICodeGenerator

        class NapiBridgeBackendImpl(Backend):
            def __init__(self, ci: CompilerInstance):
                super().__init__(ci)
                self._ci = ci

            def generate(self):
                oc = self._ci.output_config
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                NAPICodeGenerator(oc, am).generate(pg)
                DTSCodeGenerator(oc, am).generate(pg)

        return NapiBridgeBackendImpl(instance)
