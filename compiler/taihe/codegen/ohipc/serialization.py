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
from taihe.codegen.ohipc.analyses import (
    TypeCppInfo,
    fixed_array_size,
    namespace_scope_for_cpp,
    strip_leading_interface_i,
)
from taihe.utils.analyses import AnalysisManager


class OhIpcSerializer:
    """Generate HarmonyOS IPC NDK C API serialization snippets."""

    def __init__(self, am: AnalysisManager, is_proxy: bool = False):
        self.am = am
        self.is_proxy = is_proxy

    @staticmethod
    def _get_loop_var_name(base_name: str, level: int) -> str:
        """Generate unique variable name based on nesting level.

        Level 0: base_name (e.g., 'i', 'sz', 'item')
        Level 1+: base_name + level (e.g., 'i1', 'sz1', 'item1')
        """
        if level == 0:
            return base_name
        return f"{base_name}{level}"

    @staticmethod
    def _qualified_decl_name(decl) -> str:
        ns = namespace_scope_for_cpp(decl.parent_pkg)
        if ns:
            return f"{ns}::{decl.name}"
        return decl.name

    @staticmethod
    def _qualified_proxy_name(decl) -> str:
        ns = namespace_scope_for_cpp(decl.parent_pkg)
        proxy_name = f"{strip_leading_interface_i(decl.name)}Proxy"
        if ns:
            return f"{ns}::{proxy_name}"
        return proxy_name

    @staticmethod
    def _qualified_stub_name(decl) -> str:
        ns = namespace_scope_for_cpp(decl.parent_pkg)
        stub_name = f"{strip_leading_interface_i(decl.name)}Stub"
        if ns:
            return f"{ns}::{stub_name}"
        return stub_name

    @staticmethod
    def _guard_return(condition: str, ret_expr: str, indent: str) -> list[str]:
        return [
            f"{indent}if ({condition}) {{",
            f"{indent}    return {ret_expr};",
            f"{indent}}}",
        ]

    def get_cpp_type(self, ty):
        return TypeCppInfo.get(self.am, ty).as_owner

    def get_cpp_param_type(self, ty):
        return TypeCppInfo.get(self.am, ty).as_param

    def empty_array_expr(self, ty: ArrayType) -> str:
        return "{}"

    def generate_write_code(
        self,
        parcel_name,
        var_name,
        ty,
        indent="    ",
        level: int = 0,
        array_size_expr: str | None = None,
        iface_by_ref: bool = False,
    ):
        lines: list[str] = []
        success = "OH_IPC_SUCCESS"
        write_err = "OH_IPC_PARCEL_WRITE_ERROR"
        check_err = "OH_IPC_CHECK_PARAM_ERROR"

        # HarmonyOS IPC NDK has no dedicated parcel API for void/unit.
        # For this type family we intentionally emit no parcel operation.
        if isinstance(ty, (UnitType, VoidType)):
            return ""

        if isinstance(ty, ScalarType):
            kind_map = {
                ScalarKinds.BOOL: ("OH_IPCParcel_WriteInt32", "(%s ? 1 : 0)"),
                ScalarKinds.I8: ("OH_IPCParcel_WriteInt8", "%s"),
                ScalarKinds.I16: ("OH_IPCParcel_WriteInt16", "%s"),
                ScalarKinds.I32: ("OH_IPCParcel_WriteInt32", "%s"),
                ScalarKinds.I64: ("OH_IPCParcel_WriteInt64", "%s"),
                ScalarKinds.U8: ("OH_IPCParcel_WriteUint8", "%s"),
                ScalarKinds.U16: ("OH_IPCParcel_WriteUint16", "%s"),
                ScalarKinds.U32: ("OH_IPCParcel_WriteUint32", "%s"),
                ScalarKinds.U64: ("OH_IPCParcel_WriteUint64", "%s"),
                ScalarKinds.F32: ("OH_IPCParcel_WriteFloat", "%s"),
                ScalarKinds.F64: ("OH_IPCParcel_WriteDouble", "%s"),
            }
            method, fmt = kind_map.get(ty.kind, ("OH_IPCParcel_WriteInt32", "%s"))
            lines.extend(
                self._guard_return(
                    f"{method}({parcel_name}, {fmt % var_name}) != {success}",
                    write_err,
                    indent,
                )
            )
        elif isinstance(ty, StringType):
            lines.extend(
                self._guard_return(
                    f"OH_IPCParcel_WriteString({parcel_name}, {var_name}.c_str()) != {success}",
                    write_err,
                    indent,
                )
            )
        elif isinstance(ty, IfaceType):
            if self.is_proxy:
                proxy_type = self._qualified_proxy_name(ty.decl)
                if not iface_by_ref:
                    lines.extend(
                        self._guard_return(
                            f"{var_name} == nullptr",
                            check_err,
                            indent,
                        )
                    )
                iface_obj = (
                    f"static_cast<const {proxy_type}&>({var_name})"
                    if iface_by_ref
                    else f"*{var_name}"
                )
                lines.append(
                    f"{indent}auto* {var_name}Proxy = {iface_obj}.GetRemoteProxy();"
                )
                lines.extend(
                    self._guard_return(
                        f"{var_name}Proxy == nullptr",
                        check_err,
                        indent,
                    )
                )
                lines.extend(
                    self._guard_return(
                        f"OH_IPCParcel_WriteRemoteProxy({parcel_name}, {var_name}Proxy) != {success}",
                        write_err,
                        indent,
                    )
                )
            else:
                stub_type = self._qualified_stub_name(ty.decl)
                if not iface_by_ref:
                    lines.extend(
                        self._guard_return(
                            f"{var_name} == nullptr",
                            check_err,
                            indent,
                        )
                    )
                if iface_by_ref:
                    iface_obj = f"static_cast<const {stub_type}&>({var_name})"
                    lines.append(
                        f"{indent}auto* {var_name}Stub = {iface_obj}.GetRemoteStub();"
                    )
                else:
                    lines.append(
                        f"{indent}auto* {var_name}Stub = "
                        f"static_cast<{stub_type}*>({var_name})->GetRemoteStub();"
                    )
                lines.extend(
                    self._guard_return(
                        f"{var_name}Stub == nullptr",
                        check_err,
                        indent,
                    )
                )
                lines.extend(
                    self._guard_return(
                        f"OH_IPCParcel_WriteRemoteStub({parcel_name}, {var_name}Stub) != {success}",
                        write_err,
                        indent,
                    )
                )
        elif isinstance(ty, EnumType):
            lines.extend(
                self._guard_return(
                    f"OH_IPCParcel_WriteInt32({parcel_name}, (int32_t){var_name}) != {success}",
                    write_err,
                    indent,
                )
            )
        elif isinstance(ty, VectorType):
            item_name = self._get_loop_var_name("item", level)
            lines.extend(
                self._guard_return(
                    f"OH_IPCParcel_WriteInt32({parcel_name}, static_cast<int32_t>({var_name}.size())) != {success}",
                    write_err,
                    indent,
                )
            )
            lines.append(f"{indent}for (const auto& {item_name} : {var_name}) {{")
            inner_ty = ty.val_ty
            lines.extend(self.generate_write_code(parcel_name, item_name, inner_ty, indent + "    ", level + 1).splitlines())
            lines.append(f"{indent}}}")
        elif isinstance(ty, ArrayType):
            fixed_size = fixed_array_size(ty)
            size_var = array_size_expr or str(fixed_size)
            item_name = self._get_loop_var_name("item", level)
            lines.extend(
                self._guard_return(
                    f"OH_IPCParcel_WriteInt32({parcel_name}, {size_var}) != {success}",
                    write_err,
                    indent,
                )
            )
            lines.append(f"{indent}for (int32_t {self._get_loop_var_name('i', level)} = 0; {self._get_loop_var_name('i', level)} < {size_var}; ++{self._get_loop_var_name('i', level)}) {{")
            inner_ty = ty.item_ty
            lines.append(f"{indent}    {self.get_cpp_type(inner_ty)} {item_name} = {var_name}[{self._get_loop_var_name('i', level)}];")
            lines.extend(self.generate_write_code(parcel_name, item_name, inner_ty, indent + "    ", level + 1).splitlines())
            lines.append(f"{indent}}}")
        elif isinstance(ty, SetType):
            item_name = self._get_loop_var_name("item", level)
            lines.extend(
                self._guard_return(
                    f"OH_IPCParcel_WriteInt32({parcel_name}, static_cast<int32_t>({var_name}.size())) != {success}",
                    write_err,
                    indent,
                )
            )
            lines.append(f"{indent}for (const auto& {item_name} : {var_name}) {{")
            lines.extend(self.generate_write_code(parcel_name, item_name, ty.key_ty, indent + "    ", level + 1).splitlines())
            lines.append(f"{indent}}}")
        elif isinstance(ty, MapType):
            key_name = self._get_loop_var_name("key", level)
            value_name = self._get_loop_var_name("val", level)
            entry_name = self._get_loop_var_name("entry", level)
            lines.extend(
                self._guard_return(
                    f"OH_IPCParcel_WriteInt32({parcel_name}, static_cast<int32_t>({var_name}.size())) != {success}",
                    write_err,
                    indent,
                )
            )
            lines.append(f"{indent}for (const auto& {entry_name} : {var_name}) {{")
            lines.append(f"{indent}    auto {key_name} = {entry_name}.first;")
            lines.append(f"{indent}    auto {value_name} = {entry_name}.second;")
            lines.extend(self.generate_write_code(parcel_name, key_name, ty.key_ty, indent + "    ", level + 1).splitlines())
            lines.extend(self.generate_write_code(parcel_name, value_name, ty.val_ty, indent + "    ", level + 1).splitlines())
            lines.append(f"{indent}}}")
        elif isinstance(ty, StructType):
            lines.extend(
                self._guard_return(
                    f"{var_name}.Marshalling({parcel_name}) != {success}",
                    write_err,
                    indent,
                )
            )

        return "\n".join(lines)

    def generate_read_code(
        self,
        parcel_name,
        var_name,
        ty,
        indent="    ",
        is_decl=True,
        level: int = 0,
        size_output_param: str | None = None,
        iface_as_object: bool = False,
    ):
        lines: list[str] = []
        success = "OH_IPC_SUCCESS"
        read_err = "OH_IPC_PARCEL_READ_ERROR"
        decl_prefix = f"{self.get_cpp_type(ty)} " if is_decl else ""

        # HarmonyOS IPC NDK has no dedicated parcel API for void/unit.
        # For this type family we intentionally emit no parcel operation.
        if isinstance(ty, (UnitType, VoidType)):
            return ""

        if isinstance(ty, ScalarType):
            kind_map = {
                ScalarKinds.BOOL: ("OH_IPCParcel_ReadInt32", "int32_t", True),
                ScalarKinds.I8: ("OH_IPCParcel_ReadInt8", "int8_t", False),
                ScalarKinds.I16: ("OH_IPCParcel_ReadInt16", "int16_t", False),
                ScalarKinds.I32: ("OH_IPCParcel_ReadInt32", "int32_t", False),
                ScalarKinds.I64: ("OH_IPCParcel_ReadInt64", "int64_t", False),
                ScalarKinds.U8: ("OH_IPCParcel_ReadUint8", "uint8_t", False),
                ScalarKinds.U16: ("OH_IPCParcel_ReadUint16", "uint16_t", False),
                ScalarKinds.U32: ("OH_IPCParcel_ReadUint32", "uint32_t", False),
                ScalarKinds.U64: ("OH_IPCParcel_ReadUint64", "uint64_t", False),
                ScalarKinds.F32: ("OH_IPCParcel_ReadFloat", "float", False),
                ScalarKinds.F64: ("OH_IPCParcel_ReadDouble", "double", False),
            }
            method, temp_type, is_bool = kind_map.get(ty.kind, ("OH_IPCParcel_ReadInt32", "int32_t", False))
            temp_name = f"{var_name}Value"
            lines.append(f"{indent}{temp_type} {temp_name} = 0;")
            lines.extend(
                self._guard_return(
                    f"{method}({parcel_name}, &{temp_name}) != {success}",
                    read_err,
                    indent,
                )
            )
            if is_bool:
                lines.append(f"{indent}{decl_prefix}{var_name} = ({temp_name} == 1);")
            else:
                lines.append(f"{indent}{decl_prefix}{var_name} = {temp_name};")
        elif isinstance(ty, StringType):
            tmp_name = f"{var_name}Raw"
            lines.append(f"{indent}const char* {tmp_name} = OH_IPCParcel_ReadString({parcel_name});")
            lines.extend(self._guard_return(f"{tmp_name} == nullptr", read_err, indent))
            lines.append(f"{indent}{decl_prefix}{var_name} = {tmp_name};")
        elif isinstance(ty, IfaceType):
            proxy_var = f"{var_name}Proxy"
            lines.append(f"{indent}OHIPCRemoteProxy* {proxy_var} = OH_IPCParcel_ReadRemoteProxy({parcel_name});")
            lines.extend(self._guard_return(f"{proxy_var} == nullptr", read_err, indent))
            if iface_as_object:
                obj_decl_prefix = f"{self._qualified_proxy_name(ty.decl)} " if is_decl else ""
                lines.append(
                    f"{indent}{obj_decl_prefix}{var_name} = {self._qualified_proxy_name(ty.decl)}({proxy_var});"
                )
            else:
                lines.append(
                    f"{indent}{decl_prefix}{var_name} = new {self._qualified_proxy_name(ty.decl)}({proxy_var});"
                )
        elif isinstance(ty, EnumType):
            tmp_name = f"{var_name}Value"
            lines.append(f"{indent}int32_t {tmp_name} = 0;")
            lines.extend(
                self._guard_return(
                    f"OH_IPCParcel_ReadInt32({parcel_name}, &{tmp_name}) != {success}",
                    read_err,
                    indent,
                )
            )
            lines.append(f"{indent}{decl_prefix}{var_name} = ({self.get_cpp_type(ty)}){tmp_name};")
        elif isinstance(ty, VectorType):
            sz_name = self._get_loop_var_name("sz", level)
            i_name = self._get_loop_var_name("i", level)
            item_name = self._get_loop_var_name("item", level)
            if is_decl:
                lines.append(f"{indent}{decl_prefix}{var_name};")
            else:
                lines.append(f"{indent}{var_name}.clear();")
            lines.append(f"{indent}int32_t {sz_name} = 0;")
            lines.extend(
                self._guard_return(
                    f"OH_IPCParcel_ReadInt32({parcel_name}, &{sz_name}) != {success}",
                    read_err,
                    indent,
                )
            )
            lines.append(f"{indent}for (int32_t {i_name} = 0; {i_name} < {sz_name}; ++{i_name}) {{")
            inner_ty = ty.val_ty
            lines.extend(self.generate_read_code(parcel_name, item_name, inner_ty, indent + "    ", is_decl=True, level=level + 1).splitlines())
            lines.append(f"{indent}    {var_name}.push_back({item_name});")
            lines.append(f"{indent}}}")
        elif isinstance(ty, ArrayType):
            fixed_size = fixed_array_size(ty)
            sz_name = self._get_loop_var_name("sz", level)
            i_name = self._get_loop_var_name("i", level)
            item_name = self._get_loop_var_name("item", level)
            array_cpp_type = self.get_cpp_type(ty)
            lines.append(f"{indent}int32_t {sz_name} = 0;")
            lines.extend(
                self._guard_return(
                    f"OH_IPCParcel_ReadInt32({parcel_name}, &{sz_name}) != {success}",
                    read_err,
                    indent,
                )
            )
            lines.extend(
                self._guard_return(
                    f"{sz_name} != {fixed_size}",
                    read_err,
                    indent,
                )
            )
            if is_decl:
                lines.append(f"{indent}{array_cpp_type} {var_name} = {self.empty_array_expr(ty)};")
            else:
                lines.append(f"{indent}{var_name} = {self.empty_array_expr(ty)};")
            lines.append(f"{indent}for (int32_t {i_name} = 0; {i_name} < {sz_name}; ++{i_name}) {{")
            inner_ty = ty.item_ty
            lines.extend(self.generate_read_code(parcel_name, item_name, inner_ty, indent + "    ", is_decl=True, level=level + 1).splitlines())
            lines.append(f"{indent}    {var_name}[static_cast<size_t>({i_name})] = {item_name};")
            lines.append(f"{indent}}}")
            if size_output_param:
                lines.append(f"{indent}{size_output_param} = {fixed_size};")
        elif isinstance(ty, SetType):
            sz_name = self._get_loop_var_name("sz", level)
            i_name = self._get_loop_var_name("i", level)
            item_name = self._get_loop_var_name("item", level)
            if is_decl:
                lines.append(f"{indent}{decl_prefix}{var_name};")
            else:
                lines.append(f"{indent}{var_name}.clear();")
            lines.append(f"{indent}int32_t {sz_name} = 0;")
            lines.extend(
                self._guard_return(
                    f"OH_IPCParcel_ReadInt32({parcel_name}, &{sz_name}) != {success}",
                    read_err,
                    indent,
                )
            )
            lines.append(f"{indent}for (int32_t {i_name} = 0; {i_name} < {sz_name}; ++{i_name}) {{")
            lines.extend(self.generate_read_code(parcel_name, item_name, ty.key_ty, indent + "    ", is_decl=True, level=level + 1).splitlines())
            lines.append(f"{indent}    {var_name}.insert({item_name});")
            lines.append(f"{indent}}}")
        elif isinstance(ty, MapType):
            sz_name = self._get_loop_var_name("sz", level)
            i_name = self._get_loop_var_name("i", level)
            key_name = self._get_loop_var_name("key", level)
            value_name = self._get_loop_var_name("val", level)
            if is_decl:
                lines.append(f"{indent}{decl_prefix}{var_name};")
            else:
                lines.append(f"{indent}{var_name}.clear();")
            lines.append(f"{indent}int32_t {sz_name} = 0;")
            lines.extend(
                self._guard_return(
                    f"OH_IPCParcel_ReadInt32({parcel_name}, &{sz_name}) != {success}",
                    read_err,
                    indent,
                )
            )
            lines.append(f"{indent}for (int32_t {i_name} = 0; {i_name} < {sz_name}; ++{i_name}) {{")
            lines.extend(self.generate_read_code(parcel_name, key_name, ty.key_ty, indent + "    ", is_decl=True, level=level + 1).splitlines())
            lines.extend(self.generate_read_code(parcel_name, value_name, ty.val_ty, indent + "    ", is_decl=True, level=level + 1).splitlines())
            lines.append(f"{indent}    {var_name}.erase({key_name});")
            lines.append(f"{indent}    {var_name}.emplace({key_name}, {value_name});")
            lines.append(f"{indent}}}")
        elif isinstance(ty, StructType):
            if is_decl:
                lines.append(f"{indent}{decl_prefix}{var_name};")
            lines.extend(
                self._guard_return(
                    f"{var_name}.Unmarshalling({parcel_name}) != {success}",
                    read_err,
                    indent,
                )
            )

        return "\n".join(lines)
