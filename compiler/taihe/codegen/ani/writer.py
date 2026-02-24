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

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TextIO

from typing_extensions import override

from taihe.utils.outputs import FileKind, FileWriter, OutputManager

if TYPE_CHECKING:
    from taihe.codegen.ani.analyses import ArkTsModule


class NamingStrategy(ABC):
    """Base class for naming conventions."""

    @abstractmethod
    def as_func(self, name: str) -> str:
        """Convert a name to a function name."""

    @abstractmethod
    def as_field(self, name: str) -> str:
        """Convert a name to a field name."""


class DefaultNamingStrategy(NamingStrategy):
    """Default naming convention that converts names to camelCase."""

    @override
    def as_func(self, name: str) -> str:
        return name[0].lower() + name[1:]

    @override
    def as_field(self, name: str) -> str:
        return name[0].lower() + name[1:]


class UnchangeNamingStrategy(NamingStrategy):
    """Naming convention that keeps the name unchanged."""

    @override
    def as_func(self, name: str) -> str:
        return name

    @override
    def as_field(self, name: str) -> str:
        # TODO: remove all `keep-name` options in tests and fix this
        return name[0].lower() + name[1:]


ETS_DEFAULT_INDENT = "    "
ETS_COMMENT_PREFIX = "// "


class ArkTsImportManager:
    """A mixin class that manages ArkTS import statements."""

    def __init__(self, mod: "ArkTsModule", *, is_static: bool = True):
        self.module = mod
        self.import_dict: dict[str, tuple[str, str | None]] = {}
        self.typealias_dict: dict[str, tuple[str, ...]] = {}
        self.is_static = is_static

    def gen_prologue(self):
        if self.is_static:
            yield '"use static";'
        for import_name, (module_path, member_name) in self.import_dict.items():
            if member_name is None:
                import_str = f"* as {import_name}"
            elif member_name == "default":
                import_str = import_name
            elif member_name == import_name:
                import_str = f"{{{member_name}}}"
            else:
                import_str = f"{{{member_name} as {import_name}}}"
            yield f"import {import_str} from '{module_path}';"
        yield ""

    def gen_epilogue(self):
        yield ""
        for alias, type_path in self.typealias_dict.items():
            type_name = ".".join(type_path)
            yield f"type {alias} = {type_name};"

    def get_type(
        self,
        mod: "ArkTsModule",
        is_default: bool,
        *type_path: str,
    ):
        mangled_mod = "".join(c if c.isalnum() else "_" for c in mod.module_name)
        # Handle types defined in the current module
        if mod.is_same(self.module):
            mangled_type = "_".join(type_path)
            alias = f"_taihe_{mangled_mod}_{mangled_type}"
            self.add_typealias(alias, *type_path)
            return alias
        # Handle types defined in other modules
        type_head, *type_tail = type_path
        import_name = f"_taihe_{mangled_mod}_{type_head}"
        module_path = "/".join([".", *mod.relative_path_to(self.module)])
        if is_default:
            self.add_import_default(import_name, module_path)
        else:
            self.add_import_decl(import_name, module_path, type_head)
        return ".".join([import_name, *type_tail])

    def add_typealias(self, alias_name: str, *type_path: str):
        new_path = type_path
        old_path = self.typealias_dict.setdefault(alias_name, new_path)
        if old_path != new_path:
            raise ValueError(
                f"Duplicate typealias for {alias_name!r}: {old_path} vs {new_path}"
            )

    def add_import_decl(self, import_name: str, module_path: str, member_name: str):
        self._add_import(import_name, module_path, member_name)

    def add_import_default(self, import_name: str, module_path: str):
        self._add_import(import_name, module_path, "default")

    def add_import_module(self, import_name: str, module_path: str):
        self._add_import(import_name, module_path, None)

    def _add_import(self, import_name: str, module_path: str, member_name: str | None):
        new_pair = (module_path, member_name)
        old_pair = self.import_dict.setdefault(import_name, new_pair)
        if old_pair != new_pair:
            raise ValueError(
                f"Duplicate import for {import_name!r}: {old_pair} vs {new_pair}"
            )


class StsWriter(FileWriter, ArkTsImportManager):
    """Represents a static type script (sts) file."""

    def __init__(
        self,
        om: OutputManager,
        mod: "ArkTsModule",
        file_kind: FileKind,
        *,
        is_static: bool = True,
    ):
        super().__init__(
            om,
            relative_path="/".join(mod.relative_path),
            file_kind=file_kind,
            default_indent=ETS_DEFAULT_INDENT,
            comment_prefix=ETS_COMMENT_PREFIX,
        )
        ArkTsImportManager.__init__(self, mod, is_static=is_static)

    @override
    def write_prologue(self, f: TextIO):
        for line in self.gen_prologue():
            f.write(f"{line}\n")

    @override
    def write_epilogue(self, f: TextIO):
        for line in self.gen_epilogue():
            f.write(f"{line}\n")
