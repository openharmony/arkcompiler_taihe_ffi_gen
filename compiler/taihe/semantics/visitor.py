"""Implements the classic visitor pattern for core types.

In most cases, you need to call `Visitor.handle_{type,decl}`.

Design:
- Each visitable type implements the "_accept" method, which delegates to the
    corresponding `VisitorBase.visit_xxx` method.
- `VisitorBase.visit_xxx` implements the default logic for each type.
    1. Calls `node._traverse` to visit the "children" nodes for declarations.
    2. Calls `self.visit_super_type` to bubble up towards the base type inside
    the type hierarchy.
- The `VisitorBase.visit_{type,decl}` is the "root" of the type hierarchy.
"""

from typing import Any

from taihe.semantics.declarations import (
    Decl,
    DeclAlike,
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    EnumItemDecl,
    FuncDecl,
    ImportDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
    PackageLevelDecl,
    PackageRefDecl,
    ParamDecl,
    StructDecl,
    StructFieldDecl,
    TypeDecl,
    TypeRefDecl,
)
from taihe.semantics.types import (
    BuiltinType,
    ScalarType,
    SpecialType,
    Type,
    TypeAlike,
)


class TypeVisitor:
    """Visits types along the type hierarchy.

    `TypeVisitor` traverses the type hierarchy in a linear fashion, visiting
    each type and its base types. It does NOT recursively visit the
    declarations within a type (e.g., enum items, record fields).

    Contrast with `DeclVisitor`:
    - **`TypeVisitor`**: Focuses on the type hierarchy.
        - Example: `visit_enum_decl()` -> `visit_type_decl()` -> `visit_type()`
    - **`DeclVisitor`**: Traverses the declaration tree.
        - Example: `visit_enum_decl()` -> `EnumDecl._traverse()` -> `visit_enum_item_decl()`
    """

    visiting: Any
    """The current node being visited. Only for debug use."""

    def __init__(self) -> None:
        self.visiting = None

    def handle_type(self, t: TypeAlike) -> Any:
        """The entrance for visiting."""
        try:
            return t._accept(self)
        except:
            print(f"Internal error while handling {self.visiting}")
            raise

    def visit_type(self, t: Type) -> Any:
        """The fallback method which handles the most general type.

        Note that `TypeRef` and `QualifiedType` is NOT a `Type`.
        """
        del t

    ### Non-`Type`s ###

    def visit_type_ref_decl(self, d: TypeRefDecl) -> Any:
        if d.ref_ty:
            return self.handle_type(d.ref_ty)

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


class DeclVisitor:
    """Traverses a declaration and its child declarations, also traversing the type hierarchy.

    `DeclVisitor` explores the declaration tree, visiting each declaration and
    its children, while also ascending the type hierarchy.

    See the documentation of `TypeVisitor` for comparison.
    """

    visiting: Any
    """The current node being visited. Only for debug use."""

    def __init__(self) -> None:
        self.visiting = None

    def handle_decl(self, d: DeclAlike) -> Any:
        """The entrance for visiting anything "acceptable"."""
        try:
            return d._accept(self)
        except:
            print(f"Internal error while handling {self.visiting}")
            raise

    def visit_decl(self, d: Decl) -> Any:
        """The fallback method which handles the most general cases."""
        del d

    def visit_package_level_decl(self, d: PackageLevelDecl) -> Any:
        return self.visit_decl(d)

    ### Imports ###

    def visit_package_ref_decl(self, d: PackageRefDecl) -> Any:
        return self.visit_decl(d)

    def visit_decl_ref_decl(self, d: DeclarationRefDecl) -> Any:
        d._traverse(self)
        return self.visit_decl(d)

    def visit_import_decl(self, d: ImportDecl) -> Any:
        return self.visit_decl(d)

    def visit_package_import_decl(self, d: PackageImportDecl) -> Any:
        d._traverse(self)
        return self.visit_import_decl(d)

    def visit_decl_import_decl(self, d: DeclarationImportDecl) -> Any:
        d._traverse(self)
        return self.visit_import_decl(d)

    ### Functions ###

    def visit_param_decl(self, d: ParamDecl) -> Any:
        d._traverse(self)
        return self.visit_decl(d)

    def visit_func_decl(self, d: FuncDecl) -> Any:
        d._traverse(self)
        return self.visit_package_level_decl(d)

    ### Type (Generic) ###

    def visit_type_decl(self, d: TypeDecl) -> Any:
        return self.visit_package_level_decl(d)

    def visit_type_ref_decl(self, d: TypeRefDecl) -> Any:
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


# class RecursiveTypeVisitor(DeclVisitor, TypeVisitor):
#     """Visits declarations and the types referenced by the declarations.

#     `RecursiveTypeVisitor` combines the behavior of both `DeclVisitor` and
#     `TypeVisitor`. It traverses the declaration tree, visiting each
#     declaration, and then, for each type referenced within a declaration, it
#     descends into the type hierarchy. However, it does not recursively visit
#     the child types of type declarations (e.g., the fields of a struct).

#     **Example:**

#     DeclVisitor.visit_param_decl(param)
#     -> RecursiveTypeVisitor.handle_type(param.ty)
#     -> DeclVisitor.visit_type_ref_decl(param.ty)
#     -> RecursiveTypeVisitor.handle_type(param.ty.ref_ty)
#     -> return (assuming that param.ty.ref_ty is a StructDecl)
#     """

#     def handle_type(self, t: TypeAlike) -> Any:
#         if isinstance(t, TypeDecl):
#             return DeclVisitor.handle_type(self, t)
#         else:
#             return TypeVisitor.handle_type(self, t)
