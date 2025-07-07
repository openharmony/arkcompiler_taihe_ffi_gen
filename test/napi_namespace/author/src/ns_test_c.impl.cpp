#include "ns_test_c.impl.hpp"
#include "ns_test_c.proj.hpp"

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

::ns_test_c::IBase makeIBase(::taihe::string_view id) {
  return taihe::make_holder<Base, ::ns_test_c::IBase>(id);
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_makeIBase(makeIBase);
// NOLINTEND
