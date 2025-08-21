#include "ohos.multimedia.image.image.impl.hpp"
#include "ohos.multimedia.image.image.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

class PixelMapImpl {
public:
  PixelMapImpl() {}
};

class ImageSourceImpl {
public:
  ImageSourceImpl() {}

  ::ohos::multimedia::image::image::PixelMap CreatePixelMapSync(
      ::ohos::multimedia::image::image::DecodingOptions const &options) {
    return taihe::make_holder<PixelMapImpl,
                              ::ohos::multimedia::image::image::PixelMap>();
  }
};

::ohos::multimedia::image::image::ImageSource CreateImageSource() {
  return taihe::make_holder<ImageSourceImpl,
                            ::ohos::multimedia::image::image::ImageSource>();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_CreateImageSource(CreateImageSource);
// NOLINTEND
