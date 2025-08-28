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

::struct_test::Student create_student() {
  return ::struct_test::Student{"Mary", 15};
}

::struct_test::Student process_student(::struct_test::Student const &a) {
  return {a.name + " student", a.age + 10};
}

::struct_test::Teacher create_teacher() {
  return ::struct_test::Teacher{"Rose", 25};
}

::struct_test::Teacher process_teacher(::struct_test::Teacher const &a) {
  return {a.name + " teacher", a.age + 15};
}

::struct_test::G process_g(::struct_test::G const &a) {
  return {{a.f.f + 1}, a.g + 2};
}

::struct_test::H process_h(::struct_test::H const &a) {
  return {{{a.g.f.f + 1}, a.g.g + 2}, a.h + 3};
}

::struct_test::H create_h(int32_t f, int32_t g, int32_t h) {
  return {{{f}, g}, h};
}

::taihe::string give_lessons() {
  return "math";
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_from_rgb(from_rgb);
TH_EXPORT_CPP_API_to_rgb(to_rgb);
TH_EXPORT_CPP_API_from_color(from_color);
TH_EXPORT_CPP_API_to_color(to_color);
TH_EXPORT_CPP_API_create_student(create_student);
TH_EXPORT_CPP_API_process_student(process_student);
TH_EXPORT_CPP_API_create_teacher(create_teacher);
TH_EXPORT_CPP_API_process_teacher(process_teacher);
TH_EXPORT_CPP_API_process_g(process_g);
TH_EXPORT_CPP_API_process_h(process_h);
TH_EXPORT_CPP_API_create_h(create_h);
TH_EXPORT_CPP_API_give_lessons(give_lessons);
// NOLINTEND
