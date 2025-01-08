#include "rgb.show.proj.hpp"
#include "rgb.base.proj.hpp"
#include "rgb.show.impl.hpp"
#include "rgb.base.impl.hpp"

#include <iostream>
#include <iomanip>
#include <variant>

class Rectangle {
protected:
    float h;
    float w;
    std::string name;

public:
    Rectangle(taihe::core::string_view id, float h, float w)
        : name(id), h(h), w(w) {
        std::cout << "new " << this << std::endl;
    }

    ~Rectangle() {
        std::cout << "del " << this << std::endl;
    }

    taihe::core::string getId() {
        return name;
    }

    float calculateArea() {
        return h * w;
    }
};

rgb::show::IShape makeRectangleImpl(taihe::core::string_view id, float h, float w) {
    return taihe::core::make_holder<Rectangle, rgb::show::IShape>(id, h, w);
}

class ColoredRectangle : public Rectangle {
    rgb::base::ColorOrRGBOrName myColor;

public:
    ColoredRectangle(taihe::core::string_view id, float h, float w, rgb::base::ColorOrRGBOrName const& color)
        : Rectangle(id, h, w), myColor(color) {}

    rgb::base::ColorOrRGBOrName getColor() {
        return myColor;
    }

    void setColor(rgb::base::ColorOrRGBOrName const& color) {
        myColor = color;
    }

    void show() {
        std::string content = "rectangle " + name + ": h = " + std::to_string(h) + ", w = " + std::to_string(w);
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

rgb::show::IShowable makeColoredRectangleImpl(taihe::core::string_view id, rgb::base::ColorOrRGBOrName const& color, float h, float w) {
    return taihe::core::make_holder<ColoredRectangle, rgb::show::IShowable>(id, h, w, color);
}

void copyColorImpl(weak::rgb::show::IColorable dst, weak::rgb::show::IColorable src) {
    dst.setColor(src.getColor());
}

using taihe::core::static_tag_t;

struct Visitor {
    taihe::core::string operator()(static_tag_t<rgb::base::ColorOrRGBOrName::tag_t::rgb>, auto& val) {
        std::ostringstream oss;
        oss << "#" << std::hex << std::setfill('0')
            << std::setw(2) << static_cast<int>(val.r)
            << std::setw(2) << static_cast<int>(val.g)
            << std::setw(2) << static_cast<int>(val.b)
            ;
        return oss.str();
    }
    taihe::core::string operator()(static_tag_t<rgb::base::ColorOrRGBOrName::tag_t::name>, auto& val) {
        std::ostringstream oss;
        oss << "Name: " << val.c_str();
        return oss.str();
    }
    taihe::core::string operator()(static_tag_t<rgb::base::ColorOrRGBOrName::tag_t::color>, auto& val) {
        return val.accept_template(*this);
    }
    taihe::core::string operator()(static_tag_t<rgb::base::Color::tag_t::black>) {
        return "Black";
    }
    taihe::core::string operator()(static_tag_t<rgb::base::Color::tag_t::red>) {
        return "Red";
    }
    taihe::core::string operator()(static_tag_t<rgb::base::Color::tag_t::green>) {
        return "Green";
    }
    taihe::core::string operator()(static_tag_t<rgb::base::Color::tag_t::yellow>) {
        return "Yellow";
    }
    taihe::core::string operator()(static_tag_t<rgb::base::Color::tag_t::blue>) {
        return "Blue";
    }
    taihe::core::string operator()(static_tag_t<rgb::base::Color::tag_t::magenta>) {
        return "Magenta";
    }
    taihe::core::string operator()(static_tag_t<rgb::base::Color::tag_t::cyan>) {
        return "Cyan";
    }
    taihe::core::string operator()(static_tag_t<rgb::base::Color::tag_t::white>) {
        return "White";
    }
    taihe::core::string operator()(static_tag_t<rgb::base::ColorOrRGBOrName::tag_t::undefined>) {
        return "Undefined";
    }
};

taihe::core::string colorToStringImpl(rgb::base::ColorOrRGBOrName const& color) {
    return color.accept_template(Visitor());
}

TH_EXPORT_CPP_API_makeRectangle(makeRectangleImpl)
TH_EXPORT_CPP_API_makeColoredRectangle(makeColoredRectangleImpl)
TH_EXPORT_CPP_API_copyColor(copyColorImpl)
TH_EXPORT_CPP_API_toString(colorToStringImpl)
