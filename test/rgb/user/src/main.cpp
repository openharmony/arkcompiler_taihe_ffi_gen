#include "rgb.base.proj.hpp"
#include "rgb.show.proj.hpp"

#include <iostream>
#include <cmath>
#include <iomanip>

using namespace rgb;
using taihe::core::static_tag;

class ColoredCircle {
    float r;
    std::string name;

    rgb::base::ColorOrRGBOrName myColor;

public:
    ColoredCircle(taihe::core::string_view id, float r, rgb::base::ColorOrRGBOrName const& color)
        : name(id), r(r), myColor(color) {
        std::cout << "new " << this << std::endl;
    }

    ~ColoredCircle() {
        std::cout << "del " << this << std::endl;
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
        std::string content = "circle " + name + ": r = " + std::to_string(r);
        if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::tag_t::color>()) {
            std::cout << "\033[" << 30 + (int)ptr->get_tag() << "m" << content << "\033[39m" << std::endl;
        } else if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::tag_t::rgb>()) {
            std::cout << "\033[38;2;" << (int)ptr->r << ";" << (int)ptr->g << ";" << (int)ptr->b << "m" << content << "\033[39m" << std::endl;
        } else if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::tag_t::name>()) {
            std::cout << "(" << ptr->c_str() << ") " << content << std::endl;
        } else {
            std::cout << content << std::endl;
        }
    }
};

int main() {
    auto color_114514 = base::ColorOrRGBOrName::make_rgb(base::RGB{0x11, 0x45, 0x14});
    auto color_yellow = base::ColorOrRGBOrName::make_color(base::Color::make_yellow());
    auto color_my_color = base::ColorOrRGBOrName::make_name("My Color");
    auto color_unknown = base::ColorOrRGBOrName::make_undefined();

    std::cout << base::toString(color_114514).c_str() << std::endl;
    std::cout << base::toString(color_yellow).c_str() << std::endl;
    std::cout << base::toString(color_my_color).c_str() << std::endl;
    std::cout << base::toString(color_unknown).c_str() << std::endl;

    // User implements the interface
    auto circle = taihe::core::make_holder<ColoredCircle, rgb::show::IShowable>("A", 10, color_114514);
    auto rect = show::makeColoredRectangle("B", color_yellow, 5, 5);

    circle->show();
    rect.show();
    show::copyColor(rect, circle);
    rect.show();
}
