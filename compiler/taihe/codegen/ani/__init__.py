from dataclasses import dataclass
from typing import ClassVar

from taihe.driver.backend import Backend, BackendConfig
from taihe.driver.contexts import CompilerInstance


@dataclass
class AniBridgeBackendConfig(BackendConfig):
    NAME = "ani-bridge"
    DEPS: ClassVar = ["cpp-user"]

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.ani.gen_ani import ANICodeGenerator
        from taihe.codegen.ani.gen_sts import STSCodeGenerator

        # TODO: unify {ANI,STS}CodeGenerator
        class AniBridgeBackendImpl(Backend):
            def __init__(self, ci: CompilerInstance):
                super().__init__(ci)
                self._ci = ci

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                ANICodeGenerator(om, am).generate(pg)
                STSCodeGenerator(om, am).generate(pg)

        return AniBridgeBackendImpl(instance)
