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

from taihe.codegen.modobj.analyses import (
    IfaceOhIpcInfo,
    MethodOhIpcInfo,
    header_guard_for,
    namespace_scope_for_cpp,
    strip_leading_interface_i,
    type_name_to_file_stem,
)
from taihe.codegen.modobj.serialization import OhIpcSerializer
from taihe.semantics.declarations import IfaceDecl
from taihe.semantics.types import (
    ArrayType,
    IfaceType,
    MapType,
    ScalarType,
    SetType,
    StructType,
    VectorType,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import BasicOutputManager, OutputManager


class StubGenerator:
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
        self.serializer = OhIpcSerializer(am, is_proxy=False)

    @staticmethod
    def _split_long_lines(text: str) -> str:
        """Split long lines in the given text to ensure no line exceeds MAX_LINE_LENGTH."""
        lines = text.splitlines()
        result = []
        for line in lines:
            if len(line) <= StubGenerator.MAX_LINE_LENGTH:
                result.append(line)
            else:
                # Simple split: find a good place to break, like after '='
                if " = " in line:
                    idx = line.find(" = ")
                    prefix = line[: idx + len(" = ")]
                    rest = line[idx + len(" = ") :]
                    if len(prefix) + len(rest) > StubGenerator.MAX_LINE_LENGTH:
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
    def _stub_file_stem(info: IfaceOhIpcInfo) -> str:
        return f"{type_name_to_file_stem(info.interface_name)}_stub"

    def generate(self, iface: IfaceDecl):
        info = IfaceOhIpcInfo.get(self.am, iface)
        # Determine interface type
        from taihe.codegen.modobj.attribute import (
            CallbackAttribute,
            MainServiceAttribute,
        )

        is_main = MainServiceAttribute.get(iface) is not None
        is_callback = CallbackAttribute.get(iface) is not None

        if is_main:
            interface_type = 1  # mainService
        elif is_callback:
            interface_type = 2  # callback
        else:
            interface_type = 0  # normal

        self._generate_header(iface, info, interface_type)
        self._generate_source(iface, info, interface_type)

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

    @staticmethod
    def _param_local_name(param) -> str:
        if str(param.name) == "data":
            return "paramData"
        return str(param.name)

    @staticmethod
    def _is_iface_type(ty) -> bool:
        return isinstance(ty, IfaceType)

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
    def _write_cpp_signature(
        f, ret_type: str, scope_name: str, params: list[str], suffix: str = ""
    ):
        prefix = f"{ret_type} {scope_name}("
        one_line = prefix + ", ".join(params) + ")" + suffix
        if len(one_line) <= StubGenerator.MAX_LINE_LENGTH:
            f.write(one_line + "\n")
            return

        f.write(prefix + "\n")
        indent = "    "
        current = indent
        for idx, param in enumerate(params):
            frag = param + (")" + suffix if idx == len(params) - 1 else ",")
            separator = "" if current == indent else " "
            candidate = current + separator + frag
            if len(candidate) <= StubGenerator.MAX_LINE_LENGTH:
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
        if len(one_line) <= StubGenerator.MAX_LINE_LENGTH:
            f.write(one_line + "\n")
            return

        f.write(prefix + "\n")
        continuation = indent + "    "
        current = continuation
        for idx, param in enumerate(params):
            frag = param + (")" + suffix if idx == len(params) - 1 else ",")
            separator = "" if current == continuation else " "
            candidate = current + separator + frag
            if len(candidate) <= StubGenerator.MAX_LINE_LENGTH:
                current = candidate
            else:
                if current != continuation:
                    f.write(current.rstrip() + "\n")
                current = continuation + frag
        f.write(current.rstrip() + "\n")

    @staticmethod
    def _write_multiline_call(f, callee: str, args: list[str], indent: str = "    "):
        one_line = f"{indent}ErrCode errCode = {callee}({', '.join(args)});"
        if len(one_line) <= StubGenerator.MAX_LINE_LENGTH:
            f.write(one_line + "\n")
            return

        f.write(f"{indent}ErrCode errCode = {callee}(\n")
        continuation = indent + "    "
        current = continuation
        for idx, arg in enumerate(args):
            frag = arg + ("," if idx < len(args) - 1 else ")")
            separator = "" if current == continuation else " "
            candidate = current + separator + frag
            if len(candidate) <= StubGenerator.MAX_LINE_LENGTH:
                current = candidate
            else:
                if current != continuation:
                    f.write(current.rstrip() + "\n")
                current = continuation + frag
        f.write(current.rstrip() + ";\n")

    @staticmethod
    def _write_if_return(f, indent: str, condition: str, ret_expr: str):
        f.write(f"{indent}if ({condition}) {{\n")
        f.write(f"{indent}    return {ret_expr};\n")
        f.write(f"{indent}}}\n")

    def _collect_proxy_headers(self, ty, headers: set[str]):
        from taihe.semantics.types import CallbackType

        if isinstance(ty, CallbackType):
            self._collect_proxy_headers(ty.ref.return_ty, headers)
            for param in ty.ref.params:
                self._collect_proxy_headers(param.ty, headers)
            return
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
        headers.discard(f"{self._stub_file_stem(info)}.h")
        return sorted(headers)

    def _source_headers(self, iface: IfaceDecl, info: IfaceOhIpcInfo) -> list[str]:
        return self._source_proxy_headers(iface, info)

    def _generate_header(
        self, iface: IfaceDecl, info: IfaceOhIpcInfo, interface_type: int
    ):
        filename = f"{self._stub_file_stem(info)}.h"
        guard = header_guard_for(info.stub_name, iface.parent_pkg)
        namespace = namespace_scope_for_cpp(iface.parent_pkg)

        with self.om.open(filename) as f:
            f.write(f"""#ifndef {guard}
#define {guard}

""")
            # Add system headers first for non-callback interfaces
            if interface_type != 2:  # Not callback
                f.write(
                    "#include <AbilityKit/ability_runtime/modular_object_extension_context.h>\n"
                )
            f.write(f'#include "{self._iface_file_stem(iface)}.h"\n')
            f.write("\n")
            self._write_namespace_open(f, namespace)
            f.write(f"class {info.stub_name} : public {iface.name} {{\npublic:\n")
            # Generate constructor based on interface type
            if interface_type == 2:  # callback
                f.write(f"    {info.stub_name}();\n")
            else:  # normal or mainService
                f.write(
                    f"    explicit {info.stub_name}(OH_AbilityRuntime_ModObjExtensionContextHandle context);\n"
                )
            f.write(f"    ~{info.stub_name}() override;\n\n")
            f.write("    OHIPCRemoteStub* GetRemoteStub() const\n")
            f.write("    {\n")
            f.write("        return remoteStub_;\n")
            f.write("    }\n\n")
            f.write(
                "    ErrCode WriteRemoteObject(OHIPCParcel* parcel) const override;\n\n"
            )
            f.write("    static int32_t OnRemoteRequest(\n")
            f.write("        uint32_t code,\n")
            f.write("        const OHIPCParcel* data,\n")
            f.write("        OHIPCParcel* reply,\n")
            f.write("        void* userData);\n")

            f.write("\nprotected:\n")
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
            self._write_method_declaration(
                f,
                "    ",
                "int32_t",
                "OnRemoteRequestInner",
                ["uint32_t code", "const OHIPCParcel* data", "OHIPCParcel* reply"],
                ";",
            )
            for method in iface.methods:
                self._write_method_declaration(
                    f,
                    "    ",
                    "int32_t",
                    f"Handle{method.name}",
                    ["const OHIPCParcel* data", "OHIPCParcel* reply"],
                    ";",
                )

            if info.is_main_service:
                self._write_method_declaration(
                    f,
                    "    ",
                    "int32_t",
                    "HandleGetTypeLibInfo",
                    ["const OHIPCParcel* data", "OHIPCParcel* reply"],
                    ";",
                )
            self._write_method_declaration(
                f,
                "    ",
                "int32_t",
                "HandleGetVersion",
                ["const OHIPCParcel* data", "OHIPCParcel* reply"],
                ";",
            )
            self._write_method_declaration(
                f,
                "    ",
                "int32_t",
                "HandleGetTaiheVersion",
                ["const OHIPCParcel* data", "OHIPCParcel* reply"],
                ";",
            )

            f.write("\nprivate:\n")
            f.write("    OHIPCRemoteStub* remoteStub_ = nullptr;\n")
            # Add context member for non-callback interfaces
            if interface_type != 2:  # Not callback
                f.write(
                    "    OH_AbilityRuntime_ModObjExtensionContextHandle context_;\n"
                )
            f.write("};\n\n")
            self._write_namespace_close(f, namespace)
            f.write(f"\n#endif // {guard}\n")

    def _generate_source(
        self, iface: IfaceDecl, info: IfaceOhIpcInfo, interface_type: int
    ):
        filename = f"{self._stub_file_stem(info)}.cpp"
        namespace = namespace_scope_for_cpp(iface.parent_pkg)

        with self.om.open(filename) as f:
            f.write(f"""#include <cstdlib>
#include <cstring>
#include <unistd.h>

#include \"{self._stub_file_stem(info)}.h\"
""")
            # Include custom headers after stub header
            for header in self._source_headers(iface, info):
                f.write(f'#include "{header}"\n')
            f.write("\n")

            # Add helper functions and global variables after all includes
            f.write("static void* OhipcReadInterfaceTokenAllocator(int32_t len)\n")
            f.write("{\n")
            f.write("    return malloc(len);\n")
            f.write("}\n\n")

            if info.is_main_service:
                # Add typeLibInfo constant with minified .typelib.json content
                import json

                iface_base = strip_leading_interface_i(iface.name).lower()
                if not isinstance(self.om, BasicOutputManager):
                    raise ValueError(
                        "OHIPC backend requires BasicOutputManager to read generated typelib files."
                    )
                typelib_json_file = self.om.dst_dir / f"{iface_base}.typelib.json"
                typelib_info_data = ""
                try:
                    if typelib_json_file.exists():
                        with open(typelib_json_file, encoding="utf-8") as json_f:
                            # Parse JSON and re-serialize without formatting (minified)
                            json_obj = json.load(json_f)
                            minified_json = json.dumps(
                                json_obj, separators=(",", ":"), ensure_ascii=False
                            )
                            # Escape backslashes first, then escape double quotes for C string
                            typelib_info_data = minified_json.replace(
                                "\\", "\\\\"
                            ).replace('"', '\\"')
                except Exception:
                    typelib_info_data = ""

                if typelib_info_data:
                    f.write(
                        f'static const char* typeLibInfo = "{typelib_info_data}";\n\n'
                    )

            self._write_namespace_open(f, namespace)

            # Generate constructor based on interface type
            if interface_type == 2:  # callback - use OH_IPCRemoteStub_Create
                f.write(f"{info.stub_name}::{info.stub_name}()\n")
                f.write("    : remoteStub_(OH_IPCRemoteStub_Create(\n")
                f.write(f"          {iface.name}::GetDescriptor(),\n")
                f.write(f"          &{info.stub_name}::OnRemoteRequest,\n")
                f.write("          nullptr,\n")
                f.write("          this))\n")
                f.write("{\n}\n\n")
            else:  # normal or mainService - use OH_AbilityRuntime_ModObjExtensionContext_CreateIPCRemoteStub
                f.write(
                    f"{info.stub_name}::{info.stub_name}(OH_AbilityRuntime_ModObjExtensionContextHandle context)\n"
                )
                f.write("    : context_(context),\n")
                f.write(
                    "      remoteStub_(OH_AbilityRuntime_ModObjExtensionContext_CreateIPCRemoteStub(\n"
                )
                f.write("          context,\n")
                f.write(f"          {iface.name}::GetDescriptor(),\n")
                f.write(f"          &{info.stub_name}::OnRemoteRequest,\n")
                f.write("          nullptr,\n")
                f.write("          this))\n")
                f.write("{\n}\n\n")

            f.write(f"{info.stub_name}::~{info.stub_name}()\n{{\n")
            f.write("    if (remoteStub_ != nullptr) {\n")
            # Generate destructor based on interface type
            if interface_type == 2:  # callback - use OH_IPCRemoteStub_Destroy
                f.write("        OH_IPCRemoteStub_Destroy(remoteStub_);\n")
            else:  # normal or mainService - use OH_AbilityRuntime_ModObjExtensionContext_DestroyIPCRemoteStub
                f.write(
                    "        OH_AbilityRuntime_ModObjExtensionContext_DestroyIPCRemoteStub(context_, remoteStub_);\n"
                )
            f.write("        remoteStub_ = nullptr;\n")
            f.write("    }\n")
            f.write("}\n\n")

            self._write_cpp_signature(
                f,
                "ErrCode",
                f"{info.stub_name}::WriteRemoteObject",
                ["OHIPCParcel* parcel"],
                " const",
            )
            f.write("{\n")
            self._write_if_return(
                f,
                "    ",
                "parcel == nullptr || remoteStub_ == nullptr",
                "OH_IPC_CHECK_PARAM_ERROR",
            )
            self._write_if_return(
                f,
                "    ",
                "OH_IPCParcel_WriteRemoteStub(parcel, remoteStub_) != OH_IPC_SUCCESS",
                "OH_IPC_PARCEL_WRITE_ERROR",
            )
            f.write("    return OH_IPC_SUCCESS;\n")
            f.write("}\n\n")

            self._write_cpp_signature(
                f,
                "int32_t",
                f"{info.stub_name}::OnRemoteRequest",
                [
                    "uint32_t code",
                    "const OHIPCParcel* data",
                    "OHIPCParcel* reply",
                    "void* userData",
                ],
            )
            f.write("{\n")
            self._write_if_return(
                f, "    ", "userData == nullptr", "OH_IPC_CHECK_PARAM_ERROR"
            )
            f.write(f"    auto* stub = static_cast<{info.stub_name}*>(userData);\n")
            f.write("    return stub->OnRemoteRequestInner(code, data, reply);\n")
            f.write("}\n\n")

            self._write_cpp_signature(
                f,
                "int32_t",
                f"{info.stub_name}::OnRemoteRequestInner",
                ["uint32_t code", "const OHIPCParcel* data", "OHIPCParcel* reply"],
            )
            f.write("{\n")
            self._write_if_return(
                f,
                "    ",
                "data == nullptr || reply == nullptr",
                "OH_IPC_CHECK_PARAM_ERROR",
            )
            f.write("    char* remoteDescriptor = nullptr;\n")
            f.write("    int32_t remoteDescriptorLen = 0;\n")
            f.write(
                "    if (OH_IPCParcel_ReadInterfaceToken(data, &remoteDescriptor,\n"
            )
            f.write(
                "        &remoteDescriptorLen, OhipcReadInterfaceTokenAllocator) != OH_IPC_SUCCESS) {\n"
            )
            f.write("        return OH_IPC_CHECK_PARAM_ERROR;\n")
            f.write("    }\n")
            f.write(f"    if (remoteDescriptor == nullptr ||\n")
            f.write(
                f"        std::strcmp(remoteDescriptor, {iface.name}::GetDescriptor()) != 0) {{\n"
            )
            f.write("        if (remoteDescriptor != nullptr) {\n")
            f.write("            free(remoteDescriptor);\n")
            f.write("        }\n")
            f.write("        return OH_IPC_CHECK_PARAM_ERROR;\n")
            f.write("    }\n")
            f.write("    free(remoteDescriptor);\n")
            f.write("\n")
            f.write(f"    switch (static_cast<{iface.name}::IpcCode>(code)) {{\n")
            for method in iface.methods:
                m_info = MethodOhIpcInfo.get(self.am, method)
                f.write(f"        case {iface.name}::IpcCode::{m_info.command_name}:\n")
                f.write(f"            return Handle{method.name}(data, reply);\n")

            if info.is_main_service:
                f.write(
                    f"        case {iface.name}::IpcCode::COMMAND_GET_TYPE_LIB_INFO:\n"
                )
                f.write("            return HandleGetTypeLibInfo(data, reply);\n")
            f.write(f"        case {iface.name}::IpcCode::COMMAND_GET_VERSION:\n")
            f.write("            return HandleGetVersion(data, reply);\n")
            f.write(f"        case {iface.name}::IpcCode::COMMAND_GET_TAIHE_VERSION:\n")
            f.write("            return HandleGetTaiheVersion(data, reply);\n")

            f.write("        default:\n")
            f.write("            return OH_IPC_CHECK_PARAM_ERROR;\n")
            f.write("    }\n")
            f.write("}\n\n")

            for method in iface.methods:
                ret_type = (
                    self.serializer.get_cpp_type(method.return_ty)
                    if method.return_ty
                    else "void"
                )
                result_name = self._result_param_name(method)
                self._write_cpp_signature(
                    f,
                    "int32_t",
                    f"{info.stub_name}::Handle{method.name}",
                    ["const OHIPCParcel* data", "OHIPCParcel* reply"],
                )
                f.write("{\n")
                for param in method.params:
                    if self._param_mode(param) == "in":
                        var_name = self._param_local_name(param)
                        f.write(
                            self._split_long_lines(
                                self.serializer.generate_read_code(
                                    "data",
                                    var_name,
                                    param.ty,
                                    iface_as_object=self._is_iface_type(param.ty),
                                )
                            )
                            + "\n"
                        )
                    else:
                        initializer = (
                            " = nullptr" if self._is_iface_type(param.ty) else ""
                        )
                        f.write(
                            f"    {self.serializer.get_cpp_type(param.ty)} {param.name}{initializer};\n"
                        )
                if ret_type != "void":
                    if isinstance(method.return_ty, ArrayType):
                        f.write(
                            f"    {ret_type} {result_name} = {self.serializer.empty_array_expr(method.return_ty)};\n"
                        )
                    elif self._is_iface_type(method.return_ty):
                        f.write(f"    {ret_type} {result_name} = nullptr;\n")
                    elif isinstance(method.return_ty, ScalarType):
                        # Initialize scalar types to zero
                        f.write(f"    {ret_type} {result_name} = 0;\n")
                    else:
                        # For other types (string, struct, etc.), use default constructor
                        f.write(f"    {ret_type} {result_name};\n")
                # Build call arguments, using renamed variables if necessary
                call_args = []
                for param in method.params:
                    local_name = self._param_local_name(param)
                    call_args.append(local_name)
                if ret_type != "void":
                    call_args.append(result_name)
                self._write_multiline_call(f, method.name, call_args)
                self._write_if_return(
                    f,
                    "    ",
                    "OH_IPCParcel_WriteInt32(reply, errCode) != OH_IPC_SUCCESS",
                    "OH_IPC_PARCEL_WRITE_ERROR",
                )
                has_output = False
                for param in method.params:
                    if self._param_mode(param) == "out":
                        if not has_output:
                            f.write("\n")
                            has_output = True
                        f.write(
                            self._split_long_lines(
                                self.serializer.generate_write_code(
                                    "reply", param.name, param.ty, "    "
                                )
                            )
                            + "\n"
                        )
                if ret_type != "void":
                    if not has_output:
                        f.write("\n")
                        has_output = True
                    f.write(
                        self._split_long_lines(
                            self.serializer.generate_write_code(
                                "reply", result_name, method.return_ty, "    "
                            )
                        )
                        + "\n"
                    )
                if has_output:
                    f.write("\n")
                f.write("    return OH_IPC_SUCCESS;\n")
                f.write("}\n\n")

            if info.is_main_service:
                self._write_cpp_signature(
                    f,
                    "int32_t",
                    f"{info.stub_name}::HandleGetTypeLibInfo",
                    ["const OHIPCParcel* data", "OHIPCParcel* reply"],
                )
                f.write("{\n")
                f.write("    int32_t fd = 0;\n")
                f.write(
                    "    if (OH_IPCParcel_ReadFileDescriptor(data, &fd) != OH_IPC_SUCCESS) {\n"
                )
                f.write("        return OH_IPC_PARCEL_READ_ERROR;\n")
                f.write("    }\n")
                f.write("\n")
                f.write("    ErrCode errCode = GetTypeLibInfo(fd);\n")
                f.write(
                    "    if (OH_IPCParcel_WriteInt32(reply, errCode) != OH_IPC_SUCCESS) {\n"
                )
                f.write("        return OH_IPC_PARCEL_WRITE_ERROR;\n")
                f.write("    }\n")
                f.write("    return OH_IPC_SUCCESS;\n")
                f.write("}\n\n")

            self._write_cpp_signature(
                f,
                "int32_t",
                f"{info.stub_name}::HandleGetVersion",
                ["const OHIPCParcel* data", "OHIPCParcel* reply"],
            )
            f.write("{\n")
            f.write("    std::string result;\n")
            f.write("    ErrCode errCode = GetVersion(result);\n")
            f.write(
                "    if (OH_IPCParcel_WriteInt32(reply, errCode) != OH_IPC_SUCCESS) {\n"
            )
            f.write("        return OH_IPC_PARCEL_WRITE_ERROR;\n")
            f.write("    }\n")
            f.write("\n")
            f.write(
                "    if (OH_IPCParcel_WriteString(reply, result.c_str()) != OH_IPC_SUCCESS) {\n"
            )
            f.write("        return OH_IPC_PARCEL_WRITE_ERROR;\n")
            f.write("    }\n")
            f.write("    return OH_IPC_SUCCESS;\n")
            f.write("}\n\n")

            self._write_cpp_signature(
                f,
                "int32_t",
                f"{info.stub_name}::HandleGetTaiheVersion",
                ["const OHIPCParcel* data", "OHIPCParcel* reply"],
            )
            f.write("{\n")
            f.write("    std::string result;\n")
            f.write("    ErrCode errCode = GetTaiheVersion(result);\n")
            f.write(
                "    if (OH_IPCParcel_WriteInt32(reply, errCode) != OH_IPC_SUCCESS) {\n"
            )
            f.write("        return OH_IPC_PARCEL_WRITE_ERROR;\n")
            f.write("    }\n")
            f.write("\n")
            f.write(
                "    if (OH_IPCParcel_WriteString(reply, result.c_str()) != OH_IPC_SUCCESS) {\n"
            )
            f.write("        return OH_IPC_PARCEL_WRITE_ERROR;\n")
            f.write("    }\n")
            f.write("    return OH_IPC_SUCCESS;\n")
            f.write("}\n\n")

            if info.is_main_service:
                f.write(f"ErrCode {info.stub_name}::GetTypeLibInfo(int32_t fd)\n")
                f.write("{\n")
                f.write(
                    "    if (typeLibInfo == nullptr || strlen(typeLibInfo) == 0) {\n"
                )
                f.write("        close(fd);\n")
                f.write("        return OH_IPC_INNER_ERROR;\n")
                f.write("    }\n")
                f.write("\n")
                f.write(
                    "    int32_t ret = write(fd, typeLibInfo, strlen(typeLibInfo));\n"
                )
                f.write("    close(fd);\n")
                f.write("\n")
                f.write("    return ret >= 0 ? OH_IPC_SUCCESS : OH_IPC_INNER_ERROR;\n")
                f.write("}\n\n")

            f.write(f"ErrCode {info.stub_name}::GetVersion(std::string& result)\n")
            f.write("{\n")
            f.write(f'    result = "{info.version}";\n')
            f.write("    return OH_IPC_SUCCESS;\n")
            f.write("}\n\n")

            f.write(f"ErrCode {info.stub_name}::GetTaiheVersion(std::string& result)\n")
            f.write("{\n")
            f.write(f'    result = "{info.taihe_version}";\n')
            f.write("    return OH_IPC_SUCCESS;\n")
            f.write("}\n\n")

            self._write_namespace_close(f, namespace)
