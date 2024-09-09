## Requirements

- antlr4-python3-runtime
- antlr4-tools

## Build

Paste and run the following command in shell:

```sh
antlr4 -Dlanguage=Python3 -no-listener Taihe.g4 && python3 meta.py
```

# Usage

```sh
usage: python3 main.py [-h] [-I [SRC_DIRS ...]] [-O DST_DIR]

options:
  -h, --help         show this help message and exit
  -I [SRC_DIRS ...]  directories of .taihe source files
  -O DST_DIR         directory for generated .h and .cpp files
```
