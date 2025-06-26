from taihe.semantics.attributes import CheckedAttrT, RepeatableAttribute, TypedAttribute
from taihe.semantics.declarations import (
    EnumDecl,
    GenericTypeRefDecl,
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


class ClazzAttr(TypedAttribute):
    NAME = "class"
    TARGETS = frozenset({IfaceDecl, StructDecl})


class BigIntAttr(TypedAttribute):
    NAME = "bigint"
    TARGETS = frozenset({GenericTypeRefDecl})


class ArrayBufferAttr(TypedAttribute):
    NAME = "arraybuffer"
    TARGETS = frozenset({GenericTypeRefDecl})


class TypedArrayAttr(TypedAttribute):
    NAME = "typedarray"
    TARGETS = frozenset({GenericTypeRefDecl})


class FixedArrayAttr(TypedAttribute):
    NAME = "fixedarray"
    TARGETS = frozenset({GenericTypeRefDecl})


class ExtendsAttr(TypedAttribute):
    NAME = "extends"
    TARGETS = frozenset({StructFieldDecl})


class ConstAttr(TypedAttribute):
    NAME = "const"
    TARGETS = frozenset({EnumDecl})


class StsThizAttr(TypedAttribute):
    NAME = "sts_this"
    TARGETS = frozenset({ParamDecl})


class ExportDefaultAttr(TypedAttribute):
    NAME = "sts_export_default"
    TARGETS = frozenset({TypeDecl, PackageDecl})


class NullAttr(TypedAttribute):
    NAME = "null"
    TARGETS = frozenset({UnionFieldDecl})


class UndefinedAttr(TypedAttribute):
    NAME = "undefined"
    TARGETS = frozenset({UnionFieldDecl})


class ReadOnlyAttr(TypedAttribute):
    NAME = "readonly"
    TARGETS = frozenset({StructFieldDecl})


class RecordAttr(TypedAttribute):
    NAME = "record"
    TARGETS = frozenset({GenericTypeRefDecl})


class StaticAttr(TypedAttribute):
    NAME = "static"
    TARGETS = frozenset({GlobFuncDecl})

    cls_name: str


class CtorAttr(TypedAttribute):
    NAME = "ctor"
    TARGETS = frozenset({GlobFuncDecl})

    cls_name: str


class OverloadAttr(TypedAttribute):
    NAME = "overload"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})

    func_name: str


class StsInjectAttr(RepeatableAttribute):
    NAME = "sts_inject"
    TARGETS = frozenset({PackageDecl})

    sts_code: str


class StsInjectIntoModuleAttr(RepeatableAttribute):
    NAME = "sts_inject_into_module"
    TARGETS = frozenset({PackageDecl})

    sts_code: str


class StsInjectIntoClazzAttr(RepeatableAttribute):
    NAME = "sts_inject_into_class"
    TARGETS = frozenset({IfaceDecl, StructDecl})

    sts_code: str


class StsInjectIntoIfaceAttr(RepeatableAttribute):
    NAME = "sts_inject_into_interface"
    TARGETS = frozenset({IfaceDecl, StructDecl})

    sts_code: str


class StsTypeAttr(TypedAttribute):
    NAME = "sts_type"
    TARGETS = frozenset({TypeRefDecl})

    type_name: str


class GenAsyncAttr(TypedAttribute):
    NAME = "gen_async"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})

    func_name: str | None = None


class GenPromiseAttr(TypedAttribute):
    NAME = "gen_promise"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})

    func_name: str | None = None


class GetAttr(TypedAttribute):
    NAME = "get"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})

    member_name: str | None = None


class SetAttr(TypedAttribute):
    NAME = "set"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})

    member_name: str | None = None


class OnOffAttr(TypedAttribute):
    NAME = "on_off"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})

    func_name: str | None = None


class NamespaceAttr(TypedAttribute):
    NAME = "namespace"
    TARGETS = frozenset({PackageDecl})

    pkg_name: str
    namespace_name: str | None = None


BigIntAttr.MUTUALLY_EXCLUSIVE = frozenset({ArrayBufferAttr, TypedArrayAttr})
ArrayBufferAttr.MUTUALLY_EXCLUSIVE = frozenset({BigIntAttr, TypedArrayAttr})
TypedArrayAttr.MUTUALLY_EXCLUSIVE = frozenset({ArrayBufferAttr, BigIntAttr})
NullAttr.MUTUALLY_EXCLUSIVE = frozenset({UndefinedAttr})
UndefinedAttr.MUTUALLY_EXCLUSIVE = frozenset({NullAttr})
GetAttr.MUTUALLY_EXCLUSIVE = frozenset({SetAttr, OnOffAttr})
SetAttr.MUTUALLY_EXCLUSIVE = frozenset({GetAttr, OnOffAttr})
OnOffAttr.MUTUALLY_EXCLUSIVE = frozenset({GetAttr, SetAttr})

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
