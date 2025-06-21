from taihe.utils.resources import DeploymentMode, ResourceLocator


def test_dev():
    p = "repo_root/compiler/taihe/utils/resources.py"
    loc = ResourceLocator.detect(p)
    assert loc.mode == DeploymentMode.DEV
    assert loc.root_dir.name == "repo_root"


def test_pkg():
    p = ".venv/lib/python3.12/site-packages/taihe/utils/resources.py"
    loc = ResourceLocator.detect(p)
    assert loc.mode == DeploymentMode.PKG
    assert loc.root_dir.name == "taihe"


def test_bundle():
    p = "taihe-pkg/lib/pyrt/lib/python3.11/site-packages/taihe/utils/resources.py"
    loc = ResourceLocator.detect(p)
    assert loc.mode == DeploymentMode.BUNDLE
    assert loc.root_dir.name == "taihe-pkg"
