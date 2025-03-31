#include "struct_test.impl.hpp"

#include "stdexcept"
// Please delete this include when you implement
using namespace taihe;
namespace {

string concatStruct(::struct_test::Data const& data) {
  return concat(concat(data.a, data.b), to_string(data.c));
}

::struct_test::Data makeStruct(string_view a, string_view b, int32_t c) {
  return {a, b, c};
}

}  // namespace

TH_EXPORT_CPP_API_concatStruct(concatStruct);
TH_EXPORT_CPP_API_makeStruct(makeStruct);
