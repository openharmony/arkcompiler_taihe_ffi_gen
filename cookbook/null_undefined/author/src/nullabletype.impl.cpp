#include "nullabletype.impl.hpp"
#include "nullabletype.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

constexpr int32_t TAG_NULL = 0;
constexpr int32_t TAG_STRING = 1;
constexpr int32_t TAG_INT = 2;

::nullabletype::NullableValue makeNullableValue(int32_t tag) {
  switch (tag) {
  case TAG_NULL:
    return ::nullabletype::NullableValue::make_nValue();
  case TAG_STRING:
    return ::nullabletype::NullableValue::make_sValue("hello");
  case TAG_INT:
    return ::nullabletype::NullableValue::make_iValue(123);
  default:
    return ::nullabletype::NullableValue::make_uValue();
  }
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_makeNullableValue(makeNullableValue);
// NOLINTEND
