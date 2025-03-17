#include "container_example.impl.hpp"
#include "stdexcept"
#include "core/array.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {

array<int32_t> convert_arr(array_view<int32_t> a) {
    int32_t input_size = a.size();
    int32_t input_begin_val = a[0];
    int32_t input_end_val = a[input_size - 1];
    array<int32_t> res = { input_size, input_begin_val, input_end_val };
    return res;
}

}

TH_EXPORT_CPP_API_convert_arr(convert_arr)
