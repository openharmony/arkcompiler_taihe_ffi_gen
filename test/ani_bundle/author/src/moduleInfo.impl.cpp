#include "moduleInfo.impl.hpp"
#include "moduleInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace moduleInfo;

namespace {
// To be implemented.

class ModuleInfoImpl {
public:
  string moduleName_ = "this is moduleinfo with name";
  string moduleSourceDir_ = "this is moduleinfo with moduleSourceDir";

  ModuleInfoImpl() {}

  string GetModuleName() {
    return moduleName_;
  }

  string GetModuleSourceDir() {
    return moduleSourceDir_;
  }
};

ModuleInfo GetModuleInfo() {
  return make_holder<ModuleInfoImpl, ModuleInfo>();
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_GetModuleInfo(GetModuleInfo);
// NOLINTEND
