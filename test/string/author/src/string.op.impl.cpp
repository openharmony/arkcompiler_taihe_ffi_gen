#include "string.op.impl.hpp"

using namespace taihe::core;

std::tuple<string, string> ohos_split_str(string &pstr, int32_t n) {
    string const &tstr = pstr;
    int32_t l = tstr.size();
    if (n > l) {
        n = l;
    } else if (n + l < 0) {
        n = 0;
    } else if (n < 0) {
        n = n + l;
    }
    return {
        tstr.substr(0, n),
        tstr.substr(n, l - n),
    };
}

string ohos_int_to_str(int32_t n) {
    return to_string(n);
}

int32_t ohos_str_to_int(string &pstr) {
    return std::atoi(pstr.c_str());
}

TH_EXPORT_CPP_API_split(ohos_split_str)
TH_EXPORT_CPP_API_to_i32(ohos_str_to_int)
TH_EXPORT_CPP_API_from_i32(ohos_int_to_str)
