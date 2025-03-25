#include "iface_test.impl.hpp"

#include "core/string.hpp"
#include "iface_test.Foo.proj.2.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {

class Foo {
  string name_{"foo"};

 public:
  void bar() { std::cout << "Fooimpl: " << __func__ << std::endl; }
  string getName() {
    std::cout << "Fooimpl: " << __func__ << " " << name_ << std::endl;
    return name_;
  }
  void setName(string_view name) {
    std::cout << "Fooimpl: " << __func__ << " " << name << std::endl;
    name_ = name;
  }
};

::iface_test::Foo getFooIface() {
  std::cout << __func__ << std::endl;
  return make_holder<Foo, ::iface_test::Foo>();
}
string printFooName(::iface_test::weak::Foo foo) {
  auto name = foo->getName();
  std::cout << __func__ << ": " << name << std::endl;
  return name;
}

}  // namespace

TH_EXPORT_CPP_API_getFooIface(getFooIface);
TH_EXPORT_CPP_API_printFooName(printFooName);
