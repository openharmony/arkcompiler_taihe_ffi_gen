from dataclasses import dataclass, field

from typing_extensions import override

from taihe.semantics.attributes import (
    AttributeGroupTag,
    CheckedAttrT,
    RepeatableAttribute,
    TypedAttribute,
)
from taihe.semantics.declarations import (
    EnumDecl,
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    ParamDecl,
    StructDecl,
    StructFieldDecl,
    TypeDecl,
    TypeRefDecl,
    UnionFieldDecl,
)
from taihe.semantics.types import (
    ArrayType,
    MapType,
    ScalarKind,
    ScalarType,
    StringType,
    StructType,
)
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import AdhocError


@dataclass
class ClazzAttr(TypedAttribute[IfaceDecl | StructDecl]):
    NAME = "class"
    TARGETS = (IfaceDecl, StructDecl)


ARRAY_ATTRIBUTE_GROUP = AttributeGroupTag()


@dataclass
class BigIntAttr(TypedAttribute[TypeRefDecl]):
    NAME = "bigint"
    TARGETS = (TypeRefDecl,)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({ARRAY_ATTRIBUTE_GROUP})

    @override
    def check_typed_context(self, parent: TypeRefDecl, dm: DiagnosticsManager) -> None:
        if not (
            isinstance(array_ty := parent.resolved_ty, ArrayType)
            and isinstance(item_ty := array_ty.item_ty, ScalarType)
            and item_ty.kind
            in (
                ScalarKind.I8,
                ScalarKind.I16,
                ScalarKind.I32,
                ScalarKind.I64,
                ScalarKind.U8,
                ScalarKind.U16,
                ScalarKind.U32,
                ScalarKind.U64,
            )
        ):
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to array types with integer items.",
                    loc=self.loc,
                )
            )

        super().check_typed_context(parent, dm)


@dataclass
class ArrayBufferAttr(TypedAttribute[TypeRefDecl]):
    NAME = "arraybuffer"
    TARGETS = (TypeRefDecl,)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({ARRAY_ATTRIBUTE_GROUP})

    @override
    def check_typed_context(self, parent: TypeRefDecl, dm: DiagnosticsManager) -> None:
        if not (
            isinstance(array_ty := parent.resolved_ty, ArrayType)
            and isinstance(item_ty := array_ty.item_ty, ScalarType)
            and item_ty.kind in (ScalarKind.I8, ScalarKind.U8)
        ):
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to array types with byte items.",
                    loc=self.loc,
                )
            )

        super().check_typed_context(parent, dm)


@dataclass
class TypedArrayAttr(TypedAttribute[TypeRefDecl]):
    NAME = "typedarray"
    TARGETS = (TypeRefDecl,)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({ARRAY_ATTRIBUTE_GROUP})

    sts_type: str = field(init=False)

    @override
    def check_typed_context(self, parent: TypeRefDecl, dm: DiagnosticsManager) -> None:
        if (
            isinstance(array_ty := parent.resolved_ty, ArrayType)
            and isinstance(item_ty := array_ty.item_ty, ScalarType)
            and (
                sts_type := {
                    ScalarKind.F32: "Float32Array",
                    ScalarKind.F64: "Float64Array",
                    ScalarKind.I8: "Int8Array",
                    ScalarKind.I16: "Int16Array",
                    ScalarKind.I32: "Int32Array",
                    ScalarKind.I64: "BigInt64Array",
                    ScalarKind.U8: "Uint8Array",
                    ScalarKind.U16: "Uint16Array",
                    ScalarKind.U32: "Uint32Array",
                    ScalarKind.U64: "BigUint64Array",
                }.get(item_ty.kind, None)
            )
            is not None
        ):
            self.sts_type = sts_type
        else:
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to integer or float array types.",
                    loc=self.loc,
                )
            )

        super().check_typed_context(parent, dm)


@dataclass
class FixedArrayAttr(TypedAttribute[TypeRefDecl]):
    NAME = "fixedarray"
    TARGETS = (TypeRefDecl,)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({ARRAY_ATTRIBUTE_GROUP})

    @override
    def check_typed_context(self, parent: TypeRefDecl, dm: DiagnosticsManager) -> None:
        if not isinstance(parent.resolved_ty, ArrayType):
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to array types.",
                    loc=self.loc,
                )
            )

        super().check_typed_context(parent, dm)


@dataclass
class RecordAttr(TypedAttribute[TypeRefDecl]):
    NAME = "record"
    TARGETS = (TypeRefDecl,)

    @override
    def check_typed_context(self, parent: TypeRefDecl, dm: DiagnosticsManager) -> None:
        if not (
            isinstance(parent.resolved_ty, MapType)
            and (
                isinstance(parent.resolved_ty.key_ty, StringType)
                or (
                    isinstance(parent.resolved_ty.key_ty, ScalarType)
                    and parent.resolved_ty.key_ty.kind
                    in (
                        ScalarKind.F32,
                        ScalarKind.F64,
                        ScalarKind.I8,
                        ScalarKind.I16,
                        ScalarKind.I32,
                        ScalarKind.I64,
                        ScalarKind.U8,
                        ScalarKind.U16,
                        ScalarKind.U32,
                        ScalarKind.U64,
                    )
                )
            )
        ):
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to map types.",
                    loc=self.loc,
                )
            )

        super().check_typed_context(parent, dm)


@dataclass
class ExtendsAttr(TypedAttribute[StructFieldDecl]):
    NAME = "extends"
    TARGETS = (StructFieldDecl,)

    @override
    def check_typed_context(
        self,
        parent: StructFieldDecl,
        dm: DiagnosticsManager,
    ) -> None:
        if not isinstance(parent.ty_ref.resolved_ty, StructType):
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to struct fields with struct types.",
                    loc=self.loc,
                )
            )

        super().check_typed_context(parent, dm)


@dataclass
class ConstAttr(TypedAttribute[EnumDecl]):
    NAME = "const"
    TARGETS = (EnumDecl,)


@dataclass
class StsThizAttr(TypedAttribute[ParamDecl]):
    NAME = "sts_this"
    TARGETS = (ParamDecl,)


@dataclass
class ExportDefaultAttr(TypedAttribute[TypeDecl | PackageDecl]):
    NAME = "sts_export_default"
    TARGETS = (TypeDecl, PackageDecl)


NULL_UNDEFINED_GROUP = AttributeGroupTag()


@dataclass
class NullAttr(TypedAttribute[UnionFieldDecl]):
    NAME = "null"
    TARGETS = (UnionFieldDecl,)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({NULL_UNDEFINED_GROUP})

    @override
    def check_typed_context(
        self, parent: UnionFieldDecl, dm: DiagnosticsManager
    ) -> None:
        if parent.ty_ref is not None:
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to union fields without a type.",
                    loc=self.loc,
                )
            )

        super().check_typed_context(parent, dm)


@dataclass
class UndefinedAttr(TypedAttribute[UnionFieldDecl]):
    NAME = "undefined"
    TARGETS = (UnionFieldDecl,)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({NULL_UNDEFINED_GROUP})

    @override
    def check_typed_context(
        self, parent: UnionFieldDecl, dm: DiagnosticsManager
    ) -> None:
        if parent.ty_ref is not None:
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to union fields without a type.",
                    loc=self.loc,
                )
            )

        super().check_typed_context(parent, dm)


@dataclass
class ReadOnlyAttr(TypedAttribute[StructFieldDecl]):
    NAME = "readonly"
    TARGETS = (StructFieldDecl,)


@dataclass
class StsInjectAttr(RepeatableAttribute[PackageDecl]):
    NAME = "sts_inject"
    TARGETS = (PackageDecl,)

    sts_code: str


@dataclass
class StsInjectIntoModuleAttr(RepeatableAttribute[PackageDecl]):
    NAME = "sts_inject_into_module"
    TARGETS = (PackageDecl,)

    sts_code: str


@dataclass
class StsInjectIntoClazzAttr(RepeatableAttribute[IfaceDecl | StructDecl]):
    NAME = "sts_inject_into_class"
    TARGETS = (IfaceDecl, StructDecl)

    sts_code: str


@dataclass
class StsInjectIntoIfaceAttr(RepeatableAttribute[IfaceDecl | StructDecl]):
    NAME = "sts_inject_into_interface"
    TARGETS = (IfaceDecl, StructDecl)

    sts_code: str


@dataclass
class StsTypeAttr(TypedAttribute[TypeRefDecl]):
    NAME = "sts_type"
    TARGETS = (TypeRefDecl,)

    type_name: str


@dataclass
class StaticAttr(TypedAttribute[GlobFuncDecl]):
    NAME = "static"
    TARGETS = (GlobFuncDecl,)

    cls_name: str


@dataclass
class CtorAttr(TypedAttribute[GlobFuncDecl]):
    NAME = "ctor"
    TARGETS = (GlobFuncDecl,)

    cls_name: str


@dataclass
class OverloadAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "overload"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)

    func_name: str


@dataclass
class GenAsyncAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "gen_async"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)

    func_name: str | None = None
    func_prefix: str = field(default="", init=False)

    @override
    def check_typed_context(
        self,
        parent: GlobFuncDecl | IfaceMethodDecl,
        dm: DiagnosticsManager,
    ) -> None:
        if self.func_name is None:
            if len(parent.name) > 4 and parent.name[-4:].lower() == "sync":
                self.func_prefix = parent.name[-4:]
            else:
                dm.emit(
                    AdhocError(
                        f"Attribute '{self.NAME}' requires the function name to be specified when the function name does not end with 'sync'.",
                        loc=self.loc,
                    )
                )

        super().check_typed_context(parent, dm)


@dataclass
class GenPromiseAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "gen_promise"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)

    func_name: str | None = None
    func_prefix: str = field(default="", init=False)

    @override
    def check_typed_context(
        self,
        parent: GlobFuncDecl | IfaceMethodDecl,
        dm: DiagnosticsManager,
    ) -> None:
        if self.func_name is None:
            if len(parent.name) > 4 and parent.name[-4:].lower() == "sync":
                self.func_prefix = parent.name[:-4]
            else:
                dm.emit(
                    AdhocError(
                        f"Attribute '{self.NAME}' requires the function name to be specified when the function name does not end with 'sync'.",
                        loc=self.loc,
                    )
                )

        super().check_typed_context(parent, dm)


FUNCTION_TYPE_ATTRIBUTE_GROUP = AttributeGroupTag()


@dataclass
class GetAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "get"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({FUNCTION_TYPE_ATTRIBUTE_GROUP})

    member_name: str | None = None
    func_suffix: str = field(default="", init=False)

    @override
    def check_typed_context(
        self,
        parent: GlobFuncDecl | IfaceMethodDecl,
        dm: DiagnosticsManager,
    ) -> None:
        if len(parent.params) != 0 or parent.return_ty_ref is None:
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to functions with no parameters and a return type.",
                    loc=self.loc,
                )
            )

        if self.member_name is None:
            if len(parent.name) > 3 and parent.name[:3].lower() == "get":
                self.func_suffix = parent.name[3:]
            else:
                dm.emit(
                    AdhocError(
                        f"Attribute '{self.NAME}' requires the property name to be specified when the function name does not start with 'get'.",
                        loc=self.loc,
                    )
                )

        super().check_typed_context(parent, dm)


@dataclass
class SetAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "set"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({FUNCTION_TYPE_ATTRIBUTE_GROUP})

    member_name: str | None = None
    func_suffix: str = field(default="", init=False)

    @override
    def check_typed_context(
        self,
        parent: GlobFuncDecl | IfaceMethodDecl,
        dm: DiagnosticsManager,
    ) -> None:
        if len(parent.params) != 1 or parent.return_ty_ref is not None:
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to functions with one parameter and no return type.",
                    loc=self.loc,
                )
            )

        if self.member_name is None:
            if len(parent.name) > 3 and parent.name[:3].lower() == "set":
                self.func_suffix = parent.name[3:]
            else:
                dm.emit(
                    AdhocError(
                        f"Attribute '{self.NAME}' requires the property name to be specified when the function name does not start with 'set'.",
                        loc=self.loc,
                    )
                )

        super().check_typed_context(parent, dm)


@dataclass
class OnOffAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "on_off"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({FUNCTION_TYPE_ATTRIBUTE_GROUP})

    type: str | None = None
    overload: str | None = field(kw_only=True, default=None)
    func_suffix: str = field(default="", init=False)

    @override
    def check_typed_context(
        self,
        parent: GlobFuncDecl | IfaceMethodDecl,
        dm: DiagnosticsManager,
    ) -> None:
        if self.overload is not None:
            if self.type is None:
                if (
                    len(parent.name) > len(self.overload)
                    and parent.name[: len(self.overload)].lower()
                    == self.overload.lower()
                ):
                    self.func_suffix = parent.name[len(self.overload) :]
                else:
                    dm.emit(
                        AdhocError(
                            f"Attribute '{self.NAME}' requires the type to be specified when the function name does not start with '{self.overload}'.",
                            loc=self.loc,
                        )
                    )
        elif len(parent.name) > 2 and parent.name[:2].lower() == "on":
            self.overload = "on"
            if self.type is None:
                self.func_suffix = parent.name[2:]
        elif len(parent.name) > 3 and parent.name[:3].lower() == "off":
            self.overload = "off"
            if self.type is None:
                self.func_suffix = parent.name[3:]
        else:
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' requires the function name to be specified when the function name does not start with 'on' or 'off'.",
                    loc=self.loc,
                )
            )

        super().check_typed_context(parent, dm)


@dataclass
class NamespaceAttr(TypedAttribute[PackageDecl]):
    NAME = "namespace"
    TARGETS = (PackageDecl,)

    module: str
    namespace: str | None = None


all_attr_types: list[CheckedAttrT] = [
    ClazzAttr,
    BigIntAttr,
    ArrayBufferAttr,
    TypedArrayAttr,
    FixedArrayAttr,
    ExtendsAttr,
    RecordAttr,
    StaticAttr,
    ConstAttr,
    StsThizAttr,
    NullAttr,
    UndefinedAttr,
    ReadOnlyAttr,
    CtorAttr,
    GenAsyncAttr,
    GenPromiseAttr,
    OverloadAttr,
    ExportDefaultAttr,
    StsInjectAttr,
    StsInjectIntoClazzAttr,
    StsInjectIntoIfaceAttr,
    StsInjectIntoModuleAttr,
    StsTypeAttr,
    GetAttr,
    SetAttr,
    OnOffAttr,
    NamespaceAttr,
]
