"""Implements the classic visitor pattern for core types.

In most cases, you need to call `Visitor.handle`.

Design:
- Each visitable type implements the "_accept_{ty,decl}" method, which delegates to
    the corresponding `VisitorBase.visit_xxx` method.
- `VisitorBase.visit_xxx` implements the default logic for each type.
    1. Calls `node._traverse` to visit the "children" nodes.
    2. Calls `self.visit_super_type` to bubble up towards the base type inside the type hierarchy.
- The `VisitorBase.visit_{type,decl}` is the "root" of the type hierarchy.
"""

from typing import TYPE_CHECKING, Any

from taihe.semantics.declarations import (
    Decl,
    DeclarationImportDecl,
    EnumDecl,
    EnumItemDecl,
    FuncDecl,
    ImportDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
    ParamDecl,
    StructDecl,
    StructFieldDecl,
    TypeDecl,
    TypeRefDecl,
)
from taihe.semantics.types import (
    BuiltinType,
    QualifiedType,
    ScalarType,
    SpecialType,
    Type,
    TypeAlike,
    TypeRef,
)

if TYPE_CHECKING:
    from taihe.semantics.declarations import DeclAlike


class TypeVisitor:
    """Visits types and its base classes along the type hierarchy.

    Error prone cases:
    visit_type_ref_decl() -> visit_type_ref() -> handle_type(type_ref.ref_ty)
    visit_qualified_type() -> handle_type(qualty.inner_ty)

    Note that a TypeVisitor does not visit the declaration.
    In other words:
    TypeVisitor: visit_enum_decl() -> visit_type_decl() -> visit_type()
    DeclVisitor: visit_enum_decl() -> traverse() -> visit_enum_item_decl()
    """

    def handle_type(self, t: TypeAlike) -> Any:
        """The entrance for visiting."""
        return t._accept(self)

    def visit_type(self, t: Type) -> Any:
        """The fallback method which handles the most general type.

        Note that `TypeRef` and `QualifiedType` is NOT a `Type`.
        """
        del t

    ### Non-`Type`s ###

    def visit_type_ref(self, t: TypeRef) -> Any:
        if t.ref_ty:
            return self.handle_type(t.ref_ty)

    def visit_qualified_type(self, t: QualifiedType) -> Any:
        return self.handle_type(t.inner_ty)

    ### Built-in types ###

    def visit_builtin_type(self, t: BuiltinType) -> Any:
        return self.visit_type(t)

    def visit_scalar_type(self, t: ScalarType) -> Any:
        return self.visit_builtin_type(t)

    def visit_special_type(self, t: SpecialType) -> Any:
        return self.visit_builtin_type(t)

    ### Declarations ###

    def visit_type_decl(self, d: TypeDecl) -> Any:
        return self.visit_type(d)

    def visit_struct_decl(self, d: StructDecl) -> Any:
        return self.visit_type_decl(d)

    def visit_enum_decl(self, d: EnumDecl) -> Any:
        return self.visit_type_decl(d)

    def visit_type_ref_decl(self, d: TypeRefDecl) -> Any:
        return self.visit_type_ref(d)


class DeclVisitor:
    def handle_decl(self, d: "DeclAlike") -> Any:
        """The entrance for visiting anything "acceptable"."""
        return d._accept(self)

    def handle_type(self, t: TypeAlike) -> Any:
        """Override this function to handle types during the visit of declarations."""
        del t

    def visit_decl(self, d: Decl) -> Any:
        """The fallback method which handles the most general cases."""
        del d

    ### Imports ###

    def visit_import_decl(self, d: ImportDecl) -> Any:
        return self.visit_decl(d)

    def visit_package_import_decl(self, d: PackageImportDecl) -> Any:
        return self.visit_import_decl(d)

    def visit_decl_import_decl(self, d: DeclarationImportDecl) -> Any:
        return self.visit_import_decl(d)

    ### Functions ###

    def visit_param_decl(self, d: ParamDecl) -> Any:
        d._traverse(self)
        return self.visit_decl(d)

    def visit_func_decl(self, d: FuncDecl) -> Any:
        d._traverse(self)
        return self.visit_decl(d)

    ### Type (Generic) ###

    def visit_type_decl(self, d: TypeDecl) -> Any:
        return self.visit_decl(d)

    def visit_type_ref_decl(self, d: TypeRefDecl) -> Any:
        d._traverse(self)
        return self.visit_decl(d)

    ### Struct ###

    def visit_struct_field_decl(self, d: StructFieldDecl) -> Any:
        d._traverse(self)
        return self.visit_decl(d)

    def visit_struct_decl(self, d: StructDecl) -> Any:
        d._traverse(self)
        return self.visit_type_decl(d)

    ### Enum ###

    def visit_enum_item_decl(self, d: EnumItemDecl) -> Any:
        return self.visit_decl(d)

    def visit_enum_decl(self, d: EnumDecl) -> Any:
        d._traverse(self)
        return self.visit_type_decl(d)

    ### Package ###

    def visit_package(self, p: Package) -> Any:
        p._traverse(self)

    def visit_package_group(self, g: PackageGroup) -> Any:
        g._traverse(self)


class RecursiveTypeVisitor(DeclVisitor, TypeVisitor):
    """Visits declarations first, optionally descent into types.

    Special case:
       DeclVisitor.visit_param_decl(param)
    -> RecursiveTypeVisitor.handle_type(param.ty)
    -> TypeVisitor.visit_qualified_type(param.ty)
    -> RecursiveTypeVisitor.handle_type(param.ty.inner_ty)
    -> TypeVisitor.visit_type_ref_decl(param.ty.inner_ty)
    -> RecursiveTypeVisitor.handle_type(param.ty.inner_ty.ref_ty)
    """

    def handle_type(self, t: TypeAlike) -> Any:
        if isinstance(t, TypeRefDecl):
            # From "Type" back to "Decl"
            return self.visit_type_ref_decl(t)
        if isinstance(t, Decl):
            return
        else:
            # Avoid infinite recursion.
            return t._accept(self)
