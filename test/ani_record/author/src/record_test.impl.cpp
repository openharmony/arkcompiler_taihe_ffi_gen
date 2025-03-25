#include "record_test.impl.hpp"

#include "core/array.hpp"
#include "core/map.hpp"
#include "core/optional.hpp"
#include "core/string.hpp"
#include "record_test.Color.proj.0.hpp"
#include "record_test.Data.proj.1.hpp"
#include "record_test.ICpu.proj.2.hpp"
#include "record_test.ICpuInfo.proj.2.hpp"
#include "record_test.ICpuZero.proj.2.hpp"
#include "record_test.Pair.proj.1.hpp"
#include "record_test.TypeUnion.proj.1.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
class ICpu {
 public:
  int32_t add(int32_t a, int32_t b) { return a + b; }
  int32_t sub(int32_t a, int32_t b) { return a - b; }
};
class ICpuZero {
 public:
  int32_t add(int32_t a, int32_t b) { return a + b; }
  int32_t sub(int32_t a, int32_t b) { return a - b; }
};
class ICpuInfo {
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
void foreachMap(map_view<string, string> my_map) {
  std::cout << "Using begin() and end() for traversal:" << std::endl;
  for (auto it = my_map.begin(); it != my_map.end(); ++it) {
    const auto& [key, value] = *it;
    std::cout << "Key: " << key << ", Value: " << value << std::endl;
  }

  std::cout << "Using range-based for loop for traversal:" << std::endl;
  for (const auto& [key, value] : my_map) {
    std::cout << "Key: " << key << ", Value: " << value << std::endl;
  }

  std::cout << "Using const iterator for traversal:" << std::endl;
  const auto& const_map = my_map;
  for (auto it = const_map.begin(); it != const_map.end(); ++it) {
    const auto& [key, value] = *it;
    std::cout << "Key: " << key << ", Value: " << value << std::endl;
  }

  std::cout << "Using cbegin() and cend() for traversal:" << std::endl;
  for (auto it = my_map.cbegin(); it != my_map.cend(); ++it) {
    const auto& [key, value] = *it;
    std::cout << "Key: " << key << ", Value: " << value << std::endl;
  };
}

bool mapfunc01(map_view<string, bool> m) { return true; }

bool mapfunc02(map_view<string, int8_t> m) {
  for (const auto& pair : m) {
    if (pair.second <= 0) {
      return false;
    }
  }
  return true;
}

bool mapfunc03(map_view<string, int16_t> m) {
  for (const auto& pair : m) {
    if (pair.second <= 0) {
      return false;
    }
  }
  return true;
}

bool mapfunc04(map_view<string, int32_t> m) {
  for (const auto& pair : m) {
    if (pair.second <= 0) {
      return false;
    }
  }
  return true;
}

bool mapfunc05(map_view<string, int64_t> m) {
  for (const auto& pair : m) {
    if (pair.second <= 0) {
      return false;
    }
  }
  return true;
}

bool mapfunc06(map_view<string, float> m) {
  for (const auto& pair : m) {
    if (pair.second <= 0) {
      return false;
    }
  }
  return true;
}

bool mapfunc07(map_view<string, double> m) {
  for (const auto& pair : m) {
    if (pair.second <= 0) {
      return false;
    }
  }
  return true;
}

bool mapfunc08(map_view<string, string> m) {
  for (const auto& pair : m) {
    if (pair.second.empty()) {
      return false;
    }
  }
  return true;
}

bool mapfunc09(map_view<string, array<int8_t>> m) {
  for (const auto& pair : m) {
    if (pair.second.empty()) {
      return false;
    }
  }
  return true;
}

bool mapfunc10(map_view<string, array<int16_t>> m) {
  for (const auto& pair : m) {
    if (pair.second.empty()) {
      return false;
    }
  }
  return true;
}

bool mapfunc11(map_view<string, array<int32_t>> m) {
  for (const auto& pair : m) {
    if (pair.second.empty()) {
      return false;
    }
  }
  return true;
}

bool mapfunc12(map_view<string, array<int64_t>> m) {
  for (const auto& pair : m) {
    if (pair.second.empty()) {
      return false;
    }
  }
  return true;
}

bool mapfunc13(map_view<string, array<array<uint8_t>>> m) {
  for (const auto& pair : m) {
    if (pair.second.empty()) {
      return false;
    }
  }
  return true;
}

bool mapfunc14(map_view<string, array<bool>> m) {
  for (const auto& pair : m) {
    if (pair.second.empty()) {
      return false;
    }
  }
  return true;
}

bool mapfunc15(map_view<string, array<string>> m) {
  for (const auto& pair : m) {
    if (pair.second.empty()) {
      return false;
    }
  }
  return true;
}

bool mapfunc16(map_view<string, record_test::TypeUnion> m) { return true; }

bool mapfunc17(map_view<string, record_test::Color> m) { return true; }

bool mapfunc18(map_view<string, record_test::Pair> m) { return true; }

::record_test::ICpuZero makeICpuZero() {
  return make_holder<ICpuZero, ::record_test::ICpuZero>();
}

bool mapfunc19(map_view<string, record_test::ICpuZero> m) { return true; }

::record_test::ICpuInfo makeICpuInfo() {
  return make_holder<ICpuInfo, ::record_test::ICpuInfo>();
}

bool mapfunc20(map_view<string, record_test::ICpuInfo> m) { return true; }

bool mapfunc21(map_view<string, uintptr_t> m) {
  for (const auto& pair : m) {
    if (pair.second == 0) {
      return false;
    }
  }
  return true;
}

bool mapfunc22(map_view<string, map<string, bool>> m) {
  for (const auto& pair : m) {
    if (pair.second.size() == 0) {
      return false;
    }
  }
  return true;
}

bool mapfunc23(map_view<string, map<string, int32_t>> m) {
  for (const auto& pair : m) {
    if (pair.second.size() == 0) {
      return false;
    }
  }
  return true;
}

bool mapfunc24(map_view<string, map<string, array<int32_t>>> m) {
  for (const auto& pair : m) {
    if (pair.second.size() == 0) {
      return false;
    }
  }
  return true;
}

bool mapfunc25(map_view<string, map<string, string>> m) {
  for (const auto& pair : m) {
    if (pair.second.size() == 0) {
      return false;
    }
  }
  return true;
}

map<string, bool> mapfunc26() {
  map<string, bool> result;
  result.emplace("key1", true);
  result.emplace("key2", false);
  return result;
}

map<string, int8_t> mapfunc27() {
  map<string, int8_t> result;
  result.emplace("key1", static_cast<int8_t>(123));
  result.emplace("key2", static_cast<int8_t>(45));
  return result;
}

map<string, int16_t> mapfunc28() {
  map<string, int16_t> result;
  result.emplace("key1", static_cast<int16_t>(1234));
  result.emplace("key2", static_cast<int16_t>(5678));
  return result;
}

map<string, int32_t> mapfunc29() {
  map<string, int32_t> result;
  result.emplace("key1", static_cast<int32_t>(12345));
  result.emplace("key2", static_cast<int32_t>(67890));
  return result;
}

map<string, int64_t> mapfunc30() {
  map<string, int64_t> result;
  result.emplace("key1", static_cast<int64_t>(123456));
  result.emplace("key2", static_cast<int64_t>(789012));
  return result;
}

map<string, float> mapfunc31() {
  map<string, float> result;
  result.emplace("key1", 123.45f);
  result.emplace("key2", 67.89f);
  return result;
}

map<string, double> mapfunc32() {
  map<string, double> result;
  result.emplace("key1", 123.456);
  result.emplace("key2", 789.012);
  return result;
}

map<string, string> mapfunc33() {
  map<string, string> result;
  result.emplace("key1", "value1");
  result.emplace("key2", "value2");
  return result;
}

map<string, array<int8_t>> mapfunc34() {
  map<string, array<int8_t>> result;
  array<int8_t> a = {1, 2, 3};
  result.emplace("key1", a);
  array<int8_t> b = {4, 5, 6};
  result.emplace("key2", b);
  return result;
}

map<string, array<int16_t>> mapfunc35() {
  map<string, array<int16_t>> result;
  array<int16_t> a = {123, 456};
  result.emplace("key1", a);
  array<int16_t> b = {789, 1011};
  result.emplace("key2", b);
  return result;
}

map<string, array<int32_t>> mapfunc36() {
  map<string, array<int32_t>> result;
  array<int32_t> a = {1234, 5678};
  result.emplace("key1", a);
  array<int32_t> b = {9012, 3456};
  result.emplace("key2", b);
  return result;
}

map<string, array<int64_t>> mapfunc37() {
  map<string, array<int64_t>> result;
  array<int64_t> a = {12345, 67890};
  result.emplace("key1", a);
  array<int64_t> b = {11111, 22222};
  result.emplace("key2", b);
  return result;
}

map<string, array<uint8_t>> mapfunc38() {
  map<string, array<uint8_t>> result;
  array<uint8_t> a = {1, 2, 3};
  result.emplace("key1", a);
  array<uint8_t> b = {4, 5, 6};
  result.emplace("key2", b);
  return result;
}

map<string, array<bool>> mapfunc39() {
  map<string, array<bool>> result;
  array<bool> a = {true, false};
  result.emplace("key1", a);
  array<bool> b = {false, true};
  result.emplace("key2", b);
  return result;
}

map<string, array<string>> mapfunc40() {
  map<string, array<string>> result;
  array<string> a = {"value1", "value2"};
  result.emplace("key1", a);
  array<string> b = {"value3", "value4"};
  result.emplace("key2", b);
  return result;
}

map<string, record_test::TypeUnion> mapfunc41() {
  map<string, record_test::TypeUnion> result;
  result.emplace("key1", record_test::TypeUnion::make_a(123));
  result.emplace("key2", record_test::TypeUnion::make_b(true));
  result.emplace("key3", record_test::TypeUnion::make_c("value"));
  return result;
}

map<string, record_test::Color> mapfunc42() {
  map<string, record_test::Color> result;
  result.emplace("key1", record_test::Color::key_t::RED);
  result.emplace("key2", record_test::Color::key_t::GREEN);
  return result;
}

map<string, record_test::Pair> mapfunc43() {
  map<string, record_test::Pair> result;
  record_test::Pair p1{
      .a = "one",
      .b = true,
  };
  result.emplace("key1", p1);
  record_test::Pair p2{
      .a = "two",
      .b = false,
  };
  result.emplace("key2", p2);
  return result;
}

map<string, record_test::ICpuZero> mapfunc44() {
  map<string, record_test::ICpuZero> result;
  result.emplace("key1", make_holder<ICpuZero, ::record_test::ICpuZero>());
  result.emplace("key2", make_holder<ICpuZero, ::record_test::ICpuZero>());
  return result;
}

map<string, record_test::ICpuInfo> mapfunc45() {
  map<string, record_test::ICpuInfo> result;
  result.emplace("key1", make_holder<ICpuInfo, ::record_test::ICpuInfo>());
  result.emplace("key2", make_holder<ICpuInfo, ::record_test::ICpuInfo>());
  return result;
}

map<string, uintptr_t> mapfunc46() {
  map<string, uintptr_t> result;
  result.emplace("key1", reinterpret_cast<uintptr_t>(nullptr));
  result.emplace("key2", reinterpret_cast<uintptr_t>(nullptr));
  return result;
}

map<string, map<string, bool>> mapfunc47() {
  map<string, map<string, bool>> result;
  map<string, bool> m1;
  m1.emplace("subkey1", true);
  m1.emplace("subkey2", false);
  result.emplace("key1", m1);
  map<string, bool> m2;
  m2.emplace("subkey3", true);
  m2.emplace("subkey4", false);
  result.emplace("key2", m2);
  return result;
}

map<string, map<string, int32_t>> mapfunc48() {
  map<string, map<string, int32_t>> result;
  map<string, int32_t> m1;
  m1.emplace("subkey1", 100);
  m1.emplace("subkey2", 200);
  result.emplace("key1", m1);
  map<string, int32_t> m2;
  m2.emplace("subkey3", 300);
  m2.emplace("subkey4", 400);
  result.emplace("key2", m2);
  return result;
}

map<string, map<string, array<int32_t>>> mapfunc49() {
  map<string, map<string, array<int32_t>>> result;
  map<string, array<int32_t>> m1;
  array<int32_t> a1 = {1, 2, 3};
  m1.emplace("subkey1", a1);
  array<int32_t> b1 = {4, 5, 6};
  m1.emplace("subkey2", b1);
  result.emplace("key1", m1);
  map<string, array<int32_t>> m2;
  array<int32_t> a2 = {7, 8, 9};
  m2.emplace("subkey3", a2);
  array<int32_t> b2 = {10, 11, 12};
  m2.emplace("subkey4", b2);
  result.emplace("key2", m2);
  return result;
}

map<string, map<string, string>> mapfunc50() {
  map<string, map<string, string>> result;
  map<string, string> m1;
  m1.emplace("subkey1", "value1");
  m1.emplace("subkey2", "value2");
  result.emplace("key1", m1);
  map<string, string> m2;
  m2.emplace("subkey3", "value3");
  m2.emplace("subkey4", "value4");
  result.emplace("key2", m2);
  return result;
}

map<string, map<string, string>> mapfunc51(
    optional_view<map<string, string>> op) {
  map<string, map<string, string>> result;
  map<string, string> m1;
  m1.emplace("subkey1", "value1");
  m1.emplace("subkey2", "value2");
  result.emplace("key1", m1);
  map<string, string> m2;
  m2.emplace("subkey3", "value3");
  m2.emplace("subkey4", "value4");
  result.emplace("key2", m2);
  return result;
}

}  // namespace
TH_EXPORT_CPP_API_makeCpu(makeCpu);
TH_EXPORT_CPP_API_getCpuSize(getCpuSize);
TH_EXPORT_CPP_API_getASize(getASize);
TH_EXPORT_CPP_API_getStringIntSize(getStringIntSize);
TH_EXPORT_CPP_API_createStringString(createStringString);
TH_EXPORT_CPP_API_getMapfromArray(getMapfromArray);
TH_EXPORT_CPP_API_getDatafromMap(getDatafromMap);
TH_EXPORT_CPP_API_foreachMap(foreachMap);
TH_EXPORT_CPP_API_mapfunc01(mapfunc01);
TH_EXPORT_CPP_API_mapfunc02(mapfunc02);
TH_EXPORT_CPP_API_mapfunc03(mapfunc03);
TH_EXPORT_CPP_API_mapfunc04(mapfunc04);
TH_EXPORT_CPP_API_mapfunc05(mapfunc05);
TH_EXPORT_CPP_API_mapfunc06(mapfunc06);
TH_EXPORT_CPP_API_mapfunc07(mapfunc07);
TH_EXPORT_CPP_API_mapfunc08(mapfunc08);
TH_EXPORT_CPP_API_mapfunc09(mapfunc09);
TH_EXPORT_CPP_API_mapfunc10(mapfunc10);
TH_EXPORT_CPP_API_mapfunc11(mapfunc11);
TH_EXPORT_CPP_API_mapfunc12(mapfunc12);
TH_EXPORT_CPP_API_mapfunc13(mapfunc13);
TH_EXPORT_CPP_API_mapfunc14(mapfunc14);
TH_EXPORT_CPP_API_mapfunc15(mapfunc15);
TH_EXPORT_CPP_API_mapfunc16(mapfunc16);
TH_EXPORT_CPP_API_mapfunc17(mapfunc17);
TH_EXPORT_CPP_API_mapfunc18(mapfunc18);
TH_EXPORT_CPP_API_makeICpuZero(makeICpuZero);
TH_EXPORT_CPP_API_mapfunc19(mapfunc19);
TH_EXPORT_CPP_API_makeICpuInfo(makeICpuInfo);
TH_EXPORT_CPP_API_mapfunc20(mapfunc20);
TH_EXPORT_CPP_API_mapfunc21(mapfunc21);
TH_EXPORT_CPP_API_mapfunc22(mapfunc22);
TH_EXPORT_CPP_API_mapfunc23(mapfunc23);
TH_EXPORT_CPP_API_mapfunc24(mapfunc24);
TH_EXPORT_CPP_API_mapfunc25(mapfunc25);
TH_EXPORT_CPP_API_mapfunc26(mapfunc26);
TH_EXPORT_CPP_API_mapfunc27(mapfunc27);
TH_EXPORT_CPP_API_mapfunc28(mapfunc28);
TH_EXPORT_CPP_API_mapfunc29(mapfunc29);
TH_EXPORT_CPP_API_mapfunc30(mapfunc30);
TH_EXPORT_CPP_API_mapfunc31(mapfunc31);
TH_EXPORT_CPP_API_mapfunc32(mapfunc32);
TH_EXPORT_CPP_API_mapfunc33(mapfunc33);
TH_EXPORT_CPP_API_mapfunc34(mapfunc34);
TH_EXPORT_CPP_API_mapfunc35(mapfunc35);
TH_EXPORT_CPP_API_mapfunc36(mapfunc36);
TH_EXPORT_CPP_API_mapfunc37(mapfunc37);
TH_EXPORT_CPP_API_mapfunc38(mapfunc38);
TH_EXPORT_CPP_API_mapfunc39(mapfunc39);
TH_EXPORT_CPP_API_mapfunc40(mapfunc40);
TH_EXPORT_CPP_API_mapfunc41(mapfunc41);
TH_EXPORT_CPP_API_mapfunc42(mapfunc42);
TH_EXPORT_CPP_API_mapfunc43(mapfunc43);
TH_EXPORT_CPP_API_mapfunc44(mapfunc44);
TH_EXPORT_CPP_API_mapfunc45(mapfunc45);
TH_EXPORT_CPP_API_mapfunc46(mapfunc46);
TH_EXPORT_CPP_API_mapfunc47(mapfunc47);
TH_EXPORT_CPP_API_mapfunc48(mapfunc48);
TH_EXPORT_CPP_API_mapfunc49(mapfunc49);
TH_EXPORT_CPP_API_mapfunc50(mapfunc50);
TH_EXPORT_CPP_API_mapfunc51(mapfunc51);
