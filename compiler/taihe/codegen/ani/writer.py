from typing import TextIO

from typing_extensions import override

from taihe.utils.outputs import DEFAULT_INDENT, FileKind, FileWriter, OutputManager


class StsWriter(FileWriter):
    """Represents a static type script (sts) file."""

    @override
    def __init__(
        self,
        om: OutputManager,
        path: str,
        file_kind: FileKind,
        indent_unit: str = DEFAULT_INDENT,
    ):
        super().__init__(
            om,
            path=path,
            file_kind=file_kind,
            default_indent=indent_unit,
            comment_prefix="// ",
        )
        self.import_dict: dict[str, tuple[str, str | None]] = {}

    @override
    def write_prologue(self, f: TextIO):
        for import_name, decl_pair in self.import_dict.items():
            module_name, decl_name = decl_pair
            if decl_name is None:
                import_str = f"* as {import_name}"
            elif decl_name == "default":
                import_str = import_name
            elif decl_name == import_name:
                import_str = f"{{{decl_name}}}"
            else:
                import_str = f"{{{decl_name} as {import_name}}}"
            f.write(f"import {import_str} from '{module_name}';\n")

    def add_import_module(
        self,
        module_name: str,
        import_name: str,
    ):
        self._add_import(import_name, (module_name, None))

    def add_import_default(
        self,
        module_name: str,
        import_name: str,
    ):
        self._add_import(import_name, (module_name, "default"))

    def add_import_decl(
        self,
        module_name: str,
        decl_name: str,
        import_name: str | None = None,
    ):
        if import_name is None:
            import_name = decl_name
        self._add_import(import_name, (module_name, decl_name))

    def _add_import(
        self,
        import_name: str,
        new_pair: tuple[str, str | None],
    ):
        import_dict = self.import_dict
        old_pair = import_dict.setdefault(import_name, new_pair)
        if old_pair != new_pair:
            raise ValueError(
                f"Duplicate import for {import_name!r}: {old_pair} vs {new_pair}"
            )
