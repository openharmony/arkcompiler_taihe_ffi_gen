#include "hello_world.impl.hpp"

#include "core/string.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {

string add(int32_t a, int32_t b) {
  std::string sum = std::to_string(a + b);
  return sum;
}

}  // namespace

TH_EXPORT_CPP_API_add(add);
