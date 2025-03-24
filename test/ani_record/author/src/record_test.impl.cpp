#include "record_test.impl.hpp"

#include "core/array.hpp"
#include "core/map.hpp"
#include "core/string.hpp"
#include "record_test.Data.proj.1.hpp"
#include "record_test.ICpu.proj.2.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
class ICpu {
 public:
  int32_t add(int32_t a, int32_t b) { return a + b; }
  int32_t sub(int32_t a, int32_t b) { return a - b; }
};
::record_test::ICpu makeCpu() {
  return make_holder<ICpu, ::record_test::ICpu>();
}
int32_t getCpuSize(map_view<string, ::record_test::ICpu> r) { return r.size(); }
int32_t getASize(map_view<int32_t, uintptr_t> r) { return r.size(); }
int32_t getStringIntSize(map_view<string, int32_t> r) { return r.size(); }
map<string, string> createStringString(int32_t a) {
  map<string, string> m;
  while (a--) {
    m.emplace(to_string(a), "abc");
  }
  return m;
}
map<string, int32_t> getMapfromArray(array_view<::record_test::Data> d) {
  map<string, int32_t> m;
  for (int i = 0; i < d.size(); ++i) {
    m.emplace(d[i].a, d[i].b);
  }
  return m;
}
::record_test::Data getDatafromMap(map_view<string, ::record_test::Data> m,
                                   string_view k) {
  auto iter = m.find(k);
  if (iter == nullptr) {
    return {"su", 7};
  }
  return {iter->a, iter->b};
}
}  // namespace
TH_EXPORT_CPP_API_makeCpu(makeCpu) TH_EXPORT_CPP_API_getCpuSize(getCpuSize)
    TH_EXPORT_CPP_API_getASize(getASize)
        TH_EXPORT_CPP_API_getStringIntSize(getStringIntSize)
            TH_EXPORT_CPP_API_createStringString(createStringString)
                TH_EXPORT_CPP_API_getMapfromArray(getMapfromArray)
                    TH_EXPORT_CPP_API_getDatafromMap(getDatafromMap)
