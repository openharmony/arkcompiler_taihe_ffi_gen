#include "ns_test.baz.impl.hpp"

#include "core/string.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe;
namespace {

string concatStruct(::ns_test::baz::Data const& data) {
  return concat(concat(data.a, data.b), to_string(data.c));
}
::ns_test::baz::Data makeStruct(string_view a, string_view b, int32_t c) {
  return {a, b, c};
}

}  // namespace

TH_EXPORT_CPP_API_concatStruct(concatStruct);
TH_EXPORT_CPP_API_makeStruct(makeStruct);
