#include "integer.arithmetic.impl.h"

int32_t ohos_int_add(int32_t a, int32_t b) {
    return a + b;
}

int32_t ohos_int_sub(int32_t a, int32_t b) {
    return a - b;
}

TH_EXPORT_C_API_add_i32(ohos_int_add)
TH_EXPORT_C_API_sub_i32(ohos_int_sub)
