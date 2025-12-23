#include "hello_world.impl.hpp"

#include "stdexcept"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {

string add(int32_t a, int32_t b) {
  std::string sum = std::to_string(a + b);
  return sum;
}

}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_add(add);
// NOLINTEND
