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
from pathlib import Path
from typing import TYPE_CHECKING

from taihe.driver.backend import Backend, BackendConfig
from taihe.driver.options import AbstractConfigOption
from taihe.utils.exceptions import AdhocError, AdhocNote
from taihe.utils.sources import SourceFile

if TYPE_CHECKING:
    from taihe.driver.contexts import CompilerInstance
    from taihe.driver.options import OptionRegistry, OptionStore
    from taihe.utils.diagnostics import DiagnosticsManager


@dataclass
class OhIpcCommonFileOption(AbstractConfigOption):
    NAME = "modobj:ipc-common"

    paths: list[Path] = dataclass_field(default_factory=list)

    @classmethod
    def try_parse(cls, value: str | None, dm: "DiagnosticsManager"):
        if value is None:
            return cls(paths=[])
        raw_items = [item.strip() for item in value.split(";") if item.strip()]
        return cls(paths=[Path(item).resolve() for item in raw_items])


@dataclass
class ModObjIpcBackendConfig(BackendConfig):
    NAME = "modobj-ipc"

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
        from taihe.codegen.modobj.gen_interface import InterfaceGenerator
        from taihe.codegen.modobj.gen_json import JsonGenerator
        from taihe.codegen.modobj.gen_proxy import ProxyGenerator
        from taihe.codegen.modobj.gen_stub import StubGenerator

        class OhIpcBackendImpl(Backend):
            def __init__(self, ci: "CompilerInstance", config: ModObjIpcBackendConfig):
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
                from taihe.codegen.modobj.analyses import package_name_to_file_stem

                return package_name_to_file_stem(pkg_name)

            @staticmethod
            def _main_service_iface_pkg(pg):
                from taihe.codegen.modobj.attribute import MainServiceAttribute

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
                                    "MODOBJIPC generation does not allow interface/enum/struct declarations "
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
                    from taihe.codegen.modobj.analyses import fixed_array_size

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
                from taihe.codegen.modobj.attribute import all_attr_types

                self._ci.attribute_registry.register(*all_attr_types)

            def validate(self):
                from taihe.codegen.modobj.analyses import MethodOhIpcInfo
                from taihe.codegen.modobj.attribute import MainServiceAttribute
                from taihe.semantics.declarations import GenericTypeRefDecl
                from taihe.semantics.types import VoidType

                def has_list_type_ref(ty_ref) -> bool:
                    if isinstance(ty_ref, GenericTypeRefDecl):
                        if ty_ref.symbol == "List":
                            return True
                        return any(has_list_type_ref(arg.ty_ref) for arg in ty_ref.args)
                    return False

                pg = self._ci.package_group

                # Validate that there is exactly one main service interface in non-ipc-common packages
                main_service_ifaces = []
                ipc_common_main_services = []

                for pkg in pg.iterate():
                    for iface in pkg.interfaces:
                        if MainServiceAttribute.get(iface) is not None:
                            if self._is_ipc_common_pkg(pkg):
                                # ipc-common packages are not allowed to have main_service
                                ipc_common_main_services.append(iface)
                            else:
                                main_service_ifaces.append(iface)

                # Check if any ipc-common package has main_service
                if ipc_common_main_services:
                    err = AdhocError(
                        f"MODOBJIPC backend does not allow @main_service attribute in ipc-common packages, but found {len(ipc_common_main_services)}."
                    )
                    err.notes = lambda: [
                        AdhocNote(
                            f"main service interface '{iface.name}' in ipc-common package '{iface.parent_pkg.name}' declared here",
                            loc=iface.loc,
                        )
                        for iface in ipc_common_main_services
                    ]
                    self._ci.diagnostics_manager.emit(err)
                    return

                # Validate main interface files have exactly one main_service
                if len(main_service_ifaces) == 0:
                    raise ValueError(
                        "MODOBJIPC backend requires exactly one interface with @main_service attribute in main interface files (non-ipc-common), but found none."
                    )
                elif len(main_service_ifaces) > 1:
                    err = AdhocError(
                        f"MODOBJIPC backend requires exactly one interface with @main_service attribute in main interface files (non-ipc-common), but found {len(main_service_ifaces)}."
                    )
                    err.notes = lambda: [
                        AdhocNote(
                            f"main service interface '{iface.name}' declared here",
                            loc=iface.loc,
                        )
                        for iface in main_service_ifaces
                    ]
                    self._ci.diagnostics_manager.emit(err)
                    return

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
                                    "MODOBJIPC backend requires oneway methods to return void. "
                                    f"Method '{method.name}' in interface '{iface.name}' "
                                    f"returns '{method.return_ty.signature}'."
                                )
                            if has_list_type_ref(method.return_ty_ref):
                                raise ValueError(
                                    f"List type is not supported in MODOBJIPC backend. "
                                    f"Method '{method.name}' in interface '{iface.name}' has List return type."
                                )
                            for param in method.params:
                                if has_list_type_ref(param.ty_ref):
                                    raise ValueError(
                                        f"List type is not supported in MODOBJIPC backend. "
                                        f"Parameter '{param.name}' in method '{method.name}' of interface '{iface.name}' has List type."
                                    )
                    for struct in pkg.structs:
                        for struct_field in struct.fields:
                            if has_list_type_ref(struct_field.ty_ref):
                                raise ValueError(
                                    f"List type is not supported in MODOBJIPC backend. "
                                    f"Field '{struct_field.name}' in struct '{struct.name}' has List type."
                                )

                self._validate_generated_type_names(pg)
                self._validate_fixed_array_types(pg)

            def generate(self):
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
                                    bundle_name,
                                    common_structs,
                                    main_iface_pkg,
                                    common_enums,
                                )
                            else:
                                iface_gen.generate_struct_bundle(
                                    bundle_name,
                                    common_structs,
                                    enum_decls=common_enums,
                                )

                        elif common_enums:
                            if main_iface_pkg is not None:
                                iface_gen.generate_enum_bundle(
                                    bundle_name, common_enums, main_iface_pkg
                                )
                            else:
                                iface_gen.generate_enum_bundle(
                                    bundle_name, common_enums
                                )
                        continue

                    # Generate headers for regular structs in the package
                    for struct_decl in pkg.structs:
                        iface_gen.generate_struct(struct_decl)
                        iface_gen.generate_struct_source(struct_decl)

                    # Generate headers for regular enums in the package
                    for enum_decl in pkg.enums:
                        iface_gen.generate_enum(enum_decl)

        return OhIpcBackendImpl(instance, self)
