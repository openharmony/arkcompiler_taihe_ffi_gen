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

  string get() {
    return str;
  }

  ::taihe::string getAsync() {
    return str;
  }

  ::taihe::string getPromise() {
    return str;
  }

  void setSync(string_view a) {
    this->str = a;
  }

  void setAsync(::taihe::string_view a) {
    this->str = a;
  }

  void setPromise(::taihe::string_view a) {
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
