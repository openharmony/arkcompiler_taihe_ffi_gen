#include "module2.bar.impl.hpp"
#include "module2.bar.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;

namespace {
void barFunc() {
  std::cout << "namespace: module2.bar, func: bar" << std::endl;
}
}  // namespace

TH_EXPORT_CPP_API_barFunc(barFunc);
