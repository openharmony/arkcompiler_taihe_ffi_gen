#include "binding.impl.hpp"
#include "stdexcept"
#include "binding.Color.proj.1.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {

::binding::Color convert_color(::binding::Color const& a) {
    return ::binding::Color{ a.G, a.B, a.R };
}

}

TH_EXPORT_CPP_API_convert_color(convert_color);
