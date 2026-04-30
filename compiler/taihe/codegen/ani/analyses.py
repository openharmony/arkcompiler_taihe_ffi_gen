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

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field as datafield
from typing import ClassVar

from typing_extensions import override

from taihe.codegen.abi.analyses import (
    CallbackAbiInfo,
    IfaceAbiInfo,
)
from taihe.codegen.abi.writer import (
    CSourceWriter,
    render_c_string,
)
from taihe.codegen.ani.attributes import (
    ArrayBufferAttr,
    AsyncAttribute,
    BigIntAttr,
    ClassAttr,
    ConstAttr,
    ConstructorAttribute,
    CtorAttr,
    ExportDefaultAttr,
    ExtendsAttr,
    FixedArrayAttr,
    GenAsyncAttr,
    GenPromiseAttr,
    GetAttr,
    LiteralAttr,
    NamespaceAttr,
    NullAttr,
    OnOffAttr,
    OptionalAttr,
    OverloadAttr,
    PromiseAttribute,
    RecordAttr,
    RenameAttr,
    SetAttr,
    StaticAttr,
    StaticOverloadAttribute,
    StsFillAttr,
    StsInjectAttr,
    StsInjectIntoClazzAttr,
    StsInjectIntoIfaceAttr,
    StsInjectIntoModuleAttr,
    StsKeepNameAttr,
    StsLastAttr,
    StsThisAttr,
    StsTypeAttr,
    TupleAttr,
    TypedArrayAttr,
    UndefinedAttr,
    ValueArrayAttr,
)
from taihe.codegen.ani.writer import (
    ArkTsImportManager,
    DefaultNamingStrategy,
    UnchangeNamingStrategy,
    render_ets_string,
)
from taihe.codegen.cpp.analyses import (
    EnumCppInfo,
    GlobFuncCppUserInfo,
    IfaceCppInfo,
    IfaceMethodCppInfo,
    StructCppInfo,
    TypeCppInfo,
    UnionCppInfo,
)
from taihe.semantics.declarations import (
    EnumDecl,
    EnumItemDecl,
    GlobFuncDecl,
    IfaceDecl,
    IfaceExtendDecl,
    IfaceMethodDecl,
    NamedCallableDecl,
    PackageDecl,
    PackageGroup,
    ParamDecl,
    StructDecl,
    StructFieldDecl,
    UnionDecl,
    UnionFieldDecl,
)
from taihe.semantics.types import (
    ArrayType,
    CallbackType,
    CompleterType,
    EnumType,
    FutureType,
    IfaceType,
    MapType,
    NonVoidType,
    OpaqueType,
    OptionalType,
    ScalarKinds,
    ScalarType,
    SetType,
    StringType,
    StructType,
    UnionType,
    UnitType,
    VectorType,
)
from taihe.semantics.visitor import NonVoidTypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager


@dataclass
class ArkTsOutDir(AbstractAnalysis[PackageGroup]):
    module_prefix: str | None = None
    path_prefix: str | None = None

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, pg: PackageGroup) -> "ArkTsOutDir":
        raise NotImplementedError(f"{cls.__name__} should be provided by backend")


# Ani Runtime Types


@dataclass
class EtsType(ABC):
    @property
    @abstractmethod
    def sig(self) -> str: ...

    @property
    @abstractmethod
    def boxed(self) -> "EtsNonPrimitiveType": ...


@dataclass
class EtsPrimitiveType(EtsType):
    _desc_boxed: str
    _sig: str

    @property
    def sig(self) -> str:
        return self._sig

    @property
    def boxed(self) -> "EtsNonPrimitiveType":
        return EtsClassType(self._desc_boxed)


@dataclass
class EtsNonPrimitiveType(EtsType, ABC):
    @property
    @abstractmethod
    def desc(self) -> str: ...

    @property
    def boxed(self) -> "EtsNonPrimitiveType":
        return self

    @abstractmethod
    def as_union_members(self) -> Iterable["EtsUnionMemberType"]: ...


@dataclass
class EtsUnionMemberType(EtsNonPrimitiveType, ABC):
    def as_union_members(self) -> Iterable["EtsUnionMemberType"]:
        yield self


@dataclass
class EtsUnionType(EtsNonPrimitiveType):
    _members: list["EtsUnionMemberType"]

    @property
    def sig(self) -> str:
        signatures = [union_member.sig for union_member in self._members]
        signatures = sorted(set(signatures))
        signatures_str = "".join(signatures)
        return f"X{{{signatures_str}}}"

    @property
    def desc(self) -> str:
        return self.sig

    @staticmethod
    def union(*ets_types: EtsNonPrimitiveType) -> EtsNonPrimitiveType:
        members = [
            member for ets_type in ets_types for member in ets_type.as_union_members()
        ]
        if len(members) == 0:
            return EtsUndefinedType()
        if len(members) == 1:
            return members[0]
        return EtsUnionType(members)

    def as_union_members(self) -> Iterable["EtsUnionMemberType"]:
        yield from self._members


@dataclass
class EtsUndefinedType(EtsNonPrimitiveType):
    @property
    def sig(self) -> str:
        return "U"

    @property
    def desc(self) -> str:
        return "std.core.Object"

    def as_union_members(self) -> Iterable["EtsUnionMemberType"]:
        yield from ()


@dataclass
class EtsValueArrayType(EtsUnionMemberType):
    _element: EtsPrimitiveType

    @property
    def sig(self) -> str:
        return f"A{{{self._element.sig}}}"

    @property
    def desc(self) -> str:
        return self.sig


@dataclass
class EtsFixedArrayType(EtsUnionMemberType):
    _element: EtsNonPrimitiveType

    @property
    def sig(self) -> str:
        return f"A{{{self._element.sig}}}"

    @property
    def desc(self) -> str:
        return self.sig


@dataclass
class EtsClassType(EtsUnionMemberType):
    _desc: str

    @property
    def sig(self) -> str:
        return f"C{{{self._desc}}}"

    @property
    def desc(self) -> str:
        return self._desc


@dataclass
class EtsEnumType(EtsUnionMemberType):
    _desc: str

    @property
    def sig(self) -> str:
        return f"E{{{self._desc}}}"

    @property
    def desc(self) -> str:
        return self._desc


# Ani Types


@dataclass(repr=False)
class AniType:
    hint: str
    base: "AniBaseType"

    def __repr__(self) -> str:
        return f"ani_{self.hint}"

    @property
    def suffix(self) -> str:
        return self.base.hint.capitalize()


@dataclass(repr=False)
class AniBaseType(AniType):
    def __init__(self, hint: str):
        super().__init__(hint, self)


ANI_BOOLEAN = AniBaseType(hint="boolean")
ANI_FLOAT = AniBaseType(hint="float")
ANI_DOUBLE = AniBaseType(hint="double")
ANI_BYTE = AniBaseType(hint="byte")
ANI_SHORT = AniBaseType(hint="short")
ANI_INT = AniBaseType(hint="int")
ANI_LONG = AniBaseType(hint="long")
ANI_REF = AniBaseType(hint="ref")
ANI_OBJECT = AniType(hint="object", base=ANI_REF)
ANI_ARRAY = AniType(hint="array", base=ANI_REF)
ANI_FN_OBJECT = AniType(hint="fn_object", base=ANI_REF)
ANI_ENUM_ITEM = AniType(hint="enum_item", base=ANI_REF)
ANI_STRING = AniType(hint="string", base=ANI_REF)
ANI_ARRAYBUFFER = AniType(hint="arraybuffer", base=ANI_REF)
ANI_FIXEDARRAY_REF = AniType(hint="fixedarray_ref", base=ANI_REF)
ANI_FIXEDARRAY_BOOLEAN = AniType(hint="fixedarray_boolean", base=ANI_REF)
ANI_FIXEDARRAY_FLOAT = AniType(hint="fixedarray_float", base=ANI_REF)
ANI_FIXEDARRAY_DOUBLE = AniType(hint="fixedarray_double", base=ANI_REF)
ANI_FIXEDARRAY_BYTE = AniType(hint="fixedarray_byte", base=ANI_REF)
ANI_FIXEDARRAY_SHORT = AniType(hint="fixedarray_short", base=ANI_REF)
ANI_FIXEDARRAY_INT = AniType(hint="fixedarray_int", base=ANI_REF)
ANI_FIXEDARRAY_LONG = AniType(hint="fixedarray_long", base=ANI_REF)


# Ani Scopes


@dataclass(repr=False)
class AniScope:
    hint: str

    def __repr__(self) -> str:
        return f"ani_{self.hint}"

    @property
    def suffix(self) -> str:
        return self.hint.capitalize()

    @property
    def upper(self) -> str:
        return self.hint.upper()


# ArkTs Module and Namespace


@dataclass
class ArkTsModuleOrNamespace(ABC):
    scope: ClassVar[AniScope]

    is_default: bool = datafield(default=False, init=False)
    injected_codes: list[str] = datafield(default_factory=list, init=False)
    injected_globs: list[str] = datafield(default_factory=list, init=False)
    packages: list[PackageDecl] = datafield(default_factory=list, init=False)
    children: dict[str, "ArkTsNamespace"] = datafield(default_factory=dict, init=False)

    @property
    @abstractmethod
    def mod(self) -> "ArkTsModule": ...

    @property
    @abstractmethod
    def impl_desc(self) -> str: ...

    @abstractmethod
    def get_type(
        self,
        is_default: bool,
        *type_path: str,
        target: ArkTsImportManager,
    ) -> str: ...

    @property
    def descendants(self) -> Iterable["ArkTsModuleOrNamespace"]:
        yield self
        for child in self.children.values():
            yield from child.descendants

    def add_path(
        self,
        ns_parts: list[str],
        pkg: PackageDecl,
        is_default: bool,
    ) -> "ArkTsModuleOrNamespace":
        if not ns_parts:
            self.packages.append(pkg)
            self.is_default |= is_default
            return self
        ns_head, *ns_tail = ns_parts
        child = self.children.setdefault(ns_head, ArkTsNamespace(self, ns_head))
        return child.add_path(ns_tail, pkg, is_default)


@dataclass
class ArkTsModule(ArkTsModuleOrNamespace):
    parent: ArkTsOutDir
    module_name: str

    scope: ClassVar[AniScope] = AniScope("module")

    obj_drop = "_taihe_objDrop"
    obj_dup = "_taihe_objDup"
    obj_registry = "_taihe_objRegistry"

    callback_invoke = "_taihe_callbackInvoke"
    callback_inner = "_taihe_CallbackInner"
    callback_factory = "_taihe_callbackFactory"

    bigint_to_arrbuf = "_taihe_fromBigIntToArrayBuffer"
    arrbuf_to_bigint = "_taihe_fromArrayBufferToBigInt"

    BE_type = "_taihe_BusinessError"
    AC_type = "_taihe_AsyncCallback"

    async_handler_on_fulfilled = "_taihe_asyncHandlerOnFulfilled"
    async_handler_on_rejected = "_taihe_asyncHandlerOnRejected"
    async_handler_drop = "_taihe_asyncHandlerDrop"
    async_handler_registry = "_taihe_asyncHandlerRegistry"
    async_handler = "_taihe_AsyncHandler"
    completer_factory = "_taihe_completerFactory"
    future_completory = "_taihe_futureCompletory"

    @property
    def mod(self) -> "ArkTsModule":
        return self

    @property
    def impl_desc(self) -> str:
        module_prefix_desc = (
            ""
            if self.parent.module_prefix is None
            else self.parent.module_prefix.replace("/", ".") + "."
        )
        path_prefix_desc = (
            ""
            if self.parent.path_prefix is None
            else self.parent.path_prefix.replace("/", ".") + "."
        )
        module_desc = self.module_name.replace("/", ".")
        return f"{module_prefix_desc}{path_prefix_desc}{module_desc}"

    @property
    def relative_path(self) -> list[str]:
        return f"{self.module_name}.ets".split("/")

    def relative_path_to(self, base: "ArkTsModule") -> list[str]:
        if self.parent != base.parent:
            raise ValueError(
                f"Cannot compute relative path between modules in different output directories: "
                f"{self.parent} vs {base.parent}"
            )
        self_path = self.relative_path
        base_path = base.relative_path[:-1]
        while self_path and base_path and self_path[0] == base_path[0]:
            self_path.pop(0)
            base_path.pop(0)
        return [".."] * len(base_path) + self_path

    def is_same(self, other: "ArkTsModule") -> bool:
        return self.parent == other.parent and self.relative_path == other.relative_path

    def get_type(
        self,
        is_default: bool,
        *type_path: str,
        target: ArkTsImportManager,
    ) -> str:
        return target.get_type(self, is_default, *type_path)


@dataclass
class ArkTsNamespace(ArkTsModuleOrNamespace):
    parent: ArkTsModuleOrNamespace
    ns_name: str

    scope: ClassVar[AniScope] = AniScope("namespace")

    @property
    def mod(self) -> "ArkTsModule":
        return self.parent.mod

    @property
    def impl_desc(self) -> str:
        return f"{self.parent.impl_desc}.{self.ns_name}"

    def get_type(
        self,
        is_default: bool,
        *type_path: str,
        target: ArkTsImportManager,
    ) -> str:
        return self.parent.get_type(
            self.is_default,
            self.ns_name,
            *type_path,
            target=target,
        )


# ANI Analyses


class PackageGroupAniInfo(AbstractAnalysis[PackageGroup]):
    def __init__(self, am: AnalysisManager, pg: PackageGroup) -> None:
        self.mods: dict[str, ArkTsModule] = {}
        self.pkg_map: dict[PackageDecl, ArkTsModuleOrNamespace] = {}

        self.path = ArkTsOutDir.get(am, pg)

        for pkg in pg.iterate():
            ns_parts = []
            if attr := NamespaceAttr.get(pkg):
                module_str = attr.module
                if ns_name := attr.namespace:
                    ns_parts = ns_name.split(".")
            else:
                module_str = pkg.name

            is_default = ExportDefaultAttr.get(pkg) is not None

            mod = self.mods.setdefault(module_str, ArkTsModule(self.path, module_str))
            ns = self.pkg_map[pkg] = mod.add_path(ns_parts, pkg, is_default)

            for attr in StsInjectIntoModuleAttr.get_all(pkg):
                ns.injected_globs.append(attr.sts_code)

            for attr in StsInjectAttr.get_all(pkg):
                ns.injected_codes.append(attr.sts_code)

    def get_namespace(self, pkg: PackageDecl) -> ArkTsModuleOrNamespace:
        return self.pkg_map[pkg]

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, pg: PackageGroup) -> "PackageGroupAniInfo":
        return PackageGroupAniInfo(am, pg)


class PackageAniInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        self.header = f"{p.name}.ani.hpp"
        self.source = f"{p.name}.ani.cpp"

        self.cpp_ns = "::".join(p.segments)

        pg_ani_info = PackageGroupAniInfo.get(am, p.parent_group)
        self.ns = pg_ani_info.get_namespace(p)

        if (attr := StsKeepNameAttr.get(p)) and attr.option:
            self.naming = UnchangeNamingStrategy()
        else:
            self.naming = DefaultNamingStrategy()

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, p: PackageDecl) -> "PackageAniInfo":
        return PackageAniInfo(am, p)


class NamedCallableAniInfo(AbstractAnalysis[NamedCallableDecl]):
    def __init__(self, am: AnalysisManager, f: NamedCallableDecl) -> None:
        self.f = f

        naming = PackageAniInfo.get(am, f.parent_pkg).naming

        if rename_attr := RenameAttr.get(f):
            func_name = rename_attr.name
        elif rename_attr := OverloadAttr.get(f):
            func_name = rename_attr.func_name
        elif isinstance(f, GlobFuncDecl) and CtorAttr.get(f):
            func_name = ""
        else:
            func_name = naming.as_func(f.name)

        self.get_name = None
        self.set_name = None
        self.promise_name = None
        self.async_name = None
        self.norm_name = None

        self.gen_async_name = None
        self.gen_promise_name = None

        self.overload_name = None
        self.on_off_pair = None

        if get_attr := GetAttr.get(f):
            if get_attr.member_name is not None:
                get_name = get_attr.member_name
            else:
                get_name = naming.as_property(get_attr.func_suffix)
            self.get_name = get_name
        elif set_attr := SetAttr.get(f):
            if set_attr.member_name is not None:
                set_name = set_attr.member_name
            else:
                set_name = naming.as_property(set_attr.func_suffix)
            self.set_name = set_name
        elif PromiseAttribute.get(f):
            self.promise_name = func_name
        elif AsyncAttribute.get(f):
            self.async_name = func_name
        else:
            self.norm_name = func_name
            if gen_async_attr := GenAsyncAttr.get(f):
                if gen_async_attr.func_name is not None:
                    self.gen_async_name = gen_async_attr.func_name
                else:
                    self.gen_async_name = naming.as_func(gen_async_attr.func_prefix)
            if gen_promise_attr := GenPromiseAttr.get(f):
                if gen_promise_attr.func_name is not None:
                    self.gen_promise_name = gen_promise_attr.func_name
                else:
                    self.gen_promise_name = naming.as_func(gen_promise_attr.func_prefix)

        if overload_attr := StaticOverloadAttribute.get(f):
            self.overload_name = overload_attr.name

        if on_off_attr := OnOffAttr.get(f):
            if on_off_attr.type is not None:
                on_off_type = on_off_attr.type
            else:
                on_off_type = naming.as_on_off(on_off_attr.func_suffix)
            self.on_off_pair = (on_off_attr.name, on_off_type)

        self.sts_params: list[ParamDecl] = []
        for param in f.params:
            if (
                StsThisAttr.get(param)
                or StsLastAttr.get(param)
                or StsFillAttr.get(param)
            ):
                continue
            self.sts_params.append(param)

    def as_native_args(self, upper_args_sts: list[str]) -> list[str]:
        this_atg_sts = "this"
        last_arg_sts = this_atg_sts
        upper_arg_sts = iter(upper_args_sts)
        lower_args_sts: list[str] = []
        for param in self.f.params:
            if StsThisAttr.get(param):
                lower_args_sts.append(this_atg_sts)
            elif StsLastAttr.get(param):
                lower_args_sts.append(last_arg_sts)
            elif fill_attr := StsFillAttr.get(param):
                fill_arg_sts = fill_attr.content
                lower_args_sts.append(fill_arg_sts)
            else:
                lower_args_sts.append(last_arg_sts := next(upper_arg_sts))
        return lower_args_sts

    def as_normal_args(self, lower_args_sts: list[str]) -> list[str]:
        upper_args_sts: list[str] = []
        for param, lower_arg_sts in zip(self.f.params, lower_args_sts, strict=True):
            if (
                StsThisAttr.get(param)
                or StsLastAttr.get(param)
                or StsFillAttr.get(param)
            ):
                continue
            upper_args_sts.append(lower_arg_sts)
        return upper_args_sts

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: NamedCallableDecl) -> "NamedCallableAniInfo":  # fmt: skip
        return NamedCallableAniInfo(am, f)


@dataclass(frozen=True)
class IfaceThunkKey:
    iface: IfaceDecl
    method: IfaceMethodDecl


class IfaceThunkAniInfo(AbstractAnalysis[IfaceThunkKey]):
    def __init__(self, am: AnalysisManager, c: IfaceThunkKey) -> None:
        self.sts_native = f"_taihe_{c.iface.name}_{c.method.name}_native"
        iface_ani_info = IfaceAniInfo.get(am, c.iface)
        self.sts_native_base_params: list[str] = [
            f"{iface_ani_info.vtbl_ptr}: long",
            f"{iface_ani_info.data_ptr}: long",
        ]
        self.sts_native_base_args: list[str] = [
            f"this.{iface_ani_info.vtbl_ptr}",
            f"this.{iface_ani_info.data_ptr}",
        ]
        self.c_native_base_params: list[str] = [
            f"ani_long ani_vtbl_ptr",
            f"ani_long ani_data_ptr",
        ]
        iface_abi_info = IfaceAbiInfo.get(am, c.iface)
        iface_cpp_info = IfaceCppInfo.get(am, c.iface)
        iancr_cpp_info = IfaceCppInfo.get(am, c.method.parent_iface)
        method_cpp_info = IfaceMethodCppInfo.get(am, c.method)
        self.c_native_call = f"{iancr_cpp_info.as_param}({iface_cpp_info.as_param}({{reinterpret_cast<{iface_abi_info.vtable}*>(ani_vtbl_ptr), reinterpret_cast<DataBlockHead*>(ani_data_ptr)}}))->{method_cpp_info.call_name}"

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, c: IfaceThunkKey) -> "IfaceThunkAniInfo":
        return IfaceThunkAniInfo(am, c)


class IfaceMethodAniInfo(AbstractAnalysis[IfaceMethodDecl]):
    def __init__(self, am: AnalysisManager, f: IfaceMethodDecl) -> None:
        self.sts_reverse = f"_taihe_{f.parent_iface.name}_{f.name}_reverse"

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: IfaceMethodDecl) -> "IfaceMethodAniInfo":
        return IfaceMethodAniInfo(am, f)


class GlobFuncAniInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        self.sts_native = f"_taihe_{f.name}_native"
        self.sts_native_base_params: list[str] = []
        self.sts_native_base_args: list[str] = []
        self.c_native_base_params: list[str] = []
        func_cpp_user_info = GlobFuncCppUserInfo.get(am, f)
        self.c_native_call = func_cpp_user_info.full_name

        self.sts_reverse = f"_taihe_{f.name}_reverse"

        self.static_scope = None
        self.ctor_scope = None

        if old_ctor_attr := CtorAttr.get(f):
            self.ctor_scope = old_ctor_attr.cls_name
        elif ctor_attr := ConstructorAttribute.get(f):
            self.ctor_scope = ctor_attr.cls_name
        elif static_attr := StaticAttr.get(f):
            self.static_scope = static_attr.cls_name

        self.is_default = ExportDefaultAttr.get(f) is not None

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: GlobFuncDecl) -> "GlobFuncAniInfo":
        return GlobFuncAniInfo(am, f)


class EnumAniInfo(AbstractAnalysis[EnumDecl]):
    ani_type: AniType
    ets_type: EtsType

    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.ani.0.hpp"

        self.parent_ns = PackageAniInfo.get(am, d.parent_pkg).ns
        if rename_attr := RenameAttr.get(d):
            self.sts_type = rename_attr.name
        else:
            self.sts_type = d.name

        self.is_default = ExportDefaultAttr.get(d) is not None

    def sts_type_in(self, target: ArkTsImportManager):
        return self.parent_ns.get_type(
            self.is_default,
            self.sts_type,
            target=target,
        )

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, d: EnumDecl) -> "EnumAniInfo":
        if ConstAttr.get(d):
            return EnumConstAniInfo(am, d)
        return EnumObjectAniInfo(am, d)


class EnumObjectAniInfo(EnumAniInfo):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        super().__init__(am, d)

        self.type_desc = f"{self.parent_ns.impl_desc}.{self.sts_type}"
        self.ani_type = ANI_ENUM_ITEM
        self.ets_type = EtsEnumType(self.type_desc)


class EnumConstAniInfo(EnumAniInfo):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        super().__init__(am, d)

        enum_ty_ani_info = TypeAniInfo.get(am, d.ty)
        self.ani_type = enum_ty_ani_info.ani_type
        self.ets_type = enum_ty_ani_info.ets_type


class UnionAniInfo(AbstractAnalysis[UnionDecl]):
    ani_type: AniType
    ets_type: EtsType

    def __init__(self, am: AnalysisManager, d: UnionDecl) -> None:
        self.decl_header = f"{d.parent_pkg.name}.{d.name}.ani.0.hpp"
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.ani.1.hpp"

        self.parent_ns = PackageAniInfo.get(am, d.parent_pkg).ns
        if rename_attr := RenameAttr.get(d):
            self.sts_type = rename_attr.name
        else:
            self.sts_type = d.name

        self.ani_type = ANI_REF
        ets_types: list[EtsNonPrimitiveType] = []
        for field in d.fields:
            field_ani_info = TypeAniInfo.get(am, field.ty)
            ets_types.append(field_ani_info.ets_type.boxed)
        self.ets_type = EtsUnionType.union(*ets_types)

        self.sts_all_fields: list[list[UnionFieldDecl]] = []
        for field in d.fields:
            if isinstance(field_ty := field.ty, UnionType):
                inner_ani_info = UnionAniInfo.get(am, field_ty.decl)
                self.sts_all_fields.extend(
                    [field, *parts] for parts in inner_ani_info.sts_all_fields
                )
            else:
                self.sts_all_fields.append([field])

        self.is_default = ExportDefaultAttr.get(d) is not None

    def sts_type_in(self, target: ArkTsImportManager):
        return self.parent_ns.get_type(
            self.is_default,
            self.sts_type,
            target=target,
        )

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, d: UnionDecl) -> "UnionAniInfo":
        return UnionAniInfo(am, d)


class StructAniInfo(AbstractAnalysis[StructDecl]):
    ani_type: AniType
    ets_type: EtsType

    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        self.decl_header = f"{d.parent_pkg.name}.{d.name}.ani.0.hpp"
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.ani.1.hpp"

        self.parent_ns = PackageAniInfo.get(am, d.parent_pkg).ns
        if rename_attr := RenameAttr.get(d):
            self.sts_type = rename_attr.name
        else:
            self.sts_type = d.name

        self.is_default = ExportDefaultAttr.get(d) is not None

    def sts_type_in(self, target: ArkTsImportManager):
        return self.parent_ns.get_type(
            self.is_default,
            self.sts_type,
            target=target,
        )

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, d: StructDecl) -> "StructAniInfo":
        if TupleAttr.get(d):
            return StructTupleAniInfo(am, d)
        return StructObjectAniInfo(am, d)


class StructTupleAniInfo(StructAniInfo):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        super().__init__(am, d)

        self.type_desc = f"std.core.Tuple{len(d.fields)}"
        self.ani_type = ANI_OBJECT
        self.ets_type = EtsClassType(self.type_desc)


class StructObjectAniInfo(StructAniInfo):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        super().__init__(am, d)

        if ClassAttr.get(d):
            self.sts_impl = self.sts_type
        else:
            self.sts_impl = f"_taihe_{d.name}_inner"
        self.sts_factory = f"_taihe_{d.name}_factory"

        self.type_desc = f"{self.parent_ns.impl_desc}.{self.sts_type}"
        self.impl_desc = f"{self.parent_ns.impl_desc}.{self.sts_impl}"
        self.ani_type = ANI_OBJECT
        self.ets_type = EtsClassType(self.type_desc)

        self.interface_injected_codes: list[str] = []
        for iface_injected in StsInjectIntoIfaceAttr.get_all(d):
            self.interface_injected_codes.append(iface_injected.sts_code)
        self.class_injected_codes: list[str] = []
        for class_injected in StsInjectIntoClazzAttr.get_all(d):
            self.class_injected_codes.append(class_injected.sts_code)

        self.sts_class_extends: list[StructFieldDecl] = []
        self.sts_iface_extends: list[StructFieldDecl] = []
        self.sts_all_fields: list[list[StructFieldDecl]] = []
        for field in d.fields:
            if extend := ExtendsAttr.get(field):
                extend_ani_info = StructAniInfo.get(am, extend.ty.decl)
                assert isinstance(extend_ani_info, StructObjectAniInfo)
                if extend_ani_info.is_class():
                    self.sts_class_extends.append(field)
                else:
                    self.sts_iface_extends.append(field)
                self.sts_all_fields.extend(
                    [field, *parts] for parts in extend_ani_info.sts_all_fields
                )
            else:
                self.sts_all_fields.append([field])

        self.sorted_sts_all_fields = sorted(
            self.sts_all_fields,
            key=lambda parts: OptionalAttr.get(parts[-1]) is not None,
        )

        self.sts_local_fields: list[StructFieldDecl] = []
        self.sts_class_extend_fields: list[StructFieldDecl] = []
        self.sts_iface_extend_fields: list[StructFieldDecl] = []
        for parts in self.sorted_sts_all_fields:
            origin = parts[0]
            final = parts[-1]
            if extend := ExtendsAttr.get(origin):
                extend_ani_info = StructAniInfo.get(am, extend.ty.decl)
                assert isinstance(extend_ani_info, StructObjectAniInfo)
                if extend_ani_info.is_class():
                    self.sts_class_extend_fields.append(final)
                else:
                    self.sts_iface_extend_fields.append(final)
            else:
                self.sts_local_fields.append(final)

    def is_class(self):
        return self.sts_type == self.sts_impl

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, d: StructDecl) -> "StructAniInfo":
        return StructAniInfo(am, d)


class IfaceAniInfo(AbstractAnalysis[IfaceDecl]):
    ani_type: AniType
    ets_type: EtsType

    data_ptr = "_taihe_dataPtr"
    vtbl_ptr = "_taihe_vtblPtr"
    register = "_taihe_register"

    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        self.decl_header = f"{d.parent_pkg.name}.{d.name}.ani.0.hpp"
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.ani.1.hpp"

        self.parent_ns = PackageAniInfo.get(am, d.parent_pkg).ns
        if rename_attr := RenameAttr.get(d):
            self.sts_type = rename_attr.name
        else:
            self.sts_type = d.name
        if ClassAttr.get(d):
            self.sts_impl = self.sts_type
        else:
            self.sts_impl = f"_taihe_{d.name}_inner"
        self.sts_factory = f"_taihe_{d.name}_factory"

        self.type_desc = f"{self.parent_ns.impl_desc}.{self.sts_type}"
        self.impl_desc = f"{self.parent_ns.impl_desc}.{self.sts_impl}"
        self.ani_type = ANI_OBJECT
        self.ets_type = EtsClassType(self.type_desc)

        self.interface_injected_codes: list[str] = []
        for iface_injected in StsInjectIntoIfaceAttr.get_all(d):
            self.interface_injected_codes.append(iface_injected.sts_code)
        self.class_injected_codes: list[str] = []
        for class_injected in StsInjectIntoClazzAttr.get_all(d):
            self.class_injected_codes.append(class_injected.sts_code)

        self.sts_class_extends: list[IfaceExtendDecl] = []
        self.sts_iface_extends: list[IfaceExtendDecl] = []
        for extend in d.extends:
            extend_ani_info = IfaceAniInfo.get(am, extend.ty.decl)
            if extend_ani_info.is_class():
                self.sts_class_extends.append(extend)
            else:
                self.sts_iface_extends.append(extend)

        self.is_default = ExportDefaultAttr.get(d) is not None

    def is_class(self):
        return self.sts_type == self.sts_impl

    def sts_type_in(self, target: ArkTsImportManager):
        return self.parent_ns.get_type(
            self.is_default,
            self.sts_type,
            target=target,
        )

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, d: IfaceDecl) -> "IfaceAniInfo":
        return IfaceAniInfo(am, d)


class EnumFieldAniInfo(AbstractAnalysis[EnumItemDecl]):
    def __init__(self, am: AnalysisManager, d: EnumItemDecl) -> None:
        if rename_attr := RenameAttr.get(d):
            self.sts_name = rename_attr.name
        else:
            self.sts_name = d.name

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, d: EnumItemDecl) -> "EnumFieldAniInfo":
        return EnumFieldAniInfo(am, d)


class UnionFieldAniInfo(AbstractAnalysis[UnionFieldDecl]):
    def __init__(self, am: AnalysisManager, d: UnionFieldDecl) -> None:
        if rename_attr := RenameAttr.get(d):
            self.sts_name = rename_attr.name
        else:
            self.sts_name = d.name

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, d: UnionFieldDecl) -> "UnionFieldAniInfo":
        return UnionFieldAniInfo(am, d)


class StructFieldAniInfo(AbstractAnalysis[StructFieldDecl]):
    def __init__(self, am: AnalysisManager, d: StructFieldDecl) -> None:
        if rename_attr := RenameAttr.get(d):
            self.sts_name = rename_attr.name
        else:
            self.sts_name = d.name

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, d: StructFieldDecl) -> "StructFieldAniInfo":
        return StructFieldAniInfo(am, d)


class ParamAniInfo(AbstractAnalysis[ParamDecl]):
    def __init__(self, am: AnalysisManager, d: ParamDecl) -> None:
        if rename_attr := RenameAttr.get(d):
            self.sts_name = rename_attr.name
        else:
            self.sts_name = d.name

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, d: ParamDecl) -> "ParamAniInfo":
        return ParamAniInfo(am, d)


class TypeAniInfo(AbstractAnalysis[NonVoidType], ABC):
    def __init__(self, am: AnalysisManager, t: NonVoidType):
        self.cpp_info = TypeCppInfo.get(am, t)

    @property
    @abstractmethod
    def ani_type(self) -> AniType: ...

    @property
    @abstractmethod
    def ets_type(self) -> EtsType: ...

    @abstractmethod
    def sts_type_in(self, target: ArkTsImportManager) -> str: ...

    @abstractmethod
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ): ...

    @abstractmethod
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ): ...

    def gen_check_ani_ref(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, ani_ref ani_value) -> bool {{",
            f"}};",
        ):
            target.writelns(
                f"ani_boolean result = false;",
                f'env->Object_InstanceOf(static_cast<ani_object>(ani_value), TH_ANI_FIND_CLASS(env, "{self.ets_type.boxed.desc}"), &result);',
            )
            target.writelns(
                f"return result;",
            )

    def gen_into_ani_ref(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, auto&& cpp_value) -> ani_ref {{",
            f"}};",
        ):
            self.gen_into_ani(target, "into_ani_value")
            target.writelns(
                f"{self.ani_type} ani_value = into_ani_value(env, std::forward<decltype(cpp_value)>(cpp_value));",
            )
            if self.ani_type.base == ANI_REF:
                target.writelns(
                    f"ani_ref ani_boxed = ani_value;",
                    f"return ani_boxed;",
                )
            else:
                target.writelns(
                    f"ani_ref ani_boxed = {{}};",
                    f'env->Object_New(TH_ANI_FIND_CLASS(env, "{self.ets_type.boxed.desc}"), TH_ANI_FIND_CLASS_METHOD(env, "{self.ets_type.boxed.desc}", "<ctor>", "{self.ets_type.sig}:"), reinterpret_cast<ani_object*>(&ani_boxed), ani_value);',
                    f"return ani_boxed;",
                )

    def gen_from_ani_ref(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, ani_ref ani_boxed) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            if self.ani_type.base == ANI_REF:
                target.writelns(
                    f"{self.ani_type} ani_value = static_cast<{self.ani_type}>(ani_boxed);",
                )
            else:
                target.writelns(
                    f"{self.ani_type} ani_value = {{}};",
                    f'env->Object_CallMethod_{self.ani_type.suffix}(static_cast<ani_object>(ani_boxed), TH_ANI_FIND_CLASS_METHOD(env, "{self.ets_type.boxed.desc}", "to{self.ani_type.suffix}", ":{self.ets_type.sig}"), &ani_value);',
                )
            self.gen_from_ani(target, "from_ani_value")
            target.writelns(
                f"return from_ani_value(env, ani_value);",
            )

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, t: NonVoidType) -> "TypeAniInfo":
        return t.accept(TypeAniInfoDispatcher(am))


class EnumTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        enum_ani_info = EnumAniInfo.get(self.am, self.t.decl)
        return enum_ani_info.ani_type

    @property
    @override
    def ets_type(self) -> EtsType:
        enum_ani_info = EnumAniInfo.get(self.am, self.t.decl)
        return enum_ani_info.ets_type

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        enum_ani_info = EnumAniInfo.get(self.am, self.t.decl)
        return enum_ani_info.sts_type_in(target)

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        enum_ani_info = EnumAniInfo.get(self.am, self.t.decl)
        enum_cpp_info = EnumCppInfo.get(self.am, self.t.decl)
        target.add_include(enum_ani_info.impl_header)
        target.writelns(
            f"auto {name} = ::taihe::from_ani<{enum_cpp_info.as_owner}>;",
        )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        enum_ani_info = EnumAniInfo.get(self.am, self.t.decl)
        enum_cpp_info = EnumCppInfo.get(self.am, self.t.decl)
        target.add_include(enum_ani_info.impl_header)
        target.writelns(
            f"auto {name} = ::taihe::into_ani<{enum_cpp_info.as_owner}>;",
        )


class StructTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: StructType):
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        struct_ani_info = StructAniInfo.get(self.am, self.t.decl)
        return struct_ani_info.ani_type

    @property
    @override
    def ets_type(self) -> EtsType:
        struct_ani_info = StructAniInfo.get(self.am, self.t.decl)
        return struct_ani_info.ets_type

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        struct_ani_info = StructAniInfo.get(self.am, self.t.decl)
        return struct_ani_info.sts_type_in(target)

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        struct_ani_info = StructAniInfo.get(self.am, self.t.decl)
        struct_cpp_info = StructCppInfo.get(self.am, self.t.decl)
        target.add_include(struct_ani_info.impl_header)
        target.writelns(
            f"auto {name} = ::taihe::from_ani<{struct_cpp_info.as_owner}>;",
        )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        struct_ani_info = StructAniInfo.get(self.am, self.t.decl)
        struct_cpp_info = StructCppInfo.get(self.am, self.t.decl)
        target.add_include(struct_ani_info.impl_header)
        target.writelns(
            f"auto {name} = ::taihe::into_ani<{struct_cpp_info.as_owner}>;",
        )


class UnionTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: UnionType):
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        union_ani_info = UnionAniInfo.get(self.am, self.t.decl)
        return union_ani_info.ani_type

    @property
    @override
    def ets_type(self) -> EtsType:
        union_ani_info = UnionAniInfo.get(self.am, self.t.decl)
        return union_ani_info.ets_type

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        union_ani_info = UnionAniInfo.get(self.am, self.t.decl)
        return union_ani_info.sts_type_in(target)

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        union_ani_info = UnionAniInfo.get(self.am, self.t.decl)
        union_cpp_info = UnionCppInfo.get(self.am, self.t.decl)
        target.add_include(union_ani_info.impl_header)
        target.writelns(
            f"auto {name} = ::taihe::from_ani<{union_cpp_info.as_owner}>;",
        )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        union_ani_info = UnionAniInfo.get(self.am, self.t.decl)
        union_cpp_info = UnionCppInfo.get(self.am, self.t.decl)
        target.add_include(union_ani_info.impl_header)
        target.writelns(
            f"auto {name} = ::taihe::into_ani<{union_cpp_info.as_owner}>;",
        )


class IfaceTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        iface_ani_info = IfaceAniInfo.get(self.am, self.t.decl)
        return iface_ani_info.ani_type

    @property
    @override
    def ets_type(self) -> EtsType:
        iface_ani_info = IfaceAniInfo.get(self.am, self.t.decl)
        return iface_ani_info.ets_type

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        iface_ani_info = IfaceAniInfo.get(self.am, self.t.decl)
        return iface_ani_info.sts_type_in(target)

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        iface_ani_info = IfaceAniInfo.get(self.am, self.t.decl)
        iface_cpp_info = IfaceCppInfo.get(self.am, self.t.decl)
        target.add_include(iface_ani_info.impl_header)
        target.writelns(
            f"auto {name} = ::taihe::from_ani<{iface_cpp_info.as_owner}>;",
        )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        iface_ani_info = IfaceAniInfo.get(self.am, self.t.decl)
        iface_cpp_info = IfaceCppInfo.get(self.am, self.t.decl)
        target.add_include(iface_ani_info.impl_header)
        target.writelns(
            f"auto {name} = ::taihe::into_ani<{iface_cpp_info.as_owner}>;",
        )


class NullTypeAniInfo(TypeAniInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: UnitType,
        null_attr: NullAttr | None = None,
    ):
        super().__init__(am, t)

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_REF

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.Null")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        return "null"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"return {{}};",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_owner} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_ref ani_value = {{}};",
                f"env->GetNull(&ani_value);",
                f"return ani_value;",
            )

    @override
    def gen_check_ani_ref(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, ani_ref ani_value) -> bool {{",
            f"}};",
        ):
            target.writelns(
                f"ani_boolean result = false;",
                f"env->Reference_IsNull(ani_value, &result);",
                f"return result;",
            )


class UndefinedTypeAniInfo(TypeAniInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: UnitType,
        undefined_attr: UndefinedAttr,
    ):
        super().__init__(am, t)

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_REF

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsUndefinedType()

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        return "undefined"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"return {{}};",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_owner} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_ref ani_value = {{}};",
                f"env->GetUndefined(&ani_value);",
                f"return ani_value;",
            )

    @override
    def gen_check_ani_ref(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, ani_ref ani_value) -> bool {{",
            f"}};",
        ):
            target.writelns(
                f"ani_boolean result = false;",
                f"env->Reference_IsUndefined(ani_value, &result);",
                f"return result;",
            )


class StringLiteralTypeAniInfo(TypeAniInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: UnitType,
        literal_attr: LiteralAttr,
    ):
        super().__init__(am, t)
        self.value = literal_attr.value

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_STRING

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.String")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        return render_ets_string(self.value)

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"return {{}};",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_owner} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"std::string_view sv = {render_c_string(self.value)};",
                f"ani_string ani_value = {{}};",
                f"env->String_NewUTF8(sv.data(), sv.size(), &ani_value);",
                f"return ani_value;",
            )

    @override
    def gen_check_ani_ref(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, ani_ref ani_value) -> bool {{",
            f"}};",
        ):
            target.writelns(
                f"ani_boolean result = false;",
                f'env->Object_InstanceOf(static_cast<ani_object>(ani_value), TH_ANI_FIND_CLASS(env, "std.core.String"), &result);',
            )
            with target.indented(
                f"if (!result) {{",
                f"}}",
            ):
                target.writelns(
                    f"return false;",
                )
            target.writelns(
                f"std::string_view sv = {render_c_string(self.value)};",
                f"ani_size size = {{}};",
                f"env->String_GetUTF8Size(static_cast<ani_string>(ani_value), &size);",
                f"char buff[size + 1];",
                f"env->String_GetUTF8(static_cast<ani_string>(ani_value), buff, size + 1, &size);",
                f"buff[size] = '\\0';",
                f"return sv == buff;",
            )


class ScalarTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        super().__init__(am, t)
        sts_info = {
            ScalarKinds.BOOL: (ANI_BOOLEAN, "boolean", "z"),
            ScalarKinds.F32: (ANI_FLOAT, "float", "f"),
            ScalarKinds.F64: (ANI_DOUBLE, "double", "d"),
            ScalarKinds.I8: (ANI_BYTE, "byte", "b"),
            ScalarKinds.I16: (ANI_SHORT, "short", "s"),
            ScalarKinds.I32: (ANI_INT, "int", "i"),
            ScalarKinds.I64: (ANI_LONG, "long", "l"),
            ScalarKinds.U8: (ANI_BYTE, "byte", "b"),
            ScalarKinds.U16: (ANI_SHORT, "short", "s"),
            ScalarKinds.U32: (ANI_INT, "int", "i"),
            ScalarKinds.U64: (ANI_LONG, "long", "l"),
        }[t.kind]
        ani_type, sts_type, sig = sts_info
        ets_desc_boxed = f"std.core.{sts_type.capitalize()}"
        self.ani_type_inner = ani_type
        self.ets_type_inner = EtsPrimitiveType(ets_desc_boxed, sig)
        self.sts_type = sts_type

    @property
    @override
    def ani_type(self) -> AniType:
        return self.ani_type_inner

    @property
    @override
    def ets_type(self) -> EtsPrimitiveType:
        return self.ets_type_inner

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        return self.sts_type

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"return static_cast<{self.cpp_info.as_owner}>(ani_value);",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_owner} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"return static_cast<{self.ani_type}>(cpp_value);",
            )


class StringTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: StringType):
        super().__init__(am, t)

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_STRING

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.String")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        return "string"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_size size = {{}};",
                f"env->String_GetUTF8Size(ani_value, &size);",
                f"TString tstr;",
                f"char* buff = tstr_initialize(&tstr, size + 1);",
                f"env->String_GetUTF8(ani_value, buff, size + 1, &size);",
                f"buff[size] = '\\0';",
                f"tstr.length = size;",
                f"return ::taihe::string(tstr);",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_param} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_string ani_value = {{}};",
                f"env->String_NewUTF8(cpp_value.c_str(), cpp_value.size(), &ani_value);",
                f"return ani_value;",
            )


class OpaqueTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: OpaqueType) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t
        sts_type_attr = StsTypeAttr.get(self.t.ref)
        self.sts_type = sts_type_attr.type_name if sts_type_attr else "Object"

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_OBJECT

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.Object")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        return self.sts_type

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"return reinterpret_cast<{self.cpp_info.as_owner}>(ani_value);",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_owner} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"return reinterpret_cast<{self.ani_type}>(cpp_value);",
            )


class OptionalTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: OptionalType) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_REF

    @property
    @override
    def ets_type(self) -> EtsType:
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        return item_ty_ani_info.ets_type.boxed

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        item_sts_type = item_ty_ani_info.sts_type_in(target)
        return f"({item_sts_type} | undefined)"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"{self.cpp_info.as_owner} cpp_result;",
                f"ani_boolean is_undefined = {{}};",
                f"env->Reference_IsUndefined(ani_value, &is_undefined);",
            )
            with target.indented(
                f"if (!is_undefined) {{",
                f"}}",
            ):
                item_ty_ani_info.gen_from_ani_ref(target, "item_from_ani")
                target.writelns(
                    f"cpp_result.emplace(item_from_ani(env, ani_value));",
                )
            target.writelns(
                f"return cpp_result;",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_owner} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_ref ani_result = {{}};",
            )
            with target.indented(
                f"if (!cpp_value) {{",
                f"}}",
            ):
                target.writelns(
                    f"env->GetUndefined(&ani_result);",
                )
            with target.indented(
                f"else {{",
                f"}}",
            ):
                item_ty_ani_info.gen_into_ani_ref(target, "item_into_ani")
                target.writelns(
                    f"ani_result = item_into_ani(env, std::move(*cpp_value));",
                )
            target.writelns(
                f"return ani_result;",
            )


class ValueArrayTypeAniInfo(TypeAniInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: ArrayType,
        valuearray_attr: ValueArrayAttr,
    ) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t
        self.ani_type_inner = {
            ScalarKinds.BOOL: ANI_FIXEDARRAY_BOOLEAN,
            ScalarKinds.F32: ANI_FIXEDARRAY_FLOAT,
            ScalarKinds.F64: ANI_FIXEDARRAY_DOUBLE,
            ScalarKinds.I8: ANI_FIXEDARRAY_BYTE,
            ScalarKinds.I16: ANI_FIXEDARRAY_SHORT,
            ScalarKinds.I32: ANI_FIXEDARRAY_INT,
            ScalarKinds.I64: ANI_FIXEDARRAY_LONG,
            ScalarKinds.U8: ANI_FIXEDARRAY_BYTE,
            ScalarKinds.U16: ANI_FIXEDARRAY_SHORT,
            ScalarKinds.U32: ANI_FIXEDARRAY_INT,
            ScalarKinds.U64: ANI_FIXEDARRAY_LONG,
        }[valuearray_attr.item_ty.kind]

    @property
    @override
    def ani_type(self) -> AniType:
        return self.ani_type_inner

    @property
    @override
    def ets_type(self) -> EtsType:
        item_ty_ani_info = ScalarTypeAniInfo.get(self.am, self.t.item_ty)
        return EtsValueArrayType(item_ty_ani_info.ets_type)

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        item_ty_ani_info = ScalarTypeAniInfo.get(self.am, self.t.item_ty)
        item_sts_type = item_ty_ani_info.sts_type_in(target)
        return f"ValueArray<{item_sts_type}>"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_size size = {{}};",
                f"env->FixedArray_GetLength(ani_value, &size);",
                f"{item_ty_cpp_info.as_owner}* buffer = reinterpret_cast<{item_ty_cpp_info.as_owner}*>(malloc(size * sizeof({item_ty_cpp_info.as_owner})));",
                f"env->FixedArray_GetRegion_{item_ty_ani_info.ani_type.suffix}(ani_value, 0, size, reinterpret_cast<{item_ty_ani_info.ani_type}*>(buffer));",
                f"return {self.cpp_info.as_owner}(buffer, size);",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_param} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"size_t size = cpp_value.size();",
                f"{self.ani_type} ani_result = {{}};",
                f"env->FixedArray_New_{item_ty_ani_info.ani_type.suffix}(size, &ani_result);",
                f"env->FixedArray_SetRegion_{item_ty_ani_info.ani_type.suffix}(ani_result, 0, size, reinterpret_cast<{item_ty_ani_info.ani_type} const*>(cpp_value.data()));",
                f"return ani_result;",
            )


class FixedArrayTypeAniInfo(TypeAniInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: ArrayType,
        fixedarray_attr: FixedArrayAttr,
    ) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_FIXEDARRAY_REF

    @property
    @override
    def ets_type(self) -> EtsType:
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        return EtsFixedArrayType(item_ty_ani_info.ets_type.boxed)

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        item_sts_type = item_ty_ani_info.sts_type_in(target)
        return f"FixedArray<{item_sts_type}>"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_size size = {{}};",
                f"env->FixedArray_GetLength(ani_value, &size);",
                f"{item_ty_cpp_info.as_owner}* buffer = reinterpret_cast<{item_ty_cpp_info.as_owner}*>(malloc(size * sizeof({item_ty_cpp_info.as_owner})));",
            )
            with target.indented(
                f"for (size_t i = 0; i < size; i++) {{",
                f"}}",
            ):
                target.writelns(
                    f"ani_ref ani_item = {{}};",
                    f"env->FixedArray_Get_Ref(ani_value, i, reinterpret_cast<ani_ref*>(&ani_item));",
                )
                item_ty_ani_info.gen_from_ani_ref(target, "item_from_ani")
                target.writelns(
                    f"new (&buffer[i]) {item_ty_cpp_info.as_owner}(item_from_ani(env, ani_item));",
                )
            target.writelns(
                f"return {self.cpp_info.as_owner}(buffer, size);",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_owner} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"size_t size = cpp_value.size();",
                f"ani_fixedarray_ref ani_result = {{}};",
                f"ani_ref ani_init = {{}};",
                f"env->GetUndefined(&ani_init);",
                f'env->FixedArray_New_Ref(TH_ANI_FIND_CLASS(env, "{item_ty_ani_info.ets_type.boxed.desc}"), size, ani_init, &ani_result);',
            )
            with target.indented(
                f"for (size_t i = 0; i < size; i++) {{",
                f"}}",
            ):
                item_ty_ani_info.gen_into_ani_ref(target, "item_into_ani")
                target.writelns(
                    f"env->FixedArray_Set_Ref(ani_result, i, item_into_ani(env, std::move(cpp_value[i])));",
                )
            target.writelns(
                f"return ani_result;",
            )


class ArrayTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_ARRAY

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.Array")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        item_sts_type = item_ty_ani_info.sts_type_in(target)
        return f"Array<{item_sts_type}>"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_size size = {{}};",
                f"env->Array_GetLength(ani_value, &size);",
                f"{item_ty_cpp_info.as_owner}* buffer = reinterpret_cast<{item_ty_cpp_info.as_owner}*>(malloc(size * sizeof({item_ty_cpp_info.as_owner})));",
            )
            with target.indented(
                f"for (size_t i = 0; i < size; i++) {{",
                f"}}",
            ):
                target.writelns(
                    f"ani_ref ani_item = {{}};",
                    f"env->Array_Get(ani_value, i, &ani_item);",
                )
                item_ty_ani_info.gen_from_ani_ref(target, "item_from_ani")
                target.writelns(
                    f"new (&buffer[i]) {item_ty_cpp_info.as_owner}(item_from_ani(env, ani_item));",
                )
            target.writelns(
                f"return {self.cpp_info.as_owner}(buffer, size);",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_owner} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"size_t size = cpp_value.size();",
                f"ani_array ani_result = {{}};",
                f"ani_ref ani_init = {{}};",
                f"env->GetUndefined(&ani_init);",
                f"env->Array_New(size, ani_init, &ani_result);",
            )
            with target.indented(
                f"for (size_t i = 0; i < size; i++) {{",
                f"}}",
            ):
                item_ty_ani_info.gen_into_ani_ref(target, "item_into_ani")
                target.writelns(
                    f"env->Array_Set(ani_result, i, item_into_ani(env, std::move(cpp_value[i])));",
                )
            target.writelns(
                f"return ani_result;",
            )


class ArrayBufferTypeAniInfo(TypeAniInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: ArrayType,
        arraybuffer_attr: ArrayBufferAttr,
    ) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_ARRAYBUFFER

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.ArrayBuffer")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        return "ArrayBuffer"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_param} {{",
            f"}};",
        ):
            target.writelns(
                f"void* data = {{}};",
                f"ani_size length = {{}};",
                f"env->ArrayBuffer_GetInfo(ani_value, &data, &length);",
                f"return {self.cpp_info.as_param}(reinterpret_cast<{item_ty_cpp_info.as_owner}*>(data), length);",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_param} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"void* data = {{}};",
                f"ani_arraybuffer ani_result = {{}};",
                f"env->CreateArrayBuffer(cpp_value.size() * (sizeof({item_ty_cpp_info.as_owner}) / sizeof(char)), &data, &ani_result);",
                f"std::copy(cpp_value.begin(), cpp_value.end(), reinterpret_cast<{item_ty_cpp_info.as_owner}*>(data));",
                f"return ani_result;",
            )


class TypedArrayTypeAniInfo(TypeAniInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: ArrayType,
        typedarray_attr: TypedArrayAttr,
    ) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t
        self.sts_type = {
            ScalarKinds.F32: "Float32Array",
            ScalarKinds.F64: "Float64Array",
            ScalarKinds.I8: "Int8Array",
            ScalarKinds.I16: "Int16Array",
            ScalarKinds.I32: "Int32Array",
            ScalarKinds.I64: "BigInt64Array",
            ScalarKinds.U8: "Uint8Array",
            ScalarKinds.U16: "Uint16Array",
            ScalarKinds.U32: "Uint32Array",
            ScalarKinds.U64: "BigUint64Array",
        }[typedarray_attr.item_ty.kind]
        self.ets_desc = f"std.core.{self.sts_type}"

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_OBJECT

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType(self.ets_desc)

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        return self.sts_type

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_param} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_int byte_length = {{}};",
                f"ani_int byte_offset = {{}};",
                f"ani_arraybuffer arrbuf = {{}};",
            )
            assert isinstance(self.t.item_ty, ScalarType), self.t.item_ty
            if self.t.item_ty.kind.is_signed():
                target.writelns(
                    f'env->Object_GetField_Int(ani_value, TH_ANI_FIND_CLASS_FIELD(env, "{self.ets_desc}", "byteLength"), &byte_length);',
                    f'env->Object_GetField_Int(ani_value, TH_ANI_FIND_CLASS_FIELD(env, "{self.ets_desc}", "byteOffset"), &byte_offset);',
                )
            else:
                target.writelns(
                    f'env->Object_CallMethod_Int(ani_value, TH_ANI_FIND_CLASS_METHOD(env, "{self.ets_desc}", "%%get-byteLength", ":i"), &byte_length);',
                    f'env->Object_CallMethod_Int(ani_value, TH_ANI_FIND_CLASS_METHOD(env, "{self.ets_desc}", "%%get-byteOffset", ":i"), &byte_offset);',
                )
            target.writelns(
                f'env->Object_GetField_Ref(ani_value, TH_ANI_FIND_CLASS_FIELD(env, "{self.ets_desc}", "buffer"), reinterpret_cast<ani_ref*>(&arrbuf));',
                f"void* data = {{}};",
                f"ani_size length = {{}};",
                f"env->ArrayBuffer_GetInfo(arrbuf, &data, &length);",
                f"return {self.cpp_info.as_param}(reinterpret_cast<{item_ty_cpp_info.as_owner}*>(data) + byte_offset, byte_length / (sizeof({item_ty_cpp_info.as_owner}) / sizeof(char)));",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_param} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"void* data = {{}};",
                f"ani_arraybuffer arrbuf = {{}};",
                f"env->CreateArrayBuffer(cpp_value.size() * (sizeof({item_ty_cpp_info.as_owner}) / sizeof(char)), &data, &arrbuf);",
                f"std::copy(cpp_value.begin(), cpp_value.end(), reinterpret_cast<{item_ty_cpp_info.as_owner}*>(data));",
                f"ani_ref byte_length = {{}};",
                f"env->GetUndefined(&byte_length);",
                f"ani_ref byte_offset = {{}};",
                f"env->GetUndefined(&byte_offset);",
                f"ani_object ani_result = {{}};",
                f'env->Object_New(TH_ANI_FIND_CLASS(env, "{self.ets_desc}"), TH_ANI_FIND_CLASS_METHOD(env, "{self.ets_desc}", "<ctor>", "C{{std.core.ArrayBuffer}}C{{std.core.Double}}C{{std.core.Double}}:"), &ani_result, arrbuf, byte_length, byte_offset);',
                f"return ani_result;",
            )


class BigIntTypeAniInfo(TypeAniInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: ArrayType,
        bigint_attr: BigIntAttr,
    ) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_OBJECT

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.BigInt")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        return "BigInt"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        pkg_ani_info = PackageAniInfo.get(self.am, self.t.ref.parent_pkg)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_arraybuffer arrbuf = {{}};",
                f'env->Function_Call_Ref(TH_ANI_FIND_MODULE_FUNCTION(env, "{pkg_ani_info.ns.mod.impl_desc}", "{pkg_ani_info.ns.mod.bigint_to_arrbuf}", "C{{std.core.BigInt}}i:C{{std.core.ArrayBuffer}}"), reinterpret_cast<ani_ref*>(&arrbuf), ani_value, static_cast<ani_int>(sizeof({item_ty_cpp_info.as_owner}) / sizeof(char)));',
                f"void* data = {{}};",
                f"ani_size length = {{}};",
                f"env->ArrayBuffer_GetInfo(arrbuf, &data, &length);",
                f"return {self.cpp_info.as_param}(reinterpret_cast<{item_ty_cpp_info.as_owner}*>(data), length / (sizeof({item_ty_cpp_info.as_owner}) / sizeof(char)));",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
        pkg_ani_info = PackageAniInfo.get(self.am, self.t.ref.parent_pkg)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_param} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"void* data = {{}};",
                f"ani_arraybuffer arrbuf = {{}};",
                f"env->CreateArrayBuffer(cpp_value.size() * (sizeof({item_ty_cpp_info.as_owner}) / sizeof(char)), &data, &arrbuf);",
                f"std::copy(cpp_value.begin(), cpp_value.end(), reinterpret_cast<{item_ty_cpp_info.as_owner}*>(data));",
                f"ani_object ani_result = {{}};",
                f'env->Function_Call_Ref(TH_ANI_FIND_MODULE_FUNCTION(env, "{pkg_ani_info.ns.mod.impl_desc}", "{pkg_ani_info.ns.mod.arrbuf_to_bigint}", "C{{std.core.ArrayBuffer}}:C{{std.core.BigInt}}"), reinterpret_cast<ani_ref*>(&ani_result), arrbuf);',
                f"return ani_result;",
            )


class RecordTypeAniInfo(TypeAniInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: MapType,
        record_attr: RecordAttr,
    ) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_OBJECT

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.Record")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        key_ty_ani_info = TypeAniInfo.get(self.am, self.t.key_ty)
        val_ty_ani_info = TypeAniInfo.get(self.am, self.t.val_ty)
        key_sts_type = key_ty_ani_info.sts_type_in(target)
        val_sts_type = val_ty_ani_info.sts_type_in(target)
        return f"Record<{key_sts_type}, {val_sts_type}>"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        key_ty_ani_info = TypeAniInfo.get(self.am, self.t.key_ty)
        val_ty_ani_info = TypeAniInfo.get(self.am, self.t.val_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_object iter = {{}};",
                f'env->Object_CallMethod_Ref(ani_value, TH_ANI_FIND_CLASS_METHOD(env, "std.core.Record", "entries", ":C{{std.core.IterableIterator}}"), reinterpret_cast<ani_ref*>(&iter));',
                f"{self.cpp_info.as_owner} cpp_result;",
            )
            with target.indented(
                f"while (true) {{",
                f"}}",
            ):
                target.writelns(
                    f"ani_object next = {{}};",
                    f"ani_boolean done = {{}};",
                    f'env->Object_CallMethod_Ref(iter, TH_ANI_FIND_CLASS_METHOD(env, "std.core.Iterator", "next", ":C{{std.core.IteratorResult}}"), reinterpret_cast<ani_ref*>(&next));',
                    f'env->Object_GetField_Boolean(next, TH_ANI_FIND_CLASS_FIELD(env, "std.core.IteratorResult", "done"), &done);',
                )
                with target.indented(
                    f"if (done) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"break;",
                    )
                target.writelns(
                    f"ani_object item = {{}};",
                    f'env->Object_GetField_Ref(next, TH_ANI_FIND_CLASS_FIELD(env, "std.core.IteratorResult", "value"), reinterpret_cast<ani_ref*>(&item));',
                    f"ani_ref ani_key = {{}};",
                    f'env->Object_GetField_Ref(item, TH_ANI_FIND_CLASS_FIELD(env, "std.core.Tuple2", "$0"), &ani_key);',
                    f"ani_ref ani_val = {{}};",
                    f'env->Object_GetField_Ref(item, TH_ANI_FIND_CLASS_FIELD(env, "std.core.Tuple2", "$1"), &ani_val);',
                )
                key_ty_ani_info.gen_from_ani_ref(target, "key_from_ani")
                val_ty_ani_info.gen_from_ani_ref(target, "val_from_ani")
                target.writelns(
                    f"cpp_result.emplace(key_from_ani(env, ani_key), val_from_ani(env, ani_val));",
                )
            target.writelns(
                f"return cpp_result;",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        key_ty_ani_info = TypeAniInfo.get(self.am, self.t.key_ty)
        val_ty_ani_info = TypeAniInfo.get(self.am, self.t.val_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_param} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_object ani_result = {{}};",
                f'env->Object_New(TH_ANI_FIND_CLASS(env, "std.core.Record"), TH_ANI_FIND_CLASS_METHOD(env, "std.core.Record", "<ctor>", ":"), &ani_result);',
            )
            with target.indented(
                f"for (auto&& [cpp_key, cpp_val] : cpp_value) {{",
                f"}}",
            ):
                key_ty_ani_info.gen_into_ani_ref(target, "key_into_ani")
                val_ty_ani_info.gen_into_ani_ref(target, "val_into_ani")
                target.writelns(
                    f'env->Object_CallMethod_Void(ani_result, TH_ANI_FIND_CLASS_METHOD(env, "std.core.Record", "$_set", "X{{C{{std.core.BaseEnum}}C{{std.core.Numeric}}C{{std.core.String}}}}Y:"), key_into_ani(env, cpp_key), val_into_ani(env, cpp_val));',
                )
            target.writelns(
                f"return ani_result;",
            )


class MapTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_OBJECT

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.Map")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        key_ty_ani_info = TypeAniInfo.get(self.am, self.t.key_ty)
        val_ty_ani_info = TypeAniInfo.get(self.am, self.t.val_ty)
        key_sts_type = key_ty_ani_info.sts_type_in(target)
        val_sts_type = val_ty_ani_info.sts_type_in(target)
        return f"Map<{key_sts_type}, {val_sts_type}>"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        key_ty_ani_info = TypeAniInfo.get(self.am, self.t.key_ty)
        val_ty_ani_info = TypeAniInfo.get(self.am, self.t.val_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_object iter = {{}};",
                f'env->Object_CallMethod_Ref(ani_value, TH_ANI_FIND_CLASS_METHOD(env, "std.core.Map", "entries", ":C{{std.core.IterableIterator}}"), reinterpret_cast<ani_ref*>(&iter));',
                f"{self.cpp_info.as_owner} cpp_result;",
            )
            with target.indented(
                f"while (true) {{",
                f"}}",
            ):
                target.writelns(
                    f"ani_object next = {{}};",
                    f"ani_boolean done = {{}};",
                    f'env->Object_CallMethod_Ref(iter, TH_ANI_FIND_CLASS_METHOD(env, "std.core.Iterator", "next", ":C{{std.core.IteratorResult}}"), reinterpret_cast<ani_ref*>(&next));',
                    f'env->Object_GetField_Boolean(next, TH_ANI_FIND_CLASS_FIELD(env, "std.core.IteratorResult", "done"), &done);',
                )
                with target.indented(
                    f"if (done) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"break;",
                    )
                target.writelns(
                    f"ani_object item = {{}};",
                    f'env->Object_GetField_Ref(next, TH_ANI_FIND_CLASS_FIELD(env, "std.core.IteratorResult", "value"), reinterpret_cast<ani_ref*>(&item));',
                    f"ani_ref ani_key = {{}};",
                    f'env->Object_GetField_Ref(item, TH_ANI_FIND_CLASS_FIELD(env, "std.core.Tuple2", "$0"), &ani_key);',
                    f"ani_ref ani_val = {{}};",
                    f'env->Object_GetField_Ref(item, TH_ANI_FIND_CLASS_FIELD(env, "std.core.Tuple2", "$1"), &ani_val);',
                )
                key_ty_ani_info.gen_from_ani_ref(target, "key_from_ani")
                val_ty_ani_info.gen_from_ani_ref(target, "val_from_ani")
                target.writelns(
                    f"cpp_result.emplace(key_from_ani(env, ani_key), val_from_ani(env, ani_val));",
                )
            target.writelns(
                f"return cpp_result;",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        key_ty_ani_info = TypeAniInfo.get(self.am, self.t.key_ty)
        val_ty_ani_info = TypeAniInfo.get(self.am, self.t.val_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_param} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_object ani_result = {{}};",
                f'env->Object_New(TH_ANI_FIND_CLASS(env, "std.core.Map"), TH_ANI_FIND_CLASS_METHOD(env, "std.core.Map", "<ctor>", "i:"), &ani_result, 0);',
            )
            with target.indented(
                f"for (auto&& [cpp_key, cpp_val] : cpp_value) {{",
                f"}}",
            ):
                key_ty_ani_info.gen_into_ani_ref(target, "key_into_ani")
                val_ty_ani_info.gen_into_ani_ref(target, "val_into_ani")
                target.writelns(
                    f'env->Object_CallMethod_Ref(ani_result, TH_ANI_FIND_CLASS_METHOD(env, "std.core.Map", "set", "YY:C{{std.core.Map}}"), reinterpret_cast<ani_ref*>(&ani_result), key_into_ani(env, cpp_key), val_into_ani(env, cpp_val));',
                )
            target.writelns(
                f"return ani_result;",
            )


class SetTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: SetType) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_OBJECT

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.Set")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        key_ty_ani_info = TypeAniInfo.get(self.am, self.t.key_ty)
        key_sts_type = key_ty_ani_info.sts_type_in(target)
        return f"Set<{key_sts_type}>"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        key_ty_ani_info = TypeAniInfo.get(self.am, self.t.key_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_object iter = {{}};",
                f'env->Object_CallMethod_Ref(ani_value, TH_ANI_FIND_CLASS_METHOD(env, "std.core.Set", "values", ":C{{std.core.IterableIterator}}"), reinterpret_cast<ani_ref*>(&iter));',
                f"{self.cpp_info.as_owner} cpp_result;",
            )
            with target.indented(
                f"while (true) {{",
                f"}}",
            ):
                target.writelns(
                    f"ani_object next = {{}};",
                    f"ani_boolean done = {{}};",
                    f'env->Object_CallMethod_Ref(iter, TH_ANI_FIND_CLASS_METHOD(env, "std.core.Iterator", "next", ":C{{std.core.IteratorResult}}"), reinterpret_cast<ani_ref*>(&next));',
                    f'env->Object_GetField_Boolean(next, TH_ANI_FIND_CLASS_FIELD(env, "std.core.IteratorResult", "done"), &done);',
                )
                with target.indented(
                    f"if (done) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"break;",
                    )
                target.writelns(
                    f"ani_ref ani_val = {{}};",
                    f'env->Object_GetField_Ref(next, TH_ANI_FIND_CLASS_FIELD(env, "std.core.IteratorResult", "value"), &ani_val);',
                )
                key_ty_ani_info.gen_from_ani_ref(target, "val_from_ani")
                target.writelns(
                    f"cpp_result.emplace(val_from_ani(env, ani_val));",
                )
            target.writelns(
                f"return cpp_result;",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        key_ty_ani_info = TypeAniInfo.get(self.am, self.t.key_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_param} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_object ani_result = {{}};",
                f'env->Object_New(TH_ANI_FIND_CLASS(env, "std.core.Set"), TH_ANI_FIND_CLASS_METHOD(env, "std.core.Set", "<ctor>", "i:"), &ani_result, 0);',
            )
            with target.indented(
                f"for (auto&& cpp_item : cpp_value) {{",
                f"}}",
            ):
                key_ty_ani_info.gen_into_ani_ref(target, "key_into_ani")
                target.writelns(
                    f'env->Object_CallMethod_Ref(ani_result, TH_ANI_FIND_CLASS_METHOD(env, "std.core.Set", "add", "Y:C{{std.core.Set}}"), reinterpret_cast<ani_ref*>(&ani_result), key_into_ani(env, cpp_item));',
                )
            target.writelns(
                f"return ani_result;",
            )


class VectorTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: VectorType) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_ARRAY

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.Array")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.val_ty)
        item_sts_type = item_ty_ani_info.sts_type_in(target)
        return f"Array<{item_sts_type}>"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.val_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_size size = {{}};",
                f"env->Array_GetLength(ani_value, &size);",
                f"{self.cpp_info.as_owner} cpp_result;",
                f"cpp_result.reserve(size);",
            )
            with target.indented(
                f"for (size_t i = 0; i < size; i++) {{",
                f"}}",
            ):
                target.writelns(
                    f"ani_ref ani_item = {{}};",
                    f"env->Array_Get(ani_value, i, &ani_item);",
                )
                item_ty_ani_info.gen_from_ani_ref(target, "item_from_ani")
                target.writelns(
                    f"cpp_result.push_back(item_from_ani(env, ani_item));",
                )
            target.writelns(
                f"return cpp_result;",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        item_ty_ani_info = TypeAniInfo.get(self.am, self.t.val_ty)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_param} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"size_t size = cpp_value.size();",
                f"ani_array ani_result = {{}};",
                f"ani_ref ani_init = {{}};",
                f"env->GetUndefined(&ani_init);",
                f"env->Array_New(size, ani_init, &ani_result);",
            )
            with target.indented(
                f"for (size_t i = 0; i < size; i++) {{",
                f"}}",
            ):
                item_ty_ani_info.gen_into_ani_ref(target, "item_into_ani")
                target.writelns(
                    f"env->Array_Set(ani_result, i, item_into_ani(env, cpp_value[i]));",
                )
            target.writelns(
                f"return ani_result;",
            )


class CallbackTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: CallbackType) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_FN_OBJECT

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType(f"std.core.Function{len(self.t.ref.params)}")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        params = []
        for param in self.t.ref.params:
            opt = "?" if OptionalAttr.get(param) else ""
            param_ani_info = ParamAniInfo.get(self.am, param)
            param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
            params.append(
                f"{param_ani_info.sts_name}{opt}: {param_ty_ani_info.sts_type_in(target)}"
            )
        params_str = ", ".join(params)
        if isinstance(return_ty := self.t.ref.return_ty, NonVoidType):
            return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
            return_ty_sts_name = return_ty_ani_info.sts_type_in(target)
        else:
            return_ty_sts_name = "void"
        return f"(({params_str}) => {return_ty_sts_name})"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            with target.indented(
                f"struct impl_t : ::taihe::dref_guard {{",
                f"}};",
            ):
                target.writelns(
                    f"impl_t(ani_env* env, ani_ref val) : ::taihe::dref_guard(env, val) {{}}",
                )
                self.gen_invoke_operator(target)
                with target.indented(
                    f"uintptr_t getGlobalReference() const {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return reinterpret_cast<uintptr_t>(this->ref);",
                    )
            target.writelns(
                f"return ::taihe::make_holder<impl_t, {self.cpp_info.as_owner}, ::taihe::platform::ani::AniObject>(env, ani_value);",
            )

    def gen_invoke_operator(
        self,
        target: CSourceWriter,
    ):
        cb_abi_info = CallbackAbiInfo.get(self.am, self.t)
        params_cpp = []
        args_cpp = []
        for param in self.t.ref.params:
            arg_cpp = f"cpp_arg_{param.name}"
            param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
            param_ty_cpp_name = param_ty_cpp_info.as_param
            params_cpp.append(f"{param_ty_cpp_name} {arg_cpp}")
            args_cpp.append(arg_cpp)
        params_cpp_str = ", ".join(params_cpp)
        if isinstance(return_ty := self.t.ref.return_ty, NonVoidType):
            return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
            return_ty_cpp_name = return_ty_cpp_info.as_owner
        else:
            return_ty_cpp_name = "void"
        if cb_abi_info.is_noexcept:
            with target.indented(
                f"{return_ty_cpp_name} operator()({params_cpp_str}) {{",
                f"}}",
            ):
                target.writelns(
                    f"::taihe::env_guard guard;",
                    f"ani_env *env = guard.get_env();",
                )
                args_ani = []
                for param, arg_cpp in zip(self.t.ref.params, args_cpp, strict=True):
                    param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
                    param_into_ani = f"into_ani_{param.name}"
                    param_ty_ani_info.gen_into_ani_ref(target, param_into_ani)
                    args_ani.append(f"{param_into_ani}(env, {arg_cpp})")
                args_ani_str = ", ".join(args_ani)
                target.writelns(
                    f"ani_ref ani_argv[] = {{{args_ani_str}}};",
                    f"ani_ref ani_result = {{}};",
                    f"env->FunctionalObject_Call(static_cast<ani_fn_object>(this->ref), {len(self.t.ref.params)}, ani_argv, &ani_result);",
                )
                if isinstance(return_ty := self.t.ref.return_ty, NonVoidType):
                    return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
                    return_ty_ani_info.gen_from_ani_ref(target, "result_from_ani")
                    target.writelns(
                        f"return result_from_ani(env, ani_result);",
                    )
                else:
                    target.writelns(
                        f"return;",
                    )
        else:
            exp_ty_cpp_name = f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
            with target.indented(
                f"{exp_ty_cpp_name} operator()({params_cpp_str}) {{",
                f"}}",
            ):
                target.writelns(
                    f"::taihe::env_guard guard;",
                    f"ani_env *env = guard.get_env();",
                )
                args_ani = []
                for param, arg_cpp in zip(self.t.ref.params, args_cpp, strict=True):
                    param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
                    param_into_ani = f"into_ani_{param.name}"
                    param_ty_ani_info.gen_into_ani_ref(target, param_into_ani)
                    args_ani.append(f"{param_into_ani}(env, {arg_cpp})")
                args_ani_str = ", ".join(args_ani)
                target.writelns(
                    f"ani_ref ani_argv[] = {{{args_ani_str}}};",
                    f"ani_ref ani_result = {{}};",
                    f"ani_status ani_ret = env->FunctionalObject_Call(static_cast<ani_fn_object>(this->ref), {len(self.t.ref.params)}, ani_argv, &ani_result);",
                )
                with target.indented(
                    f"if (ani_ret == ANI_PENDING_ERROR) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"return ::taihe::unexpected<::taihe::error>(::taihe::catch_ani_taihe_error(env));",
                    )
                if isinstance(return_ty := self.t.ref.return_ty, NonVoidType):
                    return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
                    return_ty_ani_info.gen_from_ani_ref(target, "result_from_ani")
                    target.writelns(
                        f"return result_from_ani(env, ani_result);",
                    )
                else:
                    target.writelns(
                        f"return {{}};",
                    )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        pkg_ani_info = PackageAniInfo.get(self.am, self.t.ref.parent_pkg)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_owner} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            target.writelns(
                f"ani_fn_object ani_result = {{}};",
                f"auto wrapper = ::taihe::platform::ani::weak::AniObject(cpp_value);",
            )
            with target.indented(
                f"if (!wrapper.is_error()) {{",
                f"}}",
            ):
                target.writelns(
                    f"ani_ref global_ref = reinterpret_cast<ani_ref>(wrapper->getGlobalReference());",
                    f"ani_wref wref = {{}};",
                    f"env->WeakReference_Create(global_ref, &wref);",
                    f"ani_boolean released = {{}};",
                    f"env->WeakReference_GetReference(wref, &released, reinterpret_cast<ani_ref*>(&ani_result));",
                )
            with target.indented(
                f"else {{",
                f"}}",
            ):
                with target.indented(
                    f"struct scope_t {{",
                    f"}};",
                ):
                    self.gen_native_invoke(target, "invoke")
                target.writelns(
                    f"ani_long ani_invoke_ptr = reinterpret_cast<ani_long>(&scope_t::invoke);",
                    f"ani_long ani_vtbl_ptr = reinterpret_cast<ani_long>(cpp_value.m_handle.vtbl_ptr);",
                    f"ani_long ani_data_ptr = reinterpret_cast<ani_long>(cpp_value.m_handle.data_ptr);",
                    f"cpp_value.m_handle.data_ptr = nullptr;",
                    f'env->Function_Call_Ref(TH_ANI_FIND_MODULE_FUNCTION(env, "{pkg_ani_info.ns.mod.impl_desc}", "{pkg_ani_info.ns.mod.callback_factory}", "lll:C{{std.core.Function0}}"), reinterpret_cast<ani_ref*>(&ani_result), ani_invoke_ptr, ani_vtbl_ptr, ani_data_ptr);',
                )
            target.writelns(
                f"return ani_result;",
            )

    def gen_native_invoke(
        self,
        target: CSourceWriter,
        cpp_invoke_ptr: str,
    ):
        cb_abi_info = CallbackAbiInfo.get(self.am, self.t)
        params_ani = []
        args_ani = []
        params_ani.append("[[maybe_unused]] ani_env* env")
        params_ani.append("[[maybe_unused]] ani_long ani_vtbl_ptr")
        params_ani.append("[[maybe_unused]] ani_long ani_data_ptr")
        for i in range(16):
            arg_ani = f"ani_arg_{i}"
            param_ty_ani_name = "ani_ref"
            params_ani.append(f"[[maybe_unused]] {param_ty_ani_name} {arg_ani}")
            args_ani.append(arg_ani)
        params_ani_str = ", ".join(params_ani)
        return_ty_ani_name = "ani_ref"
        with target.indented(
            f"static {return_ty_ani_name} {cpp_invoke_ptr}({params_ani_str}) {{",
            f"}};",
        ):
            target.writelns(
                f"{self.cpp_info.as_param}::vtable_type* cpp_vtbl_ptr = reinterpret_cast<{self.cpp_info.as_param}::vtable_type*>(ani_vtbl_ptr);",
                f"DataBlockHead* cpp_data_ptr = reinterpret_cast<DataBlockHead*>(ani_data_ptr);",
                f"{self.cpp_info.as_param} cpp_func = {self.cpp_info.as_param}({{cpp_vtbl_ptr, cpp_data_ptr}});",
            )
            args_cpp = []
            for param, arg_ani in zip(self.t.ref.params, args_ani, strict=False):
                param_ty_ani_info = TypeAniInfo.get(self.am, param.ty)
                param_from_ani = f"from_ani_{param.name}"
                param_ty_ani_info.gen_from_ani_ref(target, param_from_ani)
                args_cpp.append(f"{param_from_ani}(env, {arg_ani})")
            args_cpp_str = ", ".join(args_cpp)
            lambda_invoke = f"cpp_func({args_cpp_str})"
            if isinstance(return_ty := self.t.ref.return_ty, NonVoidType):
                return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                return_ty_cpp_name = return_ty_cpp_info.as_owner
            else:
                return_ty_cpp_name = "void"
            if cb_abi_info.is_noexcept:
                if isinstance(return_ty := self.t.ref.return_ty, NonVoidType):
                    target.writelns(
                        f"{return_ty_cpp_name} cpp_result = {lambda_invoke};",
                        f"if (::taihe::has_error()) {{ return {{}}; }}",
                    )
                    return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
                    return_ty_ani_info.gen_into_ani_ref(target, "result_into_ani")
                    target.writelns(
                        f"return result_into_ani(env, std::move(cpp_result));",
                    )
                else:
                    target.writelns(
                        f"{lambda_invoke};",
                        f"if (::taihe::has_error()) {{ return {{}}; }}",
                        f"return {{}};",
                    )
            else:
                exp_ty_cpp_name = f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"  # fmt: skip
                target.writelns(
                    f"{exp_ty_cpp_name} cpp_expected = {lambda_invoke};",
                )
                if isinstance(return_ty := self.t.ref.return_ty, NonVoidType):
                    target.writelns(
                        f"if (::taihe::has_error()) {{ return {{}}; }}",
                        f"if (not cpp_expected) {{ ::taihe::throw_ani_taihe_error(env, std::move(cpp_expected.error())); return {{}}; }}",
                    )
                    return_ty_ani_info = TypeAniInfo.get(self.am, return_ty)
                    return_ty_ani_info.gen_into_ani_ref(target, "result_into_ani")
                    target.writelns(
                        f"return result_into_ani(env, std::move(cpp_expected.value()));",
                    )
                else:
                    target.writelns(
                        f"if (::taihe::has_error()) {{ return {{}}; }}",
                        f"if (not cpp_expected) {{ ::taihe::throw_ani_taihe_error(env, std::move(cpp_expected.error())); return {{}}; }}",
                        f"return {{}};",
                    )


class CompleterTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: CompleterType) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

        if isinstance(self.t.item_ty, NonVoidType):
            item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
            item_ty_cpp_name = item_ty_cpp_info.as_owner
        else:
            item_ty_cpp_name = "void"
        self.exp_ty_cpp_name = f"::taihe::expected<{item_ty_cpp_name}, ::taihe::error>"

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_FN_OBJECT

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.Function1")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        if isinstance(self.t.item_ty, NonVoidType):
            item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
            item_sts_type = item_ty_ani_info.sts_type_in(target)
        else:
            item_sts_type = "void"
        pkg_ani_info = PackageAniInfo.get(self.am, self.t.ref.parent_pkg)
        return f"{pkg_ani_info.ns.mod.AC_type}<{item_sts_type}>"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            with target.indented(
                f"struct handler_t : ::taihe::dref_guard {{",
                f"}};",
            ):
                target.writelns(
                    f"handler_t(ani_env* env, ani_ref val) : ::taihe::dref_guard(env, val) {{}}",
                )
                with target.indented(
                    f"void operator()({self.exp_ty_cpp_name}&& cpp_result) const {{",
                    f"}}",
                ):
                    target.writelns(
                        f"::taihe::env_guard guard;",
                        f"ani_env *env = guard.get_env();",
                        f"ani_ref ani_argv[2] = {{}};",
                    )
                    with target.indented(
                        f"if (cpp_result) {{",
                        f"}}",
                    ):
                        if isinstance(self.t.item_ty, NonVoidType):
                            item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
                            item_ty_ani_info.gen_into_ani_ref(target, "result_into_ani")
                            target.writelns(
                                f"ani_ref ani_result = result_into_ani(env, std::move(cpp_result.value()));",
                            )
                        else:
                            target.writelns(
                                f"ani_ref ani_result = {{}};",
                                f"env->GetUndefined(&ani_result);",
                            )
                        target.writelns(
                            f"ani_argv[1] = ani_result;",
                            f"env->GetNull(&ani_argv[0]);",
                        )
                    with target.indented(
                        f"else {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"ani_argv[0] = ::taihe::into_ani_taihe_error(env, std::move(cpp_result.error()));",
                            f"env->GetUndefined(&ani_argv[1]);",
                        )
                    target.writelns(
                        f"ani_ref ani_dummy = {{}};",
                        f"env->FunctionalObject_Call(static_cast<ani_fn_object>(this->ref), 2, ani_argv, &ani_dummy);",
                    )
            target.writelns(
                f"auto [cpp_result, cpp_future] = ::taihe::make_async_pair<{self.exp_ty_cpp_name}>();",
                f"std::move(cpp_future).on_complete<handler_t>(env, ani_value);",
                f"return cpp_result;",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        pkg_ani_info = PackageAniInfo.get(self.am, self.t.ref.parent_pkg)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_owner} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            with target.indented(
                f"struct scope_t {{",
                f"}};",
            ):
                self.gen_async_on_fulfilled(target, "on_fulfilled")
                self.gen_async_on_rejected(target, "on_rejected")
                self.gen_async_free(target, "free")
            target.writelns(
                f"ani_long ani_on_fulfilled_ptr = reinterpret_cast<ani_long>(&scope_t::on_fulfilled);",
                f"ani_long ani_on_rejected_ptr = reinterpret_cast<ani_long>(&scope_t::on_rejected);",
                f"ani_long ani_free_ptr = reinterpret_cast<ani_long>(&scope_t::free);",
                f"ani_long ani_context_ptr = reinterpret_cast<ani_long>(cpp_value.m_ctx);",
                f"cpp_value.m_ctx = nullptr;",
                f"ani_fn_object ani_result = {{}};",
                f'env->Function_Call_Ref(TH_ANI_FIND_MODULE_FUNCTION(env, "{pkg_ani_info.ns.mod.impl_desc}", "{pkg_ani_info.ns.mod.completer_factory}", "llll:C{{std.core.Function2}}"), reinterpret_cast<ani_ref*>(&ani_result), ani_on_fulfilled_ptr, ani_on_rejected_ptr, ani_free_ptr, ani_context_ptr);',
                f"return ani_result;",
            )

    def gen_async_on_fulfilled(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"static void {name}([[maybe_unused]] ani_env* env, ani_long ani_context_ptr, ani_ref data) {{",
            f"}};",
        ):
            target.writelns(
                f"auto ctx = reinterpret_cast<::taihe::async_context<{self.exp_ty_cpp_name}>*>(ani_context_ptr);",
            )
            if isinstance(self.t.item_ty, NonVoidType):
                item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
                item_ty_ani_info.gen_from_ani_ref(target, "result_from_ani")
                target.writelns(
                    f"ctx->emplace_result(result_from_ani(env, data));",
                )
            else:
                target.writelns(
                    f"ctx->emplace_result();",
                )

    def gen_async_on_rejected(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"static void {name}([[maybe_unused]] ani_env* env, ani_long ani_context_ptr, ani_ref err) {{",
            f"}};",
        ):
            target.writelns(
                f"auto ctx = reinterpret_cast<::taihe::async_context<{self.exp_ty_cpp_name}>*>(ani_context_ptr);",
                f"ctx->emplace_result(::taihe::unexpected<::taihe::error>(::taihe::from_ani_taihe_error(env, static_cast<ani_error>(err))));",
            )

    def gen_async_free(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"static void {name}([[maybe_unused]] ani_env* env, ani_long ani_context_ptr) {{",
            f"}};",
        ):
            target.writelns(
                f"auto ctx = reinterpret_cast<::taihe::async_context<{self.exp_ty_cpp_name}>*>(ani_context_ptr);",
                f"if (ctx->dec_ref()) {{ delete ctx; }}",
            )


class FutureTypeAniInfo(TypeAniInfo):
    def __init__(self, am: AnalysisManager, t: FutureType) -> None:
        super().__init__(am, t)
        self.am = am
        self.t = t

        if isinstance(self.t.item_ty, NonVoidType):
            item_ty_cpp_info = TypeCppInfo.get(self.am, self.t.item_ty)
            item_ty_cpp_name = item_ty_cpp_info.as_owner
        else:
            item_ty_cpp_name = "void"
        self.exp_ty_cpp_name = f"::taihe::expected<{item_ty_cpp_name}, ::taihe::error>"

    @property
    @override
    def ani_type(self) -> AniType:
        return ANI_OBJECT

    @property
    @override
    def ets_type(self) -> EtsType:
        return EtsClassType("std.core.Promise")

    @override
    def sts_type_in(self, target: ArkTsImportManager) -> str:
        if isinstance(self.t.item_ty, NonVoidType):
            item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
            item_sts_type = item_ty_ani_info.sts_type_in(target)
        else:
            item_sts_type = "void"
        return f"Promise<{item_sts_type}>"

    @override
    def gen_from_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        pkg_ani_info = PackageAniInfo.get(self.am, self.t.ref.parent_pkg)
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.ani_type} ani_value) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            with target.indented(
                f"struct scope_t {{",
                f"}};",
            ):
                self.gen_async_on_fulfilled(target, "on_fulfilled")
                self.gen_async_on_rejected(target, "on_rejected")
                self.gen_async_free(target, "free")
            target.writelns(
                f"auto [cpp_completer, cpp_result] = ::taihe::make_async_pair<{self.exp_ty_cpp_name}>();",
                f"ani_long ani_on_fulfilled_ptr = reinterpret_cast<ani_long>(&scope_t::on_fulfilled);",
                f"ani_long ani_on_rejected_ptr = reinterpret_cast<ani_long>(&scope_t::on_rejected);",
                f"ani_long ani_free_ptr = reinterpret_cast<ani_long>(&scope_t::free);",
                f"ani_long ani_context_ptr = reinterpret_cast<ani_long>(cpp_completer.m_ctx);",
                f"cpp_completer.m_ctx = nullptr;",
                f'env->Function_Call_Void(TH_ANI_FIND_MODULE_FUNCTION(env, "{pkg_ani_info.ns.mod.impl_desc}", "{pkg_ani_info.ns.mod.future_completory}", "llllC{{std.core.Promise}}:"), ani_on_fulfilled_ptr, ani_on_rejected_ptr, ani_free_ptr, ani_context_ptr, ani_value);',
                f"return cpp_result;",
            )

    def gen_async_on_fulfilled(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"static void {name}([[maybe_unused]] ani_env* env, ani_long ani_context_ptr, ani_ref data) {{",
            f"}};",
        ):
            target.writelns(
                f"auto ctx = reinterpret_cast<::taihe::async_context<{self.exp_ty_cpp_name}>*>(ani_context_ptr);",
            )
            if isinstance(self.t.item_ty, NonVoidType):
                item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
                item_ty_ani_info.gen_from_ani_ref(target, "result_from_ani")
                target.writelns(
                    f"ctx->emplace_result(result_from_ani(env, data));",
                )
            else:
                target.writelns(
                    f"ctx->emplace_result();",
                )

    def gen_async_on_rejected(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"static void {name}([[maybe_unused]] ani_env* env, ani_long ani_context_ptr, ani_ref err) {{",
            f"}};",
        ):
            target.writelns(
                f"auto ctx = reinterpret_cast<::taihe::async_context<{self.exp_ty_cpp_name}>*>(ani_context_ptr);",
                f"ctx->emplace_result(::taihe::unexpected<::taihe::error>(::taihe::from_ani_taihe_error(env, static_cast<ani_error>(err))));",
            )

    def gen_async_free(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"static void {name}([[maybe_unused]] ani_env* env, ani_long ani_context_ptr) {{",
            f"}};",
        ):
            target.writelns(
                f"auto ctx = reinterpret_cast<::taihe::async_context<{self.exp_ty_cpp_name}>*>(ani_context_ptr);",
                f"if (ctx->dec_ref()) {{ delete ctx; }}",
            )

    @override
    def gen_into_ani(
        self,
        target: CSourceWriter,
        name: str,
    ):
        with target.indented(
            f"auto {name} = [](ani_env* env, {self.cpp_info.as_owner} cpp_value) -> {self.ani_type} {{",
            f"}};",
        ):
            with target.indented(
                f"struct handler_t : ::taihe::dref_guard {{",
                f"}};",
            ):
                target.writelns(
                    f"handler_t(ani_env* env, ani_ref val) : ::taihe::dref_guard(env, val) {{}}",
                )
                with target.indented(
                    f"void operator()({self.exp_ty_cpp_name}&& cpp_result) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"::taihe::env_guard guard;",
                        f"ani_env *env = guard.get_env();",
                    )
                    with target.indented(
                        f"if (cpp_result) {{",
                        f"}}",
                    ):
                        if isinstance(self.t.item_ty, NonVoidType):
                            item_ty_ani_info = TypeAniInfo.get(self.am, self.t.item_ty)
                            item_ty_ani_info.gen_into_ani_ref(target, "result_into_ani")
                            target.writelns(
                                f"ani_ref ani_result = result_into_ani(env, std::move(cpp_result.value()));",
                            )
                        else:
                            target.writelns(
                                f"ani_ref ani_result = {{}};",
                                f"env->GetUndefined(&ani_result);",
                            )
                        target.writelns(
                            f'env->Object_CallMethod_Void(static_cast<ani_object>(this->ref), TH_ANI_FIND_CLASS_METHOD(env, "std.core.Promise", "resolveImpl", nullptr), ani_result, false);',
                        )
                    with target.indented(
                        f"else {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"ani_error ani_err = ::taihe::into_ani_taihe_error(env, std::move(cpp_result.error()));",
                            f'env->Object_CallMethod_Void(static_cast<ani_object>(this->ref), TH_ANI_FIND_CLASS_METHOD(env, "std.core.Promise", "rejectImpl", nullptr), ani_err, false);',
                        )
            target.writelns(
                f"ani_object ani_result = {{}};",
                f'env->Object_New(TH_ANI_FIND_CLASS(env, "std.core.Promise"), TH_ANI_FIND_CLASS_METHOD(env, "std.core.Promise", "<ctor>", ":"), &ani_result);',
                f"std::move(cpp_value).on_complete<handler_t>(env, ani_result);",
                f"return ani_result;",
            )


class TypeAniInfoDispatcher(NonVoidTypeVisitor[TypeAniInfo]):
    def __init__(self, am: AnalysisManager):
        self.am = am

    @override
    def visit_enum_type(self, t: EnumType) -> TypeAniInfo:
        return EnumTypeAniInfo(self.am, t)

    @override
    def visit_union_type(self, t: UnionType) -> TypeAniInfo:
        return UnionTypeAniInfo(self.am, t)

    @override
    def visit_struct_type(self, t: StructType) -> TypeAniInfo:
        return StructTypeAniInfo(self.am, t)

    @override
    def visit_iface_type(self, t: IfaceType) -> TypeAniInfo:
        return IfaceTypeAniInfo(self.am, t)

    @override
    def visit_opaque_type(self, t: OpaqueType) -> TypeAniInfo:
        return OpaqueTypeAniInfo(self.am, t)

    @override
    def visit_unit_type(self, t: UnitType) -> TypeAniInfo:
        if literal_attr := LiteralAttr.get(t.ref):
            return StringLiteralTypeAniInfo(self.am, t, literal_attr)
        if undefined_attr := UndefinedAttr.get(t.ref):
            return UndefinedTypeAniInfo(self.am, t, undefined_attr)
        if null_attr := NullAttr.get(t.ref):
            return NullTypeAniInfo(self.am, t, null_attr)
        # TODO: compatible with older version, to be removed in future
        if isinstance(t.ref.parent_type_holder, StructFieldDecl | UnionFieldDecl):
            if undefined_attr := UndefinedAttr.get(t.ref.parent_type_holder):
                return UndefinedTypeAniInfo(self.am, t, undefined_attr)
            if null_attr := NullAttr.get(t.ref.parent_type_holder):
                return NullTypeAniInfo(self.am, t, null_attr)
        return NullTypeAniInfo(self.am, t)

    @override
    def visit_scalar_type(self, t: ScalarType) -> TypeAniInfo:
        return ScalarTypeAniInfo(self.am, t)

    @override
    def visit_string_type(self, t: StringType) -> TypeAniInfo:
        return StringTypeAniInfo(self.am, t)

    @override
    def visit_array_type(self, t: ArrayType) -> TypeAniInfo:
        if bigint_attr := BigIntAttr.get(t.ref):
            return BigIntTypeAniInfo(self.am, t, bigint_attr)
        if typedarray_attr := TypedArrayAttr.get(t.ref):
            return TypedArrayTypeAniInfo(self.am, t, typedarray_attr)
        if arraybuffer_attr := ArrayBufferAttr.get(t.ref):
            return ArrayBufferTypeAniInfo(self.am, t, arraybuffer_attr)
        if fixedarray_attr := FixedArrayAttr.get(t.ref):
            return FixedArrayTypeAniInfo(self.am, t, fixedarray_attr)
        if valuearray_attr := ValueArrayAttr.get(t.ref):
            return ValueArrayTypeAniInfo(self.am, t, valuearray_attr)
        return ArrayTypeAniInfo(self.am, t)

    @override
    def visit_optional_type(self, t: OptionalType) -> TypeAniInfo:
        return OptionalTypeAniInfo(self.am, t)

    @override
    def visit_map_type(self, t: MapType) -> TypeAniInfo:
        if record_attr := RecordAttr.get(t.ref):
            return RecordTypeAniInfo(self.am, t, record_attr)
        return MapTypeAniInfo(self.am, t)

    @override
    def visit_set_type(self, t: SetType) -> TypeAniInfo:
        return SetTypeAniInfo(self.am, t)

    @override
    def visit_vector_type(self, t: VectorType) -> TypeAniInfo:
        return VectorTypeAniInfo(self.am, t)

    @override
    def visit_completer_type(self, t: CompleterType) -> TypeAniInfo:
        return CompleterTypeAniInfo(self.am, t)

    @override
    def visit_future_type(self, t: FutureType) -> TypeAniInfo:
        return FutureTypeAniInfo(self.am, t)

    @override
    def visit_callback_type(self, t: CallbackType) -> TypeAniInfo:
        return CallbackTypeAniInfo(self.am, t)
