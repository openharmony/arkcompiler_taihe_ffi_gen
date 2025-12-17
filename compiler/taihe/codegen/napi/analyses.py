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

from abc import ABCMeta, abstractmethod
from collections import defaultdict

from typing_extensions import override

from taihe.codegen.abi.analyses import IfaceAbiInfo, StructAbiInfo
from taihe.codegen.abi.mangle import DeclKind, encode
from taihe.codegen.abi.writer import CSourceWriter
from taihe.codegen.ani.attributes import (
    ArrayBufferAttr,
    AsyncAttribute,
    BigIntAttr,
    ClassAttr,
    ConstAttr,
    CtorAttr,
    ExtendsAttr,
    GetAttr,
    NamespaceAttr,
    PromiseAttribute,
    RecordAttr,
    SetAttr,
    StaticAttr,
    TypedArrayAttr,
    UndefinedAttr,
)
from taihe.codegen.cpp.analyses import (
    EnumCppInfo,
    TypeCppInfo,
)
from taihe.codegen.napi.attributes import (
    DtsInjectAttr,
    DtsInjectIntoClazzAttr,
    DtsInjectIntoIfaceAttr,
    DtsInjectIntoModuleAttr,
    DtsTypeAttr,
    TsInjectAttr,
    TsInjectIntoClazzAttr,
    TsInjectIntoIfaceAttr,
    TsInjectIntoModuleAttr,
)
from taihe.codegen.napi.writer import DtsWriter
from taihe.semantics.declarations import (
    EnumDecl,
    GlobFuncDecl,
    IfaceDecl,
    IfaceExtendDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
    StructDecl,
    StructFieldDecl,
    UnionDecl,
    UnionFieldDecl,
)
from taihe.semantics.types import (
    ArrayType,
    CallbackType,
    EnumType,
    IfaceType,
    MapType,
    NonVoidType,
    OpaqueType,
    OptionalType,
    ScalarKind,
    ScalarType,
    StringType,
    StructType,
    UnionType,
    UnitType,
)
from taihe.semantics.visitor import NonVoidTypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager


def get_mangled_func_name(
    pkg: PackageDecl,
    func: GlobFuncDecl,
) -> str:
    segments = [*pkg.segments, func.name]
    return encode(segments, DeclKind.NAPI_FUNC)


def get_mangled_method_name(
    iface: IfaceDecl,
    method: IfaceMethodDecl,
) -> str:
    segments = [
        *iface.parent_pkg.segments,
        iface.name,
        method.name,
    ]
    return encode(segments, DeclKind.NAPI_FUNC)


class Namespace:
    def __init__(self, name: str, parent: "Namespace | None" = None) -> None:
        self.name = name
        self.parent = parent

        self.children: dict[str, Namespace] = {}
        self.packages: list[PackageDecl] = []
        self.ts_injected_heads: list[str] = []
        self.ts_injected_codes: list[str] = []

        self.dts_injected_heads: list[str] = []
        self.dts_injected_codes: list[str] = []

        if parent is None:
            self.module = self
            self.path: list[str] = []
        else:
            self.module = parent.module
            self.path: list[str] = [*parent.path, name]

    def add_path(
        self,
        path: list[str],
        pkg: PackageDecl,
    ) -> "Namespace":
        if not path:
            self.packages.append(pkg)
            return self
        head, *tail = path
        child = self.children.setdefault(head, Namespace(head, self))
        return child.add_path(tail, pkg)

    def get_member(
        self,
        target: DtsWriter,
        dts_type_name: str,
    ) -> str:
        if self.parent is None:
            scope_name = "__" + "".join(c if c.isalnum() else "_" for c in self.name)
            target.add_import_module(f"./{self.name}", scope_name)
        else:
            scope_name = self.parent.get_member(target, self.name)
        return f"{scope_name}.{dts_type_name}"


class PackageGroupNapiInfo(AbstractAnalysis[PackageGroup]):
    def __init__(self, am: AnalysisManager, pg: PackageGroup) -> None:
        self.am = am
        self.pg = pg

        self.module_dict: dict[str, Namespace] = {}
        self.package_map: dict[PackageDecl, Namespace] = {}

        for pkg in pg.packages:
            path = []
            if attr := NamespaceAttr.get(pkg):
                module_name = attr.module
                if ns := attr.namespace:
                    path = ns.split(".")
            else:
                module_name = pkg.name

            mod = self.module_dict.setdefault(module_name, Namespace(module_name))
            ns = self.package_map[pkg] = mod.add_path(path, pkg)

            for attr in TsInjectIntoModuleAttr.get_all(pkg):
                mod.ts_injected_heads.append(attr.ts_code)

            for attr in TsInjectAttr.get_all(pkg):
                ns.ts_injected_codes.append(attr.ts_code)

            for attr in DtsInjectIntoModuleAttr.get_all(pkg):
                mod.dts_injected_heads.append(attr.dts_code)

            for attr in DtsInjectAttr.get_all(pkg):
                ns.dts_injected_codes.append(attr.dts_code)

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, pg: PackageGroup) -> "PackageGroupNapiInfo":
        return PackageGroupNapiInfo(am, pg)

    def get_namespace(self, pkg: PackageDecl) -> Namespace:
        return self.package_map[pkg]


class PackageNapiInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        self.am = am
        self.name = p.name
        self.scope_name = "__" + "".join(c if c.isalnum() else "_" for c in self.name)
        self.source = f"{p.name}.napi.cpp"
        self.header = f"{p.name}.napi.h"
        self.ts_decl = f"{p.name}.d.ts"
        self.cpp_ns = "::".join(p.segments)
        self.init_func = f"Init{self.scope_name}"
        self.macro_name = f"{self.scope_name}_NAPI_H"
        pg_napi_info = PackageGroupNapiInfo.get(am, p.parent_group)
        self.ns = pg_napi_info.get_namespace(p)

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, p: PackageDecl) -> "PackageNapiInfo":
        return PackageNapiInfo(am, p)

    def get_dts_type_name(self, target: DtsWriter, dts_type_name: str):
        target.add_import_module(f"./{self.name}", self.scope_name)
        return f"{self.scope_name}.{dts_type_name}"


class StructNapiInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        segments = [*d.parent_pkg.segments, d.name]
        self.pkg_napi_info = PackageNapiInfo.get(am, d.parent_pkg)
        self.from_napi_func_name = encode(segments, DeclKind.FROM_NAPI)
        self.into_napi_func_name = encode(segments, DeclKind.INTO_NAPI)
        self.constructor_func_name = encode(segments, DeclKind.CONSTRUCTOR)
        self.create_func_name = encode(segments, DeclKind.CREATE)
        self.decl_header = f"{d.parent_pkg.name}.{d.name}.napi.decl.h"
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.napi.impl.h"
        self.dts_type_name = d.name
        struct_abi_info = StructAbiInfo.get(am, d)
        self.ctor_ref_name = f"ctor_ref_{struct_abi_info.mangled_name}"
        if ClassAttr.get(d):
            self.dts_impl_name = f"{d.name}"
        else:
            self.dts_impl_name = f"{d.name}_inner"

        self.interfacets_ts_injected_codes: list[str] = []
        for iface_injected in TsInjectIntoIfaceAttr.get_all(d):
            self.interfacets_ts_injected_codes.append(iface_injected.ts_code)
        self.class_ts_injected_codes: list[str] = []
        for class_injected in TsInjectIntoClazzAttr.get_all(d):
            self.class_ts_injected_codes.append(class_injected.ts_code)

        self.interfacets_dts_injected_codes: list[str] = []
        for iface_injected in DtsInjectIntoIfaceAttr.get_all(d):
            self.interfacets_dts_injected_codes.append(iface_injected.dts_code)
        self.class_dts_injected_codes: list[str] = []
        for class_injected in DtsInjectIntoClazzAttr.get_all(d):
            self.class_dts_injected_codes.append(class_injected.dts_code)

        self.ctor: GlobFuncDecl | None = None
        self.static_funcs: list[tuple[str, GlobFuncDecl]] = []
        self.register_infos = []

        self.dts_fields: list[StructFieldDecl] = []
        self.dts_iface_parents: list[StructFieldDecl] = []
        self.dts_class_parents: list[StructFieldDecl] = []
        self.dts_final_fields: list[list[StructFieldDecl]] = []
        for field in d.fields:
            if ExtendsAttr.get(field):
                ty = field.ty
                if not isinstance(ty, StructType):
                    raise ValueError("struct cannot extend non-struct type")
                    # TODO: check struct parent type
                parent_napi_info = StructNapiInfo.get(am, ty.decl)
                if parent_napi_info.is_class():
                    self.dts_class_parents.append(field)
                else:
                    self.dts_iface_parents.append(field)
                self.dts_final_fields.extend(
                    [field, *parts] for parts in parent_napi_info.dts_final_fields
                )
            else:
                self.dts_fields.append(field)
                self.dts_final_fields.append([field])

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, p: StructDecl) -> "StructNapiInfo":
        return StructNapiInfo(am, p)

    def is_class(self):
        return self.dts_type_name == self.dts_impl_name

    def dts_type_in(self, target: DtsWriter):
        return self.pkg_napi_info.ns.get_member(
            target,
            self.dts_type_name,
        )


class IfaceNapiInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        self.am = am
        segments = [*d.parent_pkg.segments, d.name]
        self.pkg_napi_info = PackageNapiInfo.get(am, d.parent_pkg)
        self.from_napi_func_name = encode(segments, DeclKind.FROM_NAPI)
        self.into_napi_func_name = encode(segments, DeclKind.INTO_NAPI)
        self.constructor_func_name = encode(segments, DeclKind.CONSTRUCTOR)
        self.create_func_name = encode(segments, DeclKind.CREATE)
        self.decl_header = f"{d.parent_pkg.name}.{d.name}.napi.decl.h"
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.napi.impl.h"
        self.meth_decl_header = f"{d.parent_pkg.name}.{d.name}.meth.napi.decl.h"
        self.meth_impl_header = f"{d.parent_pkg.name}.{d.name}.meth.napi.impl.h"
        self.dts_type_name = d.name
        iface_abi_info = IfaceAbiInfo.get(am, d)
        self.ctor_ref_name = f"ctor_ref_{iface_abi_info.mangled_name}"
        if ClassAttr.get(d):
            self.dts_impl_name = f"{d.name}"
        else:
            self.dts_impl_name = f"{d.name}_inner"

        self.interface_ts_injected_codes: list[str] = []
        for iface_injected in TsInjectIntoIfaceAttr.get_all(d):
            self.interface_ts_injected_codes.append(iface_injected.ts_code)
        self.class_ts_injected_codes: list[str] = []
        for class_injected in TsInjectIntoClazzAttr.get_all(d):
            self.class_ts_injected_codes.append(class_injected.ts_code)

        self.interface_dts_injected_codes: list[str] = []
        for iface_injected in DtsInjectIntoIfaceAttr.get_all(d):
            self.interface_dts_injected_codes.append(iface_injected.dts_code)
        self.class_dts_injected_codes: list[str] = []
        for class_injected in DtsInjectIntoClazzAttr.get_all(d):
            self.class_dts_injected_codes.append(class_injected.dts_code)

        iface_register_infos: list[
            tuple[list[IfaceMethodDecl], IfaceDecl, list[str]]
        ] = []
        for ancestor in iface_abi_info.ancestor_dict:
            property_map: dict[
                str, tuple[str | None, str | None, list[IfaceMethodDecl]]
            ] = defaultdict(lambda: (None, None, []))
            for method in ancestor.methods:
                iface_meth_napi_info = IfaceMethodNapiInfo.get(self.am, method)
                mangled_name = get_mangled_method_name(d, method)
                if get_name := iface_meth_napi_info.get_name:
                    existing_get, existing_set, methods = property_map[get_name]
                    methods.append(method)
                    property_map[get_name] = (mangled_name, existing_set, methods)

                if set_name := iface_meth_napi_info.set_name:
                    existing_get, existing_set, methods = property_map[set_name]
                    methods.append(method)
                    property_map[set_name] = (existing_get, mangled_name, methods)
            for prop_name, (get_name, set_name, methods) in property_map.items():
                if methods:
                    get_mangled = get_name or "nullptr"
                    set_mangled = set_name or "nullptr"
                    props_strs = [
                        f'"{prop_name}"',
                        "nullptr",
                        "nullptr",
                        get_mangled,
                        set_mangled,
                        "nullptr",
                        "napi_default",
                        "nullptr",
                    ]
                    iface_register_infos.append((methods, ancestor, props_strs))
            for method in ancestor.methods:
                mangled_name = get_mangled_method_name(d, method)
                iface_meth_napi_info = IfaceMethodNapiInfo.get(self.am, method)
                if (
                    iface_meth_napi_info.get_name is None
                    and iface_meth_napi_info.set_name is None
                ):
                    props_strs = [
                        f'"{iface_meth_napi_info.norm_name}"',
                        "nullptr",
                        f"{mangled_name}",
                        "nullptr",
                        "nullptr",
                        "nullptr",
                        "napi_default",
                        "nullptr",
                    ]
                    iface_register_infos.append(([method], ancestor, props_strs))
        self.iface_register_infos = iface_register_infos
        self.ctor: GlobFuncDecl | None = None
        self.static_funcs: list[tuple[str, GlobFuncDecl]] = []

        self.dts_class_parents: list[IfaceExtendDecl] = []
        self.dts_iface_parents: list[IfaceExtendDecl] = []
        for extend in d.extends:
            ty = extend.ty
            assert isinstance(ty, IfaceType)
            parent_napi_info = IfaceNapiInfo.get(am, ty.decl)
            if parent_napi_info.is_class():
                self.dts_class_parents.append(extend)
            else:
                self.dts_iface_parents.append(extend)

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: IfaceDecl) -> "IfaceNapiInfo":
        return IfaceNapiInfo(am, f)

    def is_class(self):
        return self.dts_type_name == self.dts_impl_name

    def dts_type_in(self, target: DtsWriter):
        return self.pkg_napi_info.ns.get_member(
            target,
            self.dts_type_name,
        )


class IfaceMethodNapiInfo(AbstractAnalysis[IfaceMethodDecl]):
    def __init__(self, am: AnalysisManager, f: IfaceMethodDecl) -> None:
        self.get_name = None
        self.set_name = None
        self.promise_name = None
        self.async_name = None
        self.norm_name = None

        if get_attr := GetAttr.get(f):
            self.get_name = get_attr.member_name or get_attr.func_suffix
        if set_attr := SetAttr.get(f):
            self.set_name = set_attr.member_name or set_attr.func_suffix

        self.norm_name = f.name

        if PromiseAttribute.get(f):
            self.promise_name = self.norm_name
        elif AsyncAttribute.get(f):
            self.async_name = self.norm_name

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: IfaceMethodDecl) -> "IfaceMethodNapiInfo":
        return IfaceMethodNapiInfo(am, f)


class EnumNapiInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        segments = [*d.parent_pkg.segments, d.name]
        self.dts_type_name = d.name
        self.pkg_napi_info = PackageNapiInfo.get(am, d.parent_pkg)
        self.is_literal = ConstAttr.get(d) is not None
        self.create_func_name = encode(segments, DeclKind.CREATE)

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: EnumDecl) -> "EnumNapiInfo":
        return EnumNapiInfo(am, f)

    def dts_type_in(self, target: DtsWriter):
        return self.pkg_napi_info.ns.get_member(
            target,
            self.dts_type_name,
        )


class GlobFuncNapiInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        self.ctor_class_name = None
        self.static_class_name = None
        self.promise_name = None
        self.async_name = None
        self.norm_name = None
        if ctor_attr := CtorAttr.get(f):
            self.ctor_class_name = ctor_attr.cls_name
        elif static_attr := StaticAttr.get(f):
            self.static_class_name = static_attr.cls_name

        self.norm_name = f.name

        if PromiseAttribute.get(f):
            self.promise_name = self.norm_name
        elif AsyncAttribute.get(f):
            self.async_name = self.norm_name

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: GlobFuncDecl) -> "GlobFuncNapiInfo":
        return GlobFuncNapiInfo(am, f)


class UnionNapiInfo(AbstractAnalysis[UnionDecl]):
    def __init__(self, am: AnalysisManager, d: UnionDecl) -> None:
        segments = [*d.parent_pkg.segments, d.name]
        self.pkg_napi_info = PackageNapiInfo.get(am, d.parent_pkg)
        self.from_napi_func_name = encode(segments, DeclKind.FROM_NAPI)
        self.into_napi_func_name = encode(segments, DeclKind.INTO_NAPI)
        self.decl_header = f"{d.parent_pkg.name}.{d.name}.napi.decl.h"
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.napi.impl.h"
        self.dts_type_name = d.name

        self.dts_final_fields: list[list[UnionFieldDecl]] = []
        for field in d.fields:
            if field.ty_ref and isinstance(ty := field.ty, UnionType):
                inner_napi_info = UnionNapiInfo.get(am, ty.decl)
                self.dts_final_fields.extend(
                    [field, *parts] for parts in inner_napi_info.dts_final_fields
                )
            else:
                self.dts_final_fields.append([field])

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: UnionDecl) -> "UnionNapiInfo":
        return UnionNapiInfo(am, f)

    def dts_type_in(self, target: DtsWriter):
        return self.pkg_napi_info.ns.get_member(
            target,
            self.dts_type_name,
        )


class TypeNapiInfo(AbstractAnalysis[NonVoidType], metaclass=ABCMeta):
    is_optional: bool = False
    napi_type_name: str

    def __init__(self, am: AnalysisManager, t: NonVoidType):
        self.am = am
        self.cpp_info = TypeCppInfo.get(am, t)

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, t: NonVoidType) -> "TypeNapiInfo":
        return t.accept(TypeNapiInfoDispatcher(am))

    @abstractmethod
    def dts_type_in(self, target: DtsWriter) -> str:
        pass

    @abstractmethod
    def dts_return_type_in(self, target: DtsWriter) -> str:
        pass

    @abstractmethod
    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        pass

    @abstractmethod
    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        pass


class NullTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: UnitType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.cpp_info = TypeCppInfo.get(am, t)
        self.napi_type_name = "napi_null"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        return "null"

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result} = {{}};",
        )

    @override
    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"napi_get_null(env, &{napi_result});",
        )


class UndefinedTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: UnitType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.cpp_info = TypeCppInfo.get(am, t)
        self.napi_type_name = "napi_undefined"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        return "undefined"

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result} = {{}};",
        )

    @override
    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"napi_get_undefined(env, &{napi_result});",
        )


class ScalarTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        napi_type = {
            ScalarKind.BOOL: "napi_boolean",
            ScalarKind.F32: "napi_number",
            ScalarKind.F64: "napi_number",
            ScalarKind.I8: "napi_number",
            ScalarKind.I16: "napi_number",
            ScalarKind.I32: "napi_number",
            ScalarKind.I64: "napi_number",
            ScalarKind.U8: "napi_number",
            ScalarKind.U16: "napi_number",
            ScalarKind.U32: "napi_number",
            ScalarKind.U64: "napi_number",
        }.get(self.type.kind)
        if napi_type is None:
            raise ValueError(f"Unsupported ScalarKind: {self.type.kind}")
        self.napi_type_name = napi_type

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        dts_type = {
            ScalarKind.BOOL: "boolean",
            ScalarKind.F32: "number",
            ScalarKind.F64: "number",
            ScalarKind.I8: "number",
            ScalarKind.I16: "number",
            ScalarKind.I32: "number",
            ScalarKind.I64: "number",
            ScalarKind.U8: "number",
            ScalarKind.U16: "number",
            ScalarKind.U32: "number",
            ScalarKind.U64: "number",
        }.get(self.type.kind)
        if dts_type is None:
            raise ValueError(f"Unsupported ScalarKind: {self.type.kind}")
        return dts_type

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        as_napi_c = {
            ScalarKind.BOOL: "bool",
            ScalarKind.F32: "double",
            ScalarKind.F64: "double",
            ScalarKind.I8: "int32_t",
            ScalarKind.I16: "int32_t",
            ScalarKind.I32: "int32_t",
            ScalarKind.I64: "int64_t",
            ScalarKind.U8: "uint32_t",
            ScalarKind.U16: "uint32_t",
            ScalarKind.U32: "uint32_t",
            ScalarKind.U64: "double",
        }.get(self.type.kind)
        from_js_to_c_func = {
            ScalarKind.BOOL: "napi_get_value_bool",
            ScalarKind.F32: "napi_get_value_double",
            ScalarKind.F64: "napi_get_value_double",
            ScalarKind.I8: "napi_get_value_int32",
            ScalarKind.I16: "napi_get_value_int32",
            ScalarKind.I32: "napi_get_value_int32",
            ScalarKind.I64: "napi_get_value_int64",
            ScalarKind.U8: "napi_get_value_uint32",
            ScalarKind.U16: "napi_get_value_uint32",
            ScalarKind.U32: "napi_get_value_uint32",
            ScalarKind.U64: "napi_get_value_double",
        }.get(self.type.kind)
        target.writelns(
            f"{as_napi_c} {cpp_result}_tmp;",
            f"NAPI_CALL(env, {from_js_to_c_func}(env, {napi_value}, &{cpp_result}_tmp));",
            f"{self.cpp_info.as_owner} {cpp_result} = {cpp_result}_tmp;",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        from_c_to_js_func = {
            ScalarKind.BOOL: "napi_get_boolean",
            ScalarKind.F32: "napi_create_double",
            ScalarKind.F64: "napi_create_double",
            ScalarKind.I8: "napi_create_int32",
            ScalarKind.I16: "napi_create_int32",
            ScalarKind.I32: "napi_create_int32",
            ScalarKind.I64: "napi_create_int64",
            ScalarKind.U8: "napi_create_uint32",
            ScalarKind.U32: "napi_create_uint32",
            ScalarKind.U64: "napi_create_double",
        }.get(self.type.kind)
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"NAPI_CALL(env, {from_c_to_js_func}(env, {cpp_value}, &{napi_result}));",
        )


class StringTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: StringType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.cpp_info = TypeCppInfo.get(am, t)
        self.napi_type_name = "napi_string"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        return "string"

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        target.writelns(
            f"size_t {cpp_result}_len = 0;",
            f"NAPI_CALL(env, napi_get_value_string_utf8(env, {napi_value}, nullptr, 0, &{cpp_result}_len));",
            f"TString {cpp_result}_abi;",
            f"char* {cpp_result}_buf = tstr_initialize(&{cpp_result}_abi, {cpp_result}_len + 1);",
            f"NAPI_CALL(env, napi_get_value_string_utf8(env, {napi_value}, {cpp_result}_buf, {cpp_result}_len + 1, &{cpp_result}_len));",
            f"{cpp_result}_buf[{cpp_result}_len] = '\\0';",
            f"{cpp_result}_abi.length = {cpp_result}_len;",
            f"taihe::string {cpp_result}({cpp_result}_abi);",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"NAPI_CALL(env, napi_create_string_utf8(env, {cpp_value}.c_str(), {cpp_value}.size(), &{napi_result}));",
        )


class StructTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: StructType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_type_name = "napi_object"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        struct_napi_info = StructNapiInfo.get(self.am, self.type.decl)
        return struct_napi_info.dts_type_in(target)

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        struct_napi_info = StructNapiInfo.get(self.am, self.type.decl)
        target.add_include(struct_napi_info.impl_header)
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result} = {struct_napi_info.from_napi_func_name}(env, {napi_value});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        struct_napi_info = StructNapiInfo.get(self.am, self.type.decl)
        target.add_include(struct_napi_info.impl_header)
        target.writelns(
            f"napi_value {napi_result} = {struct_napi_info.into_napi_func_name}(env, {cpp_value});",
        )


class IfaceTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        iface_napi_info = IfaceNapiInfo.get(self.am, t.decl)
        self.iface_register_infos = iface_napi_info.iface_register_infos
        self.napi_type_name = "napi_object"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        iface_napi_info = IfaceNapiInfo.get(self.am, self.type.decl)
        return iface_napi_info.dts_type_in(target)

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, self.type.decl)
        target.add_include(iface_napi_info.impl_header)
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result} = {iface_napi_info.from_napi_func_name}(env, {napi_value});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        iface_napi_info = IfaceNapiInfo.get(self.am, self.type.decl)
        target.add_include(iface_napi_info.impl_header)
        target.writelns(
            f"napi_value {napi_result} = {iface_napi_info.into_napi_func_name}(env, {cpp_value});",
        )


class OptionalTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: OptionalType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.is_optional = True
        self.napi_type_name = "napi_object"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
        return item_ty_napi_info.dts_type_in(target)

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return f"{self.dts_type_in(target)} | undefined"

    @override
    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        napi_ty = f"{cpp_result}_v_ty"
        napi_status = f"{cpp_result}_v_ty_status"
        cpp_pointer = f"{cpp_result}_ptr"
        cpp_spec = f"{cpp_result}_spec"
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        target.writelns(
            f"{item_ty_cpp_info.as_owner}* {cpp_pointer} = nullptr;",
            f"napi_valuetype {napi_ty};",
            f"napi_status {napi_status} = napi_typeof(env, {napi_value}, &{napi_ty});",
        )
        with target.indented(
            f"if ({napi_status} == napi_ok && {napi_ty} != napi_undefined) {{",
            f"}}",
        ):
            item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
            item_ty_napi_info.from_napi(target, napi_value, cpp_spec)
            target.writelns(
                f"{cpp_pointer} = new {item_ty_cpp_info.as_owner}(std::move({cpp_spec}));",
            )
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result}({cpp_pointer});",
        )

    @override
    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        napi_spec = f"{napi_result}_spec"
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
        )
        with target.indented(
            f"if (!{cpp_value}) {{",
            f"}}",
        ):
            target.writelns(f"napi_get_undefined(env, &{napi_result});")
        with target.indented(
            f"else {{",
            f"}}",
        ):
            item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
            item_ty_napi_info.into_napi(target, f"(*{cpp_value})", napi_spec)
            target.writelns(
                f"{napi_result} = {napi_spec};",
            )


class CallbackTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: CallbackType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_type_name = "napi_function"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        params_ty_dts = []
        for index, param in enumerate(self.type.ref.params):
            param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
            params_ty_dts.append(
                f"arg_{index}{'?' if param_ty_napi_info.is_optional else ''}: {param_ty_napi_info.dts_type_in(target)}"
            )
        params_ty_dts_str = ", ".join(params_ty_dts)
        if isinstance(return_ty := self.type.ref.return_ty, NonVoidType):
            return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
            return_ty_dts = return_ty_napi_info.dts_type_in(target)
        else:
            return_ty_dts = "void"
        return f"(({params_ty_dts_str}) => {return_ty_dts})"

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    @override
    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        cpp_impl_class = f"{cpp_result}_cpp_impl_t"
        cpp_cb_data_type = f"{cpp_result}_cb_data"
        cpp_inputs = []
        target.add_include("optional")
        with target.indented(
            f"struct {cpp_cb_data_type} {{",
            f"}};",
        ):
            target.writelns(
                f"bool completed = false;",
                f"std::mutex mutex;",
                f"std::condition_variable cv;",
            )
            for index, param in enumerate(self.type.ref.params):
                param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                cpp_input = f"cpp_input_{index}"
                target.writelns(
                    f"std::optional<{param_ty_cpp_info.as_owner}> {cpp_input};",
                )
                cpp_inputs.append(cpp_input)
            if isinstance(return_ty := self.type.ref.return_ty, NonVoidType):
                return_ty_cpp_info = TypeCppInfo.get(self.am, return_ty)
                return_ty_cpp_name = return_ty_cpp_info.as_owner
            else:
                return_ty_cpp_name = "void"
            return_ty_expected_name = (
                f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
            )
            target.writelns(
                f"std::optional<{return_ty_expected_name}> cpp_result;",
            )

        napi_resname = f"napi_resname"
        with target.indented(
            f"struct {cpp_impl_class} {{",
            f"}};",
        ):
            target.writelns(
                f"napi_env env;",
                f"napi_ref ref;",
                f"napi_threadsafe_function tsfn;",
            )
            with target.indented(
                f"{cpp_impl_class}(napi_env env, napi_value callback): env(env), ref(nullptr), tsfn(nullptr) {{",
                f"}}",
            ):
                target.writelns(
                    f"NAPI_CALL(env, napi_create_reference(env, callback, 1, &ref));",
                    f"napi_value {napi_resname};",
                    f'NAPI_CALL(env, napi_create_string_utf8(env, "MyWorkResource", NAPI_AUTO_LENGTH, &{napi_resname}));',
                )
                with target.indented(
                    f"NAPI_CALL(env, napi_create_threadsafe_function(",
                    f"));",
                ):
                    target.writelns(
                        f"env,",
                        f"callback,",
                        f"nullptr,",
                        f"{napi_resname},",
                        f"0,",
                        f"1,",
                        f"nullptr,",
                        f"nullptr,",
                        f"nullptr,",
                    )
                    with target.indented(
                        f"[](napi_env env, napi_value js_cb, [[maybe_unused]] void* context, void* data) {{",
                        f"}},",
                    ):
                        target.writelns(
                            f"{cpp_cb_data_type}* cpp_cb =static_cast<{cpp_cb_data_type}*>(data);",
                            f"napi_value global = nullptr;",
                            f"NAPI_CALL(env, napi_get_global(env, &global));",
                        )
                        inner_napi_args = []
                        for index, param in enumerate(self.type.ref.params):
                            param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
                            inner_napi_arg = f"napi_arg_{index}"
                            inner_napi_args.append(inner_napi_arg)
                            param_ty_napi_info.into_napi(
                                target,
                                f"(*(cpp_cb->{cpp_inputs[index]}))",
                                inner_napi_arg,
                            )
                        inner_napi_args_str = ", ".join(inner_napi_args)
                        if len(self.type.ref.params) != 0:
                            target.writelns(
                                f"napi_value napi_argv[{len(self.type.ref.params)}] = {{{inner_napi_args_str}}};",
                            )
                        else:
                            target.writelns(
                                f"napi_value napi_argv[] = {{}};",
                            )
                        inner_napi_res = "napi_result"
                        inner_cpp_res = "cpp_result"
                        target.writelns(
                            f"napi_value {inner_napi_res} = nullptr;",
                            f"NAPI_CALL(env, napi_call_function(env, global, js_cb, {len(self.type.ref.params)}, napi_argv, &{inner_napi_res}));",
                        )
                        error_message_napi = "error_message_napi"
                        error_message_cpp = "error_message_cpp"
                        target.writelns(
                            f"bool has_error = false;",
                            f"napi_is_exception_pending(env, &has_error);",
                        )
                        with target.indented(
                            f"if (has_error) {{",
                            f"}}",
                        ):
                            target.writelns(
                                f"napi_value exception = nullptr;",
                                f"NAPI_CALL(env, napi_get_and_clear_last_exception(env, &exception));",
                                f"napi_value {error_message_napi};",
                                f'NAPI_CALL(env, napi_get_named_property(env, exception, "message", &{error_message_napi}));',
                                f"size_t {error_message_cpp}_len = 0;",
                                f"NAPI_CALL(env, napi_get_value_string_utf8(env, {error_message_napi}, nullptr, 0, &{error_message_cpp}_len));",
                                f"TString {error_message_cpp}_abi;",
                                f"char* {error_message_cpp}_buf = tstr_initialize(&{error_message_cpp}_abi, {error_message_cpp}_len + 1);",
                                f"NAPI_CALL(env, napi_get_value_string_utf8(env, {error_message_napi}, {error_message_cpp}_buf, {error_message_cpp}_len + 1, &{error_message_cpp}_len));",
                                f"{error_message_cpp}_buf[{error_message_cpp}_len] = '\\0';",
                                f"{error_message_cpp}_abi.length = {error_message_cpp}_len;",
                                f"taihe::string {error_message_cpp}({error_message_cpp}_abi);",
                                f"bool error_has_code;",
                                f'NAPI_CALL(env, napi_has_named_property(env, exception, "code", &error_has_code));',
                            )
                            with target.indented(
                                f"if (error_has_code) {{",
                                f"}}",
                            ):
                                error_code_napi = "error_code_napi"
                                error_code_cpp = "error_code_cpp"
                                target.writelns(
                                    f"napi_value {error_code_napi};",
                                    f'NAPI_CALL(env, napi_get_named_property(env, exception, "code", &{error_code_napi}));',
                                    f"napi_valuetype {error_code_napi}_type;",
                                    f"NAPI_CALL(env, napi_typeof(env, {error_code_napi}, &{error_code_napi}_type));",
                                    f"int32_t {error_code_cpp} = 0;",
                                )
                                with target.indented(
                                    f"switch ({error_code_napi}_type) {{",
                                    f"}}",
                                ):
                                    with target.indented(
                                        f"case napi_string: {{",
                                        f"}}",
                                    ):
                                        target.writelns(
                                            f"size_t {error_code_napi}_len = 0;",
                                            f"NAPI_CALL(env, napi_get_value_string_utf8(env, {error_code_napi}, nullptr, 0, &{error_code_napi}_len));",
                                            f"char {error_code_napi}_buffer[{error_code_napi}_len + 1];",
                                            f"size_t {error_code_napi}_copied;",
                                            f"NAPI_CALL(env, napi_get_value_string_utf8(env, {error_code_napi}, {error_code_napi}_buffer, {error_code_napi}_len + 1, &{error_code_napi}_copied));",
                                            f"{error_code_napi}_buffer[{error_code_napi}_len] = '\\0';",
                                            f"{error_code_cpp} = std::stoi({error_code_napi}_buffer);",
                                            f"cpp_cb->cpp_result = ::taihe::unexpected<::taihe::error>(taihe::error({error_message_cpp}));",
                                            f"break;",
                                        )
                                    with target.indented(
                                        f"case napi_number: {{",
                                        f"}}",
                                    ):
                                        target.writelns(
                                            f"NAPI_CALL(env, napi_get_value_int32(env, {error_code_napi}, &{error_code_cpp}));",
                                            f"cpp_cb->cpp_result = ::taihe::unexpected<::taihe::error>(taihe::error({error_message_cpp}));",
                                            f"break;",
                                        )
                                    with target.indented(
                                        f"default: {{",
                                        f"}}",
                                    ):
                                        target.writelns(
                                            f"cpp_cb->cpp_result = ::taihe::unexpected<::taihe::error>(taihe::error({error_message_cpp}));",
                                            f"break;",
                                        )
                            with target.indented(
                                f"else {{",
                                f"}}",
                            ):
                                target.writelns(
                                    f"cpp_cb->cpp_result = ::taihe::unexpected<::taihe::error>(taihe::error({error_message_cpp}));",
                                )
                        with target.indented(
                            f"else {{",
                            f"}}",
                        ):
                            if isinstance(
                                return_ty := self.type.ref.return_ty, NonVoidType
                            ):
                                return_napi_type_info = TypeNapiInfo.get(
                                    self.am, return_ty
                                )
                                return_napi_type_info.from_napi(
                                    target, inner_napi_res, inner_cpp_res
                                )
                                target.writelns(
                                    f"cpp_cb->cpp_result = {inner_cpp_res};",
                                )
                            else:
                                target.writelns(
                                    f"cpp_cb->cpp_result = {{}};",
                                )
                        target.writelns(
                            f"cpp_cb->completed = true;",
                            f"cpp_cb->cv.notify_one();",
                        )
                    target.writelns(
                        f"&tsfn",
                    )
            with target.indented(
                f"~{cpp_impl_class}() {{",
                f"}}",
            ):
                with target.indented(
                    f"if (ref) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"NAPI_CALL(env, napi_delete_reference(env, ref));",
                    )
                with target.indented(
                    f"if (tsfn) {{",
                    f"}}",
                ):
                    target.writelns(
                        f"NAPI_CALL(env, napi_release_threadsafe_function(tsfn, napi_tsfn_release));",
                    )

            inner_cpp_params = []
            inner_napi_args = []
            inner_cpp_args = []
            for index, param in enumerate(self.type.ref.params):
                inner_cpp_arg = f"cpp_arg_{index}"
                inner_napi_arg = f"napi_arg_{index}"
                param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                inner_cpp_params.append(f"{param_ty_cpp_info.as_param} {inner_cpp_arg}")
                inner_napi_args.append(inner_napi_arg)
                inner_cpp_args.append(inner_cpp_arg)
            cpp_params_str = ", ".join(inner_cpp_params)
            with target.indented(
                f"{return_ty_expected_name} operator()({cpp_params_str}) {{",
                f"}}",
            ):
                with target.indented(
                    f"if (::taihe::_is_main_thread()) {{",
                    f"}}",
                ):
                    for inner_napi_arg, inner_cpp_arg, param in zip(
                        inner_napi_args,
                        inner_cpp_args,
                        self.type.ref.params,
                        strict=True,
                    ):
                        param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
                        param_ty_napi_info.into_napi(
                            target, inner_cpp_arg, inner_napi_arg
                        )
                    inner_napi_args_str = ", ".join(inner_napi_args)
                    inner_napi_res = "napi_result"
                    inner_cpp_res = "cpp_result"
                    if len(self.type.ref.params) != 0:
                        target.writelns(
                            f"napi_value napi_argv[{len(self.type.ref.params)}] = {{{inner_napi_args_str}}};",
                        )
                    else:
                        target.writelns(
                            f"napi_value napi_argv[] = {{}};",
                        )
                    target.writelns(
                        f"napi_value {inner_napi_res} = nullptr;",
                        f"napi_value cb_ref = nullptr, global = nullptr;",
                        f"NAPI_CALL(env, napi_get_reference_value(env, ref, &cb_ref));",
                        f"napi_get_global(env, &global);",
                        f"NAPI_CALL(env, napi_call_function(env, global, cb_ref, {len(self.type.ref.params)}, napi_argv, &{inner_napi_res}));",
                    )
                    error_message_napi = "error_message_napi"
                    error_message_cpp = "error_message_cpp"
                    target.writelns(
                        f"bool has_error = false;",
                        f"napi_is_exception_pending(env, &has_error);",
                    )
                    with target.indented(
                        f"if (has_error) {{",
                        f"}}",
                    ):
                        target.writelns(
                            f"napi_value exception = nullptr;",
                            f"NAPI_CALL(env, napi_get_and_clear_last_exception(env, &exception));",
                            f"napi_value {error_message_napi};",
                            f'NAPI_CALL(env, napi_get_named_property(env, exception, "message", &{error_message_napi}));',
                            f"size_t {error_message_cpp}_len = 0;",
                            f"NAPI_CALL(env, napi_get_value_string_utf8(env, {error_message_napi}, nullptr, 0, &{error_message_cpp}_len));",
                            f"TString {error_message_cpp}_abi;",
                            f"char* {error_message_cpp}_buf = tstr_initialize(&{error_message_cpp}_abi, {error_message_cpp}_len + 1);",
                            f"NAPI_CALL(env, napi_get_value_string_utf8(env, {error_message_napi}, {error_message_cpp}_buf, {error_message_cpp}_len + 1, &{error_message_cpp}_len));",
                            f"{error_message_cpp}_buf[{error_message_cpp}_len] = '\\0';",
                            f"{error_message_cpp}_abi.length = {error_message_cpp}_len;",
                            f"taihe::string {error_message_cpp}({error_message_cpp}_abi);",
                            f"bool error_has_code;",
                            f'NAPI_CALL(env, napi_has_named_property(env, exception, "code", &error_has_code));',
                        )
                        with target.indented(
                            f"if (error_has_code) {{",
                            f"}}",
                        ):
                            error_code_napi = "error_code_napi"
                            error_code_cpp = "error_code_cpp"
                            target.writelns(
                                f"napi_value {error_code_napi};",
                                f'NAPI_CALL(env, napi_get_named_property(env, exception, "code", &{error_code_napi}));',
                                f"napi_valuetype {error_code_napi}_type;",
                                f"NAPI_CALL(env, napi_typeof(env, {error_code_napi}, &{error_code_napi}_type));",
                                f"int32_t {error_code_cpp} = 0;",
                            )
                            with target.indented(
                                f"switch ({error_code_napi}_type) {{",
                                f"}}",
                            ):
                                with target.indented(
                                    f"case napi_string: {{",
                                    f"}}",
                                ):
                                    target.writelns(
                                        f"size_t {error_code_napi}_len = 0;",
                                        f"NAPI_CALL(env, napi_get_value_string_utf8(env, {error_code_napi}, nullptr, 0, &{error_code_napi}_len));",
                                        f"char {error_code_napi}_buffer[{error_code_napi}_len + 1];",
                                        f"size_t {error_code_napi}_copied;",
                                        f"NAPI_CALL(env, napi_get_value_string_utf8(env, {error_code_napi}, {error_code_napi}_buffer, {error_code_napi}_len + 1, &{error_code_napi}_copied));",
                                        f"{error_code_napi}_buffer[{error_code_napi}_len] = '\\0';",
                                        f"{error_code_cpp} = std::stoi({error_code_napi}_buffer);",
                                        f"break;",
                                    )
                                with target.indented(
                                    f"case napi_number: {{",
                                    f"}}",
                                ):
                                    target.writelns(
                                        f"NAPI_CALL(env, napi_get_value_int32(env, {error_code_napi}, &{error_code_cpp}));",
                                        f"break;",
                                    )
                                with target.indented(
                                    f"default: {{",
                                    f"}}",
                                ):
                                    target.writelns(
                                        f"return ::taihe::unexpected<::taihe::error>(taihe::error({error_message_cpp}));",
                                        f"break;",
                                    )
                            target.writelns(
                                f"return ::taihe::unexpected<::taihe::error>(taihe::error({error_message_cpp}, {error_code_cpp}));",
                            )
                        with target.indented(
                            f"else {{",
                            f"}}",
                        ):
                            target.writelns(
                                f"return ::taihe::unexpected<::taihe::error>(taihe::error({error_message_cpp}));",
                            )
                    with target.indented(
                        f"else {{",
                        f"}}",
                    ):
                        if isinstance(
                            return_ty := self.type.ref.return_ty, NonVoidType
                        ):
                            return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
                            return_ty_napi_info.from_napi(
                                target, inner_napi_res, inner_cpp_res
                            )
                            target.writelns(
                                f"return {inner_cpp_res};",
                            )
                        else:
                            target.writelns(
                                f"return {{}};",
                            )
                cpp_cb_data = "cb_data"
                with target.indented(
                    f"else {{",
                    f"}}",
                ):
                    target.writelns(
                        f"{cpp_cb_data_type} {cpp_cb_data};",
                    )
                    for index, param in enumerate(self.type.ref.params):
                        target.writelns(
                            f"{cpp_cb_data}.{cpp_inputs[index]} = {inner_cpp_args[index]};",
                        )
                    with target.indented(
                        f"NAPI_CALL(env, napi_call_threadsafe_function(",
                        f"));",
                    ):
                        target.writelns(
                            f"tsfn,",
                            f"&{cpp_cb_data},",
                            f"napi_tsfn_blocking",
                        )
                    target.writelns(
                        f"std::unique_lock<std::mutex> lock({cpp_cb_data}.mutex);",
                        f"{cpp_cb_data}.cv.wait(lock, [&{cpp_cb_data}] {{ return {cpp_cb_data}.completed; }});",
                    )
                    if isinstance(return_ty := self.type.ref.return_ty, NonVoidType):
                        target.writelns(
                            f"return *{cpp_cb_data}.cpp_result;",
                        )
                    else:
                        target.writelns(
                            f"return {{}};",
                        )

        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result} = ::taihe::make_holder<{cpp_impl_class}, {self.cpp_info.as_owner}>(env, {napi_value});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        cpp_copy = f"{napi_result}_cpp_copy"
        cpp_scope = f"{napi_result}_cpp_scope"
        invoke_name = "invoke"
        napi_vtbl_ptr = f"{napi_result}_napi_vtbl_ptr"
        napi_data_ptr = f"{napi_result}_napi_data_ptr"
        with target.indented(
            f"struct {cpp_scope} {{",
            f"}};",
        ):
            self.gen_native_invoke(target, invoke_name)
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_copy} = {cpp_value};",
            f"{self.cpp_info.as_param}::vtable_type* {napi_vtbl_ptr} = reinterpret_cast<{self.cpp_info.as_param}::vtable_type*>({cpp_copy}.m_handle.vtbl_ptr);",
            f"DataBlockHead* {napi_data_ptr} = reinterpret_cast<DataBlockHead*>({cpp_copy}.m_handle.data_ptr);",
            f"{cpp_copy}.m_handle.data_ptr = nullptr;",
            f"{self.cpp_info.as_owner}* cpp_ptr = new {self.cpp_info.as_owner}({{{napi_vtbl_ptr}, {napi_data_ptr}}});",
            f"napi_value {napi_result} = nullptr;",
            f"NAPI_CALL(env, napi_create_function(env, nullptr, NAPI_AUTO_LENGTH, {cpp_scope}::{invoke_name}, cpp_ptr, &{napi_result}));",
        )
        with target.indented(
            f"NAPI_CALL(env, napi_add_finalizer(env, {napi_result}, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
            f"}}, nullptr, nullptr));",
        ):
            target.writelns(
                f"delete static_cast<{self.cpp_info.as_owner}*>(finalize_data);",
            )

    def gen_native_invoke(
        self,
        target: CSourceWriter,
        cpp_cast_ptr: str,
    ):
        inner_napi_args = []
        inner_cpp_args = []
        for index, param in enumerate(self.type.ref.params):
            inner_cpp_arg = f"cpp_arg_{index}"
            inner_napi_arg = f"args[{index}]"
            inner_napi_args.append(inner_napi_arg)
            inner_cpp_args.append(inner_cpp_arg)

        with target.indented(
            f"static napi_value {cpp_cast_ptr}(napi_env env, napi_callback_info info) {{",
            f"}};",
        ):
            if len(self.type.ref.params) != 0:
                target.writelns(
                    f"napi_value args[{len(self.type.ref.params)}] = {{nullptr}};",
                )
            else:
                target.writelns(
                    f"napi_value args[] = {{}};",
                )
            target.writelns(
                f"size_t argc = {len(self.type.ref.params)};",
                f"void* data_ptr = nullptr;",
                f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, &data_ptr));",
                f"{self.cpp_info.as_owner}* cpp_cb = static_cast<{self.cpp_info.as_owner}*>(data_ptr);",
            )
            args_cpp = []
            for inner_napi_arg, inner_cpp_arg, param in zip(
                inner_napi_args,
                inner_cpp_args,
                self.type.ref.params,
                strict=True,
            ):
                param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
                param_ty_napi_info.from_napi(target, inner_napi_arg, inner_cpp_arg)
                param_ty_cpp_info = TypeCppInfo.get(self.am, param.ty)
                args_cpp.append(
                    f"std::forward<{param_ty_cpp_info.as_param}>({inner_cpp_arg})"
                )
            args_cpp_str = ", ".join(args_cpp)
            with target.indented(
                f"if (cpp_cb) {{",
                f"}}",
            ):
                if isinstance(return_ty := self.type.ref.return_ty, NonVoidType):
                    cpp_return_info = TypeCppInfo.get(self.am, return_ty)
                    return_ty_cpp_name = cpp_return_info.as_owner
                else:
                    return_ty_cpp_name = "void"
                return_ty_cpp_name_expected = (
                    f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
                )
                result_cpp = "cpp_result"
                result_napi = "napi_result"
                result_expected = "expected_result"
                result_error = "error_result"
                target.writelns(
                    f"{return_ty_cpp_name_expected} {result_expected} = (*cpp_cb)({args_cpp_str});",
                )
                with target.indented(
                    f"if ({result_expected}) {{",
                    f"}}",
                ):
                    if isinstance(return_ty := self.type.ref.return_ty, NonVoidType):
                        target.writelns(
                            f"{return_ty_cpp_name} {result_cpp} = {result_expected}.value();",
                        )
                        return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
                        return_ty_napi_info.into_napi(target, result_cpp, result_napi)
                        target.writelns(
                            f"return {result_napi};",
                        )
                    else:
                        target.writelns(
                            f"return nullptr;",
                        )
                with target.indented(
                    f"else {{",
                    f"}}",
                ):
                    target.writelns(
                        f"::taihe::error {result_error} = {result_expected}.error();",
                        f"char const *code = std::to_string({result_error}.code()).c_str();",
                        f"napi_throw_error(env, code, {result_error}.message().c_str());",
                        f"return nullptr;",
                    )
            with target.indented(
                f"else {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_throw_error(env,",
                    f'    "ERR_NOT_FOUND",',
                    f'    "No cpp function pointer"',
                    f");",
                    f"return nullptr;",
                )


class EnumTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        if isinstance(self.type.decl.ty, ScalarType | StringType):
            item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
            self.napi_type_name = item_ty_napi_info.napi_type_name
        else:
            raise ValueError

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        enum_napi_info = EnumNapiInfo.get(self.am, self.type.decl)
        return enum_napi_info.dts_type_in(target)

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        enum_cpp_info = EnumCppInfo.get(self.am, self.type.decl)
        if isinstance(self.type.decl.ty, ScalarType | StringType):
            item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
            item_ty_napi_info.from_napi(target, napi_value, f"{cpp_result}_item")
        else:
            raise ValueError

        target.writelns(
            f"{enum_cpp_info.as_owner} {cpp_result} = {enum_cpp_info.as_owner}::from_value({cpp_result}_item);",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        if isinstance(self.type.decl.ty, ScalarType | StringType):
            item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
            item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.decl.ty)
            item_ty_napi_info.into_napi(
                target,
                f"(({item_ty_cpp_info.as_owner})({cpp_value}.get_value()))",
                napi_result,
            )
        else:
            raise ValueError


class ArrayBufferTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_type_name = "napi_object"

        if not isinstance(t.item_ty, ScalarType) or t.item_ty.kind not in (
            ScalarKind.I8,
            ScalarKind.U8,
        ):
            raise ValueError(
                "@arraybuffer only supports Array<i8> or Array<i8>",
            )

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        return "ArrayBuffer"

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        napi_data = f"{cpp_result}_data"
        napi_length = f"{cpp_result}_length"
        target.writelns(
            f"void* {napi_data};",
            f"size_t {napi_length};",
            f"NAPI_CALL(env, napi_get_arraybuffer_info(env, {napi_value}, &{napi_data}, &{napi_length}));",
            f"{self.cpp_info.as_param} {cpp_result}(reinterpret_cast<{item_ty_cpp_info.as_owner}*>({napi_data}), {napi_length});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        target.add_include("string.h")
        napi_data = f"{napi_result}_data"
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"void* {napi_data} = nullptr;",
            f"NAPI_CALL(env, napi_create_arraybuffer(env, {cpp_value}.size(), &{napi_data}, &{napi_result}));",
            f"std::copy({cpp_value}.begin(), {cpp_value}.end(), reinterpret_cast<{item_ty_cpp_info.as_owner}*>({napi_data}));",
        )


class ArrayTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_type_name = "napi_object"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
        return f"Array<{item_ty_napi_info.dts_type_in(target)}>"

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
        array_size = f"{cpp_result}_size"
        cpp_buffer = f"{cpp_result}_buffer"
        napi_item = f"{cpp_buffer}_napi_item"
        cpp_item = f"{cpp_buffer}_cpp_item"
        cpp_ctr = f"{cpp_buffer}_i"
        target.writelns(
            f"uint32_t {array_size};",
            f"NAPI_CALL(env, napi_get_array_length(env, {napi_value}, &{array_size}));",
            f"{item_ty_cpp_info.as_owner}* {cpp_buffer} = reinterpret_cast<{item_ty_cpp_info.as_owner}*>(malloc({array_size} * sizeof({item_ty_cpp_info.as_owner})));",
        )
        with target.indented(
            f"for (uint32_t {cpp_ctr} = 0; {cpp_ctr} < {array_size}; {cpp_ctr}++) {{",
            f"}}",
        ):
            target.writelns(
                f"napi_value {napi_item};",
                f"NAPI_CALL(env, napi_get_element(env, {napi_value}, {cpp_ctr}, &{napi_item}));",
            )
            item_ty_napi_info.from_napi(target, napi_item, cpp_item)
            target.writelns(
                f"new (&{cpp_buffer}[{cpp_ctr}]) {item_ty_napi_info.cpp_info.as_owner}(std::move({cpp_item}));",
            )
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result}({cpp_buffer}, {array_size});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
        cpp_size = f"{napi_result}_size"
        napi_item = f"{napi_result}_item"
        cpp_ctr = f"{napi_result}_i"
        target.writelns(
            f"uint32_t {cpp_size} = {cpp_value}.size();",
            f"napi_value {napi_result} = nullptr;",
            f"NAPI_CALL(env, napi_create_array_with_length(env, {cpp_size}, &{napi_result}));",
        )
        with target.indented(
            f"for (uint32_t {cpp_ctr} = 0; {cpp_ctr} < {cpp_size}; {cpp_ctr}++) {{",
            f"}}",
        ):
            item_ty_napi_info.into_napi(target, f"{cpp_value}[{cpp_ctr}]", napi_item)
            target.writelns(
                f"NAPI_CALL(env, napi_set_element(env, {napi_result}, {cpp_ctr}, {napi_item}));",
            )


class TypedArrayTypeNapiInfo(TypeNapiInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: ArrayType,
        typedarray_attr: TypedArrayAttr,
    ) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.typedarray_attr = typedarray_attr
        napi_type_name = None
        if isinstance(self.type.item_ty, ScalarType):
            napi_type_name = {
                ScalarKind.F32: "napi_float32_array",
                ScalarKind.F64: "napi_float64_array",
                ScalarKind.I8: "napi_int8_array",
                ScalarKind.I16: "napi_int16_array",
                ScalarKind.I32: "napi_int32_array",
                ScalarKind.I64: "napi_bigint64_array",
                ScalarKind.U8: "napi_uint8_array",
                ScalarKind.U16: "napi_uint16_array",
                ScalarKind.U32: "napi_uint32_array",
                ScalarKind.U64: "napi_biguint64_array",
            }.get(self.type.item_ty.kind)
        if napi_type_name is None:
            raise ValueError(f"Unsupported TypedArrayKind: {self.type}")
        self.napi_type_name = napi_type_name

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        dts_type = None
        if isinstance(self.type.item_ty, ScalarType):
            dts_type = {
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
            }.get(self.type.item_ty.kind)
        if dts_type is None:
            raise ValueError(f"Unsupported TypedArrayKind: {self.type}")
        return dts_type

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        napi_ta_type = f"{cpp_result}_type"
        napi_length = f"{cpp_result}_length"
        napi_data = f"{cpp_result}_data"
        napi_arrbuf = f"{cpp_result}_arrbuf"
        napi_byte_offset = f"{cpp_result}_byoff"
        target.writelns(
            f"napi_typedarray_type {napi_ta_type};",
            f"size_t {napi_length};",
            f"void* {napi_data};",
            f"napi_value {napi_arrbuf};",
            f"size_t {napi_byte_offset};",
            f"NAPI_CALL(env, napi_get_typedarray_info(env, {napi_value}, &{napi_ta_type}, &{napi_length}, &{napi_data}, &{napi_arrbuf}, &{napi_byte_offset}));",
            f"{self.cpp_info.as_param} {cpp_result}(reinterpret_cast<{item_ty_cpp_info.as_owner}*>({napi_data}), {napi_length});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        napi_data = f"{napi_result}_data"
        napi_arrbuf = f"{napi_result}_arrbuf"
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"napi_value {napi_arrbuf} = nullptr;",
            f"void* {napi_data} = nullptr;",
            f"NAPI_CALL(env, napi_create_arraybuffer(env, {cpp_value}.size() * sizeof({item_ty_cpp_info.as_owner}), &{napi_data}, &{napi_arrbuf}));",
            f"std::copy({cpp_value}.begin(), {cpp_value}.end(), reinterpret_cast<{item_ty_cpp_info.as_owner}*>({napi_data}));",
            f"NAPI_CALL(env, napi_create_typedarray(env, {self.napi_type_name}, {cpp_value}.size(), {napi_arrbuf}, 0, &{napi_result}));",
        )


class RecordTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_type_name = "napi_object"
        # TODO: 错误 key 类型提示

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)
        key_dts_type = key_ty_napi_info.dts_type_in(target)
        val_dts_type = val_ty_napi_info.dts_type_in(target)
        return f"Record<{key_dts_type}, {val_dts_type}>"

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        prop_names = f"{cpp_result}_prop_names"
        prop_count = f"{cpp_result}_prop_count"
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)
        napi_key = f"{cpp_result}_napi_key"
        napi_val = f"{cpp_result}_napi_val"

        cpp_key = f"{cpp_result}_cpp_key"
        cpp_val = f"{cpp_result}_cpp_val"
        target.writelns(
            f"napi_value {prop_names} = nullptr;",
            f"uint32_t {prop_count};",
            f"NAPI_CALL(env, napi_get_property_names(env, {napi_value}, &{prop_names}));",
            f"NAPI_CALL(env, napi_get_array_length(env, {prop_names}, &{prop_count}));",
            f"{self.cpp_info.as_owner} {cpp_result};",
        )
        with target.indented(
            f"for (uint32_t i = 0; i < {prop_count}; i++) {{",
            f"}}",
        ):
            target.writelns(
                f"napi_value {napi_key} = nullptr, {napi_val} = nullptr;",
                f"NAPI_CALL(env, napi_get_element(env, {prop_names}, i, &{napi_key}));",
                f"NAPI_CALL(env, napi_get_property(env, {napi_value}, {napi_key}, &{napi_val}));",
            )
            key_ty_napi_info.from_napi(target, napi_key, cpp_key)
            val_ty_napi_info.from_napi(target, napi_val, cpp_val)
            target.writelns(
                f"{cpp_result}.emplace({cpp_key}, {cpp_val});",
            )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)

        napi_key = f"{napi_result}_napi_key"
        napi_val = f"{napi_result}_napi_val"
        cpp_key = f"{napi_result}_cpp_key"
        cpp_val = f"{napi_result}_cpp_val"

        target.writelns(
            f"napi_value {napi_result};",
            f"napi_create_object(env, &{napi_result});",
        )
        with target.indented(
            f"for (const auto& [{cpp_key}, {cpp_val}] : {cpp_value}) {{",
            f"}}",
        ):
            key_ty_napi_info.into_napi(target, cpp_key, napi_key)
            val_ty_napi_info.into_napi(target, cpp_val, napi_val)
            target.writelns(
                f"NAPI_CALL(env, napi_set_property(env, {napi_result}, {napi_key}, {napi_val}));",
            )


class MapTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_type_name = "napi_object"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)
        key_dts_type = key_ty_napi_info.dts_type_in(target)
        val_dts_type = val_ty_napi_info.dts_type_in(target)
        return f"Map<{key_dts_type}, {val_dts_type}>"

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)
        cpp_key = f"{cpp_result}_cpp_key"
        cpp_val = f"{cpp_result}_cpp_val"
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result};",
            f"napi_value {cpp_result}_entries_fn = nullptr, {cpp_result}_entries_iter = nullptr;",
            f'NAPI_CALL(env, napi_get_named_property(env, {napi_value}, "entries", &{cpp_result}_entries_fn));',
            f"NAPI_CALL(env, napi_call_function(env, {napi_value}, {cpp_result}_entries_fn, 0, nullptr, &{cpp_result}_entries_iter));",
            f"napi_value {cpp_result}_next_meth = nullptr;",
            f'NAPI_CALL(env, napi_get_named_property(env, {cpp_result}_entries_iter, "next", &{cpp_result}_next_meth));',
        )
        with target.indented(
            f"while (true) {{",
            f"}}",
        ):
            target.writelns(
                f"napi_value {cpp_result}_next_result;",
                f"NAPI_CALL(env, napi_call_function(env, {cpp_result}_entries_iter, {cpp_result}_next_meth, 0, nullptr, &{cpp_result}_next_result));",
                f"bool {cpp_result}_done;",
                f"napi_value {cpp_result}_done_prop;",
                f'NAPI_CALL(env, napi_get_named_property(env, {cpp_result}_next_result, "done", &{cpp_result}_done_prop));',
                f"NAPI_CALL(env, napi_get_value_bool(env, {cpp_result}_done_prop, &{cpp_result}_done));",
                f"if ({cpp_result}_done) break;",
                f"napi_value {cpp_result}_value_prop, {cpp_result}_key, {cpp_result}_value;",
                f'NAPI_CALL(env, napi_get_named_property(env, {cpp_result}_next_result, "value", &{cpp_result}_value_prop));',
                f"NAPI_CALL(env, napi_get_element(env, {cpp_result}_value_prop, 0, &{cpp_result}_key));",
                f"NAPI_CALL(env, napi_get_element(env, {cpp_result}_value_prop, 1, &{cpp_result}_value));",
            )
            key_ty_napi_info.from_napi(target, f"{cpp_result}_key", cpp_key)
            val_ty_napi_info.from_napi(target, f"{cpp_result}_value", cpp_val)
            target.writelns(
                f"{cpp_result}.emplace({cpp_key}, {cpp_val});",
            )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        napi_key = f"{napi_result}_napi_key"
        napi_val = f"{napi_result}_napi_val"
        cpp_key = f"{napi_result}_cpp_key"
        cpp_val = f"{napi_result}_cpp_val"
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)

        target.writelns(
            f"napi_value {napi_result}_global = nullptr, {napi_result}_map_ctor = nullptr, {napi_result} = nullptr;",
            f"napi_get_global(env, &{napi_result}_global);",
            f'NAPI_CALL(env, napi_get_named_property(env, {napi_result}_global, "Map", &{napi_result}_map_ctor));',
            f"NAPI_CALL(env, napi_new_instance(env, {napi_result}_map_ctor, 0, nullptr, &{napi_result}));",
            f"napi_value {napi_result}_set_fn = nullptr;",
            f'NAPI_CALL(env, napi_get_named_property(env, {napi_result}, "set", &{napi_result}_set_fn));',
        )
        with target.indented(
            f"for (const auto& [{cpp_key}, {cpp_val}] : {cpp_value}) {{",
            f"}}",
        ):
            key_ty_napi_info.into_napi(target, cpp_key, napi_key)
            val_ty_napi_info.into_napi(target, cpp_val, napi_val)
            target.writelns(
                f"napi_value {napi_result}_args[2] = {{{napi_key}, {napi_val}}};",
                f"NAPI_CALL(env, napi_call_function(env, {napi_result}, {napi_result}_set_fn, 2, {napi_result}_args, nullptr));",
            )


class UnionTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: UnionType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_type_name = "napi_value"  # TODO not sure

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        union_napi_info = UnionNapiInfo.get(self.am, self.type.decl)
        return union_napi_info.dts_type_in(target)

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        union_napi_info = UnionNapiInfo.get(self.am, self.type.decl)
        target.add_include(union_napi_info.impl_header)
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result} = {union_napi_info.from_napi_func_name}(env, {napi_value});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        union_napi_info = UnionNapiInfo.get(self.am, self.type.decl)
        target.add_include(union_napi_info.impl_header)
        target.writelns(
            f"napi_value {napi_result} = {union_napi_info.into_napi_func_name}(env, {cpp_value});",
        )


class OpaqueTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: OpaqueType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_type_name = "napi_object"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        if dts_type_attr := DtsTypeAttr.get(self.type.ref):
            return dts_type_attr.type_name
        else:
            return "Object"

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        target.writelns(
            f"{self.cpp_info.as_owner} {cpp_result} = ({self.cpp_info.as_owner}){napi_value};",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        target.writelns(
            f"napi_value {napi_result} = (napi_value){cpp_value};",
        )


class ConstEnumTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: EnumType, const_attr: ConstAttr):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.const_attr = const_attr
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
        self.napi_type_name = item_ty_napi_info.napi_type_name

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
        return ty_napi_info.dts_type_in(target)

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        cpp_temp = f"{cpp_result}_cpp_temp"
        ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
        enum_cpp_info = EnumCppInfo.get(self.am, self.type.decl)
        ty_napi_info.from_napi(target, napi_value, cpp_temp)
        target.writelns(
            f"{enum_cpp_info.full_name} {cpp_result} = {enum_cpp_info.full_name}::from_value({cpp_temp});",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        cpp_temp = f"{napi_result}_cpp_temp"
        ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
        value_cpp_info = TypeCppInfo.get(self.am, self.type.decl.ty)
        target.writelns(
            f"{value_cpp_info.as_owner} {cpp_temp} = {cpp_value}.get_value();",
        )
        ty_napi_info.into_napi(target, cpp_temp, napi_result)


class BigIntTypeNapiInfo(TypeNapiInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: ArrayType,
    ) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        # TODO: check the attribute should be used in Array<u64>

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        return "bigint"

    @override
    def dts_return_type_in(self, target: DtsWriter) -> str:
        return self.dts_type_in(target)

    def from_napi(
        self,
        target: CSourceWriter,
        napi_value: str,
        cpp_result: str,
    ):
        target.writelns(
            f"size_t {cpp_result}_len = 0;",
            f"int {cpp_result}_sign = 0;",
            f"NAPI_CALL(env, napi_get_value_bigint_words(env, {napi_value}, nullptr, &{cpp_result}_len, nullptr));",
            f"uint64_t* {cpp_result}_words = new uint64_t[{cpp_result}_len];",
            f"NAPI_CALL(env, napi_get_value_bigint_words(env, {napi_value}, &{cpp_result}_sign, &{cpp_result}_len, {cpp_result}_words));",
            f"{self.cpp_info.as_owner} {cpp_result}(_taihe_build_num({cpp_result}_sign, {self.cpp_info.as_owner}{{{cpp_result}_words, {cpp_result}_len}}));",
        )

    def into_napi(
        self,
        target: CSourceWriter,
        cpp_value: str,
        napi_result: str,
    ):
        target.writelns(
            f"napi_value {napi_result} = nullptr;",
            f"auto [{napi_result}_sign, {napi_result}_abs] = ::taihe::_get_bigint_sign_and_abs({cpp_value});",
            f"NAPI_CALL(env, napi_create_bigint_words(env, {napi_result}_sign, {napi_result}_abs.size(), {napi_result}_abs.data(), &{napi_result}));",
        )


class TypeNapiInfoDispatcher(NonVoidTypeVisitor[TypeNapiInfo]):
    def __init__(self, am: AnalysisManager):
        self.am = am

    @override
    def visit_scalar_type(self, t: ScalarType) -> TypeNapiInfo:
        return ScalarTypeNapiInfo(self.am, t)

    @override
    def visit_string_type(self, t: StringType) -> TypeNapiInfo:
        return StringTypeNapiInfo(self.am, t)

    @override
    def visit_struct_type(self, t: StructType) -> TypeNapiInfo:
        return StructTypeNapiInfo(self.am, t)

    @override
    def visit_iface_type(self, t: IfaceType) -> TypeNapiInfo:
        return IfaceTypeNapiInfo(self.am, t)

    @override
    def visit_optional_type(self, t: OptionalType) -> TypeNapiInfo:
        return OptionalTypeNapiInfo(self.am, t)

    @override
    def visit_callback_type(self, t: CallbackType) -> TypeNapiInfo:
        return CallbackTypeNapiInfo(self.am, t)

    @override
    def visit_enum_type(self, t: EnumType) -> TypeNapiInfo:
        if const_attr := ConstAttr.get(t.decl):
            return ConstEnumTypeNapiInfo(self.am, t, const_attr)
        return EnumTypeNapiInfo(self.am, t)

    @override
    def visit_array_type(self, t: ArrayType) -> TypeNapiInfo:
        if BigIntAttr.get(t.ref):
            return BigIntTypeNapiInfo(self.am, t)
        if ArrayBufferAttr.get(t.ref):
            return ArrayBufferTypeNapiInfo(self.am, t)
        if typedarray_attr := TypedArrayAttr.get(t.ref):
            return TypedArrayTypeNapiInfo(self.am, t, typedarray_attr)
        return ArrayTypeNapiInfo(self.am, t)

    @override
    def visit_map_type(self, t: MapType) -> TypeNapiInfo:
        if RecordAttr.get(t.ref):
            return RecordTypeNapiInfo(self.am, t)
        return MapTypeNapiInfo(self.am, t)

    @override
    def visit_union_type(self, t: UnionType) -> TypeNapiInfo:
        return UnionTypeNapiInfo(self.am, t)

    @override
    def visit_opaque_type(self, t: OpaqueType) -> TypeNapiInfo:
        return OpaqueTypeNapiInfo(self.am, t)

    @override
    def visit_unit_type(self, t: UnitType) -> TypeNapiInfo:
        if UndefinedAttr.get(t.ref) or (
            isinstance(t.ref.parent_type_holder, StructFieldDecl | UnionFieldDecl)
            and UndefinedAttr.get(t.ref.parent_type_holder)
        ):
            return UndefinedTypeNapiInfo(self.am, t)
        return NullTypeNapiInfo(self.am, t)
