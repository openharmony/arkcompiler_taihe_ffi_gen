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

from typing import Any, Generic, Optional, TypeVar

from taihe.semantics.declarations import (
    Decl,
    DeclAlike,
    DeclarationImportDecl,
    DeclarationRefDecl,
    EnumDecl,
    EnumItemDecl,
    FuncBaseDecl,
    FuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    ImportDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
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

T = TypeVar("T")


class TypeVisitor(Generic[T]):
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

    visiting: Optional[TypeAlike]
    """The current node being visited. Only for debug use."""

    def __init__(self) -> None:
        self.visiting = None

    def handle_type(self, t: TypeAlike) -> T:
        """The entrance for visiting."""
        try:
            self.visiting = t
            return t._accept(self)
        except:
            print(f"Internal error while handling {self.visiting}")
            raise

    def visit_type(self, t: Type) -> T:
        """The fallback method which handles the most general type.

        Note that `TypeRef` and `QualifiedType` is NOT a `Type`.
        """
        raise NotImplementedError

    ### Non-`Type`s ###

    def visit_type_ref_decl(self, d: TypeRefDecl) -> T:
        assert d.ref_ty
        return self.handle_type(d.ref_ty)

    ### Built-in types ###

    def visit_builtin_type(self, t: BuiltinType) -> T:
        return self.visit_type(t)

    def visit_scalar_type(self, t: ScalarType) -> T:
        return self.visit_builtin_type(t)

    def visit_special_type(self, t: SpecialType) -> T:
        return self.visit_builtin_type(t)

    ### Declarations ###

    def visit_type_decl(self, d: TypeDecl) -> T:
        return self.visit_type(d)

    def visit_struct_decl(self, d: StructDecl) -> T:
        return self.visit_type_decl(d)

    def visit_enum_decl(self, d: EnumDecl) -> T:
        return self.visit_type_decl(d)

    def visit_iface_decl(self, d: IfaceDecl) -> T:
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
            self.visiting = d
            return d._accept(self)
        except:
            print(f"Internal error while handling {self.visiting}")
            raise

    def visit_decl(self, d: Decl) -> Any:
        """The fallback method which handles the most general cases."""
        del d

    def visit_func_base_decl(self, d: FuncBaseDecl) -> Any:
        d._traverse(self)
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
        return self.visit_func_base_decl(d)

    ### Type (Generic) ###

    def visit_type_decl(self, d: TypeDecl) -> Any:
        return self.visit_decl(d)

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

    ### Interface ###

    def visit_iface_method_decl(self, d: IfaceMethodDecl) -> Any:
        return self.visit_func_base_decl(d)

    def visit_iface_decl(self, d: IfaceDecl) -> Any:
        d._traverse(self)
        return self.visit_type_decl(d)

    ### Package ###

    def visit_package(self, p: Package) -> Any:
        p._traverse(self)

    def visit_package_group(self, g: PackageGroup) -> Any:
        g._traverse(self)
