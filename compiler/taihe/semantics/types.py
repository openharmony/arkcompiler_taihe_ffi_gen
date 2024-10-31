"""Defines the type system."""

from dataclasses import dataclass
from enum import Enum, IntFlag, auto
from typing import TYPE_CHECKING, Any, Optional, Protocol

if TYPE_CHECKING:
    from taihe.semantics.visitor import TypeVisitor

############################
# Infrastructure for Types #
############################


class TypeAlike(Protocol):
    """Represents classes that are similar to, but not necessarily identical to, types.

    This protocol defines a single method, `_accept`, which is used by `TypeVisitor` instances
    to traverse and process instances of classes conforming to this protocol.

    Notable implementors to this protocol are type containers, i.e. `QualifiedType` and `TypeRef`.
    """

    def _accept(self, v: "TypeVisitor") -> Any: ...


class Type(TypeAlike):
    """Represents a concrete type."""


@dataclass
class TypeRef(TypeAlike):
    """Repersents a user of a `Type`.

    Each user of a `Type` must be encapsulated in a `TypeRef`.

    For example:
    ```
    struct Foo { ... }.     // `Foo` is a `TypeDecl`.

    fn func(foo: Foo);      // `Foo` is a `TypeRef`, which points to `Foo`.
    fn func(foo: BadType);  // `BadType` is a `TypeRef`, which points to `None`.
    ```
    """

    name: str
    ref_ty: Optional[Type] = None

    def _accept(self, v: "TypeVisitor") -> Any:
        v.visiting = self
        return v.visit_type_ref(self)

    def __repr__(self) -> str:
        if self.ref_ty:
            return f"<type-ref to {self.ref_ty!r}>"
        else:
            return f"<type-ref ??? {self.name!r}>"


class TypeQualifier(IntFlag):
    NONE = 0
    MUT = auto()


@dataclass
class QualifiedType(TypeAlike):
    inner_ty: TypeRef
    qual: TypeQualifier = TypeQualifier.NONE

    def _accept(self, v: "TypeVisitor") -> Any:
        v.visiting = self
        return v.visit_qualified_type(self)

    def __repr__(self) -> str:
        return f"<type-qual {self.qual.name!r} {self.inner_ty!r}>"


##################
# Built-in Types #
##################


class BuiltinTypeKind(Enum):
    VOID = 0
    BOOL = 1
    INTEGER = 2
    FLOAT = 3

    STRING = 0x10


@dataclass(frozen=True)
class BuiltinType(Type):
    """Represents built-in types, including scalars and strings.

    Invariant: all primitive types must be directy obtained with `lookup` or
    using the exported values such as `VOID`. Do not copy or construct it on
    your own. This design allows tests such as `my_type is VOID`.
    """

    name: str
    kind: BuiltinTypeKind

    def _accept(self, v: "TypeVisitor") -> Any:
        v.visiting = self
        return v.visit_builtin_type(self)

    @staticmethod
    def lookup(name: str) -> Optional["BuiltinType"]:
        return _TYPE_MAPS.get(name)

    def __repr__(self) -> str:
        return f"<type-builtin {self.name!r}>"


@dataclass(frozen=True, repr=False)
class ScalarType(BuiltinType):
    width: int
    is_signed: bool
    is_float: bool = False

    def _accept(self, v: "TypeVisitor") -> Any:
        v.visiting = self
        return v.visit_scalar_type(self)


@dataclass(frozen=True, repr=False)
class SpecialType(BuiltinType):
    def _accept(self, v: "TypeVisitor") -> Any:
        v.visiting = self
        return v.visit_special_type(self)


VOID = SpecialType("()", BuiltinTypeKind.VOID)
STRING = SpecialType("String", BuiltinTypeKind.STRING)

BOOL = ScalarType(
    "bool", BuiltinTypeKind.BOOL, 8, is_signed=False
)  # Essentially a `u8`
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

_TYPE_MAPS: dict[str, BuiltinType] = {
    ty.name: ty
    for ty in [VOID, BOOL, STRING, I8, I16, I32, I64, U8, U16, U32, U64, F32, F64]
}
