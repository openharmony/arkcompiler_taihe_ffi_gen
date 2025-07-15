#include "import_example.impl.hpp"
#include <iostream>
#include "import_example.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

constexpr int kDefaultX = 1;
constexpr int kDefaultY = 2;

constexpr int kId = 1;
constexpr char const *kName = "1";

class IfaceAImpl {
public:

public:
  IfaceAImpl() {}

  void Foo() {
    std::cout << "Export IfaceA Foo()" << std::endl;
  }

  void Bar() {
    std::cout << "Export IfaceA Bar()" << std::endl;
  }
};

::export_enum::ExportEnum ImportEnumFunc() {
  return ::export_enum::ExportEnum::key_t::Foo;
}

::export_iface::IfaceA ImportIfaceFunc() {
  return taihe::make_holder<IfaceAImpl, ::export_iface::IfaceA>();
}

::export_namespace::NsStructA ImportNsFunc() {
  return {kDefaultX, kDefaultY};
}

::export_struct::StructA ImportStructFunc() {
  return {kId, kName};
}

::export_union::ExportUnion ImportUnionFunc() {
  return ::export_union::ExportUnion::make_Foo(kName);
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_ImportEnumFunc(ImportEnumFunc);
TH_EXPORT_CPP_API_ImportIfaceFunc(ImportIfaceFunc);
TH_EXPORT_CPP_API_ImportNsFunc(ImportNsFunc);
TH_EXPORT_CPP_API_ImportStructFunc(ImportStructFunc);
TH_EXPORT_CPP_API_ImportUnionFunc(ImportUnionFunc);
// NOLINTEND
