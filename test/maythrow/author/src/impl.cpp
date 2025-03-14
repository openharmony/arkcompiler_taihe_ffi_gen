#include <maythrow.impl.hpp>
#include <iostream>
#include "core/runtime.hpp"

int32_t maythrow_impl(int32_t a) {
    if (a == 0) {
        taihe::core::throw_error("some error happen");
        return -1;
    } else {
        return a + 10;
    }
}

TH_EXPORT_CPP_API_maythrow(maythrow_impl);
