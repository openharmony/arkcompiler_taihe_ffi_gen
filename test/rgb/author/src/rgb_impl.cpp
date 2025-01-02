#include "rgb.show.proj.hpp"
#include "rgb.base.proj.hpp"
#include "rgb.show.impl.hpp"
#include "rgb.base.impl.hpp"

#include <iostream>
#include <iomanip>

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
    return taihe::core::makeInterface<rgb::show::IShape, Rectangle>(id, h, w);
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
        std::string content = name + ": " + std::to_string(h) + "x" + std::to_string(w);
        if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::TagType::color>()) {
            std::string colorCode = "\033[" + std::to_string(30 + (int)ptr->get_tag()) + "m";
            std::cout << colorCode << content << "\033[39m" << std::endl;
        } else if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::TagType::rgb>()) {
            std::cout << "\033[38;2;" << (int)ptr->r << ";" << (int)ptr->g << ";" << (int)ptr->b << "m" << content << "\033[39m" << std::endl;
        } else if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::TagType::name>()) {
            std::cout << "(" << ptr->c_str() << ") " << content << std::endl;
        } else {
            std::cout << content << std::endl;
        }
    }
};

rgb::show::IShowable makeColoredRectangleImpl(taihe::core::string_view id, rgb::base::ColorOrRGBOrName const& color, float h, float w) {
    return taihe::core::makeInterface<rgb::show::IShowable, ColoredRectangle>(id, h, w, color);
}

void copyColorImpl(param::rgb::show::IColorable dst, param::rgb::show::IColorable src) {
    dst.setColor(src.getColor());
}

taihe::core::string colorToStringImpl(rgb::base::ColorOrRGBOrName const& color) {
    if (auto ptr = color.get_ptr<rgb::base::ColorOrRGBOrName::TagType::color>()) {
        return "Color(" + std::to_string((int)ptr->get_tag()) + ")";
    } else if (auto ptr = color.get_ptr<rgb::base::ColorOrRGBOrName::TagType::rgb>()) {
        std::ostringstream oss;
        oss << "#"
        << std::hex << std::setfill('0') << std::setw(2) << static_cast<int>(ptr->r)
        << std::setw(2) << static_cast<int>(ptr->g)
        << std::setw(2) << static_cast<int>(ptr->b);
        return oss.str();
    } else if (auto ptr = color.get_ptr<rgb::base::ColorOrRGBOrName::TagType::name>()) {
        return ptr->c_str();
    } else {
        return "Error";
    }
}

TH_EXPORT_CPP_API_makeRectangle(makeRectangleImpl)
TH_EXPORT_CPP_API_makeColoredRectangle(makeColoredRectangleImpl)
TH_EXPORT_CPP_API_copyColor(copyColorImpl)
TH_EXPORT_CPP_API_toString(colorToStringImpl)
