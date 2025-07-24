# export default

本章节介绍如何使用 `@sts_export_default` 注解来实现 ets 中的 export default

## 第一步：编写接口原型

**File: `idl/export_example.taihe`**
```taihe
@!namespace("export_pkg", "export_ns")
@!sts_export_default

struct Inner {
    i: i32;
    s: String;
}
```

然后让另一个 Taihe IDL 文件 import：

**File: `idl/import_example.taihe`**
```taihe
from export_example use Inner;

function testImport(obj: Inner): void;
```

@sts_export_default 注解使用方法如下：

- 给 namespace 添加 export_default

  ```taihe
  @!namespace("xxx", "yyy")
  @!sts_export_default

  // ...
  ```

- 给 interface/enum/union 添加 export_default

  ```taihe
  // 只能加在头等声明
  @sts_export_default
  interface IfaceA {}
  ```

注：arkts 只允许对一个实体使用 export default，请用户不要在一个 package 里面多次使用该注解

## 第二步：生成文件

**File: `generated/export_pkg.ets`**
```typescript
export default namespace export_ns { // export default
    export interface Inner {
        i: int;
        s: string;
    }
    class Inner_inner implements Inner {
        i: int;
        s: string;
        constructor(i: int, s: string) {
            this.i = i;
            this.s = s;
        }
    }
}
```

我们可以看到生成文件里面添加了 `export default`

## 第三步：在 ets 侧使用

```typescript
import {BusinessError} from "@ohos.base";
// 注：ets 里导入一个 export default 只能使用 import x from y，不可以使用 import * as X from y
import export_ns from "export_pkg";
import {testImport} from "import_example";

loadLibrary("export_default");

function main() {
    let obj: export_ns.Inner = {i: 1, s: "str"};
    testImport(obj);
}
```

Output：
```sh
obj.str= str, obj.int= 1
```