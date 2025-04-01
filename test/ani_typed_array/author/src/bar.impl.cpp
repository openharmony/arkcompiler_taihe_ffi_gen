#include "bar.impl.hpp"
#include "stdexcept"
#include "taihe/array.hpp"
#include "taihe/runtime.hpp"
using namespace taihe;

namespace {
void inUint16Array(array_view<uint16_t> v) {
  std::cout << "inUint16Array:" << std::endl;
  int i = 0;
  for (auto x : v) {
    std::cout << "v[" << i << "] = " << x << std::endl;
  }
}

array<uint16_t> outUint16Array() {
  return {0, 1, 2, 3};
}
}  // namespace

TH_EXPORT_CPP_API_inUint16Array(inUint16Array);
TH_EXPORT_CPP_API_outUint16Array(outUint16Array);
