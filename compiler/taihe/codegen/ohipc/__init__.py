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

from dataclasses import dataclass
from dataclasses import field as dataclass_field
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

from taihe.codegen.ohipc.analyses import fixed_array_size, package_name_to_file_stem
from taihe.codegen.ohipc.serialization import OhIpcSerializer
from taihe.driver.backend import Backend, BackendConfig
from taihe.driver.options import AbstractConfigOption
from taihe.semantics.types import ScalarType
from taihe.utils.exceptions import AdhocError, AdhocNote
from taihe.utils.outputs import BasicOutputManager
from taihe.utils.sources import SourceFile

if TYPE_CHECKING:
    from taihe.driver.contexts import CompilerInstance
    from taihe.driver.options import OptionRegistry, OptionStore
    from taihe.utils.diagnostics import DiagnosticsManager


@dataclass
class OhIpcCommonFileOption(AbstractConfigOption):
    NAME = "ohipc:ipc-common"

    paths: list[Path] = dataclass_field(default_factory=list)

    @classmethod
    def try_parse(cls, value: str | None, dm: "DiagnosticsManager"):
        if value is None:
            return cls(paths=[])
        raw_items = [item.strip() for item in value.split(";") if item.strip()]
        return cls(paths=[Path(item).resolve() for item in raw_items])


@dataclass
class OhIpcBackendConfig(BackendConfig):
    NAME = "ohipc-gen"

    ipc_common_paths: list[Path] = dataclass_field(default_factory=list)

    @classmethod
    def register_options_to(cls, option_registry: "OptionRegistry"):
        option_registry.register(OhIpcCommonFileOption)

    @classmethod
    def from_options(cls, options: "OptionStore", dm: "DiagnosticsManager"):
        ipc_common_opt = options.get(OhIpcCommonFileOption)
        return cls(
            ipc_common_paths=ipc_common_opt.paths if ipc_common_opt else [],
        )

    def build(self, instance: "CompilerInstance"):
        from taihe.codegen.ohipc.gen_interface import InterfaceGenerator
        from taihe.codegen.ohipc.gen_json import JsonGenerator
        from taihe.codegen.ohipc.gen_proxy import ProxyGenerator
        from taihe.codegen.ohipc.gen_stub import StubGenerator

        class OhIpcBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance", config: OhIpcBackendConfig):
                self._ci = ci
                self._config = config
                self._ipc_common_pkg_names = {
                    SourceFile(path.resolve()).pkg_name
                    for path in (config.ipc_common_paths or [])
                }

            def add_sources(self):
                existing_source_ids = {
                    source.source_identifier
                    for source in self._ci.source_manager.sources
                }

                for ipc_common_path in self._config.ipc_common_paths:
                    source = SourceFile(ipc_common_path.resolve())
                    if source.source_identifier in existing_source_ids:
                        continue
                    self._ci.source_manager.add_source(source)
                    existing_source_ids.add(source.source_identifier)

            def _is_ipc_common_pkg(self, pkg) -> bool:
                return pkg.name in self._ipc_common_pkg_names

            @staticmethod
            def _ipc_common_bundle_name(pkg_name: str) -> str:
                return package_name_to_file_stem(pkg_name)

            @staticmethod
            def _main_service_iface_pkg(pg):
                from taihe.codegen.ohipc.attribute import MainServiceAttribute

                for pkg in pg.iterate():
                    for iface in pkg.interfaces:
                        if MainServiceAttribute.get(iface) is not None:
                            return iface.parent_pkg
                return None

            def _validate_generated_type_names(self, pg) -> None:
                from taihe.semantics.declarations import EnumDecl, IfaceDecl, StructDecl

                type_kinds = (IfaceDecl, StructDecl, EnumDecl)
                seen: dict[str, IfaceDecl | StructDecl | EnumDecl] = {}

                for pkg in pg.iterate():
                    for decl in [*pkg.interfaces, *pkg.structs, *pkg.enums]:
                        if not isinstance(decl, type_kinds):
                            continue
                        if prev := seen.get(decl.name):
                            if prev.parent_pkg.name == decl.parent_pkg.name:
                                continue

                            err = AdhocError(
                                (
                                    "OHIPC generation does not allow interface/enum/struct declarations "
                                    f"with the same name: {decl.description!r}."
                                ),
                                loc=decl.loc,
                            )
                            err.notes = lambda prev=prev: [
                                AdhocNote(
                                    f"previous declaration is {prev.description!r}",
                                    loc=prev.loc,
                                )
                            ]
                            self._ci.diagnostics_manager.emit(err)
                            return
                        seen[decl.name] = decl

            def _validate_fixed_array_types(self, pg) -> None:
                from taihe.semantics.declarations import IfaceDecl, StructDecl
                from taihe.semantics.types import (
                    ArrayType,
                    MapType,
                    SetType,
                    StructType,
                    VectorType,
                )

                def ensure_fixed_array(ty) -> None:
                    if ty is None:
                        return
                    if isinstance(ty, ArrayType):
                        fixed_array_size(ty)
                        ensure_fixed_array(ty.item_ty)
                        return
                    if isinstance(ty, VectorType):
                        ensure_fixed_array(ty.val_ty)
                        return
                    if isinstance(ty, MapType):
                        ensure_fixed_array(ty.key_ty)
                        ensure_fixed_array(ty.val_ty)
                        return
                    if isinstance(ty, SetType):
                        ensure_fixed_array(ty.key_ty)
                        return
                    if isinstance(ty, StructType):
                        for struct_field in ty.decl.fields:
                            ensure_fixed_array(struct_field.ty)

                for pkg in pg.iterate():
                    for iface in pkg.interfaces:
                        assert isinstance(iface, IfaceDecl)
                        for method in iface.methods:
                            ensure_fixed_array(method.return_ty)
                            for param in method.params:
                                ensure_fixed_array(param.ty)
                    for struct in pkg.structs:
                        assert isinstance(struct, StructDecl)
                        for struct_field in struct.fields:
                            ensure_fixed_array(struct_field.ty)

            def setup(self):
                from taihe.codegen.ohipc.attribute import all_attr_types

                self._ci.attribute_registry.register(*all_attr_types)

            def validate(self):
                from taihe.codegen.ohipc.analyses import MethodOhIpcInfo
                from taihe.semantics.declarations import GenericTypeRefDecl
                from taihe.semantics.types import VoidType

                def has_list_type_ref(ty_ref) -> bool:
                    if isinstance(ty_ref, GenericTypeRefDecl):
                        if ty_ref.symbol == "List":
                            return True
                        return any(has_list_type_ref(arg.ty_ref) for arg in ty_ref.args)
                    return False

                pg = self._ci.package_group

                for pkg in pg.iterate():
                    for iface in pkg.interfaces:
                        for method in iface.methods:
                            method_info = MethodOhIpcInfo.get(
                                self._ci.analysis_manager, method
                            )
                            if method_info.is_oneway and not isinstance(
                                method.return_ty, VoidType
                            ):
                                raise ValueError(
                                    "OHIPC backend requires oneway methods to return void. "
                                    f"Method '{method.name}' in interface '{iface.name}' "
                                    f"returns '{method.return_ty.signature}'."
                                )
                            if has_list_type_ref(method.return_ty_ref):
                                raise ValueError(
                                    f"List type is not supported in OHIPC backend. "
                                    f"Method '{method.name}' in interface '{iface.name}' has List return type."
                                )
                            for param in method.params:
                                if has_list_type_ref(param.ty_ref):
                                    raise ValueError(
                                        f"List type is not supported in OHIPC backend. "
                                        f"Parameter '{param.name}' in method '{method.name}' of interface '{iface.name}' has List type."
                                    )
                    for struct in pkg.structs:
                        for struct_field in struct.fields:
                            if has_list_type_ref(struct_field.ty_ref):
                                raise ValueError(
                                    f"List type is not supported in OHIPC backend. "
                                    f"Field '{struct_field.name}' in struct '{struct.name}' has List type."
                                )

                self._validate_generated_type_names(pg)
                self._validate_fixed_array_types(pg)

            def generate(self):
                import os
                import tempfile

                om = self._ci.output_manager
                am = self._ci.analysis_manager
                pg = self._ci.package_group
                main_iface_pkg = self._main_service_iface_pkg(pg)

                iface_gen = InterfaceGenerator(om, am, self._ipc_common_pkg_names)
                proxy_gen = ProxyGenerator(om, am)
                stub_gen = StubGenerator(om, am)
                json_gen = JsonGenerator(om, am)

                # Validate map key types before generating any files.
                json_gen.validate(pg)

                # Generate JSON files first (needed by stub generator for typeLibInfo)
                json_gen.generate(pg)

                for pkg in pg.iterate():
                    # Generate code for each interface
                    for iface in pkg.interfaces:
                        iface_gen.generate(iface)
                        proxy_gen.generate(iface)
                        stub_gen.generate(iface)

                    if self._is_ipc_common_pkg(pkg):
                        bundle_name = self._ipc_common_bundle_name(pkg.name)
                        common_structs = list(pkg.structs)
                        common_enums = list(pkg.enums)

                        if common_structs:
                            if main_iface_pkg is not None:
                                iface_gen.generate_struct_bundle(
                                    bundle_name, common_structs, main_iface_pkg
                                )
                            else:
                                iface_gen.generate_struct_bundle(
                                    bundle_name, common_structs
                                )

                        if common_enums:
                            if not common_structs:
                                if main_iface_pkg is not None:
                                    iface_gen.generate_enum_bundle(
                                        bundle_name, common_enums, main_iface_pkg
                                    )
                                else:
                                    iface_gen.generate_enum_bundle(
                                        bundle_name, common_enums
                                    )
                                continue

                            if not isinstance(om, BasicOutputManager):
                                raise ValueError(
                                    "OHIPC backend requires BasicOutputManager for incremental header updates."
                                )
                            header_file = om.dst_dir.joinpath(f"{bundle_name}.h")
                            if header_file.exists():
                                temp_file_path: Path | None = None
                                try:
                                    content = header_file.read_text(encoding="utf-8")

                                    # Find the position before the innermost namespace closes
                                    lines = content.split("\n")

                                    # Find all namespace close positions
                                    namespace_close_positions = []
                                    for i, line in enumerate(lines):
                                        if line.strip().startswith("} // namespace"):
                                            namespace_close_positions.append(i)

                                    # Determine insert position
                                    if namespace_close_positions:
                                        # Insert before the FIRST namespace close (innermost)
                                        insert_pos = namespace_close_positions[0]
                                    else:
                                        # No namespace, insert before #endif
                                        for i, line in enumerate(lines):
                                            if line.strip().startswith("#endif"):
                                                insert_pos = i
                                                break
                                        else:
                                            # No #endif found, append to end
                                            insert_pos = len(lines)

                                    if insert_pos != -1:
                                        # Generate enum content (without namespace wrappers)
                                        enum_buffer = StringIO()
                                        serializer = OhIpcSerializer(
                                            self._ci.analysis_manager
                                        )

                                        for enum_decl in common_enums:
                                            underlying_type = "int32_t"
                                            if isinstance(enum_decl.ty, ScalarType):
                                                underlying_type = (
                                                    serializer.get_cpp_type(
                                                        enum_decl.ty
                                                    )
                                                )

                                            enum_buffer.write(
                                                f"enum class {enum_decl.name} : {underlying_type} {{\n"
                                            )
                                            for item in enum_decl.items:
                                                value_str = (
                                                    str(item.raw_value)
                                                    if item.raw_value is not None
                                                    else ""
                                                )
                                                if value_str:
                                                    enum_buffer.write(
                                                        f"    {item.name} = {value_str},\n"
                                                    )
                                                else:
                                                    enum_buffer.write(
                                                        f"    {item.name},\n"
                                                    )
                                            enum_buffer.write("};\n\n")

                                        # Insert enum content before the first namespace close
                                        enum_content = enum_buffer.getvalue()
                                        new_lines = (
                                            lines[:insert_pos]
                                            + enum_content.split("\n")
                                            + [""]
                                            + lines[insert_pos:]
                                        )
                                        new_content = "\n".join(new_lines)

                                        with tempfile.NamedTemporaryFile(
                                            mode="w",
                                            encoding="utf-8",
                                            dir=header_file.parent,
                                            delete=False,
                                        ) as temp_file:
                                            temp_file.write(new_content)
                                            temp_file.flush()
                                            os.fsync(temp_file.fileno())
                                            temp_file_path = Path(temp_file.name)

                                        temp_file_path.replace(header_file)
                                except OSError as e:
                                    if (
                                        temp_file_path is not None
                                        and temp_file_path.exists()
                                    ):
                                        temp_file_path.unlink(missing_ok=True)
                                    self._ci.diagnostics_manager.emit(
                                        AdhocError(
                                            f"Failed to update generated header file: {header_file}. Error: {e}",
                                            loc=None,
                                        )
                                    )
                                    raise
                        continue

                    # Generate headers for regular structs in the package
                    for struct_decl in pkg.structs:
                        iface_gen.generate_struct(struct_decl)
                        iface_gen.generate_struct_source(struct_decl)

                    # Generate headers for regular enums in the package
                    for enum_decl in pkg.enums:
                        iface_gen.generate_enum(enum_decl)

        return OhIpcBackendImpl(instance, self)
