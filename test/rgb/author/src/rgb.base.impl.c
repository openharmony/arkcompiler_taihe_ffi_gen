#include "rgb.base.impl.h"

struct rgb__base__RGB ohos_make_rgb(uint8_t r, uint8_t g, uint8_t b) {
    struct rgb__base__RGB result = {r, g, b};
    return result;
}

TH_EXPORT_C_API_make(ohos_make_rgb)
