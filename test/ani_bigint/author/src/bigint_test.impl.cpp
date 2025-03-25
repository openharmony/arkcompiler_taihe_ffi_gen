#include "bigint_test.impl.hpp"

#include <iostream>

#include "core/array.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
bool bigint01(double a, array_view<int64_t> b) { return true; }
double bigint02(double a) { return a; }
array<int64_t> bigint03(array_view<int64_t> a) { return a; }
void bigint04(array_view<int64_t> a) {
  for (int i = 0; i < a.size(); i++) {
    std::cout << a[i] << std::endl;
  }
}
array<int64_t> bigint05(double a, array_view<int64_t> b) { return b; }
double bigint06(double a, array_view<int64_t> b) { return a; }
}  // namespace
TH_EXPORT_CPP_API_bigint01(bigint01);
TH_EXPORT_CPP_API_bigint02(bigint02);
TH_EXPORT_CPP_API_bigint03(bigint03);
TH_EXPORT_CPP_API_bigint04(bigint04);
TH_EXPORT_CPP_API_bigint05(bigint05);
TH_EXPORT_CPP_API_bigint06(bigint06);
