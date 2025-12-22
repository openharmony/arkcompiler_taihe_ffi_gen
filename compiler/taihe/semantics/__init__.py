from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from taihe.driver.backend import Backend, BackendConfig
from taihe.utils.outputs import DebugOutputConfig, OutputConfig

if TYPE_CHECKING:
    from taihe.driver.contexts import CompilerInstance


@dataclass
class PrettyPrintBackendConfig(BackendConfig):
    NAME = "pretty-print"

    show_resolved = True
    colorize = True

    output_config: OutputConfig = field(default_factory=DebugOutputConfig)

    @classmethod
    def create(cls):
        return PrettyPrintBackendConfig()

    def construct(self, instance: "CompilerInstance"):
        from taihe.semantics.format import TaiheGenerator

        class PrettyPrintBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance", config: BackendConfig):
                assert isinstance(config, PrettyPrintBackendConfig)
                self._ci = ci
                self._config = config
                self._om = self._config.output_config.construct()

            def generate(self):
                generator = TaiheGenerator(
                    self._om,
                    show_resolved=self._config.show_resolved,
                    colorize=self._config.colorize,
                )
                generator.generate(self._ci.package_group)

        return PrettyPrintBackendImpl(instance, self)
