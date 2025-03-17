#include "interface.impl.hpp"
#include <cstdint>
#include <iostream>

using namespace taihe::core;

namespace {

class native_window {
private:
    int32_t height;
public:
    native_window(int32_t v)
        : height(v) {}
    int32_t getheight() {
        return this->height;
    }
    void setheight(int32_t b) {
        this->height = b;
    }
};

::interface::window get_interface(int32_t v) {
    return make_holder<native_window, ::interface::window>(v);
}

void check_interface(::interface::weak::window a) {
    int32_t res = a->getheight();
    std::cout << res << std::endl;
}

}

TH_EXPORT_CPP_API_get_interface(get_interface)
TH_EXPORT_CPP_API_check_interface(check_interface)
