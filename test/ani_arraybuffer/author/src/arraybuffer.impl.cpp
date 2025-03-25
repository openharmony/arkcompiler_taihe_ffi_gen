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
int8_t sumArrayi8(array_view<int8_t> nums) {
  return std::accumulate(nums.begin(), nums.end(), 0);
}
array<int8_t> getArrayi8(int8_t nums) {
  array<int8_t> result = array<int8_t>::make(nums);
  std::fill(result.begin(), result.end(), nums);
  return result;
}
array<int8_t> doublei8(array_view<int8_t> nums) {
  array<int8_t> result = array<int8_t>::make(nums.size());
  for (int i = 0; i < nums.size(); i++) {
    result[i] = nums[i] * 2;
  }
  return result;
}
int16_t sumArrayi16(array_view<int16_t> nums) {
  return std::accumulate(nums.begin(), nums.end(), 0);
}
array<int16_t> getArrayi16(int16_t nums) {
  array<int16_t> result = array<int16_t>::make(nums);
  std::fill(result.begin(), result.end(), nums);
  return result;
}
array<int16_t> doublei16(array_view<int16_t> nums) {
  array<int16_t> result = array<int16_t>::make(nums.size());
  for (int i = 0; i < nums.size(); i++) {
    result[i] = nums[i] * 2;
  }
  return result;
}
int32_t sumArrayi32(array_view<int32_t> nums) {
  return std::accumulate(nums.begin(), nums.end(), 0);
}
array<int32_t> getArrayi32(int32_t nums) {
  array<int32_t> result = array<int32_t>::make(nums);
  std::fill(result.begin(), result.end(), nums);
  return result;
}
array<int32_t> doublei32(array_view<int32_t> nums) {
  array<int32_t> result = array<int32_t>::make(nums.size());
  for (int i = 0; i < nums.size(); i++) {
    result[i] = nums[i] * 2;
  }
  return result;
}
int64_t sumArrayi64(array_view<int64_t> nums) {
  return std::accumulate(nums.begin(), nums.end(), 0);
}
array<int64_t> getArrayi64(int64_t nums) {
  array<int64_t> result = array<int64_t>::make(nums);
  std::fill(result.begin(), result.end(), nums);
  return result;
}
array<int64_t> doublei64(array_view<int64_t> nums) {
  array<int64_t> result = array<int64_t>::make(nums.size());
  for (int i = 0; i < nums.size(); i++) {
    result[i] = nums[i] * 2;
  }
  return result;
}
float sumArrayf32(array_view<float> nums) {
  return std::accumulate(nums.begin(), nums.end(), 0);
}
array<float> getArrayf32(float nums) {
  array<float> result = array<float>::make(nums);
  std::fill(result.begin(), result.end(), nums);
  return result;
}
array<float> doublef32(array_view<float> nums) {
  array<float> result = array<float>::make(nums.size());
  for (int i = 0; i < nums.size(); i++) {
    result[i] = nums[i] * 2;
  }
  return result;
}
double sumArrayf64(array_view<double> nums) {
  return std::accumulate(nums.begin(), nums.end(), 0);
}
array<double> getArrayf64(double nums) {
  array<double> result = array<double>::make(nums);
  std::fill(result.begin(), result.end(), nums);
  return result;
}
array<double> doublef64(array_view<double> nums) {
  array<double> result = array<double>::make(nums.size());
  for (int i = 0; i < nums.size(); i++) {
    result[i] = nums[i] * 2;
  }
  return result;
}
}  // namespace

TH_EXPORT_CPP_API_sumArrayu8(sumArrayu8);
TH_EXPORT_CPP_API_getArrayBuffer(getArrayBuffer);
TH_EXPORT_CPP_API_doubleArrayBuffer(doubleArrayBuffer);
TH_EXPORT_CPP_API_sumArrayi8(sumArrayi8);
TH_EXPORT_CPP_API_getArrayi8(getArrayi8);
TH_EXPORT_CPP_API_doublei8(doublei8);
TH_EXPORT_CPP_API_sumArrayi16(sumArrayi16);
TH_EXPORT_CPP_API_getArrayi16(getArrayi16);
TH_EXPORT_CPP_API_doublei16(doublei16);
TH_EXPORT_CPP_API_sumArrayi32(sumArrayi32);
TH_EXPORT_CPP_API_getArrayi32(getArrayi32);
TH_EXPORT_CPP_API_doublei32(doublei32);
TH_EXPORT_CPP_API_sumArrayi64(sumArrayi64);
TH_EXPORT_CPP_API_getArrayi64(getArrayi64);
TH_EXPORT_CPP_API_doublei64(doublei64);
TH_EXPORT_CPP_API_sumArrayf32(sumArrayf32);
TH_EXPORT_CPP_API_getArrayf32(getArrayf32);
TH_EXPORT_CPP_API_doublef32(doublef32);
TH_EXPORT_CPP_API_sumArrayf64(sumArrayf64);
TH_EXPORT_CPP_API_getArrayf64(getArrayf64);
TH_EXPORT_CPP_API_doublef64(doublef64);