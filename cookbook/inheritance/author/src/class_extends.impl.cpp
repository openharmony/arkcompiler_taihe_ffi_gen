#include "class_extends.impl.hpp"

#include <iostream>

#include "class_extends.InnerBaseContext.proj.2.hpp"
#include "core/string.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
class BaseContext {
 public:
  static std::string GetTypeBaseContext(std::string flag) {
    return "BaseContextType" + flag;
  }
};

class Context {
 public:
  static std::string GetTypeContext(std::string flag) {
    return "ContextType" + flag;
  }
};

class AppContext {
 public:
  static std::string GetTypeAppContext(std::string flag) {
    return "AppContext" + flag;
  }
};

class TestContext {
 public:
  static std::string GetTypeTestContext(std::string flag) {
    return "TestContext" + flag;
  }
};

class InnerBaseContext {
 public:
  uintptr_t getApplicationContext() {
    throw std::runtime_error(
        "Function InnerBaseContext::getApplicationContext Not implemented");
  }
  uintptr_t getTestContext() {
    throw std::runtime_error(
        "Function InnerBaseContext::getTestContext Not implemented");
  }
  void setSupportedProcessCacheSync(bool isSupported) {
    std::cout << "setSupportedProcessCacheSync "
              << (isSupported ? "True" : "False") << std::endl;
  }
  void setSupportedProcessCache(bool isSupported) {
    std::cout << "setSupportedProcessCache " << (isSupported ? "True" : "False")
              << std::endl;
  }
  void setName(string_view name) {
    nameType = std::string(name);
    std::cout << "setName " << nameType << std::endl;
  }
  string getName() { return nameType; }
  string getType(string_view ctxType) {
    std::string type = std::string(ctxType);
    if (type == "BCTX") {
      return BaseContext::GetTypeBaseContext(type);
    } else if (type == "CTX") {
      return Context::GetTypeContext(type);
    } else if (type == "ACTX") {
      return AppContext::GetTypeAppContext(type);
    } else if (type == "TCTX") {
      return TestContext::GetTypeTestContext(type);
    }
    return "ERROR";
  }

 private:
  std::string nameType;
};
::class_extends::InnerBaseContext makeBaseContext(int32_t init) {
  return make_holder<InnerBaseContext, ::class_extends::InnerBaseContext>();
}
}  // namespace
TH_EXPORT_CPP_API_makeBaseContext(makeBaseContext);
