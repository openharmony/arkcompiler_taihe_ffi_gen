from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from typing_extensions import override

from taihe.utils.diagnostics import DiagError, DiagNote, DiagWarn
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.declarations import (
        AttrItemDecl,
        EnumItemDecl,
        IfaceDecl,
        IfaceParentDecl,
        NamedDecl,
        Package,
        PackageLevelDecl,
        Type,
        TypeDecl,
        TypeRefDecl,
    )


@dataclass
class PackageRedefNote(DiagNote):
    @property
    @override
    def format_msg(self) -> str:
        return "previously occurred here"


@dataclass
class PackageRedefError(DiagError):
    pkg_name: str
    prev_loc: Optional[SourceLocation] = field(kw_only=True)

    def notes(self):
        if self.prev_loc:
            yield PackageRedefNote(loc=self.prev_loc)

    @property
    @override
    def format_msg(self) -> str:
        return f"package name {self.pkg_name!r} is duplicated"


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
class EnumValueConflictNote(DiagNote):
    prev: "EnumItemDecl"

    def __init__(self, prev: "EnumItemDecl"):
        self.prev = prev
        self.loc = prev.loc

    @property
    @override
    def format_msg(self) -> str:
        return f"conflict with {self.prev.description}"


@dataclass
class EnumValueConflictError(DiagError):
    prev: "EnumItemDecl"
    current: "EnumItemDecl"

    def __init__(self, prev: "EnumItemDecl", current: "EnumItemDecl"):
        self.prev = prev
        self.current = current
        self.loc = current.loc

    def notes(self):
        if self.prev.loc:
            yield DeclRedefNote(self.prev)

    @property
    @override
    def format_msg(self) -> str:
        return f"value {self.current.value} of {self.current.description} is repeated"


@dataclass
class AttrRedefNote(DiagNote):
    prev: "AttrItemDecl"

    def __init__(self, prev: "AttrItemDecl"):
        self.prev = prev
        self.loc = prev.loc

    @property
    @override
    def format_msg(self) -> str:
        return f"conflict with {self.prev.description}"


@dataclass
class AttrRedefError(DiagError):
    prev: "AttrItemDecl"
    current: "AttrItemDecl"

    def __init__(self, prev: "AttrItemDecl", current: "AttrItemDecl"):
        self.prev = prev
        self.current = current
        self.loc = current.loc

    def notes(self):
        if self.prev.loc:
            yield AttrRedefNote(self.prev)

    @property
    @override
    def format_msg(self) -> str:
        return f"duplicate {self.current.description}"


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
    pkg: "Package"

    def __init__(self, decl: "PackageLevelDecl", pkg: "Package"):
        self.decl = decl
        self.loc = decl.loc
        self.pkg = pkg

    @property
    @override
    def format_msg(self) -> str:
        return f"declaration of {self.decl.description} in {self.pkg.description} shadows a file-level declaration"


@dataclass
class ExtendsTypeError(DiagError):
    ty: "Type"

    def __init__(self, decl: "IfaceParentDecl", ty: "Type"):
        self.loc = decl.ty_ref.loc
        self.ty = ty

    @property
    @override
    def format_msg(self) -> str:
        return f"{self.ty.representation} cannot be parent of an interface"


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
    prev_loc: Optional["SourceLocation"]

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
