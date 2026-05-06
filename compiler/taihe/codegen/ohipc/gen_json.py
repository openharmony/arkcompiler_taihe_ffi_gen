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

import json
from pathlib import Path
from taihe.utils.analyses import AnalysisManager
from taihe.utils.outputs import OutputManager
from taihe.semantics.declarations import EnumDecl, IfaceDecl, PackageGroup, StructDecl
from taihe.semantics.types import (
    ArrayType,
    EnumType,
    IfaceType,
    MapType,
    ScalarType,
    SetType,
    StringType,
    StructType,
    UnitType,
    VectorType,
    VoidType,
)
from taihe.codegen.ohipc.analyses import (
    IfaceOhIpcInfo,
    MethodOhIpcInfo,
    fixed_array_size,
    interface_descriptor_for_cpp,
)
from taihe.codegen.ohipc.typelib_schema import (
    TypeInfo,
    TypeLibEnum,
    TypeLibEnumValue,
    TypeLibInterface,
    TypeLibMethod,
    TypeLibParameter,
    TypeLibSchema,
    TypeLibStruct,
    TypeLibStructField,
)


class JsonGenerator:
    def __init__(self, om: OutputManager, am: AnalysisManager):
        self.om = om
        self.am = am
        self._member_id = 1
        self._taihe_version = self._load_taihe_version()

    def _load_taihe_version(self) -> str:
        """Load taihe version from taihe_version.json"""
        version_file = Path(__file__).parent / "taihe_version.json"
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("version", "")
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return ""

    def _next_member_id(self) -> int:
        member_id = self._member_id
        self._member_id += 1
        return member_id

    @staticmethod
    def _decl_sort_key(
        decl: EnumDecl | StructDecl | IfaceDecl,
    ) -> tuple[str, str, int, int, str]:
        loc = decl.loc
        if loc is None:
            return (decl.parent_pkg.name, "", 0, 0, decl.name)

        start = loc.span.start if loc.span is not None else None
        return (
            decl.parent_pkg.name,
            loc.file.source_identifier,
            start.row if start is not None else 0,
            start.col if start is not None else 0,
            decl.name,
        )

    def _sorted_enum_decls(self, pg: PackageGroup) -> list[EnumDecl]:
        decls: list[EnumDecl] = []
        for pkg in pg.iterate():
            decls.extend(pkg.enums)
        return sorted(decls, key=self._decl_sort_key)

    def _sorted_struct_decls(self, pg: PackageGroup) -> list[StructDecl]:
        decls: list[StructDecl] = []
        for pkg in pg.iterate():
            decls.extend(pkg.structs)
        return sorted(decls, key=self._decl_sort_key)

    def _sorted_iface_decls(self, pg: PackageGroup) -> list[IfaceDecl]:
        decls: list[IfaceDecl] = []
        for pkg in pg.iterate():
            decls.extend(pkg.interfaces)
        return sorted(decls, key=self._decl_sort_key)

    def _type_name(self, ty) -> str:
        if isinstance(ty, ScalarType):
            return ty.kind.symbol
        if isinstance(ty, StringType):
            return "String"
        if isinstance(ty, (VoidType, UnitType)):
            return "void"
        if isinstance(ty, EnumType):
            return ty.decl.name
        if isinstance(ty, StructType):
            return ty.decl.name
        if isinstance(ty, IfaceType):
            return ty.decl.name
        if isinstance(ty, ArrayType):
            return f"Array<{self._type_name(ty.item_ty)}>"
        if isinstance(ty, VectorType):
            return f"Vector<{self._type_name(ty.val_ty)}>"
        if isinstance(ty, SetType):
            return f"Set<{self._type_name(ty.key_ty)}>"
        if isinstance(ty, MapType):
            return f"Map<{self._type_name(ty.key_ty)}, {self._type_name(ty.val_ty)}>"
        return ty.signature

    def _type_info(self, ty) -> TypeInfo:
        if isinstance(ty, IfaceType):
            return TypeInfo(type="interface", idl_type=ty.decl.name)
        elif isinstance(ty, StructType):
            return TypeInfo(type="struct", idl_type=ty.decl.name)
        elif isinstance(ty, EnumType):
            return TypeInfo(type="enum", idl_type=ty.decl.name)
        elif isinstance(ty, MapType):
            # For map: type + key_type (TypeInfo) + value_type (TypeInfo)
            key_type_info = self._type_info(ty.key_ty)
            value_type_info = self._type_info(ty.val_ty)
            return TypeInfo(
                type="map",
                key_type=key_type_info,
                value_type=value_type_info,
            )
        elif isinstance(ty, ArrayType):
            # For array: type + value_type (recursive TypeInfo)
            item_type_info = self._type_info(ty.item_ty)
            return TypeInfo(
                type="array",
                size=fixed_array_size(ty),
                value_type=item_type_info,
            )
        elif isinstance(ty, VectorType):
            # For vector: type + value_type (recursive TypeInfo)
            val_type_info = self._type_info(ty.val_ty)
            return TypeInfo(type="vector", value_type=val_type_info)
        elif isinstance(ty, SetType):
            # For set: type + value_type (recursive TypeInfo)
            key_type_info = self._type_info(ty.key_ty)
            return TypeInfo(type="set", value_type=key_type_info)
        else:
            # For scalar types (i32, f32, String, etc.): only type field
            type_name = self._type_name(ty)
            return TypeInfo(type=type_name)

    def _is_valid_map_key_type(self, ty) -> bool:
        return isinstance(ty, (ScalarType, StringType, EnumType))

    def _validate_type(self, ty, location: str) -> None:
        if isinstance(ty, MapType):
            if not self._is_valid_map_key_type(ty.key_ty):
                raise ValueError(
                    f"Invalid map key type '{ty.key_ty.signature}' in {location}. "
                    "Map key only supports basic types (scalar, string, enum)."
                )
            self._validate_type(ty.key_ty, location)
            self._validate_type(ty.val_ty, location)
            return
        if isinstance(ty, ArrayType):
            self._validate_type(ty.item_ty, location)
            return
        if isinstance(ty, VectorType):
            self._validate_type(ty.val_ty, location)
            return
        if isinstance(ty, SetType):
            self._validate_type(ty.key_ty, location)
            return
        # Other types (ScalarType, StringType, EnumType, StructType, IfaceType, VoidType, UnitType)
        # do not need recursive validation for map key restrictions.

    def validate(self, pg: PackageGroup) -> None:
        for pkg in pg.iterate():
            for struct_decl in pkg.structs:
                for field in struct_decl.fields:
                    self._validate_type(
                        field.ty, f"struct '{struct_decl.name}' field '{field.name}'"
                    )
            for iface in pkg.interfaces:
                for method in iface.methods:
                    self._validate_type(
                        method.return_ty,
                        f"return type of method '{method.name}' in interface '{iface.name}'",
                    )
                    for param in method.params:
                        self._validate_type(
                            param.ty,
                            f"parameter '{param.name}' of method '{method.name}' in interface '{iface.name}'",
                        )

    @staticmethod
    def _param_mode(param) -> str:
        return "in"

    @staticmethod
    def _strip_interface_prefix(name: str) -> str:
        if len(name) > 1 and name.startswith("I") and name[1].isupper():
            return name[1:]
        return name

    def _pick_primary_iface(self, pg: PackageGroup) -> str:
        from taihe.codegen.ohipc.attribute import MainServiceAttribute

        first_iface_name = ""

        for iface in self._sorted_iface_decls(pg):
            if not first_iface_name:
                first_iface_name = iface.name
            if MainServiceAttribute.get(iface) is not None:
                return iface.name

        return first_iface_name

    def _main_iface(self, pg: PackageGroup) -> IfaceDecl | None:
        from taihe.codegen.ohipc.attribute import MainServiceAttribute

        for iface in self._sorted_iface_decls(pg):
            if MainServiceAttribute.get(iface) is not None:
                return iface
        return None

    def _typelib_filename_for_iface_name(self, iface_name: str) -> str:
        iface_base = (
            self._strip_interface_prefix(iface_name).lower()
            if iface_name
            else "service"
        )
        return f"{iface_base}.typelib.json"

    def _typelib_filename(self, pg: PackageGroup) -> str:
        iface_name = self._pick_primary_iface(pg)
        return self._typelib_filename_for_iface_name(iface_name)

    def _interface_descriptor(self, iface: IfaceDecl) -> str:
        return interface_descriptor_for_cpp(iface)

    def _build_schema(
        self, pg: PackageGroup, target_iface: IfaceDecl | None = None
    ) -> TypeLibSchema:
        self._member_id = 1
        schema = TypeLibSchema()
        schema.taihe_version = self._taihe_version

        for enum_decl in self._sorted_enum_decls(pg):
            tl_enum = TypeLibEnum(
                name=enum_decl.name,
                member_id=self._next_member_id(),
            )
            for item in enum_decl.items:
                tl_enum.values.append(
                    TypeLibEnumValue(
                        name=item.name,
                        value=item.raw_value,
                        member_id=self._next_member_id(),
                    )
                )
            schema.enums.append(tl_enum)

        for struct_decl in self._sorted_struct_decls(pg):
            tl_struct = TypeLibStruct(
                name=struct_decl.name,
                member_id=self._next_member_id(),
            )
            for field in struct_decl.fields:
                tl_struct.fields.append(
                    TypeLibStructField(
                        name=field.name,
                        type_info=self._type_info(field.ty),
                        member_id=self._next_member_id(),
                    )
                )
            schema.structs.append(tl_struct)

        iface_decls = (
            [target_iface] if target_iface is not None else self._sorted_iface_decls(pg)
        )
        for iface in iface_decls:
            iface_info = IfaceOhIpcInfo.get(self.am, iface)
            from taihe.codegen.ohipc.attribute import (
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

            descriptor = self._interface_descriptor(iface)

            tli = TypeLibInterface(
                name=iface.name,
                descriptor=descriptor,
                interface_type=interface_type,
                member_id=self._next_member_id(),
            )

            for method in iface.methods:
                m_info = MethodOhIpcInfo.get(self.am, method)
                params = []
                for p in method.params:
                    params.append(
                        TypeLibParameter(
                            name=p.name,
                            type_info=self._type_info(p.ty),
                            direction="in",
                            member_id=self._next_member_id(),
                        )
                    )

                tlm = TypeLibMethod(
                    name=method.name,
                    code=m_info.ipc_code,
                    oneway=m_info.is_oneway,
                    return_type=self._type_info(method.return_ty),
                    member_id=self._next_member_id(),
                    parameters=params,
                )
                tli.methods.append(tlm)

            schema.interfaces.append(tli)

        return schema

    def generate(self, pg: PackageGroup):
        main_iface = self._main_iface(pg)
        if main_iface is None:
            return

        primary_filename = self._typelib_filename_for_iface_name(main_iface.name)
        primary_schema = self._build_schema(pg)
        with self.om.open(primary_filename, "w") as f:
            json.dump(primary_schema.to_dict(), f, indent=2)

        for iface in self._sorted_iface_decls(pg):
            if iface is main_iface:
                continue
            stale_typelib = self.om.dst_dir / self._typelib_filename_for_iface_name(iface.name)
            if stale_typelib.exists():
                stale_typelib.unlink()
