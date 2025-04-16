#include "union_ani.impl.hpp"

#include "stdexcept"
#include "taihe/runtime.hpp"
#include "taihe/string.hpp"
#include "union_ani.MyUnion.proj.1.hpp"
using namespace taihe;

namespace {
string printInnerUnion(::union_ani::InnerUnion const &data) {
  switch (data.get_tag()) {
  case ::union_ani::InnerUnion::tag_t::stringValue:
    std::cout << "s: " << data.get_stringValue_ref() << std::endl;
    return "s";
  case ::union_ani::InnerUnion::tag_t::pairValue:
    std::cout << "p: " << data.get_pairValue_ref().a << ", "
              << data.get_pairValue_ref().b << std::endl;
    return "p";
  case ::union_ani::InnerUnion::tag_t::undefinedValue:
    std::cout << "u" << std::endl;
    return "u";
  }
}

string printMyUnion(::union_ani::MyUnion const &data) {
  switch (data.get_tag()) {
  case ::union_ani::MyUnion::tag_t::innerValue:
    return printInnerUnion(data.get_innerValue_ref());
  case ::union_ani::MyUnion::tag_t::floatValue:
    std::cout << "f: " << data.get_floatValue_ref() << std::endl;
    return "f";
  }
}

::union_ani::MyUnion makeMyUnion(string_view kind) {
  float const testFloat = 123.0f;
  if (kind == "s") {
    return ::union_ani::MyUnion::make_innerValue(
        ::union_ani::InnerUnion::make_stringValue("string"));
  }
  if (kind == "p") {
    ::union_ani::Pair pair = {"a", "b"};
    return ::union_ani::MyUnion::make_innerValue(
        ::union_ani::InnerUnion::make_pairValue(pair));
  }
  if (kind == "f") {
    return ::union_ani::MyUnion::make_floatValue(testFloat);
  }
  return ::union_ani::MyUnion::make_innerValue(
      ::union_ani::InnerUnion::make_undefinedValue());
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_printMyUnion(printMyUnion);
TH_EXPORT_CPP_API_makeMyUnion(makeMyUnion);
// NOLINTEND
