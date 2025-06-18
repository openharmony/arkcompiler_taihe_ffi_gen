from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from typing_extensions import override

from taihe.utils.diagnostics import DiagError, DiagFatalError, DiagNote, DiagWarn
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.declarations import (
        EnumDecl,
        EnumItemDecl,
        IfaceDecl,
        NamedDecl,
        PackageDecl,
        PackageLevelDecl,
        Type,
        TypeDecl,
        TypeRefDecl,
    )


@dataclass
class DeclRedefNote(DiagNote):
    prev: "NamedDecl"

    def __init__(self, prev: "NamedDecl"):
        super().__init__(loc=prev.loc)
        self.prev = prev

    @override
    def describe(self) -> str:
        return f"conflict with {self.prev.description}"


@dataclass
class DeclRedefError(DiagError):
    prev: "NamedDecl"
    current: "NamedDecl"

    def __init__(self, prev: "NamedDecl", current: "NamedDecl"):
        super().__init__(loc=current.loc)
        self.prev = prev
        self.current = current

    @override
    def describe(self) -> str:
        return f"redefinition of {self.current.description}"

    @override
    def notes(self):
        if self.prev.loc:
            yield DeclRedefNote(self.prev)


@dataclass
class IDLSyntaxError(DiagError):
    token: str

    @override
    def describe(self) -> str:
        return f"unexpected {self.token!r}"


@dataclass
class PackageNotExistError(DiagError):
    name: str

    @override
    def describe(self) -> str:
        return f"package {self.name!r} not exist"


@dataclass
class DeclNotExistError(DiagError):
    name: str

    @override
    def describe(self) -> str:
        return f"declaration {self.name!r} not exist"


@dataclass
class NotATypeError(DiagError):
    name: str

    @override
    def describe(self) -> str:
        return f"{self.name!r} is not a type name"


@dataclass
class DeclarationNotInScopeError(DiagError):
    name: str

    @override
    def describe(self) -> str:
        return (
            f"declaration name {self.name!r} is not declared or imported in this scope"
        )


@dataclass
class PackageNotInScopeError(DiagError):
    name: str

    @override
    def describe(self) -> str:
        return f"package name {self.name!r} is not imported in this scope"


@dataclass
class GenericArgumentsError(DiagError):
    name: str

    @override
    def describe(self) -> str:
        return f"Invalid generic arguments in {self.name!r}"


@dataclass
class SymbolConflictWithNamespaceError(DiagError):
    decl: "PackageLevelDecl"
    pkg: "PackageDecl"

    def __init__(self, decl: "PackageLevelDecl", pkg: "PackageDecl"):
        super().__init__(loc=decl.loc)
        self.decl = decl
        self.pkg = pkg

    @override
    def describe(self) -> str:
        return f"declaration of {self.decl.description} in {self.pkg.description} shadows a file-level declaration"


@dataclass
class TypeUsageError(DiagError):
    ty: "Type"

    def __init__(self, ty_ref: "TypeRefDecl"):
        super().__init__(loc=ty_ref.loc)
        assert ty_ref.maybe_resolved_ty
        self.ty = ty_ref.maybe_resolved_ty

    @override
    def describe(self) -> str:
        return f"{self.ty.signature} cannot be used in this context"


@dataclass
class EnumValueError(DiagError):
    item: "EnumItemDecl"
    enum: "EnumDecl"

    def __init__(self, item: "EnumItemDecl", enum: "EnumDecl"):
        super().__init__(loc=item.loc)
        self.item = item
        self.enum = enum

    @override
    def describe(self) -> str:
        assert self.enum.ty_ref.maybe_resolved_ty
        return f"value of {self.item.description} ({self.item.value}) is conflict with {self.enum.description} ({self.enum.ty_ref.maybe_resolved_ty.signature})"


@dataclass
class DuplicateExtendsNote(DiagNote):
    @override
    def describe(self) -> str:
        return "previously extended here"


@dataclass
class DuplicateExtendsWarn(DiagWarn):
    iface: "IfaceDecl"
    parent_iface: "IfaceDecl"
    prev_loc: SourceLocation | None = field(kw_only=True)

    @override
    def describe(self) -> str:
        return f"{self.parent_iface.description} is extended multiple times by {self.iface.description}"

    @override
    def notes(self):
        if self.prev_loc:
            yield DuplicateExtendsNote(loc=self.prev_loc)


@dataclass
class RecursiveReferenceNote(DiagNote):
    decl: "TypeDecl"

    def __init__(
        self,
        last: tuple["TypeDecl", "TypeRefDecl"],
    ):
        super().__init__(loc=last[1].loc)
        self.decl = last[0]

    @override
    def describe(self) -> str:
        return f"referenced by {self.decl.description}"


@dataclass
class RecursiveReferenceError(DiagError):
    decl: "TypeDecl"
    other: list[tuple["TypeDecl", "TypeRefDecl"]]

    def __init__(
        self,
        last: tuple["TypeDecl", "TypeRefDecl"],
        other: list[tuple["TypeDecl", "TypeRefDecl"]],
    ):
        super().__init__(loc=last[1].loc)
        self.decl = last[0]
        self.other = other

    @override
    def describe(self) -> str:
        return f"cycle detected in {self.decl.description}"

    @override
    def notes(self):
        for n in self.other:
            yield RecursiveReferenceNote(n)


class IgnoredFileReason(Enum):
    IS_DIRECTORY = "subdirectories are ignored"
    EXTENSION_MISMATCH = "unexpected file extension"
    INVALID_PKG_NAME = "invalid package name"


@dataclass
class IgnoredFileWarn(DiagWarn):
    reason: IgnoredFileReason
    note: DiagNote | None = None

    @override
    def describe(self) -> str:
        return f"unrecognized file: {self.reason.value}"

    def notes(self):
        if self.note:
            yield self.note


@dataclass
class AdhocNote(DiagNote):
    msg: str

    @override
    def describe(self) -> str:
        return self.msg


@dataclass
class AdhocWarn(DiagWarn):
    msg: str

    @override
    def describe(self) -> str:
        return self.msg


@dataclass
class AdhocError(DiagError):
    msg: str

    @override
    def describe(self) -> str:
        return self.msg


@dataclass
class AdhocFatalError(DiagFatalError):
    msg: str

    @override
    def describe(self) -> str:
        return self.msg
