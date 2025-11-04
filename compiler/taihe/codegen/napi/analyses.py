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

from typing_extensions import override

from taihe.codegen.abi.mangle import DeclKind, encode
from taihe.codegen.abi.writer import CSourceWriter
from taihe.codegen.ani.attributes import (
    NamespaceAttr,
)
from taihe.codegen.cpp.analyses import (
    TypeCppInfo,
)
from taihe.codegen.napi.writer import DtsWriter
from taihe.semantics.declarations import (
    GlobFuncDecl,
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    PackageGroup,
)
from taihe.semantics.types import (
    NonVoidType,
    ScalarKind,
    ScalarType,
    StringType,
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


class GlobFuncNapiInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        self.ctor_class_name = None
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


class TypeNapiInfoDispatcher(NonVoidTypeVisitor[TypeNapiInfo]):
    def __init__(self, am: AnalysisManager):
        self.am = am

    @override
    def visit_scalar_type(self, t: ScalarType) -> TypeNapiInfo:
        return ScalarTypeNapiInfo(self.am, t)

    @override
    def visit_string_type(self, t: StringType) -> TypeNapiInfo:
        return StringTypeNapiInfo(self.am, t)
