# -*- coding: utf-8 -*-
#
# Copyright (c) 2025-2026 Huawei Device Co., Ltd.
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

from taihe.codegen.abi.analyses import (
    CallbackAbiInfo,
    IfaceAbiInfo,
)
from taihe.codegen.abi.writer import CSourceWriter
from taihe.codegen.cpp.analyses import (
    IfaceCppInfo,
    StructCppInfo,
    TypeCppInfo,
    UnionCppInfo,
)
from taihe.codegen.napi.attributes import (
    ArrayBufferAttr,
    AsyncAttribute,
    BigIntAttr,
    ClassAttr,
    ConstAttr,
    CtorAttr,
    DtsInjectAttr,
    DtsInjectIntoClazzAttr,
    DtsInjectIntoIfaceAttr,
    DtsInjectIntoModuleAttr,
    DtsTypeAttr,
    ExtendsAttr,
    GetAttr,
    LibAttr,
    NamespaceAttr,
    NullAttr,
    PromiseAttribute,
    ReadOnlyAttr,
    RecordAttr,
    SetAttr,
    StaticAttr,
    TsInjectAttr,
    TsInjectIntoClazzAttr,
    TsInjectIntoModuleAttr,
    TypedArrayAttr,
    UndefinedAttr,
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
    ScalarKinds,
    ScalarType,
    SetType,
    StringType,
    StructType,
    UnionType,
    UnitType,
)
from taihe.semantics.visitor import NonVoidTypeVisitor
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager


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

        self.lib_name: str | None = None

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

        for pkg in pg.iterate():
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

            if attr := LibAttr.get(pkg):
                mod.lib_name = attr.lib_name

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
        self.source = f"{p.name}.napi.cpp"
        self.header = f"{p.name}.napi.h"
        self.cpp_ns = "::".join(p.segments)
        pg_napi_info = PackageGroupNapiInfo.get(am, p.parent_group)
        self.ns = pg_napi_info.get_namespace(p)

        self.global_register_infos: dict[str, tuple[str, str, str]] = {}
        self.global_funcs: list[GlobFuncDecl] = []

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, p: PackageDecl) -> "PackageNapiInfo":
        return PackageNapiInfo(am, p)


class StructNapiInfo(AbstractAnalysis[StructDecl]):
    def __init__(self, am: AnalysisManager, d: StructDecl) -> None:
        self.pkg_napi_info = PackageNapiInfo.get(am, d.parent_pkg)
        self.decl_header = f"{d.parent_pkg.name}.{d.name}.napi.decl.h"
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.napi.impl.h"
        self.dts_type_name = d.name
        self._is_class = ClassAttr.get(d) is not None

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
        self.static_register_infos: dict[str, tuple[str, str, str]] = {}
        self.static_funcs: list[GlobFuncDecl] = []

        self.dts_iface_parents: list[StructFieldDecl] = []
        self.dts_class_parent: StructFieldDecl | None = None
        self.dts_final_fields: list[list[StructFieldDecl]] = []
        self.dts_local_fields: list[StructFieldDecl] = []
        for field in d.fields:
            if extend := ExtendsAttr.get(field):
                parent_napi_info = StructNapiInfo.get(am, extend.ty.decl)
                if parent_napi_info.is_class():
                    self.dts_class_parent = field
                else:
                    self.dts_iface_parents.append(field)
                self.dts_final_fields.extend(
                    [field, *parts] for parts in parent_napi_info.dts_final_fields
                )
            else:
                self.dts_final_fields.append([field])
                self.dts_local_fields.append(field)

        self.register_infos: dict[str, tuple[str, str, str]] = defaultdict(
            lambda: ("nullptr", "nullptr", "nullptr")
        )
        self.getters: list[tuple[str, list[StructFieldDecl]]] = []
        self.setters: list[tuple[str, list[StructFieldDecl]]] = []
        for parts in self.dts_final_fields:
            final = parts[-1]
            getter = f"getter::{final.name}"
            self.getters.append((final.name, parts))
            if ReadOnlyAttr.get(final) is None:
                setter = f"setter::{final.name}"
                self.setters.append((final.name, parts))
            else:
                setter = "nullptr"
            self.register_infos[final.name] = ("nullptr", getter, setter)

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, p: StructDecl) -> "StructNapiInfo":
        return StructNapiInfo(am, p)

    def is_class(self):
        return self._is_class

    def dts_type_in(self, target: DtsWriter):
        return self.pkg_napi_info.ns.get_member(
            target,
            self.dts_type_name,
        )


class IfaceNapiInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        self.am = am
        self.pkg_napi_info = PackageNapiInfo.get(am, d.parent_pkg)
        self.decl_header = f"{d.parent_pkg.name}.{d.name}.napi.decl.h"
        self.impl_header = f"{d.parent_pkg.name}.{d.name}.napi.impl.h"
        self.dts_type_name = d.name
        self._is_class = ClassAttr.get(d) is not None

        self.class_ts_injected_codes: list[str] = []
        for class_injected in TsInjectIntoClazzAttr.get_all(d):
            self.class_ts_injected_codes.append(class_injected.ts_code)

        self.interface_dts_injected_codes: list[str] = []
        for iface_injected in DtsInjectIntoIfaceAttr.get_all(d):
            self.interface_dts_injected_codes.append(iface_injected.dts_code)
        self.class_dts_injected_codes: list[str] = []
        for class_injected in DtsInjectIntoClazzAttr.get_all(d):
            self.class_dts_injected_codes.append(class_injected.dts_code)

        self.register_infos: dict[str, tuple[str, str, str]] = defaultdict(
            lambda: ("nullptr", "nullptr", "nullptr")
        )
        self.methods: list[tuple[str, IfaceMethodDecl]] = []
        iface_abi_info = IfaceAbiInfo.get(am, d)
        for ancestor in iface_abi_info.ancestor_infos:
            for method in ancestor.methods:
                local_name = method.name
                self.methods.append((local_name, method))
                iface_meth_napi_info = IfaceMethodNapiInfo.get(self.am, method)
                mangled_name = f"method::{local_name}"
                if get_name := iface_meth_napi_info.get_name:
                    caller, _, setter = self.register_infos[get_name]
                    self.register_infos[get_name] = (caller, mangled_name, setter)
                    continue
                if set_name := iface_meth_napi_info.set_name:
                    caller, getter, _ = self.register_infos[set_name]
                    self.register_infos[set_name] = (caller, getter, mangled_name)
                    continue
                method_name = method.name
                _, getter, setter = self.register_infos[method_name]
                self.register_infos[method_name] = (mangled_name, getter, setter)
        self.ctor: GlobFuncDecl | None = None
        self.static_register_infos: dict[str, tuple[str, str, str]] = {}
        self.static_funcs: list[GlobFuncDecl] = []

        self.dts_class_parent: IfaceExtendDecl | None = None
        self.dts_iface_parents: list[IfaceExtendDecl] = []
        for extend in d.extends:
            parent_napi_info = IfaceNapiInfo.get(am, extend.ty.decl)
            if parent_napi_info.is_class():
                self.dts_class_parent = extend
            else:
                self.dts_iface_parents.append(extend)

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: IfaceDecl) -> "IfaceNapiInfo":
        return IfaceNapiInfo(am, f)

    def is_class(self):
        return self._is_class

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
        elif set_attr := SetAttr.get(f):
            self.set_name = set_attr.member_name or set_attr.func_suffix
        elif PromiseAttribute.get(f):
            self.promise_name = f.name
        elif AsyncAttribute.get(f):
            self.async_name = f.name
        else:
            self.norm_name = f.name

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: IfaceMethodDecl) -> "IfaceMethodNapiInfo":
        return IfaceMethodNapiInfo(am, f)


class EnumNapiInfo(AbstractAnalysis[EnumDecl]):
    def __init__(self, am: AnalysisManager, d: EnumDecl) -> None:
        self.dts_type_name = d.name
        self.pkg_napi_info = PackageNapiInfo.get(am, d.parent_pkg)
        self.is_literal = ConstAttr.get(d) is not None

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

        if PromiseAttribute.get(f):
            self.promise_name = f.name
        elif AsyncAttribute.get(f):
            self.async_name = f.name
        else:
            self.norm_name = f.name

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, f: GlobFuncDecl) -> "GlobFuncNapiInfo":
        return GlobFuncNapiInfo(am, f)


class UnionNapiInfo(AbstractAnalysis[UnionDecl]):
    def __init__(self, am: AnalysisManager, d: UnionDecl) -> None:
        self.pkg_napi_info = PackageNapiInfo.get(am, d.parent_pkg)
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
    napi_valuetype: str | bool

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

    def dts_return_type_in(self, target: DtsWriter) -> str:
        if self.is_optional:
            return f"({self.dts_type_in(target)} | undefined)"
        else:
            return self.dts_type_in(target)

    @abstractmethod
    def gen_from_napi(self, target: CSourceWriter, name: str): ...

    @abstractmethod
    def gen_into_napi(self, target: CSourceWriter, name: str): ...

    def gen_check_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> bool {{",
            f"}};",
        ):
            if self.napi_valuetype is True:
                target.writelns(
                    f"return true;",
                )
                return
            if self.napi_valuetype is False:
                target.writelns(
                    f'TH_THROW(std::runtime_error, "not supported");',
                )
                return
            target.writelns(
                f"napi_valuetype napi_type;",
                f"return napi_typeof(env, napi_input, &napi_type) == napi_ok && napi_type == {self.napi_valuetype};",
            )


class NullTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: UnitType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.cpp_info = TypeCppInfo.get(am, t)
        self.napi_valuetype = "napi_null"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        return "null"

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"return {{}};",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            target.writelns(
                f"napi_value napi_result = nullptr;",
                f"napi_get_null(env, &napi_result);",
                f"return napi_result;",
            )


class UndefinedTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: UnitType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.cpp_info = TypeCppInfo.get(am, t)
        self.napi_valuetype = "napi_undefined"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        return "undefined"

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"return {{}};",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            target.writelns(
                f"napi_value napi_result = nullptr;",
                f"napi_get_undefined(env, &napi_result);",
                f"return napi_result;",
            )


class ScalarTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        napi_valuetype = {
            ScalarKinds.BOOL: "napi_boolean",
            ScalarKinds.F64: "napi_number",
            ScalarKinds.I32: "napi_number",
            ScalarKinds.I64: "napi_number",
            ScalarKinds.U32: "napi_number",
        }.get(self.type.kind)
        if napi_valuetype is None:
            raise ValueError(f"Unsupported ScalarKind: {self.type.kind}")
        self.napi_valuetype = napi_valuetype

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        dts_type = {
            ScalarKinds.BOOL: "boolean",
            ScalarKinds.F64: "number",
            ScalarKinds.I32: "number",
            ScalarKinds.I64: "number",
            ScalarKinds.U32: "number",
        }.get(self.type.kind)
        if dts_type is None:
            raise ValueError(f"Unsupported ScalarKind: {self.type.kind}")
        return dts_type

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        from_js_to_c_func = {
            ScalarKinds.BOOL: "napi_get_value_bool",
            ScalarKinds.F64: "napi_get_value_double",
            ScalarKinds.I32: "napi_get_value_int32",
            ScalarKinds.I64: "napi_get_value_int64",
            ScalarKinds.U32: "napi_get_value_uint32",
        }.get(self.type.kind)
        if from_js_to_c_func is None:
            raise ValueError(f"Unsupported ScalarKind: {self.type.kind}")
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"{self.cpp_info.as_owner} cpp_result;",
                f"NAPI_CALL(env, {from_js_to_c_func}(env, napi_input, &cpp_result));",
                f"return cpp_result;",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        from_c_to_js_func = {
            ScalarKinds.BOOL: "napi_get_boolean",
            ScalarKinds.F64: "napi_create_double",
            ScalarKinds.I32: "napi_create_int32",
            ScalarKinds.I64: "napi_create_int64",
            ScalarKinds.U32: "napi_create_uint32",
        }.get(self.type.kind)
        if from_c_to_js_func is None:
            raise ValueError(f"Unsupported ScalarKind: {self.type.kind}")
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            target.writelns(
                f"napi_value napi_result = nullptr;",
                f"NAPI_CALL(env, {from_c_to_js_func}(env, cpp_value, &napi_result));",
                f"return napi_result;",
            )


class StringTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: StringType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.cpp_info = TypeCppInfo.get(am, t)
        self.napi_valuetype = "napi_string"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        return "string"

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"size_t cpp_result_len = 0;",
                f"NAPI_CALL(env, napi_get_value_string_utf8(env, napi_input, nullptr, 0, &cpp_result_len));",
                f"TString cpp_result_abi;",
                f"char* cpp_result_buf = tstr_initialize(&cpp_result_abi, cpp_result_len + 1);",
                f"NAPI_CALL(env, napi_get_value_string_utf8(env, napi_input, cpp_result_buf, cpp_result_len + 1, &cpp_result_len));",
                f"cpp_result_buf[cpp_result_len] = '\\0';",
                f"tstr_set_len(&cpp_result_abi, cpp_result_len);",
                f"return taihe::string(cpp_result_abi);",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            target.writelns(
                f"napi_value napi_result = nullptr;",
                f"NAPI_CALL(env, napi_create_string_utf8(env, cpp_value.c_str(), cpp_value.size(), &napi_result));",
                f"return napi_result;",
            )


class StructTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: StructType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = False

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        struct_napi_info = StructNapiInfo.get(self.am, self.type.decl)
        return struct_napi_info.dts_type_in(target)

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        struct_napi_info = StructNapiInfo.get(self.am, self.type.decl)
        struct_cpp_info = StructCppInfo.get(self.am, self.type.decl)
        target.add_include(struct_napi_info.impl_header)
        target.writelns(
            f"static constexpr auto {name} = ::taihe::from_napi<{struct_cpp_info.as_owner}>;",
        )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        struct_napi_info = StructNapiInfo.get(self.am, self.type.decl)
        struct_cpp_info = StructCppInfo.get(self.am, self.type.decl)
        target.add_include(struct_napi_info.impl_header)
        target.writelns(
            f"static constexpr auto {name} = ::taihe::into_napi<{struct_cpp_info.as_owner}>;",
        )

    @override
    def gen_check_napi(self, target: CSourceWriter, name: str):
        struct_type_napi_info = StructNapiInfo.get(self.am, self.type.decl)
        struct_cpp_info = StructCppInfo.get(self.am, self.type.decl)
        if not struct_type_napi_info.is_class():
            super().gen_check_napi(target, name)
            return
        # TODO: experimental
        target.add_include(struct_type_napi_info.impl_header)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> bool {{",
            f"}};",
        ):
            target.writelns(
                f"napi_value ctor = nullptr;",
                f"bool result = false;",
                f"return napi_get_reference_value(env, ::taihe::into_napi_t<{struct_cpp_info.as_owner}>::ctor_ref, &ctor) == napi_ok",
                f"    && napi_instanceof(env, napi_input, ctor, &result) == napi_ok",
                f"    && result;",
            )


class IfaceTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = False

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        iface_napi_info = IfaceNapiInfo.get(self.am, self.type.decl)
        return iface_napi_info.dts_type_in(target)

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        iface_napi_info = IfaceNapiInfo.get(self.am, self.type.decl)
        iface_cpp_info = IfaceCppInfo.get(self.am, self.type.decl)
        target.add_include(iface_napi_info.impl_header)
        target.writelns(
            f"static constexpr auto {name} = ::taihe::from_napi<{iface_cpp_info.as_owner}>;",
        )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        iface_napi_info = IfaceNapiInfo.get(self.am, self.type.decl)
        iface_cpp_info = IfaceCppInfo.get(self.am, self.type.decl)
        target.add_include(iface_napi_info.impl_header)
        target.writelns(
            f"static constexpr auto {name} = ::taihe::into_napi<{iface_cpp_info.as_owner}>;",
        )

    @override
    def gen_check_napi(self, target: CSourceWriter, name: str):
        iface_napi_info = IfaceNapiInfo.get(self.am, self.type.decl)
        iface_cpp_info = IfaceCppInfo.get(self.am, self.type.decl)
        if not iface_napi_info.is_class():
            super().gen_check_napi(target, name)
            return
        # TODO: experimental
        target.add_include(iface_napi_info.impl_header)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> bool {{",
            f"}};",
        ):
            target.writelns(
                f"napi_value ctor = nullptr;",
                f"bool result = false;",
                f"return napi_get_reference_value(env, ::taihe::into_napi_t<{iface_cpp_info.as_owner}>::ctor_ref, &ctor) == napi_ok",
                f"    && napi_instanceof(env, napi_input, ctor, &result) == napi_ok",
                f"    && result;",
            )


class OptionalTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: OptionalType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.is_optional = True
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
        self.napi_valuetype = item_ty_napi_info.napi_valuetype

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
        return item_ty_napi_info.dts_type_in(target)

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
            item_from_napi = "from_napi_item"
            item_ty_napi_info.gen_from_napi(target, item_from_napi)
            target.writelns(
                f"napi_valuetype napi_type;",
                f"napi_status status = napi_typeof(env, napi_input, &napi_type);",
            )
            with target.indented(
                f"if (status == napi_ok && napi_type != napi_undefined) {{",
                f"}}",
            ):
                target.writelns(
                    f"return {self.cpp_info.as_owner}(std::in_place, {item_from_napi}(env, napi_input));",
                )
            with target.indented(
                f"else {{",
                f"}}",
            ):
                target.writelns(
                    f"return std::nullopt;",
                )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
            item_into_napi = "into_napi_item"
            item_ty_napi_info.gen_into_napi(target, item_into_napi)
            with target.indented(
                f"if (cpp_value) {{",
                f"}}",
            ):
                target.writelns(
                    f"return {item_into_napi}(env, *cpp_value);",
                )
            with target.indented(
                f"else {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_value napi_result = nullptr;",
                    f"napi_get_undefined(env, &napi_result);",
                    f"return napi_result;",
                )

    @override
    def gen_check_napi(self, target: CSourceWriter, name: str):
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
        return item_ty_napi_info.gen_check_napi(target, name)


class CallbackTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: CallbackType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = "napi_function"

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        params = []
        for param in self.type.ref.params:
            param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
            params.append(
                f"{param.name}{'?' if param_ty_napi_info.is_optional else ''}: {param_ty_napi_info.dts_type_in(target)}"
            )
        params_str = ", ".join(params)
        if isinstance(return_ty := self.type.ref.return_ty, NonVoidType):
            return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
            return_ty = return_ty_napi_info.dts_type_in(target)
        else:
            return_ty = "void"
        return f"(({params_str}) => {return_ty})"

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            cpp_impl_class = "cpp_impl_t"
            with target.indented(
                f"struct {cpp_impl_class}: ::taihe::napi_ref_guard {{",
                f"}};",
            ):
                target.writelns(
                    f"using ::taihe::napi_ref_guard::napi_ref_guard;",
                )
                self.gen_invoke_operator(target)
            target.writelns(
                f"return ::taihe::make_holder<{cpp_impl_class}, {self.cpp_info.as_owner}, ::taihe::platform::napi::NapiObject>(env, napi_input);;",
            )

    def gen_invoke_operator(
        self,
        target: CSourceWriter,
    ):
        cb_abi_info = CallbackAbiInfo.get(self.am, self.type)
        method_params = []
        method_args = []
        for param in self.type.ref.params:
            param_cpp_type_info = TypeCppInfo.get(self.am, param.ty)
            method_arg = f"arg_{param.name}"
            method_args.append(method_arg)
            method_params.append(f"{param_cpp_type_info.as_param} {method_arg}")
        method_params_str = ", ".join(method_params)
        if isinstance(return_ty := self.type.ref.return_ty, NonVoidType):
            return_ty_info = TypeCppInfo.get(self.am, return_ty)
            return_ty_cpp_name = return_ty_info.as_owner
        else:
            return_ty_cpp_name = "void"
        if not cb_abi_info.is_noexcept:
            return_ty_cpp_name = (
                f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
            )
        with target.indented(
            f"{return_ty_cpp_name} operator()({method_params_str}) {{",
            f"}}",
        ):
            with target.indented(
                f"return this->sync_call(",
                f");",
            ):
                self.write_sync_call_lambda(target)
                for method_arg in method_args:
                    target.writelns(
                        f", std::forward<decltype({method_arg})>({method_arg})",
                    )

    def write_sync_call_lambda(
        self,
        target: CSourceWriter,
    ):
        cb_abi_info = CallbackAbiInfo.get(self.am, self.type)
        method_params = ["napi_env env", "napi_ref ref"]
        method_args = []
        for param in self.type.ref.params:
            param_cpp_type_info = TypeCppInfo.get(self.am, param.ty)
            method_arg = f"arg_{param.name}"
            method_params.append(f"{param_cpp_type_info.as_param} {method_arg}")
            method_args.append(method_arg)
        method_params_str = ", ".join(method_params)
        if isinstance(return_ty := self.type.ref.return_ty, NonVoidType):
            return_ty_info = TypeCppInfo.get(self.am, return_ty)
            return_ty_cpp_name = return_ty_info.as_owner
        else:
            return_ty_cpp_name = "void"
        if not cb_abi_info.is_noexcept:
            return_ty_cpp_name = (
                f"::taihe::expected<{return_ty_cpp_name}, ::taihe::error>"
            )
        with target.indented(
            f"[]({method_params_str}) -> {return_ty_cpp_name} {{",
            f"}}",
        ):
            target.writelns(
                f"napi_value args[{len(self.type.ref.params)}];",
            )
            for index, (param, method_arg) in enumerate(
                zip(self.type.ref.params, method_args, strict=True)
            ):
                param_napi_type_info = TypeNapiInfo.get(self.am, param.ty)
                into_napi = f"into_napi_arg_{param.name}"
                param_napi_type_info.gen_into_napi(target, into_napi)
                target.writelns(
                    f"args[{index}] = {into_napi}(env, std::forward<decltype({method_arg})>({method_arg}));",
                )
            target.writelns(
                f"napi_value cb_ref = nullptr;",
                f"NAPI_CALL(env, napi_get_reference_value(env, ref, &cb_ref));",
                f"napi_value global = nullptr;",
                f"NAPI_CALL(env, napi_get_global(env, &global));",
                f"napi_value callback_result_napi = nullptr;",
                f"NAPI_CALL(env, napi_call_function(env, global, cb_ref, {len(self.type.ref.params)}, args, &callback_result_napi));",
            )
            if not cb_abi_info.is_noexcept:
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
                        f"return ::taihe::unexpected<::taihe::error>(::taihe::from_napi_error(env, exception));",
                    )
            if isinstance(return_ty := self.type.ref.return_ty, NonVoidType):
                return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
                return_ty_napi_info.gen_from_napi(target, "from_napi_result")
                target.writelns(
                    f"return from_napi_result(env, callback_result_napi);",
                )
            elif not cb_abi_info.is_noexcept:
                target.writelns(
                    f"return {{}};",
                )
            else:
                target.writelns(
                    f"return;",
                )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_owner} cpp_value) -> napi_value {{",
            f"}};",
        ):
            target.writelns(
                f"{self.cpp_info.as_owner}* cpp_ptr = new {self.cpp_info.as_owner}(std::move(cpp_value));",
                f"napi_value napi_result = nullptr;",
            )
            with target.indented(
                f"NAPI_CALL(env, napi_create_function(env, nullptr, NAPI_AUTO_LENGTH, []([[maybe_unused]] napi_env env, [[maybe_unused]] napi_callback_info info) -> napi_value {{",
                f"}}, cpp_ptr, &napi_result));",
            ):
                self.gen_func_content(target)
            with target.indented(
                f"NAPI_CALL(env, napi_add_finalizer(env, napi_result, cpp_ptr, []([[maybe_unused]] napi_env env, void* finalize_data, [[maybe_unused]] void* finalize_hint) {{",
                f"}}, nullptr, nullptr));",
            ):
                target.writelns(
                    f"delete static_cast<{self.cpp_info.as_owner}*>(finalize_data);",
                )
            target.writelns(
                f"return napi_result;",
            )

    def gen_func_content(
        self,
        target: CSourceWriter,
    ):
        is_noexcept = CallbackAbiInfo.get(self.am, self.type).is_noexcept
        target.writelns(
            f"{self.cpp_info.as_owner}* cpp_cb;",
            f"NAPI_CALL(env, napi_get_cb_info(env, info, nullptr, nullptr, nullptr, reinterpret_cast<void**>(&cpp_cb)));",
        )
        argc = len(self.type.ref.params)
        target.writelns(
            f"size_t argc = {argc};",
            f"napi_value args[{argc}] = {{}};",
            f"NAPI_CALL(env, napi_get_cb_info(env, info, &argc, args, nullptr, nullptr));",
        )
        cpp_exprs = self._read_func_params(target, "args")
        result_storage_type = self._get_cpp_result_type(is_noexcept)
        cpp_exprs_str = ", ".join(cpp_exprs)
        result = "cpp_result"
        if result_storage_type == "void":
            target.writelns(
                f"(*cpp_cb)({cpp_exprs_str});",
            )
        else:
            target.writelns(
                f"{result_storage_type} {result} = (*cpp_cb)({cpp_exprs_str});",
            )
        if not is_noexcept:
            with target.indented(
                f"if (not {result}.has_value()) {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_value error_obj = taihe::into_napi_error(env, {result}.error());",
                    f"napi_throw(env, error_obj);",
                    f"return nullptr;",
                )
            result = f"{result}.value()"
        if isinstance(return_ty := self.type.ref.return_ty, NonVoidType):
            return_ty_napi_info = TypeNapiInfo.get(self.am, return_ty)
            into_napi = "into_napi_result"
            return_ty_napi_info.gen_into_napi(target, into_napi)
            target.writelns(
                f"return {into_napi}(env, std::move({result}));",
            )
        else:
            target.writelns(
                f"return nullptr;",
            )

    def _get_cpp_result_type(
        self,
        is_noexcept: bool,
    ) -> str:
        if isinstance(return_ty := self.type.ref.return_ty, NonVoidType):
            cpp_ty = TypeCppInfo.get(self.am, return_ty).as_owner
        else:
            cpp_ty = "void"
        if not is_noexcept:
            cpp_ty = f"::taihe::expected<{cpp_ty}, ::taihe::error>"
        return cpp_ty

    def _read_func_params(
        self,
        target: CSourceWriter,
        args: str,
    ) -> list[str]:
        cpp_exprs = []
        for index, param in enumerate(self.type.ref.params):
            from_napi = f"from_napi_arg_{param.name}"
            param_ty_napi_info = TypeNapiInfo.get(self.am, param.ty)
            param_ty_napi_info.gen_from_napi(target, from_napi)
            cpp_exprs.append(f"{from_napi}(env, {args}[{index}])")
        return cpp_exprs


class EnumTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
        self.napi_valuetype = item_ty_napi_info.napi_valuetype

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        enum_napi_info = EnumNapiInfo.get(self.am, self.type.decl)
        return enum_napi_info.dts_type_in(target)

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            item_ty_napi_info.gen_from_napi(target, "from_napi_item")
            target.writelns(
                f"return {self.cpp_info.as_owner}::from_value(from_napi_item(env, napi_input));",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            item_ty_napi_info.gen_into_napi(target, "into_napi_item")
            target.writelns(
                f"return into_napi_item(env, cpp_value.get_value());",
            )


class ArrayBufferTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = False
        if not isinstance(t.item_ty, ScalarType) or t.item_ty.kind not in (
            ScalarKinds.I8,
            ScalarKinds.U8,
        ):
            raise ValueError(
                "@arraybuffer only supports Array<i8> or Array<i8>",
            )

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        return "ArrayBuffer"

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_param} {{",
            f"}};",
        ):
            target.writelns(
                f"void* data;",
                f"size_t size;",
                f"NAPI_CALL(env, napi_get_arraybuffer_info(env, napi_input, &data, &size));",
                f"return {self.cpp_info.as_param}(reinterpret_cast<{item_ty_cpp_info.as_owner}*>(data), size / sizeof({item_ty_cpp_info.as_owner}));",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            target.writelns(
                f"napi_value napi_result = nullptr;",
                f"void* data = nullptr;",
                f"NAPI_CALL(env, napi_create_arraybuffer(env, cpp_value.size() * sizeof({item_ty_cpp_info.as_owner}), &data, &napi_result));",
                f"std::copy(cpp_value.begin(), cpp_value.end(), reinterpret_cast<{item_ty_cpp_info.as_owner}*>(data));",
                f"return napi_result;",
            )

    @override
    def gen_check_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> bool {{",
            f"}};",
        ):
            target.writelns(
                f"bool result = false;",
                f"return napi_is_arraybuffer(env, napi_input, &result) == napi_ok && result;",
            )


class ArrayTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = False

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
        return f"Array<{item_ty_napi_info.dts_type_in(target)}>"

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            item_from_napi = "from_napi_item"
            item_ty_napi_info.gen_from_napi(target, item_from_napi)
            target.writelns(
                f"uint32_t size;",
                f"NAPI_CALL(env, napi_get_array_length(env, napi_input, &size));",
                f"{item_ty_cpp_info.as_owner}* cpp_buffer = reinterpret_cast<{item_ty_cpp_info.as_owner}*>(malloc(size * sizeof({item_ty_cpp_info.as_owner})));",
            )
            with target.indented(
                f"for (uint32_t i = 0; i < size; i++) {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_value napi_item;",
                    f"NAPI_CALL(env, napi_get_element(env, napi_input, i, &napi_item));",
                    f"new (&cpp_buffer[i]) {item_ty_napi_info.cpp_info.as_owner}({item_from_napi}(env, napi_item));",
                )
            target.writelns(
                f"return {self.cpp_info.as_owner}(cpp_buffer, size);",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.item_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            item_into_napi = "into_napi_item"
            item_ty_napi_info.gen_into_napi(target, item_into_napi)
            target.writelns(
                f"uint32_t size = cpp_value.size();",
                f"napi_value napi_result = nullptr;",
                f"NAPI_CALL(env, napi_create_array_with_length(env, size, &napi_result));",
            )
            with target.indented(
                f"for (uint32_t i = 0; i < size; i++) {{",
                f"}}",
            ):
                target.writelns(
                    f"NAPI_CALL(env, napi_set_element(env, napi_result, i, {item_into_napi}(env, cpp_value[i])));",
                )
            target.writelns(
                f"return napi_result;",
            )

    @override
    def gen_check_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> bool {{",
            f"}};",
        ):
            target.writelns(
                f"bool result = false;",
                f"return napi_is_array(env, napi_input, &result) == napi_ok && result;",
            )


class TypedArrayTypeNapiInfo(TypeNapiInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: ArrayType,
    ) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = False
        napi_typedarray_type = None
        if isinstance(self.type.item_ty, ScalarType):
            napi_typedarray_type = {
                ScalarKinds.F32: "napi_float32_array",
                ScalarKinds.F64: "napi_float64_array",
                ScalarKinds.I8: "napi_int8_array",
                ScalarKinds.I16: "napi_int16_array",
                ScalarKinds.I32: "napi_int32_array",
                ScalarKinds.I64: "napi_bigint64_array",
                ScalarKinds.U8: "napi_uint8_array",
                ScalarKinds.U16: "napi_uint16_array",
                ScalarKinds.U32: "napi_uint32_array",
                ScalarKinds.U64: "napi_biguint64_array",
            }.get(self.type.item_ty.kind)
        if napi_typedarray_type is None:
            raise ValueError(f"Unsupported TypedArrayKind: {self.type}")
        self.napi_typedarray_type = napi_typedarray_type

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        dts_type = None
        if isinstance(self.type.item_ty, ScalarType):
            dts_type = {
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
            }.get(self.type.item_ty.kind)
        if dts_type is None:
            raise ValueError(f"Unsupported TypedArrayKind: {self.type}")
        return dts_type

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_param} {{",
            f"}};",
        ):
            target.writelns(
                f"size_t size;",
                f"void* data;",
                f"NAPI_CALL(env, napi_get_typedarray_info(env, napi_input, nullptr, &size, &data, nullptr, nullptr));",
                f"return {self.cpp_info.as_param}(reinterpret_cast<{item_ty_cpp_info.as_owner}*>(data), size / sizeof({item_ty_cpp_info.as_owner}));",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        item_ty_cpp_info = TypeCppInfo.get(self.am, self.type.item_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            target.writelns(
                f"napi_value napi_result = nullptr;",
                f"napi_value arrbuf = nullptr;",
                f"void* data = nullptr;",
                f"NAPI_CALL(env, napi_create_arraybuffer(env, cpp_value.size() * sizeof({item_ty_cpp_info.as_owner}), &data, &arrbuf));",
                f"std::copy(cpp_value.begin(), cpp_value.end(), reinterpret_cast<{item_ty_cpp_info.as_owner}*>(data));",
                f"NAPI_CALL(env, napi_create_typedarray(env, {self.napi_typedarray_type}, cpp_value.size(), arrbuf, 0, &napi_result));",
                f"return napi_result;",
            )

    @override
    def gen_check_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> bool {{",
            f"}};",
        ):
            target.writelns(
                f"bool result = false;",
                f"if (napi_is_typedarray(env, napi_input, &result) != napi_ok || !result) {{",
                f"    return false;",
                f"}}",
                f"napi_typedarray_type napi_type;",
                f"return napi_get_typedarray_info(env, napi_input, &napi_type, nullptr, nullptr, nullptr, nullptr) == napi_ok && napi_type == {self.napi_typedarray_type};",
            )


class RecordTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = False

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)
        key_dts_type = key_ty_napi_info.dts_type_in(target)
        val_dts_type = val_ty_napi_info.dts_type_in(target)
        return f"Record<{key_dts_type}, {val_dts_type}>"

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            key_from_napi = "from_napi_key"
            val_from_napi = "from_napi_value"
            key_ty_napi_info.gen_from_napi(target, key_from_napi)
            val_ty_napi_info.gen_from_napi(target, val_from_napi)
            target.writelns(
                f"napi_value prop_names = nullptr;",
                f"uint32_t prop_count;",
                f"NAPI_CALL(env, napi_get_property_names(env, napi_input, &prop_names));",
                f"NAPI_CALL(env, napi_get_array_length(env, prop_names, &prop_count));",
                f"{self.cpp_info.as_owner} cpp_result;",
            )
            with target.indented(
                f"for (uint32_t i = 0; i < prop_count; i++) {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_value napi_key = nullptr;",
                    f"napi_value napi_val = nullptr;",
                    f"NAPI_CALL(env, napi_get_element(env, prop_names, i, &napi_key));",
                    f"NAPI_CALL(env, napi_get_property(env, napi_input, napi_key, &napi_val));",
                    f"cpp_result.emplace({key_from_napi}(env, napi_key), {val_from_napi}(env, napi_val));",
                )
            target.writelns(
                f"return cpp_result;",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            key_into_napi = "into_napi_key"
            val_into_napi = "into_napi_value"
            key_ty_napi_info.gen_into_napi(target, key_into_napi)
            val_ty_napi_info.gen_into_napi(target, val_into_napi)
            target.writelns(
                f"napi_value napi_result;",
                f"napi_create_object(env, &napi_result);",
            )
            with target.indented(
                f"for (const auto& [cpp_key, cpp_val] : cpp_value) {{",
                f"}}",
            ):
                target.writelns(
                    f"NAPI_CALL(env, napi_set_property(env, napi_result, {key_into_napi}(env, cpp_key), {val_into_napi}(env, cpp_val)));",
                )
            target.writelns(
                f"return napi_result;",
            )


class MapTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = False

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)
        key_dts_type = key_ty_napi_info.dts_type_in(target)
        val_dts_type = val_ty_napi_info.dts_type_in(target)
        return f"Map<{key_dts_type}, {val_dts_type}>"

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            key_from_napi = "from_napi_key"
            val_from_napi = "from_napi_value"
            key_ty_napi_info.gen_from_napi(target, key_from_napi)
            val_ty_napi_info.gen_from_napi(target, val_from_napi)
            target.writelns(
                f"{self.cpp_info.as_owner} cpp_result;",
                f"napi_value entries_fn = nullptr;",
                f"napi_value entries_iter = nullptr;",
                f'NAPI_CALL(env, napi_get_named_property(env, napi_input, "entries", &entries_fn));',
                f"NAPI_CALL(env, napi_call_function(env, napi_input, entries_fn, 0, nullptr, &entries_iter));",
                f"napi_value next_meth = nullptr;",
                f'NAPI_CALL(env, napi_get_named_property(env, entries_iter, "next", &next_meth));',
            )
            with target.indented(
                f"while (true) {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_value next_result;",
                    f"NAPI_CALL(env, napi_call_function(env, entries_iter, next_meth, 0, nullptr, &next_result));",
                    f"bool done;",
                    f"napi_value done_prop;",
                    f'NAPI_CALL(env, napi_get_named_property(env, next_result, "done", &done_prop));',
                    f"NAPI_CALL(env, napi_get_value_bool(env, done_prop, &done));",
                    f"if (done) break;",
                    f"napi_value value_prop, napi_key, napi_val;",
                    f'NAPI_CALL(env, napi_get_named_property(env, next_result, "value", &value_prop));',
                    f"NAPI_CALL(env, napi_get_element(env, value_prop, 0, &napi_key));",
                    f"NAPI_CALL(env, napi_get_element(env, value_prop, 1, &napi_val));",
                    f"cpp_result.emplace({key_from_napi}(env, napi_key), {val_from_napi}(env, napi_val));",
                )
            target.writelns(
                f"return cpp_result;",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        key_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        val_ty_napi_info = TypeNapiInfo.get(self.am, self.type.val_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            key_into_napi = "into_napi_key"
            val_into_napi = "into_napi_value"
            key_ty_napi_info.gen_into_napi(target, key_into_napi)
            val_ty_napi_info.gen_into_napi(target, val_into_napi)
            target.writelns(
                f"napi_value global = nullptr;",
                f"napi_value map_ctor = nullptr;",
                f"napi_value napi_result = nullptr;",
                f"napi_get_global(env, &global);",
                f'NAPI_CALL(env, napi_get_named_property(env, global, "Map", &map_ctor));',
                f"NAPI_CALL(env, napi_new_instance(env, map_ctor, 0, nullptr, &napi_result));",
                f"napi_value set_fn = nullptr;",
                f'NAPI_CALL(env, napi_get_named_property(env, napi_result, "set", &set_fn));',
            )
            with target.indented(
                f"for (const auto& [cpp_key, cpp_val] : cpp_value) {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_value args[2] = {{{key_into_napi}(env, cpp_key), {val_into_napi}(env, cpp_val)}};",
                    f"NAPI_CALL(env, napi_call_function(env, napi_result, set_fn, 2, args, nullptr));",
                )
            target.writelns(
                f"return napi_result;",
            )

    @override
    def gen_check_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> bool {{",
            f"}};",
        ):
            target.writelns(
                f"napi_value global = nullptr;",
                f"napi_value map_ctor = nullptr;",
                f"bool result = false;",
                f"return napi_get_global(env, &global) == napi_ok",
                f'    && napi_get_named_property(env, global, "Map", &map_ctor) == napi_ok',
                f"    && napi_instanceof(env, napi_input, map_ctor, &result) == napi_ok",
                f"    && result;",
            )


class SetTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: SetType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = False

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        item_dts_type = item_ty_napi_info.dts_type_in(target)
        return f"Set<{item_dts_type}>"

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            item_from_napi = "from_napi_item"
            item_ty_napi_info.gen_from_napi(target, item_from_napi)
            target.writelns(
                f"{self.cpp_info.as_owner} cpp_result;",
                f"napi_value values_fn = nullptr;",
                f"napi_value values_iter = nullptr;",
                f'NAPI_CALL(env, napi_get_named_property(env, napi_input, "values", &values_fn));',
                f"NAPI_CALL(env, napi_call_function(env, napi_input, values_fn, 0, nullptr, &values_iter));",
                f"napi_value next_meth = nullptr;",
                f'NAPI_CALL(env, napi_get_named_property(env, values_iter, "next", &next_meth));',
            )
            with target.indented(
                f"while (true) {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_value next_result;",
                    f"NAPI_CALL(env, napi_call_function(env, values_iter, next_meth, 0, nullptr, &next_result));",
                    f"bool done;",
                    f"napi_value done_prop;",
                    f'NAPI_CALL(env, napi_get_named_property(env, next_result, "done", &done_prop));',
                    f"NAPI_CALL(env, napi_get_value_bool(env, done_prop, &done));",
                    f"if (done) break;",
                    f"napi_value value_prop;",
                    f'NAPI_CALL(env, napi_get_named_property(env, next_result, "value", &value_prop));',
                    f"cpp_result.emplace({item_from_napi}(env, value_prop));",
                )
            target.writelns(
                f"return cpp_result;",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.key_ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            item_into_napi = "into_napi_item"
            item_ty_napi_info.gen_into_napi(target, item_into_napi)
            target.writelns(
                f"napi_value global = nullptr;",
                f"napi_value set_ctor = nullptr;",
                f"napi_value napi_result = nullptr;",
                f"napi_get_global(env, &global);",
                f'NAPI_CALL(env, napi_get_named_property(env, global, "Set", &set_ctor));',
                f"NAPI_CALL(env, napi_new_instance(env, set_ctor, 0, nullptr, &napi_result));",
                f"napi_value add_fn = nullptr;",
                f'NAPI_CALL(env, napi_get_named_property(env, napi_result, "add", &add_fn));',
            )
            with target.indented(
                f"for (const auto& cpp_item : cpp_value) {{",
                f"}}",
            ):
                target.writelns(
                    f"napi_value args[1] = {{{item_into_napi}(env, cpp_item)}};",
                    f"NAPI_CALL(env, napi_call_function(env, napi_result, add_fn, 1, args, nullptr));",
                )
            target.writelns(
                f"return napi_result;",
            )

    @override
    def gen_check_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> bool {{",
            f"}};",
        ):
            target.writelns(
                f"napi_value global = nullptr;",
                f"napi_value set_ctor = nullptr;",
                f"bool result = false;",
                f"return napi_get_global(env, &global) == napi_ok",
                f'    && napi_get_named_property(env, global, "Set", &set_ctor) == napi_ok',
                f"    && napi_instanceof(env, napi_input, set_ctor, &result) == napi_ok",
                f"    && result;",
            )


class UnionTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: UnionType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = False

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        union_napi_info = UnionNapiInfo.get(self.am, self.type.decl)
        return union_napi_info.dts_type_in(target)

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        union_napi_info = UnionNapiInfo.get(self.am, self.type.decl)
        union_cpp_info = UnionCppInfo.get(self.am, self.type.decl)
        target.add_include(union_napi_info.impl_header)
        target.writelns(
            f"static constexpr auto {name} = ::taihe::from_napi<{union_cpp_info.as_owner}>;",
        )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        union_napi_info = UnionNapiInfo.get(self.am, self.type.decl)
        union_cpp_info = UnionCppInfo.get(self.am, self.type.decl)
        target.add_include(union_napi_info.impl_header)
        target.writelns(
            f"static constexpr auto {name} = ::taihe::into_napi<{union_cpp_info.as_owner}>;",
        )


class OpaqueTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: OpaqueType) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = True

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        if dts_type_attr := DtsTypeAttr.get(self.type.ref):
            return dts_type_attr.type_name
        else:
            return "Object"

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"return reinterpret_cast<{self.cpp_info.as_owner}>(napi_input);",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            target.writelns(
                f"return reinterpret_cast<napi_value>(cpp_value);",
            )


class ConstEnumTypeNapiInfo(TypeNapiInfo):
    def __init__(self, am: AnalysisManager, t: EnumType):
        super().__init__(am, t)
        self.am = am
        self.type = t
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
        self.napi_valuetype = item_ty_napi_info.napi_valuetype

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
        return ty_napi_info.dts_type_in(target)

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            item_ty_napi_info.gen_from_napi(target, "from_napi_item")
            target.writelns(
                f"return {self.cpp_info.as_owner}::from_value(from_napi_item(env, napi_input));",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        item_ty_napi_info = TypeNapiInfo.get(self.am, self.type.decl.ty)
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            item_ty_napi_info.gen_into_napi(target, "into_napi_item")
            target.writelns(
                f"return into_napi_item(env, cpp_value.get_value());",
            )


class BigIntTypeNapiInfo(TypeNapiInfo):
    def __init__(
        self,
        am: AnalysisManager,
        t: ArrayType,
    ) -> None:
        super().__init__(am, t)
        self.am = am
        self.type = t
        self.napi_valuetype = "napi_bigint"
        if not (
            isinstance(self.type.item_ty, ScalarType)
            and self.type.item_ty.kind == ScalarKinds.U64
        ):
            raise ValueError(
                "Attribute bigint can only be attached to array types with u64 items"
            )

    @override
    def dts_type_in(self, target: DtsWriter) -> str:
        return "bigint"

    @override
    def gen_from_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, napi_value napi_input) -> {self.cpp_info.as_owner} {{",
            f"}};",
        ):
            target.writelns(
                f"size_t size = 0;",
                f"int sign = 0;",
                f"NAPI_CALL(env, napi_get_value_bigint_words(env, napi_input, nullptr, &size, nullptr));",
                f"taihe::array<uint64_t> words(size);",
                f"NAPI_CALL(env, napi_get_value_bigint_words(env, napi_input, &sign, &size, words.data()));",
                f"return taihe::_build_num(sign, words);",
            )

    @override
    def gen_into_napi(self, target: CSourceWriter, name: str):
        with target.indented(
            f"static constexpr auto {name} = [](napi_env env, {self.cpp_info.as_param} cpp_value) -> napi_value {{",
            f"}};",
        ):
            target.writelns(
                f"napi_value napi_result = nullptr;",
                f"auto [sign, abs] = ::taihe::_get_bigint_sign_and_abs(cpp_value);",
                f"NAPI_CALL(env, napi_create_bigint_words(env, sign, abs.size(), abs.data(), &napi_result));",
                f"return napi_result;",
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
            return ConstEnumTypeNapiInfo(self.am, t)
        return EnumTypeNapiInfo(self.am, t)

    @override
    def visit_array_type(self, t: ArrayType) -> TypeNapiInfo:
        if BigIntAttr.get(t.ref):
            return BigIntTypeNapiInfo(self.am, t)
        if ArrayBufferAttr.get(t.ref):
            return ArrayBufferTypeNapiInfo(self.am, t)
        if TypedArrayAttr.get(t.ref):
            return TypedArrayTypeNapiInfo(self.am, t)
        return ArrayTypeNapiInfo(self.am, t)

    @override
    def visit_set_type(self, t: SetType) -> TypeNapiInfo:
        return SetTypeNapiInfo(self.am, t)

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
        if UndefinedAttr.get(t.ref):
            return UndefinedTypeNapiInfo(self.am, t)
        if NullAttr.get(t.ref):
            return NullTypeNapiInfo(self.am, t)
        return NullTypeNapiInfo(self.am, t)
