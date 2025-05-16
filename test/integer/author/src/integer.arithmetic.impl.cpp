#include "integer.arithmetic.impl.hpp"

int32_t ohos_int_add(int32_t a, int32_t b) {
  return a + b;
}

int32_t ohos_int_sub(int32_t a, int32_t b) {
  return a - b;
}

int32_t ohos_int_mul(int32_t a, int32_t b) {
  return a * b;
}

integer::arithmetic::i32Pair ohos_int_divmod(int32_t a, int32_t b) {
  return {
      a / b,
      a % b,
  };
}

TH_EXPORT_CPP_API_add_i32(ohos_int_add);
TH_EXPORT_CPP_API_sub_i32(ohos_int_sub);
TH_EXPORT_CPP_API_mul_i32(ohos_int_mul);
TH_EXPORT_CPP_API_divmod_i32(ohos_int_divmod);
