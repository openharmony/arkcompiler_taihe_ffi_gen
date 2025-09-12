#include "bigint_test.impl.hpp"
#include <iostream>
#include "bigint_test.proj.hpp"

namespace {

::taihe::array<uint64_t> processBigInt(::taihe::array_view<uint64_t> a) {
  ::taihe::array<uint64_t> res(a.size() + 1);
  res[0] = 0;
  for (int i = 0; i < a.size(); i++) {
    res[i + 1] = a[i];
    std::cout << "arr[" << i << "] = " << a[i] << std::endl;
  }
  return res;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_processBigInt(processBigInt);
// NOLINTEND
