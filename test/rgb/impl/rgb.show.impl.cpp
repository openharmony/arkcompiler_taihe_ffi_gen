#include "rgb.show.impl.hpp"

#include "stdio.h"

void show_rgb(rgb::base::RGB const& color) {
    printf("#%02x%02x%02x\n", color.r, color.g, color.b);
}

TH_EXPORT_CPP_API_show(show_rgb)