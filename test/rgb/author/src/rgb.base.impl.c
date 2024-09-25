#include "rgb.base.impl.h"

struct rgb__base__RGB ohos_color_convert(rgb__base__Color color) {
    struct rgb__base__RGB result = {
        color >> 16 & 0xff,
        color >>  8 & 0xff,
        color >>  0 & 0xff,
    };
    return result;
}

void ohos_color_invert(rgb__base__RGB *ptr) {
    ptr->r = 0xff - ptr->r;
    ptr->g = 0xff - ptr->g;
    ptr->b = 0xff - ptr->b;
}

TH_EXPORT_C_API_get_rgb(ohos_color_convert)
TH_EXPORT_C_API_invert_rgb(ohos_color_invert)
