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
from enum import Enum

from typing_extensions import override

from taihe.semantics.attributes import TypedAttribute
from taihe.semantics.declarations import TypeRefDecl
from taihe.semantics.types import StringType
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import AdhocError


class Encoding(Enum):
    UTF8 = "utf-8"
    UTF16 = "utf-16"
    COMMON = "common"


@dataclass
class EncodingAttr(TypedAttribute[TypeRefDecl]):
    NAME = "encoding"
    TARGETS = (TypeRefDecl,)

    value: Encoding

    @override
    def check_typed_context(self, parent: TypeRefDecl, dm: DiagnosticsManager) -> None:
        if not isinstance(parent.resolved_ty, StringType):
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to String types.",
                    loc=self.loc,
                )
            )
        super().check_typed_context(parent, dm)


all_attr_types = [
    EncodingAttr,
]
