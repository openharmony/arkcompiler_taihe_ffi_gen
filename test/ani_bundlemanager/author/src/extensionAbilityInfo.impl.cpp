#include "extensionAbilityInfo.impl.hpp"
#include <iostream>
#include "extensionAbilityInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace extensionAbilityInfo;

namespace {
// To be implemented.

class ExtensionAbilityInfoImpl {
public:
  int32_t extensionAbilityInfoImpl = 21474;

  ExtensionAbilityInfoImpl() {}

  string GetBundleName() {
    return "ExtensionAbilityInfoImpl::getBundleName";
  }

  string GetModuleName() {
    return "ExtensionAbilityInfoImpl::getModuleName";
  }

  string GetName() {
    return "ExtensionAbilityInfoImpl::getName";
  }

  int32_t GetLabelId() {
    return extensionAbilityInfoImpl;
  }

  int32_t GetDescriptionId() {
    return extensionAbilityInfoImpl;
  }

  int32_t GetIconId() {
    return extensionAbilityInfoImpl;
  }

  bool GetExported() {
    return true;
  }

  bool GetExtensionAbilityTypeName() {
    return true;
  }

  array<string> GetPermissions() {
    array<string> str = {"ExtensionAbilityInfoImpl::getPermissions"};
    return str;
  }

  bool GetEnabled() {
    return true;
  }

  string GetReadPermission() {
    return "ExtensionAbilityInfoImpl::getReadPermission";
  }

  string GetWritePermission() {
    return "ExtensionAbilityInfoImpl::getWritePermission";
  }

  int32_t GetAppIndex() {
    return extensionAbilityInfoImpl;
  }
};

ExtensionAbilityInfo GetExtensionAbilityInfo() {
  return make_holder<ExtensionAbilityInfoImpl, ExtensionAbilityInfo>();
}
}  // namespace

TH_EXPORT_CPP_API_GetExtensionAbilityInfo(GetExtensionAbilityInfo);