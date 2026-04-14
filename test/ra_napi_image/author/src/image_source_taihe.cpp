/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
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

#include "image_common.h"
#include "image_dfx.h"
#include "image_log.h"
#include "image_source_taihe.h"
#include "image_taihe_utils.h"
#include "image_trace.h"
#include "image_type.h"
#include "jpeg_decoder_yuv.h"
#include "media_errors.h"
#include "pixel_map_taihe.h"
#include "exif_metadata_formatter.h"

using namespace ANI::Image;
using JpegYuvDecodeError = OHOS::ImagePlugin::JpegYuvDecodeError;

namespace {
constexpr int INVALID_FD = -1;
constexpr uint32_t NUM_0 = 0;
}  // namespace

namespace ANI::Image {
static std::string const FILE_URL_PREFIX = "file://";
thread_local std::string ImageSourceImpl::filePath_ = "";
thread_local int ImageSourceImpl::fileDescriptor_ = -1;
thread_local void *ImageSourceImpl::fileBuffer_ = nullptr;
thread_local size_t ImageSourceImpl::fileBufferSize_ = 0;

static std::mutex imageSourceCrossThreadMutex_;

struct ImageSourceTaiheContext {
    ImageSourceImpl *thisPtr;
    uint32_t status;
    std::string pathName = "";
    int fdIndex = INVALID_FD;
    void *sourceBuffer = nullptr;
    size_t sourceBufferSize = NUM_0;
    std::string keyStr;
    std::string valueStr;
    std::vector<std::string> keyStrArray;
    std::vector<std::pair<std::string, std::string>> kVStrArray;
    std::string defaultValueStr;
    uint32_t index = 0;
    bool isBatch = false;
    OHOS::Media::DecodeOptions decodeOpts;
    std::shared_ptr<OHOS::Media::ImageSource> rImageSource;
    std::shared_ptr<OHOS::Media::PixelMap> rPixelMap;
    std::string errMsg;
    std::multimap<std::int32_t, std::string> errMsgArray;
    std::unique_ptr<std::vector<std::unique_ptr<OHOS::Media::PixelMap>>> pixelMaps;
    std::unique_ptr<std::vector<int32_t>> delayTimes;
};

static std::map<int32_t, Image_ErrorCode> const ERROR_CODE_MAP = {
    {OHOS::Media::ERR_IMAGE_INVALID_PARAMETER, Image_ErrorCode::IMAGE_BAD_PARAMETER},
    {OHOS::Media::COMMON_ERR_INVALID_PARAMETER, Image_ErrorCode::IMAGE_BAD_PARAMETER},
    {JpegYuvDecodeError::JpegYuvDecodeError_InvalidParameter, Image_ErrorCode::IMAGE_BAD_PARAMETER},
    {OHOS::Media::ERR_IMAGE_SOURCE_DATA, Image_ErrorCode::IMAGE_BAD_SOURCE},
    {OHOS::Media::ERR_IMAGE_SOURCE_DATA_INCOMPLETE, Image_ErrorCode::IMAGE_BAD_SOURCE},
    {OHOS::Media::ERR_IMAGE_GET_DATA_ABNORMAL, Image_ErrorCode::IMAGE_BAD_SOURCE},
    {OHOS::Media::ERR_IMAGE_DATA_ABNORMAL, Image_ErrorCode::IMAGE_BAD_SOURCE},
    {OHOS::Media::ERROR, Image_ErrorCode::IMAGE_BAD_SOURCE},
    {JpegYuvDecodeError::JpegYuvDecodeError_BadImage, Image_ErrorCode::IMAGE_BAD_SOURCE},
    {OHOS::Media::ERR_IMAGE_MISMATCHED_FORMAT, Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_MIMETYPE},
    {OHOS::Media::ERR_IMAGE_UNKNOWN_FORMAT, Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_MIMETYPE},
    {OHOS::Media::ERR_IMAGE_DECODE_HEAD_ABNORMAL, Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_MIMETYPE},
    {OHOS::Media::ERR_IMAGE_TOO_LARGE, Image_ErrorCode::IMAGE_SOURCE_TOO_LARGE},
    {OHOS::Media::ERR_MEDIA_INVALID_OPERATION, Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_ALLOCATOR_TYPE},
    {OHOS::Media::IMAGE_RESULT_FORMAT_CONVERT_FAILED, Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_OPTIONS},
    {OHOS::Media::ERR_MEDIA_FORMAT_UNSUPPORT, Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_OPTIONS},
    {OHOS::Media::ERR_IMAGE_PIXELMAP_CREATE_FAILED, Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_OPTIONS},
    {JpegYuvDecodeError::JpegYuvDecodeError_ConvertError, Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_OPTIONS},
    {OHOS::Media::ERR_IMAGE_CROP, Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_OPTIONS},
    {OHOS::Media::ERR_IMAGE_DECODE_FAILED, Image_ErrorCode::IMAGE_DECODE_FAILED},
    {OHOS::Media::ERR_IMAGE_DECODE_ABNORMAL, Image_ErrorCode::IMAGE_DECODE_FAILED},
    {OHOS::Media::ERR_IMAGE_PLUGIN_CREATE_FAILED, Image_ErrorCode::IMAGE_DECODE_FAILED},
    {JpegYuvDecodeError::JpegYuvDecodeError_DecodeFailed, Image_ErrorCode::IMAGE_DECODE_FAILED},
    {JpegYuvDecodeError::JpegYuvDecodeError_MemoryNotEnoughToSaveResult, Image_ErrorCode::IMAGE_DECODE_FAILED},
    {OHOS::Media::ERR_IMAGE_MALLOC_ABNORMAL, Image_ErrorCode::IMAGE_SOURCE_ALLOC_FAILED},
    {OHOS::Media::ERR_IMAGE_DATA_UNSUPPORT, Image_ErrorCode::IMAGE_SOURCE_ALLOC_FAILED},
    {OHOS::Media::ERR_DMA_NOT_EXIST, Image_ErrorCode::IMAGE_SOURCE_ALLOC_FAILED},
    {OHOS::Media::ERR_DMA_DATA_ABNORMAL, Image_ErrorCode::IMAGE_SOURCE_ALLOC_FAILED},
    {OHOS::Media::ERR_SHAMEM_DATA_ABNORMAL, Image_ErrorCode::IMAGE_SOURCE_ALLOC_FAILED}};

static std::map<Image_ErrorCode, std::string> const ERROR_CODE_MESSAGE_MAP = {
    {Image_ErrorCode::IMAGE_BAD_PARAMETER,
     "Parameter error. Possible causes:"
     "1.Mandatory parameters are left unspecified. 2.Incorrect parameter types. 3.Parameter verification failed."},
    {Image_ErrorCode::IMAGE_BAD_SOURCE,
     "Bad source. e.g.,1.Image has invalid width or height."
     "2.Image source incomplete. 3.Read image data failed. 4. Codec create failed."
     "5.The sourceOption specifies an odd width, causing the YUV420 PixelMap conversion to RGBA failed."},
    {Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_MIMETYPE, "Unsupported mimetype."},
    {Image_ErrorCode::IMAGE_SOURCE_TOO_LARGE, "Image too large."},
    {Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_ALLOCATOR_TYPE,
     "Unsupported allocator type. e.g.,"
     "use share memory to decode a HDR image as only DMA supported hdr metadata."},
    {Image_ErrorCode::IMAGE_SOURCE_UNSUPPORTED_OPTIONS,
     "Unsupported options. e.g.,"
     "1.Convert image into desired pixelFormat failed. 2.Crop pixelMap failed."},
    {Image_ErrorCode::IMAGE_DECODE_FAILED, "Decode failed. e.g.,Decode image header failed."},
    {Image_ErrorCode::IMAGE_SOURCE_ALLOC_FAILED, "Memory allocation failed."}};

static Image_ErrorCode ConvertToErrorCode(int32_t errorCode)
{
    Image_ErrorCode apiErrorCode = Image_ErrorCode::IMAGE_DECODE_FAILED;
    auto iter = ERROR_CODE_MAP.find(errorCode);
    if (iter != ERROR_CODE_MAP.end()) {
        apiErrorCode = iter->second;
    }
    return apiErrorCode;
}

static std::string GetErrorCodeMsg(Image_ErrorCode apiErrorCode)
{
    std::string errMsg = "Decode failed.";
    auto iter = ERROR_CODE_MESSAGE_MAP.find(apiErrorCode);
    if (iter != ERROR_CODE_MESSAGE_MAP.end()) {
        errMsg = iter->second;
    }
    return errMsg;
}

ImageSourceImpl::ImageSourceImpl()
{
}

ImageSourceImpl::ImageSourceImpl(std::shared_ptr<OHOS::Media::ImageSource> imageSource)
{
    nativeImgSrc = imageSource;
}

ImageSourceImpl::~ImageSourceImpl()
{
    ReleaseSync();
}

int64_t ImageSourceImpl::GetImplPtr()
{
    return reinterpret_cast<uintptr_t>(this);
}

ImageInfo ImageSourceImpl::GetImageInfoSync(uint32_t index)
{
    OHOS::Media::ImageInfo imageinfo;
    bool isHdr = false;
    if (nativeImgSrc != nullptr) {
        index = index >= NUM_0 ? index : NUM_0;
        nativeImgSrc->GetImageInfo(index, imageinfo);
        isHdr = nativeImgSrc->IsHdrImage();
    } else {
        ImageTaiheUtils::ThrowExceptionError("nativeImgSrc is nullptr");
    }
    return ImageTaiheUtils::ToTaiheImageInfo(imageinfo, isHdr);
}

ImageInfo ImageSourceImpl::GetImageInfoRetPromise(uint32_t index)
{
    return GetImageInfoSync(index);
}

ImageInfo ImageSourceImpl::GetImageInfoWithAsync(uint32_t index)
{
    return GetImageInfoSync(index);
}

static bool ParseRotate(DecodingOptions const &options, OHOS::Media::DecodeOptions &dst, std::string &errMsg)
{
    if (options.rotate.has_value()) {
        dst.rotateNewDegrees = options.rotate.value();
        if (dst.rotateNewDegrees >= 0 && dst.rotateNewDegrees <= 360) {  // 360 is the maximum rotation angle.
            dst.rotateDegrees = static_cast<float>(dst.rotateNewDegrees);
            IMAGE_LOGD("rotateDegrees: %{public}f", dst.rotateDegrees);
        } else {
            IMAGE_LOGD("Invalid rotate %{public}d", dst.rotateNewDegrees);
            errMsg = "DecodeOptions mismatch";
            return false;
        }
    }
    return true;
}

static OHOS::Media::Rect ParseDesiredRegion(DecodingOptions const &options)
{
    OHOS::Media::Rect rect {};
    if (options.desiredRegion.has_value()) {
        auto &region = options.desiredRegion.value();
        rect.left = region.x;
        rect.top = region.y;
        rect.width = region.size.width;
        rect.height = region.size.height;
        IMAGE_LOGD("desiredRegion: %{public}d, %{public}d, %{public}d, %{public}d", rect.left, rect.top, rect.width,
                   rect.height);
    }
    return rect;
}

static bool IsAstc(int32_t val)
{
    if (val >= static_cast<int32_t>(OHOS::Media::PixelFormat::ASTC_4x4) &&
        val <= static_cast<int32_t>(OHOS::Media::PixelFormat::ASTC_8x8)) {
        return true;
    }
    return false;
}

static bool IsSupportPixelFormat(int32_t val)
{
    if (IsAstc(val)) {
        return true;
    }
    if (val >= static_cast<int32_t>(OHOS::Media::PixelFormat::UNKNOWN) &&
        val < static_cast<int32_t>(OHOS::Media::PixelFormat::EXTERNAL_MAX)) {
        return true;
    }

    return false;
}

static OHOS::Media::PixelFormat ParsePixelFormat(int32_t val)
{
    if (IsAstc(val)) {
        return OHOS::Media::PixelFormat(val);
    }
    if (val < static_cast<int32_t>(OHOS::Media::PixelFormat::EXTERNAL_MAX)) {
        return OHOS::Media::PixelFormat(val);
    }

    return OHOS::Media::PixelFormat::UNKNOWN;
}

static bool ParsePixelFormat(optional<PixelMapFormat> val, OHOS::Media::PixelFormat &dst, std::string const &name,
                             std::string &errMsg)
{
    if (!val.has_value()) {
        IMAGE_LOGD("no %{public}s", name.c_str());
    } else {
        int32_t pixelFormat = val->get_value();
        if (IsSupportPixelFormat(pixelFormat)) {
            dst = ParsePixelFormat(pixelFormat);
            IMAGE_LOGD("PixelFormat: %{public}d", dst);
        } else {
            IMAGE_LOGD("Invalid %{public}s %{public}d", name.c_str(), pixelFormat);
            errMsg = "DecodeOptions mismatch";
            return false;
        }
    }
    return true;
}

static void ParseDesiredColorSpace(DecodingOptions const &options, OHOS::Media::DecodeOptions &dst)
{
    if (options.desiredColorSpace.has_value()) {
        IMAGE_LOGD("desiredColorSpace parse finished");
        return;
    }
}

static OHOS::Media::DecodeDynamicRange ParseDynamicRange(DecodingOptions const &options)
{
    if (options.desiredDynamicRange.has_value()) {
        int32_t desiredDynamicRange = options.desiredDynamicRange->get_value();
        if (desiredDynamicRange <= static_cast<int32_t>(OHOS::Media::DecodeDynamicRange::HDR)) {
            IMAGE_LOGD("desiredDynamicRange: %{public}d", desiredDynamicRange);
            return OHOS::Media::DecodeDynamicRange(desiredDynamicRange);
        }
    }
    return OHOS::Media::DecodeDynamicRange::SDR;
}

static OHOS::Media::ResolutionQuality ParseResolutionQuality(DecodingOptions const &options)
{
    if (options.resolutionQuality.has_value()) {
        int32_t resolutionQuality = options.resolutionQuality->get_value();
        if (resolutionQuality <= static_cast<int32_t>(OHOS::Media::ResolutionQuality::HIGH) &&
            (resolutionQuality >= static_cast<int32_t>(OHOS::Media::ResolutionQuality::UNKNOWN))) {
            IMAGE_LOGD("resolutionQuality: %{public}d", resolutionQuality);
            return OHOS::Media::ResolutionQuality(resolutionQuality);
        }
    }
    return OHOS::Media::ResolutionQuality::UNKNOWN;
}

static inline bool IsCropStrategyVaild(int32_t strategy)
{
    return strategy >= static_cast<int32_t>(OHOS::Media::CropAndScaleStrategy::SCALE_FIRST) &&
           strategy <= static_cast<int32_t>(OHOS::Media::CropAndScaleStrategy::CROP_FIRST);
}

static void ParseCropAndScaleStrategy(DecodingOptions const &options, OHOS::Media::DecodeOptions &dst)
{
    if (options.cropAndScaleStrategy.has_value() && IsCropStrategyVaild(options.cropAndScaleStrategy->get_value())) {
        IMAGE_LOGI("The strategy has taken effect");
        dst.cropAndScaleStrategy = OHOS::Media::CropAndScaleStrategy(options.cropAndScaleStrategy->get_value());
        IMAGE_LOGD("cropAndScaleStrategy: %{public}d", dst.cropAndScaleStrategy);
        return;
    }
    IMAGE_LOGI("default cropAndScaleStrategy");
}

static void ParseReusePixelMap(DecodingOptions const &options, OHOS::Media::DecodeOptions &dst)
{
    if (options.reusePixelmap.has_value()) {
        PixelMap etsPixelMap = options.reusePixelmap.value();
        std::shared_ptr<OHOS::Media::PixelMap> rPixelMap = PixelMapImpl::GetPixelMap(etsPixelMap);
        if (rPixelMap != nullptr) {
            dst.reusePixelmap = rPixelMap;
            IMAGE_LOGD("reusePixelmap parse finished");
        }
    }
}

static bool ParseDecodeOptions2(DecodingOptions const &options, OHOS::Media::DecodeOptions &dst, std::string &errMsg)
{
    if (!ParsePixelFormat(options.desiredPixelFormat, dst.desiredPixelFormat, "desiredPixelFormat", errMsg) ||
        !ParsePixelFormat(options.photoDesiredPixelFormat, dst.photoDesiredPixelFormat, "photoDesiredPixelFormat",
                          errMsg)) {
        return false;
    }

    if (options.fitDensity.has_value()) {
        dst.fitDensity = options.fitDensity.value();
        IMAGE_LOGD("fitDensity: %{public}d", dst.fitDensity);
    }

    if (options.fillColor.has_value()) {
        dst.SVGOpts.fillColor.isValidColor = true;
        dst.SVGOpts.fillColor.color = options.fillColor.value();
        IMAGE_LOGD("fillColor: %{public}d", dst.SVGOpts.fillColor.color);
    }

    if (options.SVGResize.has_value()) {
        dst.SVGOpts.SVGResize.isValidPercentage = true;
        dst.SVGOpts.SVGResize.resizePercentage = options.SVGResize.value();
        IMAGE_LOGD("SVGResize: %{public}d", dst.SVGOpts.SVGResize.resizePercentage);
    }

    ParseDesiredColorSpace(options, dst);
    if (dst.desiredColorSpaceInfo == nullptr) {
        IMAGE_LOGD("no desiredColorSpace");
    }

    dst.desiredDynamicRange = ParseDynamicRange(options);
    dst.resolutionQuality = ParseResolutionQuality(options);
    ParseCropAndScaleStrategy(options, dst);
    ParseReusePixelMap(options, dst);
    return true;
}

static bool ParseDecodeOptions(DecodingOptions const &options, OHOS::Media::DecodeOptions &dst, uint32_t &index,
                               std::string &errMsg)
{
    if (options.index.has_value()) {
        index = options.index.value();
        IMAGE_LOGD("index: %{public}d", index);
    }

    if (options.sampleSize.has_value()) {
        dst.sampleSize = options.sampleSize.value();
        IMAGE_LOGD("sampleSize: %{public}d", dst.sampleSize);
    }

    CHECK_ERROR_RETURN_RET_LOG(!ParseRotate(options, dst, errMsg), false, "%{public}s ParseRotate failed", __func__);

    if (options.editable.has_value()) {
        dst.editable = options.editable.value();
        IMAGE_LOGD("editable: %{public}d", dst.editable);
    }

    if (options.desiredSize.has_value()) {
        dst.desiredSize.width = options.desiredSize.value().width;
        dst.desiredSize.height = options.desiredSize.value().height;
        IMAGE_LOGD("desiredSize: %{public}d, %{public}d", dst.desiredSize.width, dst.desiredSize.height);
    }

    dst.desiredRegion = ParseDesiredRegion(options);
    return ParseDecodeOptions2(options, dst, errMsg);
}

static std::shared_ptr<OHOS::Media::PixelMap> CreatePixelMapInner(ImageSourceImpl *const thisPtr,
                                                                  std::shared_ptr<OHOS::Media::ImageSource> imageSource,
                                                                  uint32_t index, OHOS::Media::DecodeOptions decodeOpts,
                                                                  uint32_t &status)
{
    if (thisPtr == nullptr || imageSource == nullptr) {
        IMAGE_LOGE("Invailed args");
        status = OHOS::Media::ERROR;
    }

    std::shared_ptr<OHOS::Media::PixelMap> pixelMap;
    auto incPixelMap = (thisPtr == nullptr) ? nullptr : thisPtr->GetIncrementalPixelMap();
    if (incPixelMap != nullptr) {
        IMAGE_LOGD("Get Incremental PixelMap!!!");
        pixelMap = incPixelMap;
    } else {
        decodeOpts.invokeType = OHOS::Media::JS_INTERFACE;
        pixelMap = (imageSource == nullptr)
                       ? nullptr
                       : imageSource->CreatePixelMapEx((index >= NUM_0) ? index : NUM_0, decodeOpts, status);
    }

    if (status != OHOS::Media::SUCCESS || pixelMap == nullptr) {
        IMAGE_LOGE("Create PixelMap error");
    }

    return pixelMap;
}

static void CreatePixelMapExecute(std::unique_ptr<ImageSourceTaiheContext> &taiheContext)
{
    IMAGE_LOGD("CreatePixelMapExecute IN");
    if (taiheContext == nullptr) {
        IMAGE_LOGE("%{public}s taiheContext is nullptr", __func__);
        return;
    }

    if (taiheContext->errMsg.size() > 0) {
        IMAGE_LOGE("%{public}s errMsg: %{public}s", __func__, taiheContext->errMsg.c_str());
        return;
    }

    taiheContext->rPixelMap = CreatePixelMapInner(taiheContext->thisPtr, taiheContext->rImageSource,
                                                  taiheContext->index, taiheContext->decodeOpts, taiheContext->status);

    if (taiheContext->status != OHOS::Media::SUCCESS) {
        taiheContext->errMsg = "Create PixelMap error";
        IMAGE_LOGE("Create PixelMap error");
    }
    IMAGE_LOGD("CreatePixelMapExecute OUT");
}

static PixelMap CreatePixelMapComplete(std::unique_ptr<ImageSourceTaiheContext> &taiheContext)
{
    IMAGE_LOGD("CreatePixelMapComplete IN");
    if (taiheContext->status == OHOS::Media::SUCCESS && taiheContext->rPixelMap != nullptr) {
        return make_holder<PixelMapImpl, PixelMap>(taiheContext->rPixelMap);
    }
    IMAGE_LOGD("CreatePixelMapComplete OUT");
    ImageTaiheUtils::ThrowExceptionError(taiheContext->errMsg);
    return make_holder<PixelMapImpl, PixelMap>();
}

PixelMap ImageSourceImpl::CreatePixelMapSync(DecodingOptions const &options)
{
    std::unique_ptr<ImageSourceTaiheContext> taiheContext = std::make_unique<ImageSourceTaiheContext>();
    taiheContext->rImageSource = nativeImgSrc;
    if (taiheContext->rImageSource == nullptr) {
        IMAGE_LOGE("%{public}s nativeImgSrc is nullptr", __func__);
        ImageTaiheUtils::ThrowExceptionError(IMAGE_BAD_PARAMETER, "nativeImgSrc is nullptr");
        return make_holder<PixelMapImpl, PixelMap>();
    }

    taiheContext->thisPtr = this;
    if (taiheContext->thisPtr == nullptr) {
        IMAGE_LOGE("%{public}s thisPtr is nullptr", __func__);
        ImageTaiheUtils::ThrowExceptionError(IMAGE_BAD_PARAMETER, "thisPtr is nullptr");
        return make_holder<PixelMapImpl, PixelMap>();
    }

    if (!ParseDecodeOptions(options, taiheContext->decodeOpts, taiheContext->index, taiheContext->errMsg)) {
        IMAGE_LOGE("%{public}s ParseDecodeOptions failed", __func__);
    }

    ImageTaiheUtils::HicheckerReport();
    CreatePixelMapExecute(taiheContext);
    return CreatePixelMapComplete(taiheContext);
}

PixelMap ImageSourceImpl::CreatePixelMapRetPromise(DecodingOptions const &options)
{
    return CreatePixelMapSync(options);
}

PixelMap ImageSourceImpl::CreatePixelMapWithAsync(DecodingOptions const &options)
{
    return CreatePixelMapSync(options);
}

static void CreatePixelMapUsingAllocatorSyncExecute(std::unique_ptr<ImageSourceTaiheContext> &taiheContext)
{
    if (taiheContext == nullptr) {
        IMAGE_LOGE("%{public}s taiheContext is nullptr", __func__);
        return;
    }

    taiheContext->rPixelMap = CreatePixelMapInner(taiheContext->thisPtr, taiheContext->rImageSource,
                                                  taiheContext->index, taiheContext->decodeOpts, taiheContext->status);
    if (taiheContext->status != OHOS::Media::SUCCESS) {
        Image_ErrorCode apiErrorCode = ConvertToErrorCode(taiheContext->status);
        std::string apiErrorMsg = GetErrorCodeMsg(apiErrorCode);
        taiheContext->errMsgArray.emplace(apiErrorCode, apiErrorMsg);
    }
}

static PixelMap CreatePixelMapUsingAllocatorSyncComplete(std::unique_ptr<ImageSourceTaiheContext> &taiheContext)
{
    if (taiheContext->status == OHOS::Media::SUCCESS && taiheContext->rPixelMap != nullptr) {
        return make_holder<PixelMapImpl, PixelMap>(taiheContext->rPixelMap);
    }
    for (auto const &[errorCode, errMsg] : taiheContext->errMsgArray) {
        ImageTaiheUtils::ThrowExceptionError(errorCode, errMsg);
    }
    return make_holder<PixelMapImpl, PixelMap>();
}

static bool CheckAsyncContext(std::unique_ptr<ImageSourceTaiheContext> &taiheContext, bool check)
{
    if (taiheContext == nullptr) {
        IMAGE_LOGE("context is nullptr");
        return false;
    }

    if (check) {
        if (taiheContext->errMsg.size() > 0) {
            IMAGE_LOGE("mismatch args");
            taiheContext->status = OHOS::Media::ERROR;
            return false;
        }

        if (taiheContext->rImageSource == nullptr) {
            IMAGE_LOGE("empty context rImageSource");
            taiheContext->status = OHOS::Media::ERROR;
            return false;
        }
    }

    return true;
}

static void GenerateErrMsg(std::unique_ptr<ImageSourceTaiheContext> &context, std::string &errMsg)
{
    if (context == nullptr) {
        return;
    }
    switch (context->status) {
        case OHOS::Media::ERR_IMAGE_DECODE_EXIF_UNSUPPORT:
            errMsg = "The image does not support EXIF decoding.";
            break;
        case OHOS::Media::ERROR:
            errMsg = "The operation failed.";
            break;
        case OHOS::Media::ERR_IMAGE_DATA_UNSUPPORT:
            errMsg = "The image data is not supported.";
            break;
        case OHOS::Media::ERR_IMAGE_SOURCE_DATA:
            errMsg = "The image source data is incorrect.";
            break;
        case OHOS::Media::ERR_IMAGE_SOURCE_DATA_INCOMPLETE:
            errMsg = "The image source data is incomplete.";
            break;
        case OHOS::Media::ERR_IMAGE_MISMATCHED_FORMAT:
            errMsg = "The image format does not mastch.";
            break;
        case OHOS::Media::ERR_IMAGE_UNKNOWN_FORMAT:
            errMsg = "Unknown image format.";
            break;
        case OHOS::Media::ERR_IMAGE_INVALID_PARAMETER:
            errMsg = "Invalid image parameter.";
            break;
        case OHOS::Media::ERR_IMAGE_DECODE_FAILED:
            errMsg = "Failed to decode the image.";
            break;
        case OHOS::Media::ERR_IMAGE_PLUGIN_CREATE_FAILED:
            errMsg = "Failed to create the image plugin.";
            break;
        case OHOS::Media::ERR_IMAGE_DECODE_HEAD_ABNORMAL:
            errMsg = "Failed to decode the image header.";
            break;
        case OHOS::Media::ERR_MEDIA_VALUE_INVALID:
            errMsg = "The EXIF value is invalid.";
            break;
        default:
            errMsg = "There is unknown error happened.";
    }
}

static void GetImagePropertiesExecute(std::unique_ptr<ImageSourceTaiheContext> &context)
{
    if (context == nullptr) {
        IMAGE_LOGE("empty context");
        return;
    }
    uint32_t status = OHOS::Media::SUCCESS;
    for (auto keyStrIt = context->keyStrArray.begin(); keyStrIt != context->keyStrArray.end(); ++keyStrIt) {
        std::string valueStr = "";
        status = context->rImageSource->GetImagePropertyString(0, *keyStrIt, valueStr);
        if (status == OHOS::Media::SUCCESS) {
            context->kVStrArray.emplace_back(std::make_pair(*keyStrIt, valueStr));
        } else {
            context->kVStrArray.emplace_back(std::make_pair(*keyStrIt, ""));
            context->errMsgArray.insert(std::make_pair(status, *keyStrIt));
            IMAGE_LOGE("errCode: %{public}u , exif key: %{public}s", status, keyStrIt->c_str());
        }
    }
    context->status =
        context->kVStrArray.size() == context->errMsgArray.size() ? OHOS::Media::ERROR : OHOS::Media::SUCCESS;
}

static PropertyValue CreatePropertyValue(std::string const &valueStr)
{
    if (!valueStr.empty()) {
        return PropertyValue::make_type_string(valueStr);
    } else {
        return PropertyValue::make_type_null();
    }
}

map<PropertyKey, PropertyValue> CreatePropertiesRecord(
    std::vector<std::pair<std::string, std::string>> recordParameters)
{
    map<PropertyKey, PropertyValue> result;
    for (size_t index = 0; index < recordParameters.size(); ++index) {
        PropertyKey::key_t key;
        if (!ImageTaiheUtils::GetEnumKeyByValue<PropertyKey>(recordParameters[index].first, key)) {
            IMAGE_LOGE("Get current record parameter failed");
            continue;
        }
        PropertyValue value = CreatePropertyValue(recordParameters[index].second);
        result.emplace(PropertyKey(key), value);
    }

    IMAGE_LOGD("Get record parameters info success.");
    return result;
}

void CreateObtainErrorArray(std::multimap<std::int32_t, std::string> errMsgArray)
{
    for (auto it = errMsgArray.begin(); it != errMsgArray.end(); ++it) {
        std::string errMsg;
        int32_t errCode = it->first;
        if (errCode == OHOS::Media::ERR_IMAGE_DECODE_ABNORMAL) {
            errMsg = "The image source data is incorrect! exif key: " + it->second;
        } else if (errCode == OHOS::Media::ERR_IMAGE_UNKNOWN_FORMAT) {
            errMsg = "Unknown image format! exif key: " + it->second;
        } else if (errCode == OHOS::Media::ERR_IMAGE_DECODE_FAILED) {
            errMsg = "Failed to decode the image! exif key: " + it->second;
        } else {
            errCode = OHOS::Media::ERROR;
            errMsg = "There is generic taihe failure! exif key: " + it->second;
        }
        ImageTaiheUtils::ThrowExceptionError(errCode, errMsg);
    }

    IMAGE_LOGD("Create obtain error array success.");
}

std::vector<std::string> GetStringArrayArgument(array_view<PropertyKey> key)
{
    std::vector<std::string> keyStrArray;

    for (uint32_t i = 0; i < key.size(); i++) {
        keyStrArray.emplace_back(key[i].get_value());
    }

    IMAGE_LOGD("Get string argument success.");
    return keyStrArray;
}

map<PropertyKey, PropertyValue> ImageSourceImpl::GetImagePropertiesRetPromise(array_view<PropertyKey> key)
{
    OHOS::Media::ImageTrace imageTrace("ImageSourceImpl::GetImagePropertiesSync");

    map<PropertyKey, PropertyValue> result;
    std::unique_ptr<ImageSourceTaiheContext> context = std::make_unique<ImageSourceTaiheContext>();
    if (nativeImgSrc == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(OHOS::Media::COMMON_ERR_INVALID_PARAMETER, "empty native rImageSource");
        return result;
    }
    context->rImageSource = nativeImgSrc;
    context->keyStrArray = GetStringArrayArgument(key);
    if (context->keyStrArray.size() == 0) return result;

    GetImagePropertiesExecute(context);

    if (context->status == OHOS::Media::SUCCESS) {
        result = CreatePropertiesRecord(context->kVStrArray);
    } else {
        CreateObtainErrorArray(context->errMsgArray);
    }
    return result;
}

void CreateModifyErrorArray(std::multimap<std::int32_t, std::string> errMsgArray)
{
    for (auto it = errMsgArray.begin(); it != errMsgArray.end(); ++it) {
        if (it->first == OHOS::Media::ERR_MEDIA_WRITE_PARCEL_FAIL) {
            ImageTaiheUtils::ThrowExceptionError(it->first,
                                                 "Create Fd without write permission! exif key: " + it->second);
        } else if (it->first == OHOS::Media::ERR_MEDIA_OUT_OF_RANGE) {
            ImageTaiheUtils::ThrowExceptionError(
                it->first, "The given buffer size is too small to add new exif data! exif key: " + it->second);
        } else if (it->first == OHOS::Media::ERR_IMAGE_DECODE_EXIF_UNSUPPORT) {
            ImageTaiheUtils::ThrowExceptionError(it->first,
                                                 "The image does not support EXIF decoding. exif key: " + it->second);
        } else if (it->first == OHOS::Media::ERR_MEDIA_VALUE_INVALID) {
            ImageTaiheUtils::ThrowExceptionError(it->first, it->second);
        } else {
            ImageTaiheUtils::ThrowExceptionError(OHOS::Media::ERROR,
                                                 "There is generic taihe failure! exif key: " + it->second);
        }
    }

    IMAGE_LOGD("Create modify error array success.");
}

static void ModifyImagePropertyComplete(std::unique_ptr<ImageSourceTaiheContext> &context)
{
    if (context == nullptr) {
        IMAGE_LOGE("context is nullptr");
        return;
    }

    if (context->status == OHOS::Media::SUCCESS) {
        IMAGE_LOGI("ModifyImageProperty success.");
        return;
    }

    if (context->isBatch) {
        CreateModifyErrorArray(context->errMsgArray);
    } else {
        if (context->status == OHOS::Media::ERR_MEDIA_WRITE_PARCEL_FAIL) {
            if (context->fdIndex != INVALID_FD) {
                ImageTaiheUtils::ThrowExceptionError(context->status, "Create Fd without write permission!");
            } else {
                ImageTaiheUtils::ThrowExceptionError(context->status,
                                                     "The EXIF data failed to be written to the file.");
            }
        } else if (context->status == OHOS::Media::ERR_MEDIA_OUT_OF_RANGE) {
            ImageTaiheUtils::ThrowExceptionError(context->status,
                                                 "The given buffer size is too small to add new exif data!");
        } else if (context->status == OHOS::Media::ERR_IMAGE_DECODE_EXIF_UNSUPPORT) {
            ImageTaiheUtils::ThrowExceptionError(context->status,
                                                 "The exif data format is not standard, so modify it failed!");
        } else if (context->status == OHOS::Media::ERR_MEDIA_VALUE_INVALID) {
            ImageTaiheUtils::ThrowExceptionError(context->status, context->errMsg);
        } else {
            ImageTaiheUtils::ThrowExceptionError(context->status, "There is generic taihe failure!");
        }
    }
}

static uint32_t CheckExifDataValue(std::string const &key, std::string const &value, std::string &errorInfo)
{
    auto status = static_cast<uint32_t>(OHOS::Media::ExifMetadatFormatter::Validate(key, value));
    if (status != OHOS::Media::SUCCESS) {
        errorInfo = key + " has invalid exif value: ";
        errorInfo.append(value);
    }
    return status;
}

static void ModifyImagePropertyExecute(std::unique_ptr<ImageSourceTaiheContext> &context)
{
    if (context == nullptr) {
        IMAGE_LOGE("empty context");
        return;
    }
    IMAGE_LOGD("ModifyImagePropertyExecute CheckExifDataValue");
    uint32_t status = CheckExifDataValue(context->keyStr, context->valueStr, context->errMsg);
    IMAGE_LOGD("ModifyImagePropertyExecute Check ret status: %{public}d", status);
    if (status != OHOS::Media::SUCCESS) {
        IMAGE_LOGE("There is invalid exif data parameter");
        context->status = status;
        return;
    }
    context->status = context->rImageSource->ModifyImagePropertyEx(context->index, context->keyStr, context->valueStr);
}

void ImageSourceImpl::ModifyImagePropertyRetPromise(PropertyKey key, string_view value)
{
    OHOS::Media::ImageTrace imageTrace("ImageSourceImpl::ModifyImagePropertySync");

    std::unique_ptr<ImageSourceTaiheContext> context = std::make_unique<ImageSourceTaiheContext>();
    if (nativeImgSrc == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(OHOS::Media::COMMON_ERR_INVALID_PARAMETER, "empty native rImageSource");
        return;
    }
    context->rImageSource = nativeImgSrc;

    context->keyStr = std::string(key.get_value());
    context->valueStr = std::string(value);

    context->pathName = ImageSourceImpl::filePath_;
    context->fdIndex = ImageSourceImpl::fileDescriptor_;
    context->sourceBuffer = ImageSourceImpl::fileBuffer_;
    context->sourceBufferSize = ImageSourceImpl::fileBufferSize_;

    ModifyImagePropertyExecute(context);
    ModifyImagePropertyComplete(context);
}

void ImageSourceImpl::ModifyImagePropertyWithAsync(PropertyKey key, string_view value)
{
    return ModifyImagePropertyRetPromise(key, value);
}

static void ModifyImagePropertiesExecute(std::unique_ptr<ImageSourceTaiheContext> &context)
{
    if (context == nullptr) {
        IMAGE_LOGE("empty context");
        return;
    }
    uint32_t status = OHOS::Media::SUCCESS;
    for (auto recordIterator = context->kVStrArray.begin(); recordIterator != context->kVStrArray.end();
         ++recordIterator) {
        IMAGE_LOGD("CheckExifDataValue");
        status = CheckExifDataValue(recordIterator->first, recordIterator->second, context->errMsg);
        IMAGE_LOGD("Check ret status: %{public}d", status);
        if (status != OHOS::Media::SUCCESS) {
            IMAGE_LOGE("There is invalid exif data parameter");
            context->errMsgArray.insert(std::make_pair(status, context->errMsg));
            continue;
        }
        status = context->rImageSource->ModifyImagePropertyEx(0, recordIterator->first, recordIterator->second);
        if (status != OHOS::Media::SUCCESS) {
            context->errMsgArray.insert(std::make_pair(status, recordIterator->first));
        }
    }
    context->status = context->errMsgArray.size() > 0 ? OHOS::Media::ERROR : OHOS::Media::SUCCESS;
}

std::vector<std::pair<std::string, std::string>> GetRecordArgument(map_view<PropertyKey, PropertyValue> records)
{
    std::vector<std::pair<std::string, std::string>> kVStrArray;

    for (auto const &[key, value] : records) {
        std::string valueStr;
        if (value.holds_type_string()) {
            valueStr = std::string(value.get_type_string_ref());
        } else if (value.holds_type_null()) {
            valueStr = "";
        }
        kVStrArray.push_back(std::make_pair(std::string(key.get_value()), valueStr));
    }

    IMAGE_LOGD("Get record argument success.");
    return kVStrArray;
}

void ImageSourceImpl::ModifyImagePropertiesRetPromise(map_view<PropertyKey, PropertyValue> records)
{
    OHOS::Media::ImageTrace imageTrace("ImageSourceImpl::ModifyImagePropertiesSync");

    std::unique_ptr<ImageSourceTaiheContext> context = std::make_unique<ImageSourceTaiheContext>();
    if (nativeImgSrc == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(OHOS::Media::COMMON_ERR_INVALID_PARAMETER, "empty native rImageSource");
        return;
    }
    context->rImageSource = nativeImgSrc;

    context->kVStrArray = GetRecordArgument(records);
    if (context->kVStrArray.size() == 0) return;
    context->isBatch = true;

    context->pathName = ImageSourceImpl::filePath_;
    context->fdIndex = ImageSourceImpl::fileDescriptor_;
    context->sourceBuffer = ImageSourceImpl::fileBuffer_;
    context->sourceBufferSize = ImageSourceImpl::fileBufferSize_;

    ModifyImagePropertiesExecute(context);
    ModifyImagePropertyComplete(context);
}

void ImageSourceImpl::ReleaseSync()
{
    if (!isRelease) {
        if (nativeImgSrc != nullptr) {
            nativeImgSrc = nullptr;
        }
        isRelease = true;
    }
}

void ImageSourceImpl::ReleaseRetPromise()
{
    ReleaseSync();
}

void ImageSourceImpl::ReleaseWithAsync()
{
    ReleaseSync();
}
}  // namespace ANI::Image

// NOLINTEND
