#include "array_ani.impl.hpp"
#include "stdexcept"
// Please delete this include when you implement

#include <numeric>

using namespace taihe::core;
namespace {

int32_t sumArray(array_view<int32_t> nums, int32_t base) {
    return std::accumulate(nums.begin(), nums.end(), base);
}

int32_t getArrayValue(array_view<int32_t> nums, int32_t idx) {
    if (idx >= 0 && idx < nums.size()) {
        return nums[idx];
    }
    throw std::runtime_error("Index out of range");
}

array<int32_t> makeArray(int32_t value, int32_t num) {
    array<int32_t> result = array<int32_t>::make(num);
    std::fill(result.begin(), result.end(), value);
    return result;
}

}

TH_EXPORT_CPP_API_sumArray(sumArray)
TH_EXPORT_CPP_API_getArrayValue(getArrayValue)
TH_EXPORT_CPP_API_makeArray(makeArray)
