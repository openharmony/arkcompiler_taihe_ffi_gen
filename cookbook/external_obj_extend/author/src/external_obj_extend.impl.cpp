#include "external_obj_extend.impl.hpp"
#include "external_obj_extend.proj.hpp"
#include "taihe/runtime.hpp"

namespace {
class MyContext_innerImpl {
public:
  MyContext_innerImpl() {}

  ::taihe::string start() {
    return "MyContext start";
  }

  ::taihe::string stop() {
    return "MyContext stop";
  }
};

::external_obj_extend::MyContext_inner createMyContext_inner() {
  return taihe::make_holder<MyContext_innerImpl,
                            ::external_obj_extend::MyContext_inner>();
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_createMyContext_inner(createMyContext_inner);
// NOLINTEND
