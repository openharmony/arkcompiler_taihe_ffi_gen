#include "hello.impl.hpp"
#include <iostream>
#include "hello.proj.hpp"
#include "stdexcept"
#include "taihe/optional.hpp"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

void setData(::hello::Data const &data) {}

::hello::Data getData() {
  return {
      .a = taihe::optional<taihe::string>{std::in_place, "name"},
      .b = taihe::optional<double>{std::in_place, 2.5},
      .c = taihe::optional<int>{std::in_place, 3},
      .d = taihe::optional<bool>{std::in_place, true},
      .e = taihe::optional<bool>{std::in_place, true},
      .f = taihe::optional<bool>{std::in_place, false},
      .g = taihe::optional<bool>{std::in_place, false},
  };
}

void setRecord(::taihe::map_view<::taihe::string, ::taihe::string> rec) {}

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
