#include "onoff.impl.hpp"
#include "stdexcept"
#include "core/string.hpp"
#include "onoff.IBase.proj.2.hpp"
#include <iostream>
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
class IBase {
public:
    IBase(string a, string b): str(a), new_str(b) {}
    ~IBase(){}
    string onGet() {
        return str;
    }
    string onGetNew() {
        return new_str;
    }
    void offSet(string_view a) {
        std::cout << "off set" << std::endl; 
        str = a;
    }
    void offSetNew(string_view a) {
        std::cout << "off setNew" << std::endl; 
        new_str = a;
    }
private:
    string str;
    string new_str;
};
::onoff::IBase getIBase(string_view a, string_view b) {
    return make_holder<IBase, ::onoff::IBase>(a, b);
}
void onFoo(int32_t a) {
    std::cout << "onFoo" << std::endl; 
}
void onBar(int32_t a) {
    std::cout << "onBar" << std::endl; 
}
void onBaz(string_view a) {
    std::cout << "onBaz" << std::endl; 
}
void onQux(string_view a, int32_t b) {
    std::cout << "onQux" << std::endl; 
}

void offFoo(int32_t a) {
    std::cout << "offFoo" << std::endl; 
}
void offBar(int32_t a) {
    std::cout << "offBar" << std::endl; 
}
void offBaz(string_view a) {
    std::cout << "offBaz" << std::endl; 
}
void offQux(string_view a, int32_t b) {
    std::cout << "offQux" << std::endl; 
}
}
TH_EXPORT_CPP_API_getIBase(getIBase)
TH_EXPORT_CPP_API_onFoo(onFoo)
TH_EXPORT_CPP_API_onBar(onBar)
TH_EXPORT_CPP_API_onBaz(onBaz)
TH_EXPORT_CPP_API_onQux(onQux)
TH_EXPORT_CPP_API_offFoo(offFoo)
TH_EXPORT_CPP_API_offBar(offBar)
TH_EXPORT_CPP_API_offBaz(offBaz)
TH_EXPORT_CPP_API_offQux(offQux)
