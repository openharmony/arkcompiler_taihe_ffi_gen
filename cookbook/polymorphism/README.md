# 多态

把子类对象当初父类对象使用是多态的常见场景，在 Taihe 里面使用 Union 来实现多态

## 第一步 在 taihe 文件中声明

`polymorphism/idl/poly.taihe`

```taihe
// interface 继承
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

function makeAnimal(): Animal;
function makeDog(): Dog;
function makeCat(): Cat;

enum AnimalTag: i32 {
    ANIMAL = 0,
    DOG = 1,
    CAT = 2,
}

union AnimalType {
    dog: Dog;
    cat: Cat;
    animal: Animal; // 基类需要写在最下面
}

function getAnimal(tag: AnimalTag): AnimalType;
function interactAnimal(a: AnimalType): void;

// struct extends 继承
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

enum PersonTag: i32 {
    PERSON = 0,
    WORKER = 1,
    STUDENT = 2,
}

union PersonType {
    worker: Worker;
    student: Student;
    person: Person; // 基类需要写在最下面
}

function getPerson(tag: PersonTag, name: String, age: i32): PersonType;
function introduceYourself(p: PersonType): void;
```

继承关系如下：
```
    Animal
    /  \
   Dog Cat

    Person
    /  \
Worker Student
```

## 第二步 实现声明的接口

`polymorphism/author/src/poly.impl.cpp`

```C++
class AnimalImpl {
public:
  AnimalImpl() {}

  void speak() {
    std::cout << "Animal Speak" << std::endl;
  }

  void move() {
    std::cout << "Animal Move" << std::endl;
  }
};

class DogImpl {
public:
  DogImpl() {}

  void fetch() {
    std::cout << "Dog Fetch" << std::endl;
  }

  void speak() {
    std::cout << "Dog Speak" << std::endl;
  }

  void move() {
    std::cout << "Dog Move" << std::endl;
  }
};

class CatImpl {
public:
  CatImpl() {}

  void fetch() {
    std::cout << "Cat Fetch" << std::endl;
  }

  void speak() {
    std::cout << "Cat Speak" << std::endl;
  }

  void move() {
    std::cout << "Cat Move" << std::endl;
  }
};

::poly::Animal makeAnimal() {
  return taihe::make_holder<AnimalImpl, ::poly::Animal>();
}

::poly::Dog makeDog() {
  return taihe::make_holder<DogImpl, ::poly::Dog>();
}

::poly::Cat makeCat() {
  return taihe::make_holder<CatImpl, ::poly::Cat>();
}

::poly::AnimalType getAnimal(::poly::AnimalTag tag) {
  switch (tag.get_key()) {
  case ::poly::AnimalTag::key_t::ANIMAL:
    return ::poly::AnimalType::make_animal(
        taihe::make_holder<AnimalImpl, ::poly::Animal>());
  case ::poly::AnimalTag::key_t::DOG:
    return ::poly::AnimalType::make_dog(
        taihe::make_holder<DogImpl, ::poly::Dog>());
  case ::poly::AnimalTag::key_t::CAT:
    return ::poly::AnimalType::make_cat(
        taihe::make_holder<CatImpl, ::poly::Cat>());
  }
}

void interactAnimal(::poly::AnimalType const &a) {
  switch (a.get_tag()) {
  case ::poly::AnimalType::tag_t::animal:
    std::cout << "Unknown Animal" << std::endl;
    a.get_animal_ref()->speak();
    a.get_animal_ref()->move();
    break;
  case ::poly::AnimalType::tag_t::dog:
    std::cout << "It's a dog" << std::endl;
    ::poly::Animal(a.get_dog_ref())->speak();
    ::poly::Animal(a.get_dog_ref())->move();
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
    std::cout << "My name is " << p.get_person_ref().name << " and my age is "
              << p.get_person_ref().age << std::endl;
    break;
  case ::poly::PersonType::tag_t::worker:
    std::cout << "My name is " << p.get_worker_ref().person.name
              << " and my age is " << p.get_worker_ref().person.age
              << std::endl;
    std::cout << "I'm a worker, and have worked for "
              << p.get_worker_ref().service_len << " years" << std::endl;
    break;
  case ::poly::PersonType::tag_t::student:
    std::cout << "My name is " << p.get_student_ref().person.name
              << " and my age is " << p.get_student_ref().person.age
              << std::endl;
    std::cout << "I'm a student, and grade ranking: "
              << p.get_student_ref().rank << std::endl;
    break;
  }
}
```

## 第三步 生成并编译

```sh
taihe-tryit test -u sts cookbook/polymorphism --sts-keep-name
```

`main.ets`
```TypeScript
    let unknownObj = poly.getAnimal(poly.AnimalTag.ANIMAL);
    let dogObj = poly.getAnimal(poly.AnimalTag.DOG);
    let catObj = poly.getAnimal(poly.AnimalTag.CAT);
    poly.interactAnimal(unknownObj);
    poly.interactAnimal(dogObj);
    poly.interactAnimal(catObj);

    let unknownPer = poly.getPerson(poly.PersonTag.PERSON, "Mike", 18);
    let workerPer = poly.getPerson(poly.PersonTag.WORKER, "Tom", 30);
    let studentPer = poly.getPerson(poly.PersonTag.STUDENT, "jimmy", 20);
    poly.introduceYourself(unknownPer);
    poly.introduceYourself(workerPer);
    poly.introduceYourself(studentPer);
```

```sh
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