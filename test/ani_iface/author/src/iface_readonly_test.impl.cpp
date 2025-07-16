#include "iface_readonly_test.impl.hpp"

#include "iface_readonly_test.Noo.proj.2.hpp"
#include "taihe/string.hpp"
using namespace taihe;

namespace {
class Noo {
  string name_{"noo"};
  ::taihe::optional<int32_t> age_{::taihe::optional<int32_t>(std::in_place, 1)};

public:
  void Bar() {
    std::cout << "Nooimpl: " << __func__ << std::endl;
  }

  string GetName() {
    std::cout << "Nooimpl: " << __func__ << " " << name_ << std::endl;
    return name_;
  }

  ::taihe::optional<int32_t> GetAge() {
    return age_;
  }

  void SetAge(::taihe::optional_view<int32_t> a) {
    this->age_ = a;
    return;
  }
};

::iface_readonly_test::Noo GetNooIface() {
  return make_holder<Noo, ::iface_readonly_test::Noo>();
}

string PrintNooName(::iface_readonly_test::weak::Noo noo) {
  auto name = noo->GetName();
  std::cout << __func__ << ": " << name << std::endl;
  return name;
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_GetNooIface(GetNooIface);
TH_EXPORT_CPP_API_PrintNooName(PrintNooName);
// NOLINTEND