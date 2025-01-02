#include "rgb.base.proj.hpp"
#include "rgb.show.proj.hpp"

#include <iostream>
#include <format>
#include <cmath>

using namespace rgb;
using taihe::core::ConstexprTag;

class ColoredCircle {
    float r;
    std::string name;

    rgb::base::ColorOrRGBOrName myColor;

public:
    ColoredCircle(taihe::core::string_view id, float r, rgb::base::ColorOrRGBOrName const& color)
        : name(id), r(r), myColor(color) {
        std::cout << std::format("new 0x{:016x}", (size_t)((void*)this)) << std::endl;
    }

    ~ColoredCircle() {
        std::cout << std::format("del 0x{:016x}", (size_t)((void*)this)) << std::endl;
    }

    taihe::core::string getId() {
        return name;
    }

    float calculateArea() {
        return M_PI * r * r;
    }

    rgb::base::ColorOrRGBOrName getColor() {
        return myColor;
    }

    void setColor(rgb::base::ColorOrRGBOrName const& color) {
        myColor = color;
    }

    void show() {
        std::string content = std::format("{}: {}", name, r);
        if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::TagType::color>()) {
            std::cout << std::format("\033[{}m{}\033[39m", 30 + (int)ptr->get_tag(), content) << std::endl;
        } else if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::TagType::rgb>()) {
            std::cout << std::format("\033[38;2;{};{};{}m{}\033[39m", ptr->r, ptr->g, ptr->b, content) << std::endl;
        } else if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::TagType::name>()) {
            std::cout << std::format("({}) {}", ptr->c_str(), content) << std::endl;
        } else {
            std::cout << content << std::endl;
        }
    }
};

int main() {
    base::ColorOrRGBOrName color_114514(ConstexprTag<base::ColorOrRGBOrName::TagType::rgb>, 0x11, 0x45, 0x14);
    base::ColorOrRGBOrName color_yellow(ConstexprTag<base::ColorOrRGBOrName::TagType::color>, ConstexprTag<base::Color::TagType::yellow>);
    base::ColorOrRGBOrName color_xxx(ConstexprTag<base::ColorOrRGBOrName::TagType::name>, "XXX");
    base::ColorOrRGBOrName color_unknown(ConstexprTag<base::ColorOrRGBOrName::TagType::undefined>);

    std::cout << base::toString(color_114514).c_str() << std::endl;
    std::cout << base::toString(color_yellow).c_str() << std::endl;
    std::cout << base::toString(color_xxx).c_str() << std::endl;
    std::cout << base::toString(color_unknown).c_str() << std::endl;

    auto circle = taihe::core::makeInterface<rgb::show::IShowable, ColoredCircle>("circle", 10, color_114514);
    auto rect = show::makeColoredRectangle("rect a", color_yellow, 5, 5);

    circle.show();
    rect.show();
    show::copyColor(rect, circle);
    rect.show();
}
