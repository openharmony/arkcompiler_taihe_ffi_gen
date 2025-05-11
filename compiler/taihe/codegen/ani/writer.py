from typing import TextIO

from typing_extensions import override

from taihe.utils.outputs import DEFAULT_INDENT, FileWriter, OutputConfig


class StsWriter(FileWriter):
    """Represents a static type script (sts) file."""

    @override
    def __init__(self, oc: OutputConfig, path: str, indent_unit: str = DEFAULT_INDENT):
        super().__init__(
            oc, path=path, default_indent=indent_unit, comment_prefix="// "
        )
        self.import_dict: dict[str, str] = {}

    @override
    def write_prologue(self, f: TextIO):
        for import_name, module_name in self.import_dict.items():
            f.write(f'import * as {import_name} from "./{module_name}";\n')

    def add_import(self, import_name: str, module_name: str):
        self.import_dict.setdefault(import_name, module_name)
