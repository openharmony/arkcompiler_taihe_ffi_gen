#include "on_off.impl.hpp"

#include <iostream>

#include "core/callback.hpp"
#include "core/string.hpp"
#include "on_off.IBase.proj.2.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
class IBase {
 public:
  IBase(string a, string b) : str(a), new_str(b) {}
  ~IBase() {}
  void onSet(callback_view<void()> a) {
    a();
    std::cout << "IBase::onSet" << std::endl;
  }
  void offSet(callback_view<void()> a) {
    a();
    std::cout << "IBase::offSet" << std::endl;
  }

 private:
  string str;
  string new_str;
};

::on_off::IBase getIBase(string_view a, string_view b) {
  return make_holder<IBase, ::on_off::IBase>(a, b);
}
void onFoo(callback_view<void()> a) {
  a();
  std::cout << "onFoo" << std::endl;
}
void onBar(callback_view<void()> a) {
  a();
  std::cout << "onBar" << std::endl;
}
void onBaz(int32_t a, callback_view<void()> cb) {
  cb();
  std::cout << "a =" << a << ", onBaz" << std::endl;
}
void offFoo(callback_view<void()> a) {
  a();
  std::cout << "offFoo" << std::endl;
}
void offBar(callback_view<void()> a) {
  a();
  std::cout << "offBar" << std::endl;
}
void offBaz(int32_t a, callback_view<void()> cb) {
  cb();
  std::cout << "offBaz" << std::endl;
}
}  // namespace
TH_EXPORT_CPP_API_getIBase(getIBase);
TH_EXPORT_CPP_API_onFoo(onFoo);
TH_EXPORT_CPP_API_onBar(onBar);
TH_EXPORT_CPP_API_onBaz(onBaz);
TH_EXPORT_CPP_API_offFoo(offFoo);
TH_EXPORT_CPP_API_offBar(offBar);
TH_EXPORT_CPP_API_offBaz(offBaz);
