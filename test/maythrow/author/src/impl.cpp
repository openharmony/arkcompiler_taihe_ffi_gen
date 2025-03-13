#include <maythrow.impl.hpp>
#include <iostream>
#include "core/runtime.hpp"

void maythrow_impl(int32_t a) {
    if (a == 0) {
        taihe::core::throw_error("some error happen");
    } else {
        std::cout << "success" << std::endl;
    }
}

TH_EXPORT_CPP_API_maythrow(maythrow_impl);