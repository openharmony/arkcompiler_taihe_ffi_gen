from codecs import decode
from collections.abc import Iterable

from typing_extensions import override

from taihe.parse import Visitor, ast
from taihe.parse.ast_generation import generate_ast
from taihe.semantics.declarations import (
    ArrayTypeRefDecl,
    AttrItemDecl,
    BuiltinTypeRefDecl,
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    EnumItemDecl,
    GenericTypeRefDecl,
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    IfaceParentDecl,
    Package,
    PackageImportDecl,
    PackageRefDecl,
    ParamDecl,
    StructDecl,
    StructFieldDecl,
    UserTypeRefDecl,
)
from taihe.utils.diagnostics import AbstractDiagnosticsManager
from taihe.utils.sources import SourceBase, SourceLocation


def pkg2str(pkg_name: ast.PkgName) -> str:
    if pkg_name:
        return ".".join(t.text for t in pkg_name.parts)
    else:
        return ""


class ExprEvaluator(Visitor):
    @override
    def visit_LiteralBoolExpr(self, node: ast.LiteralBoolExpr) -> bool:
        return {
            "TRUE": True,
            "FALSE": False,
        }[node.val.text]

    @override
    def visit_ComparisonBoolExpr(self, node: ast.ComparisonBoolExpr) -> bool:
        return {
            ">": int.__gt__,
            "<": int.__lt__,
            ">=": int.__ge__,
            "<=": int.__le__,
            "==": int.__eq__,
            "!=": int.__ne__,
        }[node.op.text](
            int(self.visit(node.left)),
            int(self.visit(node.right)),
        )

    @override
    def visit_UnaryBoolExpr(self, node: ast.UnaryBoolExpr) -> bool:
        assert node.op.text == "!"
        return not self.visit(node.expr)

    @override
    def visit_BinaryBoolExpr(self, node: ast.BinaryBoolExpr) -> bool:
        return {
            "&&": bool.__and__,
            "||": bool.__or__,
        }[node.op.text](
            bool(self.visit(node.left)),
            bool(self.visit(node.right)),
        )

    @override
    def visit_ParenthesisBoolExpr(self, node: ast.ParenthesisBoolExpr) -> bool:
        return self.visit(node.expr)

    @override
    def visit_ConditionalBoolExpr(self, node: ast.ConditionalBoolExpr) -> bool:
        return (
            self.visit(node.then_expr)
            if self.visit(node.cond)
            else self.visit(node.else_expr)
        )

    @override
    def visit_LiteralIntExpr(self, node: ast.LiteralIntExpr) -> int:
        text = node.val.text
        if text.startswith("0b"):
            return int(text, 2)
        if text.startswith("0o"):
            return int(text, 8)
        if text.startswith("0x"):
            return int(text, 16)
        return int(text)

    @override
    def visit_ParenthesisIntExpr(self, node: ast.ParenthesisIntExpr) -> int:
        return self.visit(node.expr)

    @override
    def visit_ConditionalIntExpr(self, node: ast.ConditionalIntExpr) -> int:
        return (
            self.visit(node.then_expr)
            if self.visit(node.cond)
            else self.visit(node.else_expr)
        )

    @override
    def visit_UnaryIntExpr(self, node: ast.UnaryIntExpr) -> int:
        return {
            "-": int.__neg__,
            "+": int.__pos__,
            "~": int.__invert__,
        }[node.op.text](
            int(self.visit(node.expr)),
        )

    @override
    def visit_BinaryIntExpr(self, node: ast.BinaryIntExpr) -> int:
        return {
            "+": int.__add__,
            "-": int.__sub__,
            "*": int.__mul__,
            "/": int.__floordiv__,
            "%": int.__mod__,
            "<<": int.__lshift__,
            ">>": int.__rshift__,
            "&": int.__and__,
            "|": int.__or__,
            "^": int.__xor__,
        }[node.op.text](
            int(self.visit(node.left)),
            int(self.visit(node.right)),
        )

    @override
    def visit_LiteralStringExpr(self, node: ast.LiteralStringExpr) -> str:
        return "".join(decode(val.text[1:-1], "unicode-escape") for val in node.vals)


class AstConverter(ExprEvaluator):
    """Converts a node on AST to the intermetiade representation.

    Note that declerations with errors are discarded.
    """

    source: SourceBase
    diag: AbstractDiagnosticsManager

    def __init__(self, source: SourceBase, diag: AbstractDiagnosticsManager):
        self.source = source
        self.diag = diag

    def loc(self, t: ast.any):
        # Remember, token.column is 0-based.
        return SourceLocation(self.source, *t._beg, *t._end)

    @override
    def visit_AttrItem(self, node: ast.AttrItem) -> AttrItemDecl:
        if val := node.val:
            d = AttrItemDecl(str(node.name), self.loc(node.name), self.visit(val.expr))
        else:
            d = AttrItemDecl(str(node.name), self.loc(node.name))
        return d

    @override
    def visit_PrimitiveType(self, node: ast.PrimitiveType) -> BuiltinTypeRefDecl:
        return BuiltinTypeRefDecl(str(node.name), self.loc(node.name))

    @override
    def visit_UserType(self, node: ast.UserType) -> UserTypeRefDecl:
        if node.pkg_name:
            loc = self.loc(node)
            name = pkg2str(node.pkg_name) + "." + str(node.decl_name)
        else:
            loc = self.loc(node.decl_name)
            name = str(node.decl_name)
        ty_ref = UserTypeRefDecl(name, loc)
        return ty_ref

    @override
    def visit_GenericType(self, node: ast.GenericType) -> GenericTypeRefDecl:
        if node.pkg_name:
            loc = self.loc(node)
            name = pkg2str(node.pkg_name) + "." + str(node.decl_name)
        else:
            loc = self.loc(node.decl_name)
            name = str(node.decl_name)
        args = [self.visit(arg) for arg in node.args]
        ty_ref = GenericTypeRefDecl(name, args, loc)
        return ty_ref

    @override
    def visit_ArrayType(self, node: ast.ArrayType) -> ArrayTypeRefDecl:
        name = str(node.name)
        const = {"CArray": True, "MArray": False}[name]
        arg_ty_ref = self.visit(node.arg)
        loc = self.loc(node)
        return ArrayTypeRefDecl(name, const, arg_ty_ref, loc)

    @override
    def visit_UsePackage(self, node: ast.UsePackage) -> Iterable[PackageImportDecl]:
        p_ref = PackageRefDecl(pkg2str(node.pkg_name), self.loc(node.pkg_name))
        if node.pkg_alias:
            d = PackageImportDecl(
                p_ref,
                name=str(node.pkg_alias),
                loc=self.loc(node.pkg_alias),
            )
        else:
            d = PackageImportDecl(
                p_ref,
            )
        yield d

    @override
    def visit_UseSymbol(self, node: ast.UseSymbol) -> Iterable[DeclarationImportDecl]:
        p_ref = PackageRefDecl(pkg2str(node.pkg_name), self.loc(node.pkg_name))
        for p in node.decl_alias_pairs:
            d_ref = DeclarationRefDecl(str(p.decl_name), self.loc(p.decl_name), p_ref)
            if p.decl_alias:
                d = DeclarationImportDecl(
                    d_ref,
                    name=str(p.decl_alias),
                    loc=self.loc(p.decl_alias),
                )
            else:
                d = DeclarationImportDecl(
                    d_ref,
                )
            yield d

    @override
    def visit_StructProperty(self, node: ast.StructProperty) -> StructFieldDecl:
        d = StructFieldDecl(str(node.name), self.loc(node.name), self.visit(node.ty))
        self.diag.for_each(node.attrs, lambda a: d.add_attr(self.visit(a)))
        return d

    @override
    def visit_Struct(self, node: ast.Struct) -> StructDecl:
        d = StructDecl(str(node.name), self.loc(node.name))
        self.diag.for_each(node.fields, lambda f: d.add_field(self.visit(f)))
        self.diag.for_each(node.attrs, lambda a: d.add_attr(self.visit(a)))
        return d

    @override
    def visit_EnumProperty(self, node: ast.EnumProperty) -> EnumItemDecl:
        d = EnumItemDecl(
            str(node.name),
            self.loc(node.name),
            ty_ref=self.visit(node.ty) if node.ty else None,
            value=self.visit(node.expr) if node.expr else None,
        )
        self.diag.for_each(node.attrs, lambda a: d.add_attr(self.visit(a)))
        return d

    @override
    def visit_Enum(self, node: ast.Enum) -> EnumDecl:
        d = EnumDecl(str(node.name), self.loc(node.name))
        self.diag.for_each(node.fields, lambda f: d.add_item(self.visit(f)))
        self.diag.for_each(node.attrs, lambda a: d.add_attr(self.visit(a)))
        return d

    @override
    def visit_Parameter(self, node: ast.Parameter) -> ParamDecl:
        d = ParamDecl(str(node.name), self.loc(node.name), self.visit(node.ty))
        self.diag.for_each(node.attrs, lambda a: d.add_attr(self.visit(a)))
        return d

    @override
    def visit_InterfaceFunction(self, node: ast.InterfaceFunction) -> IfaceMethodDecl:
        if ty := node.return_ty:
            d = IfaceMethodDecl(str(node.name), self.loc(node.name), self.visit(ty))
        else:
            d = IfaceMethodDecl(str(node.name), self.loc(node.name))
        self.diag.for_each(node.parameters, lambda p: d.add_param(self.visit(p)))
        self.diag.for_each(node.attrs, lambda a: d.add_attr(self.visit(a)))
        return d

    @override
    def visit_InterfaceParent(self, node: ast.InterfaceParent) -> IfaceParentDecl:
        p = IfaceParentDecl("", None, self.visit(node.ty))
        return p

    @override
    def visit_Interface(self, node: ast.Interface) -> IfaceDecl:
        d = IfaceDecl(str(node.name), self.loc(node.name))
        self.diag.for_each(node.fields, lambda f: d.add_method(self.visit(f)))
        self.diag.for_each(node.extends, lambda i: d.add_parent(self.visit(i)))
        self.diag.for_each(node.attrs, lambda a: d.add_attr(self.visit(a)))
        return d

    @override
    def visit_GlobalFunction(self, node: ast.GlobalFunction) -> GlobFuncDecl:
        if ty := node.return_ty:
            d = GlobFuncDecl(str(node.name), self.loc(node.name), self.visit(ty))
        else:
            d = GlobFuncDecl(str(node.name), self.loc(node.name))
        self.diag.for_each(node.parameters, lambda p: d.add_param(self.visit(p)))
        self.diag.for_each(node.attrs, lambda a: d.add_attr(self.visit(a)))
        return d

    @override
    def visit_Spec(self, node: ast.Spec) -> Package:
        pkg = Package(self.source.pkg_name, SourceLocation(self.source))
        for u in node.uses:
            self.diag.for_each(self.visit(u), pkg.add_import)
        self.diag.for_each(node.fields, lambda n: pkg.add_declaration(self.visit(n)))
        self.diag.for_each(node.attrs, lambda a: pkg.add_attr(self.visit(a)))
        return pkg

    def convert(self) -> Package:
        """Converts the whole source code buffer to a package."""
        ast = generate_ast(self.source, self.diag)

        return self.visit_Spec(ast)
