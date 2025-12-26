# 搭建开发环境

## 项目配置

- **操作系统**
  推荐 Linux（或 WSL），Windows 不保证完整支持
- **软件最低版本**
  - **运行时**
    - Clang 15，GCC 不保证完整支持
    - CMake 3.14
  - **编译器**
    - Python 3.10
    - uv，安装可参考[官方文档](https://github.com/astral-sh/uv)

## 编译器

首先配置 Python 及依赖环境。

Ubuntu 用户可运行 `scripts/install-ubuntu-deps` 一键配置环境。

通过 `scripts/install-ubuntu-deps` 配置好环境后，每次使用时都需要先在项目根目录下运行 `source .venv/bin/activate` 来激活虚拟环境，或者在使用命令行工具时运行 `uv run taihec` 或 `uv run taihe-tryit` 命令而不是直接运行 `taihec` 或 `taihe-tryit`。

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
