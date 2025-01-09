#include "integer.arithmetic.impl.hpp"

integer::arithmetic::i32Pair ohos_int_divmod(int32_t a, int32_t b) {
    return {
        a / b,
        a % b,
    };
}

TH_EXPORT_CPP_API_divmod_i32(ohos_int_divmod)
