#include <async_test.impl.hpp>
#include <cstdint>
#include <iostream>

#include "taihe/runtime.hpp"

namespace {
int32_t add_impl(int32_t a, int32_t b) {
  if (a == 0) {
    taihe::set_business_error(1, "some error happen in add impl");
    return b;
  } else {
    std::cout << "add impl " << a + b << std::endl;
    return a + b;
  }
}

::async_test::IBase getIBase_impl() {
  struct AuthorIBase {
    taihe::string name;

    AuthorIBase() : name("My IBase") {}

    ~AuthorIBase() {}

    taihe::string get() {
      return name;
    }

    taihe::string getWithCallback() {
      return name;
    }

    taihe::string getReturnsPromise() {
      return name;
    }

    void set(taihe::string_view a) {
      this->name = a;
      return;
    }

    void setWithCallback(taihe::string_view a) {
      this->name = a;
      return;
    }

    void setReturnsPromise(taihe::string_view a) {
      this->name = a;
      return;
    }

    void makeSync() {
      TH_THROW(std::runtime_error, "makeSync not implemented");
    }

    void makeWithCallback() {
      TH_THROW(std::runtime_error, "makeSync not implemented");
    }

    void makeReturnsPromise() {
      TH_THROW(std::runtime_error, "makeSync not implemented");
    }
  };

  return taihe::make_holder<AuthorIBase, ::async_test::IBase>();
}

void fromStructSync_impl(::async_test::Data const &data) {
  std::cout << data.a.c_str() << " " << data.b.c_str() << " " << data.c
            << std::endl;
  if (data.c == 0) {
    taihe::set_business_error(1, "some error happen in fromStructSync_impl");
  }
  return;
}

::async_test::Data toStructSync_impl(taihe::string_view a, taihe::string_view b,
                                     int32_t c) {
  if (c == 0) {
    taihe::set_business_error(1, "some error happen in toStructSync_impl");
    return {a, b, c};
  }
  return {a, b, c};
}

void printSync() {
  std::cout << "print Sync" << std::endl;
}

void makeGlobalSync() {
  std::cout << "makeGlobal" << std::endl;
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_addSync(add_impl);
TH_EXPORT_CPP_API_addWithAsync(add_impl);
TH_EXPORT_CPP_API_addReturnsPromise(add_impl);
TH_EXPORT_CPP_API_getIBase(getIBase_impl);
TH_EXPORT_CPP_API_getIBaseWithCallback(getIBase_impl);
TH_EXPORT_CPP_API_getIBaseReturnsPromise(getIBase_impl);
TH_EXPORT_CPP_API_fromStructSync(fromStructSync_impl);
TH_EXPORT_CPP_API_fromStructWithCallback(fromStructSync_impl);
TH_EXPORT_CPP_API_fromStructReturnsPromise(fromStructSync_impl);
TH_EXPORT_CPP_API_toStructSync(toStructSync_impl);
TH_EXPORT_CPP_API_toStructWithCallback(toStructSync_impl);
TH_EXPORT_CPP_API_toStructReturnsPromise(toStructSync_impl);
TH_EXPORT_CPP_API_printSync(printSync);
TH_EXPORT_CPP_API_printWithCallback(printSync);
TH_EXPORT_CPP_API_printReturnsPromise(printSync);
TH_EXPORT_CPP_API_makeGlobalSync(makeGlobalSync);
TH_EXPORT_CPP_API_makeGlobalWithCallback(makeGlobalSync);
TH_EXPORT_CPP_API_makeGlobalReturnsPromise(makeGlobalSync);
// NOLINTEND