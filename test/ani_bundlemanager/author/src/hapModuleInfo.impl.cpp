#include "hapModuleInfo.impl.hpp"
#include <iostream>
#include "hapModuleInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace hapModuleInfo;

namespace {
// To be implemented.

class HapModuleInfoImpl {
public:
  int32_t hapModuleInfoImpl = 21474;

  HapModuleInfoImpl() {}

  string GetName() {
    return "HapModuleInfoImpl::getName";
  }

  string GetIcon() {
    return "HapModuleInfoImpl::getIcon";
  }

  int32_t GetIconId() {
    return hapModuleInfoImpl;
  }

  string GetLabel() {
    return "HapModuleInfoImpl::getLabel";
  }

  int32_t GetLabelId() {
    return hapModuleInfoImpl;
  }

  string GetDescription() {
    return "HapModuleInfoImpl::getDescription";
  }

  int32_t GetDescriptionId() {
    return hapModuleInfoImpl;
  }

  string GetMainElementName() {
    return "HapModuleInfoImpl::getMainElementName";
  }

  array<string> GetDeviceTypes() {
    array<string> str = {"HapModuleInfoImpl::getDeviceTypes"};
    return str;
  }

  bool GetInstallationFree() {
    return true;
  }

  string GetHashValue() {
    return "HapModuleInfoImpl::getHashValue";
  }

  string GetFileContextMenuConfig() {
    return "HapModuleInfoImpl::getFileContextMenuConfig";
  }

  string GetNativeLibraryPath() {
    return "HapModuleInfoImpl::getNativeLibraryPath";
  }

  string GetCodePath() {
    return "HapModuleInfoImpl::getCodePath";
  }
};

class DependencyImpl {
public:
  int32_t dependencyImpl = 21474;

  DependencyImpl() {}

  string GetModuleName() {
    return "HapModuleInfoImpl::getModuleName";
  }

  string GetBundleName() {
    return "HapModuleInfoImpl::getBundleName";
  }

  int32_t GetVersionCode() {
    return dependencyImpl;
  }
};

class PreloadItemImpl {
public:
  PreloadItemImpl() {}

  string GetModuleName() {
    return "PreloadItemImpl::getModuleName";
  }
};

class RouterItemImpl {
public:
  RouterItemImpl() {}

  string GetName() {
    return "RouterItemImpl::getName";
  }

  string GetPageSourceFile() {
    return "RouterItemImpl::getPageSourceFile";
  }

  string GetBuildFunction() {
    return "RouterItemImpl::getBuildFunction";
  }

  string GetCustomData() {
    return "RouterItemImpl::getCustomData";
  }
};

class DataItemImpl {
public:
  DataItemImpl() {}

  string GetKey() {
    return "DataItemImpl::getKey";
  }

  string GetValue() {
    return "DataItemImpl::getValue";
  }
};

HapModuleInfo GetHapModuleInfo() {
  return make_holder<HapModuleInfoImpl, HapModuleInfo>();
}

Dependency GetDependency() {
  return make_holder<DependencyImpl, Dependency>();
}

PreloadItem GetPreloadItem() {
  return make_holder<PreloadItemImpl, PreloadItem>();
}

RouterItem GetRouterItem() {
  return make_holder<RouterItemImpl, RouterItem>();
}

DataItem GetDataItem() {
  return make_holder<DataItemImpl, DataItem>();
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_GetHapModuleInfo(GetHapModuleInfo);
TH_EXPORT_CPP_API_GetDependency(GetDependency);
TH_EXPORT_CPP_API_GetPreloadItem(GetPreloadItem);
TH_EXPORT_CPP_API_GetRouterItem(GetRouterItem);
TH_EXPORT_CPP_API_GetDataItem(GetDataItem);
// NOLINTEND
