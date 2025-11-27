#include "foo.impl.hpp"
#include "foo.DerivedMethodClass.template.hpp"
#include "stdexcept"

namespace {
::foo::DerivedMethodClass makeDerivedMethodClass() {
  // The parameters in the make_holder function should be of the same type
  // as the parameters in the constructor of the actual implementation class.
  return taihe::make_holder<DerivedMethodClassImpl,
                            ::foo::DerivedMethodClass>();
}

::foo::DerivedDataClass makeDerivedDataClass() {
  return {
      .base = {"base"},
      .foo = {"foo"},
      .bar = {"bar"},
      .x = 42,
      .y = 56,
  };
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_makeDerivedMethodClass(makeDerivedMethodClass);
TH_EXPORT_CPP_API_makeDerivedDataClass(makeDerivedDataClass);
// NOLINTEND
