#include <iostream>

#include "foo.DerivedMethodClass.template.hpp"

void DerivedMethodClassImpl::derived() {
  std::cout << __PRETTY_FUNCTION__ << std::endl;
}

void DerivedMethodClassImpl::base() {
  std::cout << __PRETTY_FUNCTION__ << std::endl;
}

void DerivedMethodClassImpl::foo() {
  std::cout << __PRETTY_FUNCTION__ << std::endl;
}

void DerivedMethodClassImpl::bar() {
  std::cout << __PRETTY_FUNCTION__ << std::endl;
}
