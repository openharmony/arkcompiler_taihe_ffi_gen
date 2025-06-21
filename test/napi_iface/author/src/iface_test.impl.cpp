#include "iface_test.impl.hpp"
#include <iostream>
#include "iface_test.proj.hpp"

namespace {

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

class Shape {
protected:
  ::taihe::string id;
  float a;
  float b;

public:
  Shape(::taihe::string_view id, float a, float b) : id(id), a(a), b(b) {
    std::cout << "new shape " << this << std::endl;
  }

  ~Shape() {
    std::cout << "del shape " << this << std::endl;
  }

  ::taihe::string getId() {
    return id;
  }

  void setId(::taihe::string_view s) {
    id = s;
    return;
  }

  float calculateArea() {
    return a * b;
  }
};

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

::iface_test::IBase makeIBase(::taihe::string_view id) {
  return make_holder<Base, ::iface_test::IBase>(id);
}

void copyIBase(::iface_test::weak::IBase a, ::iface_test::weak::IBase b) {
  a->setId(b->getId());
  return;
}

::iface_test::IShape makeIShape(::taihe::string_view id, double a, double b) {
  return ::taihe::make_holder<Shape, ::iface_test::IShape>(id, a, b);
}

::iface_test::CTest createCTest(int32_t id) {
  return taihe::make_holder<CTestImpl, ::iface_test::CTest>(id);
}

::iface_test::CTest changeCTest(::iface_test::weak::CTest a) {
  int32_t x = a->add(3, 4);
  return taihe::make_holder<CTestImpl, ::iface_test::CTest>(x);
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_makeIBase(makeIBase);
TH_EXPORT_CPP_API_copyIBase(copyIBase);
TH_EXPORT_CPP_API_makeIShape(makeIShape);
TH_EXPORT_CPP_API_createCTest(createCTest);
TH_EXPORT_CPP_API_changeCTest(changeCTest);
// NOLINTEND
