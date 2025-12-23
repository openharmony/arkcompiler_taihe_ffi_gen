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
  optional<string> deviceId;
  string bundleName_ = "bundleName_";
  string abilityName_ = "abilityName_";
  optional<string> uri;
  optional<string> shortName;

  ElementNameImpl() {}

  void SetDevicedId(optional<string> deviceId) {
    this->deviceId = deviceId;
  }

  optional<string> GetDevicedId() {
    return deviceId;
  }

  void SetBundleName(string_view bundleName) {
    bundleName_ = bundleName;
  }

  string GetBundleName() {
    return bundleName_;
  }

  void SetAbilityName(string_view abilityName) {
    abilityName_ = abilityName;
  }

  string GetAbilityName() {
    return abilityName_;
  }

  void SetUri(optional<string> uri) {
    this->uri = uri;
  }

  optional<string> GetUri() {
    return uri;
  }

  void SetShortName(optional<string> shortName) {
    this->shortName = shortName;
  }

  optional<string> GetShortName() {
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
