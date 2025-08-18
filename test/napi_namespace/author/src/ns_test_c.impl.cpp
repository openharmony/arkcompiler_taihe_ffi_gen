#include <iostream>
#include "my_module_b.functiontest.impl.hpp"
#include "my_module_b.functiontest.proj.hpp"

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

::my_module_b::functiontest::IBase makeIBase(::taihe::string_view id) {
  return taihe::make_holder<Base, ::my_module_b::functiontest::IBase>(id);
}

void bar() {
  std::cout << "namespace: my_module_b.functiontest, func: bar" << std::endl;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_makeIBase(makeIBase);
TH_EXPORT_CPP_API_bar(bar);
// NOLINTEND
