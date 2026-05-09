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

from taihe.semantics.attributes import AttributeGroupTag, CheckedAttrT, TypedAttribute
from taihe.semantics.declarations import (
    IfaceDecl,
    IfaceMethodDecl,
    PackageDecl,
    ParamDecl,
    TypeRefDecl,
)
from taihe.semantics.types import ArrayType
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import AdhocError

MAIN_INTERFACE_GROUP = AttributeGroupTag()


@dataclass
class NamespaceAttr(TypedAttribute[PackageDecl]):
    NAME = "namespace"
    TARGETS = (PackageDecl,)

    module: str
    namespace: str | None = None


@dataclass
class OnewayAttribute(TypedAttribute[IfaceMethodDecl]):
    """Marks a method as asynchronous (one-way)."""

    NAME = "oneway"
    TARGETS = (IfaceMethodDecl,)


@dataclass
class MainServiceAttribute(TypedAttribute[IfaceDecl]):
    """Marks an interface as the main service interface with a version."""

    NAME = "main_service"
    TARGETS = (IfaceDecl,)
    ATTRIBUTE_GROUP_TAGS = frozenset({MAIN_INTERFACE_GROUP})

    version: str = "1"


@dataclass
class CallbackAttribute(TypedAttribute[IfaceDecl]):
    """Marks an interface as a callback interface."""

    NAME = "callback"
    TARGETS = (IfaceDecl,)


@dataclass
class IpcCodeAttribute(TypedAttribute[IfaceMethodDecl]):
    """Specifies the IPC code for a method."""

    NAME = "ipccode"
    TARGETS = (IfaceMethodDecl,)

    code: int = 0


@dataclass
class IpcInCapacityAttribute(TypedAttribute[IfaceMethodDecl]):
    """Specifies the IPC input capacity in KB."""

    NAME = "ipcincapacity"
    TARGETS = (IfaceMethodDecl,)

    capacity: int = 0


@dataclass
class IpcOutCapacityAttribute(TypedAttribute[IfaceMethodDecl]):
    """Specifies the IPC output capacity in KB."""

    NAME = "ipcoutcapacity"
    TARGETS = (IfaceMethodDecl,)

    capacity: int = 0


PARAM_DIRECTION_GROUP = AttributeGroupTag()


@dataclass
class InAttribute(TypedAttribute[ParamDecl]):
    """Marks a parameter as input."""

    NAME = "in"
    TARGETS = (ParamDecl,)
    ATTRIBUTE_GROUP_TAGS = frozenset({PARAM_DIRECTION_GROUP})


@dataclass
class OutAttribute(TypedAttribute[ParamDecl]):
    """Marks a parameter as output."""

    NAME = "out"
    TARGETS = (ParamDecl,)
    ATTRIBUTE_GROUP_TAGS = frozenset({PARAM_DIRECTION_GROUP})


@dataclass
class SizeAttribute(TypedAttribute[TypeRefDecl]):
    """Specifies a fixed OHIPC array size on an array type reference."""

    NAME = "size"
    TARGETS = (TypeRefDecl,)

    size: int

    def check_typed_context(self, parent: TypeRefDecl, dm: DiagnosticsManager) -> None:
        if not isinstance(parent.resolved_ty, ArrayType):
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to array types.",
                    loc=self.loc,
                )
            )
        elif self.size <= 0:
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' requires a positive integer size.",
                    loc=self.loc,
                )
            )

        super().check_typed_context(parent, dm)


all_attr_types: list[CheckedAttrT] = [
    OnewayAttribute,
    MainServiceAttribute,
    CallbackAttribute,
    IpcCodeAttribute,
    IpcInCapacityAttribute,
    IpcOutCapacityAttribute,
    InAttribute,
    OutAttribute,
    SizeAttribute,
    NamespaceAttr,  # Support @!namespace attribute
]
