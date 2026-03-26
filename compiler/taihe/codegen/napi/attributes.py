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

from dataclasses import dataclass

from taihe.codegen.ani.attributes import (
    ArrayBufferAttr,
    AsyncAttribute,
    BigIntAttr,
    ClassAttr,
    ConstAttr,
    CtorAttr,
    ExtendsAttr,
    GetAttr,
    NamespaceAttr,
    NullAttr,
    PromiseAttribute,
    ReadOnlyAttr,
    RecordAttr,
    SetAttr,
    StaticAttr,
    TypedArrayAttr,
    UndefinedAttr,
)
from taihe.semantics.attributes import (
    RepeatableAttribute,
    TypedAttribute,
)
from taihe.semantics.declarations import (
    IfaceDecl,
    PackageDecl,
    StructDecl,
    TypeRefDecl,
)


@dataclass
class DtsTypeAttr(TypedAttribute[TypeRefDecl]):
    # TODO: Hack

    NAME = "dts_type"
    TARGETS = (TypeRefDecl,)

    type_name: str


@dataclass
class LibAttr(TypedAttribute[PackageDecl]):
    # TODO: Hack

    NAME = "lib"
    TARGETS = (PackageDecl,)

    lib_name: str


@dataclass
class DtsInjectAttr(RepeatableAttribute[PackageDecl]):
    # TODO: Hack

    NAME = "dts_inject"
    TARGETS = (PackageDecl,)

    dts_code: str


@dataclass
class DtsInjectIntoModuleAttr(RepeatableAttribute[PackageDecl]):
    # TODO: Hack

    NAME = "dts_inject_into_module"
    TARGETS = (PackageDecl,)

    dts_code: str


@dataclass
class DtsInjectIntoClazzAttr(RepeatableAttribute[IfaceDecl | StructDecl]):
    # TODO: Hack

    NAME = "dts_inject_into_class"
    TARGETS = (IfaceDecl, StructDecl)

    dts_code: str


@dataclass
class DtsInjectIntoIfaceAttr(RepeatableAttribute[IfaceDecl | StructDecl]):
    # TODO: Hack

    NAME = "dts_inject_into_interface"
    TARGETS = (IfaceDecl, StructDecl)

    dts_code: str


@dataclass
class TsInjectAttr(RepeatableAttribute[PackageDecl]):
    # TODO: Hack

    NAME = "ts_inject"
    TARGETS = (PackageDecl,)

    ts_code: str


@dataclass
class TsInjectIntoModuleAttr(RepeatableAttribute[PackageDecl]):
    # TODO: Hack

    NAME = "ts_inject_into_module"
    TARGETS = (PackageDecl,)

    ts_code: str


@dataclass
class TsInjectIntoClazzAttr(RepeatableAttribute[IfaceDecl | StructDecl]):
    # TODO: Hack

    NAME = "ts_inject_into_class"
    TARGETS = (IfaceDecl, StructDecl)

    ts_code: str


@dataclass
class TsInjectIntoIfaceAttr(RepeatableAttribute[IfaceDecl | StructDecl]):
    # TODO: Hack

    NAME = "ts_inject_into_interface"
    TARGETS = (IfaceDecl, StructDecl)

    ts_code: str


all_napi_attr_types = [
    DtsTypeAttr,
    LibAttr,
    DtsInjectAttr,
    DtsInjectIntoModuleAttr,
    DtsInjectIntoClazzAttr,
    DtsInjectIntoIfaceAttr,
    TsInjectAttr,
    TsInjectIntoModuleAttr,
    TsInjectIntoClazzAttr,
    TsInjectIntoIfaceAttr,
    # TODO: hack from ani
    ArrayBufferAttr,
    AsyncAttribute,
    BigIntAttr,
    ClassAttr,
    ConstAttr,
    CtorAttr,
    ExtendsAttr,
    GetAttr,
    NamespaceAttr,
    PromiseAttribute,
    RecordAttr,
    ReadOnlyAttr,
    SetAttr,
    StaticAttr,
    TypedArrayAttr,
    UndefinedAttr,
    NullAttr,
]
