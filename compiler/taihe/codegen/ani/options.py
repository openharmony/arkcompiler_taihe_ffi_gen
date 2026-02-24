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

from typing_extensions import Self

from taihe.driver.options import AbstractConfigOption


@dataclass
class ArktsKeepNameOption(AbstractConfigOption):
    """Keep original function names in generated ArkTS code.

    When enabled, function names in the generated ArkTS code will match
    the names in the Taihe IDL file exactly, instead of being converted
    to camelCase.

    Usage: -Carkts:keep-name
    """

    NAME = "arkts:keep-name"

    @classmethod
    def parse(cls, value: str | None) -> Self:
        return cls()


@dataclass
class ArktsModulePrefixOption(AbstractConfigOption):
    """Specify the module name for generated ArkTS code.

    This affects the ANI signatures of generated symbols. DevEco users
    must specify this option.

    Usage: -Carkts:module-prefix=com.example
    """

    NAME = "arkts:module-prefix"

    prefix: str | None = None

    @classmethod
    def parse(cls, value: str | None) -> Self:
        return cls(prefix=value)


@dataclass
class ArktsPathPrefixOption(AbstractConfigOption):
    """Specify the path prefix for generated ArkTS code.

    This affects the ANI signatures of generated symbols. DevEco users
    must specify this option.

    Usage: -Carkts:path-prefix=src/arkts
    """

    NAME = "arkts:path-prefix"

    prefix: str | None = None

    @classmethod
    def parse(cls, value: str | None) -> Self:
        return cls(prefix=value)


# All ANI config options for easy registration
all_ani_config_options = [
    ArktsKeepNameOption,
    ArktsModulePrefixOption,
    ArktsPathPrefixOption,
]
