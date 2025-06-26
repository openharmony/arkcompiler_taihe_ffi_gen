"""Customizable metadata for declarations.

# Overview

The attribute subsystem provides a type-safe, hierarchical framework for
attaching metadata to declarations. It supports both validation and automatic
type checking through a plugin architecture.

## Architecture

The system follows a hierarchical design:

```
AnyAttribute = UncheckedAttribute | AbstractCheckedAttribute
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
   - `CheckedAttributeManager.attach()` dispatches to appropriate handlers
   - `AbstractCheckedAttribute.can_attach_on()` validates parent declarations
   - `AbstractCheckedAttribute.try_construct()` validates arguments and constructs instances
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from difflib import get_close_matches
from types import NoneType, UnionType
from typing import (
    TYPE_CHECKING,
    ClassVar,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
)

from typing_extensions import Self, override

from taihe.utils.diagnostics import DiagnosticsManager
from taihe.utils.exceptions import (
    AttrArgCountError,
    AttrArgOrderError,
    AttrArgReAssignError,
    AttrArgTypeError,
    AttrArgUndefError,
    AttrMutuallyExclusiveError,
    AttrRepeatError,
    AttrUndefError,
)
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.declarations import Decl

T = TypeVar("T", bound="AbstractCheckedAttribute")


@dataclass
class Argument:
    """Represents a single argument within an attribute invocation.

    Attributes store both the source location (for error reporting) and the
    evaluated value of each argument.
    """

    loc: SourceLocation | None
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

    key: str
    value: float | bool | int | str
    """The evaluated constant value of the argument."""


@dataclass
class UncheckedAttribute:
    """Raw attribute data before type checking and validation.

    This represents the syntactic form of an attribute as parsed from source code,
    before any semantic analysis or type checking has been performed.
    """

    name: str
    """The attribute name as it appears in source code (without @ prefix)."""

    loc: SourceLocation | None
    """Source location of the attribute name for error reporting."""

    args: Sequence[Argument]
    """Positional arguments passed to the attribute."""

    @staticmethod
    def get(decl: "Decl", name: str | None = None) -> Iterable["UncheckedAttribute"]:
        attrs = decl.attributes.get(UncheckedAttribute, [])
        attrs = cast("list[UncheckedAttribute]", attrs)
        if name:
            return filter(lambda a: a.name == name, attrs)
        else:
            return attrs

    @staticmethod
    def contains(decl: "Decl", name: str) -> bool:
        return any(True for _ in UncheckedAttribute.get(decl, name))


class AbstractCheckedAttribute(ABC):
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

    TARGETS: ClassVar[frozenset[type["Decl"]]] = frozenset()
    """Set of declaration types this attribute can be attached to.

    The system uses isinstance() checking, so inheritance hierarchies
    are properly supported.
    """

    loc: SourceLocation | None
    """Source location of the attribute name for error reporting."""

    NAME: ClassVar[str]
    """Explicit attribute name."""

    @classmethod
    @abstractmethod
    def register_to(cls, registry: "CheckedAttributeManager") -> None:
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
        perant: "Decl",
        raw: UncheckedAttribute,
        dm: DiagnosticsManager,
    ) -> Self | None:
        """Attempts to construct a validated attribute from raw data.

        This method performs argument validation and type checking. On success,
        it returns a fully constructed attribute instance. On failure, it emits
        diagnostic messages and returns None.

        Args:
            perant: attribute node perant node
            raw: The unchecked attribute data from parsing
            dm: Diagnostics manager for error reporting

        Returns:
            Validated attribute instance on success, None on failure

        Note:
            This method must not raise exceptions. All errors should be reported
            through the diagnostics manager.
        """


class AutoCheckedAttribute(AbstractCheckedAttribute):
    """Base class providing automatic name inference and target checking.

    This class implements common patterns for attribute registration and
    target validation, reducing boilerplate in concrete attribute implementations.
    """

    MUTUALLY_EXCLUSIVE: ClassVar[frozenset[type["AutoCheckedAttribute"]]] = frozenset()
    """Set of attribute types that are mutually exclusive with this one.

    If a declaration already has any attribute in this set, attaching this
    attribute will result in a conflict.

    This mechanism allows attribute authors to prevent logically conflicting
    annotations from being used together on the same declaration.
    """

    @override
    @classmethod
    def register_to(cls, registry: "CheckedAttributeManager") -> None:
        """Registers using the inferred or explicit attribute name."""
        registry.register_one(cls.NAME, cls)

    @override
    @classmethod
    def try_construct(
        cls,
        perant: "Decl",
        raw: UncheckedAttribute,
        dm: DiagnosticsManager,
    ) -> Self | None:
        """Attempts to construct a validated attribute from raw data.

        This method performs argument validation and type checking. On success,
        it returns a fully constructed attribute instance. On failure, it emits
        diagnostic messages and returns None.

        Args:
            perant: attribute node perant node
            raw: The unchecked attribute data from parsing
            dm: Diagnostics manager for error reporting

        Returns:
            Validated attribute instance on success, None on failure

        Note:
            This method must not raise exceptions. All errors should be reported
            through the diagnostics manager.
        """
        if not cls._check_mutual_exclusivity(perant, raw, dm):
            return None

        pos_args, kw_args, arg_error = cls._split_and_validate_args(raw, dm)
        if arg_error:
            return None

        # Split arguments into required and optional
        type_hints = cls._get_own_instance_fields()
        required_args, optional_args = cls._categorize_args(type_hints)

        if not cls._validate_argument_count(
            raw, len(required_args), len(optional_args), dm
        ):
            return None

        inst = cls.__new__(cls)
        inst.loc = raw.loc

        # Check parameter order, type, and parameter assignment
        if not cls._process_args(
            inst,
            pos_args,
            kw_args,
            required_args,
            optional_args,
            type_hints,
            raw.name,
            dm,
        ):
            return None

        return inst

    @classmethod
    def _check_mutual_exclusivity(
        cls,
        perant: "Decl",
        raw: UncheckedAttribute,
        dm: DiagnosticsManager,
    ) -> bool:
        """Check for mutually exclusive attribute conflicts on the same declaration.

        This method verifies that the current attribute does not conflict with
        any attributes already attached to the target declaration, based on the
        `MUTUALLY_EXCLUSIVE` set.

        Args:
            perant: The declaration the attribute is being applied to.
            raw: The raw attribute instance from parsing.
            dm: Diagnostics manager for error reporting.

        Returns:
            True if no mutually exclusive attributes are found; False otherwise.
        """
        if cls.MUTUALLY_EXCLUSIVE:
            for attr_type, _ in perant.attributes.items():
                if attr_type in cls.MUTUALLY_EXCLUSIVE and issubclass(
                    attr_type, AutoCheckedAttribute
                ):
                    dm.emit(AttrMutuallyExclusiveError(raw, attr_type))
                    return False
        return True

    @classmethod
    def _split_and_validate_args(
        cls,
        raw: UncheckedAttribute,
        dm: DiagnosticsManager,
    ) -> tuple[list[Argument], list[Argument], bool]:
        """Split raw arguments into positional and keyword, and validate ordering.

        Positional arguments must appear before any keyword arguments.
        Mixing positional and keyword arguments with incorrect order results in diagnostics.

        Args:
            raw: The raw unchecked attribute containing argument list.
            dm: Diagnostics manager for reporting invalid order.

        Returns:
            A tuple of:
            - List of positional arguments
            - List of keyword arguments
            - A boolean indicating if any ordering errors were found
        """
        pos_args: list[Argument] = []
        kw_args: list[Argument] = []
        seen_keyword = False
        error = False

        for arg in raw.args:
            if arg.key == "":
                if seen_keyword:
                    dm.emit(AttrArgOrderError(arg))
                    error = True
                pos_args.append(arg)
            else:
                seen_keyword = True
                kw_args.append(arg)

        return pos_args, kw_args, error

    @classmethod
    def _categorize_args(
        cls, type_hints: dict[str, type]
    ) -> tuple[list[str], list[str]]:
        """Categorize attribute fields into required and optional.

        Based on the type hints declared on the attribute class,
        arguments are split into:
        - Required: no default, not Optional
        - Optional: declared as Optional[T] or T | None or Union[T, None]

        Returns:
            A tuple of:
            - List of required field names
            - List of optional field names
        """
        required_args: list[str] = []
        optional_args: list[str] = []

        for name, hint in type_hints.items():
            origin = get_origin(hint)
            args = get_args(hint)
            if origin in (Union, UnionType) and type(None) in args:
                # this arg's type is Optional[T] or T | None or Union[T, None]
                optional_args.append(name)
            else:
                required_args.append(name)

        return required_args, optional_args

    @classmethod
    def _validate_argument_count(
        cls,
        raw: UncheckedAttribute,
        required_count: int,
        optional_count: int,
        dm: DiagnosticsManager,
    ) -> bool:
        """Validate that the number of arguments matches the expected count.

        Rules:
        - The number of arguments must be at least the number of required fields.
        - The number of arguments must not exceed the total of required + optional fields.

        Violating these rules triggers a diagnostic error indicating
        the expected and actual argument counts.

        Returns:
            True if the argument count is valid; False otherwise.
        """
        if (
            len(raw.args) > (required_count + optional_count)
            or len(raw.args) < required_count
        ):
            dm.emit(
                AttrArgCountError(
                    raw.loc,
                    raw.name,
                    required_count,
                    optional_count,
                    len(raw.args),
                )
            )
            return False
        return True

    @classmethod
    def _process_args(
        cls,
        inst: Self,
        pos_args: list[Argument],
        kw_args: list[Argument],
        required_args: list[str],
        optional_args: list[str],
        type_hints: dict[str, type],
        attr_name: str,
        dm: DiagnosticsManager,
    ) -> bool:
        """Process and validate arguments.

        Rules:
        - Positional arguments are matched in order to required and optional fields.
        - Keyword arguments must refer to a known field and cannot duplicate positional ones.
        - All argument types must match the declared type hints.
        - Duplicate or undefined argument names result in diagnostics.

        Returns:
            True if all arguments are valid and successfully assigned;
            False if any validation fails (with diagnostics emitted).
        """
        seen_names: set[str] = set()

        for i, arg in enumerate(pos_args):
            field = (
                required_args[i]
                if i < len(required_args)
                else optional_args[i - len(required_args)]
            )
            seen_names.add(field)
            if not cls._validate_and_set_argument(
                inst, arg, field, type_hints[field], attr_name, dm
            ):
                return False

        for arg in kw_args:
            key = arg.key
            if key not in required_args and key not in optional_args:
                dm.emit(AttrArgUndefError(arg))
                return False
            if key in seen_names:
                dm.emit(AttrArgReAssignError(arg))
                return False
            if not cls._validate_and_set_argument(
                inst, arg, key, type_hints[key], attr_name, dm
            ):
                return False
            seen_names.add(key)

        return True

    @classmethod
    def _validate_and_set_argument(
        cls,
        inst: Self,
        arg: Argument,
        field: str,
        expected_type: type,
        attr_name: str,
        dm: DiagnosticsManager,
    ) -> bool:
        if not isinstance(arg.value, expected_type):
            dm.emit(
                AttrArgTypeError(
                    arg.loc,
                    attr_name,
                    cls._format_type(expected_type),
                    type(arg.value).__name__,
                )
            )
            return False

        setattr(inst, field, arg.value)
        return True

    @classmethod
    def _is_positional_then_keyword(cls, args: Sequence[Argument]) -> Argument | None:
        """Determine the order of args.

        Support mixed use of args and kwargs, but args must come before kwargs
        args.keys: ["", "", ""]  # OK
        args.keys: ["key1", "key2"] # OK
        args.keys: ["", "key1", ""] # ERROR

        Returns:
            The `loc` of the first positional argument that appears after
        a keyword argument. If all good, return None.
        """
        seen_keyword = False
        for arg in args:
            if arg.key == "":
                if seen_keyword:
                    return arg
            else:
                seen_keyword = True
        return None

    @classmethod
    def _get_own_instance_fields(cls) -> dict[str, type]:
        """Retrieve instance-level annotated fields defined in the current class.

        This method returns a dictionary mapping field names to their type annotations
        for all attributes defined in the current class (i.e., not inherited from a base class).
        It excludes fields annotated as `ClassVar`, as those are considered class-level variables
        and not instance-specific.

        Returns:
            dict[str, type]: A dictionary where keys are attribute names and values are their
            corresponding type annotations, excluding `ClassVar` types.

        Note:
            This method assumes that `cls.__annotations__` only includes fields declared in the
            current class and not inherited ones. If inheritance filtering is needed, additional
            logic is required.
        """
        result: dict[str, type] = {}
        for name, hint in cls.__annotations__.items():
            if get_origin(hint) is not ClassVar:
                result[name] = hint
        return result

    @classmethod
    def _format_type(cls, tp: type) -> str:
        """Format type for error messages."""
        origin = get_origin(tp)
        args = get_args(tp)
        if origin is UnionType or origin is Union:
            return " | ".join(cls._format_type(a) for a in args if a is not NoneType)
        return tp.__name__


class TypedAttribute(AutoCheckedAttribute):
    """Type-checked attribute that can be attached at most once per declaration."""

    @classmethod
    def _is_unique_attachment(cls, parent: "Decl") -> bool:
        """Checks if this would be the first attachment of this attribute type."""
        existing_attrs = parent.attributes.get(cls, [])
        return len(existing_attrs) == 0

    @classmethod
    def get(cls: type[T], decl: "Decl") -> T | None:
        """Retrieves the single instance of this attribute from a declaration.

        Args:
            decl: The declaration to search

        Returns:
            The attribute instance if present, None otherwise
        """
        if attrs := decl.attributes.get(cls):
            return cast("T", attrs[0])
        return None

    @override
    @classmethod
    def try_construct(
        cls, perant: "Decl", raw: UncheckedAttribute, dm: DiagnosticsManager
    ) -> Self | None:
        if not cls._is_unique_attachment(perant):
            dm.emit(AttrRepeatError(raw))
            return None
        return super().try_construct(perant, raw, dm)


class RepeatableAttribute(AutoCheckedAttribute):
    """Type-checked attribute that can be attached multiple times per declaration."""

    @classmethod
    def get(cls: type[T], decl: "Decl") -> list[T]:
        """Retrieves all instances of this attribute from a declaration.

        Args:
            decl: The declaration to search

        Returns:
            List of attribute instances (empty if none present)
        """
        attrs = decl.attributes.get(cls, [])
        return cast("list[T]", attrs)


# Type aliases for clarity
CheckedAttrT = type[AbstractCheckedAttribute]
AnyAttribute = AbstractCheckedAttribute | UncheckedAttribute


class CheckedAttributeManager:
    """Registry for mapping attribute names to their implementation classes.

    This registry serves as the central dispatch mechanism during IR construction,
    allowing the system to convert unchecked attributes to their typed equivalents.
    """

    def __init__(self) -> None:
        self._name_to_attr: dict[str, CheckedAttrT] = {}

    def register_one(self, name: str, attr_type: CheckedAttrT) -> None:
        """Registers a single attribute type with the given name.

        Args:
            name: The attribute name (without @ prefix)
            attr_type: The attribute implementation class

        Raises:
            ValueError: If an attribute with this name is already registered
        """
        if name in self._name_to_attr:
            existing = self._name_to_attr[name]
            raise ValueError(
                f"Attribute '{name}' already registered to {existing.__qualname__}, "
                f"cannot register {attr_type.__qualname__}"
            )
        self._name_to_attr[name] = attr_type

    def register(self, *attr_types: CheckedAttrT) -> None:
        """Registers multiple attribute types using their inferred names.

        Args:
            *attr_types: Attribute classes to register

        This is a convenience method that calls register_to() on each class.
        """
        for attr_type in attr_types:
            attr_type.register_to(self)

    def attach(
        self, raw: UncheckedAttribute, decl: "Decl", dm: DiagnosticsManager
    ) -> AbstractCheckedAttribute | None:
        """Validates and attaches an unchecked attribute to a declaration.

        This method orchestrates the entire attachment process:
        1. Looks up the attribute type by name
        2. Validates attachment eligibility
        3. Constructs the typed attribute instance
        4. Adds it to the declaration's attribute collection

        Args:
            raw: Unchecked attribute data from parsing
            decl: Target declaration for attachment
            dm: Diagnostics manager for error reporting

        Returns:
            The constructed attribute instance on success, None on failure

        Raises:
            AdhocError: If the attribute name is not registered
        """
        # Look up the attribute type - this is the only case where we raise
        # an exception, as unknown attributes indicate a configuration error
        attr_type = self._name_to_attr.get(raw.name)
        if attr_type is None:
            suggestions = get_close_matches(raw.name, self._name_to_attr.keys())
            new_suggestons: list[str] = []
            for suggestion in suggestions:
                sugg_attr_type = self._name_to_attr.get(suggestion)
                if (
                    sugg_attr_type
                    and sugg_attr_type.TARGETS
                    and not any(isinstance(decl, t) for t in sugg_attr_type.TARGETS)
                ):
                    continue
                else:
                    new_suggestons.append(suggestion)
            dm.emit(AttrUndefError(raw.loc, raw.name, new_suggestons))
            return None

        # check attrbute conflict
        elif attr_type.TARGETS and not any(
            isinstance(decl, t) for t in attr_type.TARGETS
        ):
            dm.emit(AttrUndefError(raw.loc, raw.name, []))

        # Attempt to construct the typed attribute
        if checked_attr := attr_type.try_construct(decl, raw, dm):
            # Add to the declaration's attribute collection
            checked_attr.loc = raw.loc
            decl.add_attribute(checked_attr)
            return checked_attr

        return None
