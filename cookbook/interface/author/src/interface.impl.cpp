#include "interface.impl.hpp"
#include <iostream>
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {

class window {
public:
    int32_t getheight() {
        throw std::runtime_error("Function window::getheight Not implemented");
    }
    void setheight(int32_t b) {
        throw std::runtime_error("Function window::setheight Not implemented");
    }
};

class native_window: public window {
    private:
        int32_t height = 10;
    public:
    int32_t getheight() {
        return this->height;
    }
    void setheight(int32_t b) {
        this->height = b;
    }
};

::interface::window get_interface() {
    return make_holder<native_window, ::interface::window>();
}
void check_interface(::interface::weak::window a) {
    int32_t res = a->getheight();
    std::cout << res << std::endl;
}

}

TH_EXPORT_CPP_API_get_interface(get_interface)
TH_EXPORT_CPP_API_check_interface(check_interface)
