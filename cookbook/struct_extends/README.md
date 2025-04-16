# Struct 继承

Taihe 的 `sturct` 为值类型，不支持继承，我们提供 `@extends` 注解，以组合的方式实现继承

## 第一步：编写接口原型

**File: `idl/structext.taihe`**
```taihe
struct Position {
    x: i32;
    y: i32;
    z: i32;
}

@class
struct Player {
    @extends pos: Position;
    name: String;
}

function addNewPlayer(name: String): Player; 
```

1. 上面的例子中，使用 `@extends` 注解将 Postion 以组合的方式实现 Player 类继承 Postion 类

2. Taihe 的 `struct Player` 默认在 sts侧 生成的是 `interface Player`（用于接受 ArkTS 用户的传入）和 `class Player_inner implements Player`（用于 C++ 返回值的传出）。可以使用 `@class` 规避 `interface Player`，直接生成 `class Player` 保证 ArkTS 的兼容性

我们可以看到在 sts 侧对应生成的 Player 为：

```typescript
export class Player implements Position {
    x: int;
    y: int;
    z: int;
    name: string;
    constructor(
        x: int,
        y: int,
        z: int,
        name: string,
    ) {
        this.x = x;
        this.y = y;
        this.z = z;
        this.name = name;
    }
}
```

## 第二步: 完成 C++ 实现

```C++
Player addNewPlayer(string_view name) {
    return {{0, 0, 0}, name};
}
```

在 C++ 侧，可以把 `Player` 类像 `struct` 一样处理

## 第三步：在 ets 侧使用

```typescript
let Player1 = structext.addNewPlayer("Tom");
let Player2 = structext.addNewPlayer("Jimmy");
console.log("Player1's name is " + Player1.name);
console.log("Player2's name is " + Player2.name);
Player2.x += 1;
Player2.y += 1;
Player2.z += 1;
console.log("Player1's position is " + Player1.x + "," + Player1.y + "," + Player1.z);
console.log("Player2's position is " + Player2.x + "," + Player2.y + "," + Player2.z);
```

需要注意的是，使用时使用的是 `Player1.x` 而非 `Player1.Position.x`

Output:
```sh
Player1's name is Tom
Player2's name is Jimmy
Player1's position is 0,0,0
Player2's position is 1,1,1
```