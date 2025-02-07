#include "rgb.base.proj.hpp"
#include "rgb.show.proj.hpp"

#include <iostream>
#include <cmath>
#include <iomanip>

using namespace rgb::base;
using namespace rgb::show;
using namespace taihe::core;

class ColoredCircle {
    float r;
    std::string name;

    ColorOrRGBOrName myColor;

public:
    ColoredCircle(string_view id, float r, ColorOrRGBOrName const& color)
        : name(id), r(r), myColor(color) {
        std::cout << "new " << this << std::endl;
    }

    ~ColoredCircle() {
        std::cout << "del " << this << std::endl;
    }

    string getId() {
        return name;
    }

    float calculateArea() {
        return M_PI * r * r;
    }

    ColorOrRGBOrName getColor() {
        return myColor;
    }

    void setColor(ColorOrRGBOrName const& color) {
        myColor = color;
    }

    void show() {
        std::string content = "circle " + name + ": r = " + std::to_string(r);
        if (auto ptr = myColor.get_ptr<ColorOrRGBOrName::tag_t::color>()) {
            std::cout << "\033[" << 30 + (int)ptr->get_tag() << "m" << content << "\033[39m" << std::endl;
        } else if (auto ptr = myColor.get_ptr<ColorOrRGBOrName::tag_t::rgb>()) {
            std::cout << "\033[38;2;" << (int)ptr->r << ";" << (int)ptr->g << ";" << (int)ptr->b << "m" << content << "\033[39m" << std::endl;
        } else if (auto ptr = myColor.get_ptr<ColorOrRGBOrName::tag_t::name>()) {
            std::cout << "(" << ptr->c_str() << ") " << content << std::endl;
        } else {
            std::cout << content << std::endl;
        }
    }
};

void show_array(array_view<IBase> arr, string_view sv) {
    std::cout << sv << ": ";
    for (auto item : arr) {
        std::cout << item.getId() << ", ";
    }
    std::cout << std::endl;
}

int main() {
    Color yellow = Color::make_yellow();
    ColorOrRGBOrName color_114514 = ColorOrRGBOrName::make_rgb(RGB{0x11, 0x45, 0x14});
    ColorOrRGBOrName color_yellow = ColorOrRGBOrName::make_color(yellow);
    ColorOrRGBOrName color_miku = ColorOrRGBOrName::make_name("Miku");
    ColorOrRGBOrName color_unknown = ColorOrRGBOrName::make_undefined();

    std::cout << toString(color_114514) << std::endl;
    std::cout << toString(color_yellow) << std::endl;
    std::cout << toString(color_miku) << std::endl;
    std::cout << toString(color_unknown) << std::endl;

    if (string* safe_ptr = color_miku.get_name_ptr(); safe_ptr != nullptr) {
        std::cout << "color_miku is holding name, name is " << *safe_ptr << std::endl;
    } else {
        std::cout << "Error" << std::endl;
    }

    if (color_miku.holds_name()) {
        string& color_ptr_name_ref = color_miku.get_name_ref();
        std::cout << "color_miku is holding name, name is " << color_ptr_name_ref << std::endl;
    } else {
        std::cout << "Error" << std::endl;
    }

    color_miku.emplace_rgb(RGB{0x39, 0xC5, 0xBB});
    std::cout << toString(color_miku) << std::endl;

    rgb::base::ColorOrRGBOrName::tag_t tag = color_miku.get_tag();
    switch (color_miku.get_tag()) {
    case ColorOrRGBOrName::tag_t::color:
        std::cout << "color_miku is holding color" << std::endl;
        break;
    case ColorOrRGBOrName::tag_t::rgb:
        std::cout << "color_miku is holding rgb" << std::endl;
        break;
    case ColorOrRGBOrName::tag_t::name:
        std::cout << "color_miku is holding name" << std::endl;
        break;
    default:
        std::cout << "color_miku is holding other stuff" << std::endl;
        break;
    }

    // User implements the interface
    auto circle = make_holder<ColoredCircle, IShowable>("A", 10, color_114514);
    auto rect = makeColoredRectangle("B", color_yellow, 5, 5);
    Color color_single = Color::make_yellow();
    weak::IShowable circle_as_showable = circle;

    circle->show();
    circle_as_showable.show();
    rect.show();
    copyColor(rect, circle);
    rect.show();

    auto dst = array<IBase>(10, circle);
    auto src = array<IBase>(4, rect);
    show_array(dst, "dst");
    show_array(src, "src");
    auto res = exchange(dst, src);
    show_array(dst, "dst");
    show_array(src, "src");
    show_array(res, "res");

    vector<IBase> vec;
    fill(vec);
    for (int i = 0; i < vec.size(); i++) {
        std::cout << vec[i].getId() << std::endl;
    }
}
