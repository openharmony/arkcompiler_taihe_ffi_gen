#include "arrbuffer.impl.hpp"
#include "stdexcept"
#include "core/array.hpp"
#include "core/runtime.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
int32_t convert2Int(array_view<uint8_t> a) {
    int32_t num = 0;
    if (a.size() >= 4) { 
        num = *(int32_t*)a.begin();
    } else {
        throw_error("ArrayBuffer len < 4");
    }
    return num;
}
}
TH_EXPORT_CPP_API_convert2Int(convert2Int)
