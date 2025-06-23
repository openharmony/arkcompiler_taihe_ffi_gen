from taihe.utils.resources import DeploymentMode, ResourceContext


def test_dev():
    p = "/tmp/repo_root/compiler/taihe/utils/resources.py"
    loc = ResourceContext.from_path(p)
    assert loc.deployment_mode == DeploymentMode.DEV
    assert loc.base_dir.name == "repo_root"


def test_pkg():
    p = ".venv/lib/python3.12/site-packages/taihe/utils/resources.py"
    loc = ResourceContext.from_path(p)
    assert loc.deployment_mode == DeploymentMode.PKG
    assert loc.base_dir.name == "data"


def test_bundle():
    p = "taihe-pkg/lib/pyrt/lib/python3.11/site-packages/taihe/utils/resources.py"
    loc = ResourceContext.from_path(p)
    assert loc.deployment_mode == DeploymentMode.BUNDLE
    assert loc.base_dir.name == "taihe-pkg"
