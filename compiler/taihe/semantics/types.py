# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Huawei Device Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        GenericTypeRefDecl,
        IfaceDecl,
        StructDecl,
        TypeDecl,
        TypeRefDecl,
        UnionDecl,
    )
    from taihe.semantics.visitor import (
        ArrayTypeVisitor,
        BooleanTypeVisitor,
        BuiltinTypeVisitor,
        CallbackTypeVisitor,
        CompleterTypeVisitor,
        EnumTypeVisitor,
        FloatingPointTypeVisitor,
        FutureTypeVisitor,
        GenericTypeVisitor,
        IfaceTypeVisitor,
        IntegerTypeVisitor,
        MapTypeVisitor,
        NonVoidTypeVisitor,
        OpaqueTypeVisitor,
        OptionalTypeVisitor,
        SetTypeVisitor,
        StringTypeVisitor,
        StructTypeVisitor,
        TypeVisitor,
        UnionTypeVisitor,
        UnitTypeVisitor,
        UserTypeVisitor,
        VectorTypeVisitor,
        VoidTypeVisitor,
    )


_R = TypeVar("_R")


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
    def accept(self, v: "TypeVisitor[_R]") -> _R: ...


@dataclass(frozen=True, repr=False)
class VoidType(Type):
    """Represents the void type, which indicates no value."""

    @property
    @override
    def signature(self):
        return "void"

    @override
    def accept(self, v: "VoidTypeVisitor[_R]") -> _R:
        return v.visit_void_type(self)


@dataclass(frozen=True, repr=False)
class NonVoidType(Type, ABC):
    """Represents a valid type that can be used in the type system."""

    @override
    def accept(self, v: "NonVoidTypeVisitor[_R]") -> _R: ...


#################
# Builtin Types #
#################


@dataclass(frozen=True, repr=False)
class BuiltinType(NonVoidType, ABC):
    """Base class for literal types."""

    @abstractmethod
    def accept(self, v: "BuiltinTypeVisitor[_R]") -> _R: ...


@dataclass(frozen=True, repr=False)
class UnitType(BuiltinType):
    @property
    @override
    def signature(self):
        return "unit"

    @override
    def accept(self, v: "UnitTypeVisitor[_R]") -> _R:
        return v.visit_unit_type(self)


class ScalarKindClass:
    """Base class for scalar type kinds."""

    def __init__(self, symbol: str):
        self.symbol = symbol

    @property
    @abstractmethod
    def width(self) -> int: ...

    @abstractmethod
    def is_signed(self) -> bool: ...


class IntegerKind(ScalarKindClass, Enum):
    I8 = ("i8", 8, True)
    I16 = ("i16", 16, True)
    I32 = ("i32", 32, True)
    I64 = ("i64", 64, True)
    U8 = ("u8", 8, False)
    U16 = ("u16", 16, False)
    U32 = ("u32", 32, False)
    U64 = ("u64", 64, False)

    def __init__(self, symbol: str, width: int, is_signed: bool):
        super().__init__(symbol)
        self._width = width
        self._is_signed = is_signed

    @property
    def width(self) -> int:
        return self._width

    def is_signed(self) -> bool:
        return self._is_signed


class BooleanKind(ScalarKindClass, Enum):
    BOOL = ("bool",)

    def __init__(self, symbol: str):
        super().__init__(symbol)

    @property
    def width(self) -> int:
        return 8

    def is_signed(self) -> bool:
        return False


class FloatingPointKind(ScalarKindClass, Enum):
    F32 = ("f32", 32)
    F64 = ("f64", 64)

    def __init__(self, symbol: str, width: int):
        super().__init__(symbol)
        self._width = width

    @property
    def width(self) -> int:
        return self._width

    def is_signed(self) -> bool:
        return True


ScalarKind = BooleanKind | IntegerKind | FloatingPointKind


class ScalarKinds:
    BOOL = BooleanKind.BOOL
    I8 = IntegerKind.I8
    I16 = IntegerKind.I16
    I32 = IntegerKind.I32
    I64 = IntegerKind.I64
    U8 = IntegerKind.U8
    U16 = IntegerKind.U16
    U32 = IntegerKind.U32
    U64 = IntegerKind.U64
    F32 = FloatingPointKind.F32
    F64 = FloatingPointKind.F64


@dataclass(frozen=True, repr=False)
class ScalarType(BuiltinType):
    kind: ScalarKind

    @property
    @override
    def signature(self):
        return self.kind.symbol


@dataclass(frozen=True, repr=False)
class BooleanType(ScalarType):
    kind: BooleanKind = BooleanKind.BOOL

    @override
    def accept(self, v: "BooleanTypeVisitor[_R]") -> _R:
        return v.visit_boolean_type(self)


@dataclass(frozen=True, repr=False)
class FloatingPointType(ScalarType):
    kind: FloatingPointKind

    @override
    def accept(self, v: "FloatingPointTypeVisitor[_R]") -> _R:
        return v.visit_floating_point_type(self)


@dataclass(frozen=True, repr=False)
class IntegerType(ScalarType):
    kind: IntegerKind

    @override
    def accept(self, v: "IntegerTypeVisitor[_R]") -> _R:
        return v.visit_integer_type(self)


@dataclass(frozen=True, repr=False)
class StringType(BuiltinType):
    @property
    @override
    def signature(self):
        return "String"

    @override
    def accept(self, v: "StringTypeVisitor[_R]") -> _R:
        return v.visit_string_type(self)


@dataclass(frozen=True, repr=False)
class OpaqueType(BuiltinType):
    @property
    @override
    def signature(self):
        return "Opaque"

    @override
    def accept(self, v: "OpaqueTypeVisitor[_R]") -> _R:
        return v.visit_opaque_type(self)


# Builtin Types Map
BUILTIN_TYPES: dict[str, Callable[["TypeRefDecl"], Type]] = {
    "void": VoidType,
    "unit": UnitType,
    "bool": BooleanType,
    "f32": lambda ty_ref: FloatingPointType(ty_ref, FloatingPointKind.F32),
    "f64": lambda ty_ref: FloatingPointType(ty_ref, FloatingPointKind.F64),
    "i8": lambda ty_ref: IntegerType(ty_ref, IntegerKind.I8),
    "i16": lambda ty_ref: IntegerType(ty_ref, IntegerKind.I16),
    "i32": lambda ty_ref: IntegerType(ty_ref, IntegerKind.I32),
    "i64": lambda ty_ref: IntegerType(ty_ref, IntegerKind.I64),
    "u8": lambda ty_ref: IntegerType(ty_ref, IntegerKind.U8),
    "u16": lambda ty_ref: IntegerType(ty_ref, IntegerKind.U16),
    "u32": lambda ty_ref: IntegerType(ty_ref, IntegerKind.U32),
    "u64": lambda ty_ref: IntegerType(ty_ref, IntegerKind.U64),
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
    def accept(self, v: "CallbackTypeVisitor[_R]") -> _R:
        return v.visit_callback_type(self)


####################
# Builtin Generics #
####################


class GenericType(NonVoidType, ABC):
    @classmethod
    @abstractmethod
    def try_construct(
        cls,
        ref: "GenericTypeRefDecl",
        dm: DiagnosticsManager,
    ) -> "GenericType | None":
        """Try to construct the generic type from the type reference.

        Args:
            ref: The generic type reference declaration.
            dm: The diagnostics manager.

        Returns:
            The constructed generic type, or None if construction failed.
        """

    @abstractmethod
    def accept(self, v: "GenericTypeVisitor[_R]") -> _R: ...


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
        ref: "GenericTypeRefDecl",
        dm: DiagnosticsManager,
    ) -> "ArrayType | None":
        if len(ref.args) != 1:
            dm.emit(GenericArgumentsError(ref, 1, len(ref.args)))
            return None
        item_ty = ref.args[0].ty
        if not isinstance(item_ty, NonVoidType):
            dm.emit(TypeUsageError(ref.args[0].ty_ref, item_ty))
            return None
        return cls(ref, item_ty)

    @override
    def accept(self, v: "ArrayTypeVisitor[_R]") -> _R:
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
        ref: "GenericTypeRefDecl",
        dm: DiagnosticsManager,
    ) -> "OptionalType | None":
        if len(ref.args) != 1:
            dm.emit(GenericArgumentsError(ref, 1, len(ref.args)))
            return None
        item_ty = ref.args[0].ty
        if not isinstance(item_ty, NonVoidType):
            dm.emit(TypeUsageError(ref.args[0].ty_ref, item_ty))
            return None
        return cls(ref, item_ty)

    @override
    def accept(self, v: "OptionalTypeVisitor[_R]") -> _R:
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
        ref: "GenericTypeRefDecl",
        dm: DiagnosticsManager,
    ) -> "VectorType | None":
        if len(ref.args) != 1:
            dm.emit(GenericArgumentsError(ref, 1, len(ref.args)))
            return None
        key_ty = ref.args[0].ty
        if not isinstance(key_ty, NonVoidType):
            dm.emit(TypeUsageError(ref.args[0].ty_ref, key_ty))
            return None
        return cls(ref, key_ty)

    @override
    def accept(self, v: "VectorTypeVisitor[_R]") -> _R:
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
        ref: "GenericTypeRefDecl",
        dm: DiagnosticsManager,
    ) -> "MapType | None":
        if len(ref.args) != 2:
            dm.emit(GenericArgumentsError(ref, 2, len(ref.args)))
            return None
        key_ty = ref.args[0].ty
        if not isinstance(key_ty, NonVoidType):
            dm.emit(TypeUsageError(ref.args[0].ty_ref, key_ty))
            return None
        val_ty = ref.args[1].ty
        if not isinstance(val_ty, NonVoidType):
            dm.emit(TypeUsageError(ref.args[1].ty_ref, val_ty))
            return None
        return cls(ref, key_ty, val_ty)

    @override
    def accept(self, v: "MapTypeVisitor[_R]") -> _R:
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
        ref: "GenericTypeRefDecl",
        dm: DiagnosticsManager,
    ) -> "SetType | None":
        if len(ref.args) != 1:
            dm.emit(GenericArgumentsError(ref, 1, len(ref.args)))
            return None
        key_ty = ref.args[0].ty
        if not isinstance(key_ty, NonVoidType):
            dm.emit(TypeUsageError(ref.args[0].ty_ref, key_ty))
            return None
        return cls(ref, key_ty)

    @override
    def accept(self, v: "SetTypeVisitor[_R]") -> _R:
        return v.visit_set_type(self)


@dataclass(frozen=True, repr=False)
class CompleterType(GenericType):
    item_ty: Type

    @property
    @override
    def signature(self):
        return f"Completer<{self.item_ty.signature}>"

    @classmethod
    def try_construct(
        cls,
        ref: "GenericTypeRefDecl",
        dm: DiagnosticsManager,
    ) -> "CompleterType | None":
        if len(ref.args) != 1:
            dm.emit(GenericArgumentsError(ref, 1, len(ref.args)))
            return None
        item_ty = ref.args[0].ty
        return cls(ref, item_ty)

    @override
    def accept(self, v: "CompleterTypeVisitor[_R]") -> _R:
        return v.visit_completer_type(self)


@dataclass(frozen=True, repr=False)
class FutureType(GenericType):
    item_ty: Type

    @property
    @override
    def signature(self):
        return f"Future<{self.item_ty.signature}>"

    @classmethod
    def try_construct(
        cls,
        ref: "GenericTypeRefDecl",
        dm: DiagnosticsManager,
    ) -> "FutureType | None":
        if len(ref.args) != 1:
            dm.emit(GenericArgumentsError(ref, 1, len(ref.args)))
            return None
        item_ty = ref.args[0].ty
        return cls(ref, item_ty)

    @override
    def accept(self, v: "FutureTypeVisitor[_R]") -> _R:
        return v.visit_future_type(self)


# Builtin Generics Map
BUILTIN_GENERICS: dict[str, type[GenericType]] = {
    "Array": ArrayType,
    "Optional": OptionalType,
    "Vector": VectorType,
    "Map": MapType,
    "Set": SetType,
    "Completer": CompleterType,
    "Future": FutureType,
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
    def accept(self, v: "UserTypeVisitor[_R]") -> _R: ...


@dataclass(frozen=True, repr=False)
class EnumType(UserType):
    decl: "EnumDecl"

    @override
    def accept(self, v: "EnumTypeVisitor[_R]") -> _R:
        return v.visit_enum_type(self)


@dataclass(frozen=True, repr=False)
class StructType(UserType):
    decl: "StructDecl"

    @override
    def accept(self, v: "StructTypeVisitor[_R]") -> _R:
        return v.visit_struct_type(self)


@dataclass(frozen=True, repr=False)
class UnionType(UserType):
    decl: "UnionDecl"

    @override
    def accept(self, v: "UnionTypeVisitor[_R]") -> _R:
        return v.visit_union_type(self)


@dataclass(frozen=True, repr=False)
class IfaceType(UserType):
    decl: "IfaceDecl"

    @override
    def accept(self, v: "IfaceTypeVisitor[_R]") -> _R:
        return v.visit_iface_type(self)
