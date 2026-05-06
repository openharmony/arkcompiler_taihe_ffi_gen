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
from pathlib import Path

from taihe.codegen.ohipc.analyses import (
    IfaceOhIpcInfo,
    MethodOhIpcInfo,
    header_guard_for,
    interface_descriptor_for_cpp,
    namespace_scope_for_cpp,
    type_name_to_file_stem,
)
from taihe.codegen.ohipc.serialization import OhIpcSerializer
from taihe.semantics.declarations import EnumDecl, IfaceDecl, PackageDecl, StructDecl
from taihe.semantics.types import (
    ArrayType,
    EnumType,
    IfaceType,
    MapType,
    SetType,
    StructType,
    VectorType,
)
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import OutputManager


class InterfaceGenerator:
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

    def __init__(
        self,
        om: OutputManager,
        am: AnalysisManager,
        ipc_common: list[Path] | None = None,
    ):
        self.om = om
        self.am = am
        self.serializer = OhIpcSerializer(am)
        self.ipc_common_paths = {path.resolve() for path in (ipc_common or [])}

    def _is_ipc_common_struct(self, struct_decl: StructDecl) -> bool:
        if not self.ipc_common_paths or struct_decl.loc is None:
            return False
        source = struct_decl.loc.file
        return (
            hasattr(source, "path")
            and Path(source.path).resolve() in self.ipc_common_paths
        )

    @staticmethod
    def _ipc_common_bundle_header_by_path(ipc_common: Path) -> str:
        stem = ipc_common.stem
        if stem.startswith("I") and len(stem) > 1:
            stem = stem[1:]
        return f"{type_name_to_file_stem(stem)}.h"

    def _ipc_common_bundle_header(self, struct_decl: StructDecl) -> str | None:
        if not self._is_ipc_common_struct(struct_decl):
            return None
        source = struct_decl.loc.file
        return self._ipc_common_bundle_header_by_path(Path(source.path).resolve())

    @staticmethod
    def _iface_file_stem(iface: IfaceDecl) -> str:
        return f"i{type_name_to_file_stem(iface.name)}"

    @staticmethod
    def _struct_file_stem(struct_decl: StructDecl) -> str:
        return type_name_to_file_stem(struct_decl.name)

    @staticmethod
    def _enum_file_stem(enum_decl: EnumDecl) -> str:
        return type_name_to_file_stem(enum_decl.name)

    @staticmethod
    def _proxy_file_stem(iface_decl: IfaceDecl) -> str:
        return f"{type_name_to_file_stem(iface_decl.name)}_proxy"

    @staticmethod
    def _stub_file_stem(iface_decl: IfaceDecl) -> str:
        return f"{type_name_to_file_stem(iface_decl.name)}_stub"

    def generate(self, iface: IfaceDecl):
        info = IfaceOhIpcInfo.get(self.am, iface)
        filename = f"{self._iface_file_stem(iface)}.h"
        with self.om.open(filename, "w") as f:
            self._write_header(f, iface, info)

    def generate_struct(self, struct_decl: StructDecl):
        filename = f"{self._struct_file_stem(struct_decl)}.h"
        with self.om.open(filename, "w") as f:
            self._write_struct_header(f, struct_decl)

    def generate_struct_source(self, struct_decl: StructDecl):
        filename = f"{self._struct_file_stem(struct_decl)}.cpp"
        with self.om.open(filename, "w") as f:
            self._write_struct_source(f, struct_decl)

    def generate_enum(self, enum_decl: EnumDecl):
        filename = f"{self._enum_file_stem(enum_decl)}.h"
        with self.om.open(filename, "w") as f:
            self._write_enum_header(f, enum_decl)

    def generate_enum_bundle(
        self,
        bundle_name: str,
        enum_decls: list[EnumDecl],
        override_pkg: PackageDecl | None = None,
    ):
        with self.om.open(f"{bundle_name}.h", "w") as f:
            self._write_enum_bundle_header(f, bundle_name, enum_decls, override_pkg)

    def generate_struct_bundle(
        self,
        bundle_name: str,
        struct_decls: list[StructDecl],
        override_pkg: PackageDecl | None = None,
    ):
        with self.om.open(f"{bundle_name}.h", "w") as f:
            self._write_struct_bundle_header(f, bundle_name, struct_decls, override_pkg)
        with self.om.open(f"{bundle_name}.cpp", "w") as f:
            self._write_struct_bundle_source(f, bundle_name, struct_decls, override_pkg)

    def _collect_type_headers(self, ty, headers: set[str]):
        if isinstance(ty, StructType):
            bundle_header = self._ipc_common_bundle_header(ty.decl)
            if bundle_header is not None:
                headers.add(bundle_header)
            else:
                headers.add(f"{type_name_to_file_stem(ty.decl.name)}.h")
            return
        if isinstance(ty, EnumType):
            bundle_header = self._ipc_common_bundle_header(ty.decl)
            if bundle_header is not None:
                headers.add(bundle_header)
            else:
                headers.add(f"{type_name_to_file_stem(ty.decl.name)}.h")
            return
        if isinstance(ty, IfaceType):
            headers.add(f"i{type_name_to_file_stem(ty.decl.name)}.h")
            return
        if isinstance(ty, VectorType):
            self._collect_type_headers(ty.val_ty, headers)
            return
        if isinstance(ty, ArrayType):
            self._collect_type_headers(ty.item_ty, headers)
            return
        if isinstance(ty, MapType):
            self._collect_type_headers(ty.key_ty, headers)
            self._collect_type_headers(ty.val_ty, headers)
            return
        if isinstance(ty, SetType):
            self._collect_type_headers(ty.key_ty, headers)

    def _collect_proxy_headers(self, ty, headers: set[str]):
        if isinstance(ty, IfaceType):
            headers.add(f"{self._proxy_file_stem(ty.decl)}.h")
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

    def _iface_headers(self, iface: IfaceDecl) -> list[str]:
        headers: set[str] = set()
        for method in iface.methods:
            for param in method.params:
                self._collect_type_headers(param.ty, headers)
            self._collect_type_headers(method.return_ty, headers)
        headers.discard(f"{self._iface_file_stem(iface)}.h")
        return sorted(headers)

    def _iface_proxy_headers(self, iface: IfaceDecl) -> list[str]:
        headers: set[str] = set()
        for method in iface.methods:
            for param in method.params:
                self._collect_proxy_headers(param.ty, headers)
            self._collect_proxy_headers(method.return_ty, headers)
        headers.discard(f"{self._proxy_file_stem(iface)}.h")
        return sorted(headers)

    def _struct_headers(self, struct_decl: StructDecl) -> list[str]:
        headers: set[str] = set()
        for field in struct_decl.fields:
            self._collect_type_headers(field.ty, headers)
        headers.discard(f"{self._struct_file_stem(struct_decl)}.h")
        return sorted(headers)

    def _struct_proxy_headers(self, struct_decl: StructDecl) -> list[str]:
        headers: set[str] = set()
        for field in struct_decl.fields:
            self._collect_proxy_headers(field.ty, headers)
            # Also collect stub headers for interface types used in marshalling
            self._collect_stub_headers_for_struct(field.ty, headers)
        return sorted(headers)

    def _collect_stub_headers_for_struct(self, ty, headers: set[str]):
        """Collect stub headers needed for struct marshalling.

        When marshalling interface types in structs, we need stub headers
        because the generated code uses static_pointer_cast to Stub classes.
        """
        if isinstance(ty, IfaceType):
            headers.add(f"{self._stub_file_stem(ty.decl)}.h")
            return
        if isinstance(ty, VectorType):
            self._collect_stub_headers_for_struct(ty.val_ty, headers)
            return
        if isinstance(ty, ArrayType):
            self._collect_stub_headers_for_struct(ty.item_ty, headers)
            return
        if isinstance(ty, MapType):
            self._collect_stub_headers_for_struct(ty.key_ty, headers)
            self._collect_stub_headers_for_struct(ty.val_ty, headers)
            return
        if isinstance(ty, SetType):
            self._collect_stub_headers_for_struct(ty.key_ty, headers)
            return
        if isinstance(ty, StructType):
            for field in ty.decl.fields:
                self._collect_stub_headers_for_struct(field.ty, headers)

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
        ret_type = self.serializer.get_cpp_type(method.return_ty)
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
    def _write_method_declaration(
        f, indent: str, ret_type: str, name: str, params: list[str], suffix: str
    ):
        prefix = f"{indent}{ret_type} {name}("
        one_line = prefix + ", ".join(params) + ")" + suffix
        if len(one_line) <= InterfaceGenerator.MAX_LINE_LENGTH:
            f.write(one_line + "\n")
            return
        f.write(prefix + "\n")
        continuation = indent + "    "
        current = continuation
        for idx, part in enumerate(params):
            frag = part + (")" + suffix if idx == len(params) - 1 else ",")
            separator = "" if current == continuation else " "
            candidate = current + separator + frag
            if len(candidate) <= InterfaceGenerator.MAX_LINE_LENGTH:
                current = candidate
            else:
                if current != continuation:
                    f.write(current.rstrip() + "\n")
                current = continuation + frag
        f.write(current.rstrip() + "\n")

    @staticmethod
    def _needs_field_scope(ty) -> bool:
        return isinstance(ty, (VectorType, ArrayType, SetType, MapType))

    def _write_struct_header(self, f, struct_decl: StructDecl):
        guard = header_guard_for(struct_decl.name, struct_decl.parent_pkg)
        namespace = namespace_scope_for_cpp(struct_decl.parent_pkg)
        current_year = datetime.now().year
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

#include <IPCKit/ipc_kit.h>

#include <array>
#include <cstdint>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <vector>

""")
        for header in self._struct_headers(struct_decl):
            f.write(f'#include "{header}"\n')
        f.write("\n")
        self._write_namespace_open(f, namespace)
        f.write(f"struct {struct_decl.name} {{\n")
        for field in struct_decl.fields:
            cpp_type = self.serializer.get_cpp_type(field.ty)
            if isinstance(field.ty, ArrayType):
                f.write(
                    f"    {cpp_type} {field.name} = {self.serializer.empty_array_expr(field.ty)};\n"
                )
            else:
                f.write(f"    {cpp_type} {field.name};\n")
        f.write("\n    int32_t Marshalling(OHIPCParcel* parcel) const;\n")
        f.write("    int32_t Unmarshalling(const OHIPCParcel* parcel);\n")
        f.write("};\n\n")
        self._write_namespace_close(f, namespace)
        f.write(f"\n#endif // {guard}\n")

    def _write_struct_source(self, f, struct_decl: StructDecl):
        namespace = namespace_scope_for_cpp(struct_decl.parent_pkg)
        current_year = datetime.now().year
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

#include "{self._struct_file_stem(struct_decl)}.h"
""")
        for header in self._struct_proxy_headers(struct_decl):
            f.write(f'#include "{header}"\n')
        f.write("\n")
        self._write_namespace_open(f, namespace)
        f.write(
            f"int32_t {struct_decl.name}::Marshalling(OHIPCParcel* parcel) const\n{{\n"
        )
        for field in struct_decl.fields:
            code = self.serializer.generate_write_code(
                "parcel",
                field.name,
                field.ty,
                "        " if self._needs_field_scope(field.ty) else "    ",
            )
            if self._needs_field_scope(field.ty):
                f.write("    {\n")
                f.write(code + "\n")
                f.write("    }\n")
            else:
                f.write(code + "\n")
        f.write("    return OH_IPC_SUCCESS;\n}\n\n")
        f.write(
            f"int32_t {struct_decl.name}::Unmarshalling(const OHIPCParcel* parcel)\n{{\n"
        )
        for field in struct_decl.fields:
            code = self.serializer.generate_read_code(
                "parcel",
                field.name,
                field.ty,
                "        " if self._needs_field_scope(field.ty) else "    ",
                is_decl=False,
            )
            if self._needs_field_scope(field.ty):
                f.write("    {\n")
                f.write(code + "\n")
                f.write("    }\n")
            else:
                f.write(code + "\n")
        f.write("    return OH_IPC_SUCCESS;\n}\n\n")
        self._write_namespace_close(f, namespace)

    def _write_struct_bundle_header(
        self,
        f,
        bundle_name: str,
        struct_decls: list[StructDecl],
        override_pkg: PackageDecl | None = None,
    ):
        # Use override package if provided (from main service interface), otherwise use struct's own package
        pkg = override_pkg if override_pkg is not None else struct_decls[0].parent_pkg
        guard = header_guard_for(bundle_name, pkg)
        namespace = namespace_scope_for_cpp(pkg)
        current_year = datetime.now().year
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

#include <IPCKit/ipc_kit.h>

#include <array>
#include <cstdint>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <vector>

""")
        includes: set[str] = set()
        for struct_decl in struct_decls:
            includes.update(self._struct_headers(struct_decl))
        for header in sorted(includes):
            if header != f"{bundle_name}.h":
                f.write(f'#include "{header}"\n')
        f.write("\n")
        self._write_namespace_open(f, namespace)
        for struct_decl in struct_decls:
            f.write(f"struct {struct_decl.name} {{\n")
            for field in struct_decl.fields:
                cpp_type = self.serializer.get_cpp_type(field.ty)
                if isinstance(field.ty, ArrayType):
                    f.write(
                        f"    {cpp_type} {field.name} = {self.serializer.empty_array_expr(field.ty)};\n"
                    )
                else:
                    f.write(f"    {cpp_type} {field.name};\n")
            f.write("\n    int32_t Marshalling(OHIPCParcel* parcel) const;\n")
            f.write("    int32_t Unmarshalling(const OHIPCParcel* parcel);\n")
            f.write("};\n\n")
        self._write_namespace_close(f, namespace)
        f.write(f"\n#endif // {guard}\n")

    def _write_struct_bundle_source(
        self,
        f,
        bundle_name: str,
        struct_decls: list[StructDecl],
        override_pkg: PackageDecl | None = None,
    ):
        # Use override package if provided (from main service interface), otherwise use struct's own package
        pkg = override_pkg if override_pkg is not None else struct_decls[0].parent_pkg
        namespace = namespace_scope_for_cpp(pkg)
        current_year = datetime.now().year
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

#include "{bundle_name}.h"
""")
        proxy_headers: set[str] = set()
        for struct_decl in struct_decls:
            proxy_headers.update(self._struct_proxy_headers(struct_decl))
        for header in sorted(proxy_headers):
            f.write(f'#include "{header}"\n')
        f.write("\n")
        self._write_namespace_open(f, namespace)
        for struct_decl in struct_decls:
            f.write(
                f"int32_t {struct_decl.name}::Marshalling(OHIPCParcel* parcel) const\n{{\n"
            )
            for field in struct_decl.fields:
                code = self.serializer.generate_write_code(
                    "parcel",
                    field.name,
                    field.ty,
                    "        " if self._needs_field_scope(field.ty) else "    ",
                )
                if self._needs_field_scope(field.ty):
                    f.write("    {\n")
                    f.write(code + "\n")
                    f.write("    }\n")
                else:
                    f.write(code + "\n")
            f.write("    return OH_IPC_SUCCESS;\n}\n\n")
            f.write(
                f"int32_t {struct_decl.name}::Unmarshalling(const OHIPCParcel* parcel)\n{{\n"
            )
            for field in struct_decl.fields:
                code = self.serializer.generate_read_code(
                    "parcel",
                    field.name,
                    field.ty,
                    "        " if self._needs_field_scope(field.ty) else "    ",
                    is_decl=False,
                )
                if self._needs_field_scope(field.ty):
                    f.write("    {\n")
                    f.write(code + "\n")
                    f.write("    }\n")
                else:
                    f.write(code + "\n")
            f.write("    return OH_IPC_SUCCESS;\n}\n\n")
        self._write_namespace_close(f, namespace)

    def _write_enum_header(self, f, enum_decl: EnumDecl):
        guard = header_guard_for(enum_decl.name, enum_decl.parent_pkg)
        namespace = namespace_scope_for_cpp(enum_decl.parent_pkg)
        current_year = datetime.now().year
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

#include <cstdint>

""")
        self._write_namespace_open(f, namespace)
        # Get the underlying type (default to int32_t if not specified)
        underlying_type = "int32_t"
        if enum_decl.ty is not None:
            from taihe.semantics.types import ScalarType

            if isinstance(enum_decl.ty, ScalarType):
                underlying_type = self.serializer.get_cpp_type(enum_decl.ty)

        f.write(f"enum class {enum_decl.name} : {underlying_type} {{\n")
        for item in enum_decl.items:
            value_str = str(item.raw_value) if item.raw_value is not None else ""
            if value_str:
                f.write(f"    {item.name} = {value_str},\n")
            else:
                f.write(f"    {item.name},\n")
        f.write("};\n\n")
        self._write_namespace_close(f, namespace)
        f.write(f"\n#endif // {guard}\n")

    def _write_enum_bundle_header(
        self,
        f,
        bundle_name: str,
        enum_decls: list[EnumDecl],
        override_pkg: PackageDecl | None = None,
    ):
        # Use override package if provided (from main service interface), otherwise use enum's own package
        pkg = override_pkg if override_pkg is not None else enum_decls[0].parent_pkg
        guard = header_guard_for(bundle_name, pkg)
        namespace = namespace_scope_for_cpp(pkg)
        current_year = datetime.now().year
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

#include <cstdint>

""")
        self._write_namespace_open(f, namespace)
        for enum_decl in enum_decls:
            # Get the underlying type (default to int32_t if not specified)
            underlying_type = "int32_t"
            if enum_decl.ty is not None:
                from taihe.semantics.types import ScalarType

                if isinstance(enum_decl.ty, ScalarType):
                    underlying_type = self.serializer.get_cpp_type(enum_decl.ty)

            f.write(f"enum class {enum_decl.name} : {underlying_type} {{\n")
            for item in enum_decl.items:
                value_str = str(item.raw_value) if item.raw_value is not None else ""
                if value_str:
                    f.write(f"    {item.name} = {value_str},\n")
                else:
                    f.write(f"    {item.name},\n")
            f.write("};\n\n")
        self._write_namespace_close(f, namespace)
        f.write(f"\n#endif // {guard}\n")

    def _write_header(self, f, iface: IfaceDecl, info: IfaceOhIpcInfo):
        guard = header_guard_for(iface.name, iface.parent_pkg)
        namespace = namespace_scope_for_cpp(iface.parent_pkg)
        current_year = datetime.now().year
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

#include <IPCKit/ipc_kit.h>

#include <array>
#include <cstdint>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <vector>


""")
        for header in self._iface_headers(iface):
            f.write(f'#include "{header}"\n')
        f.write("\n")
        self._write_namespace_open(f, namespace)
        f.write("using ErrCode = int32_t;\n\n")
        f.write(f"class {iface.name} {{\npublic:\n")
        f.write(f"    virtual ~{iface.name}() = default;\n")
        descriptor = interface_descriptor_for_cpp(iface)
        f.write(
            f'    static const char* GetDescriptor() {{ return "{descriptor}"; }}\n\n'
        )
        f.write("    enum class IpcCode : uint32_t {\n")
        for method in iface.methods:
            m_info = MethodOhIpcInfo.get(self.am, method)
            f.write(f"        {m_info.command_name} = {m_info.ipc_code},\n")

        if info.is_main_service:
            f.write(
                f"        COMMAND_GET_TYPE_LIB_INFO = {info.get_type_lib_info_code},\n"
            )
        f.write(f"        COMMAND_GET_VERSION = {info.get_version_code},\n")
        f.write(f"        COMMAND_GET_TAIHE_VERSION = {info.get_taihe_version_code},\n")

        f.write("    };\n\n")
        for method in iface.methods:
            self._write_method_declaration(
                f,
                "    ",
                "virtual ErrCode",
                method.name,
                self._method_param_parts(method),
                " = 0;",
            )

        if info.is_main_service:
            self._write_method_declaration(
                f,
                "    ",
                "virtual ErrCode",
                "GetTypeLibInfo",
                ["int32_t fd"],
                " = 0;",
            )
        self._write_method_declaration(
            f,
            "    ",
            "virtual ErrCode",
            "GetVersion",
            ["std::string& result"],
            " = 0;",
        )
        self._write_method_declaration(
            f,
            "    ",
            "virtual ErrCode",
            "GetTaiheVersion",
            ["std::string& result"],
            " = 0;",
        )

        f.write("};\n\n")
        self._write_namespace_close(f, namespace)
        f.write(f"\n#endif // {guard}\n")
