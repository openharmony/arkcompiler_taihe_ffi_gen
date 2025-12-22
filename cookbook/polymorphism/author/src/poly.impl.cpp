/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "poly.impl.hpp"
#include <iostream>
#include "poly.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
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
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_makeAnimal(makeAnimal);
TH_EXPORT_CPP_API_makeDog(makeDog);
TH_EXPORT_CPP_API_makeCat(makeCat);
TH_EXPORT_CPP_API_getAnimal(getAnimal);
TH_EXPORT_CPP_API_interactAnimal(interactAnimal);
TH_EXPORT_CPP_API_getPerson(getPerson);
TH_EXPORT_CPP_API_introduceYourself(introduceYourself);
// NOLINTEND
