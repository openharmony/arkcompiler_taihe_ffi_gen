"""Format the IDL files."""

from codecs import encode
from typing import TextIO

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
    StructDecl,
    StructFieldDecl,
    TypeAliasDecl,
    TypeDecl,
    TypeRefDecl,
)
from taihe.semantics.types import (
    BuiltinType,
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
        real_type = (
            "<error type>"
            if not d.resolved_ty
            else self.type_name_printer.handle_type(d.resolved_ty)
        )
        return (
            f"{d.symbol} {AnsiStyle.GREEN}/* {real_type} */{AnsiStyle.RESET}"
            if d.is_resolved
            else d.symbol
        )

    def get_package_ref_decl(self, d: PackageRefDecl) -> str:
        return d.symbol

    def get_decl_ref_decl(self, d: DeclarationRefDecl) -> str:
        return d.symbol

    def get_parent_decl(self, d: IfaceParentDecl) -> str:
        res = self.get_type_ref_decl(d.ty_ref)
        return self.with_attr(d, res)

    def get_param_decl(self, d: ParamDecl) -> str:
        res = f"{d.name}: {self.get_type_ref_decl(d.ty_ref)}"
        return self.with_attr(d, res)

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

    def with_attr(self, d: Decl, s: str) -> str:
        if d.attrs:
            fmt_attrs = ", ".join(map(self.get_attr_item, d.attrs.values()))
            attr = f"{AnsiStyle.MAGENTA}[{fmt_attrs}]{AnsiStyle.RESET_ALL}"
            return f"{attr} {s}"
        else:
            return s

    def write_attr(self, d: Decl):
        if d.attrs:
            fmt_attrs = ", ".join(map(self.get_attr_item, d.attrs.values()))
            attr = f"{AnsiStyle.MAGENTA}[{fmt_attrs}]{AnsiStyle.RESET_ALL}"
            self.buffer.write(self.indent * 2 * " ")
            self.buffer.write(f"{attr}\n")

    @override
    def visit_package_import_decl(self, d: PackageImportDecl):
        self.write_attr(d)

        use_kw = self.as_keyword("use")
        as_kw = self.as_keyword("as")

        as_ = f" {as_kw} {d.name}" if d.is_alias() else ""

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{use_kw} {self.get_package_ref_decl(d.pkg_ref)}{as_};\n")

    @override
    def visit_decl_import_decl(self, d: DeclarationImportDecl):
        self.write_attr(d)

        from_kw = self.as_keyword("from")
        use_kw = self.as_keyword("use")
        as_kw = self.as_keyword("as")

        as_ = f" {as_kw} {d.name}" if d.is_alias() else ""

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(
            f"{from_kw} {self.get_package_ref_decl(d.decl_ref.pkg_ref)} {use_kw} {self.get_decl_ref_decl(d.decl_ref)}{as_};\n"
        )

    @override
    def visit_func_base_decl(self, d: FuncBaseDecl):
        self.write_attr(d)

        func_kw = self.as_keyword("fn")

        fmt_args = ", ".join(self.get_param_decl(x) for x in d.params)
        ret = f"-> {self.get_type_ref_decl(d.return_ty_ref)}" if d.return_ty_ref else ""

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{func_kw} {d.name}({fmt_args}){ret};\n")

    @override
    def visit_struct_field_decl(self, d: StructFieldDecl):
        self.write_attr(d)

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{d.name}: {self.get_type_ref_decl(d.ty_ref)};\n")

    @override
    def visit_enum_item_decl(self, d: EnumItemDecl):
        self.write_attr(d)

        ty_name = f": {self.get_type_ref_decl(d.ty_ref)}" if d.ty_ref else ""
        value = "unknown" if d.value is None else str(d.value)
        comment = (
            ""
            if d.value is None
            else f" {AnsiStyle.GREEN}// {hex(d.value)}{AnsiStyle.RESET}"
        )

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{d.name}{ty_name} = {value};{comment}\n")

    @override
    def visit_enum_decl(self, d: EnumDecl):
        self.write_attr(d)

        enum_kw = self.as_keyword("enum")

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{enum_kw} {d.name} {{")
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
        self.write_attr(d)

        struct_kw = self.as_keyword("struct")

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{struct_kw} {d.name} {{")
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
        self.write_attr(d)

        iface_kw = self.as_keyword("interface")

        extends = (
            ": " + ", ".join(self.get_parent_decl(e) for e in d.parents)
            if d.parents
            else ""
        )

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{iface_kw} {d.name}{extends} {{")
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
        self.write_attr(d)

        type_kw = self.as_keyword("type")

        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"{type_kw} {d.name} = {self.get_type_ref_decl(d.ty_ref)};\n")

    @override
    def visit_package(self, p: Package):
        self.buffer.write(self.indent * 2 * " ")
        self.buffer.write(f"// {self.with_attr(p, p.name)}\n")
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
