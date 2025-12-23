#include <iostream>
#include "abilityInfo.impl.hpp"
#include "abilityInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"
using namespace taihe;
using namespace abilityInfo;

namespace {
// To be implemented.

class AbilityInfoImpl {
public:
  int32_t abilityInfoImpl = 100;

  AbilityInfoImpl() {}

  std::string GetBundleName() {
    return "AbilityInfo::getBundleName";
  }

  std::string GetName() {
    return "AbilityInfo::getName";
  }

  std::string GetLabel() {
    return "AbilityInfo::getLabel";
  }

  std::string GetDescription() {
    return "AbilityInfo::getDescription";
  }

  std::string GetIcon() {
    return "AbilityInfo::getIcon";
  }

  int32_t GetLabelId() {
    return abilityInfoImpl;
  }

  int32_t GetDescriptionId() {
    return abilityInfoImpl;
  }

  int32_t GetIconId() {
    return abilityInfoImpl;
  }

  std::string GetModuleName() {
    return "AbilityInfo::getModuleName";
  }

  std::string GetProcess() {
    return "AbilityInfo::getProcess";
  }

  std::string GetTargetAbility() {
    return "AbilityInfo::getTargetAbility";
  }

  int32_t GetBackgroundModes() {
    return abilityInfoImpl;
  }

  bool GetIsVisible() {
    return true;
  }

  bool GetFormEnabled() {
    return true;
  }

  array<string> GetPermissions() {
    array<string> str = {"AbilityInfo::getTargetAbility"};
    return str;
  }

  array<string> GetDeviceTypes() {
    array<string> str = {"AbilityInfo::getDeviceTypes"};
    return str;
  }

  array<string> GetDeviceCapabilities() {
    array<string> str = {"AbilityInfo::getDeviceCapabilities"};
    return str;
  }

  std::string GetReadPermission() {
    return "AbilityInfo::getReadPermission";
  }

  std::string GetWritePermission() {
    return "AbilityInfo::getWritePermission";
  }

  std::string GetUri() {
    return "AbilityInfo::getUri";
  }

  bool GetEnabled() {
    return true;
  }
};

AbilityInfo GetAbilityInfo() {
  return make_holder<AbilityInfoImpl, AbilityInfo>();
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_GetAbilityInfo(GetAbilityInfo);
// NOLINTEND
