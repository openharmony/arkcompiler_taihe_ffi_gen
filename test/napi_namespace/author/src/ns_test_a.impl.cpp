#include "ns_test_a.impl.hpp"
#include "ns_test_a.proj.hpp"

namespace {
::taihe::string Funtest(::ns_test_a::Color s) {
  switch (s.get_key()) {
  case ::ns_test_a::Color::key_t::BLUE:
    return "blue";
  case ::ns_test_a::Color::key_t::GREEN:
    return "green";
  case ::ns_test_a::Color::key_t::RED:
    return "red";
  }
  return "error";
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_Funtest(Funtest);
// NOLINTEND
