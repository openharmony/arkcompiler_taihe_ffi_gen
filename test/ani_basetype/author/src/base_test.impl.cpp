#include "base_test.impl.hpp"

#include "core/runtime.hpp"
#include "stdexcept"
// Please delete this include when you implement
using namespace taihe::core;
namespace {

int8_t add_i8(int8_t a, int8_t b) { return a + b; }
int16_t sub_i16(int16_t a, int16_t b) { return a - b; }
int32_t mul_i32(int32_t a, int32_t b) { return a * b; }
int64_t div_i64(int64_t a, int64_t b) {
  if (b == 0) {
    taihe::core::set_error("some error happen");
    return -1;
  }
  return a / b;
}
float add_f32(float a, float b) { return a + b; }
float sub_f32(float a, float b) { return a - b; }
double add_f64(float a, double b) { return a + b; }
double sub_f64(float a, double b) { return a - b; }
double mul_f64(float a, float b) { return a * b; }
bool check(bool a, bool b) {
  if (a && b) {
    return true;
  }
  return false;
}
string concatx(string_view a, string_view b) {
  return taihe::core::concat(a, b);
}
string splitx(string_view a, int32_t n) {
  int32_t size = a.size();
  if (n >= size) {
    n = size;
  } else if (n < 0) {
    n = 0;
  }
  return taihe::core::substr(a, 0, n);
}
int32_t to_i32(string_view a) { return std::atoi(a.c_str()); }
string from_i32(int32_t a) { return taihe::core::to_string(a); }
}  // namespace

TH_EXPORT_CPP_API_add_i8(add_i8);
TH_EXPORT_CPP_API_sub_i16(sub_i16);
TH_EXPORT_CPP_API_mul_i32(mul_i32);
TH_EXPORT_CPP_API_div_i64(div_i64);
TH_EXPORT_CPP_API_add_f32(add_f32);
TH_EXPORT_CPP_API_sub_f32(sub_f32);
TH_EXPORT_CPP_API_add_f64(add_f64);
TH_EXPORT_CPP_API_sub_f64(sub_f64);
TH_EXPORT_CPP_API_mul_f64(mul_f64);
TH_EXPORT_CPP_API_check(check);
TH_EXPORT_CPP_API_concatx(concatx);
TH_EXPORT_CPP_API_splitx(splitx);
TH_EXPORT_CPP_API_to_i32(to_i32);
TH_EXPORT_CPP_API_from_i32(from_i32);
