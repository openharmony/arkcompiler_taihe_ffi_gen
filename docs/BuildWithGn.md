# 在项目的 GN 构建流程中加入 Taihe

## 如何将 Taihe 加入项目构建流程

需要将 Taihe 中的 **runtime** 和 **compiler** 部分加入到项目构建流程。

- **Taihe runtime** 部分产物为 `libtaihe-rt.so`，可以通过 `libs` 和 `lib_dirs` 字段来设置依赖。
  
```gn
shared_library("author") {
  lib_dirs = [ libtaihe_rt_path ]
  libs = ["taihe-rt"]
}
```

- **Taihe compiler** 部分的运行调用使用 `taihe_compiler` 模板进行了封装，在使用时直接在 `BUILD.gn` 中使用模板实例化，并设置到 `deps` 中即可。

### 1. 使用 `taihe_compiler` 模板

实例化一个 `taihe_compiler`，指定需要编译的 `.taihe` 文件，以及编译的模式。

```gn
taihe_compiler("author_compiler") {
  sources = [
    "a.taihe",
    "b.taihe"
  ]
  mode = "author"
}
```

- `sources`：需要编译的 `.taihe` 文件，`taihe_compiler` 会生成对应的头文件。
- `mode`：`taihe_compiler` 提供两种编译模式，`author` 模式和 `user` 模式。

### 2. 设置依赖

通过 `deps` 字段引入 `"author_compiler"`，会编译提供的 `.taihe` 文件生成头文件，并将这些头文件引入到后续构建过程中。

```gn
shared_library("author") {
  deps = [
    ":author_compiler",
  ]
}
```

## 运行示例项目

### **路径**

`TaiheCompiler/test/integer`

### **步骤**

1. **clone taihe 项目并编译**

```sh
git clone git@github.com:Jemtaly/TaiheCompiler.git
cd TaiheCompiler
./scripts/build
```

2. **给出 taihe 产物的路径 `TAIHE_OUT_PATH`**

```sh
export TAIHE_OUT_PATH={path_to_taihe_outs}
```

3. **运行示例项目**

```sh
cd ./test/integer
gn gen out --args='target_cpu="$(uname -m)"'
ninja -C out
```
