#include "staticTest.impl.hpp"
#include <cstdint>
#include <iostream>
#include "core/runtime.hpp"

int32_t add_impl(int32_t a, int32_t b) {
    if (a == 0) {
        taihe::core::throw_error("some error happen in add impl");
        return b;
    } else {
        std::cout << "add impl " << a + b << std::endl;
        return a + b;
    }
}

int32_t sum_impl(int32_t a, int32_t b) {
  return a * b;
}
struct AuthorIBase {
  taihe::core::string name;
  AuthorIBase(taihe::core::string_view name) : name(name) {}
  AuthorIBase(taihe::core::string_view name, taihe::core::string_view t) : name(t) {}
  ~AuthorIBase() {}
  taihe::core::string get() {
    return name;
  }
  void set(taihe::core::string_view a) {
    this->name = a;
    return;
  }
};
::staticTest::IBase getIBase_impl(taihe::core::string_view name) {
    return taihe::core::make_holder<AuthorIBase, ::staticTest::IBase>(name);
}
::staticTest::IBase getIBase_test_impl(taihe::core::string_view name, taihe::core::string_view t) {
  return taihe::core::make_holder<AuthorIBase, ::staticTest::IBase>(name, t);
}

class ITest {
  public:
    ITest() : name("hello ITest") {}
    ~ITest() {}
    taihe::core::string name;
    taihe::core::string get() {
      return name;
    }
    void set(taihe::core::string_view a) {
      this->name = a;
      return;
    }
};

int32_t static_func(int32_t a, int32_t b) {
  return a + b;
}
::staticTest::ITest ctor_func() {
  return taihe::core::make_holder<ITest, ::staticTest::ITest>();
}

TH_EXPORT_CPP_API_addSync(add_impl);
TH_EXPORT_CPP_API_sumSync(sum_impl);
TH_EXPORT_CPP_API_getIBase(getIBase_impl);
TH_EXPORT_CPP_API_getIBase_test(getIBase_test_impl);
TH_EXPORT_CPP_API_static_func(static_func)
TH_EXPORT_CPP_API_ctor_func(ctor_func)
