#include "bigint_test.impl.hpp"

#include "core/array.hpp"
using namespace taihe;
namespace {
int64_t getNumfromBigint(array_view<int64_t> a) {
  int64_t res = a[a.size() - 1] & 0xFF;
  return res;
}
array<int64_t> genBigint(array_view<int64_t> a) { return a; }
}  // namespace
TH_EXPORT_CPP_API_getNumfromBigint(getNumfromBigint);
TH_EXPORT_CPP_API_genBigint(genBigint);
