# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Huawei Device Co., Ltd.
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

import re
from collections.abc import Hashable

from typing_extensions import override

from taihe.semantics.declarations import IfaceDecl, IfaceMethodDecl, PackageDecl
from taihe.semantics.types import (
    ArrayType,
    EnumType,
    IfaceType,
    MapType,
    ScalarKinds,
    ScalarType,
    SetType,
    StringType,
    StructType,
    UnitType,
    VectorType,
    VoidType,
)
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager


def camel_to_snake(name):
    """Converts camelCase to UPPER_SNAKE_CASE."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).upper()


def strip_leading_interface_i(name: str) -> str:
    if len(name) > 1 and name.startswith("I") and name[1].isupper():
        return name[1:]
    return name


def type_name_to_file_stem(name: str) -> str:
    core = strip_leading_interface_i(name)
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", core)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def package_name_to_file_stem(name: str) -> str:
    return "_".join(type_name_to_file_stem(segment) for segment in name.split("."))


def resolved_codegen_package_name(pkg: PackageDecl) -> str | None:
    # Try to get @!namespace attribute (standard Taihe IDL format)
    from taihe.codegen.ohipc.attribute import NamespaceAttr

    ns_attr = NamespaceAttr.get(pkg)
    if ns_attr is not None:
        # Combine module and namespace path
        parts = [ns_attr.module]
        if ns_attr.namespace:
            parts.extend(ns_attr.namespace.split("."))
        return ".".join(parts)

    # No namespace attribute, return None to indicate no namespace
    return None


def namespace_segments_for_cpp(pkg: PackageDecl) -> list[str]:
    resolved = resolved_codegen_package_name(pkg)
    if resolved:
        return resolved.split(".")
    # No namespace, return empty list
    return []


def namespace_scope_for_cpp(pkg: PackageDecl) -> str:
    segments = namespace_segments_for_cpp(pkg)
    if not segments:
        return ""  # No namespace
    return "::".join(segments)


def interface_descriptor_for_cpp(iface: IfaceDecl) -> str:
    segments = namespace_segments_for_cpp(iface.parent_pkg)
    if not segments:
        return iface.name
    return ".".join([*segments, iface.name])


def header_guard_for(name: str, pkg: PackageDecl) -> str:
    parts = [camel_to_snake(segment) for segment in namespace_segments_for_cpp(pkg)]
    guard = camel_to_snake(name)
    if guard.startswith("I_"):
        guard = f"I{guard[2:]}"
    parts.append(guard)
    return f"{'_'.join(parts)}_H"


def qualified_decl_name_for_cpp(decl) -> str:
    ns = namespace_scope_for_cpp(decl.parent_pkg)
    if ns:
        return f"{ns}::{decl.name}"
    return decl.name


def fixed_array_size(t: ArrayType) -> int:
    from taihe.codegen.ohipc.attribute import SizeAttribute

    if attr := SizeAttribute.get(t.ref):
        return attr.size
    raise ValueError(
        f"OHIPC Array type '{t.signature}' requires @size(N) on the array type."
    )


class TypeCppInfo(AbstractAnalysis[Hashable]):
    def __init__(self, as_owner: str, as_param: str | None = None) -> None:
        self.as_owner = as_owner
        self.as_param = as_owner if as_param is None else as_param

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, ty) -> "TypeCppInfo":
        if isinstance(ty, ScalarType):
            return ScalarTypeCppInfo(am, ty)
        if isinstance(ty, StringType):
            return StringTypeCppInfo(am, ty)
        if isinstance(ty, IfaceType):
            return IfaceTypeCppInfo(am, ty)
        if isinstance(ty, VectorType):
            return VectorTypeCppInfo(am, ty)
        if isinstance(ty, ArrayType):
            return ArrayTypeCppInfo(am, ty)
        if isinstance(ty, MapType):
            return MapTypeCppInfo(am, ty)
        if isinstance(ty, SetType):
            return SetTypeCppInfo(am, ty)
        if isinstance(ty, StructType):
            return StructTypeCppInfo(am, ty)
        if isinstance(ty, EnumType):
            return EnumTypeCppInfo(am, ty)
        if isinstance(ty, UnitType | VoidType):
            return UnitTypeCppInfo(am, ty)
        return TypeCppInfo("int32_t")


class ScalarTypeCppInfo(TypeCppInfo):
    def __init__(self, am: AnalysisManager, t: ScalarType) -> None:
        super().__init__(
            {
                ScalarKinds.BOOL: "bool",
                ScalarKinds.I8: "int8_t",
                ScalarKinds.I16: "int16_t",
                ScalarKinds.I32: "int32_t",
                ScalarKinds.I64: "int64_t",
                ScalarKinds.U8: "uint8_t",
                ScalarKinds.U16: "uint16_t",
                ScalarKinds.U32: "uint32_t",
                ScalarKinds.U64: "uint64_t",
                ScalarKinds.F32: "float",
                ScalarKinds.F64: "double",
            }.get(t.kind, "int32_t")
        )


class StringTypeCppInfo(TypeCppInfo):
    def __init__(self, am: AnalysisManager, t: StringType) -> None:
        super().__init__("std::string", "const std::string&")


class IfaceTypeCppInfo(TypeCppInfo):
    def __init__(self, am: AnalysisManager, t: IfaceType) -> None:
        owner = f"{qualified_decl_name_for_cpp(t.decl)}*"
        super().__init__(owner, f"const {qualified_decl_name_for_cpp(t.decl)}&")


class ArrayTypeCppInfo(TypeCppInfo):
    def __init__(self, am: AnalysisManager, t: ArrayType) -> None:
        item_ty_cpp_info = TypeCppInfo.get(am, t.item_ty)
        size = fixed_array_size(t)
        owner = f"std::array<{item_ty_cpp_info.as_owner}, {size}>"
        super().__init__(owner, f"const {owner}&")


class VectorTypeCppInfo(TypeCppInfo):
    def __init__(self, am: AnalysisManager, t: VectorType) -> None:
        val_ty_cpp_info = TypeCppInfo.get(am, t.val_ty)
        owner = f"std::vector<{val_ty_cpp_info.as_owner}>"
        super().__init__(owner, f"const {owner}&")


class MapTypeCppInfo(TypeCppInfo):
    def __init__(self, am: AnalysisManager, t: MapType) -> None:
        key_ty_cpp_info = TypeCppInfo.get(am, t.key_ty)
        val_ty_cpp_info = TypeCppInfo.get(am, t.val_ty)
        owner = f"std::map<{key_ty_cpp_info.as_owner}, {val_ty_cpp_info.as_owner}>"
        super().__init__(owner, f"const {owner}&")


class SetTypeCppInfo(TypeCppInfo):
    def __init__(self, am: AnalysisManager, t: SetType) -> None:
        key_ty_cpp_info = TypeCppInfo.get(am, t.key_ty)
        owner = f"std::set<{key_ty_cpp_info.as_owner}>"
        super().__init__(owner, f"const {owner}&")


class StructTypeCppInfo(TypeCppInfo):
    def __init__(self, am: AnalysisManager, t: StructType) -> None:
        owner = qualified_decl_name_for_cpp(t.decl)
        super().__init__(owner, f"const {owner}&")


class EnumTypeCppInfo(TypeCppInfo):
    def __init__(self, am: AnalysisManager, t: EnumType) -> None:
        super().__init__(qualified_decl_name_for_cpp(t.decl))


class UnitTypeCppInfo(TypeCppInfo):
    def __init__(self, am: AnalysisManager, t: UnitType | VoidType) -> None:
        super().__init__("void")


class MethodOhIpcInfo(AbstractAnalysis[IfaceMethodDecl]):
    def __init__(self, am: AnalysisManager, m: IfaceMethodDecl) -> None:
        # Default IPC code starts from 1001
        self.ipc_code = 1001
        self.is_oneway = False

        # Check explicit backend attributes attached on OHIDL declarations.
        from taihe.codegen.ohipc.attribute import IpcCodeAttribute, OnewayAttribute

        if attr := IpcCodeAttribute.get(m):
            self.ipc_code = attr.code
        if OnewayAttribute.get(m) is not None:
            self.is_oneway = True

        self.command_name = f"COMMAND_{camel_to_snake(m.name)}"

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, m: IfaceMethodDecl) -> "MethodOhIpcInfo":
        return MethodOhIpcInfo(am, m)


class IfaceOhIpcInfo(AbstractAnalysis[IfaceDecl]):
    def __init__(self, am: AnalysisManager, d: IfaceDecl) -> None:
        # Check for duplicate method names since C doesn't support overloading
        method_names = set()
        for method in d.methods:
            if method.name in method_names:
                raise ValueError(
                    f"Duplicate method name '{method.name}' in interface '{d.name}'. C language does not support function overloading."
                )
            method_names.add(method.name)

        self.namespace = namespace_scope_for_cpp(d.parent_pkg)
        self.interface_name = d.name
        base_name = strip_leading_interface_i(d.name)
        self.proxy_name = f"{base_name}Proxy"
        self.stub_name = f"{base_name}Stub"

        self.version = "1"
        from taihe.codegen.ohipc.attribute import MainServiceAttribute

        self.is_main_service = False
        if attr := MainServiceAttribute.get(d):
            self.is_main_service = True
            self.version = attr.version

        # Load taihe_version from taihe_version.json
        import json
        from pathlib import Path

        version_file = Path(__file__).parent / "taihe_version.json"
        try:
            with open(version_file, encoding="utf-8") as f:
                data = json.load(f)
                self.taihe_version = data.get("version", "")
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            self.taihe_version = ""

        # Assign sequential IPC codes if not explicitly set
        current_code = 1001
        for method in d.methods:
            info = MethodOhIpcInfo.get(am, method)
            from taihe.codegen.ohipc.attribute import IpcCodeAttribute

            if IpcCodeAttribute.get(method) is None:
                info.ipc_code = current_code
            current_code = max(current_code + 1, info.ipc_code + 1)

        # Metadata methods are available on all generated interfaces.
        self.get_type_lib_info_code = 1
        self.get_version_code = 2
        self.get_taihe_version_code = 3

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, d: IfaceDecl) -> "IfaceOhIpcInfo":
        return IfaceOhIpcInfo(am, d)


class PackageOhIpcInfo(AbstractAnalysis[PackageDecl]):
    def __init__(self, am: AnalysisManager, p: PackageDecl) -> None:
        self.namespace = namespace_scope_for_cpp(p)

    @classmethod
    @override
    def _create(cls, am: AnalysisManager, p: PackageDecl) -> "PackageOhIpcInfo":
        return PackageOhIpcInfo(am, p)
