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

from taihe.driver.options import AbstractConfigOption

if TYPE_CHECKING:
    from taihe.utils.diagnostics import DiagnosticsManager


@dataclass
class NoexceptAllOption(AbstractConfigOption):
    """Apply @noexcept to all functions, methods, and callbacks.

    When enabled, all global functions, interface methods, and callback types
    will be treated as if they have the @noexcept attribute.

    Usage: -Cnoexcept-all
    """

    NAME = "noexcept-all"

    @classmethod
    def try_parse(cls, value: str | None, dm: "DiagnosticsManager"):
        return cls()


all_abi_config_options = [
    NoexceptAllOption,
]
