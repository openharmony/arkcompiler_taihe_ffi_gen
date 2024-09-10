## Requirements

- antlr4-python3-runtime
- antlr4-tools

## Build

Paste and run the following command in shell:

```sh
antlr4 -Dlanguage=Python3 -no-listener Taihe.g4 && python3 meta.py
```

## Usage

```text
usage: main.py [-h] -O DST_DIR -I [SRC_DIRS ...] dll_name

positional arguments:
  dll_name           use -D{DLL_NAME}_DLLEXPORT / -D{DLL_NAME}_DLLIMPORT to export/import .dll when compiling

options:
  -h, --help         show this help message and exit
  -O DST_DIR         directory for generated .h and .cpp files
  -I [SRC_DIRS ...]  directories of .taihe source files
```
