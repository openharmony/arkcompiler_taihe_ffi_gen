#include "rgb.base.proj.hpp"
#include "rgb.show.proj.hpp"

#include <core/callback.hpp>

#include <iostream>
#include <cmath>
#include <iomanip>

using namespace rgb::base;
using namespace rgb::show;
using namespace taihe::core;

void show_array(array_view<IBase> arr, string_view sv) {
    std::cout << sv << ": ";
    for (auto item : arr) {
        std::cout << item->getId() << ", ";
    }
    std::cout << std::endl;
}

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

struct UserType {
    std::string id;

    UserType(std::string const& id) : id(id) {
        std::cout << this->getId() << " made" << std::endl;
    }

    ~UserType() {
        std::cout << this->getId() << " deleted" << std::endl;
    }

    std::string getId() { return "UserType(" + this->id + ")"; }
};

struct MyCallback {
    MyCallback() {
        std::cout << "Callback " << this << " made" << std::endl;
    }

    ~MyCallback() {
        std::cout << "Callback " << this << " deleted" << std::endl;
    }

    string operator()(string_view a, string_view b) {
        std::cout << "Callback " << this << " called" << std::endl;
        return concat(a, b);
    }
};

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

    if (string* name_ptr = color_miku.get_name_ptr()) {
        std::cout << "color_miku is holding name, name is " << *name_ptr << std::endl;
    } else {
        std::cout << "Error" << std::endl;
    }

    if (color_miku.holds_name()) {
        string& name_ref = color_miku.get_name_ref();
        std::cout << "color_miku is holding name, name is " << name_ref << std::endl;
    } else {
        std::cout << "Error" << std::endl;
    }

    color_miku.emplace_rgb(RGB{0x39, 0xC5, 0xBB});
    std::cout << toString(color_miku) << std::endl;

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
    auto circle_original = make_holder<ColoredCircle, IShowable>("A", 10, color_114514);
    weak::IShowable circle_ref = circle_original;
    IShowable rect = makeColoredRectangle("B", color_yellow, 5, 5);
    Color color_single = Color::make_yellow();

    circle_original->show();
    circle_ref->show();
    rect->show();
    copyColor(rect, circle_ref);
    rect->show();

    // array
    {
        std::cout << "-------- Testing Arr --------" << std::endl;
        auto dst = array<IBase>(10, circle_ref);
        auto src = array<IBase>(4, rect);
        show_array(dst, "dst");
        show_array(src, "src");
        auto res = exchange(dst, src);
        show_array(dst, "dst");
        show_array(src, "src");
        show_array(res, "res");
    }

    // vector
    {
        std::cout << "-------- Testing Vec --------" << std::endl;
        vector<IBase> vec_0;
        vector<IBase> vec_1 = vec_0;
        fillVec(vec_0);
        for (int i = 0; i < vec_1.size(); i++) {
            std::cout << vec_1[i]->getId() << std::endl;
        }
    }

    // map
    {
        std::cout << "-------- Testing Map --------" << std::endl;
        map<string, IBase> map_0;
        map<string, IBase> map_1 = map_0;
        map_0.emplace<0>("a", make_holder<UserType, IBase>("a"));
        map_0.emplace<0>("b", make_holder<UserType, IBase>("b"));
        fillMap(map_0);
        if (auto ptr = map_1.find("a")) {
            std::cout << "a: " << (*ptr)->getId() << std::endl;
        }
        if (auto ptr = map_1.find("b")) {
            std::cout << "b: " << (*ptr)->getId() << std::endl;
        }
        if (auto ptr = map_1.find("c")) {
            std::cout << "c: " << (*ptr)->getId() << std::endl;
        }
        if (auto ptr = map_1.find("d")) {
            std::cout << "d: " << (*ptr)->getId() << std::endl;
        }
    }

    // set
    {
        std::cout << "-------- Testing Set --------" << std::endl;
        set<string> set_0;
        set<string> set_1 = set_0;
        set_0.emplace("a");
        fillSet(set_0);
        if (set_1.find("a")) {
            std::cout << "a exists" << std::endl;
        }
        if (set_1.find("b")) {
            std::cout << "b exists" << std::endl;
        }
        if (set_1.find("c")) {
            std::cout << "c exists" << std::endl;
        }
    }

    {
        std::cout << "-------- Testing Callback --------" << std::endl;
        auto cb_0 = make_callback<MyCallback, string, string_view, string_view>();
        auto cb_1 = cb_0;
        auto res = cb_1("abc", "123");
        std::cout << "res = " << res << std::endl;
    }
}
