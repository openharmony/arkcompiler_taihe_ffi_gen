#include "binding.impl.hpp"

#include "binding.Color.proj.1.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {

::binding::Color convert_color(::binding::Color const &a) {
  return ::binding::Color{a.G, a.B, a.R};
}

}  // namespace

TH_EXPORT_CPP_API_convert_color(convert_color);
