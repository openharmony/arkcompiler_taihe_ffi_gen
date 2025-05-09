#include "arraybuffer.impl.hpp"

#include "stdexcept"
#include "taihe/array.hpp"
#include "taihe/runtime.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
int32_t convert2Int(array_view<uint8_t> a) {
  int32_t num = 0;
  if (a.size() >= 4) {
    num = *(int32_t *)a.begin();
  } else {
    set_business_error(1, "ArrayBuffer len < 4");
  }
  return num;
}
}  // namespace

TH_EXPORT_CPP_API_convert2Int(convert2Int);
