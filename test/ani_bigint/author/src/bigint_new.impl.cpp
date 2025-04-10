#include "bigint_new.impl.hpp"
#include <cstdint>
#include "bigint_new.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

#include <iostream>

using namespace taihe;

namespace {
// To be implemented.

array<uint64_t> processBigInt(array_view<uint64_t> a) {
  array<uint64_t> res(a.size() + 1);
  res[0] = 0;
  for (int i = 0; i < a.size(); i++) {
    res[i + 1] = a[i];
    std::cerr << "arr[" << i << "] = " << a[i] << std::endl;
  }
  return res;
}
}  // namespace

TH_EXPORT_CPP_API_processBigInt(processBigInt);
