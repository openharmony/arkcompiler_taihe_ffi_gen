from dataclasses import dataclass
from typing import ClassVar

from taihe.driver.backend import Backend, BackendConfig
from taihe.driver.contexts import CompilerInstance


@dataclass
class AniBridgeBackendConfig(BackendConfig):
    NAME = "ani-bridge"
    DEPS: ClassVar = ["cpp-user"]

    keep_name: bool = False
    """Use the original function name (instead of "camelCase") in exported ArkTS sources."""

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.ani.attributes import all_attr_types
        from taihe.codegen.ani.gen_ani import AniCodeGenerator
        from taihe.codegen.ani.gen_sts import StsCodeGenerator

        instance.attribute_registry.register(*all_attr_types)

        # TODO: unify {Ani,Sts}CodeGenerator
        class AniBridgeBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance"):
                super().__init__(ci)
                self._ci = ci

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                AniCodeGenerator(om, am).generate(pg)
                StsCodeGenerator(om, am).generate(pg)

        return AniBridgeBackendImpl(instance)
