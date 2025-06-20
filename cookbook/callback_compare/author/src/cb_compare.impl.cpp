#include "cb_compare.impl.hpp"
#include "cb_compare.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

bool cbCompare(::taihe::callback_view<::taihe::string()> cb1,
               ::taihe::callback_view<::taihe::string()> cb2) {
  return cb1 == cb2 ? true : false;
}

}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_cbCompare(cbCompare);
// NOLINTEND
