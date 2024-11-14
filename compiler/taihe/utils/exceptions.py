from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from taihe.utils.diagnostics import DiagError, DiagFatalError, DiagNote
from taihe.utils.sources import SourceLocation

if TYPE_CHECKING:
    from taihe.semantics.declarations import (
        Decl,
        IfaceDecl,
        PackageLevelDecl,
        StructFieldDecl,
        TypeRefDecl,
    )


@dataclass
class DefinitionConflictDiagNote(DiagNote):
    MSG = "previously defined here"


@dataclass
class EnumValueCollisionDiagNote(DiagNote):
    MSG = "first use"


@dataclass
class RecursiveExtensionNote(DiagNote):
    MSG = "the interface is extended by {iface.name}"

    def __init__(
        self,
        last: tuple["IfaceDecl", "TypeRefDecl"],
    ):
        self.loc = last[1].loc
        self.iface = last[0]


@dataclass
class RecursiveInclusionNote(DiagNote):
    MSG = "the struct is included in {struct.name}"

    def __init__(
        self,
        last: "StructFieldDecl",
    ):
        self.loc = last.loc
        self.struct = last.parent


@dataclass
class PackageRedefDiagError(DiagError):
    MSG = "redefinition of package {pkg_name!r}"

    pkg_name: str
    prev: SourceLocation

    def notes(self):
        yield DefinitionConflictDiagNote(loc=self.prev)


@dataclass
class DeclRedefDiagError(DiagError):
    MSG = "redefinition of {current.description}"

    prev: "Decl"
    current: "Decl"

    def __init__(self, prev: "Decl", current: "Decl"):
        self.prev = prev
        self.current = current
        self.loc = current.loc

    def notes(self):
        yield DefinitionConflictDiagNote(loc=self.prev.loc)


@dataclass
class EnumValueCollisionError(DiagError):
    MSG = "discriminant value '{value}' already exists"

    prev: "Decl"
    current: "Decl"
    value: int

    def __init__(self, prev: "Decl", current: "Decl", value: int):
        self.prev = prev
        self.current = current
        self.loc = current.loc
        self.value = value

    def notes(self):
        yield EnumValueCollisionDiagNote(loc=self.prev.loc)


@dataclass
class PackageNotExistError(DiagFatalError):
    MSG = "package {pkg!r} not exist"

    pkg: str

    def __init__(
        self,
        pkg: str,
        loc: Optional["SourceLocation"],
    ):
        self.pkg = pkg
        self.loc = loc


@dataclass
class DeclNotExistError(DiagError):
    MSG = "declaration {decl!r} not exist"

    decl: str

    def __init__(
        self,
        decl: str,
        loc: Optional["SourceLocation"],
    ):
        self.decl = decl
        self.loc = loc


@dataclass
class DeclarationNotInScopeError(DiagError):
    MSG = "declaration {decl!r} is not declared or imported in this scope"

    decl: str

    def __init__(
        self,
        decl: str,
        loc: Optional["SourceLocation"],
    ):
        self.decl = decl
        self.loc = loc


@dataclass
class PackageNotInScopeError(DiagError):
    MSG = "package {decl!r} is not imported in this scope"

    decl: str

    def __init__(
        self,
        decl: str,
        loc: Optional["SourceLocation"],
    ):
        self.decl = decl
        self.loc = loc


@dataclass
class SymbolConflictWithNamespaceError(DiagError):
    MSG = "declaration of {current.description} in package {pkg_name!r} shadows a file-level declaration"

    current: "PackageLevelDecl"

    def __init__(self, current: "PackageLevelDecl", pkg_name: str):
        self.current = current
        self.loc = current.loc
        self.pkg_name = pkg_name


@dataclass
class ExtendsTypeError(DiagError):
    MSG = "expected an interface, got {name}"

    def __init__(self, ty: "TypeRefDecl"):
        self.loc = ty.loc
        self.name = ty.name


@dataclass
class RecursiveExtensionError(DiagError):
    MSG = "recursive extension is found in {iface.name}"

    def __init__(
        self,
        last: tuple["IfaceDecl", "TypeRefDecl"],
        other: list[tuple["IfaceDecl", "TypeRefDecl"]],
    ):
        self.loc = last[1].loc
        self.iface = last[0]
        self.other = other

    def notes(self):
        for n in self.other:
            yield RecursiveExtensionNote(n)


@dataclass
class RecursiveInclusionError(DiagError):
    MSG = "recursive inclusion is found in {struct.name}"

    def __init__(
        self,
        last: "StructFieldDecl",
        other: list["StructFieldDecl"],
    ):
        self.loc = last.loc
        self.struct = last.parent
        self.other = other

    def notes(self):
        for n in self.other:
            yield RecursiveInclusionNote(n)


@dataclass
class NotATypeError(DiagError):
    MSG = "declaration {name!r} is not a type"

    decl: str

    def __init__(
        self,
        decl: str,
        loc: Optional["SourceLocation"],
    ):
        self.decl = decl
        self.loc = loc


@dataclass
class NotAPackageError(DiagError):
    MSG = "{name!r} is not a package"

    decl: str

    def __init__(
        self,
        decl: str,
        loc: Optional["SourceLocation"],
    ):
        self.decl = decl
        self.loc = loc


@dataclass
class NotADeclarationError(DiagError):
    MSG = "{name!r} is not a declaration"

    decl: str

    def __init__(
        self,
        decl: str,
        loc: Optional["SourceLocation"],
    ):
        self.decl = decl
        self.loc = loc


@dataclass
class QualifierError(DiagError):
    MSG = "qualifier {qual} cannot be applied to {name}"

    def __init__(self, ty: "TypeRefDecl"):
        self.loc = ty.loc
        self.name = ty.name
        self.qual = ty.qual.describe()
