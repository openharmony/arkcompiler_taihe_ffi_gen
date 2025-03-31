#include "new_ns.my_ns.impl.hpp"

#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
int32_t myfunc2(int32_t a, int32_t b) {
  return a + b;
}
}  // namespace

TH_EXPORT_CPP_API_myfunc2(myfunc2);
