#include "taihe/callback.hpp"
#include <iostream>
#include "callbackTest.impl.hpp"
#include "taihe/string.hpp"

using namespace taihe;

namespace {

class MyInterfaceImpl {
public:
  static int const ten = 10;
  static int const hundred = 100;
  static long long const tenBillion = 1000000000LL;

  MyInterfaceImpl() {}

  ::taihe::string TestCbIntString(
      ::taihe::callback_view<void(int8_t, int32_t)> f) {
    f(ten, hundred);
    return "testCbIntString";
  }

  bool TestCbIntBool(::taihe::callback_view<void(int16_t, int64_t)> f) {
    f(hundred, tenBillion);
    return true;
  }

  ::callbackTest::EnumData TestCbEnum(::taihe::callback_view<void(int32_t)> f) {
    f(ten);
    return ::callbackTest::EnumData(::callbackTest::EnumData::key_t::F32_A);
  }
};

void TestCbV(callback_view<void()> f) {
  f();
}

void TestCbI(callback_view<void(int32_t)> f) {
  static int const one = 1;
  f(one);
}

void TestCbS(callback_view<void(string_view, bool)> f) {
  f("hello", true);
}

string TestCbRs(callback_view<string(string_view)> f) {
  taihe::string out = f("hello");
  return out;
}

void TestCbStruct(
    callback_view<::callbackTest::Data(::callbackTest::Data const &)> f) {
  ::callbackTest::Data result = f(::callbackTest::Data{"a", "b", 1});
  return;
}

::callbackTest::MyInterface GetInterface() {
  return taihe::make_holder<MyInterfaceImpl, ::callbackTest::MyInterface>();
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_TestCbV(TestCbV);
TH_EXPORT_CPP_API_TestCbI(TestCbI);
TH_EXPORT_CPP_API_TestCbS(TestCbS);
TH_EXPORT_CPP_API_TestCbRs(TestCbRs);
TH_EXPORT_CPP_API_TestCbStruct(TestCbStruct);
TH_EXPORT_CPP_API_GetInterface(GetInterface);
// NOLINTEND