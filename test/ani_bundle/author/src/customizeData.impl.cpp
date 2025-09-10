#include "customizeData.impl.hpp"
#include <iostream>
#include "customizeData.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace customizeData;

namespace {

class CustomizeDataImpl {
public:
  string name_ = "bob";
  string value_ = "jack";
  string extra_ = "john";

  CustomizeDataImpl() {}

  void SetName(string_view name) {
    name_ = name;
  }

  string GetName() {
    return name_;
  }

  void SetValue(string_view value) {
    value_ = value;
  }

  string GetValue() {
    return value_;
  }

  void SetExtra(string_view extra) {
    extra_ = extra;
  }

  string GetExtra() {
    return extra_;
  }
};

CustomizeData GetCustomizeData() {
  return make_holder<CustomizeDataImpl, CustomizeData>();
}
}  // namespace

TH_EXPORT_CPP_API_GetCustomizeData(GetCustomizeData);