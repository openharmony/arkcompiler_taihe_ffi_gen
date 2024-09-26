#include "rgb.base.impl.h"

struct __rgb__base__RGB ohos_color_convert(__rgb__base__Color color) {
    struct __rgb__base__RGB result = {
        color >> 16 & 0xff,
        color >>  8 & 0xff,
        color >>  0 & 0xff,
    };
    return result;
}

void ohos_color_invert(__rgb__base__RGB *ptr) {
    ptr->r = ~ptr->r;
    ptr->g = ~ptr->g;
    ptr->b = ~ptr->b;
}

TH_EXPORT_C_API_get_rgb(ohos_color_convert)
TH_EXPORT_C_API_invert_rgb(ohos_color_invert)
