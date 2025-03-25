#include "async.impl.hpp"

#include "async.IStringHolder.proj.2.hpp"
#include "core/string.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
class IStringHolder {
 public:
  IStringHolder() : str("MyStr") {}
  ~IStringHolder() {}
  string get() { return str; }
  void set(string_view a) { this->str = a; }

 private:
  string str;
};
int32_t addSync(int32_t a, int32_t b) { return a + b; }
::async::IStringHolder makeIStringHolder() {
  return make_holder<IStringHolder, ::async::IStringHolder>();
}
}  // namespace
TH_EXPORT_CPP_API_addSync(addSync);
TH_EXPORT_CPP_API_makeIStringHolder(makeIStringHolder);
