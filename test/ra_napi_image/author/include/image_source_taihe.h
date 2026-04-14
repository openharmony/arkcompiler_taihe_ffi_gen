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

#ifndef FRAMEWORKS_KITS_TAIHE_INCLUDE_IMAGE_SOURCE_TAIHE_H
#define FRAMEWORKS_KITS_TAIHE_INCLUDE_IMAGE_SOURCE_TAIHE_H

#include "image_packer_taihe.h"
#include "image_source.h"
#include "ohos.multimedia.image.image.proj.hpp"
#include "ohos.multimedia.image.image.impl.hpp"
#include "taihe/runtime.hpp"

namespace ANI::Image {
using namespace taihe;
using namespace ohos::multimedia::image::image;

class ImageSourceImpl {
public:
    ImageSourceImpl();
    explicit ImageSourceImpl(std::shared_ptr<OHOS::Media::ImageSource> imageSource);
    ~ImageSourceImpl();
    int64_t GetImplPtr();

    ImageInfo GetImageInfoSync(uint32_t index);
    ImageInfo GetImageInfoRetPromise(uint32_t index);
    ImageInfo GetImageInfoWithAsync(uint32_t index);
    PixelMap CreatePixelMapSync(DecodingOptions const &options);
    PixelMap CreatePixelMapRetPromise(DecodingOptions const &options);
    PixelMap CreatePixelMapWithAsync(DecodingOptions const &options);
    map<PropertyKey, PropertyValue> GetImagePropertiesRetPromise(array_view<PropertyKey> key);
    void ModifyImagePropertyRetPromise(PropertyKey key, string_view value);
    void ModifyImagePropertyWithAsync(PropertyKey key, string_view value);
    void ModifyImagePropertiesRetPromise(map_view<PropertyKey, PropertyValue> records);

    void ReleaseSync();
    void ReleaseRetPromise();
    void ReleaseWithAsync();

    std::shared_ptr<OHOS::Media::ImageSource> nativeImgSrc = nullptr;

    std::shared_ptr<OHOS::Media::IncrementalPixelMap> GetIncrementalPixelMap() const
    {
        return navIncPixelMap_;
    }

    static thread_local std::string filePath_;
    static thread_local int fileDescriptor_;
    static thread_local void *fileBuffer_;
    static thread_local size_t fileBufferSize_;

private:
    std::shared_ptr<OHOS::Media::IncrementalPixelMap> navIncPixelMap_;
    bool isRelease = false;
};
}  // namespace ANI::Image

#endif  // FRAMEWORKS_KITS_TAIHE_INCLUDE_IMAGE_SOURCE_TAIHE_H
// NOLINTEND
