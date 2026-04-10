# AGENTS.md

**Name**: Taihe

**Purpose**: Multi-language interface programming model compiler and code generator

**Primary Language**: Python, C++

## Project Overview

Taihe is a multi-language interface programming model that generates cross-language bindings from IDL (Interface Definition Language) files. It separates API publishers from consumers at the binary level, enabling independent upgrades.

Key capabilities:
- Parse `.taihe` IDL files defining structs, enums, interfaces, functions
- Generate C ABI layer for binary compatibility
- Generate C++ projections for comfortable native development
- Generate ArkTS/ANI bindings for HarmonyOS development

## Tooling Requirements

- Python 3.11+, uv package manager
- Clang 15+, CMake 3.14+
- Linux recommended (Windows not fully supported)

## Directory Structure

```
taihe/
├── compiler/
│   ├── taihe/               # Compiler source code
│   │   ├── utils/           # Utilities: diagnostics, analyses, file handling
│   │   ├── parse/           # Frontend: parsing and AST to IR conversion
│   │   ├── semantics/       # Semantic analysis and IR definitions
│   │   ├── codegen/         # Code generation backends
│   │   ├── driver/          # Compiler driver and backend system
│   │   └── cli/             # Command-line interface
│   ├── Taihe.g4             # ANTLR grammar file
│   └── tests/               # Python unit tests
├── runtime/                 # Taihe runtime library (C++)
│   ├── include/             # Taihe runtime headers
│   │   └── taihe/           # Common runtime headers
│   │      └── platform/     # Platform-specific headers
│   └── src/                 # Taihe runtime source files
├── stdlib/                  # Standard library IDL files
├── test/                    # Integration tests
│   └── .../                 # Test projects with idl/, author/, user/ structure
├── cookbook/                # Example projects
│   └── .../                 # Example projects with idl/, author/, user/ structure and additional README.md
└── docs/                    # Documentation
    ├── public/              # User-facing documentation
    │   ├── spec/            # Language specification and reference
    │   └── backend-*/       # Backend specific usage guides
    └── internal/            # Developer documentation
        ├── compiler/        # Compiler architecture and development
        └── runtime/         # Runtime architecture and development
```

## Development Commands

### Environment Setup

```bash
# Sync Python dependencies
uv sync

# Build ANTLR parser (required after Taihe.g4 changes)
uv build

# Activate virtual environment
source .venv/bin/activate
```

### Running the Compiler

```bash
taihec --help
taihec idl/path/to/file.taihe ... --output output/dir --generate backend ... --codegen key=value ...
```

### Code Quality

```bash
# Check formatting and types (run before committing)
scripts/check

# Auto-fix code formatting
scripts/autofix
```

### Testing

There are two layers of tests. Use the right one depending on what you're testing:

- **pytest** (`compiler/tests/`): Only for testing the compiler frontend — parsing, semantic analysis, error diagnostics. Not for backend-specific features like code generation or annotations.
- **taihe-tryit / integration tests** (`test/`): End-to-end tests for backend features (code generation, annotations, runtime behavior). Each test is a self-contained project with `idl/`, `author/`, `user/` directories. If user-facing interface or functionality is affected, also add corresponding examples to `cookbook/`. Don't forget to register new subdirectories in `CMakeLists.txt`.

```bash
# Clean previous builds
rm -rf build/

# Run all tests (pytest, core, ani, cmake)
scripts/test

# Run specific test suites
scripts/test --run pytest          # Python unit tests only
scripts/test --run pytest core     # Multiple test suites
scripts/test --run ani             # ANI tests (requires CMake build)

# Run single pytest file
uv run pytest compiler/tests/test_semantic_error.py -v
```

### Testing Individual Projects (taihe-tryit)

`taihe-tryit` is a development utility for testing single cookbook examples or test cases. Each project follows the structure: `idl/` (source .taihe files), `author/` (implementation), `user/` (consumer code), `generated/` (output from code generation), `build/` (build artifacts).

**Standard workflow:**

1. **Define Interface**: Write `.taihe` IDL files in `idl/`.
2. **Generate Code**: Run `taihe-tryit generate -u <mode> example` to produce bridge code in `generated/` and author-side templates in `generated/temp/`.
3. **Implement Author Side**: Write the implementation in `author/`, referring to the generated templates.
4. **Implement User Side**: Write consumer code in `user/`.
5. **Run Test**: Run `taihe-tryit test -u <mode> example` to regenerate, build, and execute the test.

**Commands:**

```bash
taihe-tryit create -u cpp path/to/example         # Create a new project scaffold
taihe-tryit generate -u sts path/to/example       # Generate code only (no build)
taihe-tryit build -u sts path/to/example          # Build only (assumes code generated)
taihe-tryit test -u cpp test/rgb                  # Full flow: generate + build + run
taihe-tryit test -u sts test/ani_callback         # Full flow (ArkTS Static mode)
```

## Architecture

### Compiler Pipeline

The compilation is driven by `CompilerInstance.run()`, which executes the following phases:

| Phase | Compiler Action | Backend Hook | Backend Action | Hook Constraints |
|-------|-----------------|--------------|----------------|------------------|
| (init) | Construct backends | `register()` | Register attributes | - |
| `collect()` | Scan and add source files | `inject()` | Add backend-specific sources (e.g., stdlib) | - |
| `parse()` | Parse sources to syntax IR | - | - | - |
| `resolve()` | Resolve names, types, enum values, attributes | - | - | - |
| `post_process()` | - | `post_process()` | Add backend-specific metadata to resolved IR | Must be idempotent. Must not affect other backends or modify shared attributes, only for adding backend-specific metadata. May call `Analysis.provide()`. |
| `validate()` | Semantic validation | `validate()` | Backend-specific validation | Must not transform IR. Must not break previously valid code, code without backend-specific features must always pass. |
| `generate()` | Code generation (skip if errors) | `generate()` | Emit output files | Must not transform IR or report errors at this stage. |

### Key Modules

1. **Frontend** (`taihe.parse`): Source text -> IR
   - `compiler/Taihe.g4`: ANTLR grammar definition
   - `taihe.parse.antlr`: Generated lexer/parser (regenerate with `uv build`)
   - `taihe.parse.convert`: AST to IR conversion

2. **Semantics** (`taihe.semantics`): IR resolution and validation
   - `declarations.py`: IR node types (GlobFuncDecl, StructDecl, EnumDecl, etc.)
   - `types.py`: Type system definitions
   - `attributes.py`: Language-agnostic annotation system
   - `visitor.py`: DeclVisitor, RecursiveDeclVisitor, TypeVisitor patterns
   - `analysis.py`: IR resolution (name/type/attribute) and semantic validation passes

3. **Code Generation** (`taihe.codegen`): IR -> Target source code
   - `abi/`: C ABI layer generation (mangle, analyses, gen_abi, gen_impl)
   - `cpp/`: C++ projection generation
   - `ani/`: ArkTS/ANI binding generation

### Driver and Backend System

- `taihe.driver.contexts`: CompilerInvocation (configuration) and CompilerInstance (execution)
- `taihe.driver.backend`: BackendRegistry, BackendConfig, Backend base classes

Current Available backends:
- ABI related: `abi-header`, `abi-source`, `c-author`
- C++ related: `cpp-common`, `cpp-user`, `cpp-author`
- ArkTS/ANI related: `ani-bridge`
- Utility: `pretty-print`

### Key Design Patterns

- **Analysis System** (`taihe.utils.analyses`): Cached, lazy computation of derived information attached to IR nodes via AnalysisManager
- **Diagnostics** (`taihe.utils.diagnostics`): Structured error/warning reporting with source locations
- **Attribute System** (`taihe.semantics.attributes`): Flexible annotation system for attaching metadata to IR nodes without modifying their structure, used for implementing backend-specific features

## Documentation

Here are some useful references for different tasks:

| Task | Reference |
|------|-----------|
| Use Taihe CLI tools | `docs/public/spec/CliReference.md` |
| IDL syntax and language features | `docs/public/spec/IdlReference.md` |
| C++ projection usage | `docs/public/backend-cpp/CppUsageGuide.md` |
| Compiler architecture and development | `docs/internal/compiler` |
| Runtime library architecture and development | `docs/internal/runtime` |

For usage patterns, refer to `cookbook/` examples. For complete test cases, see `test/`.

## Development Notes

### Common Pitfalls

1. **Virtual environment required**: `taihec` and `taihe-tryit` require an activated virtual environment. Use `source .venv/bin/activate` first, or prefix commands with `uv run`.

2. **ANTLR regeneration**: After modifying `compiler/Taihe.g4`, you must run `uv build` to regenerate the parser. Forgetting this will cause the changes to have no effect.

3. **CMake cache stale**: `scripts/test` depends on CMake and does not automatically clean the `build/` directory. If you only modified compiler code, CMake won't detect the changes. Run `rm -rf build/` before re-running tests to ensure a fresh build.

4. **CMakeLists.txt updates**: When adding new subdirectories to `test/` or `cookbook/`, remember to register them in the corresponding `CMakeLists.txt`.

### Workflow Recommendations

- **Consult documentation first**: For IDL syntax, type mappings, and backend-specific features, refer to `docs/` before guessing. The documentation is authoritative for current behavior.
- **Use `taihe-tryit generate`**: When developing backends, use `taihe-tryit generate` to quickly validate code generation without a full build/run cycle.

### Code Style

- **Python**: ruff format + ruff check + pyright type checking. Type annotations are always required for function signatures.
- **C++**: clang-format-19, C++17 standard, Clang compiler. Since the Taihe runtime aims to provide users with a similar experience to the C++ standard library, its naming conventions and coding styles should also follow the C++ standard library as much as possible.
- **ArkTS**: clang-format-19 (with JS assumptions).
