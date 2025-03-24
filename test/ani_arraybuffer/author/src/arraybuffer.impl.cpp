#include "arraybuffer.impl.hpp"

#include <numeric>
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
uint8_t sumArrayu8(array_view<uint8_t> nums) {
  return std::accumulate(nums.begin(), nums.end(), 0);
}
array<uint8_t> getArrayBuffer(uint8_t nums) {
  array<uint8_t> result = array<uint8_t>::make(nums);
  std::fill(result.begin(), result.end(), nums);
  return result;
}
array<uint8_t> doubleArrayBuffer(array_view<uint8_t> nums) {
  array<uint8_t> result = array<uint8_t>::make(nums.size());
  for (int i = 0; i < nums.size(); i++) {
    result[i] = nums[i] * 2;
  }
  return result;
}

}  // namespace

TH_EXPORT_CPP_API_sumArrayu8(sumArrayu8)
    TH_EXPORT_CPP_API_getArrayBuffer(getArrayBuffer)
        TH_EXPORT_CPP_API_doubleArrayBuffer(doubleArrayBuffer)
