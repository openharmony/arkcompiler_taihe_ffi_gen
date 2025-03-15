#include "enum_ani.impl.hpp"
#include "stdexcept"
// Please delete this include when you implement
using namespace taihe::core;
namespace {

int32_t addEnum(::enum_ani::Color const& color, int32_t n) {
    return static_cast<int32_t>(color.get_tag()) + n;
}

::enum_ani::Color getEnum(int32_t n) {
    if (n < static_cast<int32_t>(::enum_ani::Color::tag_t::red) ||
        n > static_cast<int32_t>(::enum_ani::Color::tag_t::blue)) {
        throw std::runtime_error("invalid enum value");        
    }
    switch(static_cast<::enum_ani::Color::tag_t>(n)) {
        case ::enum_ani::Color::tag_t::red:
            return ::enum_ani::Color::make<::enum_ani::Color::tag_t::red>();
        case ::enum_ani::Color::tag_t::yellow:
            return ::enum_ani::Color::make<::enum_ani::Color::tag_t::yellow>();
        case ::enum_ani::Color::tag_t::blue:
            return ::enum_ani::Color::make<::enum_ani::Color::tag_t::blue>();
    }
    throw std::runtime_error("invalid enum value");     
}       

}

TH_EXPORT_CPP_API_addEnum(addEnum)
TH_EXPORT_CPP_API_getEnum(getEnum)
