#include "hello.impl.hpp"
#include <iostream>
#include "hello.proj.hpp"
#include "stdexcept"
#include "taihe/optional.hpp"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

void setData(::hello::Data const &data) {
  // std::cerr << "data:" << std::endl;
  // if (data.a.has_value()) {
  //   std::cerr << "a: " << data.a.value() << std::endl;
  // }
  // if (data.b.has_value()) {
  //   std::cerr << "b: " << data.b.value() << std::endl;
  // }
  // if (data.c.has_value()) {
  //   std::cerr << "c: " << data.c.value() << std::endl;
  // }
  // if (data.d.has_value()) {
  //   std::cerr << "d: " << data.d.value() << std::endl;
  // }
  // if (data.e.has_value()) {
  //   std::cerr << "e: " << data.e.value() << std::endl;
  // }
  // if (data.f.has_value()) {
  //   std::cerr << "f: " << data.f.value() << std::endl;
  // }
  // if (data.g.has_value()) {
  //   std::cerr << "g: " << data.g.value() << std::endl;
  // }
}

::hello::Data getData() {
  return {
      .a = {std::in_place, "name"},
      .b = {std::in_place, 2.5},
      .c = {std::in_place, 3},
      .d = {std::in_place, true},
      .e = {std::in_place, true},
      .f = {std::in_place, false},
      .g = {std::in_place, false},
  };
}

void setRecord(::taihe::map_view<::taihe::string, ::taihe::string> rec) {
  // std::cerr << "record:" << std::endl;
  // for (auto const &[key, value] : rec) {
  //   std::cerr << key << ": " << value << std::endl;
  // }
}

static ::taihe::map<::taihe::string, ::taihe::string> global_rec = [] {
  ::taihe::map<::taihe::string, ::taihe::string> rec;
  rec.emplace("key0", "value0");
  rec.emplace("key1", "value1");
  rec.emplace("key2", "value2");
  rec.emplace("key3", "value3");
  rec.emplace("key4", "value4");
  rec.emplace("key5", "value5");
  rec.emplace("key6", "value6");
  rec.emplace("key7", "value7");
  return rec;
}();

::taihe::map<::taihe::string, ::taihe::string> getRecord() {
  return global_rec;
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_setData(setData);
TH_EXPORT_CPP_API_getData(getData);
TH_EXPORT_CPP_API_setRecord(setRecord);
TH_EXPORT_CPP_API_getRecord(getRecord);
// NOLINTEND
