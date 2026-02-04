# 多态

在面向对象编程中，多态是一个核心概念：我们可以把子类对象当作父类对象使用，并在需要时判断其实际类型或转换回子类。然而，在跨语言场景下，这个看似简单的需求面临特殊的挑战。

## 跨语言多态的挑战

在纯 ArkTS/TypeScript 代码中，我们可以通过 `instanceof` 来判断对象的实际类型：

```typescript
class Animal { /* ... */ }
class Dog extends Animal { /* ... */ }
class Cat extends Animal { /* ... */ }

function processAnimal(a: Animal) {
    if (a instanceof Dog) {
        // 处理 Dog
    } else if (a instanceof Cat) {
        // 处理 Cat
    }
}

// 创建一个 Dog 对象并将其作为 Animal 传递
processAnimal(new Dog());  // ✅ 正确识别这是一只 Dog
```

但当我们需要**在 ArkTS 和 C++ 之间传递对象**时，情况就变得复杂了。

```typescript
// 假设 IDL 中声明了：function nativeProcessAnimal(a: Animal): void;
// ArkTS 调用：
nativeProcessAnimal(new Dog());  // ❌ C++ 侧只能看到 Animal，无法识别是 Dog

// 假设 IDL 中声明了：function nativeCreateAnimal(idx: i32): Animal;
// C++ 返回一个 Dog 对象，但 ArkTS 收到的是：
console.log(nativeCreateAnimal(0) instanceof Dog);  // ❌ false - 类型信息已丢失
```

这是因为 Taihe 的工作原理是：根据 IDL 中声明的接口类型，在 ArkTS 和 C++ 之间进行数据转换。当一个函数的参数或返回值声明为 `Animal` 类型时，Taihe 只会按照 `Animal` 接口的定义来传递数据，子类特有的类型信息无法保留。

## 解决方案：使用 Union 实现类型安全的多态

Taihe 提供的**标签联合（Tagged Union）**类型可以被用来来解决这个问题。Union 会在传递数据时附带一个“标签”，明确标识当前是哪种具体类型，从而在跨语言边界时保留类型信息。

## 第一步：定义 IDL 接口

**File: `idl/poly.taihe`**

在 IDL 中，我们需要定义：
1. 接口的继承关系（`Dog`、`Cat` 继承自 `Animal`）
2. 一个 Union 类型，包含所有可能的具体类型
3. 使用 Union 类型作为函数参数和返回值

```rust
// 定义接口继承关系
interface Animal {
    speak(): void;
    move(): void;
}

@class
interface Dog: Animal {
    fetch(): void;
}

@class
interface Cat: Animal {
    fetch(): void;
}

// 关键：定义 Union 来包装所有可能的类型
union AnimalType {
    dog: Dog;
    cat: Cat;
    animal: Animal;  // 注意：基类需要写在最下面（见下方说明）
}

// 用于创建不同动物的标签
enum AnimalTag: i32 {
    ANIMAL = 0,
    DOG = 1,
    CAT = 2,
}

// 使用 Union 作为参数和返回值，保留类型信息
function getAnimal(tag: AnimalTag): AnimalType;
function interactAnimal(a: AnimalType): void;
```

> **⚠️ Union 成员顺序很重要**
>
> 在 ArkTS 侧，Union 类型会被投影为 TypeScript 的联合类型（Sum Type）。当 ArkTS 向 C++ 传递数据时，Taihe 会按照 Union 成员的**声明顺序**依次尝试匹配类型。如果把基类 `Animal` 写在前面，子类对象会优先匹配到基类，导致类型信息丢失。因此，**始终将基类放在 Union 定义的最后**。

下面是一个使用 `struct` 继承的类似示例：

```rust
// struct 继承示例
struct Person {
    name: String;
    age: i32;
}

struct Worker {
    @extends person: Person;
    service_len: i32;
}

struct Student {
    @extends person: Person;
    rank: i32;
}

union PersonType {
    worker: Worker;
    student: Student;
    person: Person;  // 基类写在最下面
}

enum PersonTag: i32 {
    PERSON = 0,
    WORKER = 1,
    STUDENT = 2,
}

function getPerson(tag: PersonTag, name: String, age: i32): PersonType;
function introduceYourself(p: PersonType): void;
```

继承关系如下：

```
    Animal                Person
    /    \                /    \
  Dog    Cat         Worker  Student
```

## 第二步：实现 C++ 接口

**File: `author/src/poly.impl.cpp`**

在 C++ 侧，需要为每个接口类型提供实现类，并通过 Union 的工厂方法来创建和识别不同类型。

```cpp
// 接口实现类
class AnimalImpl {
public:
    void speak() { std::cout << "Animal Speak" << std::endl; }
    void move() { std::cout << "Animal Move" << std::endl; }
};

class DogImpl {
public:
    void fetch() { std::cout << "Dog Fetch" << std::endl; }
    void speak() { std::cout << "Dog Speak" << std::endl; }
    void move() { std::cout << "Dog Move" << std::endl; }
};

class CatImpl {
public:
    void fetch() { std::cout << "Cat Fetch" << std::endl; }
    void speak() { std::cout << "Cat Speak" << std::endl; }
    void move() { std::cout << "Cat Move" << std::endl; }
};
```

### 创建 Union 对象

使用 `AnimalType::make_xxx()` 工厂方法创建带有正确标签的 Union 对象：

```cpp
::poly::AnimalType getAnimal(::poly::AnimalTag tag) {
    switch (tag.get_key()) {
    case ::poly::AnimalTag::key_t::ANIMAL:
        // 使用 make_animal 创建 Animal 类型的 Union
        return ::poly::AnimalType::make_animal(
            taihe::make_holder<AnimalImpl, ::poly::Animal>());
    case ::poly::AnimalTag::key_t::DOG:
        // 使用 make_dog 创建 Dog 类型的 Union
        return ::poly::AnimalType::make_dog(
            taihe::make_holder<DogImpl, ::poly::Dog>());
    case ::poly::AnimalTag::key_t::CAT:
        // 使用 make_cat 创建 Cat 类型的 Union
        return ::poly::AnimalType::make_cat(
            taihe::make_holder<CatImpl, ::poly::Cat>());
    }
}
```

### 识别 Union 中的实际类型

使用 `get_tag()` 获取标签，再用对应的 `get_xxx_ref()` 方法取出具体类型的对象：

```cpp
void interactAnimal(::poly::AnimalType const &a) {
    switch (a.get_tag()) {
    case ::poly::AnimalType::tag_t::animal:
        std::cout << "Unknown Animal" << std::endl;
        a.get_animal_ref()->speak();
        a.get_animal_ref()->move();
        break;
    case ::poly::AnimalType::tag_t::dog:
        std::cout << "It's a dog" << std::endl;
        // 可以调用父类方法
        ::poly::Animal(a.get_dog_ref())->speak();
        ::poly::Animal(a.get_dog_ref())->move();
        // 也可以调用子类特有的方法
        a.get_dog_ref()->fetch();
        break;
    case ::poly::AnimalType::tag_t::cat:
        std::cout << "It's a cat" << std::endl;
        ::poly::Animal(a.get_cat_ref())->speak();
        ::poly::Animal(a.get_cat_ref())->move();
        a.get_cat_ref()->fetch();
        break;
    }
}
```

### struct 继承的处理方式类似

对于 struct 类型的 Union，处理方式基本相同：

```cpp
::poly::PersonType getPerson(::poly::PersonTag tag, ::taihe::string_view name,
                             int32_t age) {
    switch (tag.get_key()) {
    case ::poly::PersonTag::key_t::PERSON: {
        ::poly::Person person{name, age};
        return ::poly::PersonType::make_person(person);
    }
    case ::poly::PersonTag::key_t::WORKER: {
        ::poly::Worker worker{{name, age}, 12};
        return ::poly::PersonType::make_worker(worker);
    }
    case ::poly::PersonTag::key_t::STUDENT: {
        ::poly::Student student{{name, age}, 1};
        return ::poly::PersonType::make_student(student);
    }
    }
}

void introduceYourself(::poly::PersonType const &p) {
    switch (p.get_tag()) {
    case ::poly::PersonType::tag_t::person:
        std::cout << "My name is " << p.get_person_ref().name 
                  << " and my age is " << p.get_person_ref().age << std::endl;
        break;
    case ::poly::PersonType::tag_t::worker:
        std::cout << "My name is " << p.get_worker_ref().person.name
                  << " and my age is " << p.get_worker_ref().person.age << std::endl;
        std::cout << "I'm a worker, and have worked for "
                  << p.get_worker_ref().service_len << " years" << std::endl;
        break;
    case ::poly::PersonType::tag_t::student:
        std::cout << "My name is " << p.get_student_ref().person.name
                  << " and my age is " << p.get_student_ref().person.age << std::endl;
        std::cout << "I'm a student, and grade ranking: "
                  << p.get_student_ref().rank << std::endl;
        break;
    }
}
```

## 第三步：在 ArkTS 侧调用

编译并运行示例：

```sh
taihe-tryit test -u sts cookbook/polymorphism -Csts:keep-name
```

**File: `user/main.ets`**

```typescript
// 创建不同类型的动物
let unknownObj = poly.getAnimal(poly.AnimalTag.ANIMAL);
let dogObj = poly.getAnimal(poly.AnimalTag.DOG);
let catObj = poly.getAnimal(poly.AnimalTag.CAT);

// Union 类型在跨语言传递时保留了具体类型信息
poly.interactAnimal(unknownObj);
poly.interactAnimal(dogObj);
poly.interactAnimal(catObj);

// struct 继承示例
let unknownPer = poly.getPerson(poly.PersonTag.PERSON, "Mike", 18);
let workerPer = poly.getPerson(poly.PersonTag.WORKER, "Tom", 30);
let studentPer = poly.getPerson(poly.PersonTag.STUDENT, "jimmy", 20);

poly.introduceYourself(unknownPer);
poly.introduceYourself(workerPer);
poly.introduceYourself(studentPer);
```

**输出结果：**

```
Unknown Animal
Animal Speak
Animal Move
It's a dog
Dog Speak
Dog Move
Dog Fetch
It's a cat
Cat Speak
Cat Move
Cat Fetch
My name is Mike and my age is 18
My name is Tom and my age is 30
I'm a worker, and have worked for 12 years
My name is jimmy and my age is 20
I'm a student, and grade ranking: 1
```

## 总结

| 场景 | 推荐方案 |
|------|----------|
| 只需调用接口方法，不关心具体类型 | 直接使用 interface 继承 |
| 需要在跨语言边界识别或转换具体类型 | 使用 Union 包装所有可能的类型 |

使用 Union 实现多态的要点：

1. **定义 Union 类型**：将所有可能的具体类型作为成员，基类放在最后
2. **创建时使用工厂方法**：如 `AnimalType::make_dog(...)` 来附带正确的类型标签
3. **使用时检查标签**：通过 `get_tag()` 判断类型，用 `get_xxx_ref()` 获取具体对象

---

## 相关文档

- [继承](../inherit/README.md) - 接口继承
- [多继承](../multiple_inherit/README.md) - 多接口继承
- [Enum 与 Union](../enum_union/README.md) - Union 详细用法
