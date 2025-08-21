#include "import_example.impl.hpp"
#include <iostream>
#include "import_example.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

constexpr int K_DEFAULT_X = 1;
constexpr int K_DEFAULT_Y = 2;

constexpr int K_ID = 1;
constexpr char const *K_NAME = "1";

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
  return {K_DEFAULT_X, K_DEFAULT_Y};
}

::export_struct::StructA ImportStructFunc() {
  return {K_ID, K_NAME};
}

::export_union::ExportUnion ImportUnionFunc() {
  return ::export_union::ExportUnion::make_Foo(K_NAME);
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
