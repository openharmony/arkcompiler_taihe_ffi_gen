#include <cmath>
#include <core/callback.hpp>
#include <cstddef>
#include <iomanip>
#include <iostream>

#include "core/object.hpp"
#include "rgb.base.proj.hpp"
#include "rgb.show.proj.hpp"

using namespace rgb::base;
using namespace rgb::show;
using namespace taihe::core;

struct UserType {
  string id;

  auto getId() { return "UserType(" + std::string(id) + ")"; }

  void userMethod() { std::cout << "User Method Called;" << std::endl; }

  UserType(string_view id) : id(id) {
    std::cout << getId() << " made" << std::endl;
  }

  ~UserType() { std::cout << getId() << " deleted" << std::endl; }
};

int main() {
  ColorOrRGBOrName color_114514 =
      ColorOrRGBOrName::make_rgb(RGB{0x11, 0x45, 0x14});
  ColorOrRGBOrName color_yellow =
      ColorOrRGBOrName::make_color(Color::key_t::yellow);
  ColorOrRGBOrName color_miku = ColorOrRGBOrName::make_name(Name::key_t::BLUE);
  ColorOrRGBOrName color_unknown = ColorOrRGBOrName::make_undefined();

  {
    std::cout << "-------- Testing Union --------" << std::endl;

    std::cout << toString(color_114514) << std::endl;
    std::cout << toString(color_yellow) << std::endl;
    std::cout << toString(color_miku) << std::endl;
    std::cout << toString(color_unknown) << std::endl;

    if (Name* name_ptr = color_miku.get_name_ptr()) {
      std::cout << "color_miku is holding name, name is " << *name_ptr
                << std::endl;
    } else {
      std::cout << "Error" << std::endl;
    }

    if (color_miku.holds_name()) {
      Name name_ref = color_miku.get_name_ref();
      std::cout << "color_miku is holding name, name is " << name_ref
                << std::endl;
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
  }

  {
    std::cout << "-------- Testing Interface Call --------" << std::endl;

    class MyColoredObject {
      std::string name;

      ColorOrRGBOrName myColor;

     public:
      string getId() { return name; }

      MyColoredObject(string_view id, ColorOrRGBOrName const& color)
          : name(id), myColor(color) {
        std::cout << getId() << " made" << std::endl;
      }

      ~MyColoredObject() { std::cout << getId() << " deleted" << std::endl; }

      ColorOrRGBOrName getColor() { return myColor; }

      void setColor(ColorOrRGBOrName const& color) { myColor = color; }
    };

    IColorable colored_circ =
        make_holder<MyColoredObject, IColorable>("Circ", color_114514);
    IShowable colored_rect = makeColoredRectangle("Rect", color_yellow, 5, 5);

    colored_rect->show();
    copyColor(colored_rect, colored_circ);
    colored_rect->show();

    impl_holder<UserType, IBase> obj = make_holder<UserType, IBase>("obj");

    // `impl_holder<Impl, Iface...>` can call methods of Impl itself that are
    // not defined in the interface.
    obj->userMethod();
  }

  {
    std::cout << "-------- Testing Interface Cast --------" << std::endl;

    IBase ibase_a = makeColoredRectangle("A", color_yellow, 1, 2);
    IBase ibase_b = makeRectangle("B", 3, 4);

    if (weak::IColorable icolorable_a = weak::IColorable(ibase_a)) {
      std::cout << "A Dynamic Cast success" << std::endl;
    } else {
      std::cout << "A Dynamic Cast failed" << std::endl;
    }

    if (weak::IColorable icolorable_b = weak::IColorable(ibase_b)) {
      std::cout << "B Dynamic Cast success" << std::endl;
    } else {
      std::cout << "B Dynamic Cast failed" << std::endl;
    }

    // You can also dynamic cast a `data_holder`.
    data_holder obj = make_holder<UserType, IBase>("obj");

    if (weak::IBase obj_as_ibase = weak::IBase(obj)) {
      std::cout << "obj Dynamic Cast success" << std::endl;
    } else {
      std::cout << "obj Dynamic Cast failed" << std::endl;
    }
  }

  {
    std::cout << "-------- Testing Array --------" << std::endl;

    auto show_array = [](array_view<IBase> arr, string_view sv) {
      std::cout << sv << ": ";
      for (auto item : arr) {
        std::cout << item->getId() << ", ";
      }
      std::cout << std::endl;
    };

    auto dst = array<IBase>::make(5, make_holder<UserType, IBase>("x"));
    auto src = array<IBase>::make(2, make_holder<UserType, IBase>("y"));

    show_array(dst, "dst");
    show_array(src, "src");

    auto res = exchangeArr(dst, src);

    show_array(dst, "dst");
    show_array(src, "src");
    show_array(res, "res");
  }

  {
    std::cout << "-------- Testing Optional --------" << std::endl;

    IBase obj = make_holder<UserType, IBase>("some");

    testOptional(&obj);
    testOptional(NULL);
  }

  {
    std::cout << "-------- Testing Vector --------" << std::endl;

    vector<IBase> vec_0;
    vector<IBase> vec_1 = vec_0;

    fillVec(vec_0);

    std::cout << "Vector = ";
    for (int i = 0; i < vec_1.size(); i++) {
      std::cout << vec_1[i]->getId() << ", ";
    }
    std::cout << std::endl;
  }

  {
    std::cout << "-------- Testing Map --------" << std::endl;

    map<string, IBase> map_0;
    map<string, IBase> map_1 = map_0;

    map_0.emplace<0>("a", make_holder<UserType, IBase>("a"));
    map_0.emplace<0>("b", make_holder<UserType, IBase>("b"));

    fillMap(map_0);

    std::cout << "Map = ";
    map_1.accept([](string_view key, weak::IBase value) {
      std::cout << key << ": " << value->getId() << ", ";
    });
    std::cout << std::endl;
  }

  {
    std::cout << "-------- Testing Set --------" << std::endl;

    set<string> set_0;
    set<string> set_1 = set_0;

    set_0.emplace("a");

    fillSet(set_0);

    std::cout << "Set = ";
    set_1.accept([](string_view key) { std::cout << key << ", "; });
    std::cout << std::endl;
  }

  {
    std::cout << "-------- Testing Callback --------" << std::endl;

    struct MyCallback {
      string f;

      MyCallback(string_view f) : f(f) {
        std::cout << "Callback " << f << " made" << std::endl;
      }

      ~MyCallback() {
        std::cout << "Callback " << f << " deleted" << std::endl;
      }

      string operator()(string_view a, string_view b) {
        std::cout << "Callback " << f << " called" << std::endl;
        return std::string(f) + "(" + a.c_str() + ", " + b.c_str() + ")";
      }
    };

    auto tmp =
        currying(callback<string(string_view, string_view)>::from<MyCallback>(
            "f"))("abc");
    auto res = tmp("123");

    std::cout << "res = " << res << std::endl;
  }
}
