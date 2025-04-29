from typing import TextIO

from typing_extensions import override

from taihe.utils.outputs import DEFAULT_INDENT, FileWriter, OutputManager


class StsWriter(FileWriter):
    """Represents a static type script (sts) file."""

    @override
    def __init__(self, om: OutputManager, path: str, indent_unit: str = DEFAULT_INDENT):
        super().__init__(om, path=path, indent_unit=indent_unit)
        self.import_dict: dict[str, str] = {}

    @override
    def write_prologue(self, f: TextIO):
        for import_name, module_name in self.import_dict.items():
            f.write(f'import * as {import_name} from "./{module_name}";\n')

    def import_module(self, import_name: str, module_name: str):
        self.import_dict.setdefault(import_name, module_name)
