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

from dataclasses import dataclass, field


@dataclass
class TypeInfo:
    type: str
    idl_type: str = ""
    size: int | None = None
    key_type: "TypeInfo | str | None" = None
    value_type: "TypeInfo | str | None" = None
    item_type: "TypeInfo | None" = None
    val_type: "TypeInfo | None" = None


@dataclass
class TypeLibEnumValue:
    name: str
    value: int | float | str | bool | None
    member_id: int = 0


@dataclass
class TypeLibEnum:
    name: str
    member_id: int = 0
    values: list[TypeLibEnumValue] = field(default_factory=list)


@dataclass
class TypeLibStructField:
    name: str
    type_info: TypeInfo
    member_id: int = 0


@dataclass
class TypeLibStruct:
    name: str
    member_id: int = 0
    fields: list[TypeLibStructField] = field(default_factory=list)


@dataclass
class TypeLibParameter:
    name: str
    type_info: TypeInfo
    direction: str
    member_id: int = 0


@dataclass
class TypeLibMethod:
    name: str
    code: int
    oneway: bool
    return_type: TypeInfo
    member_id: int = 0
    parameters: list[TypeLibParameter] = field(default_factory=list)
    return_value_parameter: TypeLibParameter | None = None


@dataclass
class TypeLibInterface:
    name: str
    descriptor: str
    interface_type: int = 0
    member_id: int = 0
    methods: list[TypeLibMethod] = field(default_factory=list)


@dataclass
class TypeLibSchema:
    version: str = "1.0"
    taihe_version: str = ""
    enums: list[TypeLibEnum] = field(default_factory=list)
    structs: list[TypeLibStruct] = field(default_factory=list)
    interfaces: list[TypeLibInterface] = field(default_factory=list)
    copyright: str = ""

    def to_dict(self):
        def _type_info_dict(type_info: TypeInfo):
            result = {"type": type_info.type}
            if type_info.size is not None:
                result["size"] = type_info.size
            if type_info.key_type is not None:
                # key_type can be string or TypeInfo
                if isinstance(type_info.key_type, str):
                    result["key_type"] = type_info.key_type
                else:
                    result["key_type"] = _type_info_dict(type_info.key_type)
            if type_info.value_type is not None:
                # value_type can be string or TypeInfo
                if isinstance(type_info.value_type, str):
                    result["value_type"] = type_info.value_type
                else:
                    result["value_type"] = _type_info_dict(type_info.value_type)
            if type_info.idl_type:
                result["idl_type"] = type_info.idl_type
            if type_info.item_type is not None:
                result["item_type"] = _type_info_dict(type_info.item_type)
            if type_info.val_type is not None:
                result["val_type"] = _type_info_dict(type_info.val_type)
            return result

        result = {
            "version": self.version,
            "taihe_version": self.taihe_version,
            "enums": [
                {
                    "memberId": enum.member_id,
                    "name": enum.name,
                    "values": [
                        {
                            "memberId": value.member_id,
                            "name": value.name,
                            "value": value.value,
                        }
                        for value in enum.values
                    ],
                }
                for enum in self.enums
            ],
            "structs": [
                {
                    "memberId": struct.member_id,
                    "name": struct.name,
                    "fields": [
                        {
                            "memberId": field.member_id,
                            "name": field.name,
                            "type_info": _type_info_dict(field.type_info),
                        }
                        for field in struct.fields
                    ],
                }
                for struct in self.structs
            ],
            "interfaces": [
                {
                    "memberId": iface.member_id,
                    "name": iface.name,
                    "descriptor": iface.descriptor,
                    "interface_type": iface.interface_type,
                    "methods": [
                        {
                            "memberId": m.member_id,
                            "name": m.name,
                            "code": m.code,
                            "oneway": m.oneway,
                            "return_type": _type_info_dict(m.return_type),
                            "parameters": [
                                {
                                    "memberId": p.member_id,
                                    "name": p.name,
                                    "type_info": _type_info_dict(p.type_info),
                                }
                                for p in m.parameters
                            ],
                        }
                        for m in iface.methods
                    ],
                }
                for iface in self.interfaces
            ],
        }
        if self.copyright:
            result["copyright"] = self.copyright
        return result
