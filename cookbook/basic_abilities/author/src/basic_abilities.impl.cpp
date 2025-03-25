#include "basic_abilities.impl.hpp"

#include "core/array.hpp"
#include "core/string.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {

array<string> convert_arr(array_view<int32_t> a, string_view str) {
  int32_t input_size = a.size();
  int32_t input_begin_val = a[0];
  int32_t input_end_val = a[input_size - 1];
  array<string> res = {{std::to_string(input_size)},
                       {std::to_string(input_begin_val)},
                       {std::to_string(input_end_val)},
                       str};
  return res;
}

}  // namespace

TH_EXPORT_CPP_API_convert_arr(convert_arr);
