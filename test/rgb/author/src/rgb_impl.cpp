#include <iomanip>
#include <iostream>
#include <string>
#include <variant>

#include "rgb.base.impl.hpp"
#include "rgb.show.impl.hpp"

using namespace rgb::base;
using namespace rgb::show;
using namespace taihe;

class Rectangle {
protected:
  float h;
  float w;
  std::string name;

public:
  string getId() {
    return name;
  }

  Rectangle(string_view id, float h, float w) : h(h), w(w), name(id) {
    std::cout << getId() << " made" << std::endl;
  }

  ~Rectangle() {
    std::cout << getId() << " deleted" << std::endl;
  }

  float calculateArea() {
    return h * w;
  }
};

class ColoredRectangle : public Rectangle {
  ColorOrRGBOrName myColor;

public:
  ColoredRectangle(string_view id, float h, float w,
                   ColorOrRGBOrName const &color)
      : Rectangle(id, h, w), myColor(color) {}

  ColorOrRGBOrName getColor() {
    return myColor;
  }

  void setColor(ColorOrRGBOrName const &color) {
    myColor = color;
  }

  void show() {
    std::string content = "rectangle " + name + ": h = " + std::to_string(h) +
                          ", w = " + std::to_string(w);
    if (auto color_ptr = myColor.get_ptr<ColorOrRGBOrName::tag_t::color>()) {
      std::cout << "\033[" << 30 + (int)*color_ptr << "m" << content
                << "\033[39m" << std::endl;
    } else if (auto rgb_ptr = myColor.get_ptr<ColorOrRGBOrName::tag_t::rgb>()) {
      std::cout << "\033[38;2;" << (int)rgb_ptr->r << ";" << (int)rgb_ptr->g
                << ";" << (int)rgb_ptr->b << "m" << content << "\033[39m"
                << std::endl;
    } else if (auto name_ptr =
                   myColor.get_ptr<ColorOrRGBOrName::tag_t::name>()) {
      std::cout << "(" << *name_ptr << ") " << content << std::endl;
    } else {
      std::cout << content << std::endl;
    }
  }
};

IShape makeRectangleImpl(string_view id, float h, float w) {
  return make_holder<Rectangle, IShape>(id, h, w);
}

IShowable makeColoredRectangleImpl(string_view id,
                                   ColorOrRGBOrName const &color, float h,
                                   float w) {
  return make_holder<ColoredRectangle, IShowable>(id, h, w, color);
}

void copyColorImpl(weak::IColorable dst, weak::IColorable src) {
  std::cout << "copying color form " << weak::IBase(src)->getId() << " to "
            << weak::IBase(dst)->getId() << "." << std::endl;
  dst->setColor(src->getColor());
}

string colorToStringImpl(ColorOrRGBOrName const &color) {
  static struct Visitor {
    string operator()(static_tag_t<ColorOrRGBOrName::tag_t::rgb>,
                      const RGB &val) {
      std::ostringstream oss;
      oss << "#" << std::hex << std::setfill('0') << std::setw(2)
          << static_cast<int>(val.r) << std::setw(2) << static_cast<int>(val.g)
          << std::setw(2) << static_cast<int>(val.b);
      return oss.str();
    }

    string operator()(static_tag_t<ColorOrRGBOrName::tag_t::name>,
                      string const &val) {
      std::ostringstream oss;
      oss << "Name: " << val.c_str();
      return oss.str();
    }

    string operator()(static_tag_t<ColorOrRGBOrName::tag_t::color>,
                      Color const &val) {
      return std::to_string(val.get_value());
    }

    string operator()(static_tag_t<ColorOrRGBOrName::tag_t::name>,
                      Name const &val) {
      return string(val);
    }

    string operator()(static_tag_t<ColorOrRGBOrName::tag_t::undefined>) {
      return "Undefined";
    }
  } visitor;

  return color.accept_template(visitor);
}

array<IBase> exchangeArrImpl(array_view<IBase> dst, array_view<IBase> src) {
  auto n = std::min(dst.size(), src.size());
  auto res = array<IBase>(move_data_t{}, dst.data(), n);
  for (std::size_t i = 0; i < n; i++) {
    dst[i] = src[i];
  }
  return res;
}

void testOptionalImpl(optional_view<IBase> optional) {
  if (optional) {
    std::cout << "optional is not empty, " << (*optional)->getId()
              << " is in the optional" << std::endl;
  } else {
    std::cout << "optional is empty" << std::endl;
  }
}

struct AuthorType {
  string id;

  auto getId() {
    return "AuthorType(" + std::string(id) + ")";
  }

  AuthorType(string_view id) : id(id) {
    std::cout << getId() << " made" << std::endl;
  }

  ~AuthorType() {
    std::cout << getId() << " deleted" << std::endl;
  }
};

void fillVecImpl(vector_view<IBase> target) {
  target.push_back(make_holder<AuthorType, IBase>("0"));
  target.push_back(make_holder<AuthorType, IBase>("1"));
  target.push_back(make_holder<AuthorType, IBase>("2"));
}

void fillMapImpl(map_view<string, IBase> target) {
  target.emplace<1>("a", make_holder<AuthorType, IBase>("a"));
  target.emplace<0>("b", make_holder<AuthorType, IBase>("b"));
  target.emplace<0>("c", make_holder<AuthorType, IBase>("c"));
}

void fillSetImpl(set_view<string> target) {
  target.emplace("a");
  target.emplace("b");
}

callback<callback<string(string_view)>(string_view)> curryingImpl(
    callback_view<string(string_view, string_view)> f) {
  return callback<callback<string(string_view)>(string_view)>::from(
      [f = callback<string(string_view, string_view)>(f)](
          string_view x) -> callback<string(string_view)> {
        return callback<string(string_view)>::from(
            [f = f, x = string(x)](string_view y) -> string {
              return f(x, y);
            });
      });
}

TH_EXPORT_CPP_API_makeRectangle(makeRectangleImpl);
TH_EXPORT_CPP_API_makeColoredRectangle(makeColoredRectangleImpl);
TH_EXPORT_CPP_API_copyColor(copyColorImpl);
TH_EXPORT_CPP_API_toString(colorToStringImpl);
TH_EXPORT_CPP_API_exchangeArr(exchangeArrImpl);
TH_EXPORT_CPP_API_testOptional(testOptionalImpl);
TH_EXPORT_CPP_API_fillVec(fillVecImpl);
TH_EXPORT_CPP_API_fillMap(fillMapImpl);
TH_EXPORT_CPP_API_fillSet(fillSetImpl);
TH_EXPORT_CPP_API_currying(curryingImpl);
