#include "typedarray_test.impl.hpp"
#include <iostream>
#include <numeric>
#include "typedarray_test.proj.hpp"

namespace {

int8_t SumUint8Array(::taihe::array_view<uint8_t> v) {
  return std::accumulate(v.begin(), v.end(), 0);
}

::taihe::array<uint8_t> NewUint8Array(int64_t n, int8_t v) {
  ::taihe::array<uint8_t> result(n);
  std::fill(result.begin(), result.end(), v);
  return result;
}

float SumFloat32Array(::taihe::array_view<float> v) {
  return std::accumulate(v.begin(), v.end(), 0.0f);
}

::taihe::array<float> NewFloat32Array(int64_t n, float v) {
  ::taihe::array<float> result(n);
  std::fill(result.begin(), result.end(), v);
  return result;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_SumUint8Array(SumUint8Array);
TH_EXPORT_CPP_API_NewUint8Array(NewUint8Array);
TH_EXPORT_CPP_API_SumFloat32Array(SumFloat32Array);
TH_EXPORT_CPP_API_NewFloat32Array(NewFloat32Array);
// NOLINTEND
