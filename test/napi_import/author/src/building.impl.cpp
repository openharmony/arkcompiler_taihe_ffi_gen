#include "building.impl.hpp"
#include "building.proj.hpp"
#include "people.proj.hpp"

namespace {
::building::group make_group() {
  return ::building::group{::people::student{"mary", 20}, 23};
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_make_group(make_group);
// NOLINTEND
