# 快速启动

本文档说明如何快速使用 taihe 工具进行代码生成。

## 安装 taihe 包
```bash
pip install taihe-0.1.0-py3-none-any.whl
```

### 运行测试示例
在本项目的 `test` 目录下包含有若干使用示例，在安装完成后，你可以通过 `run-test` 命令来运行这些示例：
```sh
# 测试基本函数、结构体
./run-test test/integer - O3

# 测试字符串的跨二进制传递
./run-test test/string -O3

# 测试 OOP、枚举类、联合体
./run-test test/rgb -O3

# 综合场景测试
./run-test test/xml -O3 -a \"-lexpat\" -r "../test/xml/data/test.xml"

# 测试异步功能
./run-test test/promise -O3
```

查看 `run-test` 使用帮助：
```sh
./run-test -h
```

此外，你也可以自行编写测试样例，测试样例目录结构须遵循如下规则：

- `test_case/idl`：包含用户自己编写的 IDL 文件
- `test_case/author`：作者侧的接口实现代码
- `test_case/user`：用户侧的接口调用代码

```
test
├── test_case
│   ├── author
│   │   └── impl.cpp
│   └── user
│   │   └── main.cpp
│   └── idl
│       ├── idl_1.taihe
│       └── idl_2.taihe
```

以上目录要求仅与 `run-test` 测试脚本相关，如自行编写测试脚本可不按照此目录设置。

## 运行
通过 IDL 生成作者侧相关代码：
```bash
python -m taihe -I path/to/idl/files/ -O author/output/files/directory/ -a
```

通过 IDL 生成用户侧相关代码：
```bash
python -m taihe -I path/to/idl/files/ -O author/output/files/directory/ -u
```

查看使用帮助：
```bash
python -m taihe -h
```
