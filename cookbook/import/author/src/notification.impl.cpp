#include "notification.impl.hpp"
#include <iostream>
#include "notification.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace notification;

namespace {
class INotificationServiceImpl {
public:
  INotificationServiceImpl() {}

  void sendMessage(::user::weak::IUser a) {
    string_view user_email = a->getEmail();
    std::cout << "Welcome " << a->getEmail() << std::endl;
  }
};

INotificationService makeNotificationService() {
  return make_holder<INotificationServiceImpl, INotificationService>();
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_makeNotificationService(makeNotificationService);
// NOLINTEND
