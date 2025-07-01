# 搭建开发环境

## 项目配置

- **操作系统**
  推荐 Linux (或 WSL)，Windows 不保证完整支持
- **软件最低版本**
  - **运行时**
    - Clang 15，GCC 不保证完整支持
    - CMake 3.14
  - **编译器**
    - Python 3.10
    - uv，可参考[官方文档](https://github.com/astral-sh/uv)
    - ANTLR 4
    - antlr4-python3-runtime
    - antlr4-tools

初次克隆项目时，可安装 Git Hook，在提交时自动触发代码检查：

```bash
./scripts/install-git-hooks
```

## 编译器

首先配置 Python 及依赖环境。后续操作均假设位于 `compiler/` 目录下。

### 初次克隆项目时

```bash
# 读取 pyproject.toml 文件，解析依赖项并安装至 `compiler/.venv` 目录下
uv sync

# 基于 ANTLR 文法，生成部分项目代码
uv run ./generate-grammar
```

### 后续运行时

可以直接使用 `source .venv/bin/activate` 进入 venv 环境。

### 运行编译器主程序

```bash
taihec --help
```
