#include "rgb.show.proj.hpp"
#include "rgb.base.proj.hpp"
#include "rgb.show.impl.hpp"
#include "rgb.base.impl.hpp"

#include <iostream>
#include <format>

class Rectangle {
protected:
    float h;
    float w;

    std::string name;

public:
    Rectangle(taihe::core::string_view id, float h, float w)
        : name(id), h(h), w(w) {
        std::cout << std::format("new 0x{:016x}", (size_t)((void*)this)) << std::endl;
    }

    ~Rectangle() {
        std::cout << std::format("del 0x{:016x}", (size_t)((void*)this)) << std::endl;
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
        std::string content = std::format("{}: {}x{}", name, h, w);
        if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::TagType::color>()) {
            std::cout << std::format("\033[{}m{}\033[39m", 30 + (int)ptr->tag, content) << std::endl;
        } else if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::TagType::rgb>()) {
            std::cout << std::format("\033[38;2;{};{};{}m{}\033[39m", ptr->r, ptr->g, ptr->b, content) << std::endl;
        } else if (auto ptr = myColor.get_ptr<rgb::base::ColorOrRGBOrName::TagType::name>()) {
            std::cout << std::format("({}) {}", ptr->c_str(), content) << std::endl;
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
        return std::format("Color({})", (int)ptr->tag);
    } else if (auto ptr = color.get_ptr<rgb::base::ColorOrRGBOrName::TagType::rgb>()) {
        return std::format("#{:02x}{:02x}{:02x}", ptr->r, ptr->g, ptr->b);
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
