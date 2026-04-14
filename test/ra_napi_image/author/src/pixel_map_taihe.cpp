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

#include "image_log.h"
#include "image_taihe_utils.h"
#include "media_errors.h"
#include "pixel_map_taihe.h"
#include <regex>
#include "pixel_map_from_surface.h"
#include "sync_fence.h"
#include "transaction/rs_interfaces.h"

namespace ANI::Image {
PixelMapImpl::PixelMapImpl()
{
}

PixelMapImpl::PixelMapImpl(array_view<uint8_t> const &colors, InitializationOptions const &etsOptions)
{
    Media::InitializationOptions options;
    ParseInitializationOptions(etsOptions, options);
    if (!Is10BitFormat(options.pixelFormat)) {
        nativePixelMap_ = Media::PixelMap::Create(reinterpret_cast<uint32_t *>(colors.data()),
                                                  colors.size() / sizeof(uint32_t), options);
    }
    if (nativePixelMap_ == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(Media::COMMON_ERR_INVALID_PARAMETER,
                                             "Create PixelMap by buffer and options failed");
    }
}

PixelMapImpl::PixelMapImpl(InitializationOptions const &etsOptions)
{
    Media::InitializationOptions options;
    ParseInitializationOptions(etsOptions, options);
    if (Is10BitFormat(options.pixelFormat)) {
        options.useDMA = true;
    }
    nativePixelMap_ = Media::PixelMap::Create(options);
    if (nativePixelMap_ == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(Media::COMMON_ERR_INVALID_PARAMETER, "Create PixelMap by options failed");
    }
}

PixelMapImpl::PixelMapImpl(std::shared_ptr<Media::PixelMap> pixelMap)
{
    nativePixelMap_ = pixelMap;
    if (nativePixelMap_ == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(Media::COMMON_ERR_INVALID_PARAMETER, "Create PixelMap failed");
    }
}

PixelMapImpl::~PixelMapImpl()
{
    Release();
}

int64_t PixelMapImpl::GetImplPtr()
{
    return reinterpret_cast<uintptr_t>(this);
}

std::shared_ptr<Media::PixelMap> PixelMapImpl::GetNativePtr()
{
    return nativePixelMap_;
}

std::shared_ptr<Media::PixelMap> PixelMapImpl::GetPixelMap(PixelMap etsPixelMap)
{
    PixelMapImpl *pixelMapImpl = reinterpret_cast<PixelMapImpl *>(etsPixelMap->GetImplPtr());
    if (pixelMapImpl == nullptr) {
        IMAGE_LOGE("%{public}s etsPixelMap is nullptr", __func__);
        return nullptr;
    }
    return pixelMapImpl->GetNativePtr();
}

ImageInfo PixelMapImpl::GetImageInfoSync()
{
    if (nativePixelMap_ == nullptr) {
        // ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "Native PixelMap is nullptr");
        return MakeEmptyImageInfo();
    }
    if (!aniEditable_) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "PixelMap has crossed threads");
        return MakeEmptyImageInfo();
    }

    Media::ImageInfo imageInfo;
    nativePixelMap_->GetImageInfo(imageInfo);
    ImageInfo result = ImageTaiheUtils::ToTaiheImageInfo(imageInfo, nativePixelMap_->IsHdr());
    result.density = imageInfo.baseDensity;
    result.stride = nativePixelMap_->GetRowStride();
    return result;
}

ImageInfo PixelMapImpl::GetImageInfoRetPromise()
{
    return GetImageInfoSync();
}

ImageInfo PixelMapImpl::GetImageInfoAsync()
{
    return GetImageInfoSync();
}

void PixelMapImpl::ReadPixelsToBufferSync(array_view<uint8_t> dst)
{
    if (nativePixelMap_ == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "Native PixelMap is nullptr");
        return;
    }
    if (!aniEditable_) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "PixelMap has crossed threads");
        return;
    }

    uint32_t status = nativePixelMap_->ReadPixels(dst.size(), dst.data());
    if (status != Media::SUCCESS) {
        IMAGE_LOGE("[PixelMap ANI] ReadPixels failed");
    }
}

void PixelMapImpl::ReadPixelsToBufferRetPromise(array_view<uint8_t> dst)
{
    return ReadPixelsToBufferSync(dst);
}

void PixelMapImpl::ReadPixelsToBufferWithAsync(array_view<uint8_t> dst)
{
    return ReadPixelsToBufferSync(dst);
}

PixelMap PixelMapImpl::CreateAlphaPixelmapSync()
{
    if (nativePixelMap_ == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "Native PixelMap is nullptr");
        return make_holder<PixelMapImpl, PixelMap>();
    }
    if (!aniEditable_) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "PixelMap has crossed threads");
        return make_holder<PixelMapImpl, PixelMap>();
    }

    Media::InitializationOptions options;
    options.pixelFormat = Media::PixelFormat::ALPHA_8;
    auto alphaPixelMap = Media::PixelMap::Create(*nativePixelMap_, options);
    return make_holder<PixelMapImpl, PixelMap>(std::move(alphaPixelMap));
}

PixelMap PixelMapImpl::CreateAlphaPixelmapRetPromise()
{
    return CreateAlphaPixelmapSync();
}

PixelMap PixelMapImpl::CreateAlphaPixelmapWithAsync()
{
    return CreateAlphaPixelmapSync();
}

int32_t PixelMapImpl::GetBytesNumberPerRow()
{
    if (nativePixelMap_ == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "Native PixelMap is nullptr");
        return 0;
    }
    if (!aniEditable_) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "PixelMap has crossed threads");
        return 0;
    }

    return nativePixelMap_->GetRowBytes();
}

int32_t PixelMapImpl::GetPixelBytesNumber()
{
    if (nativePixelMap_ == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "Native PixelMap is nullptr");
        return 0;
    }
    if (!aniEditable_) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "PixelMap has crossed threads");
        return 0;
    }

    return nativePixelMap_->GetByteCount();
}

void PixelMapImpl::ScaleSync(float x, float y)
{
    if (nativePixelMap_ == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "Native PixelMap is nullptr");
        return;
    }
    if (!aniEditable_) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "PixelMap has crossed threads");
        return;
    }

    nativePixelMap_->scale(x, y);
}

void PixelMapImpl::ScaleWithAntiAliasingSync(float x, float y, AntiAliasingLevel level)
{
    if (nativePixelMap_ == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "Native PixelMap is nullptr");
        return;
    }
    if (!aniEditable_) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "PixelMap has crossed threads");
        return;
    }

    nativePixelMap_->scale(x, y, Media::AntiAliasingOption(level.get_value()));
}

void PixelMapImpl::CropSync(ohos::multimedia::image::image::Region const &region)
{
    if (nativePixelMap_ == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "Native PixelMap is nullptr");
        return;
    }
    if (!aniEditable_) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "PixelMap has crossed threads");
        return;
    }

    Media::Rect rect = {region.x, region.y, region.size.width, region.size.height};
    uint32_t status = nativePixelMap_->crop(rect);
    if (status != Media::SUCCESS) {
        IMAGE_LOGE("[PixelMap ANI] crop failed");
    }
}

void PixelMapImpl::FlipSync(bool horizontal, bool vertical)
{
    if (nativePixelMap_ == nullptr) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "Native PixelMap is nullptr");
        return;
    }
    if (!aniEditable_) {
        ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE, "PixelMap has crossed threads");
        return;
    }

    nativePixelMap_->flip(horizontal, vertical);
}

void PixelMapImpl::ReleaseSync()
{
    if (nativePixelMap_ != nullptr) {
        if (!nativePixelMap_->IsModifiable()) {
            ImageTaiheUtils::ThrowExceptionError(Media::ERR_RESOURCE_UNAVAILABLE,
                                                 "Unable to release the PixelMap "
                                                 "because it's locked or unmodifiable");
        } else {
            IMAGE_LOGD("[PixelMap ANI] Releasing PixelMap with ID: %{public}d", nativePixelMap_->GetUniqueId());
            nativePixelMap_.reset();
        }
    }
}

void PixelMapImpl::ReleaseRetPromise()
{
    return ReleaseSync();
}

void PixelMapImpl::ReleaseWithAsync()
{
    return ReleaseSync();
}

bool PixelMapImpl::Is10BitFormat(Media::PixelFormat format)
{
    return format == Media::PixelFormat::RGBA_1010102 || format == Media::PixelFormat::YCBCR_P010 ||
           format == Media::PixelFormat::YCRCB_P010;
}

void PixelMapImpl::ParseInitializationOptions(InitializationOptions const &etsOptions,
                                              Media::InitializationOptions &options)
{
    options.size = {etsOptions.size.width, etsOptions.size.height};
    if (etsOptions.srcPixelFormat) {
        options.srcPixelFormat = Media::PixelFormat(etsOptions.srcPixelFormat->get_value());
    }
    if (etsOptions.pixelFormat) {
        options.pixelFormat = Media::PixelFormat(etsOptions.pixelFormat->get_value());
    }
    if (etsOptions.editable) {
        options.editable = *etsOptions.editable;
    }
    if (etsOptions.alphaType) {
        options.alphaType = Media::AlphaType(etsOptions.alphaType->get_value());
    }
    if (etsOptions.scaleMode) {
        options.scaleMode = Media::ScaleMode(etsOptions.scaleMode->get_value());
    }
}

void PixelMapImpl::Release()
{
    if (nativePixelMap_ != nullptr) {
        nativePixelMap_.reset();
    }
}

}  // namespace ANI::Image

// NOLINTEND
