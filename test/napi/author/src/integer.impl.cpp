#include "integer.impl.hpp"

int32_t ohos_int_add(int32_t a, int32_t b) {
    return a + b;
}

int32_t ohos_int_sub(int32_t a, int32_t b) {
    return a - b;
}

int32_t ohos_int_mul(int32_t a, int32_t b) {
    return a * b;
}

TH_EXPORT_CPP_API_add(ohos_int_add)
TH_EXPORT_CPP_API_mul(ohos_int_mul)
