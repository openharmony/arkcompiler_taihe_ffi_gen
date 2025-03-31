#include "ns_test.foo.bar.impl.hpp"

#include "core/string.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe;
namespace {

int32_t add(int32_t a, int32_t b) { return a + b; }

}  // namespace

TH_EXPORT_CPP_API_add(add);
