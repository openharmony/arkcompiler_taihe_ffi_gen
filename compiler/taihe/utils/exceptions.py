from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from typing_extensions import override

from taihe.utils.diagnostics import DiagError, DiagNote, DiagWarn

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
    from taihe.utils.sources import SourceLocation


@dataclass
class DeclRedefNote(DiagNote):
    prev: "NamedDecl"

    def __init__(self, prev: "NamedDecl"):
        self.prev = prev
        self.loc = prev.loc

    @property
    @override
    def format_msg(self) -> str:
        return f"conflict with {self.prev.description}"


@dataclass
class DeclRedefError(DiagError):
    prev: "NamedDecl"
    current: "NamedDecl"

    def __init__(self, prev: "NamedDecl", current: "NamedDecl"):
        self.prev = prev
        self.current = current
        self.loc = current.loc

    def notes(self):
        if self.prev.loc:
            yield DeclRedefNote(self.prev)

    @property
    @override
    def format_msg(self) -> str:
        return f"redefinition of {self.current.description}"


@dataclass
class IDLSyntaxError(DiagError):
    token: str

    @property
    @override
    def format_msg(self) -> str:
        return f"unexpected {self.token!r}"


@dataclass
class PackageNotExistError(DiagError):
    name: str

    @property
    @override
    def format_msg(self) -> str:
        return f"package {self.name!r} not exist"


@dataclass
class DeclNotExistError(DiagError):
    name: str

    @property
    @override
    def format_msg(self) -> str:
        return f"declaration {self.name!r} not exist"


@dataclass
class NotATypeError(DiagError):
    name: str

    @property
    @override
    def format_msg(self) -> str:
        return f"{self.name!r} is not a type name"


@dataclass
class DeclarationNotInScopeError(DiagError):
    name: str

    @property
    @override
    def format_msg(self) -> str:
        return (
            f"declaration name {self.name!r} is not declared or imported in this scope"
        )


@dataclass
class PackageNotInScopeError(DiagError):
    name: str

    @property
    @override
    def format_msg(self) -> str:
        return f"package name {self.name!r} is not imported in this scope"


@dataclass
class GenericArgumentsError(DiagError):
    name: str

    @property
    @override
    def format_msg(self) -> str:
        return f"Invalid generic arguments in {self.name!r}"


@dataclass
class SymbolConflictWithNamespaceError(DiagError):
    decl: "PackageLevelDecl"
    pkg: "PackageDecl"

    def __init__(self, decl: "PackageLevelDecl", pkg: "PackageDecl"):
        self.decl = decl
        self.loc = decl.loc
        self.pkg = pkg

    @property
    @override
    def format_msg(self) -> str:
        return f"declaration of {self.decl.description} in {self.pkg.description} shadows a file-level declaration"


@dataclass
class TypeUsageError(DiagError):
    ty: "Type"

    def __init__(self, ty_ref: "TypeRefDecl"):
        assert ty_ref.resolved_ty
        self.ty = ty_ref.resolved_ty
        self.loc = ty_ref.loc

    @property
    @override
    def format_msg(self) -> str:
        return f"{self.ty.representation} cannot be used in this context"


@dataclass
class EnumValueError(DiagError):
    item: "EnumItemDecl"
    enum: "EnumDecl"

    def __init__(self, item: "EnumItemDecl", enum: "EnumDecl"):
        self.loc = item.loc
        self.item = item
        self.enum = enum

    @property
    @override
    def format_msg(self) -> str:
        if self.enum.ty_ref is None:
            type_repr = "empty"
        else:
            assert self.enum.ty_ref.resolved_ty
            type_repr = self.enum.ty_ref.resolved_ty.representation
        return f"value of {self.item.description} ({self.item.value}) is conflict with {self.enum.description} ({type_repr})"


@dataclass
class DuplicateExtendsNote(DiagNote):
    @property
    @override
    def format_msg(self) -> str:
        return "previously extended here"


@dataclass
class DuplicateExtendsWarn(DiagWarn):
    iface: "IfaceDecl"
    parent_iface: "IfaceDecl"
    prev_loc: Optional["SourceLocation"] = field(kw_only=True)

    def notes(self):
        if self.prev_loc:
            yield DuplicateExtendsNote(loc=self.prev_loc)

    @property
    @override
    def format_msg(self) -> str:
        return f"{self.parent_iface.description} is extended multiple times by {self.iface.description}"


@dataclass
class RecursiveReferenceNote(DiagNote):
    decl: "TypeDecl"

    def __init__(
        self,
        last: tuple["TypeDecl", "TypeRefDecl"],
    ):
        self.loc = last[1].loc
        self.decl = last[0]

    @property
    @override
    def format_msg(self) -> str:
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
        self.loc = last[1].loc
        self.decl = last[0]
        self.other = other

    def notes(self):
        for n in self.other:
            yield RecursiveReferenceNote(n)

    @property
    @override
    def format_msg(self) -> str:
        return f"cycle detected in {self.decl.description}"


@dataclass
class AdhocNote(DiagNote):
    msg: str

    @property
    @override
    def format_msg(self) -> str:
        return self.msg
