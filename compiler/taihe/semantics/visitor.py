"""Implements the classic visitor pattern for core types.

In most cases, you need to call `node.accept(visitor)` to visit a node.
"""

from typing import TYPE_CHECKING, Generic, TypeVar

from typing_extensions import override

if TYPE_CHECKING:
    from taihe.semantics.declarations import (
        Decl,
        DeclarationImportDecl,
        DeclarationRefDecl,
        EnumItemDecl,
        ExplicitTypeRefDecl,
        GenericTypeRefDecl,
        GlobFuncDecl,
        IfaceExtendDecl,
        IfaceMethodDecl,
        ImplicitTypeRefDecl,
        ImportDecl,
        LongTypeRefDecl,
        PackageDecl,
        PackageGroup,
        PackageImportDecl,
        PackageLevelDecl,
        PackageRefDecl,
        ParamDecl,
        ShortTypeRefDecl,
        StructFieldDecl,
        UnionFieldDecl,
    )
    from taihe.semantics.types import (
        ArrayType,
        CallbackType,
        CallbackTypeRefDecl,
        EnumDecl,
        EnumType,
        GenericArgDecl,
        GenericType,
        IfaceDecl,
        IfaceType,
        LiteralType,
        MapType,
        NonVoidType,
        OpaqueType,
        OptionalType,
        ScalarType,
        SetType,
        StringType,
        StructDecl,
        StructType,
        Type,
        TypeDecl,
        TypeRefDecl,
        UnionDecl,
        UnionType,
        UserType,
        VectorType,
        VoidType,
    )


R = TypeVar("R")


class ScalarTypeVisitor(Generic[R]):
    def visit_scalar_type(self, t: "ScalarType") -> R:
        raise NotImplementedError


class StringTypeVisitor(Generic[R]):
    def visit_string_type(self, t: "StringType") -> R:
        raise NotImplementedError


class LiteralTypeVisitor(
    Generic[R],
    ScalarTypeVisitor[R],
    StringTypeVisitor[R],
):
    def visit_literal_type(self, t: "LiteralType") -> R:
        raise NotImplementedError

    @override
    def visit_scalar_type(self, t: "ScalarType") -> R:
        return self.visit_literal_type(t)

    @override
    def visit_string_type(self, t: "StringType") -> R:
        return self.visit_literal_type(t)


class OpaqueTypeVisitor(Generic[R]):
    def visit_opaque_type(self, t: "OpaqueType") -> R:
        raise NotImplementedError


class OptionalTypeVisitor(Generic[R]):
    def visit_optional_type(self, t: "OptionalType") -> R:
        raise NotImplementedError


class ArrayTypeVisitor(Generic[R]):
    def visit_array_type(self, t: "ArrayType") -> R:
        raise NotImplementedError


class VectorTypeVisitor(Generic[R]):
    def visit_vector_type(self, t: "VectorType") -> R:
        raise NotImplementedError


class MapTypeVisitor(Generic[R]):
    def visit_map_type(self, t: "MapType") -> R:
        raise NotImplementedError


class SetTypeVisitor(Generic[R]):
    def visit_set_type(self, t: "SetType") -> R:
        raise NotImplementedError


class GenericTypeVisitor(
    Generic[R],
    OptionalTypeVisitor[R],
    ArrayTypeVisitor[R],
    VectorTypeVisitor[R],
    MapTypeVisitor[R],
    SetTypeVisitor[R],
):
    def visit_generic_type(self, t: "GenericType") -> R:
        raise NotImplementedError

    @override
    def visit_optional_type(self, t: "OptionalType") -> R:
        return self.visit_generic_type(t)

    @override
    def visit_array_type(self, t: "ArrayType") -> R:
        return self.visit_generic_type(t)

    @override
    def visit_vector_type(self, t: "VectorType") -> R:
        return self.visit_generic_type(t)

    @override
    def visit_map_type(self, t: "MapType") -> R:
        return self.visit_generic_type(t)

    @override
    def visit_set_type(self, t: "SetType") -> R:
        return self.visit_generic_type(t)


class CallbackTypeVisitor(Generic[R]):
    def visit_callback_type(self, t: "CallbackType") -> R:
        raise NotImplementedError


class EnumTypeVisitor(Generic[R]):
    def visit_enum_type(self, t: "EnumType") -> R:
        raise NotImplementedError


class StructTypeVisitor(Generic[R]):
    def visit_struct_type(self, t: "StructType") -> R:
        raise NotImplementedError


class UnionTypeVisitor(Generic[R]):
    def visit_union_type(self, t: "UnionType") -> R:
        raise NotImplementedError


class IfaceTypeVisitor(Generic[R]):
    def visit_iface_type(self, t: "IfaceType") -> R:
        raise NotImplementedError


class UserTypeVisitor(
    Generic[R],
    EnumTypeVisitor[R],
    StructTypeVisitor[R],
    UnionTypeVisitor[R],
    IfaceTypeVisitor[R],
):
    def visit_user_type(self, t: "UserType") -> R:
        raise NotImplementedError

    @override
    def visit_enum_type(self, t: "EnumType") -> R:
        return self.visit_user_type(t)

    @override
    def visit_struct_type(self, t: "StructType") -> R:
        return self.visit_user_type(t)

    @override
    def visit_union_type(self, t: "UnionType") -> R:
        return self.visit_user_type(t)

    @override
    def visit_iface_type(self, t: "IfaceType") -> R:
        return self.visit_user_type(t)


class NonVoidTypeVisitor(
    Generic[R],
    OpaqueTypeVisitor[R],
    LiteralTypeVisitor[R],
    GenericTypeVisitor[R],
    CallbackTypeVisitor[R],
    UserTypeVisitor[R],
):
    def visit_non_void_type(self, t: "NonVoidType") -> R:
        raise NotImplementedError

    @override
    def visit_opaque_type(self, t: "OpaqueType") -> R:
        return self.visit_non_void_type(t)

    @override
    def visit_literal_type(self, t: "LiteralType") -> R:
        return self.visit_non_void_type(t)

    @override
    def visit_generic_type(self, t: "GenericType") -> R:
        return self.visit_non_void_type(t)

    @override
    def visit_callback_type(self, t: "CallbackType") -> R:
        return self.visit_non_void_type(t)

    @override
    def visit_user_type(self, t: "UserType") -> R:
        return self.visit_non_void_type(t)


class VoidTypeVisitor(Generic[R]):
    def visit_void_type(self, t: "VoidType") -> R:
        raise NotImplementedError


class TypeVisitor(
    Generic[R],
    NonVoidTypeVisitor[R],
    VoidTypeVisitor[R],
):
    def visit_type(self, t: "Type") -> R:
        raise NotImplementedError

    @override
    def visit_non_void_type(self, t: "NonVoidType") -> R:
        return self.visit_type(t)

    @override
    def visit_void_type(self, t: "VoidType") -> R:
        return self.visit_type(t)


class GenericArgVisitor(Generic[R]):
    def visit_generic_arg(self, d: "GenericArgDecl") -> R:
        raise NotImplementedError


class ParamVisitor(Generic[R]):
    def visit_param(self, d: "ParamDecl") -> R:
        raise NotImplementedError


class ShortTypeRefVisitor(Generic[R]):
    def visit_short_type_ref(self, d: "ShortTypeRefDecl") -> R:
        raise NotImplementedError


class LongTypeRefVisitor(Generic[R]):
    def visit_long_type_ref(self, d: "LongTypeRefDecl") -> R:
        raise NotImplementedError


class GenericTypeRefVisitor(Generic[R]):
    def visit_generic_type_ref(self, d: "GenericTypeRefDecl") -> R:
        raise NotImplementedError


class CallbackTypeRefVisitor(Generic[R]):
    def visit_callback_type_ref(self, d: "CallbackTypeRefDecl") -> R:
        raise NotImplementedError


class ExplicitTypeRefVisitor(
    Generic[R],
    ShortTypeRefVisitor[R],
    LongTypeRefVisitor[R],
    GenericTypeRefVisitor[R],
    CallbackTypeRefVisitor[R],
):
    def visit_explicit_type_ref(self, d: "ExplicitTypeRefDecl") -> R:
        raise NotImplementedError

    @override
    def visit_short_type_ref(self, d: "ShortTypeRefDecl") -> R:
        return self.visit_explicit_type_ref(d)

    @override
    def visit_long_type_ref(self, d: "LongTypeRefDecl") -> R:
        return self.visit_explicit_type_ref(d)

    @override
    def visit_generic_type_ref(self, d: "GenericTypeRefDecl") -> R:
        return self.visit_explicit_type_ref(d)

    @override
    def visit_callback_type_ref(self, d: "CallbackTypeRefDecl") -> R:
        return self.visit_explicit_type_ref(d)


class ImplicitTypeRefVisitor(Generic[R]):
    def visit_implicit_type_ref(self, d: "ImplicitTypeRefDecl") -> R:
        raise NotImplementedError


class TypeRefVisitor(
    Generic[R],
    ExplicitTypeRefVisitor[R],
    ImplicitTypeRefVisitor[R],
):
    def visit_type_ref(self, d: "TypeRefDecl") -> R:
        raise NotImplementedError

    @override
    def visit_explicit_type_ref(self, d: "ExplicitTypeRefDecl") -> R:
        return self.visit_type_ref(d)

    @override
    def visit_implicit_type_ref(self, d: "ImplicitTypeRefDecl") -> R:
        return self.visit_type_ref(d)


class PackageRefVisitor(Generic[R]):
    def visit_package_ref(self, d: "PackageRefDecl") -> R:
        raise NotImplementedError


class DeclarationRefVisitor(Generic[R]):
    def visit_declaration_ref(self, d: "DeclarationRefDecl") -> R:
        raise NotImplementedError


class PackageImportVisitor(Generic[R]):
    def visit_package_import(self, d: "PackageImportDecl") -> R:
        raise NotImplementedError


class DeclarationImportVisitor(Generic[R]):
    def visit_declaration_import(self, d: "DeclarationImportDecl") -> R:
        raise NotImplementedError


class ImportVisitor(
    Generic[R],
    PackageImportVisitor[R],
    DeclarationImportVisitor[R],
):
    def visit_import(self, d: "ImportDecl") -> R:
        raise NotImplementedError

    @override
    def visit_package_import(self, d: "PackageImportDecl") -> R:
        return self.visit_import(d)

    @override
    def visit_declaration_import(self, d: "DeclarationImportDecl") -> R:
        return self.visit_import(d)


class EnumItemVisitor(Generic[R]):
    def visit_enum_item(self, d: "EnumItemDecl") -> R:
        raise NotImplementedError


class StructFieldVisitor(Generic[R]):
    def visit_struct_field(self, d: "StructFieldDecl") -> R:
        raise NotImplementedError


class UnionFieldVisitor(Generic[R]):
    def visit_union_field(self, d: "UnionFieldDecl") -> R:
        raise NotImplementedError


class IfaceExtendVisitor(Generic[R]):
    def visit_iface_extend(self, d: "IfaceExtendDecl") -> R:
        raise NotImplementedError


class IfaceMethodVisitor(Generic[R]):
    def visit_iface_method(self, d: "IfaceMethodDecl") -> R:
        raise NotImplementedError


class EnumDeclVisitor(Generic[R]):
    def visit_enum_decl(self, d: "EnumDecl") -> R:
        raise NotImplementedError


class StructDeclVisitor(Generic[R]):
    def visit_struct_decl(self, d: "StructDecl") -> R:
        raise NotImplementedError


class UnionDeclVisitor(Generic[R]):
    def visit_union_decl(self, d: "UnionDecl") -> R:
        raise NotImplementedError


class IfaceDeclVisitor(Generic[R]):
    def visit_iface_decl(self, d: "IfaceDecl") -> R:
        raise NotImplementedError


class TypeDeclVisitor(
    Generic[R],
    EnumDeclVisitor[R],
    StructDeclVisitor[R],
    UnionDeclVisitor[R],
    IfaceDeclVisitor[R],
):
    def visit_type_decl(self, d: "TypeDecl") -> R:
        raise NotImplementedError

    @override
    def visit_enum_decl(self, d: "EnumDecl") -> R:
        return self.visit_type_decl(d)

    @override
    def visit_struct_decl(self, d: "StructDecl") -> R:
        return self.visit_type_decl(d)

    @override
    def visit_union_decl(self, d: "UnionDecl") -> R:
        return self.visit_type_decl(d)

    @override
    def visit_iface_decl(self, d: "IfaceDecl") -> R:
        return self.visit_type_decl(d)


class GlobFuncVisitor(Generic[R]):
    def visit_glob_func(self, d: "GlobFuncDecl") -> R:
        raise NotImplementedError


class PackageLevelVisitor(
    Generic[R],
    GlobFuncVisitor[R],
    TypeDeclVisitor[R],
):
    def visit_package_level(self, d: "PackageLevelDecl") -> R:
        raise NotImplementedError

    @override
    def visit_glob_func(self, d: "GlobFuncDecl") -> R:
        return self.visit_package_level(d)

    @override
    def visit_type_decl(self, d: "TypeDecl") -> R:
        return self.visit_package_level(d)


class PackageVisitor(Generic[R]):
    def visit_package(self, p: "PackageDecl") -> R:
        raise NotImplementedError


class PackageGroupVisitor(Generic[R]):
    def visit_package_group(self, g: "PackageGroup") -> R:
        raise NotImplementedError


class DeclVisitor(
    Generic[R],
    GenericArgVisitor[R],
    ParamVisitor[R],
    TypeRefVisitor[R],
    PackageRefVisitor[R],
    DeclarationRefVisitor[R],
    ImportVisitor[R],
    EnumItemVisitor[R],
    StructFieldVisitor[R],
    UnionFieldVisitor[R],
    IfaceExtendVisitor[R],
    IfaceMethodVisitor[R],
    PackageLevelVisitor[R],
    PackageVisitor[R],
    PackageGroupVisitor[R],
):
    def visit_decl(self, d: "Decl") -> R:
        raise NotImplementedError

    @override
    def visit_generic_arg(self, d: "GenericArgDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_param(self, d: "ParamDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_type_ref(self, d: "TypeRefDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_package_ref(self, d: "PackageRefDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_declaration_ref(self, d: "DeclarationRefDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_import(self, d: "ImportDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_enum_item(self, d: "EnumItemDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_struct_field(self, d: "StructFieldDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_union_field(self, d: "UnionFieldDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_iface_extend(self, d: "IfaceExtendDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_iface_method(self, d: "IfaceMethodDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_package_level(self, d: "PackageLevelDecl") -> R:
        return self.visit_decl(d)

    @override
    def visit_package(self, p: "PackageDecl") -> R:
        return self.visit_decl(p)

    @override
    def visit_package_group(self, g: "PackageGroup") -> R:
        raise NotImplementedError


class RecursiveDeclVisitor(DeclVisitor[None]):
    """A visitor that recursively traverses all declarations and their sub-declarations.

    This class is useful for full-tree traversal scenarios.
    """

    @override
    def visit_decl(self, d: "Decl") -> None:
        pass

    @override
    def visit_generic_arg(self, d: "GenericArgDecl") -> None:
        d.ty_ref.accept(self)
        super().visit_generic_arg(d)

    @override
    def visit_param(self, d: "ParamDecl") -> None:
        d.ty_ref.accept(self)
        super().visit_param(d)

    @override
    def visit_implicit_type_ref(self, d: "ImplicitTypeRefDecl") -> None:
        super().visit_implicit_type_ref(d)

    @override
    def visit_short_type_ref(self, d: "ShortTypeRefDecl") -> None:
        super().visit_short_type_ref(d)

    @override
    def visit_long_type_ref(self, d: "LongTypeRefDecl") -> None:
        super().visit_long_type_ref(d)

    @override
    def visit_generic_type_ref(self, d: "GenericTypeRefDecl") -> None:
        for i in d.args:
            i.accept(self)
        super().visit_generic_type_ref(d)

    @override
    def visit_callback_type_ref(self, d: "CallbackTypeRefDecl") -> None:
        for i in d.params:
            i.accept(self)
        d.return_ty_ref.accept(self)
        super().visit_callback_type_ref(d)

    @override
    def visit_package_ref(self, d: "PackageRefDecl") -> None:
        super().visit_package_ref(d)

    @override
    def visit_declaration_ref(self, d: "DeclarationRefDecl") -> None:
        d.pkg_ref.accept(self)
        super().visit_declaration_ref(d)

    @override
    def visit_package_import(self, d: "PackageImportDecl") -> None:
        d.pkg_ref.accept(self)
        super().visit_package_import(d)

    @override
    def visit_declaration_import(self, d: "DeclarationImportDecl") -> None:
        d.decl_ref.accept(self)
        super().visit_declaration_import(d)

    @override
    def visit_enum_item(self, d: "EnumItemDecl") -> None:
        super().visit_enum_item(d)

    @override
    def visit_struct_field(self, d: "StructFieldDecl") -> None:
        d.ty_ref.accept(self)
        super().visit_struct_field(d)

    @override
    def visit_union_field(self, d: "UnionFieldDecl") -> None:
        d.ty_ref.accept(self)
        super().visit_union_field(d)

    @override
    def visit_iface_extend(self, d: "IfaceExtendDecl") -> None:
        d.ty_ref.accept(self)
        super().visit_iface_extend(d)

    @override
    def visit_iface_method(self, d: "IfaceMethodDecl") -> None:
        for i in d.params:
            i.accept(self)
        d.return_ty_ref.accept(self)
        super().visit_iface_method(d)

    @override
    def visit_enum_decl(self, d: "EnumDecl") -> None:
        d.ty_ref.accept(self)
        for i in d.items:
            i.accept(self)
        super().visit_enum_decl(d)

    @override
    def visit_union_decl(self, d: "UnionDecl") -> None:
        for i in d.fields:
            i.accept(self)
        super().visit_union_decl(d)

    @override
    def visit_struct_decl(self, d: "StructDecl") -> None:
        for i in d.fields:
            i.accept(self)
        super().visit_struct_decl(d)

    @override
    def visit_iface_decl(self, d: "IfaceDecl") -> None:
        for i in d.extends:
            i.accept(self)
        for i in d.methods:
            i.accept(self)
        super().visit_iface_decl(d)

    @override
    def visit_glob_func(self, d: "GlobFuncDecl") -> None:
        for i in d.params:
            i.accept(self)
        d.return_ty_ref.accept(self)
        super().visit_glob_func(d)

    @override
    def visit_package(self, p: "PackageDecl") -> None:
        for i in p.pkg_imports:
            i.accept(self)
        for i in p.decl_imports:
            i.accept(self)
        for i in p.declarations:
            i.accept(self)
        super().visit_package(p)

    @override
    def visit_package_group(self, g: "PackageGroup") -> None:
        for i in g.packages:
            i.accept(self)
