#include "overlayModuleInfo.impl.hpp"
#include "overlayModuleInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace overlayModuleInfo;

namespace {
// To be implemented.

class OverlayModuleInfoImpl {
public:
  int32_t overlayModuleInfoImpl = 21474;

  OverlayModuleInfoImpl() {}

  string GetBundleName() {
    return "OverlayModuleInfoImpl::getBundleName";
  }

  string GetModuleName() {
    return "OverlayModuleInfoImpl::getModuleName";
  }

  string GetTargetModuleName() {
    return "OverlayModuleInfoImpl::getTargetModuleName";
  }

  int32_t GetPriority() {
    return overlayModuleInfoImpl;
  }

  int32_t GetState() {
    return overlayModuleInfoImpl;
  }
};

OverlayModuleInfo GetOverlayModuleInfo() {
  return make_holder<OverlayModuleInfoImpl, OverlayModuleInfo>();
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_GetOverlayModuleInfo(GetOverlayModuleInfo);
// NOLINTEND
