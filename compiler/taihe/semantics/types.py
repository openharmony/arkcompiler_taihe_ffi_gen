"""Defines the type system."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, TypeVar

from typing_extensions import override

from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import GenericArgumentsError, TypeUsageError

if TYPE_CHECKING:
    from taihe.semantics.declarations import (
        CallbackTypeRefDecl,
        EnumDecl,
        GenericArgDecl,
        IfaceDecl,
        StructDecl,
        TypeDecl,
        TypeRefDecl,
        UnionDecl,
    )
    from taihe.semantics.visitor import (
        ArrayTypeVisitor,
        CallbackTypeVisitor,
        EnumTypeVisitor,
        GenericTypeVisitor,
        IfaceTypeVisitor,
        LiteralTypeVisitor,
        MapTypeVisitor,
        NonVoidTypeVisitor,
        OpaqueTypeVisitor,
        OptionalTypeVisitor,
        ScalarTypeVisitor,
        SetTypeVisitor,
        StringTypeVisitor,
        StructTypeVisitor,
        TypeVisitor,
        UnionTypeVisitor,
        UserTypeVisitor,
        VectorTypeVisitor,
        VoidTypeVisitor,
    )


R = TypeVar("R")


############################
# Infrastructure for Types #
############################


@dataclass(frozen=True, repr=False)
class Type(ABC):
    """Base class for all types."""

    ref: "TypeRefDecl"

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.signature}>"

    @property
    @abstractmethod
    def signature(self) -> str:
        """Return the representation of the type."""

    @abstractmethod
    def accept(self, v: "TypeVisitor[R]") -> R: ...


@dataclass(frozen=True, repr=False)
class VoidType(Type):
    """Represents the void type, which indicates no value."""

    @property
    @override
    def signature(self):
        return "void"

    @override
    def accept(self, v: "VoidTypeVisitor[R]") -> R:
        return v.visit_void_type(self)


@dataclass(frozen=True, repr=False)
class NonVoidType(Type, ABC):
    """Represents a valid type that can be used in the type system."""

    @override
    def accept(self, v: "NonVoidTypeVisitor[R]") -> R: ...


#################
# Builtin Types #
#################


@dataclass(frozen=True, repr=False)
class LiteralType(NonVoidType, ABC):
    """Base class for literal types."""

    @abstractmethod
    def accept(self, v: "LiteralTypeVisitor[R]") -> R: ...


class ScalarKind(Enum):
    """Enumeration of scalar types."""

    BOOL = ("bool", 8, False, False)
    F32 = ("f32", 32, True, True)
    F64 = ("f64", 64, True, True)
    I8 = ("i8", 8, True, False)
    I16 = ("i16", 16, True, False)
    I32 = ("i32", 32, True, False)
    I64 = ("i64", 64, True, False)
    U8 = ("u8", 8, False, False)
    U16 = ("u16", 16, False, False)
    U32 = ("u32", 32, False, False)
    U64 = ("u64", 64, False, False)

    def __init__(self, symbol: str, width: int, is_signed: bool, is_float: bool):
        self.symbol = symbol
        self.width = width
        self.is_signed = is_signed
        self.is_float = is_float


@dataclass(frozen=True, repr=False)
class ScalarType(LiteralType):
    kind: ScalarKind

    @property
    @override
    def signature(self):
        return self.kind.symbol

    @override
    def accept(self, v: "ScalarTypeVisitor[R]") -> R:
        return v.visit_scalar_type(self)


@dataclass(frozen=True, repr=False)
class StringType(LiteralType):
    @property
    @override
    def signature(self):
        return "String"

    @override
    def accept(self, v: "StringTypeVisitor[R]") -> R:
        return v.visit_string_type(self)


@dataclass(frozen=True, repr=False)
class OpaqueType(NonVoidType):
    @property
    @override
    def signature(self):
        return "Opaque"

    @override
    def accept(self, v: "OpaqueTypeVisitor[R]") -> R:
        return v.visit_opaque_type(self)


# Builtin Types Map
BUILTIN_TYPES: dict[str, Callable[["TypeRefDecl"], Type]] = {
    "void": VoidType,
    "bool": lambda ty_ref: ScalarType(ty_ref, ScalarKind.BOOL),
    "f32": lambda ty_ref: ScalarType(ty_ref, ScalarKind.F32),
    "f64": lambda ty_ref: ScalarType(ty_ref, ScalarKind.F64),
    "i8": lambda ty_ref: ScalarType(ty_ref, ScalarKind.I8),
    "i16": lambda ty_ref: ScalarType(ty_ref, ScalarKind.I16),
    "i32": lambda ty_ref: ScalarType(ty_ref, ScalarKind.I32),
    "i64": lambda ty_ref: ScalarType(ty_ref, ScalarKind.I64),
    "u8": lambda ty_ref: ScalarType(ty_ref, ScalarKind.U8),
    "u16": lambda ty_ref: ScalarType(ty_ref, ScalarKind.U16),
    "u32": lambda ty_ref: ScalarType(ty_ref, ScalarKind.U32),
    "u64": lambda ty_ref: ScalarType(ty_ref, ScalarKind.U64),
    "String": StringType,
    "Opaque": OpaqueType,
}


#################
# Callback Type #
#################


@dataclass(frozen=True, repr=False)
class CallbackType(NonVoidType):
    ref: "CallbackTypeRefDecl"

    @property
    @override
    def signature(self):
        params_fmt = ", ".join(
            f"{param.name}: {param.ty.signature}" for param in self.ref.params
        )
        return_fmt = self.ref.return_ty.signature
        return f"({params_fmt}) => {return_fmt}"

    @override
    def accept(self, v: "CallbackTypeVisitor[R]") -> R:
        return v.visit_callback_type(self)


####################
# Builtin Generics #
####################


class GenericType(NonVoidType, ABC):
    @classmethod
    @abstractmethod
    def try_construct(
        cls,
        ty_ref: "TypeRefDecl",
        *args: "GenericArgDecl",
        dm: "DiagnosticsManager",
    ) -> "GenericType | None": ...

    @abstractmethod
    def accept(self, v: "GenericTypeVisitor[R]") -> R: ...


@dataclass(frozen=True, repr=False)
class ArrayType(GenericType):
    item_ty: NonVoidType

    @property
    @override
    def signature(self):
        return f"Array<{self.item_ty.signature}>"

    @classmethod
    def try_construct(
        cls,
        ty_ref: "TypeRefDecl",
        *args: "GenericArgDecl",
        dm: "DiagnosticsManager",
    ) -> "ArrayType | None":
        if len(args) != 1:
            dm.emit(GenericArgumentsError(ty_ref, 1, len(args)))
            return None
        item_ty = args[0].ty
        if not isinstance(item_ty, NonVoidType):
            dm.emit(TypeUsageError(args[0].ty_ref, item_ty))
            return None
        return cls(ty_ref, item_ty)

    @override
    def accept(self, v: "ArrayTypeVisitor[R]") -> R:
        return v.visit_array_type(self)


@dataclass(frozen=True, repr=False)
class OptionalType(GenericType):
    item_ty: NonVoidType

    @property
    @override
    def signature(self):
        return f"Optional<{self.item_ty.signature}>"

    @classmethod
    def try_construct(
        cls,
        ty_ref: "TypeRefDecl",
        *args: "GenericArgDecl",
        dm: "DiagnosticsManager",
    ) -> "OptionalType | None":
        if len(args) != 1:
            dm.emit(GenericArgumentsError(ty_ref, 1, len(args)))
            return None
        item_ty = args[0].ty
        if not isinstance(item_ty, NonVoidType):
            dm.emit(TypeUsageError(args[0].ty_ref, item_ty))
            return None
        return cls(ty_ref, item_ty)

    @override
    def accept(self, v: "OptionalTypeVisitor[R]") -> R:
        return v.visit_optional_type(self)


@dataclass(frozen=True, repr=False)
class VectorType(GenericType):
    val_ty: NonVoidType

    @property
    @override
    def signature(self):
        return f"Vector<{self.val_ty.signature}>"

    @classmethod
    def try_construct(
        cls,
        ty_ref: "TypeRefDecl",
        *args: "GenericArgDecl",
        dm: "DiagnosticsManager",
    ) -> "VectorType | None":
        if len(args) != 1:
            dm.emit(GenericArgumentsError(ty_ref, 1, len(args)))
            return None
        key_ty = args[0].ty
        if not isinstance(key_ty, NonVoidType):
            dm.emit(TypeUsageError(args[0].ty_ref, key_ty))
            return None
        return cls(ty_ref, key_ty)

    @override
    def accept(self, v: "VectorTypeVisitor[R]") -> R:
        return v.visit_vector_type(self)


@dataclass(frozen=True, repr=False)
class MapType(GenericType):
    key_ty: NonVoidType
    val_ty: NonVoidType

    @property
    @override
    def signature(self):
        return f"Map<{self.key_ty.signature}, {self.val_ty.signature}>"

    @classmethod
    def try_construct(
        cls,
        ty_ref: "TypeRefDecl",
        *args: "GenericArgDecl",
        dm: "DiagnosticsManager",
    ) -> "MapType | None":
        if len(args) != 2:
            dm.emit(GenericArgumentsError(ty_ref, 2, len(args)))
            return None
        key_ty = args[0].ty
        if not isinstance(key_ty, NonVoidType):
            dm.emit(TypeUsageError(args[0].ty_ref, key_ty))
            return None
        val_ty = args[1].ty
        if not isinstance(val_ty, NonVoidType):
            dm.emit(TypeUsageError(args[1].ty_ref, val_ty))
            return None
        return cls(ty_ref, key_ty, val_ty)

    @override
    def accept(self, v: "MapTypeVisitor[R]") -> R:
        return v.visit_map_type(self)


@dataclass(frozen=True, repr=False)
class SetType(GenericType):
    key_ty: NonVoidType

    @property
    @override
    def signature(self):
        return f"Set<{self.key_ty.signature}>"

    @classmethod
    def try_construct(
        cls,
        ty_ref: "TypeRefDecl",
        *args: "GenericArgDecl",
        dm: "DiagnosticsManager",
    ) -> "SetType | None":
        if len(args) != 1:
            dm.emit(GenericArgumentsError(ty_ref, 1, len(args)))
            return None
        key_ty = args[0].ty
        if not isinstance(key_ty, NonVoidType):
            dm.emit(TypeUsageError(args[0].ty_ref, key_ty))
            return None
        return cls(ty_ref, key_ty)

    @override
    def accept(self, v: "SetTypeVisitor[R]") -> R:
        return v.visit_set_type(self)


# Builtin Generics Map
BUILTIN_GENERICS: dict[str, type[GenericType]] = {
    "Array": ArrayType,
    "Optional": OptionalType,
    "Vector": VectorType,
    "Map": MapType,
    "Set": SetType,
}


##############
# User Types #
##############


@dataclass(frozen=True, repr=False)
class UserType(NonVoidType, ABC):
    decl: "TypeDecl"

    @property
    @override
    def signature(self):
        return self.decl.full_name

    @abstractmethod
    def accept(self, v: "UserTypeVisitor[R]") -> R: ...


@dataclass(frozen=True, repr=False)
class EnumType(UserType):
    decl: "EnumDecl"

    @override
    def accept(self, v: "EnumTypeVisitor[R]") -> R:
        return v.visit_enum_type(self)


@dataclass(frozen=True, repr=False)
class StructType(UserType):
    decl: "StructDecl"

    @override
    def accept(self, v: "StructTypeVisitor[R]") -> R:
        return v.visit_struct_type(self)


@dataclass(frozen=True, repr=False)
class UnionType(UserType):
    decl: "UnionDecl"

    @override
    def accept(self, v: "UnionTypeVisitor[R]") -> R:
        return v.visit_union_type(self)


@dataclass(frozen=True, repr=False)
class IfaceType(UserType):
    decl: "IfaceDecl"

    @override
    def accept(self, v: "IfaceTypeVisitor[R]") -> R:
        return v.visit_iface_type(self)
