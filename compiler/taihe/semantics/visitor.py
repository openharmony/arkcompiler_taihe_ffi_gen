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

from typing import Generic, Optional, TypeVar

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
    IfaceParentDecl,
    ImportDecl,
    Package,
    PackageGroup,
    PackageImportDecl,
    PackageRefDecl,
    ParamDecl,
    RetvalDecl,
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

    visiting: Optional[TypeAlike] = None
    """The current node being visited. Only for debug use."""

    def handle_type(self, t: TypeAlike) -> T:
        """The entrance for visiting."""
        r = self.visiting
        self.visiting = t
        try:
            return t._accept(self)
        except:
            print(
                f"Internal error from {self.__class__.__name__} while handling {self.visiting}"
            )
            raise
        finally:
            self.visiting = r

    def visit_type(self, t: Type) -> T:
        """The fallback method which handles the most general type.

        Note that `TypeRef` is NOT a `Type`.
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

    visiting: Optional[DeclAlike] = None
    """The current node being visited. Only for debug use."""

    def handle_decl(self, d: DeclAlike) -> None:
        """The entrance for visiting anything "acceptable"."""
        r = self.visiting
        self.visiting = d
        try:
            return d._accept(self)
        except:
            print(
                f"Internal error from {self.__class__.__name__} while handling {self.visiting}"
            )
            raise
        finally:
            self.visiting = r

    def visit_decl(self, d: Decl) -> None:
        """The fallback method which handles the most general cases."""
        del d

    def visit_param_decl(self, d: ParamDecl) -> None:
        for i in d.children:
            self.handle_decl(i)
        return self.visit_decl(d)

    def visit_retval_decl(self, d: RetvalDecl) -> None:
        for i in d.children:
            self.handle_decl(i)
        return self.visit_decl(d)

    def visit_func_base_decl(self, d: FuncBaseDecl) -> None:
        for i in d.children:
            self.handle_decl(i)
        return self.visit_decl(d)

    ### Imports ###

    def visit_package_ref_decl(self, d: PackageRefDecl) -> None:
        return self.visit_decl(d)

    def visit_decl_ref_decl(self, d: DeclarationRefDecl) -> None:
        for i in d.children:
            self.handle_decl(i)
        return self.visit_decl(d)

    def visit_import_decl(self, d: ImportDecl) -> None:
        return self.visit_decl(d)

    def visit_package_import_decl(self, d: PackageImportDecl) -> None:
        for i in d.children:
            self.handle_decl(i)
        return self.visit_import_decl(d)

    def visit_decl_import_decl(self, d: DeclarationImportDecl) -> None:
        for i in d.children:
            self.handle_decl(i)
        return self.visit_import_decl(d)

    ### Functions ###

    def visit_func_decl(self, d: FuncDecl) -> None:
        return self.visit_func_base_decl(d)

    ### Type (Generic) ###

    def visit_type_decl(self, d: TypeDecl) -> None:
        return self.visit_decl(d)

    def visit_type_ref_decl(self, d: TypeRefDecl) -> None:
        return self.visit_decl(d)

    ### Struct ###

    def visit_struct_field_decl(self, d: StructFieldDecl) -> None:
        for i in d.children:
            self.handle_decl(i)
        return self.visit_decl(d)

    def visit_struct_decl(self, d: StructDecl) -> None:
        for i in d.children:
            self.handle_decl(i)
        return self.visit_type_decl(d)

    ### Enum ###

    def visit_enum_item_decl(self, d: EnumItemDecl) -> None:
        return self.visit_decl(d)

    def visit_enum_decl(self, d: EnumDecl) -> None:
        for i in d.children:
            self.handle_decl(i)
        return self.visit_type_decl(d)

    ### Interface ###

    def visit_iface_parent_decl(self, d: IfaceParentDecl) -> None:
        for i in d.children:
            self.handle_decl(i)
        return self.visit_decl(d)

    def visit_iface_method_decl(self, d: IfaceMethodDecl) -> None:
        return self.visit_func_base_decl(d)

    def visit_iface_decl(self, d: IfaceDecl) -> None:
        for i in d.children:
            self.handle_decl(i)
        return self.visit_type_decl(d)

    ### Package ###

    def visit_package(self, p: Package) -> None:
        for i in p.children:
            self.handle_decl(i)

    def visit_package_group(self, g: PackageGroup) -> None:
        for i in g.children:
            self.handle_decl(i)
