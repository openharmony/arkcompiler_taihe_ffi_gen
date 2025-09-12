from dataclasses import dataclass
from typing import ClassVar

from taihe.driver.backend import Backend, BackendConfig
from taihe.driver.contexts import CompilerInstance


@dataclass
class NapiBridgeBackendConfig(BackendConfig):
    NAME = "napi-bridge"
    DEPS: ClassVar = ["cpp-user"]

    def construct(self, instance: CompilerInstance) -> Backend:
        from taihe.codegen.ani.attributes import all_attr_types
        from taihe.codegen.napi.attributes import all_napi_attr_types
        from taihe.codegen.napi.gen_dts import DtsCodeGenerator
        from taihe.codegen.napi.gen_napi import NapiCodeGenerator
        from taihe.codegen.napi.gen_ts import TsCodeGenerator

        instance.attribute_registry.register(*all_attr_types)
        instance.attribute_registry.register(*all_napi_attr_types)

        class NapiBridgeBackendImpl(Backend):
            def __init__(self, ci: CompilerInstance):
                super().__init__(ci)
                self._ci = ci

            def generate(self):
                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                NapiCodeGenerator(om, am).generate(pg)
                DtsCodeGenerator(om, am).generate(pg)
                TsCodeGenerator(om, am).generate(pg)

        return NapiBridgeBackendImpl(instance)
