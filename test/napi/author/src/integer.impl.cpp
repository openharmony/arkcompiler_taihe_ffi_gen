#include "integer.impl.hpp"

int32_t ohos_int_add(int32_t a, int32_t b) {
    return a + b;
}

int32_t ohos_int_mul(int32_t a, int32_t b) {
    if ( a * b > 20) {
        return true;
    } else {
        return false;
    }
}

float ohos_int_sub(float a, float b, bool c) {
    if (c) {
        return a - b;
    } else {
        return b;
    }
}

TH_EXPORT_CPP_API_add(ohos_int_add)
TH_EXPORT_CPP_API_mul(ohos_int_mul)
TH_EXPORT_CPP_API_sub(ohos_int_sub)
