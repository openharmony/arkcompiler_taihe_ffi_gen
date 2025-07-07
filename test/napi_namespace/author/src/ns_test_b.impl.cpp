#include "ns_test_b.impl.hpp"
#include "ns_test_b.proj.hpp"

namespace {

int32_t Funtest(::ns_test_b::MyStruct const &s) {
  return s.a + s.b;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_Funtest(Funtest);
// NOLINTEND
