#include <iostream>
#include "my_module_a.ns1.impl.hpp"
#include "my_module_a.ns1.proj.hpp"

namespace {
::taihe::string Funtest(::my_module_a::ns1::Color s) {
  switch (s.get_key()) {
  case ::my_module_a::ns1::Color::key_t::BLUE:
    return "blue";
  case ::my_module_a::ns1::Color::key_t::GREEN:
    return "green";
  case ::my_module_a::ns1::Color::key_t::RED:
    return "red";
  }
  return "error";
}

void noo() {
  std::cout << "namespace: my_module_a.ns1, func: noo" << std::endl;
}

class Base {
protected:
  ::taihe::string id;

public:
  Base(::taihe::string_view id) : id(id) {
    std::cout << "new base " << this << std::endl;
  }

  ~Base() {
    std::cout << "del base " << this << std::endl;
  }

  ::taihe::string getId() {
    return id;
  }

  void setId(::taihe::string_view s) {
    id = s;
    return;
  }
};

::my_module_a::ns1::IBase makeIBase(::taihe::string_view id) {
  return taihe::make_holder<Base, ::my_module_a::ns1::IBase>(id);
}

void bar() {
  std::cout << "namespace: my_module_b.functiontest, func: bar" << std::endl;
}

class CTestImpl {
  int32_t x;

public:
  CTestImpl(int32_t x) : x(x) {
    std::cout << "new ctest " << this->x << std::endl;
  }

  ~CTestImpl() {
    std::cout << "del ctest " << this << std::endl;
  }

  float add(int32_t a, int32_t b) {
    return a + b + this->x;
  }
};

::my_module_a::ns1::CTest createCTest(int32_t id) {
  return taihe::make_holder<CTestImpl, ::my_module_a::ns1::CTest>(id);
}

::my_module_a::ns1::CTest changeCTest(::my_module_a::ns1::weak::CTest a) {
  int32_t x = a->add(3, 4);
  return taihe::make_holder<CTestImpl, ::my_module_a::ns1::CTest>(x);
}

int32_t multiply(int32_t a, int32_t b) {
  return a * b;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_Funtest(Funtest);
TH_EXPORT_CPP_API_noo(noo);
TH_EXPORT_CPP_API_makeIBase(makeIBase);
TH_EXPORT_CPP_API_bar(bar);
TH_EXPORT_CPP_API_createCTest(createCTest);
TH_EXPORT_CPP_API_changeCTest(changeCTest);
TH_EXPORT_CPP_API_multiply(multiply);
// NOLINTEND
