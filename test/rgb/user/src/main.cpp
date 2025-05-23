#include <cmath>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <optional>
#include <taihe/callback.hpp>
#include <taihe/object.hpp>
#include <unordered_map>
#include <unordered_set>

#include "rgb.base.user.hpp"
#include "rgb.show.user.hpp"

using namespace rgb::base;
using namespace rgb::show;
using namespace taihe;

string toString(ColorOrRGBOrName const &color) {
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

struct UserType {
  static inline std::unordered_set<UserType *> registry;

private:
  string id;
  ColorOrRGBOrName myColor;

public:
  auto getId() {
    return "UserType(" + std::string(id) + ")";
  }

  void userMethod() {
    std::cout << "User Method Called;" << std::endl;
  }

  void setColor(ColorOrRGBOrName const &color) {
    myColor = color;
  }

  ColorOrRGBOrName getColor() {
    return myColor;
  }

  UserType(string_view id, ColorOrRGBOrName const &color)
      : id(id), myColor(color) {
    std::cout << getId() << " made" << std::endl;
    registry.insert(this);
  }

  ~UserType() {
    std::cout << getId() << " deleted" << std::endl;
    registry.erase(this);
  }

  UserType(string_view id) : UserType(id, ColorOrRGBOrName::make_undefined()) {}
};

static ColorOrRGBOrName color_114514 =
    ColorOrRGBOrName::make_rgb(RGB{0x11, 0x45, 0x14});
static ColorOrRGBOrName color_yellow =
    ColorOrRGBOrName::make_color(Color::key_t::yellow);
static ColorOrRGBOrName color_miku =
    ColorOrRGBOrName::make_name(Name::key_t::BLUE);
static ColorOrRGBOrName color_unknown = ColorOrRGBOrName::make_undefined();

bool testUnion() {
  std::cout << toString(color_114514) << std::endl;
  std::cout << toString(color_yellow) << std::endl;
  std::cout << toString(color_miku) << std::endl;
  std::cout << toString(color_unknown) << std::endl;

  if (Name *name_ptr = color_miku.get_name_ptr()) {
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

  return true;
}

bool testInterfaceCall() {
  IColorable colored_circ =
      make_holder<UserType, IColorable>("Circ", color_114514);
  IShowable colored_rect = makeColoredRectangle("Rect", color_yellow, 5, 5);

  if (!same(weak::IColorable(colored_rect)->getColor(), color_yellow)) {
    return false;
  }

  copyColor(colored_rect, colored_circ);

  if (!same(weak::IColorable(colored_rect)->getColor(), color_114514)) {
    return false;
  }

  return true;
}

bool testInterfaceCast() {
  IBase ibase_a = makeColoredRectangle("A", color_yellow, 1, 2);
  IBase ibase_b = makeRectangle("B", 3, 4);

  bool good_cast;
  if (weak::IColorable icolorable_a = weak::IColorable(ibase_a)) {
    std::cout << "A Dynamic Cast success" << std::endl;
    good_cast = true;
  } else {
    std::cout << "A Dynamic Cast failed" << std::endl;
    good_cast = false;
  }

  bool bad_cast;
  if (weak::IColorable icolorable_b = weak::IColorable(ibase_b)) {
    std::cout << "B Dynamic Cast success" << std::endl;
    bad_cast = true;
  } else {
    std::cout << "B Dynamic Cast failed" << std::endl;
    bad_cast = false;
  }

  return good_cast && !bad_cast;
}

bool testArray() {
  std::size_t m = 5;
  std::size_t n = 2;

  auto x = make_holder<UserType, IBase>("x");
  auto y = make_holder<UserType, IBase>("y");

  auto dst = array<IBase>::make(m, x);
  auto src = array<IBase>::make(n, y);

  auto res = exchangeArr(dst, src);

  if (dst.size() != m || src.size() != n || res.size() != n) {
    return false;
  }
  for (int i = 0; i < n; i++) {
    if (!same(src[i], y) || !same(dst[i], y) || !same(res[i], x)) {
      return false;
    }
  }
  for (int i = n; i < m; i++) {
    if (!same(dst[i], x)) {
      return false;
    }
  }

  return true;
}

bool testOptional() {
  auto some =
      optional<IBase>(std::in_place, make_holder<UserType, IBase>("some"));
  auto some_str = getIdFromOptional(some);
  if (!some_str.has_value() || some_str.value() != some.value()->getId()) {
    return false;
  }

  auto none = optional<IBase>(std::nullopt);
  auto none_str = getIdFromOptional(none);
  if (none_str.has_value()) {
    return false;
  }

  return true;
}

bool testVector() {
  array<IBase> src = {
      make_holder<UserType, IBase>("a"),
      make_holder<UserType, IBase>("b"),
      make_holder<UserType, IBase>("c"),
  };

  vector<IBase> res = makeVec(src);
  if (res.size() != src.size()) {
    return false;
  }
  for (size_t i = 0; i < src.size(); i++) {
    if (res[i]->getId() != src[i]->getId()) {
      return false;
    }
  }

  vector<IBase> buf;
  fillVec(src, buf);
  if (buf.size() != src.size()) {
    return false;
  }
  for (size_t i = 0; i < src.size(); i++) {
    if (buf[i]->getId() != src[i]->getId()) {
      return false;
    }
  }

  return true;
}

bool testMap() {
  array<string> keys = {"a", "b", "c", "a"};
  array<IBase> src = {
      make_holder<UserType, IBase>("a"),
      make_holder<UserType, IBase>("b"),
      make_holder<UserType, IBase>("c"),
      make_holder<UserType, IBase>("d"),
  };

  std::unordered_map<std::string, IBase> expected;
  size_t n = std::min(keys.size(), src.size());
  for (size_t i = 0; i < n; i++) {
    expected.emplace(std::string(keys[i]), src[i]);
  }

  map<string, IBase> res = makeMap(keys, src);
  if (res.size() != expected.size()) {
    return false;
  }
  for (auto const &[key, value] : expected) {
    auto it = res.find_item(key);
    if (!it || it->second->getId() != value->getId()) {
      return false;
    }
  }

  map<string, IBase> buf;
  fillMap(keys, src, buf);
  if (buf.size() != expected.size()) {
    return false;
  }
  for (auto const &[key, value] : expected) {
    auto it = buf.find_item(key);
    if (!it || it->second->getId() != value->getId()) {
      return false;
    }
  }

  return true;
}

bool testSet() {
  array<string> src = {"a", "b", "c", "a"};

  std::unordered_set<std::string> expected;
  for (size_t i = 0; i < src.size(); i++) {
    expected.emplace(std::string(src[i]));
  }

  set<string> res = makeSet(src);
  if (res.size() != expected.size()) {
    return false;
  }
  for (auto const &key : expected) {
    auto it = res.find_item(key);
    if (!it) {
      return false;
    }
  }

  set<string> buf;
  fillSet(src, buf);
  if (buf.size() != expected.size()) {
    return false;
  }
  for (auto const &key : expected) {
    auto it = buf.find_item(key);
    if (!it) {
      return false;
    }
  }

  return true;
}

bool testCallback() {
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

  auto ocp = currying(
      make_holder<MyCallback, callback<string(string_view, string_view)>>("f"))(
      "abc");
  auto res = ocp("123");

  typename callback<string(string_view, string_view)>::vtable_type x;

  std::cout << "res = " << res << std::endl;

  return res == MyCallback("f")("abc", "123");
}

bool TestMemoryLeak() {
  bool leak = false;

  for (auto *user : UserType::registry) {
    std::cout << user->getId() << " is still alive" << std::endl;
    leak = true;
  }

  return !leak;
}

class Tester {
  std::vector<std::pair<std::string, bool>> results;

public:
  Tester() {}

  template<typename Func, typename... Args>
  void test(std::string name, Func &&func, Args &&...args) {
    std::cout << ">> Running test: " << name << std::endl;
    bool result = func(std::forward<Args>(args)...);
    std::cout << (result ? "\033[32m" : "\033[31m") << ">> Test " << name << " "
              << (result ? "passed" : "failed") << "!" << "\033[0m"
              << std::endl;
    results.emplace_back(name, result);
  }

  size_t failures() const {
    size_t count = 0;
    for (auto const &[name, result] : results) {
      if (!result) {
        count++;
      }
    }
    return count;
  }
};

int main() {
  Tester tester;

  tester.test("Union", testUnion);
  tester.test("Interface Call", testInterfaceCall);
  tester.test("Interface Cast", testInterfaceCast);
  tester.test("Array", testArray);
  tester.test("Optional", testOptional);
  tester.test("Vector", testVector);
  tester.test("Map", testMap);
  tester.test("Set", testSet);
  tester.test("Callback", testCallback);
  tester.test("Memory Leak", TestMemoryLeak);

  size_t failed_count = tester.failures();
  if (failed_count > 0) {
    std::cout << "\033[31m" << failed_count
              << " test(s) failed. Please check the output above.\033[0m"
              << std::endl;
  } else {
    std::cout << "\033[32mAll tests passed!\033[0m" << std::endl;
  }
}
