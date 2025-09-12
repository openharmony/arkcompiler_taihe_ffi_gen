#include "arraybuffer_test.impl.hpp"
#include <numeric>
#include "arraybuffer_test.proj.hpp"

namespace {
uint8_t SumArrayU8(::taihe::array_view<uint8_t> nums) {
  return std::accumulate(nums.begin(), nums.end(), 0);
}

::taihe::array<uint8_t> GetArrayBuffer(uint8_t nums) {
  ::taihe::array<uint8_t> result = ::taihe::array<uint8_t>::make(nums);
  std::fill(result.begin(), result.end(), nums);
  return result;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_SumArrayU8(SumArrayU8);
TH_EXPORT_CPP_API_GetArrayBuffer(GetArrayBuffer);
// NOLINTEND
