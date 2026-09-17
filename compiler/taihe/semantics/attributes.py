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

"""Customizable metadata for declarations.

# Overview

The attribute subsystem provides a type-safe, hierarchical framework for
attaching metadata to declarations. It supports both validation and automatic
type checking through a plugin architecture.

## Architecture

The system follows a hierarchical design:

```
AnyAttribute
├── UncheckedAttribute: Raw attributes without validation
└── AbstractCheckedAttribute: Base class for validated attributes
    └── AutoCheckedAttribute: Automatic checking via configuration
        ├── TypedAttribute: Single-use attributes with type checking
        └── RepeatableAttribute: Multi-use attributes with type checking
```

## Lifecycle

1. **Backend Initialization**: Backends register attributes using
   `AbstractCheckedAttribute.register_to(registry)`
2. **IR Construction**: The IR converter processes unchecked attributes:
   - `AttributeRegistry.try_resolve()` dispatches to appropriate handlers
   - `AbstractCheckedAttribute.try_construct()` validates arguments and constructs instances
"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import MISSING, Field, dataclass, fields
from dataclasses import field as datafield
from difflib import get_close_matches
from enum import Enum
from itertools import chain
from types import UnionType
from typing import Any, ClassVar, Generic, Literal, TypeVar, Union, get_args, get_origin

from typing_extensions import Self, override

from taihe.semantics.declarations import Decl
from taihe.semantics.format import TaiheFormatter
from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import (
    AttrArgMissingError,
    AttrArgOrderError,
    AttrArgRedefError,
    AttrArgTypeError,
    AttrArgUnrequiredError,
    AttrConflictError,
    AttrNotExistError,
    AttrTargetError,
)
from taihe.utils.sources import SourceLocation

RawValueType = float | bool | int | str


@dataclass
class Argument:
    """Represents a single argument within an attribute invocation.

    Attributes store both the source location (for error reporting) and the
    evaluated value of each argument.
    """

    loc: SourceLocation | None = datafield(kw_only=True)
    """Source location of this argument for error reporting.

    For positional arguments, this covers the entire argument expression.
    For keyword arguments, this covers both the key and value.

    Example:
    ```
    # For positional arguments
    @foo(2 + 3)
         ^^^^^

    # For keyword arguments (in the future?)
    @foo(bar="baz")
         ^^^^^^^^^
    ```
    """

    key: str | None
    """The name of the argument if it is a keyword argument, or None for positional arguments."""

    value: RawValueType
    """The evaluated constant value of the argument."""


@dataclass
class AnyAttribute(ABC):
    """Base class for all attributes, both checked and unchecked.

    This serves as a common interface for both raw attributes (UncheckedAttribute)
    and validated attributes (AbstractCheckedAttribute). It provides a unified
    way to retrieve the name and arguments of an attribute for diagnostics.
    """

    loc: SourceLocation | None = datafield(kw_only=True)
    """Source location of the attribute name for error reporting."""

    @property
    def description(self) -> str:
        """Provides a human-readable description of the attribute.

        This can be overridden by subclasses to provide more context.
        """
        return f"attribute {TaiheFormatter().get_format_attr(self)}"

    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the attribute without the '@' prefix.

        This is used for diagnostics and debugging purposes.
        """

    @abstractmethod
    def get_args(self) -> Iterable[Argument]:
        """Returns the list of arguments passed to this attribute.

        This is used for diagnostics and debugging purposes.
        """

    @abstractmethod
    def check_context(self, parent: Decl, dm: DiagnosticsManager) -> None:
        """Checks if this attribute can be attached to the given declaration.

        This method should be implemented by subclasses to enforce specific
        attachment rules. It should not raise exceptions, but instead use
        the diagnostics manager to report any issues.

        Args:
            parent: The declaration to check against
            dm: Diagnostics manager for error reporting
        """


@dataclass
class UncheckedAttribute(AnyAttribute):
    """Raw attribute data before type checking and validation.

    This represents the syntactic form of an attribute as parsed from source code,
    before any semantic analysis or type checking has been performed.
    """

    name: str
    """The attribute name as it appears in source code (without @ prefix)."""

    args: list[Argument]
    """Positional arguments passed to the attribute."""

    @classmethod
    def consume(cls, decl: Decl) -> Iterable[Self]:
        """Yields all unchecked attributes from a declaration.

        This method iterates through the declaration's attributes and yields
        each unchecked attribute of the specified class, removing it from the
        declaration's attribute list.
        """
        unchecked_attrs = decl.find_attributes(cls)
        while unchecked_attrs:
            yield unchecked_attrs.pop(0)

    @override
    def get_name(self) -> str:
        return self.name

    @override
    def get_args(self) -> Iterable[Argument]:
        return self.args

    @override
    def check_context(self, parent: Decl, dm: DiagnosticsManager) -> None:
        pass


class AbstractCheckedAttribute(AnyAttribute, ABC):
    """Base class for validated attributes with pluggable checking logic.

    This provides the low-level framework for implementing custom attributes.
    Most backend developers should use `TypedAttribute` or `RepeatableAttribute`
    instead, which provide automatic type checking.

    ## Inheritance Constraints

    While you can subclass, registering or querying the base class is not
    supported. For example:
    ```
    class Base(CheckedAttribute)
    class DerivedA(Base)
    class DerivedB(Base)

    Base.register_to(registry)      # Error
    DerivedA.register_to(registry)  # OK
    DerivedB.register_to(registry)  # OK
    Base.get(d)                     # Error
    DerivedA.get(d)                 # OK
    DerivedB.get(d)                 # OK
    ```
    """

    @classmethod
    @abstractmethod
    def register_to(cls, registry: "AttributeRegistry") -> None:
        """Registers this attribute type with the given registry.

        Args:
            registry: The registry to register with

        This method defines how the attribute should be looked up during
        the attachment phase.
        """

    @classmethod
    @abstractmethod
    def try_construct(
        cls,
        raw: UncheckedAttribute,
        dm: DiagnosticsManager,
    ) -> Self | None:
        """Process the validated arguments and construct the attribute instance.

        This method should be implemented by subclasses to handle specific
        argument processing logic.

        Args:
            raw: The unchecked attribute data from parsing
            dm: Diagnostics manager for error reporting

        Returns:
            An instance of the attribute on success, None on failure
        """


@dataclass(frozen=True)
class ConversionFailure:
    message: str
    children: tuple["ConversionFailure", ...] = ()


class CustomConvertible(ABC):
    @classmethod
    @abstractmethod
    def from_value(cls, value: RawValueType) -> Self | ConversionFailure: ...

    @abstractmethod
    def to_value(self) -> RawValueType: ...


_FromValue = Callable[[RawValueType], Any | ConversionFailure]
_FieldInfo = tuple[Field[Any], _FromValue]


def _from_value_from_hint(hint: Any) -> _FromValue:
    if isinstance(hint, type):
        if issubclass(hint, CustomConvertible):
            return hint.from_value

        if issubclass(hint, Enum):
            args = [member.value for member in hint]
            if not args:
                raise TypeError(f"Enum {hint.__name__} has no members")
            if any(not isinstance(arg, RawValueType) for arg in args):
                raise TypeError(f"Enum {hint.__name__} has non-primitive values")

            def enum_from_value(
                value: RawValueType,
            ) -> Enum | ConversionFailure:
                if any(type(value) is type(arg) and value == arg for arg in args):
                    return hint(value)
                members = ", ".join(map(repr, args))
                return ConversionFailure(
                    message=f"Value is not compatible with any valid member of enum {hint.__name__}: {members}",
                )

            return enum_from_value

        if hint in (bool, int, str, float):

            def value_from_value(
                value: RawValueType,
            ) -> RawValueType | ConversionFailure:
                # Do not use isinstance here because bool is subclass of int
                if type(value) is hint:
                    return value
                return ConversionFailure(
                    message=f"Value is not of type {hint.__name__}",
                )

            return value_from_value

    if origin := get_origin(hint):
        args = get_args(hint)

        if origin is Union or origin is UnionType:
            args = [arg for arg in args if arg is not type(None)]
            if not args:
                raise TypeError(f"Union type {hint} has no valid types")
            from_values = [_from_value_from_hint(arg) for arg in args]
            if len(args) == 1:
                return from_values[0]

            def union_from_value(
                value: RawValueType,
            ) -> Any | ConversionFailure:
                children: list[ConversionFailure] = []
                for from_value in from_values:
                    result = from_value(value)
                    if not isinstance(result, ConversionFailure):
                        return result
                    children.append(result)
                return ConversionFailure(
                    message="Value is not compatible with any type in Union",
                    children=tuple(children),
                )

            return union_from_value

        if origin is Literal:
            args = [arg for arg in args if arg is not None]
            if not args:
                raise TypeError(f"Literal type {hint} has no valid values")
            if any(not isinstance(arg, RawValueType) for arg in args):
                raise TypeError(f"Literal type {hint} has non-primitive values")

            def literal_from_value(
                value: RawValueType,
            ) -> Any | ConversionFailure:
                if any(type(value) is type(arg) and value == arg for arg in args):
                    return value
                members = ", ".join(map(repr, args))
                return ConversionFailure(
                    message=f"Value is not one of the allowed literals: {members}",
                )

            return literal_from_value

    raise TypeError(f"Unsupported type hint: {hint}")


def _to_value(attr: Any) -> RawValueType | None:
    if attr is None:
        return None
    if isinstance(attr, CustomConvertible):
        return attr.to_value()
    if isinstance(attr, Enum):
        value = attr.value
    else:
        value = attr
    if type(value) in (float, bool, int, str):
        return value
    raise TypeError(f"Unsupported attribute value type: {type(attr).__name__}")


class AttributeGroupTag:
    pass


_D = TypeVar("_D", bound=Decl)


class AutoCheckedAttribute(AbstractCheckedAttribute, Generic[_D]):
    """Base class providing automatic name inference and target checking.

    This class implements common patterns for attribute registration and
    target validation, reducing boilerplate in concrete attribute implementations.
    """

    NAME: ClassVar[str]
    """Explicit attribute name."""

    TARGETS: ClassVar[tuple[type[_D], ...]]  # type: ignore
    """Declaration types this attribute can be attached to.

    The system uses isinstance() checking, so inheritance hierarchies are properly
    supported.

    Use `(Decl,)` to indicate the attribute can be attached to any declaration.
    """

    ATTRIBUTE_GROUP_TAGS: ClassVar[frozenset[AttributeGroupTag]] = frozenset()
    """Set of tags indicating mutually exclusive attribute groups.

    If this is non-empty, the attribute cannot coexist with any other
    attribute that has any of these tags.
    """

    @override
    @classmethod
    def register_to(cls, registry: "AttributeRegistry") -> None:
        registry.register_one(cls.NAME, cls)

    @override
    @classmethod
    def try_construct(
        cls,
        raw: UncheckedAttribute,
        dm: DiagnosticsManager,
    ) -> Self | None:
        args: list[Argument] = []
        kwargs: dict[str, Argument] = {}

        for arg in raw.args:
            if arg.key is None:
                if kwargs:
                    dm.emit(AttrArgOrderError(arg))
                    return None
                args.append(arg)
            else:
                if (prev := kwargs.get(arg.key)) is not None:
                    dm.emit(AttrArgRedefError(prev, arg))
                    return None
                kwargs[arg.key] = arg

        return cls.try_construct_from_parsed_args(args, kwargs, dm, loc=raw.loc)

    @classmethod
    def try_construct_from_parsed_args(
        cls,
        args: list[Argument],
        kwargs: dict[str, Argument],
        dm: DiagnosticsManager,
        *,
        loc: SourceLocation | None,
    ) -> Self | None:
        """Constructs the attribute instance from parsed arguments.

        This method processes the positional and keyword arguments, validates
        them against the dataclass fields, and constructs the attribute instance.

        Args:
            loc: Source location of the attribute for error reporting
            name: The name of the attribute (without @ prefix)
            args: Positional arguments passed to the attribute
            kwargs: Keyword arguments passed to the attribute
            dm: Diagnostics manager for error reporting

        Returns:
            An instance of the attribute on success, None on failure
        """
        args_fields: list[_FieldInfo] = []
        kwargs_fields: dict[str, _FieldInfo] = {}
        for field in fields(cls):
            if field.name == "loc" or not field.init:
                continue
            from_value = _from_value_from_hint(field.type)
            field_info = field, from_value
            if field.kw_only is True:
                kwargs_fields[field.name] = field_info
            else:
                args_fields.append(field_info)

        dataclass_args: list[Any] = []
        for arg in args:
            if not args_fields:
                dm.emit(AttrArgUnrequiredError(cls.NAME, arg))
                return None
            field, from_value = args_fields.pop(0)
            attr = from_value(arg.value)
            if isinstance(attr, ConversionFailure):
                dm.emit(AttrArgTypeError(cls.NAME, field.name, arg, attr))
                return None
            dataclass_args.append(attr)

        for field_info in args_fields:
            kwargs_fields[field_info[0].name] = field_info

        dataclass_kwargs: dict[str, Any] = {}
        for name, arg in kwargs.items():
            if name not in kwargs_fields:
                dm.emit(AttrArgUnrequiredError(cls.NAME, arg))
                return None
            field, from_value = kwargs_fields.pop(name)
            attr = from_value(arg.value)
            if isinstance(attr, ConversionFailure):
                dm.emit(AttrArgTypeError(cls.NAME, field.name, arg, attr))
                return None
            dataclass_kwargs[field.name] = attr

        has_missing = False
        for field, _ in kwargs_fields.values():
            if field.default is MISSING and field.default_factory is MISSING:
                dm.emit(AttrArgMissingError(cls.NAME, field.name, loc=loc))
                has_missing = True
        if has_missing:
            return None

        return cls(*dataclass_args, **dataclass_kwargs, loc=loc)

    @override
    def check_context(self, parent: Decl, dm: DiagnosticsManager) -> None:
        if not isinstance(parent, self.TARGETS):
            dm.emit(AttrTargetError(parent, self))
            return

        self.check_typed_context(parent, dm)

    def check_typed_context(self, parent: _D, dm: DiagnosticsManager) -> None:
        """Checks if this attribute can be attached to the given declaration.

        Notice that parent type is already checked outside.

        Args:
            parent: The declaration to check against
            dm: Diagnostics manager for error reporting

        Returns:
            True if the attribute can be attached, False otherwise
        """
        for prev in chain(*parent.attributes.values()):
            if type(prev) is type(self):
                continue
            if not isinstance(prev, AutoCheckedAttribute):
                continue
            if self.ATTRIBUTE_GROUP_TAGS & prev.ATTRIBUTE_GROUP_TAGS:
                dm.emit(AttrConflictError(prev, self))  # type: ignore

    @override
    def get_name(self) -> str:
        return self.NAME

    @override
    def get_args(self) -> Iterable[Argument]:
        args: list[tuple[str, float | int | str | bool]] = []
        kwargs: list[tuple[str, float | int | str | bool]] = []
        dfargs: list[tuple[str, float | int | str | bool]] = []
        has_skipped_default_value = False
        for field in fields(self):
            if field.name == "loc" or not field.init:
                continue
            attr = getattr(self, field.name, None)
            value = _to_value(attr)
            if value is None:
                has_skipped_default_value = True
                continue
            pair = field.name, value
            if field.kw_only is True:
                kwargs.append(pair)
            elif field.default is MISSING and field.default_factory is MISSING:
                args.append(pair)
            else:
                dfargs.append(pair)
        if has_skipped_default_value:
            kwargs.extend(dfargs)
        else:
            args.extend(dfargs)
        for _, value in args:
            yield Argument(None, value, loc=None)
        for name, value in kwargs:
            yield Argument(name, value, loc=None)


class TypedAttribute(AutoCheckedAttribute[_D]):
    """Type-checked attribute that can be attached at most once per declaration."""

    @classmethod
    def get(cls, decl: _D) -> Self | None:
        """Retrieves the single instance of this attribute from a declaration.

        Args:
            decl: The declaration to search

        Returns:
            The attribute instance if present, None otherwise
        """
        if attrs := decl.find_attributes(cls):
            return attrs[0]
        return None

    @override
    def check_typed_context(self, parent: _D, dm: DiagnosticsManager) -> None:
        prev = self.get(parent)
        if prev is not None and prev is not self:
            dm.emit(AttrConflictError(prev, self))

        super().check_typed_context(parent, dm)


class RepeatableAttribute(AutoCheckedAttribute[_D]):
    """Type-checked attribute that can be attached multiple times per declaration."""

    @classmethod
    def get_all(cls, decl: _D) -> list[Self]:
        """Retrieves all instances of this attribute from a declaration.

        Args:
            decl: The declaration to search

        Returns:
            List of attribute instances (empty if none present)
        """
        return decl.find_attributes(cls)


# Type aliases for clarity
CheckedAttrT = type[AbstractCheckedAttribute]


class AttributeRegistry:
    """Registry for mapping attribute names to their implementation classes.

    This registry serves as the central dispatch mechanism during IR construction,
    allowing the system to convert unchecked attributes to their typed equivalents.
    """

    def __init__(self) -> None:
        self._name_to_attr_type: dict[str, CheckedAttrT] = {}

    def register_one(self, name: str, attr_type: CheckedAttrT) -> None:
        """Registers a single attribute type with the given name.

        Args:
            name: The attribute name (without @ prefix)
            attr_type: The attribute implementation class

        Raises:
            ValueError: If an attribute with this name is already registered
        """
        setted_attr_type = self._name_to_attr_type.setdefault(name, attr_type)
        if setted_attr_type is not attr_type:
            raise ValueError(
                f"Attribute '{name}' already registered to {setted_attr_type.__qualname__}, "
                f"cannot register {attr_type.__qualname__}"
            )

    def register(self, *attr_types: CheckedAttrT) -> None:
        """Registers multiple attribute types using their inferred names.

        Args:
            *attr_types: Attribute classes to register

        This is a convenience method that calls register_to() on each class.
        """
        for attr_type in attr_types:
            attr_type.register_to(self)

    def try_resolve(
        self,
        raw: UncheckedAttribute,
        dm: DiagnosticsManager,
    ) -> AbstractCheckedAttribute | None:
        """Validates and constructs a typed attribute from unchecked attribute data.

        This method orchestrates the entire attachment process:
        1. Looks up the attribute type by name
        2. Constructs the typed attribute instance

        Args:
            raw: Unchecked attribute data from parsing
            dm: Diagnostics manager for error reporting
        """
        attr_type = self._name_to_attr_type.get(raw.name)
        if attr_type is None:
            suggestions = get_close_matches(raw.name, self._name_to_attr_type.keys())
            dm.emit(AttrNotExistError(raw.name, suggestions, loc=raw.loc))
            return None

        return attr_type.try_construct(raw, dm)
