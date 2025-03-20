#include "union_ani.impl.hpp"
#include "stdexcept"
#include "union_ani.Union.proj.1.hpp"
#include "core/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
string printUnion(::union_ani::Union const& data) {
    switch (data.get_tag()) {
    case ::union_ani::Union::tag_t::sValue:
        std::cout << "s: " << data.get_sValue_ref() << std::endl;
        return "s";
    case ::union_ani::Union::tag_t::iValue:
        std::cout << "i: " << data.get_iValue_ref() << std::endl;
        return "i";
    case ::union_ani::Union::tag_t::pValue:
        std::cout << "p: " << data.get_pValue_ref().a << ", " << data.get_pValue_ref().b << std::endl;
        return "p";
    case ::union_ani::Union::tag_t::uValue:
        std::cout << "u" << std::endl;
        return "u";
    }
}
::union_ani::Union makeUnion(string_view kind) {
    if (kind == "s") {
        return ::union_ani::Union::make_sValue("string");
    }
    if (kind == "i") {
        return ::union_ani::Union::make_iValue(123);
    }
    if (kind == "p") {
        ::union_ani::Pair pair = {"a", "b"};
        return ::union_ani::Union::make_pValue(pair);
    }
    return ::union_ani::Union::make_uValue();
}
}
TH_EXPORT_CPP_API_printUnion(printUnion)
TH_EXPORT_CPP_API_makeUnion(makeUnion)
