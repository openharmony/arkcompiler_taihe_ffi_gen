#include "iface_readonly_test.impl.hpp"

#include "core/string.hpp"
#include "iface_readonly_test.Noo.proj.2.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
class Noo {
  string name_{"noo"};

 public:
  void bar() { std::cout << "Nooimpl: " << __func__ << std::endl; }
  string getName() {
    std::cout << "Nooimpl: " << __func__ << " " << name_ << std::endl;
    return name_;
  }
};
::iface_readonly_test::Noo getNooIface() {
  return make_holder<Noo, ::iface_readonly_test::Noo>();
}
string printNooName(::iface_readonly_test::weak::Noo noo) {
  auto name = noo->getName();
  std::cout << __func__ << ": " << name << std::endl;
  return name;
}
}  // namespace
TH_EXPORT_CPP_API_getNooIface(getNooIface);
TH_EXPORT_CPP_API_printNooName(printNooName);
