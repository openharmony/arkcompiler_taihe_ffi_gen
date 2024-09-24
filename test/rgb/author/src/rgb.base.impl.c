#include "rgb.base.impl.h"

struct rgb__base__RGB ohos_color_convert(rgb__base__Color color) {
    struct rgb__base__RGB result = {
        color >> 16 & 0xff,
        color >>  8 & 0xff,
        color >>  0 & 0xff,
    };
    return result;
}

TH_EXPORT_C_API_convert(ohos_color_convert)
