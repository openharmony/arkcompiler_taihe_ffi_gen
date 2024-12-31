#include "rgb.base.proj.hpp"
#include "rgb.show.proj.hpp"

#include <iostream>

using namespace rgb;

// class ColoredCircle : public Rectangle {
//     rgb::base::ColorOrRGBOrName myColor;
// public:
//     ColoredRectangle(taihe::core::string_view id, float h, float w, rgb::base::ColorOrRGBOrName const& color)
//         : Rectangle(id, h, w), myColor(color) {}

//     rgb::base::ColorOrRGBOrName getColor() {
//         return myColor;
//     }

//     void setColor(rgb::base::ColorOrRGBOrName const& color) {
//         myColor = color;
//     }

//     void show() {
//         std::string content = std::format("{}: {}x{}", name, h, w);
//         if (auto ptr = myColor.get_ptr(rgb::base::ColorOrRGBOrName::ConstexprTag::color)) {
//             std::cout << std::format("\033[{}m{}\033[39m", (int)ptr->tag, content) << std::endl;
//         } else if (auto ptr = myColor.get_ptr(rgb::base::ColorOrRGBOrName::ConstexprTag::rgb)) {
//             std::cout << std::format("\033[38;2;{};{};{}m{}\033[39m", ptr->r, ptr->g, ptr->b, content) << std::endl;
//         } else if (auto ptr = myColor.get_ptr(rgb::base::ColorOrRGBOrName::ConstexprTag::name)) {
//             std::cout << std::format("({}) {}", ptr->c_str(), content) << std::endl;
//         } else {
//             std::cout << content << std::endl;
//         }
//     }
// };

int main() {
    base::ColorOrRGBOrName color_114514(base::ColorOrRGBOrName::ConstexprTag::rgb, 0x11, 0x45, 0x14);
    base::ColorOrRGBOrName color_yellow(base::ColorOrRGBOrName::ConstexprTag::color, base::Color::ConstexprTag::yellow);
    base::ColorOrRGBOrName color_xxx(base::ColorOrRGBOrName::ConstexprTag::name, "XXX");
    base::ColorOrRGBOrName color_unknown(base::ColorOrRGBOrName::ConstexprTag::undefined);

    std::cout << base::toString(color_114514).c_str() << std::endl;
    std::cout << base::toString(color_yellow).c_str() << std::endl;
    std::cout << base::toString(color_xxx).c_str() << std::endl;
    std::cout << base::toString(color_unknown).c_str() << std::endl;

    auto rect_a = show::makeColoredRectangle("rect a", color_114514, 10, 10);
    auto rect_b = show::makeColoredRectangle("rect b", color_yellow, 5, 5);

    rect_a.show();
    rect_b.show();
    show::copyColor(rect_b, rect_a);
    rect_b.show();
}
