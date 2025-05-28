#include "struct_test.impl.hpp"
#include "struct_test.proj.hpp"

namespace {
int32_t from_rgb(::struct_test::RGB const &rgb) {
  return rgb.r + rgb.g + rgb.b;
}

::struct_test::RGB to_rgb(int32_t a) {
  ::struct_test::RGB rgb{a, a / 2, a / 4};
  return rgb;
}

double from_color(::struct_test::Color const &color) {
  if (color.flag) {
    return color.rgb.r + 100;
  } else {
    return color.price + 1;
  }
}

::struct_test::Color to_color(::taihe::string_view a, bool b, double c,
                              ::struct_test::RGB const &d) {
  ::struct_test::Color color{a, b, c, d};
  return color;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_from_rgb(from_rgb);
TH_EXPORT_CPP_API_to_rgb(to_rgb);
TH_EXPORT_CPP_API_from_color(from_color);
TH_EXPORT_CPP_API_to_color(to_color);
// NOLINTEND
