#include "new_ns.impl.hpp"

#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
int32_t myfunc1(int32_t a, int32_t b) { return a + b; }
}  // namespace
TH_EXPORT_CPP_API_myfunc1(myfunc1)
