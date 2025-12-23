#include "typedarray.impl.hpp"
#include <iostream>
#include "stdexcept"
#include "taihe/runtime.hpp"
#include "typedarray.proj.hpp"

using namespace taihe;

namespace {
array<uint16_t> createUint16Array() {
  return {1, 3, 5, 6, 9};
}

void printUint16Array(array_view<uint16_t> arr) {
  size_t i = 0;
  for (uint16_t val : arr) {
    std::cout << "Index: " << i++ << " Value: " << val << std::endl;
  }
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_createUint16Array(createUint16Array);
TH_EXPORT_CPP_API_printUint16Array(printUint16Array);
// NOLINTEND
