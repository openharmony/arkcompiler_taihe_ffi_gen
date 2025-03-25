#include "core/array.hpp"

#include "array_test.Color.proj.0.hpp"
#include "array_test.Data.proj.1.hpp"
#include "array_test.impl.hpp"
#include "core/map.hpp"
#include "core/string.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement

#include <algorithm>
#include <numeric>

using namespace taihe::core;
namespace {
int32_t sumArray(array_view<int32_t> nums, int32_t base) {
  return std::accumulate(nums.begin(), nums.end(), base);
}
int64_t getArrayValue(array_view<int64_t> nums, int32_t idx) {
  if (idx >= 0 && idx < nums.size()) {
    return nums[idx];
  }
  throw std::runtime_error("Index out of range");
}
array<string> toStingArray(array_view<int32_t> nums) {
  auto result = array<string>::make(nums.size(), "");
  std::transform(nums.begin(), nums.end(), result.begin(),
                 [](int32_t n) { return to_string(n); });
  return result;
}
array<int32_t> makeIntArray(int32_t value, int32_t num) {
  return array<int32_t>::make(num, value);
}
array<::array_test::Color> makeEnumArray(::array_test::Color value,
                                         int32_t num) {
  return array<::array_test::Color>::make(num, value);
}
array<map<string, int64_t>> makeRecordArray(string_view key, int64_t val,
                                            int32_t num) {
  map<string, int64_t> record;
  record.emplace(key, val);
  return array<map<string, int64_t>>::make(num, record);
}
array<::array_test::Data> makeStructArray(string_view a, string_view b,
                                          int32_t c, int32_t num) {
  return array<::array_test::Data>::make(num, ::array_test::Data{a, b, c});
}
}  // namespace
TH_EXPORT_CPP_API_sumArray(sumArray);
TH_EXPORT_CPP_API_getArrayValue(getArrayValue);
TH_EXPORT_CPP_API_toStingArray(toStingArray);
TH_EXPORT_CPP_API_makeIntArray(makeIntArray);
TH_EXPORT_CPP_API_makeEnumArray(makeEnumArray);
TH_EXPORT_CPP_API_makeRecordArray(makeRecordArray);
TH_EXPORT_CPP_API_makeStructArray(makeStructArray);
