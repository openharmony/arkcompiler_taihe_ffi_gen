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
from typing import TYPE_CHECKING

from typing_extensions import override

if TYPE_CHECKING:
    from taihe.utils.diagnostics import DiagnosticsManager

from taihe.semantics.attributes import (
    TypedAttribute,
)
from taihe.semantics.declarations import (
    CallbackTypeRefDecl,
    GlobFuncDecl,
    IfaceMethodDecl,
    TypeRefDecl,
)
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import AdhocError


@dataclass
class NoexceptAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl | TypeRefDecl]):
    NAME = "noexcept"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl, TypeRefDecl)

    @override
    def check_typed_context(
        self,
        parent: GlobFuncDecl | IfaceMethodDecl | TypeRefDecl,
        dm: DiagnosticsManager,
    ) -> None:
        if isinstance(parent, TypeRefDecl) and not isinstance(
            parent, CallbackTypeRefDecl
        ):
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to fields with callback type not {type(parent)}.",
                    loc=self.loc,
                )
            )

        super().check_typed_context(parent, dm)


all_attr_types = [
    NoexceptAttr,
]
