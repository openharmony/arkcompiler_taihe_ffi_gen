#include "foo.impl.hpp"
#include "stdexcept"
#include "taihe/array.hpp"
#include "taihe/runtime.hpp"
using namespace taihe;

namespace {
void inArrayBuffer(array_view<uint16_t> v) {
  std::cout << "inArrayBuffer:" << std::endl;
  int i = 0;
  for (auto x : v) {
    std::cout << "v[" << i << "] = " << x << std::endl;
  }
}

array<uint16_t> outArrayBuffer() {
  return {0, 1, 2, 3};
}
}  // namespace

TH_EXPORT_CPP_API_inArrayBuffer(inArrayBuffer);
TH_EXPORT_CPP_API_outArrayBuffer(outArrayBuffer);
