#include "overload.impl.hpp"
#include "stdexcept"
#include "core/array.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
int32_t sum_two(int32_t a, int32_t b) {
    return a + b;
}
int32_t sum_arr(array_view<int32_t> a) {
    if (a.size() == 0) return 0;
    int32_t result = 0;
    for (int i = 0; i < a.size(); ++i) {
        result += a[i];
    }
    return result;
}
}
TH_EXPORT_CPP_API_sum_two(sum_two);
TH_EXPORT_CPP_API_sum_arr(sum_arr);
