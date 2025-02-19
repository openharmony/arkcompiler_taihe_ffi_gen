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
    - Poetry，可参考[官方文档](https://python-poetry.org/docs/#installation)  
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
# 修改配置，设置项目环境存储于 compiler/.venv
poetry config virtualenvs.in-project true

# 创建并激活虚拟环境
poetry shell

# 读取 pyproject.toml 文件，解析依赖项并安装
poetry install

# 基于 ANTLR 文法，生成部分项目代码
./generate-grammar
```

### 后续运行时

可以直接使用 `poetry shell` 进入 venv 环境。

### 运行编译器主程序

```bash
python -m taihe --help
```

### 打包并测试编译器

```bash
# 打包
# 执行命令前注释 .gitignore 文件中的 compiler/taihe/parse/antlr
# 默认输出文件夹为 dist/
poetry build

# 测试
./run-test ../test/integer/
```

