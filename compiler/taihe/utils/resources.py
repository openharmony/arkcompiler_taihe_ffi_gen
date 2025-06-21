"""Tools for tracking resources."""

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

BUNDLE_PYTHON_RUNTIME_DIR_NAME = "pyrt"


class DeploymentMode(Enum):
    DEV = auto()  # Inside the Git repository (repo_root)
    PKG = auto()  # pip install ... (site-packages/taihe)
    BUNDLE = auto()  # Bundled with a python executable (taihe-pkg)


# TODO: CLI: override and print the paths
class ResourceType(Enum):
    """Identifier of resources."""

    RUNTIME_SOURCE = "runtime-source"
    RUNTIME_HEADER = "runtime-header"
    STDLIB = "stdlib"
    DOCUMENTATION = "doc"
    PANDA_VM = "panda-vm"


_MODE_TO_LAYOUT: dict[DeploymentMode, dict[ResourceType, str]] = {
    DeploymentMode.DEV: {
        ResourceType.RUNTIME_SOURCE: "runtime/src",
        ResourceType.RUNTIME_HEADER: "runtime/include",
        ResourceType.STDLIB: "stdlib",
        ResourceType.DOCUMENTATION: "cookbook",
        ResourceType.PANDA_VM: ".panda_vm",
    },
    # Python packaging is not supported yet
    DeploymentMode.PKG: {},
    DeploymentMode.BUNDLE: {
        ResourceType.RUNTIME_SOURCE: "src/taihe/runtime",
        ResourceType.RUNTIME_HEADER: "include",
        ResourceType.STDLIB: "lib/taihe/stdlib",
        ResourceType.DOCUMENTATION: "share/doc/taihe",
        ResourceType.PANDA_VM: "var/lib/panda_vm",
    },
}


@dataclass
class ResourceLocator:
    mode: DeploymentMode
    root_dir: Path = field(default_factory=Path)
    # Path means a overridden value.
    # str means a pre-configured relative path.
    _layout: dict[ResourceType, Path | str] = field(init=False)

    def __post_init__(self):
        # Clone the configuration for later modification.
        self._layout = dict(_MODE_TO_LAYOUT[self.mode])

    def get(self, t: ResourceType) -> Path:
        key = self._layout[t]
        if isinstance(key, str):
            return self.root_dir / key
        else:
            return key

    def override(self, t: ResourceType, p: Path):
        self._layout[t] = p.resolve()

    @classmethod
    def detect(cls, file: str = __file__):
        # The directory looks like:
        #   7    6     5   4      3            2         1     0
        #                      repo_root/     compiler/taihe/utils/resources.py
        #           .venv/lib/python3.12/site-packages/taihe/utils/resources.py
        # taihe/lib/ pyrt/lib/python3.11/site-packages/taihe/utils/resources.py
        #            ^^^^                ^^^^^^^^^^^^^
        #     python_runtime_dir            repo_dir
        #
        # We use the heuristics based on the name of repository and python runtime.
        DEPTH_REPO = 2
        DEPTH_PYRT = 5
        DEPTH_PKG_ROOT = 7
        parents = Path(file).absolute().parents

        def get(i: int) -> Path:
            if i < len(parents):
                return parents[i]
            return Path()

        repo_dir = get(DEPTH_REPO)
        if repo_dir.name == "compiler":
            return ResourceLocator(DeploymentMode.DEV, get(DEPTH_REPO + 1))

        if repo_dir.name == "site-packages":
            if get(DEPTH_PYRT).name == BUNDLE_PYTHON_RUNTIME_DIR_NAME:
                return ResourceLocator(DeploymentMode.BUNDLE, get(DEPTH_PKG_ROOT))
            else:
                return ResourceLocator(DeploymentMode.PKG, get(DEPTH_REPO - 1))

        raise RuntimeError(f"cannot determine deployment layout ({repo_dir=})")
