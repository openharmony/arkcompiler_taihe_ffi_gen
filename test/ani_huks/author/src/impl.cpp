#include "huks.impl.hpp"
#include "huks.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace huks;

namespace {
// To be implemented.

std::string ArrayAsString(array_view<uint8_t> data) {
  std::string res;
  int const tempnum = 16;
  for (int i = 0; i < data.size(); i++) {
    uint8_t c = static_cast<uint8_t>(data[i]);
    static constexpr char const *const TEST_STR = "0123456789abcdef";
    res += TEST_STR[data[i] / tempnum];
    res += TEST_STR[data[i] % tempnum];
  }
  return res;
}

std::string BigIntAsString(array<uint64_t> const &data) {
  std::string res;
  for (auto const &item : data) {
    res += std::to_string(item);
    res += " ";
  }
  return res;
}

HuksResult generateKeySync(string_view keyAlias, HuksOptions const &options) {
  std::cout << "keyAlias: " << keyAlias << std::endl;
  if (auto inData = options.inData) {
    std::cout << "inData = " << ArrayAsString(*inData) << std::endl;
  } else {
    std::cout << "No inData!" << std::endl;
  }
  if (auto properties = options.properties) {
    std::cout << "Properties:" << std::endl;
    for (auto const &property : *properties) {
      std::cout << "tag = " << (size_t)property.tag.get_value() << std::endl;
      switch (property.value.get_tag()) {
      case huks::HuksParamValue::tag_t::bigintValue:
        std::cout << "bigint "
                  << BigIntAsString(property.value.get_bigintValue_ref())
                  << std::endl;
        break;
      case huks::HuksParamValue::tag_t::booleanValue:
        std::cout << "boolean " << property.value.get_booleanValue_ref()
                  << std::endl;
        break;
      case huks::HuksParamValue::tag_t::arrayValue:
        std::cout << "array "
                  << ArrayAsString(property.value.get_arrayValue_ref())
                  << std::endl;
        break;
      case huks::HuksParamValue::tag_t::numberValue:
        std::cout << "number " << property.value.get_numberValue_ref()
                  << std::endl;
        break;
      }
    }
  } else {
    std::cout << "No Properties!" << std::endl;
  }
  huks::HuksParam huksParam = {
      .tag = huks::HuksTag::key_t::HUKS_TAG_ACCESS_TIME,
      .value =
          huks::HuksParamValue::make_arrayValue(array<uint8_t>::make(4, 0xcc)),
  };
  huks::HuksResult huksResult = {
      .errorCode = 0.0,
      .outData = optional<array<uint8_t>>::make(array<uint8_t>::make(3, 0x12)),
      .properties = optional<array<huks::HuksParam>>::make(
          array<huks::HuksParam>::make(7, huksParam)),
      .certChains =
          optional<array<string>>::make(array<string>::make(5, "Hello")),
  };
  return huksResult;
}

void generateKeyItemSync(string_view keyAlias, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "generateKeyItemSync not implemented");
}

HuksResult deleteKeySync(string_view keyAlias, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "deleteKeySync not implemented");
}

void deleteKeyItemSync(string_view keyAlias, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "deleteKeyItemSync not implemented");
}

HuksResult importKeySync(string_view keyAlias, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "importKeySync not implemented");
}

void importKeyItemSync(string_view keyAlias, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "importKeyItemSync not implemented");
}

void importWrappedKeyItemSync(string_view keyAlias,
                              string_view wrappingKeyAlias,
                              HuksOptions const &options) {
  TH_THROW(std::runtime_error, "importWrappedKeyItemSync not implemented");
}

HuksResult exportKeySync(string_view keyAlias, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "exportKeySync not implemented");
}

HuksReturnResult exportKeyItemSync(string_view keyAlias,
                                   HuksOptions const &options) {
  TH_THROW(std::runtime_error, "exportKeyItemSync not implemented");
}

HuksResult getKeyPropertiesSync(string_view keyAlias,
                                HuksOptions const &options) {
  TH_THROW(std::runtime_error, "getKeyPropertiesSync not implemented");
}

HuksReturnResult getKeyItemPropertiesSync(string_view keyAlias,
                                          HuksOptions const &options) {
  TH_THROW(std::runtime_error, "getKeyItemPropertiesSync not implemented");
}

bool isKeyExistSync(string_view keyAlias, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "isKeyExistSync not implemented");
}

bool isKeyItemExistSync(string_view keyAlias, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "isKeyItemExistSync not implemented");
}

bool hasKeyItemSync(string_view keyAlias, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "hasKeyItemSync not implemented");
}

HuksHandle initSync(string_view keyAlias, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "initSync not implemented");
}

HuksSessionHandle initSessionSync(string_view keyAlias,
                                  HuksOptions const &options) {
  TH_THROW(std::runtime_error, "initSessionSync not implemented");
}

HuksResult updateSync(double handle, optional_view<array<uint8_t>> token,
                      HuksOptions const &options) {
  TH_THROW(std::runtime_error, "updateSync not implemented");
}

HuksReturnResult updateSessionSyncWithoutToken(double handle,
                                               HuksOptions const &options) {
  TH_THROW(std::runtime_error, "updateSessionSyncWithoutToken not implemented");
}

HuksReturnResult updateSessionSyncWithToken(double handle,
                                            HuksOptions const &options,
                                            array_view<uint8_t> token) {
  TH_THROW(std::runtime_error, "updateSessionSyncWithToken not implemented");
}

HuksReturnResult updateSessionSync(double handle, HuksOptions const &options,
                                   optional_view<array<uint8_t>> token) {
  TH_THROW(std::runtime_error, "updateSessionSync not implemented");
}

HuksResult finishSync(double handle, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "finishSync not implemented");
}

HuksReturnResult finishSessionSyncWithoutToken(double handle,
                                               HuksOptions const &options) {
  TH_THROW(std::runtime_error, "finishSessionSyncWithoutToken not implemented");
}

HuksReturnResult finishSessionSyncWithToken(double handle,
                                            HuksOptions const &options,
                                            array_view<uint8_t> token) {
  TH_THROW(std::runtime_error, "finishSessionSyncWithToken not implemented");
}

HuksReturnResult finishSessionSync(double handle, HuksOptions const &options,
                                   optional_view<array<uint8_t>> token) {
  TH_THROW(std::runtime_error, "finishSessionSync not implemented");
}

HuksResult abortSync(double handle, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "abortSync not implemented");
}

void abortSessionSync(double handle, HuksOptions const &options) {
  TH_THROW(std::runtime_error, "abortSessionSync not implemented");
}

HuksReturnResult attestKeyItemSync(string_view keyAlias,
                                   HuksOptions const &options) {
  TH_THROW(std::runtime_error, "attestKeyItemSync not implemented");
}

HuksReturnResult anonAttestKeyItemSync(string_view keyAlias,
                                       HuksOptions const &options) {
  TH_THROW(std::runtime_error, "anonAttestKeyItemSync not implemented");
}

string getSdkVersion(HuksOptions const &options) {
  TH_THROW(std::runtime_error, "getSdkVersion not implemented");
}

HuksListAliasesReturnResult listAliasesSync(HuksOptions const &options) {
  TH_THROW(std::runtime_error, "listAliasesSync not implemented");
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_generateKeySync(generateKeySync);
TH_EXPORT_CPP_API_generateKeyItemSync(generateKeyItemSync);
TH_EXPORT_CPP_API_deleteKeySync(deleteKeySync);
TH_EXPORT_CPP_API_deleteKeyItemSync(deleteKeyItemSync);
TH_EXPORT_CPP_API_importKeySync(importKeySync);
TH_EXPORT_CPP_API_importKeyItemSync(importKeyItemSync);
TH_EXPORT_CPP_API_importWrappedKeyItemSync(importWrappedKeyItemSync);
TH_EXPORT_CPP_API_exportKeySync(exportKeySync);
TH_EXPORT_CPP_API_exportKeyItemSync(exportKeyItemSync);
TH_EXPORT_CPP_API_getKeyPropertiesSync(getKeyPropertiesSync);
TH_EXPORT_CPP_API_getKeyItemPropertiesSync(getKeyItemPropertiesSync);
TH_EXPORT_CPP_API_isKeyExistSync(isKeyExistSync);
TH_EXPORT_CPP_API_isKeyItemExistSync(isKeyItemExistSync);
TH_EXPORT_CPP_API_hasKeyItemSync(hasKeyItemSync);
TH_EXPORT_CPP_API_initSync(initSync);
TH_EXPORT_CPP_API_initSessionSync(initSessionSync);
TH_EXPORT_CPP_API_updateSync(updateSync);
TH_EXPORT_CPP_API_updateSessionSyncWithoutToken(updateSessionSyncWithoutToken);
TH_EXPORT_CPP_API_updateSessionSyncWithToken(updateSessionSyncWithToken);
TH_EXPORT_CPP_API_updateSessionSync(updateSessionSync);
TH_EXPORT_CPP_API_finishSync(finishSync);
TH_EXPORT_CPP_API_finishSessionSyncWithoutToken(finishSessionSyncWithoutToken);
TH_EXPORT_CPP_API_finishSessionSyncWithToken(finishSessionSyncWithToken);
TH_EXPORT_CPP_API_finishSessionSync(finishSessionSync);
TH_EXPORT_CPP_API_abortSync(abortSync);
TH_EXPORT_CPP_API_abortSessionSync(abortSessionSync);
TH_EXPORT_CPP_API_attestKeyItemSync(attestKeyItemSync);
TH_EXPORT_CPP_API_anonAttestKeyItemSync(anonAttestKeyItemSync);
TH_EXPORT_CPP_API_getSdkVersion(getSdkVersion);
TH_EXPORT_CPP_API_listAliasesSync(listAliasesSync);
// NOLINTEND
