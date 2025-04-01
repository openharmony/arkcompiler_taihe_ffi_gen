#include "ns_test.baz.impl.hpp"

#include "stdexcept"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {

string concatStruct(::ns_test::baz::Data const& data) {
  return data.a + data.b + to_string(data.c);
}

::ns_test::baz::Data makeStruct(string_view a, string_view b, int32_t c) {
  return {a, b, c};
}

}  // namespace

TH_EXPORT_CPP_API_concatStruct(concatStruct);
TH_EXPORT_CPP_API_makeStruct(makeStruct);
