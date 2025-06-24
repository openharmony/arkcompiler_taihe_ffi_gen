from dataclasses import dataclass

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


@dataclass
class ArrayBufferAttr(TypedAttribute[TypeRefDecl]):
    NAME = "arraybuffer"
    TARGETS = (TypeRefDecl,)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({ARRAY_ATTRIBUTE_GROUP})


@dataclass
class TypedArrayAttr(TypedAttribute[TypeRefDecl]):
    NAME = "typedarray"
    TARGETS = (TypeRefDecl,)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({ARRAY_ATTRIBUTE_GROUP})


@dataclass
class FixedArrayAttr(TypedAttribute[TypeRefDecl]):
    NAME = "fixedarray"
    TARGETS = (TypeRefDecl,)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({ARRAY_ATTRIBUTE_GROUP})


@dataclass
class ExtendsAttr(TypedAttribute[StructFieldDecl]):
    NAME = "extends"
    TARGETS = (StructFieldDecl,)


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


@dataclass
class UndefinedAttr(TypedAttribute[UnionFieldDecl]):
    NAME = "undefined"
    TARGETS = (UnionFieldDecl,)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({NULL_UNDEFINED_GROUP})


@dataclass
class ReadOnlyAttr(TypedAttribute[StructFieldDecl]):
    NAME = "readonly"
    TARGETS = (StructFieldDecl,)


@dataclass
class RecordAttr(TypedAttribute[TypeRefDecl]):
    NAME = "record"
    TARGETS = (TypeRefDecl,)


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
class GenAsyncAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "gen_async"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)

    func_name: str | None = None


@dataclass
class GenPromiseAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "gen_promise"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)

    func_name: str | None = None


FUNCTION_LIKE_ATTRIBUTE_GROUP = AttributeGroupTag()


@dataclass
class GetAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "get"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({FUNCTION_LIKE_ATTRIBUTE_GROUP})

    member_name: str | None = None


@dataclass
class SetAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "set"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({FUNCTION_LIKE_ATTRIBUTE_GROUP})

    member_name: str | None = None


@dataclass
class OnOffAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "on_off"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({FUNCTION_LIKE_ATTRIBUTE_GROUP})

    func_name: str | None = None


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
