#include <cmath>
#include <core/callback.hpp>
#include <cstddef>
#include <iomanip>
#include <iostream>

#include "core/object.hpp"
#include "core/string.hpp"
#include "impl_test.proj.hpp"

using namespace impl_test;
using namespace taihe::core;

#define TRY_CATCH_BLOCK(func)                                   \
  try {                                                         \
    func;                                                       \
  } catch (const std::runtime_error& e) {                       \
    std::cerr << "Caught exception: " << e.what() << std::endl; \
  } catch (...) {                                               \
    std::cerr << "Caught unknown exception!" << std::endl;      \
  }

int main() {
  TRY_CATCH_BLOCK(int a = add(1, 2))
  impl_test::IBase obj = impl_test::makeIBase();
  TRY_CATCH_BLOCK(obj->getId())
  impl_test::IBase newobj = obj->getIBase();
  TRY_CATCH_BLOCK(newobj->getId())
  TRY_CATCH_BLOCK(newobj->getIBase())
  return 0;
}

#undef TRY_CATCH_BLOCK