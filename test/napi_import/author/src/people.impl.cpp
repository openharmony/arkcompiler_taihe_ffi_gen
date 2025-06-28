#include "people.impl.hpp"
#include "people.proj.hpp"

namespace {
::people::student make_student() {
  return ::people::student{"mike", 22};
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_make_student(make_student);
// NOLINTEND
