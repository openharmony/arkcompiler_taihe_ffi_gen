#include "foo.DerivedMethodClass.impl.hpp"

taihe::string DerivedMethodClassImpl::derived() {
  return "derived";
}

taihe::string DerivedMethodClassImpl::base() {
  return "base";
}

taihe::string DerivedMethodClassImpl::foo() {
  return "foo";
}

taihe::string DerivedMethodClassImpl::bar() {
  return "bar";
}
