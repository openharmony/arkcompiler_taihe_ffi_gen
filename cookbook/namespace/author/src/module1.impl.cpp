#include "module1.impl.hpp"
#include <iostream>
#include "module1.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;

namespace {
void module1Run() {
  std::cout << "Module: module1" << std::endl;
}
}  // namespace

TH_EXPORT_CPP_API_module1Run(module1Run);
