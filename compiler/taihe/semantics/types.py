"""Defines the type system."""

from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Protocol

from typing_extensions import override

if TYPE_CHECKING:
    from taihe.semantics.declarations import (
        EnumDecl,
        IfaceDecl,
        StructDecl,
        TypeDecl,
    )
    from taihe.semantics.visitor import TypeVisitor

############################
# Infrastructure for Types #
############################


class TypeProtocol(Protocol):
    def _accept(self, v: "TypeVisitor") -> Any: ...


class Type(metaclass=ABCMeta):
    """Represents a concrete type."""

    @property
    @abstractmethod
    def repr(self) -> str: ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.repr}>"

    @abstractmethod
    def _accept(self, v: "TypeVisitor") -> Any: ...


##################
# Built-in Types #
##################


class BuiltinTypeKind(Enum):
    VOID = 0

    BOOL = 1
    INTEGER = 2
    FLOAT = 3

    STRING = 0x10


@dataclass(frozen=True, repr=False)
class BuiltinType(Type, metaclass=ABCMeta):
    """Represents built-in types, including scalars and strings.

    Invariant: all primitive types must be directy obtained with `lookup` or
    using the exported values such as `VOID`. Do not copy or construct it on
    your own. This design allows tests such as `my_type is VOID`.
    """

    name: str
    kind: BuiltinTypeKind

    @property
    @override
    def repr(self):
        return f"{self.name}"


@dataclass(frozen=True, repr=False)
class ScalarType(BuiltinType):
    width: int
    is_signed: bool
    is_float: bool = False

    @override
    def _accept(self, v: "TypeVisitor") -> Any:
        return v.visit_scalar_type(self)


@dataclass(frozen=True, repr=False)
class SpecialType(BuiltinType):
    @override
    def _accept(self, v: "TypeVisitor") -> Any:
        return v.visit_special_type(self)


BOOL = ScalarType("bool", BuiltinTypeKind.BOOL, 8, is_signed=False)

F32 = ScalarType("f32", BuiltinTypeKind.FLOAT, 32, is_signed=True, is_float=True)
F64 = ScalarType("f64", BuiltinTypeKind.FLOAT, 64, is_signed=True, is_float=True)

I8 = ScalarType("i8", BuiltinTypeKind.INTEGER, 8, is_signed=True)
I16 = ScalarType("i16", BuiltinTypeKind.INTEGER, 16, is_signed=True)
I32 = ScalarType("i32", BuiltinTypeKind.INTEGER, 32, is_signed=True)
I64 = ScalarType("i64", BuiltinTypeKind.INTEGER, 64, is_signed=True)

U8 = ScalarType("u8", BuiltinTypeKind.INTEGER, 8, is_signed=False)
U16 = ScalarType("u16", BuiltinTypeKind.INTEGER, 16, is_signed=False)
U32 = ScalarType("u32", BuiltinTypeKind.INTEGER, 32, is_signed=False)
U64 = ScalarType("u64", BuiltinTypeKind.INTEGER, 64, is_signed=False)

STRING = SpecialType("String", BuiltinTypeKind.STRING)

# Builtin Types map
BUILTIN_TYPES: dict[str, Type] = {
    ty.name: ty for ty in [BOOL, I8, I16, I32, I64, U8, U16, U32, U64, F32, F64, STRING]
}


####################
# Builtin Generics #
####################


@dataclass(frozen=True, repr=False)
class ArrayType(Type, metaclass=ABCMeta):
    item_ty: Type

    @override
    def _accept(self, v: "TypeVisitor") -> Any:
        return v.visit_array_type(self)

    @property
    @override
    def repr(self):
        return f"array of ({self.item_ty.repr})"


@dataclass(frozen=True, repr=False)
class VectorType(Type, metaclass=ABCMeta):
    val_ty: Type

    @override
    def _accept(self, v: "TypeVisitor") -> Any:
        return v.visit_vector_type(self)

    @property
    @override
    def repr(self):
        return f"Vector<{self.val_ty.repr}>"


@dataclass(frozen=True, repr=False)
class MapType(Type, metaclass=ABCMeta):
    key_ty: Type
    val_ty: Type

    @override
    def _accept(self, v: "TypeVisitor") -> Any:
        return v.visit_map_type(self)

    @property
    @override
    def repr(self):
        return f"Map<{self.key_ty.repr}, {self.val_ty.repr}>"


@dataclass(frozen=True, repr=False)
class SetType(Type, metaclass=ABCMeta):
    key_ty: Type

    @override
    def _accept(self, v: "TypeVisitor") -> Any:
        return v.visit_set_type(self)

    @property
    @override
    def repr(self):
        return f"Set<{self.key_ty.repr}>"


@dataclass(frozen=True, repr=False)
class CallbackType(Type, metaclass=ABCMeta):
    return_ty: Optional[Type]
    params_ty: tuple[Type, ...]

    @override
    def _accept(self, v: "TypeVisitor") -> Any:
        return v.visit_callback_type(self)

    @property
    @override
    def repr(self):
        return_fmt = ty.repr if (ty := self.return_ty) else "void"
        params_fmt = ", ".join(ty.repr for ty in self.params_ty)
        return f"({params_fmt}) -> {return_fmt}"


# Builtin Generics Map
BUILTIN_GENERICS: dict[str, Callable[[*tuple[Type, ...]], Type]] = {  # pyre-ignore
    "Vector": lambda *args: VectorType(*args),
    "Map": lambda *args: MapType(*args),
    "Set": lambda *args: SetType(*args),
}


##############
# User Types #
##############


class UserType(Type, metaclass=ABCMeta):
    ty_decl: "TypeDecl"

    @property
    @override
    def repr(self):
        return f"{self.ty_decl.full_name}"


@dataclass(frozen=True, repr=False)
class StructType(UserType):
    ty_decl: "StructDecl"

    @override
    def _accept(self, v: "TypeVisitor") -> Any:
        return v.visit_struct_type(self)


@dataclass(frozen=True, repr=False)
class EnumType(UserType):
    ty_decl: "EnumDecl"

    @override
    def _accept(self, v: "TypeVisitor") -> Any:
        return v.visit_enum_type(self)


@dataclass(frozen=True, repr=False)
class IfaceType(UserType):
    ty_decl: "IfaceDecl"

    @override
    def _accept(self, v: "TypeVisitor") -> Any:
        return v.visit_iface_type(self)
