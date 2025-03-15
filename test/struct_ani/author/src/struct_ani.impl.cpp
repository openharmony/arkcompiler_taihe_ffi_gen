#include "struct_ani.impl.hpp"
#include "stdexcept"
// Please delete this include when you implement
using namespace taihe::core;
namespace {

string concatStruct(::struct_ani::Data const& data) {
    return concat(concat(data.a, data.b), to_string(data.c));
}

::struct_ani::Data makeStruct(string_view a, string_view b, int32_t c) {
    return {a, b, c};
}

}

TH_EXPORT_CPP_API_concatStruct(concatStruct)
TH_EXPORT_CPP_API_makeStruct(makeStruct)
