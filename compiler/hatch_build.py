import re
import subprocess
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from functools import cache
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

compiler_dir = Path(__file__).parent
sys.path.insert(0, str(compiler_dir))
from taihe.utils.resources import Antlr, ResourceContext  # noqa: E402

ANTLR_PKG = "taihe.parse.antlr"


@cache
def get_parser():
    from taihe.parse.antlr.TaiheParser import TaiheParser

    return TaiheParser


def get_hint(attr_kind):
    if attr_kind.endswith("Lst"):
        return f'List["TaiheAST.{attr_kind[:-3]}"]'
    if attr_kind.endswith("Opt"):
        return f'Optional["TaiheAST.{attr_kind[:-3]}"]'
    return f'"TaiheAST.{attr_kind}"'


def get_attr_pairs(ctx):
    for attr_full_name in ctx.__dict__:
        if not attr_full_name.startswith("_") and attr_full_name != "parser":
            yield attr_full_name.split("_", 1)


def snake_case(name):
    """Convert CamelCase to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class Inspector:
    def __init__(self):
        self.parentCtx = None
        self.invokingState = None
        self.children = None
        self.start = None
        self.stop = None


def generate_ast(antlr_path: Path):
    """Generate the TaiheAST.py file."""
    ast_file = antlr_path / "TaiheAST.py"
    ast_file.parent.mkdir(parents=True, exist_ok=True)

    with open(ast_file, "w") as file:
        file.write(
            "from dataclasses import dataclass\n"
            "from typing import Any, Union, List, Optional\n"
            "\n"
            "from taihe.utils.sources import SourceLocation\n"
            "\n"
            "\n"
            "class TaiheAST:\n"
            "    @dataclass(kw_only=True)\n"
            "    class any:\n"
            "        loc: SourceLocation\n"
            "\n"
            "        def _accept(self, visitor) -> Any:\n"
            "            raise NotImplementedError()\n"
            "\n"
            "\n"
            "    @dataclass\n"
            "    class TOKEN(any):\n"
            "        text: str\n"
            "\n"
            "        def __str__(self):\n"
            "            return self.text\n"
            "\n"
            "        def _accept(self, visitor) -> Any:\n"
            "            return visitor.visit_token(self)\n"
            "\n"
        )
        parser = get_parser()
        type_list = []
        for rule_name in parser.ruleNames:
            node_kind = rule_name[0].upper() + rule_name[1:]
            ctx_kind = node_kind + "Context"
            ctx_type = getattr(parser, ctx_kind)
            type_list.append((node_kind, ctx_type))
        for node_kind, ctx_type in type_list:
            subclasses = ctx_type.__subclasses__()
            if subclasses:
                file.write(f"    {node_kind} = Union[\n")
                for sub_type in subclasses:
                    sub_kind = sub_type.__name__
                    attr_kind = sub_kind[:-7]
                    attr_hint = get_hint(attr_kind)
                    type_list.append((attr_kind, sub_type))
                    file.write(f"        {attr_hint},\n")
                file.write("    ]\n\n")
            else:
                ctx = ctx_type(None, Inspector())
                file.write(f"    @dataclass\n    class {node_kind}(any):\n")
                for attr_kind, attr_name in get_attr_pairs(ctx):
                    attr_hint = get_hint(attr_kind)
                    file.write(f"        {attr_name}: {attr_hint}\n")
                file.write(
                    f"\n"
                    f"        def _accept(self, visitor) -> Any:\n"
                    f"            return visitor.visit_{snake_case(node_kind)}(self)\n"
                    f"\n"
                )


def generate_visitor(antlr_path: Path):
    """Generate the TaiheVisitor.py file."""
    visitor_file = antlr_path / "TaiheVisitor.py"
    visitor_file.parent.mkdir(parents=True, exist_ok=True)

    with open(visitor_file, "w") as file:
        file.write(
            f"from {ANTLR_PKG}.TaiheAST import TaiheAST\n"
            f"\n"
            f"from typing import Any\n"
            f"\n"
            f"\n"
            f"class TaiheVisitor:\n"
            f"    def visit(self, node: TaiheAST.any) -> Any:\n"
            f"        return node._accept(self)\n"
            f"\n"
            f"    def visit_token(self, node: TaiheAST.TOKEN) -> Any:\n"
            f"        raise NotImplementedError()\n"
            f"\n"
        )
        parser = get_parser()
        type_list = []
        for rule_name in parser.ruleNames:
            node_kind = rule_name[0].upper() + rule_name[1:]
            ctx_kind = node_kind + "Context"
            ctx_type = getattr(parser, ctx_kind)
            type_list.append((node_kind, ctx_type))
        for node_kind, ctx_type in type_list:
            subclasses = ctx_type.__subclasses__()
            if subclasses:
                for sub_type in subclasses:
                    sub_kind = sub_type.__name__
                    attr_kind = sub_kind[:-7]
                    file.write(
                        f"    def visit_{snake_case(attr_kind)}(self, node: TaiheAST.{attr_kind}) -> Any:\n"
                        f"        return self.visit_{snake_case(node_kind)}(node)\n"
                        f"\n"
                    )
            file.write(
                f"    def visit_{snake_case(node_kind)}(self, node: TaiheAST.{node_kind}) -> Any:\n"
                f"        raise NotImplementedError()\n"
                f"\n"
            )


def already_compiled(g4_path: Path, antlr_path: Path) -> bool:
    parser_file = antlr_path / "TaiheParser.py"
    return (
        parser_file.exists() and g4_path.stat().st_mtime < parser_file.stat().st_mtime
    )


def do_gen_grammar():
    g4_path = compiler_dir / "Taihe.g4"
    antlr_path = compiler_dir / ANTLR_PKG.replace(".", "/")
    if already_compiled(g4_path, antlr_path):
        print("Already compiled, skipping ANTLR generation")
        return

    ResourceContext.initialize()
    print("Running antlr...")
    Antlr.resolve().run_tool(
        [
            "-Dlanguage=Python3",
            "-no-listener",
            str(g4_path),
            "-o",
            str(antlr_path),
        ]
    )
    generate_ast(antlr_path)
    generate_visitor(antlr_path)


def git(args: Sequence[str], root: str, default: str = "unknown") -> str:
    try:
        return subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=True,
            cwd=root,
        ).stdout
    except FileNotFoundError:
        return default
    except subprocess.CalledProcessError:
        return default


def do_gen_version(root: str, target: Path, version: str):
    git_commit = git(
        ["rev-parse", "HEAD"], root=root, default="<unknown-commit>"
    ).strip()
    git_message = git(
        ["log", "-1", "--pretty=%B"],
        root=root,
        default="<unknown-message>",
    ).splitlines()[0]

    now = datetime.now()
    build_timestamp = now.astimezone(timezone.utc).timestamp()
    build_date = now.strftime("%Y%m%d")

    target.write_text(
        f"""version = {version!r}
git_commit = {git_commit!r}
git_message = {git_message!r}
build_date = {build_date!r}
build_time_utc = {build_timestamp!r}
"""
    )


class TaiheBuildHook(BuildHookInterface):
    """Hatch build hook for generating ANTLR-based AST and visitor classes."""

    PLUGIN_NAME = "taihe-build"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        del version
        do_gen_grammar()

        config_version_file = "compiler/taihe/_version.py"
        build_data["artifacts"].append(config_version_file)
        do_gen_version(
            self.root, Path(self.root) / config_version_file, self.metadata.version
        )
