from dataclasses import dataclass
from typing import ClassVar

from taihe.driver.backend import Backend, BackendConfig
from taihe.driver.contexts import CompilerInstance
from taihe.utils.resources import StandardLibrary
from taihe.utils.sources import SourceFile


@dataclass
class AniBridgeBackendConfig(BackendConfig):
    NAME = "ani-bridge"
    DEPS: ClassVar = ["cpp-user"]

    keep_name: bool = False
    """Use the original function name (instead of "camelCase") in exported ArkTS sources."""

    @classmethod
    def create(cls):
        return AniBridgeBackendConfig()

    def construct(self, instance: CompilerInstance):
        from taihe.codegen.ani.attributes import all_attr_types
        from taihe.codegen.ani.gen_ani import AniCodeGenerator
        from taihe.codegen.ani.gen_sts import StsCodeGenerator

        # TODO: unify {Ani,Sts}CodeGenerator
        class AniBridgeBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance"):
                self._ci = ci

            def register(self):
                self._ci.attribute_registry.register(*all_attr_types)

            def inject(self):
                self._ci.source_manager.add_source(
                    SourceFile(
                        StandardLibrary.resolve_path() / "taihe.platform.ani.taihe",
                        is_stdlib=True,
                    )
                )

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                AniCodeGenerator(om, am).generate(pg)
                StsCodeGenerator(om, am).generate(pg)

        return AniBridgeBackendImpl(instance)
