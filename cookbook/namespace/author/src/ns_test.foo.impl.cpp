#include "ns_test.foo.impl.hpp"

#include "iostream"
#include "ns_test.foo.window.proj.2.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {

    class window {
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
    
    ::ns_test::foo::window get_interface(int32_t v) {
        return make_holder<window, ::ns_test::foo::window>();
    }
    void check_interface(::ns_test::foo::weak::window a) {
        int32_t res = a->getheight();
        std::cout << res << std::endl;
    }
    
    }
    
TH_EXPORT_CPP_API_get_interface(get_interface);
TH_EXPORT_CPP_API_check_interface(check_interface);
