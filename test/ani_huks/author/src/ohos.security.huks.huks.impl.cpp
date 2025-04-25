#include <cstddef>
#include <cstdint>
#include <cstring>
#include <memory>
#include <optional>
#include <utility>

#include <taihe/array.hpp>
#include <taihe/optional.hpp>
#include <taihe/runtime.hpp>
#include <taihe/string.hpp>

#include "ohos.security.huks.huks.impl.hpp"
#include "ohos.security.huks.huks.proj.hpp"

#include "hks_api.h"
#include "hks_errcode_adapter.h"
#include "hks_errno.h"
#include "hks_mem.h"
#include "hks_param.h"
#include "hks_template.h"
#include "hks_type.h"
#include "hks_type_enum.h"

using namespace ohos::security::huks;

namespace {
using errno_t = int32_t;

errno_t U64FromBigInt(uint64_t *valuePtr, taihe::array_view<uint64_t> bigint) {
  if (bigint.size() == 0) {
    *valuePtr = 0;
  }
  *valuePtr = bigint[0];
  return HKS_SUCCESS;
}

errno_t BlobSetNull(HksBlob *blobPtr) {
  blobPtr->data = nullptr;
  blobPtr->size = 0;
  return HKS_SUCCESS;
}

errno_t BlobMallocBuffer(HksBlob *blobPtr, size_t size) {
  blobPtr->data = static_cast<uint8_t *>(HksMalloc(size));
  if (blobPtr->data == nullptr) {
    return HKS_ERROR_MALLOC_FAIL;
  }
  blobPtr->size = size;
  return HKS_SUCCESS;
}

errno_t BlobFromArray(HksBlob *blobPtr, taihe::array_view<uint8_t> av) {
  errno_t ret = BlobMallocBuffer(blobPtr, blobPtr->size);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  std::memcpy(blobPtr->data, av.data(), blobPtr->size);
  return HKS_SUCCESS;
}

errno_t BlobFromString(HksBlob *blobPtr, taihe::string_view sv) {
  errno_t ret = BlobMallocBuffer(blobPtr, blobPtr->size);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  std::memcpy(blobPtr->data, sv.data(), blobPtr->size);
  return HKS_SUCCESS;
}

void BlobFree(HksBlob *blobPtr, bool const isNeedFresh = false) {
  if (blobPtr->data != nullptr) {
    if (isNeedFresh && blobPtr->size != 0) {
      std::memset(blobPtr->data, 0, blobPtr->size);
    }
    HksFreeImpl(blobPtr->data);
    blobPtr->data = nullptr;
  }
  blobPtr->size = 0;
}

errno_t ParamParse(HksParam *hksParamPtr, huks::HuksParam taiheParam) {
  hksParamPtr->tag = taiheParam.tag.get_value();
  switch (GetTagType(static_cast<enum HksTag>(hksParamPtr->tag))) {
  case HKS_TAG_TYPE_INT:
    HKS_IF_NOT_TRUE_RETURN(taiheParam.value.holds_numberValue(), HKS_FAILURE);
    hksParamPtr->int32Param =
        static_cast<int32_t>(taiheParam.value.get_numberValue_ref());
    return HKS_SUCCESS;
  case HKS_TAG_TYPE_UINT:
    HKS_IF_NOT_TRUE_RETURN(taiheParam.value.holds_numberValue(), HKS_FAILURE);
    hksParamPtr->uint32Param =
        static_cast<uint32_t>(taiheParam.value.get_numberValue_ref());
    return HKS_SUCCESS;
  case HKS_TAG_TYPE_BOOL:
    HKS_IF_NOT_TRUE_RETURN(taiheParam.value.holds_booleanValue(), HKS_FAILURE);
    hksParamPtr->boolParam = taiheParam.value.get_booleanValue_ref();
    return HKS_SUCCESS;
  case HKS_TAG_TYPE_ULONG:
    HKS_IF_NOT_TRUE_RETURN(taiheParam.value.holds_bigintValue(), HKS_FAILURE);
    return U64FromBigInt(&hksParamPtr->uint64Param,
                         taiheParam.value.get_bigintValue_ref());
  case HKS_TAG_TYPE_BYTES:
    BlobSetNull(&hksParamPtr->blob);
    HKS_IF_NOT_TRUE_RETURN(taiheParam.value.holds_arrayValue(), HKS_FAILURE);
    return BlobFromArray(&hksParamPtr->blob,
                         taiheParam.value.get_arrayValue_ref());
  case HKS_TAG_TYPE_INVALID:
    return HKS_SUCCESS;
  default:
    return HKS_FAILURE;
  }
}

void ParamFree(HksParam *hksParamPtr) {
  switch (GetTagType(static_cast<enum HksTag>(hksParamPtr->tag))) {
  case HKS_TAG_TYPE_BYTES:
    return BlobFree(&hksParamPtr->blob);
  default:
    return;
  }
}

errno_t PropertiesParse(
    HksParamSet **hksParamSetPtr,
    taihe::optional_view<taihe::array<huks::HuksParam>> properties) {
  errno_t ret = HKS_SUCCESS;
  taihe::array<HksParam> hksParams(properties->size());
  size_t n = 0;
  do {
    for (; n < properties->size(); ++n) {
      ret = ParamParse(&hksParams[n], properties->at(n));
      HKS_IF_NOT_SUCC_BREAK(ret);
    }
    ret = HksInitParamSet(hksParamSetPtr);
    HKS_IF_NOT_SUCC_BREAK(ret);
    ret = HksAddParams(*hksParamSetPtr, hksParams.data(), hksParams.size());
    HKS_IF_NOT_SUCC_BREAK(ret);
    ret = HksBuildParamSet(hksParamSetPtr);
    HKS_IF_NOT_SUCC_BREAK(ret);
  } while (0);
  for (size_t i = 0; i < n; ++i) {
    ParamFree(&hksParams[i]);
  }
  if (ret != HKS_SUCCESS) {
    HksFreeParamSet(hksParamSetPtr);
  }
  return ret;
}

class CommonContext {
public:
  int32_t result = 0;
  struct HksBlob keyAlias{0, nullptr};
  struct HksParamSet *paramSetIn = nullptr;
  struct HksParamSet *paramSetOut = nullptr;

  CommonContext() = default;

  ~CommonContext() {
    BlobFree(&this->keyAlias);
    if (this->paramSetOut != nullptr) {
      HksFreeParamSet(&this->paramSetIn);
    }
    if (this->paramSetOut != nullptr) {
      HksFreeParamSet(&this->paramSetOut);
    }
  }
};

class KeyContext : public CommonContext {
public:
  struct HksBlob key{0, nullptr};

  KeyContext() = default;

  ~KeyContext() {
    BlobFree(&this->key, true);
  }
};

class ImportWrappedKeyContext : public KeyContext {
public:
  struct HksBlob wrappingKeyAlias{0, nullptr};

  ImportWrappedKeyContext() = default;

  ~ImportWrappedKeyContext() {
    BlobFree(&this->wrappingKeyAlias);
  }
};

class SessionContext : public CommonContext {
public:
  struct HksBlob inData{0, nullptr};
  struct HksBlob outData{0, nullptr};
  struct HksBlob handle{0, nullptr};
  struct HksBlob token{0, nullptr};

  SessionContext() = default;

  ~SessionContext() {
    BlobFree(&this->token, true);
    BlobFree(&this->handle);
    BlobFree(&this->inData);
    BlobFree(&this->outData, true);
  }
};

// Main

errno_t generateKeyInner(CommonContext &ctx, taihe::string_view keyAlias,
                         huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = BlobFromString(&ctx.keyAlias, keyAlias);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksGenerateKey(&ctx.keyAlias, ctx.paramSetIn, ctx.paramSetOut);
}

errno_t deleteKeyInner(CommonContext &ctx, taihe::string_view keyAlias,
                       huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = BlobFromString(&ctx.keyAlias, keyAlias);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksDeleteKey(&ctx.keyAlias, ctx.paramSetIn);
}

errno_t importKeyInner(KeyContext &ctx, taihe::string_view keyAlias,
                       huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = BlobFromString(&ctx.keyAlias, keyAlias);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = options.inData ? BlobFromArray(&ctx.key, *options.inData)
                       : BlobSetNull(&ctx.key);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksImportKey(&ctx.keyAlias, ctx.paramSetIn, &ctx.key);
}

errno_t importWrappedKeyInner(ImportWrappedKeyContext &ctx,
                              taihe::string_view keyAlias,
                              taihe::string_view wrappingKeyAlias,
                              huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = BlobFromString(&ctx.keyAlias, keyAlias);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = options.inData ? BlobFromArray(&ctx.key, *options.inData)
                       : BlobSetNull(&ctx.key);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = BlobFromString(&ctx.wrappingKeyAlias, wrappingKeyAlias);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksImportWrappedKey(&ctx.keyAlias, &ctx.wrappingKeyAlias,
                             ctx.paramSetIn, &ctx.key);
}

errno_t exportKeyInner(KeyContext &ctx, taihe::string_view keyAlias,
                       huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = BlobFromString(&ctx.keyAlias, keyAlias);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = BlobMallocBuffer(&ctx.key, MAX_KEY_SIZE);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksExportPublicKey(&ctx.keyAlias, ctx.paramSetIn, &ctx.key);
}

errno_t isKeyExistInner(CommonContext &ctx, taihe::string_view keyAlias,
                        huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = BlobFromString(&ctx.keyAlias, keyAlias);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksKeyExist(&ctx.keyAlias, ctx.paramSetIn);
}

errno_t initSessionSync(SessionContext &ctx, taihe::string_view keyAlias,
                        huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = BlobFromString(&ctx.keyAlias, keyAlias);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = BlobMallocBuffer(&ctx.handle, HKS_MAX_KEY_LEN);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = BlobMallocBuffer(&ctx.token, HKS_MAX_KEY_LEN);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksInit(&ctx.keyAlias, ctx.paramSetIn, &ctx.handle, &ctx.token);
}

errno_t updateSync(SessionContext &ctx, int64_t handle,
                   taihe::optional_view<taihe::array<uint8_t>> token,
                   huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = options.inData ? BlobFromArray(&ctx.inData, *options.inData)
                       : BlobSetNull(&ctx.inData);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = BlobMallocBuffer(&ctx.handle, HKS_MAX_KEY_LEN);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = BlobMallocBuffer(&ctx.outData, HKS_MAX_KEY_LEN);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksUpdate(&ctx.handle, ctx.paramSetIn, &ctx.inData, &ctx.outData);
}

errno_t finishSync(SessionContext &ctx, int64_t handle,
                   taihe::optional_view<taihe::array<uint8_t>> token,
                   huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = options.inData ? BlobFromArray(&ctx.inData, *options.inData)
                       : BlobSetNull(&ctx.inData);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = BlobMallocBuffer(&ctx.handle, HKS_MAX_KEY_LEN);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = BlobMallocBuffer(&ctx.outData, HKS_MAX_KEY_LEN);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksFinish(&ctx.handle, ctx.paramSetIn, &ctx.inData, &ctx.outData);
}

errno_t abortSessionSync(SessionContext &ctx, int64_t handle,
                         huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = options.inData ? BlobFromArray(&ctx.inData, *options.inData)
                       : BlobSetNull(&ctx.inData);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = BlobMallocBuffer(&ctx.handle, HKS_MAX_KEY_LEN);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksAbort(&ctx.handle, ctx.paramSetIn);
}

struct CertArray {
  std::unique_ptr<std::array<uint8_t, HKS_CERT_APP_SIZE>> appCert{};
  std::unique_ptr<std::array<uint8_t, HKS_CERT_DEVICE_SIZE>> devCert{};
  std::unique_ptr<std::array<uint8_t, HKS_CERT_CA_SIZE>> caCert{};
  std::unique_ptr<std::array<uint8_t, HKS_CERT_ROOT_SIZE>> rootCert{};
  std::unique_ptr<std::array<HksBlob, HKS_CERT_COUNT>> blob{};
  HksCertChain chain{};

  CertArray()
      : appCert(new std::array<uint8_t, HKS_CERT_APP_SIZE>),
        devCert(new std::array<uint8_t, HKS_CERT_DEVICE_SIZE>),
        caCert(new std::array<uint8_t, HKS_CERT_CA_SIZE>),
        rootCert(new std::array<uint8_t, HKS_CERT_ROOT_SIZE>),
        blob(new std::array<HksBlob, HKS_CERT_COUNT>{{
            {.size = HKS_CERT_APP_SIZE, .data = appCert->data()},
            {.size = HKS_CERT_DEVICE_SIZE, .data = devCert->data()},
            {.size = HKS_CERT_CA_SIZE, .data = caCert->data()},
            {.size = HKS_CERT_ROOT_SIZE, .data = rootCert->data()},
        }}),
        chain{.certs = blob->data(), .certsCount = HKS_CERT_COUNT} {}
};

errno_t attestKey(CommonContext &ctx, CertArray &ca,
                  taihe::string_view keyAlias,
                  huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = BlobFromString(&ctx.keyAlias, keyAlias);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksAttestKey(&ctx.keyAlias, ctx.paramSetIn, &ca.chain);
}

errno_t anonAttestKey(CommonContext &ctx, CertArray &ca,
                      taihe::string_view keyAlias,
                      huks::HuksOptions const &options) {
  errno_t ret = HKS_SUCCESS;
  ret = BlobFromString(&ctx.keyAlias, keyAlias);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  ret = PropertiesParse(&ctx.paramSetIn, options.properties);
  HKS_IF_NOT_SUCC_RETURN(ret, ret);
  return HksAnonAttestKey(&ctx.keyAlias, ctx.paramSetIn, &ca.chain);
}

// Return

template<errno_t... skips>
void SetErrorExcept(errno_t ret) {
  if (((skips != ret) && ...)) {
    HksResult resultInfo = HksConvertErrCode(ret);
    taihe::set_business_error(resultInfo.errorCode, resultInfo.errorMsg);
  }
}

taihe::array<uint8_t> GetArrayBuffer(HksBlob blob) {
  return taihe::array<uint8_t>{taihe::copy_data_t{}, blob.data, blob.size};
}

taihe::array<taihe::string> GetArrayString(HksCertChain certChain) {
  taihe::array<taihe::string> certs{certChain.certsCount};
  for (size_t i = 0; i < certChain.certsCount; ++i) {
    certs[i] = taihe::string(reinterpret_cast<char *>(certChain.certs[i].data),
                             certChain.certs[i].size);
  }
  return certs;
}

void GetVoid(errno_t ret) {
  SetErrorExcept<HKS_SUCCESS>(ret);
  return;
}

bool GetKeyExistBool(errno_t ret) {
  SetErrorExcept<HKS_SUCCESS, HKS_ERROR_KEY_NOT_EXIST>(ret);
  return ret == HKS_SUCCESS;
}

huks::HuksReturnResult GetReturnResult(errno_t ret, HksBlob outData) {
  SetErrorExcept<HKS_SUCCESS>(ret);
  return {
      .outData = {std::in_place, GetArrayBuffer(outData)},
  };
}

huks::HuksReturnResult GetReturnResult(errno_t ret, HksCertChain certChain) {
  SetErrorExcept<HKS_SUCCESS>(ret);
  return {
      .certChains = {std::in_place, GetArrayString(certChain)},
  };
}

huks::HuksSessionHandle GetSessionHandle(errno_t ret, HksBlob handle,
                                         HksBlob challenge) {
  SetErrorExcept<HKS_SUCCESS>(ret);
  return {
      .handle =
          static_cast<int64_t>(*reinterpret_cast<uint64_t *>(handle.data)),
      .challenge = {std::in_place, GetArrayBuffer(challenge)},
  };
}

// Exported

void generateKeyItemSync(taihe::string_view keyAlias,
                         huks::HuksOptions const &options) {
  CommonContext ctx;
  errno_t ret = generateKeyInner(ctx, keyAlias, options);
  return GetVoid(ret);
}

void deleteKeyItemSync(taihe::string_view keyAlias,
                       huks::HuksOptions const &options) {
  CommonContext ctx;
  errno_t ret = deleteKeyInner(ctx, keyAlias, options);
  return GetVoid(ret);
}

void importKeyItemSync(taihe::string_view keyAlias,
                       huks::HuksOptions const &options) {
  KeyContext ctx;
  errno_t ret = importKeyInner(ctx, keyAlias, options);
  return GetVoid(ret);
}

void importWrappedKeyItemSync(taihe::string_view keyAlias,
                              taihe::string_view wrappingKeyAlias,
                              huks::HuksOptions const &options) {
  ImportWrappedKeyContext ctx;
  errno_t ret = importWrappedKeyInner(ctx, keyAlias, wrappingKeyAlias, options);
  return GetVoid(ret);
}

huks::HuksReturnResult exportKeyItemSync(taihe::string_view keyAlias,
                                         huks::HuksOptions const &options) {
  KeyContext ctx;
  errno_t ret = exportKeyInner(ctx, keyAlias, options);
  return GetReturnResult(ret, ctx.key);
}

bool isKeyItemExistSync(taihe::string_view keyAlias,
                        huks::HuksOptions const &options) {
  CommonContext ctx;
  errno_t ret = isKeyExistInner(ctx, keyAlias, options);
  return GetKeyExistBool(ret);
}

huks::HuksSessionHandle initSessionSync(taihe::string_view keyAlias,
                                        huks::HuksOptions const &options) {
  SessionContext ctx;
  errno_t ret = initSessionSync(ctx, keyAlias, options);
  return GetSessionHandle(ret, ctx.handle, ctx.token);
}

huks::HuksReturnResult updateSessionSync(
    int64_t handle, huks::HuksOptions const &options,
    taihe::optional_view<taihe::array<uint8_t>> token) {
  SessionContext ctx;
  errno_t ret = updateSync(ctx, handle, token, options);
  return GetReturnResult(ret, ctx.outData);
}

huks::HuksReturnResult updateSessionSyncWithoutToken(
    int64_t handle, huks::HuksOptions const &options) {
  taihe::optional<taihe::array<uint8_t>> opt_token{std::nullopt};
  return updateSessionSync(handle, options, opt_token);
}

huks::HuksReturnResult updateSessionSyncWithToken(
    int64_t handle, huks::HuksOptions const &options,
    taihe::array_view<uint8_t> token) {
  taihe::optional<taihe::array<uint8_t>> opt_token{std::in_place, options};
  return updateSessionSync(handle, options, opt_token);
}

huks::HuksReturnResult finishSessionSync(
    int64_t handle, huks::HuksOptions const &options,
    taihe::optional_view<taihe::array<uint8_t>> token) {
  SessionContext ctx;
  errno_t ret = finishSync(ctx, handle, token, options);
  return GetReturnResult(ret, ctx.outData);
}

huks::HuksReturnResult finishSessionSyncWithoutToken(
    int64_t handle, huks::HuksOptions const &options) {
  taihe::optional<taihe::array<uint8_t>> opt_token{std::nullopt};
  return finishSessionSync(handle, options, opt_token);
}

huks::HuksReturnResult finishSessionSyncWithToken(
    int64_t handle, huks::HuksOptions const &options,
    taihe::array_view<uint8_t> token) {
  taihe::optional<taihe::array<uint8_t>> opt_token{std::in_place, options};
  return finishSessionSync(handle, options, opt_token);
}

void abortSessionSync(int64_t handle, huks::HuksOptions const &options) {
  SessionContext ctx;
  errno_t ret = abortSessionSync(ctx, handle, options);
  return GetVoid(ret);
}

huks::HuksReturnResult attestKeyItemSync(taihe::string_view keyAlias,
                                         huks::HuksOptions const &options) {
  CommonContext ctx;
  CertArray ca;
  errno_t ret = attestKey(ctx, ca, keyAlias, options);
  return GetReturnResult(ret, ca.chain);
}

huks::HuksReturnResult anonAttestKeyItemSync(taihe::string_view keyAlias,
                                             huks::HuksOptions const &options) {
  CommonContext ctx;
  CertArray ca;
  errno_t ret = anonAttestKey(ctx, ca, keyAlias, options);
  return GetReturnResult(ret, ca.chain);
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_generateKeyItemSync(generateKeyItemSync);
TH_EXPORT_CPP_API_deleteKeyItemSync(deleteKeyItemSync);
TH_EXPORT_CPP_API_importKeyItemSync(importKeyItemSync);
TH_EXPORT_CPP_API_importWrappedKeyItemSync(importWrappedKeyItemSync);
TH_EXPORT_CPP_API_exportKeyItemSync(exportKeyItemSync);
TH_EXPORT_CPP_API_isKeyItemExistSync(isKeyItemExistSync);
TH_EXPORT_CPP_API_initSessionSync(initSessionSync);
TH_EXPORT_CPP_API_updateSessionSyncWithoutToken(updateSessionSyncWithoutToken);
TH_EXPORT_CPP_API_updateSessionSyncWithToken(updateSessionSyncWithToken);
TH_EXPORT_CPP_API_updateSessionSync(updateSessionSync);
TH_EXPORT_CPP_API_finishSessionSyncWithoutToken(finishSessionSyncWithoutToken);
TH_EXPORT_CPP_API_finishSessionSyncWithToken(finishSessionSyncWithToken);
TH_EXPORT_CPP_API_finishSessionSync(finishSessionSync);
TH_EXPORT_CPP_API_abortSessionSync(abortSessionSync);
TH_EXPORT_CPP_API_attestKeyItemSync(attestKeyItemSync);
TH_EXPORT_CPP_API_anonAttestKeyItemSync(anonAttestKeyItemSync);
// NOLINTEND
