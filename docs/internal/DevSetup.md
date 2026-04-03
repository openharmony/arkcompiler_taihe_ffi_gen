# 搭建开发环境

## 项目配置

- **操作系统**
  推荐 Linux（或 WSL），Windows 不保证完整支持
- **软件最低版本**
  - **运行时**
    - Clang 15，GCC 不保证完整支持
    - CMake 3.14
  - **编译器**
    - Python 3.11.4
    - uv，安装可参考[官方文档](https://github.com/astral-sh/uv)

## 编译器

首先配置 Python 及依赖环境。

Ubuntu 用户可在拉取的 Taihe 项目根目录下运行 `scripts/install-ubuntu-deps` 一键配置环境。

在配置好环境后，每次使用时都需要先在项目根目录下运行 `source .venv/bin/activate` 来激活虚拟环境，或者在使用命令行工具时运行 `uv run taihec` 或 `uv run taihe-tryit` 命令而不是直接运行 `taihec` 或 `taihe-tryit`。

### 初次克隆项目时

```bash
# 读取 pyproject.toml 文件，解析依赖项并安装至 `.venv` 目录下
uv sync

# 基于 ANTLR 文法，生成部分项目代码
uv build
```

### 后续运行时

可以直接使用 `source .venv/bin/activate` 进入 venv 环境。

### 运行编译器主程序

```bash
taihec --help
```

## 代码检查与测试

### 代码格式检查

在提交代码前，需要运行代码检查脚本以确保代码符合项目规范：

```bash
scripts/check
```

该脚本会执行以下检查：
- `ruff format --check` - Python 代码格式检查
- `ruff check` - Python 代码 lint 检查
- `pyright compiler` - Python 类型检查

### 自动修复代码格式

另外，开发者应该在提交代码前运行自动修复脚本以确保代码格式符合项目规范：

```bash
# 修复所有代码格式（Python、C++、ArkTS）
scripts/autofix

# 仅修复 Python 代码
scripts/autofix --python

# 仅修复 C++ 代码
scripts/autofix --cpp

# 仅修复 ArkTS 代码
scripts/autofix --arkts
```

### 运行测试

> **注意**：运行测试前需要手动删除根目录下的 `build` 目录以确保依赖 CMake 构建的测试项目能够正确重新生成。

运行项目测试套件：

```bash
scripts/test
```

默认会运行以下测试：
- `pytest` - Python 单元测试
- `core` - 核心功能测试
- `ani` - ANI 相关测试
- `cmake` - CMake 构建测试

也可以指定运行特定测试：

```bash
# 仅运行 pytest
scripts/test --run pytest

# 运行多个指定测试
scripts/test --run pytest core
```
