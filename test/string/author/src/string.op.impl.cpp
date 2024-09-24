#include "string.op.impl.hpp"

using namespace taihe::core;

std::tuple<string, string> ohos_split_str(string_view pstr, int32_t n) {
    int32_t l = pstr.size();
    if (n > l) {
        n = l;
    } else if (n + l < 0) {
        n = 0;
    } else if (n < 0) {
        n = n + l;
    }
    return {
        pstr.substr(0, n),
        pstr.substr(n, l - n),
    };
}

string ohos_int_to_str(int32_t n) {
    return to_string(n);
}

int32_t ohos_str_to_int(string_view pstr) {
    return std::atoi(pstr.c_str());
}

TH_EXPORT_CPP_API_split(ohos_split_str)
TH_EXPORT_CPP_API_to_i32(ohos_str_to_int)
TH_EXPORT_CPP_API_from_i32(ohos_int_to_str)
