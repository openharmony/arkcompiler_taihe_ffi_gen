from dataclasses import dataclass

from taihe.semantics.attributes import (
    AttributeGroupTag,
    CheckedAttrT,
    RepeatableAttribute,
    TypedAttribute,
)
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


@dataclass
class ClazzAttr(TypedAttribute):
    NAME = "class"
    TARGETS = frozenset({IfaceDecl, StructDecl})


ARRAY_ATTRIBUTE_GROUP = AttributeGroupTag()


@dataclass
class BigIntAttr(TypedAttribute):
    NAME = "bigint"
    TARGETS = frozenset({GenericTypeRefDecl})
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({ARRAY_ATTRIBUTE_GROUP})


@dataclass
class ArrayBufferAttr(TypedAttribute):
    NAME = "arraybuffer"
    TARGETS = frozenset({GenericTypeRefDecl})
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({ARRAY_ATTRIBUTE_GROUP})


@dataclass
class TypedArrayAttr(TypedAttribute):
    NAME = "typedarray"
    TARGETS = frozenset({GenericTypeRefDecl})
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({ARRAY_ATTRIBUTE_GROUP})


@dataclass
class FixedArrayAttr(TypedAttribute):
    NAME = "fixedarray"
    TARGETS = frozenset({GenericTypeRefDecl})
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({ARRAY_ATTRIBUTE_GROUP})


@dataclass
class ExtendsAttr(TypedAttribute):
    NAME = "extends"
    TARGETS = frozenset({StructFieldDecl})


@dataclass
class ConstAttr(TypedAttribute):
    NAME = "const"
    TARGETS = frozenset({EnumDecl})


@dataclass
class StsThizAttr(TypedAttribute):
    NAME = "sts_this"
    TARGETS = frozenset({ParamDecl})


@dataclass
class ExportDefaultAttr(TypedAttribute):
    NAME = "sts_export_default"
    TARGETS = frozenset({TypeDecl, PackageDecl})


NULL_UNDEFINED_GROUP = AttributeGroupTag()


@dataclass
class NullAttr(TypedAttribute):
    NAME = "null"
    TARGETS = frozenset({UnionFieldDecl})
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({NULL_UNDEFINED_GROUP})


@dataclass
class UndefinedAttr(TypedAttribute):
    NAME = "undefined"
    TARGETS = frozenset({UnionFieldDecl})
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({NULL_UNDEFINED_GROUP})


@dataclass
class ReadOnlyAttr(TypedAttribute):
    NAME = "readonly"
    TARGETS = frozenset({StructFieldDecl})


@dataclass
class RecordAttr(TypedAttribute):
    NAME = "record"
    TARGETS = frozenset({GenericTypeRefDecl})


@dataclass
class StaticAttr(TypedAttribute):
    NAME = "static"
    TARGETS = frozenset({GlobFuncDecl})

    cls_name: str


@dataclass
class CtorAttr(TypedAttribute):
    NAME = "ctor"
    TARGETS = frozenset({GlobFuncDecl})

    cls_name: str


@dataclass
class OverloadAttr(TypedAttribute):
    NAME = "overload"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})

    func_name: str


@dataclass
class StsInjectAttr(RepeatableAttribute):
    NAME = "sts_inject"
    TARGETS = frozenset({PackageDecl})

    sts_code: str


@dataclass
class StsInjectIntoModuleAttr(RepeatableAttribute):
    NAME = "sts_inject_into_module"
    TARGETS = frozenset({PackageDecl})

    sts_code: str


@dataclass
class StsInjectIntoClazzAttr(RepeatableAttribute):
    NAME = "sts_inject_into_class"
    TARGETS = frozenset({IfaceDecl, StructDecl})

    sts_code: str


@dataclass
class StsInjectIntoIfaceAttr(RepeatableAttribute):
    NAME = "sts_inject_into_interface"
    TARGETS = frozenset({IfaceDecl, StructDecl})

    sts_code: str


@dataclass
class StsTypeAttr(TypedAttribute):
    NAME = "sts_type"
    TARGETS = frozenset({TypeRefDecl})

    type_name: str


@dataclass
class GenAsyncAttr(TypedAttribute):
    NAME = "gen_async"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})

    func_name: str | None = None


@dataclass
class GenPromiseAttr(TypedAttribute):
    NAME = "gen_promise"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})

    func_name: str | None = None


FUNCTION_LIKE_ATTRIBUTE_GROUP = AttributeGroupTag()


@dataclass
class GetAttr(TypedAttribute):
    NAME = "get"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({FUNCTION_LIKE_ATTRIBUTE_GROUP})

    member_name: str | None = None


@dataclass
class SetAttr(TypedAttribute):
    NAME = "set"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({FUNCTION_LIKE_ATTRIBUTE_GROUP})

    member_name: str | None = None


@dataclass
class OnOffAttr(TypedAttribute):
    NAME = "on_off"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({FUNCTION_LIKE_ATTRIBUTE_GROUP})

    func_name: str | None = None


@dataclass
class NamespaceAttr(TypedAttribute):
    NAME = "namespace"
    TARGETS = frozenset({PackageDecl})

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
