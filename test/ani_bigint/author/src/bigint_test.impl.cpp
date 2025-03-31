#include "bigint_test.impl.hpp"

#include <iostream>

#include "core/array.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe;
namespace {
bool BigInt01(double a, array_view<int64_t> b) { return true; }
double BigInt02(double a) { return a; }
array<int64_t> BigInt03(array_view<int64_t> a) { return a; }
void BigInt04(array_view<int64_t> a) {
  for (int i = 0; i < a.size(); i++) {
    std::cout << a[i] << std::endl;
  }
}
array<int64_t> BigInt05(double a, array_view<int64_t> b) { return b; }
double BigInt06(double a, array_view<int64_t> b) { return a; }
}  // namespace
TH_EXPORT_CPP_API_BigInt01(BigInt01);
TH_EXPORT_CPP_API_BigInt02(BigInt02);
TH_EXPORT_CPP_API_BigInt03(BigInt03);
TH_EXPORT_CPP_API_BigInt04(BigInt04);
TH_EXPORT_CPP_API_BigInt05(BigInt05);
TH_EXPORT_CPP_API_BigInt06(BigInt06);
