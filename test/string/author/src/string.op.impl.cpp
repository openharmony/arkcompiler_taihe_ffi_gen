#include "string.op.impl.hpp"

using namespace taihe::core;

std::tuple<string, string> ohos_split_str(param::string pstr, int32_t n) {
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

TH_EXPORT_CPP_API_split(ohos_split_str)
