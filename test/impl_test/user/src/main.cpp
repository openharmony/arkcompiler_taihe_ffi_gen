#include <cmath>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <taihe/callback.hpp>

#include "impl_test.proj.hpp"
#include "taihe/object.hpp"
#include "taihe/string.hpp"

using namespace impl_test;
using namespace taihe;

#define TRY_CATCH_BLOCK(func)                                   \
  try {                                                         \
    func;                                                       \
  } catch (std::runtime_error const& e) {                       \
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