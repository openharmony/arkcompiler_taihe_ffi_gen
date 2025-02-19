# 阶段性目标

## Project setup

- **Goal:** A plus B
  - **C (author):** business logic, `return a + b`
  - **C (interface):** auto-generated, header + implementation
  - **C (consumer):** consumer logic, `assert(add(1, 1) == 2)`
- **Features**
  - Namespaces
  - Primitive types
- **Initialize the repository**
- **Compiler**
  - Infra, DSL design, lex & parse
  - C ABI generation

## Core standard library

- **Goal**
  - `assert(concat(["hello", " ", "world"]) == "hello world")`
  - `assert(split("a,b,c", ",") == ["a", "b", "c"])`
  - Integrated test infrastructure
- **Features**
  - Standard library: Strings and arrays
  - C++ projection: memory management
  - Parameters: in/out/fill/byval/byref

## Composite types

- **Goal:** logger
  - Enum for log level
  - Struct for log details
  - Constant literal for log paths
- **Features:** struct, enum, and constants

## OOP

- **Goal:** shapes
  - **Inheritance**
    - **Author:** `IShape: IColorable`
    - **Consumer:** `Rectangle: IShape`
    - **Consumer:** `Square: Rectangle`
  - **Methods:** `IShape::calculateArea()`, `IColor::copyColorFrom()`
  - **Properties:** `IShape::name`, `IColorable::color`
- **Features**
  - Methods
  - Properties
  - Inheritance

## Callbacks

- **Goal:** timer
- **Features**
  - Callback and related library support
  - Type alias
  - Object lifetime management

## TODO

### High-Level Designs

- Error handling
- Thread safety
- RPC (?)

### Engineering

- Integrate with OHOS
  - Migrate from C(++)
  - Migrate: Cangjie / ArkUI
  - Integrate with the build system
- Standard library
- Code generation
  - Dart
  - ArkTS (NAPI)

### Refactor

#### Driver

- Introduce the concept of "Backend"
- Introduce the concept of "Action", such as partial compilation, batch compilation, and code check
- Design flexible option parsing for specific backend

#### Parser

- Add support for `#[attributes]`
- Report parsing errors to `DiagnosticsManager`
- Report warning on unexpected code styles (e.g. `class FOOBAR`)

#### Semantics

- **Types:** support tuple
- **Pass:** analysis for type dependency graph
- **Decl (or parse/convert):** fix the parent field of `TypeRefDecl`

#### Projection, C and Cpp

- Reorganize the source structure and support partial type imports
- Remove `std::add_rvalue_reference_t` with type analysis
- Use proper name mangling
- Reorganize the filesystem hierarchy of header files
