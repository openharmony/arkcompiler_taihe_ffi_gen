#include "hapModuleInfo.impl.hpp"
#include "hapModuleInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace hapModuleInfo;

namespace {

class HapModuleInfoImpl {
public:
  int32_t hapModuleInfoImpl = 1024;

  HapModuleInfoImpl() {}

  string GetName() {
    return "HapModuleInfo::getName";
  }

  string GetDescription() {
    return "HapModuleInfo::getDescription";
  }

  int32_t GetDescriptionId() {
    return hapModuleInfoImpl;
  }

  string GetIcon() {
    return "HapModuleInfo::getIcon";
  }

  string GetLabel() {
    return "HapModuleInfo::getLabel";
  }

  int32_t GetLabelId() {
    return hapModuleInfoImpl;
  }

  int32_t GetIconId() {
    return hapModuleInfoImpl;
  }

  string GetBackgroundImg() {
    return "HapModuleInfo::getBackgroundImg";
  }

  int32_t GetSupportedModes() {
    return hapModuleInfoImpl;
  }

  array<string> GetReqCapabilities() {
    array<string> str = {"HapModuleInfo::getReqCapabilities"};
    return str;
  }

  array<string> GetDeviceTypes() {
    array<string> str = {"HapModuleInfo::getDeviceTypes"};
    return str;
  }

  string GetModuleName() {
    return "HapModuleInfo::getModuleName";
  }

  string GetMainAbilityName() {
    return "HapModuleInfo::getMainAbilityName";
  }

  bool GetInstallationFree() {
    return true;
  }
};

HapModuleInfo GetHapModuleInfo() {
  return make_holder<HapModuleInfoImpl, HapModuleInfo>();
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_GetHapModuleInfo(GetHapModuleInfo);
// NOLINTEND
