#include "async.impl.hpp"

#include "async.IStringHolder.proj.2.hpp"
#include "stdexcept"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
class IStringHolder {
public:
  IStringHolder() : str("MyStr") {}

  ~IStringHolder() {}

  string getStrSync() {
    return str;
  }

  ::taihe::string getStrWithAsync() {
    return str;
  }

  ::taihe::string getStrRetPromise() {
    return str;
  }

  void setStrSync(string_view a) {
    this->str = a;
  }

  void setStrWithAsync(::taihe::string_view a) {
    this->str = a;
  }

  void setStrRetPromise(::taihe::string_view a) {
    this->str = a;
  }

private:
  string str;
};

int32_t addSync(int32_t a, int32_t b) {
  return a + b;
}

::async::IStringHolder makeIStringHolder() {
  return make_holder<IStringHolder, ::async::IStringHolder>();
}
}  // namespace

TH_EXPORT_CPP_API_addAsync(addSync);
TH_EXPORT_CPP_API_addPromise(addSync);
TH_EXPORT_CPP_API_addSync(addSync);
TH_EXPORT_CPP_API_makeIStringHolder(makeIStringHolder);
