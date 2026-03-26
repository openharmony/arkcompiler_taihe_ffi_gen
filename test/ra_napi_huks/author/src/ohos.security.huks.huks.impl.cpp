/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
// This file is a test file.
// NOLINTBEGIN

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <memory>
#include <optional>
#include <utility>

#include <taihe/array.hpp>
#include <taihe/optional.hpp>
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

#define OUTPUT_DATA_SIZE 0x10000

using namespace ohos::security::huks;

namespace {
using errno_t = int32_t;

errno_t U64FromBigInt(uint64_t *valuePtr, taihe::array_view<uint64_t> bigint)
{
    if (bigint.size() == 0) {
        *valuePtr = 0;
    }
    *valuePtr = bigint[0];
    return HKS_SUCCESS;
}

errno_t BlobSetNull(HksBlob *blobPtr)
{
    blobPtr->data = nullptr;
    blobPtr->size = 0;
    return HKS_SUCCESS;
}

errno_t BlobMallocBuffer(HksBlob *blobPtr, size_t size)
{
    blobPtr->data = static_cast<uint8_t *>(HksMalloc(size));
    if (blobPtr->data == nullptr) {
        return HKS_ERROR_MALLOC_FAIL;
    }
    blobPtr->size = size;
    return HKS_SUCCESS;
}

errno_t BlobFromLong(HksBlob *blobPtr, int64_t value)
{
    errno_t ret = BlobMallocBuffer(blobPtr, sizeof(value));
    HKS_IF_NOT_SUCC_RETURN(ret, ret);
    std::memcpy(blobPtr->data, &value, sizeof(value));
    return HKS_SUCCESS;
}

errno_t BlobFromArray(HksBlob *blobPtr, taihe::array_view<uint8_t> av)
{
    errno_t ret = BlobMallocBuffer(blobPtr, av.size());
    HKS_IF_NOT_SUCC_RETURN(ret, ret);
    std::memcpy(blobPtr->data, av.data(), av.size());
    return HKS_SUCCESS;
}

errno_t BlobFromString(HksBlob *blobPtr, taihe::string_view sv)
{
    errno_t ret = BlobMallocBuffer(blobPtr, sv.size());
    HKS_IF_NOT_SUCC_RETURN(ret, ret);
    std::memcpy(blobPtr->data, sv.data(), sv.size());
    return HKS_SUCCESS;
}

void BlobFree(HksBlob *blobPtr, bool const isNeedFresh = false)
{
    if (blobPtr->data != nullptr) {
        if (isNeedFresh && blobPtr->size != 0) {
            std::memset(blobPtr->data, 0, blobPtr->size);
        }
        HksFreeImpl(blobPtr->data);
        blobPtr->data = nullptr;
    }
    blobPtr->size = 0;
}

errno_t ParamParse(HksParam *hksParamPtr, huks::HuksParam const &taiheParam)
{
    hksParamPtr->tag = taiheParam.tag.get_value();
    switch (GetTagType(static_cast<enum HksTag>(hksParamPtr->tag))) {
        case HKS_TAG_TYPE_INT:
            HKS_IF_NOT_TRUE_RETURN(taiheParam.value.holds_numberValue(), HKS_FAILURE);
            hksParamPtr->int32Param = static_cast<int32_t>(taiheParam.value.get_numberValue_ref());
            return HKS_SUCCESS;
        case HKS_TAG_TYPE_UINT:
            HKS_IF_NOT_TRUE_RETURN(taiheParam.value.holds_numberValue(), HKS_FAILURE);
            hksParamPtr->uint32Param = static_cast<uint32_t>(taiheParam.value.get_numberValue_ref());
            return HKS_SUCCESS;
        case HKS_TAG_TYPE_BOOL:
            HKS_IF_NOT_TRUE_RETURN(taiheParam.value.holds_booleanValue(), HKS_FAILURE);
            hksParamPtr->boolParam = taiheParam.value.get_booleanValue_ref();
            return HKS_SUCCESS;
        case HKS_TAG_TYPE_ULONG:
            HKS_IF_NOT_TRUE_RETURN(taiheParam.value.holds_bigintValue(), HKS_FAILURE);
            return U64FromBigInt(&hksParamPtr->uint64Param, taiheParam.value.get_bigintValue_ref());
        case HKS_TAG_TYPE_BYTES:
            BlobSetNull(&hksParamPtr->blob);
            HKS_IF_NOT_TRUE_RETURN(taiheParam.value.holds_arrayValue(), HKS_FAILURE);
            return BlobFromArray(&hksParamPtr->blob, taiheParam.value.get_arrayValue_ref());
        default:
            return HKS_FAILURE;
    }
}

void ParamFree(HksParam *hksParamPtr)
{
    switch (GetTagType(static_cast<enum HksTag>(hksParamPtr->tag))) {
        case HKS_TAG_TYPE_BYTES:
            return BlobFree(&hksParamPtr->blob);
        default:
            return;
    }
}

template<bool isNeedFresh = false>
struct BlobGuard {
    HksBlob data {0, nullptr};

    BlobGuard() = default;

    ~BlobGuard()
    {
        BlobFree(&this->data, isNeedFresh);
    }
};

errno_t PropertiesParse(HksParamSet **hksParamSetPtr, taihe::optional_view<taihe::array<huks::HuksParam>> properties)
{
    errno_t ret = HKS_SUCCESS;
    taihe::array<HksParam> hksParams(properties->size());
    size_t n = 0;
    do {
        for (; n < properties->size(); ++n) {
            ret = ParamParse(&hksParams[n], properties->at(n));
            HKS_IF_NOT_SUCC_BREAK(ret);
        }
        HKS_IF_NOT_SUCC_BREAK(ret);
        ret = HksInitParamSet(hksParamSetPtr);
        HKS_IF_NOT_SUCC_BREAK(ret);
        ret = HksAddParams(*hksParamSetPtr, hksParams.data(), hksParams.size());
        HKS_IF_NOT_SUCC_BREAK(ret);
        ret = HksBuildParamSet(hksParamSetPtr);
    } while (0);
    for (size_t i = 0; i < n; ++i) {
        ParamFree(&hksParams[i]);
    }
    if (ret != HKS_SUCCESS) {
        HksFreeParamSet(hksParamSetPtr);
    }
    return ret;
}

void PropertiesFree(HksParamSet **hksParamSetPtr)
{
    if (hksParamSetPtr != nullptr) {
        HksFreeParamSet(hksParamSetPtr);
    }
}

struct ParamSetGuard {
    HksParamSet *data {nullptr};

    ParamSetGuard() = default;

    ~ParamSetGuard()
    {
        PropertiesFree(&this->data);
    }
};

struct CertChainGuard {
    std::unique_ptr<std::array<uint8_t, HKS_CERT_APP_SIZE>> appCert {};
    std::unique_ptr<std::array<uint8_t, HKS_CERT_DEVICE_SIZE>> devCert {};
    std::unique_ptr<std::array<uint8_t, HKS_CERT_CA_SIZE>> caCert {};
    std::unique_ptr<std::array<uint8_t, HKS_CERT_ROOT_SIZE>> rootCert {};
    std::unique_ptr<std::array<HksBlob, HKS_CERT_COUNT>> blob {};
    HksCertChain data {};

    CertChainGuard()
        : appCert(new std::array<uint8_t, HKS_CERT_APP_SIZE>)
        , devCert(new std::array<uint8_t, HKS_CERT_DEVICE_SIZE>)
        , caCert(new std::array<uint8_t, HKS_CERT_CA_SIZE>)
        , rootCert(new std::array<uint8_t, HKS_CERT_ROOT_SIZE>)
        , blob(new std::array<HksBlob, HKS_CERT_COUNT> {{
              {.size = HKS_CERT_APP_SIZE, .data = appCert->data()},
              {.size = HKS_CERT_DEVICE_SIZE, .data = devCert->data()},
              {.size = HKS_CERT_CA_SIZE, .data = caCert->data()},
              {.size = HKS_CERT_ROOT_SIZE, .data = rootCert->data()},
          }})
        , data {.certs = blob->data(), .certsCount = HKS_CERT_COUNT}
    {
    }
};

// Return

template<errno_t... skips>
void SetErrorExcept(errno_t ret)
{
    if (((skips != ret) && ...)) {
        HksResult resultInfo = HksConvertErrCode(ret);
        // taihe::set_business_error(resultInfo.errorCode, resultInfo.errorMsg);
    }
}

taihe::array<uint8_t> GetArrayBuffer(HksBlob blob)
{
    return taihe::array<uint8_t> {taihe::copy_data, blob.data, blob.size};
}

taihe::array<taihe::string> GetArrayString(HksCertChain certChain)
{
    taihe::array<taihe::string> certs(certChain.certsCount, "");
    for (size_t i = 0; i < certChain.certsCount; ++i) {
        certs[i] = taihe::string(reinterpret_cast<char *>(certChain.certs[i].data), certChain.certs[i].size);
    }
    return certs;
}

void GetVoid(errno_t ret)
{
    SetErrorExcept<HKS_SUCCESS>(ret);
    return;
}

bool GetKeyExistBool(errno_t ret)
{
    SetErrorExcept<HKS_SUCCESS, HKS_ERROR_KEY_NOT_EXIST>(ret);
    return ret == HKS_SUCCESS;
}

huks::HuksReturnResult GetReturnResult(errno_t ret, HksBlob outData)
{
    SetErrorExcept<HKS_SUCCESS>(ret);
    return {
        .outData = ::taihe::optional<::taihe::array<uint8_t>>(std::in_place, GetArrayBuffer(outData)),
    };
}

huks::HuksReturnResult GetReturnResult(errno_t ret, HksCertChain certChain)
{
    SetErrorExcept<HKS_SUCCESS>(ret);
    return {
        .certChains = ::taihe::optional<::taihe::array<::taihe::string>>(std::in_place, GetArrayString(certChain)),
    };
}

huks::HuksSessionHandle GetSessionHandle(errno_t ret, HksBlob handle, HksBlob challenge)
{
    SetErrorExcept<HKS_SUCCESS>(ret);
    return {
        .handle = static_cast<int64_t>(*reinterpret_cast<uint64_t *>(handle.data)),
        .challenge = ::taihe::optional<::taihe::array<uint8_t>>(std::in_place, GetArrayBuffer(challenge)),
    };
}

// Exported

void generateKeyItemSync(taihe::string_view keyAlias, huks::HuksOptions const &options)
{
    BlobGuard<0> ctxKeyAlias;
    ParamSetGuard ctxParamSetIn;
    ParamSetGuard ctxParamSetOut;
    errno_t ret;
    do {
        ret = BlobFromString(&ctxKeyAlias.data, keyAlias);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksGenerateKey(&ctxKeyAlias.data, ctxParamSetIn.data, ctxParamSetOut.data);
    } while (0);
    return GetVoid(ret);
}

::taihe::expected<void, ::taihe::error> generateKeyItemAsync(::taihe::string_view keyAlias,
                                                             ::ohos::security::huks::huks::HuksOptions const &options)
{
    generateKeyItemSync(keyAlias, options);
    return {};
}

::taihe::expected<void, ::taihe::error> generateKeyItemRetpromise(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    generateKeyItemSync(keyAlias, options);
    return {};
}

void deleteKeyItemSync(taihe::string_view keyAlias, huks::HuksOptions const &options)
{
    BlobGuard<0> ctxKeyAlias;
    ParamSetGuard ctxParamSetIn;
    errno_t ret;
    do {
        ret = BlobFromString(&ctxKeyAlias.data, keyAlias);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksDeleteKey(&ctxKeyAlias.data, ctxParamSetIn.data);
    } while (0);
    return GetVoid(ret);
}

::taihe::expected<void, ::taihe::error> deleteKeyItemAsync(::taihe::string_view keyAlias,
                                                           ::ohos::security::huks::huks::HuksOptions const &options)
{
    deleteKeyItemSync(keyAlias, options);
    return {};
}

::taihe::expected<void, ::taihe::error> deleteKeyItemRetpromise(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    deleteKeyItemSync(keyAlias, options);
    return {};
}

void importKeyItemSync(taihe::string_view keyAlias, huks::HuksOptions const &options)
{
    BlobGuard<0> ctxKeyAlias;
    ParamSetGuard ctxParamSetIn;
    BlobGuard<1> ctxKey;
    errno_t ret;
    do {
        ret = BlobFromString(&ctxKeyAlias.data, keyAlias);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = options.inData ? BlobFromArray(&ctxKey.data, *options.inData) : BlobSetNull(&ctxKey.data);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksImportKey(&ctxKeyAlias.data, ctxParamSetIn.data, &ctxKey.data);
    } while (0);
    return GetVoid(ret);
}

::taihe::expected<void, ::taihe::error> importKeyItemAsync(::taihe::string_view keyAlias,
                                                           ::ohos::security::huks::huks::HuksOptions const &options)
{
    importKeyItemSync(keyAlias, options);
    return {};
}

::taihe::expected<void, ::taihe::error> importKeyItemRetpromise(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    importKeyItemSync(keyAlias, options);
    return {};
}

void importWrappedKeyItemSync(taihe::string_view keyAlias, taihe::string_view wrappingKeyAlias,
                              huks::HuksOptions const &options)
{
    BlobGuard<0> ctxKeyAlias;
    BlobGuard<0> ctxWrappingKeyAlias;
    ParamSetGuard ctxParamSetIn;
    BlobGuard<1> ctxKey;
    errno_t ret;
    do {
        ret = BlobFromString(&ctxKeyAlias.data, keyAlias);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = options.inData ? BlobFromArray(&ctxKey.data, *options.inData) : BlobSetNull(&ctxKey.data);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = BlobFromString(&ctxWrappingKeyAlias.data, wrappingKeyAlias);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksImportWrappedKey(&ctxKeyAlias.data, &ctxWrappingKeyAlias.data, ctxParamSetIn.data, &ctxKey.data);
    } while (0);
    return GetVoid(ret);
}

::taihe::expected<void, ::taihe::error> importWrappedKeyItemAsync(
    ::taihe::string_view keyAlias, ::taihe::string_view wrappingKeyAlias,
    ::ohos::security::huks::huks::HuksOptions const &options)
{
    importWrappedKeyItemSync(keyAlias, wrappingKeyAlias, options);
    return {};
}

::taihe::expected<void, ::taihe::error> importWrappedKeyItemRetpromise(
    ::taihe::string_view keyAlias, ::taihe::string_view wrappingKeyAlias,
    ::ohos::security::huks::huks::HuksOptions const &options)
{
    importWrappedKeyItemSync(keyAlias, wrappingKeyAlias, options);
    return {};
}

huks::HuksReturnResult exportKeyItemSync(taihe::string_view keyAlias, huks::HuksOptions const &options)
{
    BlobGuard<0> ctxKeyAlias;
    ParamSetGuard ctxParamSetIn;
    BlobGuard<1> ctxKey;
    errno_t ret;
    do {
        ret = BlobFromString(&ctxKeyAlias.data, keyAlias);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = BlobMallocBuffer(&ctxKey.data, MAX_KEY_SIZE);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksExportPublicKey(&ctxKeyAlias.data, ctxParamSetIn.data, &ctxKey.data);
    } while (0);
    return GetReturnResult(ret, ctxKey.data);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> exportKeyItemAsync(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    return exportKeyItemSync(keyAlias, options);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> exportKeyItemRetpromise(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    return exportKeyItemSync(keyAlias, options);
}

bool isKeyItemExistSync(taihe::string_view keyAlias, huks::HuksOptions const &options)
{
    BlobGuard<0> ctxKeyAlias;
    ParamSetGuard ctxParamSetIn;
    errno_t ret;
    do {
        ret = BlobFromString(&ctxKeyAlias.data, keyAlias);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksKeyExist(&ctxKeyAlias.data, ctxParamSetIn.data);
    } while (0);
    return GetKeyExistBool(ret);
}

::taihe::expected<bool, ::taihe::error> isKeyItemExistAsync(::taihe::string_view keyAlias,
                                                            ::ohos::security::huks::huks::HuksOptions const &options)
{
    return isKeyItemExistSync(keyAlias, options);
}

::taihe::expected<bool, ::taihe::error> isKeyItemExistRetpromise(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    return isKeyItemExistSync(keyAlias, options);
}

huks::HuksSessionHandle initSessionSync(taihe::string_view keyAlias, huks::HuksOptions const &options)
{
    BlobGuard<0> ctxKeyAlias;
    ParamSetGuard ctxParamSetIn;
    BlobGuard<0> ctxHandle;
    BlobGuard<1> ctxToken;
    errno_t ret;
    do {
        ret = BlobFromString(&ctxKeyAlias.data, keyAlias);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = BlobMallocBuffer(&ctxHandle.data, HKS_MAX_KEY_LEN);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = BlobMallocBuffer(&ctxToken.data, HKS_MAX_KEY_LEN);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksInit(&ctxKeyAlias.data, ctxParamSetIn.data, &ctxHandle.data, &ctxToken.data);
    } while (0);
    return GetSessionHandle(ret, ctxHandle.data, ctxToken.data);
}

::taihe::expected<::ohos::security::huks::huks::HuksSessionHandle, ::taihe::error> initSessionAsync(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    return initSessionSync(keyAlias, options);
}

::taihe::expected<::ohos::security::huks::huks::HuksSessionHandle, ::taihe::error> initSessionRetpromise(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    return initSessionSync(keyAlias, options);
}

huks::HuksReturnResult updateSessionSync(int64_t handle, huks::HuksOptions const &options,
                                         taihe::optional_view<taihe::array<uint8_t>> token)
{
    BlobGuard<0> ctxHandle;
    ParamSetGuard ctxParamSetIn;
    BlobGuard<0> ctxInData;
    BlobGuard<1> ctxOutData;
    errno_t ret;
    do {
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = options.inData ? BlobFromArray(&ctxInData.data, *options.inData) : BlobSetNull(&ctxInData.data);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = BlobFromLong(&ctxHandle.data, handle);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = BlobMallocBuffer(&ctxOutData.data, ctxInData.data.size + OUTPUT_DATA_SIZE);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksUpdate(&ctxHandle.data, ctxParamSetIn.data, &ctxInData.data, &ctxOutData.data);
    } while (0);
    return GetReturnResult(ret, ctxOutData.data);
}

huks::HuksReturnResult updateSessionSyncWithoutToken(int64_t handle, huks::HuksOptions const &options)
{
    taihe::optional<taihe::array<uint8_t>> opt_token(std::nullopt);
    return updateSessionSync(handle, options, opt_token);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> updateSessionAsyncWithoutToken(
    int64_t handle, ::ohos::security::huks::huks::HuksOptions const &options)
{
    return updateSessionSyncWithoutToken(handle, options);
}

huks::HuksReturnResult updateSessionSyncWithToken(int64_t handle, huks::HuksOptions const &options,
                                                  taihe::array_view<uint8_t> token)
{
    taihe::optional<taihe::array<uint8_t>> opt_token(std::in_place, token);
    return updateSessionSync(handle, options, opt_token);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> updateSessionAsyncWithToken(
    int64_t handle, ::ohos::security::huks::huks::HuksOptions const &options, ::taihe::array_view<uint8_t> token)
{
    return updateSessionSyncWithToken(handle, options, token);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> updateSessionRetpromise(
    int64_t handle, ::ohos::security::huks::huks::HuksOptions const &options,
    ::taihe::optional_view<::taihe::array<uint8_t>> token)
{
    return updateSessionSync(handle, options, token);
}

huks::HuksReturnResult finishSessionSync(int64_t handle, huks::HuksOptions const &options,
                                         taihe::optional_view<taihe::array<uint8_t>> token)
{
    BlobGuard<0> ctxHandle;
    ParamSetGuard ctxParamSetIn;
    BlobGuard<0> ctxInData;
    BlobGuard<1> ctxOutData;
    errno_t ret;
    do {
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = options.inData ? BlobFromArray(&ctxInData.data, *options.inData) : BlobSetNull(&ctxInData.data);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = BlobFromLong(&ctxHandle.data, handle);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = BlobMallocBuffer(&ctxOutData.data, ctxInData.data.size + OUTPUT_DATA_SIZE);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksFinish(&ctxHandle.data, ctxParamSetIn.data, &ctxInData.data, &ctxOutData.data);
    } while (0);
    return GetReturnResult(ret, ctxOutData.data);
}

huks::HuksReturnResult finishSessionSyncWithoutToken(int64_t handle, huks::HuksOptions const &options)
{
    taihe::optional<taihe::array<uint8_t>> opt_token(std::nullopt);
    return finishSessionSync(handle, options, opt_token);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> finishSessionAsyncWithoutToken(
    int64_t handle, ::ohos::security::huks::huks::HuksOptions const &options)
{
    return finishSessionSyncWithoutToken(handle, options);
}

huks::HuksReturnResult finishSessionSyncWithToken(int64_t handle, huks::HuksOptions const &options,
                                                  taihe::array_view<uint8_t> token)
{
    taihe::optional<taihe::array<uint8_t>> opt_token(std::in_place, token);
    return finishSessionSync(handle, options, opt_token);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> finishSessionAsyncWithToken(
    int64_t handle, ::ohos::security::huks::huks::HuksOptions const &options, ::taihe::array_view<uint8_t> token)
{
    return finishSessionSyncWithToken(handle, options, token);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> finishSessionRetpromise(
    int64_t handle, ::ohos::security::huks::huks::HuksOptions const &options,
    ::taihe::optional_view<::taihe::array<uint8_t>> token)
{
    return finishSessionSync(handle, options, token);
}

void abortSessionSync(int64_t handle, huks::HuksOptions const &options)
{
    BlobGuard<0> ctxHandle;
    ParamSetGuard ctxParamSetIn;
    errno_t ret;
    do {
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = BlobFromLong(&ctxHandle.data, handle);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksAbort(&ctxHandle.data, ctxParamSetIn.data);
    } while (0);
    return GetVoid(ret);
}

::taihe::expected<void, ::taihe::error> abortSessionAsync(int64_t handle,
                                                          ::ohos::security::huks::huks::HuksOptions const &options)
{
    abortSessionSync(handle, options);
    return {};
}

::taihe::expected<void, ::taihe::error> abortSessionRetpromise(int64_t handle,
                                                               ::ohos::security::huks::huks::HuksOptions const &options)
{
    abortSessionSync(handle, options);
    return {};
}

huks::HuksReturnResult attestKeyItemSync(taihe::string_view keyAlias, huks::HuksOptions const &options)
{
    BlobGuard<0> ctxKeyAlias;
    ParamSetGuard ctxParamSetIn;
    CertChainGuard ctxCC;
    errno_t ret;
    do {
        ret = BlobFromString(&ctxKeyAlias.data, keyAlias);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksAttestKey(&ctxKeyAlias.data, ctxParamSetIn.data, &ctxCC.data);
    } while (0);
    return GetReturnResult(ret, ctxCC.data);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> attestKeyItemAsync(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    return attestKeyItemSync(keyAlias, options);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> attestKeyItemRetpromise(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    return attestKeyItemSync(keyAlias, options);
}

huks::HuksReturnResult anonAttestKeyItemSync(taihe::string_view keyAlias, huks::HuksOptions const &options)
{
    BlobGuard<0> ctxKeyAlias;
    ParamSetGuard ctxParamSetIn;
    CertChainGuard ctxCC;
    errno_t ret;
    do {
        ret = BlobFromString(&ctxKeyAlias.data, keyAlias);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = PropertiesParse(&ctxParamSetIn.data, options.properties);
        HKS_IF_NOT_SUCC_BREAK(ret, ret);
        ret = HksAnonAttestKey(&ctxKeyAlias.data, ctxParamSetIn.data, &ctxCC.data);
    } while (0);
    return GetReturnResult(ret, ctxCC.data);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> anonAttestKeyItemAsync(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    return anonAttestKeyItemSync(keyAlias, options);
}

::taihe::expected<::ohos::security::huks::huks::HuksReturnResult, ::taihe::error> anonAttestKeyItemRetpromise(
    ::taihe::string_view keyAlias, ::ohos::security::huks::huks::HuksOptions const &options)
{
    return anonAttestKeyItemSync(keyAlias, options);
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_generateKeyItemAsync(generateKeyItemAsync);
TH_EXPORT_CPP_API_generateKeyItemRetpromise(generateKeyItemRetpromise);
TH_EXPORT_CPP_API_deleteKeyItemAsync(deleteKeyItemAsync);
TH_EXPORT_CPP_API_deleteKeyItemRetpromise(deleteKeyItemRetpromise);
TH_EXPORT_CPP_API_importKeyItemAsync(importKeyItemAsync);
TH_EXPORT_CPP_API_importKeyItemRetpromise(importKeyItemRetpromise);
TH_EXPORT_CPP_API_importWrappedKeyItemAsync(importWrappedKeyItemAsync);
TH_EXPORT_CPP_API_importWrappedKeyItemRetpromise(importWrappedKeyItemRetpromise);
TH_EXPORT_CPP_API_exportKeyItemAsync(exportKeyItemAsync);
TH_EXPORT_CPP_API_exportKeyItemRetpromise(exportKeyItemRetpromise);
TH_EXPORT_CPP_API_isKeyItemExistAsync(isKeyItemExistAsync);
TH_EXPORT_CPP_API_isKeyItemExistRetpromise(isKeyItemExistRetpromise);
TH_EXPORT_CPP_API_initSessionAsync(initSessionAsync);
TH_EXPORT_CPP_API_initSessionRetpromise(initSessionRetpromise);
TH_EXPORT_CPP_API_updateSessionAsyncWithoutToken(updateSessionAsyncWithoutToken);
TH_EXPORT_CPP_API_updateSessionAsyncWithToken(updateSessionAsyncWithToken);
TH_EXPORT_CPP_API_updateSessionRetpromise(updateSessionRetpromise);
TH_EXPORT_CPP_API_finishSessionAsyncWithoutToken(finishSessionAsyncWithoutToken);
TH_EXPORT_CPP_API_finishSessionAsyncWithToken(finishSessionAsyncWithToken);
TH_EXPORT_CPP_API_finishSessionRetpromise(finishSessionRetpromise);
TH_EXPORT_CPP_API_abortSessionAsync(abortSessionAsync);
TH_EXPORT_CPP_API_abortSessionRetpromise(abortSessionRetpromise);
TH_EXPORT_CPP_API_attestKeyItemAsync(attestKeyItemAsync);
TH_EXPORT_CPP_API_attestKeyItemRetpromise(attestKeyItemRetpromise);
TH_EXPORT_CPP_API_anonAttestKeyItemAsync(anonAttestKeyItemAsync);
TH_EXPORT_CPP_API_anonAttestKeyItemRetpromise(anonAttestKeyItemRetpromise);
// NOLINTEND
