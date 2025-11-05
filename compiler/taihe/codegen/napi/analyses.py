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
    ClassAttr,
    ConstAttr,
    CtorAttr,
    ExtendsAttr,
    GetAttr,
    NamespaceAttr,
    SetAttr,
    StaticAttr,
)
from taihe.codegen.cpp.analyses import (
    EnumCppInfo,
    TypeCppInfo,
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
)
from taihe.semantics.types import (
    EnumType,
    IfaceType,
    NonVoidType,
    ScalarKind,
    ScalarType,
    StringType,
    StructType,
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
        self.norm_name = None
        if ctor_attr := CtorAttr.get(f):
            self.ctor_class_name = ctor_attr.cls_name
        elif static_attr := StaticAttr.get(f):
            self.static_class_name = static_attr.cls_name
        self.norm_name = f.name

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: GlobFuncDecl) -> "GlobFuncNapiInfo":
        return GlobFuncNapiInfo(am, f)


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
            ScalarKind.U64: "uint64_t",
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
            ScalarKind.U64: "napi_get_value_bigint_uint64",
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
    def visit_enum_type(self, t: EnumType) -> TypeNapiInfo:
        if const_attr := ConstAttr.get(t.decl):
            return ConstEnumTypeNapiInfo(self.am, t, const_attr)
        return EnumTypeNapiInfo(self.am, t)
