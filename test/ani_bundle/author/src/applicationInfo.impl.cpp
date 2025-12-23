#include "applicationInfo.impl.hpp"
#include <iostream>
#include "applicationInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace applicationInfo;

namespace {
// To be implemented.

class ApplicationInfoImpl {
public:
  int32_t applicationInfoImpl = 102;

  ApplicationInfoImpl() {}

  string GetName() {
    return "ApplicationInfo::getName";
  }

  string GetDescription() {
    return "ApplicationInfo::getDescription";
  }

  int32_t GetDescriptionId() {
    return applicationInfoImpl;
  }

  bool GetSystemApp() {
    return true;
  }

  bool GetEnabled() {
    return true;
  }

  string GetLabel() {
    return "ApplicationInfo::getLabel";
  }

  string GetLabelId() {
    return "ApplicationInfo::getLabelId";
  }

  string GetIcon() {
    return "ApplicationInfo::getIcon";
  }

  int32_t GetIconId() {
    return applicationInfoImpl;
  }

  string GetProcess() {
    return "ApplicationInfo::getProcess";
  }

  int32_t GetSupportedModes() {
    return applicationInfoImpl;
  }

  array<string> GetModuleSourceDirs() {
    array<string> str = {"ApplicationInfo::getProcess"};
    return str;
  }

  array<string> GetPermissions() {
    array<string> str = {"ApplicationInfo::getPermissions"};
    return str;
  }

  string GetEntryDir() {
    return "ApplicationInfo::getEntryDir";
  }

  string GetCodePath() {
    return "ApplicationInfo::getCodePath";
  }

  bool GetRemovable() {
    return true;
  }

  int32_t GetAccessTokenId() {
    return applicationInfoImpl;
  }

  int32_t GetUid() {
    return applicationInfoImpl;
  }

  string GetEntityType() {
    return "ApplicationInfo::getEntityType";
  }
};

ApplicationInfo GetApplicationInfo() {
  return make_holder<ApplicationInfoImpl, ApplicationInfo>();
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_GetApplicationInfo(GetApplicationInfo);
// NOLINTEND
