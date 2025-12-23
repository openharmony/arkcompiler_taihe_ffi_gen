#include "user.impl.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"
#include "user.proj.hpp"

using namespace taihe;
using namespace user;

namespace {
// To be implemented.

class IUserImpl {
public:
  IUserImpl(string_view path) : m_email(path) {}

  string getEmail() {
    return this->m_email;
  }

  void setEmail(string_view path) {
    this->m_email = path;
  }

private:
  string m_email;
};

IUser makeUser(string_view path) {
  return make_holder<IUserImpl, IUser>(path);
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_makeUser(makeUser);
// NOLINTEND
