#include <cmath>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <string>
#include <taihe/callback.hpp>
#include <taihe/object.hpp>
#include <unordered_map>
#include <unordered_set>

#include "rgb.base.user.hpp"
#include "rgb.show.IShape.proj.1.hpp"
#include "rgb.show.user.hpp"

#include "taihe/string.hpp"
#include "tester.hpp"

using namespace rgb::base;
using namespace rgb::show;
using namespace taihe;

template<typename... Ts>
struct overloads : Ts... {
  using Ts::operator()...;
};

template<typename... Ts>
overloads(Ts...) -> overloads<Ts...>;

string toString(ColorOrRGBOrName const &color) {
  return color.match_function<string>(overloads{
      [](static_tag_t<ColorOrRGBOrName::tag_t::rgb>, const RGB &val) {
        std::ostringstream oss;
        oss << "#" << std::hex << std::setfill('0') << std::setw(2)
            << static_cast<int>(val.r) << std::setw(2)
            << static_cast<int>(val.g) << std::setw(2)
            << static_cast<int>(val.b);
        return oss.str();
      },
      [](static_tag_t<ColorOrRGBOrName::tag_t::name>, Name const &val) {
        return string(val);
      },
      [](static_tag_t<ColorOrRGBOrName::tag_t::color>, Color const &val) {
        return std::to_string(val.get_value());
      },
      [](static_tag_t<ColorOrRGBOrName::tag_t::undefined>) {
        return "Undefined";
      },
  });
}

struct UserType {
  static inline std::unordered_set<UserType *> registry;

private:
  string id;
  ColorOrRGBOrName myColor;

public:
  auto getId() {
    return concat({"UserType", "(", id, ")"});
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

void testUnion() {
  std::cout << toString(color_114514) << std::endl;
  std::cout << toString(color_yellow) << std::endl;
  std::cout << toString(color_miku) << std::endl;
  std::cout << toString(color_unknown) << std::endl;

  if (Name *name_ptr = color_miku.get_name_ptr()) {
    std::cout << "color_miku is holding name, name is " << *name_ptr
              << std::endl;
  } else {
    std::cout << "Error" << std::endl;
    Tester::assert(false, "color_miku should hold a name");
  }

  if (color_miku.holds_name()) {
    Name name_ref = color_miku.get_name_ref();
    std::cout << "color_miku is holding name, name is " << name_ref
              << std::endl;
  } else {
    std::cout << "Error" << std::endl;
    Tester::assert(false, "color_miku should hold a name");
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

  Tester::assert(color_miku.get_tag() == ColorOrRGBOrName::tag_t::rgb,
                 "color_miku should hold rgb, got %s",
                 toString(color_miku).c_str());
}

void testInterfaceCall() {
  IShowable colored_rect = makeColoredRectangle("Rect", color_yellow, 5, 5);

  Tester::assert(weak::IColorable(colored_rect)->getColor() == color_yellow,
                 "Colored Rectangle should have color %s, got %s",
                 toString(color_yellow).c_str(),
                 toString(weak::IColorable(colored_rect)->getColor()).c_str());

  copyColor(colored_rect,
            make_holder<UserType, IColorable>("Circ", color_114514));

  Tester::assert(weak::IColorable(colored_rect)->getColor() == color_114514,
                 "Colored Rectangle should have color %s, got %s",
                 toString(color_114514).c_str(),
                 toString(weak::IColorable(colored_rect)->getColor()).c_str());
}

void testInterfaceCast() {
  IBase ibase_a = makeColoredRectangle("A", color_yellow, 1, 2);

  Tester::assert(!weak::IColorable(ibase_a).is_error(),
                 "Dynamic cast from %s to IColorable should succeed",
                 ibase_a->getId().c_str());

  IBase ibase_b = makeRectangle("B", 3, 4);

  Tester::assert(weak::IColorable(ibase_b).is_error(),
                 "Dynamic cast from %s to IColorable should fail",
                 ibase_b->getId().c_str());
}

void testArray() {
  std::size_t m = 5;
  std::size_t n = 2;

  auto x = make_holder<UserType, IBase>("x");
  auto y = make_holder<UserType, IBase>("y");

  auto dst = array<IBase>::make(m, x);
  auto src = array<IBase>::make(n, y);

  auto res = exchangeArr(dst, src);

  Tester::assert(dst.size() == m, "dst size should be %zu, got %zu", m,
                 dst.size());
  Tester::assert(src.size() == n, "src size should be %zu, got %zu", n,
                 src.size());
  Tester::assert(res.size() == n, "res size should be %zu, got %zu", n,
                 res.size());

  for (size_t i = 0; i < n; i++) {
    Tester::assert(src[i] == y, "src[%zu] should be %s, got %s", i,
                   y->getId().c_str(), src[i]->getId().c_str());
    Tester::assert(dst[i] == y, "dst[%zu] should be %s, got %s", i,
                   y->getId().c_str(), dst[i]->getId().c_str());
    Tester::assert(res[i] == x, "res[%zu] should be %s, got %s", i,
                   x->getId().c_str(), res[i]->getId().c_str());
  }
  for (size_t i = n; i < m; i++) {
    Tester::assert(dst[i] == x, "dst[%zu] should be %s, got %s", i,
                   x->getId().c_str(), dst[i]->getId().c_str());
  }
}

void testOptional() {
  auto some =
      optional<IBase>(std::in_place, make_holder<UserType, IBase>("some"));
  auto some_str = getIdFromOptional(some);
  Tester::assert(some_str.has_value(), "some_str should have value");
  Tester::assert(some_str.value() == some.value()->getId(),
                 "some_str should be %s, got %s", some.value()->getId().c_str(),
                 some_str.value().c_str());

  auto none = optional<IBase>(std::nullopt);
  auto none_str = getIdFromOptional(none);
  Tester::assert(!none_str.has_value(), "none_str should not have value");
}

void testVector() {
  array<IBase> src = {
      make_holder<UserType, IBase>("a"),
      make_holder<UserType, IBase>("b"),
      make_holder<UserType, IBase>("c"),
  };

  vector<IBase> res = makeVec(src);
  Tester::assert(res.size() == src.size(),
                 "Vector result size should be %zu, got %zu", src.size(),
                 res.size());
  for (size_t i = 0; i < src.size(); i++) {
    Tester::assert(res[i]->getId() == src[i]->getId(),
                   "res[%zu] should be %s, got %s", i, src[i]->getId().c_str(),
                   res[i]->getId().c_str());
  }

  vector<IBase> buf;
  fillVec(src, buf);
  Tester::assert(buf.size() == src.size(),
                 "Vector buffer size should be %zu, got %zu", src.size(),
                 buf.size());
  for (size_t i = 0; i < src.size(); i++) {
    Tester::assert(buf[i]->getId() == src[i]->getId(),
                   "buf[%zu] should be %s, got %s", i, src[i]->getId().c_str(),
                   buf[i]->getId().c_str());
  }
}

void testMap() {
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
  Tester::assert(res.size() == expected.size(),
                 "Map result size should be %zu, got %zu", expected.size(),
                 res.size());
  for (auto const &[key, value] : expected) {
    auto it = res.find_item(key);
    Tester::assert(it, "Map should contain key %s", key.c_str());
    Tester::assert(it->second->getId() == value->getId(),
                   "Map[%s] should be %s, got %s", key.c_str(),
                   value->getId().c_str(), it->second->getId().c_str());
  }

  map<string, IBase> buf;
  fillMap(keys, src, buf);
  Tester::assert(buf.size() == expected.size(),
                 "Map buffer size should be %zu, got %zu", expected.size(),
                 buf.size());
  for (auto const &[key, value] : expected) {
    auto it = buf.find_item(key);
    Tester::assert(it, "buffer should contain key %s", key.c_str());
    Tester::assert(it->second->getId() == value->getId(),
                   "buffer[%s] should be %s, got %s", key.c_str(),
                   value->getId().c_str(), it->second->getId().c_str());
  }
}

void testSet() {
  array<string> src = {"a", "b", "c", "a"};

  std::unordered_set<std::string> expected;
  for (size_t i = 0; i < src.size(); i++) {
    expected.emplace(std::string(src[i]));
  }

  set<string> res = makeSet(src);
  Tester::assert(res.size() == expected.size(),
                 "Set result size should be %zu, got %zu", expected.size(),
                 res.size());
  for (auto const &key : expected) {
    auto it = res.find_item(key);
    Tester::assert(it, "Set should contain key %s", key.c_str());
  }

  set<string> buf;
  fillSet(src, buf);
  Tester::assert(buf.size() == expected.size(),
                 "Set buffer size should be %zu, got %zu", expected.size(),
                 buf.size());
  for (auto const &key : expected) {
    auto it = buf.find_item(key);
    Tester::assert(it, "buffer should contain key %s", key.c_str());
  }
}

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

void testCallback() {
  auto curried = currying(
      make_holder<MyCallback, callback<string(string_view, string_view)>>("f"));
  auto f = curried("abc");
  auto x = f("123");
  auto y = f("456");

  auto expected_x = MyCallback("f")("abc", "123");
  Tester::assert(x == expected_x, "x should be %s, got %s", expected_x.c_str(),
                 x.c_str());

  auto expected_y = MyCallback("f")("abc", "456");
  Tester::assert(y == expected_y, "y should be %s, got %s", expected_y.c_str(),
                 y.c_str());
}

struct AutoCompareType {
  string id;

  AutoCompareType(string_view id) : id(id) {
    std::cout << "AutoCompareType " << id << " made" << std::endl;
  }

  string getId() const {
    return id;
  }
};

struct UserCompareType {
  string id;

  UserCompareType(string_view id) : id(id) {
    std::cout << "UserCompareType " << id << " made" << std::endl;
  }

  string getId() const {
    return id;
  }
};

template<>
struct taihe::same_impl_t<UserCompareType> {
  bool operator()(data_view lhs, data_view rhs) const {
    auto lhs_with_id = weak::IBase(lhs);
    auto rhs_with_id = weak::IBase(rhs);
    if (lhs_with_id.is_error() || rhs_with_id.is_error()) {
      return same_impl<void>(lhs, rhs);
    }
    return lhs_with_id->getId() == rhs_with_id->getId();
  }
};

template<>
struct taihe::hash_impl_t<UserCompareType> {
  std::size_t operator()(data_view val) const {
    auto val_with_id = weak::IBase(val);
    if (val_with_id.is_error()) {
      return hash_impl<void>(val);
    }
    return std::hash<std::string_view>{}(val_with_id->getId());
  }
};

void testCompare() {
  // AutoCompareType uses default comparison
  map<IBase, string> auto_compare_map;
  auto_compare_map.emplace(make_holder<AutoCompareType, IBase>("a"), "a");
  auto_compare_map.emplace(make_holder<AutoCompareType, IBase>("b"), "b");
  auto_compare_map.emplace(make_holder<AutoCompareType, IBase>("a"), "c");
  std::cout << "AutoCompareMap size: " << auto_compare_map.size() << std::endl;
  for (auto const &[key, value] : auto_compare_map) {
    std::cout << "AutoCompareMap: " << key->getId() << " -> " << value
              << std::endl;
  }

  // UserCompareType uses custom comparison
  map<IBase, string> user_compare_map;
  user_compare_map.emplace(make_holder<UserCompareType, IBase>("a"), "a");
  user_compare_map.emplace(make_holder<UserCompareType, IBase>("b"), "b");
  user_compare_map.emplace(make_holder<UserCompareType, IBase>("a"), "c");
  std::cout << "UserCompareMap size: " << user_compare_map.size() << std::endl;
  for (auto const &[key, value] : user_compare_map) {
    std::cout << "UserCompareMap: " << key->getId() << " -> " << value
              << std::endl;
  }

  Tester::assert(auto_compare_map.size() == 3,
                 "AutoCompareMap should have 3 items, got %zu",
                 auto_compare_map.size());
  Tester::assert(user_compare_map.size() == 2,
                 "UserCompareMap should have 2 items, got %zu",
                 user_compare_map.size());
}

void testHashAndSame() {
  auto a = make_holder<UserType, IBase>("a");
  std::cout << "Hash of a: " << std::hash<IBase>()(a) << std::endl;
  std::cout << "Comparing a with itself: " << std::boolalpha << (a == a)
            << std::endl;

  taihe::array<IBase> arr = {a, a, a};
  std::cout << "Hash of array with three a's: "
            << std::hash<array<IBase>>()(arr) << std::endl;
  std::cout << "Comparing array with three a's with itself: " << std::boolalpha
            << (arr == arr) << std::endl;

  taihe::optional<IBase> opt(std::in_place, a);
  std::cout << "Hash of optional with a: " << std::hash<optional<IBase>>()(opt)
            << std::endl;
  std::cout << "Comparing optional with a with itself: " << std::boolalpha
            << (opt == opt) << std::endl;

  taihe::vector<IBase> vec;
  vec.push_back(a);
  std::cout << "Hash of vector with a: " << std::hash<vector<IBase>>()(vec)
            << std::endl;
  std::cout << "Comparing vector with a with itself: " << std::boolalpha
            << (vec == vec) << std::endl;

  taihe::set<IBase> s;
  s.emplace(a);
  std::cout << "Hash of set with a: " << std::hash<set<IBase>>()(s)
            << std::endl;
  std::cout << "Comparing set with a with itself: " << std::boolalpha
            << (s == s) << std::endl;

  taihe::map<IBase, IBase> m;
  m.emplace(a, a);
  std::cout << "Hash of map with a: " << std::hash<map<IBase, IBase>>()(m)
            << std::endl;
  std::cout << "Comparing map with a with itself: " << std::boolalpha
            << (m == m) << std::endl;

  taihe::callback<string(string_view, string_view)> cb(
      make_holder<MyCallback, callback<string(string_view, string_view)>>(
          "cb"));
  std::cout << "Hash of callback: "
            << std::hash<callback<string(string_view, string_view)>>()(cb)
            << std::endl;
  std::cout << "Comparing callback with itself: " << std::boolalpha
            << (cb == cb) << std::endl;
}

void testMemoryLeak() {
  size_t remaining = 0;

  for (auto *user : UserType::registry) {
    std::cout << user->getId() << " is still alive" << std::endl;
    remaining++;
  }

  Tester::assert(remaining == 0,
                 "Memory leak detected: %zu UserType objects are still alive",
                 remaining);
}

int main() {
  Tester tester;

  tester.run("testUnion", testUnion);
  tester.run("testInterfaceCall", testInterfaceCall);
  tester.run("testInterfaceCast", testInterfaceCast);
  tester.run("testArray", testArray);
  tester.run("testOptional", testOptional);
  tester.run("testVector", testVector);
  tester.run("testMap", testMap);
  tester.run("testSet", testSet);
  tester.run("testCallback", testCallback);
  tester.run("testCompare", testCompare);
  tester.run("testHashAndSame", testHashAndSame);
  tester.run("testMemoryLeak", testMemoryLeak);

  return tester.report();
}
