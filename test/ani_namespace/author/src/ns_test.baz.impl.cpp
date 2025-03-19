#include "ns_test.baz.impl.hpp"
#include "stdexcept"
#include "ns_test.baz.Color.proj.1.hpp"
#include "ns_test.baz.Data.proj.1.hpp"
#include "core/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {

int32_t addEnum(::ns_test::baz::Color const& color, int32_t n) {
    return static_cast<int32_t>(color.get_tag()) + n;
}
::ns_test::baz::Color getEnum(int32_t n) {
    if (n < static_cast<int32_t>(::ns_test::baz::Color::tag_t::red) ||
    n > static_cast<int32_t>(::ns_test::baz::Color::tag_t::blue)) {
        throw std::runtime_error("invalid enum value");        
    }
    switch(static_cast<::ns_test::baz::Color::tag_t>(n)) {
        case ::ns_test::baz::Color::tag_t::red:
            return ::ns_test::baz::Color::make<::ns_test::baz::Color::tag_t::red>();
        case ::ns_test::baz::Color::tag_t::yellow:
            return ::ns_test::baz::Color::make<::ns_test::baz::Color::tag_t::yellow>();
        case ::ns_test::baz::Color::tag_t::blue:
            return ::ns_test::baz::Color::make<::ns_test::baz::Color::tag_t::blue>();
    }
    throw std::runtime_error("invalid enum value");
}
string concatStruct(::ns_test::baz::Data const& data) {
    return concat(concat(data.a, data.b), to_string(data.c));
}
::ns_test::baz::Data makeStruct(string_view a, string_view b, int32_t c) {
    return {a, b, c};
}

}

TH_EXPORT_CPP_API_addEnum(addEnum)
TH_EXPORT_CPP_API_getEnum(getEnum)
TH_EXPORT_CPP_API_concatStruct(concatStruct)
TH_EXPORT_CPP_API_makeStruct(makeStruct)
