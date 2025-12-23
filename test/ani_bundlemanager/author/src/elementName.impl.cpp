#include "elementName.impl.hpp"
#include "elementName.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace elementName;

namespace {
// To be implemented.

class ElementNameImpl {
public:
  string deviceId = "";
  string bundleName = "";
  string moduleName = "";
  string abilityName = "";
  string uri = "";
  string shortName = "";

  ElementNameImpl() {}

  void SetDevicedId(string_view deviceId) {
    this->deviceId = deviceId;
  }

  string GetDevicedId() {
    return deviceId;
  }

  void SetBundleName(string_view bundleName) {
    this->bundleName = bundleName;
  }

  string GetBundleName() {
    return bundleName;
  }

  void SetMundleName(string_view moduleName) {
    this->moduleName = moduleName;
  }

  string GetMundleName() {
    return moduleName;
  }

  void SetAbilityName(string_view abilityName) {
    this->abilityName = abilityName;
  }

  string GetAbilityName() {
    return abilityName;
  }

  void SetUri(string_view uri) {
    this->uri = uri;
  }

  string GetUri() {
    return uri;
  }

  void SetShortName(string_view shortName) {
    this->shortName = shortName;
  }

  string GetShortName() {
    return shortName;
  }
};

ElementName GetElementName() {
  return make_holder<ElementNameImpl, ElementName>();
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_GetElementName(GetElementName);
// NOLINTEND
