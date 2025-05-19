from typing import TextIO

from typing_extensions import override

from taihe.utils.outputs import DEFAULT_INDENT, FileWriter, OutputConfig


class StsWriter(FileWriter):
    """Represents a static type script (sts) file."""

    @override
    def __init__(self, oc: OutputConfig, path: str, indent_unit: str = DEFAULT_INDENT):
        super().__init__(
            oc,
            path=path,
            default_indent=indent_unit,
            comment_prefix="// ",
        )
        self.import_dict: dict[str, tuple[str, str | None]] = {}

    @override
    def write_prologue(self, f: TextIO):
        for import_name, module_name in self.import_dict.items():
            module_name, type_name = module_name
            if type_name is None:
                import_str = f"* as {import_name}"
            elif type_name == import_name:
                import_str = f"{{{type_name}}}"
            else:
                import_str = f"{{{type_name} as {import_name}}}"
            f.write(f"import {import_str} from '{module_name}';\n")

    def _add_import(
        self,
        module_name: str,
        new_pair: tuple[str, str | None],
    ):
        if (old_pair := self.import_dict.setdefault(module_name, new_pair)) != new_pair:
            raise ValueError(
                f"Duplicate import for {module_name!r}: {old_pair} vs {new_pair}"
            )

    def add_import_module(
        self,
        module_name: str,
        import_name: str,
    ):
        self._add_import(import_name, (module_name, None))

    def add_import_type(
        self,
        module_name: str,
        type_name: str,
        import_name: str | None = None,
    ):
        if import_name is None:
            import_name = type_name
        self._add_import(import_name, (module_name, type_name))
