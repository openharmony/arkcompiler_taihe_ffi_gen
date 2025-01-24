#include "string.impl.hpp"

taihe::core::string ohos_concat_str(taihe::core::string_view a, taihe::core::string_view b) {
    return concat(a, b);
}

taihe::core::string ohos_int_to_str(int32_t n) {
    return taihe::core::to_string(n);
}

int32_t ohos_str_to_int(taihe::core::string_view pstr) {
    return std::atoi(pstr.c_str());
}

TH_EXPORT_CPP_API_concat(ohos_concat_str)
TH_EXPORT_CPP_API_to_i32(ohos_str_to_int)
TH_EXPORT_CPP_API_from_i32(ohos_int_to_str)
