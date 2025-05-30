#include "iface_test.impl.hpp"
#include "iface_test.proj.hpp"

namespace {

class Base {
protected:
  ::taihe::string id;

public:
  Base(::taihe::string_view id) : id(id) {
    std::cout << "new " << this << std::endl;
  }

  ~Base() {
    std::cout << "del " << this << std::endl;
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
    std::cout << "new " << this << std::endl;
  }

  ~Shape() {
    std::cout << "del " << this << std::endl;
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

::iface_test::IBase makeIBase(::taihe::string_view id) {
  return make_holder<Base, ::iface_test::IBase>(id);
}

void copyIBase(::iface_test::weak::IBase a, ::iface_test::weak::IBase b) {
  a->setId(b->getId());
  return;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_makeIBase(makeIBase);
TH_EXPORT_CPP_API_copyIBase(copyIBase);
// NOLINTEND
