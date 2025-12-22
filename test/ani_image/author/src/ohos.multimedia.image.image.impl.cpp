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

#include "ohos.multimedia.image.image.impl.hpp"
#include <iostream>
#include "../include/image_source.h"
#include "../include/image_type.h"
#include "../include/pixel_map.h"
#include "ohos.multimedia.image.image.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace ohos::multimedia::image::image;

namespace {

static string const FILE_URL_PREFIX = "file://";

static std::string FileUrlToRawPath(std::string const &path) {
  if (path.size() > FILE_URL_PREFIX.size() &&
      (path.compare(0, FILE_URL_PREFIX.size(), FILE_URL_PREFIX) == 0)) {
    return path.substr(FILE_URL_PREFIX.size());
  }
  return path;
}

// inline OHOS::Media::PixelFormat toPixelFormat(PixelMapFormat::key_t key) {
//     return static_cast<OHOS::Media::PixelFormat>(static_cast<int>(key));
// }

inline PixelMapFormat::key_t toPixelMapFormatKey(
    OHOS::Media::PixelFormat format) {
  if (static_cast<int>(format) >= 0 && static_cast<int>(format) <= 12) {
    return static_cast<PixelMapFormat::key_t>(static_cast<int>(format));
  } else {
    return PixelMapFormat::key_t::UNKNOWN;
  }
}

// inline OHOS::Media::AlphaType toAlphaType(AlphaType::key_t key)
// {
//     return static_cast<OHOS::Media::AlphaType>(static_cast<int>(key));
// }

inline AlphaType::key_t toAlphaTypeKey(OHOS::Media::AlphaType alphaType) {
  return static_cast<AlphaType::key_t>(static_cast<int>(alphaType));
}

class PixelMapImpl {
public:
  PixelMapImpl() {}

  PixelMapImpl(std::shared_ptr<OHOS::Media::PixelMap> ptr) : m_pdata(ptr) {}

  ~PixelMapImpl() {
    if (this->m_pdata != nullptr) {
      this->m_pdata = nullptr;
    }
  }

  PixelMap createAlphaPixelmapSync() {
    OHOS::Media::InitializationOptions opts;
    opts.pixelFormat = OHOS::Media::PixelFormat::ALPHA_8;
    OHOS::Media::PixelMap::Create(opts);
    return make_holder<PixelMapImpl, PixelMap>();
  }

  ImageInfo getImageInfoSync() {
    OHOS::Media::ImageInfo imgInfo;
    this->m_pdata->GetImageInfo(imgInfo);
    return {{imgInfo.size.width, imgInfo.size.height},
            imgInfo.baseDensity,
            imgInfo.size.height,
            toPixelMapFormatKey(imgInfo.pixelFormat),
            toAlphaTypeKey(imgInfo.alphaType),
            imgInfo.encodedFormat,
            this->m_pdata->IsHdr()};
  }

  int32_t getBytesNumberPerRow() {
    return this->m_pdata->GetRowBytes();
  }

  int32_t getPixelBytesNumber() {
    return this->m_pdata->GetByteCount();
  }

  void readPixelsToBufferSync(array_view<uint8_t> buff) {
    this->m_pdata->ReadPixels(buff.size(), buff.data());
  }

  void scaleSyncWithoutLevel(double x, double y) {
    this->m_pdata->scale(static_cast<float>(x), static_cast<float>(y),
                         OHOS::Media::AntiAliasingOption::NONE);
  }

  void scaleSyncWithLevel(double x, double y, AntiAliasingLevel level) {
    this->m_pdata->scale(static_cast<float>(x), static_cast<float>(y),
                         OHOS::Media::AntiAliasingOption(level.get_value()));
  }

  void cropSync(Region const &region) {
    OHOS::Media::Rect rect = {region.x, region.y, region.size.width,
                              region.size.height};
    this->m_pdata->crop(rect);
  }

  void flipSync(bool horizontal, bool vertical) {
    this->m_pdata->flip(horizontal, vertical);
  }

  void releaseSync() {
    this->m_pdata.reset();
  }

  int64_t getInner() {
    return reinterpret_cast<int64_t>(this);
  }

protected:
  std::shared_ptr<OHOS::Media::PixelMap> m_pdata;
};

class ImageSourceImpl {
public:
  ImageSourceImpl() {}

  ImageSourceImpl(string_view str) {
    std::string stdStr{std::string_view(str)};
    this->filePath_ = FileUrlToRawPath(stdStr);
    OHOS::Media::SourceOptions opts;
    uint32_t errorCode;
    this->m_pdata = OHOS::Media::ImageSource::CreateImageSource(
        this->filePath_, opts, errorCode);
    this->fileDescriptor_ = 0;  // TODO
  }

  ImageSourceImpl(int32_t fd) {
    OHOS::Media::SourceOptions opts;
    uint32_t errorCode;
    this->m_pdata =
        OHOS::Media::ImageSource::CreateImageSource(fd, opts, errorCode);
    this->fileDescriptor_ = 0;  // TODO
  }

  ImageInfo getImageInfoSync(int32_t index) {
    OHOS::Media::ImageInfo imgInfo;
    return {{imgInfo.size.width, imgInfo.size.height},
            imgInfo.baseDensity,
            imgInfo.size.height,
            toPixelMapFormatKey(imgInfo.pixelFormat),
            toAlphaTypeKey(imgInfo.alphaType),
            imgInfo.encodedFormat,
            false};
  }

  PixelMap createPixelMapSync(optional_view<DecodingOptions> options) {
    return make_holder<PixelMapImpl, PixelMap>(
        std::make_shared<OHOS::Media::PixelMap>());
  }

  void modifyImageProperty(string_view key, string_view value) {
    std::cout << "ModifyImageProperty get key:" << key << "value:" << value
              << std::endl;
  }

  void modifyImagePropertiesSync(map_view<string, NullableString> records) {
    for (auto it = records.begin(); it != records.end(); ++it) {
      auto const &[key, value] = *it;
      switch (value.get_tag()) {
      case NullableString::tag_t::str:
        this->modifyImageProperty(key, value.get_str_ref());
      case NullableString::tag_t::null:
        this->modifyImageProperty(key, "");
      }
    }
  }

  map<string, NullableString> getImagePropertiesSync(array_view<string> key) {
    map<string, NullableString> result;
    for (auto it = key.begin(); it != key.end(); ++it) {
      result.emplace(*it, NullableString::make_str(""));
    }
    return result;
  }

  void release() {
    this->m_pdata.reset();
  }

private:
  std::shared_ptr<OHOS::Media::ImageSource> m_pdata;
  std::string filePath_;
  int fileDescriptor_;
};
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
// NOLINTEND
