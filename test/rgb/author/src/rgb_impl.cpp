#include "rgb.show.proj.hpp"
#include "rgb.base.proj.hpp"
#include "rgb.show.impl.hpp"
#include "rgb.base.impl.hpp"

#include <iostream>
#include <iomanip>
#include <variant>

using namespace rgb::base;
using namespace rgb::show;
using namespace taihe::core;

class Rectangle {
protected:
    float h;
    float w;
    std::string name;

public:
    Rectangle(string_view id, float h, float w)
        : name(id), h(h), w(w) {
        std::cout << "new " << this << std::endl;
    }

    ~Rectangle() {
        std::cout << "del " << this << std::endl;
    }

    string getId() {
        return name;
    }

    float calculateArea() {
        return h * w;
    }
};

IShape makeRectangleImpl(string_view id, float h, float w) {
    return make_holder<Rectangle, IShape>(id, h, w);
}

class ColoredRectangle : public Rectangle {
    ColorOrRGBOrName myColor;

public:
    ColoredRectangle(string_view id, float h, float w, ColorOrRGBOrName const& color)
        : Rectangle(id, h, w), myColor(color) {}

    ColorOrRGBOrName getColor() {
        return myColor;
    }

    void setColor(ColorOrRGBOrName const& color) {
        myColor = color;
    }

    void show() {
        std::string content = "rectangle " + name + ": h = " + std::to_string(h) + ", w = " + std::to_string(w);
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

IShowable makeColoredRectangleImpl(string_view id, ColorOrRGBOrName const& color, float h, float w) {
    return make_holder<ColoredRectangle, IShowable>(id, h, w, color);
}

void copyColorImpl(weak::IColorable dst, weak::IColorable src) {
    dst.setColor(src.getColor());
}

struct Visitor {
    string operator()(static_tag_t<ColorOrRGBOrName::tag_t::rgb>, auto& val) {
        std::ostringstream oss;
        oss << "#" << std::hex << std::setfill('0')
            << std::setw(2) << static_cast<int>(val.r)
            << std::setw(2) << static_cast<int>(val.g)
            << std::setw(2) << static_cast<int>(val.b)
            ;
        return oss.str();
    }
    string operator()(static_tag_t<ColorOrRGBOrName::tag_t::name>, auto& val) {
        std::ostringstream oss;
        oss << "Name: " << val.c_str();
        return oss.str();
    }
    string operator()(static_tag_t<ColorOrRGBOrName::tag_t::color>, auto& val) {
        return val.accept_template(*this);
    }
    string operator()(static_tag_t<Color::tag_t::black>) {
        return "Black";
    }
    string operator()(static_tag_t<Color::tag_t::red>) {
        return "Red";
    }
    string operator()(static_tag_t<Color::tag_t::green>) {
        return "Green";
    }
    string operator()(static_tag_t<Color::tag_t::yellow>) {
        return "Yellow";
    }
    string operator()(static_tag_t<Color::tag_t::blue>) {
        return "Blue";
    }
    string operator()(static_tag_t<Color::tag_t::magenta>) {
        return "Magenta";
    }
    string operator()(static_tag_t<Color::tag_t::cyan>) {
        return "Cyan";
    }
    string operator()(static_tag_t<Color::tag_t::white>) {
        return "White";
    }
    string operator()(static_tag_t<ColorOrRGBOrName::tag_t::undefined>) {
        return "Undefined";
    }
};

string colorToStringImpl(ColorOrRGBOrName const& color) {
    return color.accept_template(Visitor());
}

TH_EXPORT_CPP_API_makeRectangle(makeRectangleImpl)
TH_EXPORT_CPP_API_makeColoredRectangle(makeColoredRectangleImpl)
TH_EXPORT_CPP_API_copyColor(copyColorImpl)
TH_EXPORT_CPP_API_toString(colorToStringImpl)
