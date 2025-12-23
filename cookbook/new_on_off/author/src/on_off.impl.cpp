#include "on_off.impl.hpp"
#include "on_off.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace on_off;

namespace {
class ISetterObserverImpl {
public:
  ISetterObserverImpl() {}

  void onSet(::taihe::string_view type, callback_view<void()> a) {
    a();
    std::cout << "IBase::onSet" << std::endl;
  }

  void offSet(::taihe::string_view type, callback_view<void()> a) {
    a();
    std::cout << "IBase::offSet" << std::endl;
  }
};

ISetterObserver getISetterObserver() {
  return make_holder<ISetterObserverImpl, ISetterObserver>();
}

void onFoo(::taihe::string_view type, callback_view<void()> a) {
  a();
  std::cout << "onFoo" << std::endl;
}

void onBar(::taihe::string_view type, callback_view<void()> a) {
  a();
  std::cout << "onBar" << std::endl;
}

void onBaz(::taihe::string_view type, int32_t a,
           callback_view<void(int32_t)> cb) {
  cb(a);
  std::cout << "onNewBaz" << std::endl;
}

void offFoo(::taihe::string_view type, callback_view<void()> a) {
  a();
  std::cout << "offFoo" << std::endl;
}

void offBar(::taihe::string_view type, callback_view<void()> a) {
  a();
  std::cout << "offBar" << std::endl;
}

void offBaz(::taihe::string_view type, int32_t a,
            callback_view<void(int32_t)> cb) {
  cb(a);
  std::cout << "offNewBaz" << std::endl;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_getISetterObserver(getISetterObserver);
TH_EXPORT_CPP_API_onFoo(onFoo);
TH_EXPORT_CPP_API_onBar(onBar);
TH_EXPORT_CPP_API_onBaz(onBaz);
TH_EXPORT_CPP_API_offFoo(offFoo);
TH_EXPORT_CPP_API_offBar(offBar);
TH_EXPORT_CPP_API_offBaz(offBaz);
// NOLINTEND
