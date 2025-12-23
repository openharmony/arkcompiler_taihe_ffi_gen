#include "structext.impl.hpp"
#include "stdexcept"
#include "structext.proj.hpp"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace structext;

namespace {
Player addNewPlayer(string_view name) {
  return {{0, 0, 0}, name};
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_addNewPlayer(addNewPlayer);
// NOLINTEND
