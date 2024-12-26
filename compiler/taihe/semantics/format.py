"""Format the IDL files."""

from codecs import encode
from typing import Optional, TextIO

from typing_extensions import override

from taihe.semantics.declarations import (
    AttrItemDecl,
    Decl,
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    EnumItemDecl,
    FuncBaseDecl,
    IfaceDecl,
    IfaceParentDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
    PackageRefDecl,
    ParamDecl,
    RetvalDecl,
    StructDecl,
    StructFieldDecl,
    TypeAliasDecl,
    TypeDecl,
    TypeRefDecl,
)
from taihe.semantics.types import (
    BuiltinType,
    Type,
)
from taihe.semantics.visitor import DeclVisitor, TypeVisitor
from taihe.utils.diagnostics import AnsiStyle


def pretty_print(x: Decl, buffer: TextIO):
    printer = _PrettyPrinter(buffer)
    printer.handle_decl(x)


class _TypeNamePrinter(TypeVisitor[str]):
    @override
    def visit_type_decl(self, d: TypeDecl):
        return f"{pkg.name}.{d.name}" if (pkg := d.parent) else d.name

    @override
    def visit_builtin_type(self, t: BuiltinType):
        return t.name


class _PrettyPrinter(DeclVisitor):
    def __init__(self, buffer: TextIO):
        self.buffer = buffer
        self.indent = 0
        self.type_name_printer = _TypeNamePrinter()

    def get_type_ref_decl(self, d: TypeRefDecl) -> str:
        if d.is_resolved:
            return f"{d.symbol} {AnsiStyle.GREEN}/* {self.get_real_type(d.resolved_ty)} */{AnsiStyle.RESET}"
        else:
            return d.symbol

    def get_type(self, t: Type) -> str:
        return self.type_name_printer.handle_type(t)

    def get_real_type(self, t: Optional[Type]) -> str:
        return "<error type>" if not t else self.get_type(t)

    def get_package_ref_decl(self, d: PackageRefDecl) -> str:
        return d.symbol

    def get_decl_ref_decl(self, d: DeclarationRefDecl) -> str:
        return d.symbol

    def get_parent_decl(self, d: IfaceParentDecl) -> str:
        res = self.get_type_ref_decl(d.ty_ref)
        return self.with_attrs(d, res)

    def get_return_decl(self, d: RetvalDecl) -> str:
        res = self.get_type_ref_decl(d.ty_ref)
        return self.with_attrs(d, res)

    def get_param_decl(self, d: ParamDecl) -> str:
        res = f"{d.name}: {self.get_type_ref_decl(d.ty_ref)}"
        return self.with_attrs(d, res)

    def get_attr_item(self, d: AttrItemDecl) -> str:
        if d.value is None:
            return d.name
        elif isinstance(d.value, bool):
            value = "TRUE" if d.value else "FALSE"
        elif isinstance(d.value, int):
            value = str(d.value)
        elif isinstance(d.value, str):
            value = '"' + encode(d.value, "unicode-escape").decode() + '"'
        else:
            raise ValueError()

        return f"{d.name} = {value}"

    def as_keyword(self, s) -> str:
        return f"{AnsiStyle.CYAN}{s}{AnsiStyle.RESET}"

    def with_attrs(self, d: Decl, s: str) -> str:
        if d.attrs:
            fmt_attrs = ", ".join(map(self.get_attr_item, d.attrs.values()))
            return f"{AnsiStyle.MAGENTA}[{fmt_attrs}]{AnsiStyle.RESET_ALL} {s}"
        else:
            return s

    def write_attrs(self, d: Decl):
        if d.attrs:
            fmt_attrs = ", ".join(map(self.get_attr_item, d.attrs.values()))
            self.buffer.write(self.indent * 2 * " ")
            self.buffer.write(
                f"{AnsiStyle.MAGENTA}[{fmt_attrs}]{AnsiStyle.RESET_ALL}\n"
            )

    @override
    def visit_package_import_decl(self, d: PackageImportDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"use {self.get_package_ref_decl(d.pkg_ref)}")
        if d.is_alias():
            self.buffer.write(f" as {d.name}")
        self.buffer.write(";\n")

    @override
    def visit_decl_import_decl(self, d: DeclarationImportDecl):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(
            f"{self.as_keyword('from')} {self.get_package_ref_decl(d.decl_ref.pkg_ref)} {self.as_keyword('use')} {self.get_decl_ref_decl(d.decl_ref)}"
        )
        if d.is_alias():
            self.buffer.write(f" {self.as_keyword('as')} {d.name}")
        self.buffer.write(";\n")

    @override
    def visit_func_base_decl(self, d: FuncBaseDecl):
        self.write_attrs(d)

        self.buffer.write(self.indent * 2 * " ")
        fmt_args = ", ".join(self.get_param_decl(x) for x in d.params)
        if len(d.retvals) == 0:
            self.buffer.write(f"{self.as_keyword('fn')} {d.name}({fmt_args});\n")
        elif len(d.retvals) == 1:
            fmt_ret = self.get_return_decl(d.retvals[0])
            self.buffer.write(
                f"{self.as_keyword('fn')} {d.name}({fmt_args}) -> {fmt_ret};\n"
            )
        else:
            fmt_ret = ", ".join(self.get_return_decl(r) for r in d.retvals)
            self.buffer.write(
                f"{self.as_keyword('fn')} {d.name}({fmt_args}) -> ({fmt_ret});\n"
            )

    @override
    def visit_struct_field_decl(self, d: StructFieldDecl):
        self.write_attrs(d)

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{d.name}: {self.get_type_ref_decl(d.ty_ref)};\n")

    @override
    def visit_enum_item_decl(self, d: EnumItemDecl):
        self.write_attrs(d)

        self.buffer.write(self.indent * 2 * " ")
        if d.value is None:
            self.buffer.write(
                f"{d.name}; {AnsiStyle.GREEN}// unknown{AnsiStyle.RESET}\n"
            )
        else:
            self.buffer.write(
                f"{d.name} = {d.value}; {AnsiStyle.GREEN}// {hex(d.value)}{AnsiStyle.RESET}\n"
            )

    @override
    def visit_enum_decl(self, d: EnumDecl):
        self.write_attrs(d)

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{self.as_keyword('enum')} {d.name} {{")
        if d.items:
            self.buffer.write("\n")
            self.indent += 1
            for i in d.items:
                self.handle_decl(i)
            self.indent -= 1
            self.buffer.write(self.indent * 2 * " ")
        self.buffer.write("}\n")

    @override
    def visit_struct_decl(self, d: StructDecl):
        self.write_attrs(d)

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{self.as_keyword('struct')} {d.name} {{")
        if d.fields:
            self.buffer.write("\n")
            self.indent += 1
            for f in d.fields:
                self.handle_decl(f)
            self.indent -= 1
            self.buffer.write(self.indent * 2 * " ")
        self.buffer.write("}\n")

    @override
    def visit_iface_decl(self, d: IfaceDecl):
        self.write_attrs(d)

        self.buffer.write(self.indent * 2 * " ")
        if d.parents:
            fmt_extends = ", ".join(self.get_parent_decl(e) for e in d.parents)
            self.buffer.write(
                f"{self.as_keyword('interface')} {d.name}: {fmt_extends} {{"
            )
        else:
            self.buffer.write(f"{self.as_keyword('interface')} {d.name} {{")
        if d.methods:
            self.buffer.write("\n")
            self.indent += 1
            for f in d.methods:
                self.handle_decl(f)
            self.indent -= 1
            self.buffer.write(self.indent * 2 * " ")
        self.buffer.write("}\n")

    @override
    def visit_type_alias_decl(self, d: TypeAliasDecl):
        self.write_attrs(d)

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(
            f"{self.as_keyword('type')} {d.name} = {self.get_type_ref_decl(d.ty_ref)}; {AnsiStyle.GREEN}// {self.get_real_type(d.final_ty)}{AnsiStyle.RESET}\n"
        )

    @override
    def visit_package(self, p: Package):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"// {self.with_attrs(p, p.name)}\n")
        for d in p.pkg_imports:
            self.handle_decl(d)
        for d in p.decl_imports:
            self.handle_decl(d)
        for d in p.type_aliases:
            self.handle_decl(d)
        for d in p.structs:
            self.handle_decl(d)
        for d in p.enums:
            self.handle_decl(d)
        for d in p.interfaces:
            self.handle_decl(d)
        for d in p.functions:
            self.handle_decl(d)

    @override
    def visit_package_group(self, g: PackageGroup):
        for i, p in enumerate(g.packages):
            if i != 0:
                self.buffer.write("\n")
            self.handle_decl(p)
