#include "union_ani.impl.hpp"
#include "stdexcept"
// Please delete this include when you implement
using namespace taihe::core;
namespace {

string printUnion(::union_ani::ColorName const& data) {
    switch (data.get_tag()) {
        case ::union_ani::ColorName::tag_t::undefined:
            std::cout << static_cast<int32_t>(data.get_tag()) << " : " << "undefined" << std::endl;
            break;
        case ::union_ani::ColorName::tag_t::color:
            if (auto ptr = data.get_color_ptr()) {
                std::cout << static_cast<int32_t>(data.get_tag()) << " : " << static_cast<int32_t>(ptr->get_tag()) << std::endl;
            }
            break;
        case ::union_ani::ColorName::tag_t::rgb:
            if (auto ptr = data.get_rgb_ptr()) {
                std::cout << static_cast<int32_t>(data.get_tag()) << " : " << ptr->r + ptr->g + ptr->b << std::endl;
            }
            break;
        case ::union_ani::ColorName::tag_t::name:
            if (auto ptr = data.get_name_ptr()) {
                std::cout << static_cast<int32_t>(data.get_tag()) << " : " << *ptr << std::endl;
            }
            break;

    }
    return to_string(static_cast<int32_t>(data.get_tag()));
}

::union_ani::ColorName makeUnion(int32_t n) {
    switch (static_cast<::union_ani::ColorName::tag_t>(n)) {   
        case ::union_ani::ColorName::tag_t::undefined:
            return ::union_ani::ColorName::make_undefined();
            break;
        case ::union_ani::ColorName::tag_t::color:
            return ::union_ani::ColorName::make_color(::union_ani::Color::make_RED());
            break;  
        case ::union_ani::ColorName::tag_t::rgb:
            return ::union_ani::ColorName::make_rgb();
            break;  
        case ::union_ani::ColorName::tag_t::name:
            return ::union_ani::ColorName::make_name("C++");
            break;  
        default:
            return ::union_ani::ColorName::make_undefined();
            break;
    }   
}

}

TH_EXPORT_CPP_API_printUnion(printUnion)
TH_EXPORT_CPP_API_makeUnion(makeUnion)