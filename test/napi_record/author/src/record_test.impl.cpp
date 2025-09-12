#include "record_test.impl.hpp"
#include "record_test.proj.hpp"

namespace {
int32_t getStringIntSize(::taihe::map_view<::taihe::string, int32_t> r) {
  return r.size();
}

::taihe::map<::taihe::string, ::taihe::string> createStringString(int32_t a) {
  ::taihe::map<::taihe::string, ::taihe::string> m;
  while (a--) {
    m.emplace(::taihe::to_string(a), "abc");
  }
  return m;
}

void setStringColor(
    ::taihe::map_view<::taihe::string, ::record_test::Color> m) {
  for (auto const &[key, val] : m) {
    std::cout << "C++ MapStringColor: key: " << key << " value: " << val
              << std::endl;
  }
  return;
}

::taihe::map<::taihe::string, ::record_test::Color> getStringColor() {
  ::taihe::map<::taihe::string, ::record_test::Color> result;
  result.emplace("key1", record_test::Color::key_t::RED);
  result.emplace("key2", record_test::Color::key_t::GREEN);
  return result;
}

void setStringData(::taihe::map_view<::taihe::string, ::record_test::Data> m) {
  for (auto const &[key, val] : m) {
    std::cout << "C++ MapStringColor: key: " << key << " value: ";
    std::cout << val.a << " " << val.b << " " << val.c << std::endl;
  }
}

::taihe::map<::taihe::string, ::record_test::Data> getStringData() {
  ::taihe::map<::taihe::string, ::record_test::Data> result;
  result.emplace("key1", ::record_test::Data{"a1", "b1", 1});
  result.emplace("key2", ::record_test::Data{"a2", "b2", 2});
  return result;
}

class Base {
protected:
  ::taihe::string id;

public:
  Base(::taihe::string_view id) : id(id) {
    std::cout << "new base " << this << std::endl;
  }

  ~Base() {
    std::cout << "del shape " << this << std::endl;
  }

  ::taihe::string getId() {
    return id;
  }

  void setId(::taihe::string_view s) {
    id = s;
    return;
  }
};

void setStringIBase(
    ::taihe::map_view<::taihe::string, ::record_test::IBase> m) {
  for (auto const &[key, val] : m) {
    std::cout << "C++ MapStringIBase: key: " << key
              << " value: " << val->getId() << std::endl;
  }
  return;
}

::taihe::map<::taihe::string, ::record_test::IBase> getStringIBase() {
  auto basea = ::taihe::make_holder<Base, ::record_test::IBase>("basea");
  auto baseb = ::taihe::make_holder<Base, ::record_test::IBase>("baseb");
  ::taihe::map<::taihe::string, ::record_test::IBase> result;
  result.emplace("key1", basea);
  result.emplace("key2", baseb);
  return result;
}

}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_getStringIntSize(getStringIntSize);
TH_EXPORT_CPP_API_createStringString(createStringString);
TH_EXPORT_CPP_API_setStringColor(setStringColor);
TH_EXPORT_CPP_API_getStringColor(getStringColor);
TH_EXPORT_CPP_API_setStringData(setStringData);
TH_EXPORT_CPP_API_getStringData(getStringData);
TH_EXPORT_CPP_API_setStringIBase(setStringIBase);
TH_EXPORT_CPP_API_getStringIBase(getStringIBase);
// NOLINTEND
