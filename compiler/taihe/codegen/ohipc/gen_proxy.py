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

from datetime import datetime

from taihe.codegen.ohipc.analyses import (
    IfaceOhIpcInfo,
    MethodOhIpcInfo,
    header_guard_for,
    namespace_scope_for_cpp,
    type_name_to_file_stem,
)
from taihe.codegen.ohipc.serialization import OhIpcSerializer
from taihe.semantics.declarations import IfaceDecl
from taihe.semantics.types import (
    ArrayType,
    IfaceType,
    MapType,
    SetType,
    StructType,
    VectorType,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import OutputManager


class ProxyGenerator:
    MAX_LINE_LENGTH = 120

    @staticmethod
    def _array_size_name(name: str) -> str:
        return f"{name}Size"

    @staticmethod
    def _write_namespace_open(f, namespace: str):
        parts = namespace.split("::") if namespace else []
        for part in parts:
            f.write(f"namespace {part} {{\n")
        f.write("\n")

    @staticmethod
    def _write_namespace_close(f, namespace: str):
        parts = namespace.split("::") if namespace else []
        for part in reversed(parts):
            f.write(f"}} // namespace {part}\n")

    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am
        self.serializer = OhIpcSerializer(am, is_proxy=True)

    @staticmethod
    def _split_long_lines(text: str) -> str:
        """Split long lines in the given text to ensure no line exceeds MAX_LINE_LENGTH."""
        lines = text.splitlines()
        result = []
        for line in lines:
            if len(line) <= ProxyGenerator.MAX_LINE_LENGTH:
                result.append(line)
            else:
                # Simple split: find a good place to break, like after '='
                if " = " in line:
                    idx = line.find(" = ")
                    prefix = line[: idx + len(" = ")]
                    rest = line[idx + len(" = ") :]
                    if len(prefix) + len(rest) > ProxyGenerator.MAX_LINE_LENGTH:
                        result.append(prefix.rstrip())
                        result.append("        " + rest)
                    else:
                        result.append(line)
                else:
                    result.append(line)  # Keep as is if can't split nicely
        return "\n".join(result)

    @staticmethod
    def _iface_file_stem(iface: IfaceDecl) -> str:
        return f"i{type_name_to_file_stem(iface.name)}"

    @staticmethod
    def _proxy_file_stem(info: IfaceOhIpcInfo) -> str:
        return f"{type_name_to_file_stem(info.interface_name)}_proxy"

    def generate(self, iface: IfaceDecl):
        info = IfaceOhIpcInfo.get(self.am, iface)
        self._generate_header(iface, info)
        self._generate_source(iface, info)

    @staticmethod
    def _param_mode(param) -> str:
        return "in"

    def _append_method_param_parts(
        self, parts: list[str], method, name: str, ty, is_output: bool = False
    ):
        cpp_type = (
            self.serializer.get_cpp_type(ty)
            if is_output
            else self.serializer.get_cpp_param_type(ty)
        )
        if is_output:
            parts.append(f"{cpp_type}& {name}")
            return

        parts.append(f"{cpp_type} {name}")

    def _method_param_parts(self, method) -> list[str]:
        parts = []
        for param in method.params:
            self._append_method_param_parts(parts, method, param.name, param.ty)
        ret_type = (
            self.serializer.get_cpp_type(method.return_ty)
            if method.return_ty
            else "void"
        )
        if ret_type != "void":
            self._append_method_param_parts(
                parts,
                method,
                self._result_param_name(method),
                method.return_ty,
                is_output=True,
            )
        return parts

    @staticmethod
    def _result_param_name(method) -> str:
        existing_names = {str(param.name) for param in method.params}
        if "result" not in existing_names:
            return "result"
        candidate = "returnValue"
        while candidate in existing_names:
            candidate += "Value"
        return candidate

    @staticmethod
    def _write_cpp_signature(f, ret_type: str, scope_name: str, params: list[str]):
        prefix = f"{ret_type} {scope_name}("
        one_line = prefix + ", ".join(params) + ")"
        if len(one_line) <= ProxyGenerator.MAX_LINE_LENGTH:
            f.write(one_line + "\n")
            return

        f.write(prefix + "\n")
        indent = "    "
        current = indent
        for idx, param in enumerate(params):
            frag = param + (")" if idx == len(params) - 1 else ",")
            separator = "" if current == indent else " "
            candidate = current + separator + frag
            if len(candidate) <= ProxyGenerator.MAX_LINE_LENGTH:
                current = candidate
            else:
                if current != indent:
                    f.write(current.rstrip() + "\n")
                current = indent + frag
        f.write(current.rstrip() + "\n")

    @staticmethod
    def _write_method_declaration(
        f, indent: str, ret_type: str, name: str, params: list[str], suffix: str
    ):
        prefix = f"{indent}{ret_type} {name}("
        one_line = prefix + ", ".join(params) + ")" + suffix
        if len(one_line) <= ProxyGenerator.MAX_LINE_LENGTH:
            f.write(one_line + "\n")
            return

        f.write(prefix + "\n")
        continuation = indent + "    "
        current = continuation
        for idx, param in enumerate(params):
            frag = param + (")" + suffix if idx == len(params) - 1 else ",")
            separator = "" if current == continuation else " "
            candidate = current + separator + frag
            if len(candidate) <= ProxyGenerator.MAX_LINE_LENGTH:
                current = candidate
            else:
                if current != continuation:
                    f.write(current.rstrip() + "\n")
                current = continuation + frag
        f.write(current.rstrip() + "\n")

    @staticmethod
    def _write_if_return(f, indent: str, condition: str, ret_expr: str):
        f.write(f"{indent}if ({condition}) {{\n")
        f.write(f"{indent}    return {ret_expr};\n")
        f.write(f"{indent}}}\n")

    def _collect_proxy_headers(self, ty, headers: set[str]):
        if isinstance(ty, IfaceType):
            headers.add(f"{type_name_to_file_stem(ty.decl.name)}_proxy.h")
            return
        if isinstance(ty, VectorType):
            self._collect_proxy_headers(ty.val_ty, headers)
            return
        if isinstance(ty, ArrayType):
            self._collect_proxy_headers(ty.item_ty, headers)
            return
        if isinstance(ty, MapType):
            self._collect_proxy_headers(ty.key_ty, headers)
            self._collect_proxy_headers(ty.val_ty, headers)
            return
        if isinstance(ty, SetType):
            self._collect_proxy_headers(ty.key_ty, headers)
            return
        if isinstance(ty, StructType):
            for field in ty.decl.fields:
                self._collect_proxy_headers(field.ty, headers)

    def _source_proxy_headers(
        self, iface: IfaceDecl, info: IfaceOhIpcInfo
    ) -> list[str]:
        headers: set[str] = set()
        for method in iface.methods:
            for param in method.params:
                self._collect_proxy_headers(param.ty, headers)
            self._collect_proxy_headers(method.return_ty, headers)
        headers.discard(f"{self._proxy_file_stem(info)}.h")
        return sorted(headers)

    def _generate_header(self, iface: IfaceDecl, info: IfaceOhIpcInfo):
        filename = f"{self._proxy_file_stem(info)}.h"
        guard = header_guard_for(info.proxy_name, iface.parent_pkg)
        namespace = namespace_scope_for_cpp(iface.parent_pkg)
        current_year = datetime.now().year

        with self.om.open(filename) as f:
            f.write(f"""/*
 * Copyright (c) {current_year} Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the \"License\");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an \"AS IS\" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef {guard}
#define {guard}

#include \"{self._iface_file_stem(iface)}.h\"

""")
            self._write_namespace_open(f, namespace)
            f.write(f"class {info.proxy_name} : public {iface.name} {{\npublic:\n")
            f.write(
                f"    explicit {info.proxy_name}(OHIPCRemoteProxy* remote) : remote_(remote) {{}}\n"
            )
            f.write(f"    ~{info.proxy_name}() override = default;\n\n")
            f.write(
                "    OHIPCRemoteProxy* GetRemoteProxy() const\n    {\n        return remote_;\n    }\n\n"
            )
            for method in iface.methods:
                self._write_method_declaration(
                    f,
                    "    ",
                    "ErrCode",
                    method.name,
                    self._method_param_parts(method),
                    " override;",
                )

            if info.is_main_service:
                self._write_method_declaration(
                    f,
                    "    ",
                    "ErrCode",
                    "GetTypeLibInfo",
                    ["int32_t fd"],
                    " override;",
                )
            self._write_method_declaration(
                f,
                "    ",
                "ErrCode",
                "GetVersion",
                ["std::string& result"],
                " override;",
            )
            self._write_method_declaration(
                f,
                "    ",
                "ErrCode",
                "GetTaiheVersion",
                ["std::string& result"],
                " override;",
            )

            f.write("\nprivate:\n")
            f.write("    OHIPCRemoteProxy* remote_ = nullptr;\n")
            f.write("};\n")
            if namespace:
                f.write("\n")
            self._write_namespace_close(f, namespace)
            f.write(f"\n#endif // {guard}\n")

    def _generate_source(self, iface: IfaceDecl, info: IfaceOhIpcInfo):
        filename = f"{self._proxy_file_stem(info)}.cpp"
        namespace = namespace_scope_for_cpp(iface.parent_pkg)
        current_year = datetime.now().year

        with self.om.open(filename) as f:
            f.write(f"""/*
 * Copyright (c) {current_year} Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the \"License\");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an \"AS IS\" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include \"{self._proxy_file_stem(info)}.h\"
""")
            for header in self._source_proxy_headers(iface, info):
                f.write(f'#include "{header}"\n')
            f.write("\n")
            self._write_namespace_open(f, namespace)
            f.write("namespace {\n")
            f.write("struct ParcelDeleter {\n")
            f.write("    void operator()(OHIPCParcel* parcel) const\n    {\n")
            f.write("        if (parcel != nullptr) {\n")
            f.write("            OH_IPCParcel_Destroy(parcel);\n")
            f.write("        }\n")
            f.write("    }\n")
            f.write("};\n")
            f.write("} // namespace\n\n")

            for method in iface.methods:
                m_info = MethodOhIpcInfo.get(self.am, method)
                params = self._method_param_parts(method)
                ret_type = (
                    self.serializer.get_cpp_type(method.return_ty)
                    if method.return_ty
                    else "void"
                )
                result_name = self._result_param_name(method)
                request_mode = (
                    "OH_IPC_REQUEST_MODE_ASYNC"
                    if m_info.is_oneway
                    else "OH_IPC_REQUEST_MODE_SYNC"
                )

                self._write_cpp_signature(
                    f, "ErrCode", f"{info.proxy_name}::{method.name}", params
                )
                f.write("{\n")
                self._write_if_return(
                    f, "    ", "remote_ == nullptr", "OH_IPC_CHECK_PARAM_ERROR"
                )
                f.write("\n")
                # Use unique names to avoid conflict with method parameters
                parcel_data_var = "parcelData"
                parcel_reply_var = "parcelReply"
                # Check if parameter names conflict with our parcel variables
                param_names = {str(param.name) for param in method.params}
                if "parcelData" in param_names:
                    parcel_data_var = "ipcData"
                if "parcelReply" in param_names:
                    parcel_reply_var = "ipcReply"

                f.write(
                    f"    std::unique_ptr<OHIPCParcel, ParcelDeleter> {parcel_data_var}(OH_IPCParcel_Create());\n"
                )
                f.write(
                    f"    std::unique_ptr<OHIPCParcel, ParcelDeleter> {parcel_reply_var}(OH_IPCParcel_Create());\n"
                )
                self._write_if_return(
                    f,
                    "    ",
                    f"{parcel_data_var} == nullptr || {parcel_reply_var} == nullptr",
                    "OH_IPC_CHECK_PARAM_ERROR",
                )
                f.write("\n")
                self._write_if_return(
                    f,
                    "    ",
                    f"OH_IPCParcel_WriteInterfaceToken({parcel_data_var}.get(),\n        {iface.name}::GetDescriptor()) != OH_IPC_SUCCESS",
                    "OH_IPC_PARCEL_WRITE_ERROR",
                )
                f.write("\n")
                for param in method.params:
                    if self._param_mode(param) == "in":
                        f.write(
                            self._split_long_lines(
                                self.serializer.generate_write_code(
                                    f"{parcel_data_var}.get()",
                                    param.name,
                                    param.ty,
                                    iface_by_ref=True,
                                )
                            )
                            + "\n"
                        )
                f.write("\n")
                f.write(f"    OH_IPC_MessageOption option = {{ {request_mode}, 0 }};\n")
                f.write("    int32_t transportErr = OH_IPCRemoteProxy_SendRequest(\n")
                f.write("        remote_,\n")
                f.write(
                    f"        static_cast<uint32_t>({iface.name}::IpcCode::{m_info.command_name}),\n"
                )
                f.write(f"        {parcel_data_var}.get(),\n")
                f.write(f"        {parcel_reply_var}.get(),\n")
                f.write("        &option);\n")
                self._write_if_return(
                    f, "    ", "transportErr != OH_IPC_SUCCESS", "transportErr"
                )
                f.write("\n")
                if m_info.is_oneway:
                    f.write("    return OH_IPC_SUCCESS;\n")
                    f.write("}\n\n")
                    continue
                f.write("    int32_t errCode = OH_IPC_SUCCESS;\n")
                self._write_if_return(
                    f,
                    "    ",
                    f"OH_IPCParcel_ReadInt32({parcel_reply_var}.get(), &errCode) != OH_IPC_SUCCESS",
                    "OH_IPC_PARCEL_READ_ERROR",
                )
                self._write_if_return(f, "    ", "errCode != OH_IPC_SUCCESS", "errCode")
                f.write("\n")
                for param in method.params:
                    if self._param_mode(param) == "out":
                        f.write(
                            self._split_long_lines(
                                self.serializer.generate_read_code(
                                    f"{parcel_reply_var}.get()",
                                    param.name,
                                    param.ty,
                                    is_decl=False,
                                )
                            )
                            + "\n"
                        )
                if ret_type != "void":
                    f.write(
                        self._split_long_lines(
                            self.serializer.generate_read_code(
                                f"{parcel_reply_var}.get()",
                                result_name,
                                method.return_ty,
                                is_decl=False,
                            )
                        )
                        + "\n"
                    )
                f.write("\n    return OH_IPC_SUCCESS;\n")
                f.write("}\n\n")

            if info.is_main_service:
                self._write_cpp_signature(
                    f,
                    "ErrCode",
                    f"{info.proxy_name}::GetTypeLibInfo",
                    ["int32_t fd"],
                )
                f.write("{\n")
                self._write_if_return(
                    f, "    ", "remote_ == nullptr", "OH_IPC_CHECK_PARAM_ERROR"
                )
                f.write("\n")
                parcel_data_var = "parcelData"
                parcel_reply_var = "parcelReply"
                param_names = {"fd"}
                if "parcelData" in param_names:
                    parcel_data_var = "ipcData"
                if "parcelReply" in param_names:
                    parcel_reply_var = "ipcReply"

                f.write(
                    f"    std::unique_ptr<OHIPCParcel, ParcelDeleter> {parcel_data_var}(OH_IPCParcel_Create());\n"
                )
                f.write(
                    f"    std::unique_ptr<OHIPCParcel, ParcelDeleter> {parcel_reply_var}(OH_IPCParcel_Create());\n"
                )
                self._write_if_return(
                    f,
                    "    ",
                    f"{parcel_data_var} == nullptr || {parcel_reply_var} == nullptr",
                    "OH_IPC_CHECK_PARAM_ERROR",
                )
                f.write("\n")
                self._write_if_return(
                    f,
                    "    ",
                    f"OH_IPCParcel_WriteInterfaceToken({parcel_data_var}.get(),\n        {iface.name}::GetDescriptor()) != OH_IPC_SUCCESS",
                    "OH_IPC_PARCEL_WRITE_ERROR",
                )
                f.write("\n")
                f.write("    // Write fd using OH_IPCParcel_WriteFileDescriptor\n")
                f.write(
                    f"    if (OH_IPCParcel_WriteFileDescriptor({parcel_data_var}.get(), fd) != OH_IPC_SUCCESS) {{\n"
                )
                f.write("        return OH_IPC_PARCEL_WRITE_ERROR;\n")
                f.write("    }\n")
                f.write("\n")
                f.write(
                    "    OH_IPC_MessageOption option = { OH_IPC_REQUEST_MODE_SYNC, 0 };\n"
                )
                f.write("    int32_t transportErr = OH_IPCRemoteProxy_SendRequest(\n")
                f.write("        remote_,\n")
                f.write(
                    f"        static_cast<uint32_t>({iface.name}::IpcCode::COMMAND_GET_TYPE_LIB_INFO),\n"
                )
                f.write(f"        {parcel_data_var}.get(),\n")
                f.write(f"        {parcel_reply_var}.get(),\n")
                f.write("        &option);\n")
                self._write_if_return(
                    f, "    ", "transportErr != OH_IPC_SUCCESS", "transportErr"
                )
                f.write("\n")
                f.write("    int32_t errCode = OH_IPC_SUCCESS;\n")
                self._write_if_return(
                    f,
                    "    ",
                    f"OH_IPCParcel_ReadInt32({parcel_reply_var}.get(), &errCode) != OH_IPC_SUCCESS",
                    "OH_IPC_PARCEL_READ_ERROR",
                )
                self._write_if_return(f, "    ", "errCode != OH_IPC_SUCCESS", "errCode")
                f.write("\n")
                f.write("    return OH_IPC_SUCCESS;\n")
                f.write("}\n\n")

            self._write_cpp_signature(
                f,
                "ErrCode",
                f"{info.proxy_name}::GetVersion",
                ["std::string& result"],
            )
            f.write("{\n")
            self._write_if_return(
                f, "    ", "remote_ == nullptr", "OH_IPC_CHECK_PARAM_ERROR"
            )
            f.write("\n")
            parcel_data_var = "parcelData"
            parcel_reply_var = "parcelReply"

            f.write(
                f"    std::unique_ptr<OHIPCParcel, ParcelDeleter> {parcel_data_var}(OH_IPCParcel_Create());\n"
            )
            f.write(
                f"    std::unique_ptr<OHIPCParcel, ParcelDeleter> {parcel_reply_var}(OH_IPCParcel_Create());\n"
            )
            self._write_if_return(
                f,
                "    ",
                f"{parcel_data_var} == nullptr || {parcel_reply_var} == nullptr",
                "OH_IPC_CHECK_PARAM_ERROR",
            )
            f.write("\n")
            self._write_if_return(
                f,
                "    ",
                f"OH_IPCParcel_WriteInterfaceToken({parcel_data_var}.get(),\n        {iface.name}::GetDescriptor()) != OH_IPC_SUCCESS",
                "OH_IPC_PARCEL_WRITE_ERROR",
            )
            f.write("\n")
            f.write(
                "    OH_IPC_MessageOption option = { OH_IPC_REQUEST_MODE_SYNC, 0 };\n"
            )
            f.write("    int32_t transportErr = OH_IPCRemoteProxy_SendRequest(\n")
            f.write("        remote_,\n")
            f.write(
                f"        static_cast<uint32_t>({iface.name}::IpcCode::COMMAND_GET_VERSION),\n"
            )
            f.write(f"        {parcel_data_var}.get(),\n")
            f.write(f"        {parcel_reply_var}.get(),\n")
            f.write("        &option);\n")
            self._write_if_return(
                f, "    ", "transportErr != OH_IPC_SUCCESS", "transportErr"
            )
            f.write("\n")
            f.write("    int32_t errCode = OH_IPC_SUCCESS;\n")
            self._write_if_return(
                f,
                "    ",
                f"OH_IPCParcel_ReadInt32({parcel_reply_var}.get(), &errCode) != OH_IPC_SUCCESS",
                "OH_IPC_PARCEL_READ_ERROR",
            )
            self._write_if_return(f, "    ", "errCode != OH_IPC_SUCCESS", "errCode")
            f.write("\n")
            f.write(
                "    const char* versionStr = OH_IPCParcel_ReadString(parcelReply.get());\n"
            )
            f.write("    if (versionStr == nullptr) {\n")
            f.write("        return OH_IPC_PARCEL_READ_ERROR;\n")
            f.write("    }\n")
            f.write("    result = versionStr;\n")
            f.write("\n")
            f.write("    return OH_IPC_SUCCESS;\n")
            f.write("}\n\n")

            self._write_cpp_signature(
                f,
                "ErrCode",
                f"{info.proxy_name}::GetTaiheVersion",
                ["std::string& result"],
            )
            f.write("{\n")
            self._write_if_return(
                f, "    ", "remote_ == nullptr", "OH_IPC_CHECK_PARAM_ERROR"
            )
            f.write("\n")
            parcel_data_var = "parcelData"
            parcel_reply_var = "parcelReply"

            f.write(
                f"    std::unique_ptr<OHIPCParcel, ParcelDeleter> {parcel_data_var}(OH_IPCParcel_Create());\n"
            )
            f.write(
                f"    std::unique_ptr<OHIPCParcel, ParcelDeleter> {parcel_reply_var}(OH_IPCParcel_Create());\n"
            )
            self._write_if_return(
                f,
                "    ",
                f"{parcel_data_var} == nullptr || {parcel_reply_var} == nullptr",
                "OH_IPC_CHECK_PARAM_ERROR",
            )
            f.write("\n")
            self._write_if_return(
                f,
                "    ",
                f"OH_IPCParcel_WriteInterfaceToken({parcel_data_var}.get(),\n        {iface.name}::GetDescriptor()) != OH_IPC_SUCCESS",
                "OH_IPC_PARCEL_WRITE_ERROR",
            )
            f.write("\n")
            f.write(
                "    OH_IPC_MessageOption option = { OH_IPC_REQUEST_MODE_SYNC, 0 };\n"
            )
            f.write("    int32_t transportErr = OH_IPCRemoteProxy_SendRequest(\n")
            f.write("        remote_,\n")
            f.write(
                f"        static_cast<uint32_t>({iface.name}::IpcCode::COMMAND_GET_TAIHE_VERSION),\n"
            )
            f.write(f"        {parcel_data_var}.get(),\n")
            f.write(f"        {parcel_reply_var}.get(),\n")
            f.write("        &option);\n")
            self._write_if_return(
                f, "    ", "transportErr != OH_IPC_SUCCESS", "transportErr"
            )
            f.write("\n")
            f.write("    int32_t errCode = OH_IPC_SUCCESS;\n")
            self._write_if_return(
                f,
                "    ",
                f"OH_IPCParcel_ReadInt32({parcel_reply_var}.get(), &errCode) != OH_IPC_SUCCESS",
                "OH_IPC_PARCEL_READ_ERROR",
            )
            self._write_if_return(f, "    ", "errCode != OH_IPC_SUCCESS", "errCode")
            f.write("\n")
            f.write(
                "    const char* versionStr = OH_IPCParcel_ReadString(parcelReply.get());\n"
            )
            f.write("    if (versionStr == nullptr) {\n")
            f.write("        return OH_IPC_PARCEL_READ_ERROR;\n")
            f.write("    }\n")
            f.write("    result = versionStr;\n")
            f.write("\n")
            f.write("    return OH_IPC_SUCCESS;\n")
            f.write("}\n\n")

            self._write_namespace_close(f, namespace)
