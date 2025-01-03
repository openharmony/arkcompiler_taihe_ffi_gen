#include "greet.proj.hpp"
#include "greet.impl.hpp"

#include <iostream>

auto makeEnglishGreeterImpl() {
    auto en_greeter_impl = [](taihe::core::string_view target) {
        std::cout << "Hello, " << target.c_str() << "!" << std::endl;
    };
    return taihe::core::new_instance<greet::Greeter, decltype(en_greeter_impl)>(en_greeter_impl);
}

class NamedEnglishGreeter {
    taihe::core::string name;

public:
    NamedEnglishGreeter(taihe::core::string_view name) : name(name) {}

    void operator()(taihe::core::string_view target) {
        std::cout << "Hello, " << target.c_str() << "! My name is " << name.c_str() << "!"  << std::endl;
    }
};

auto makeNamedEnglishGreeterImpl(taihe::core::string_view name) {
    return taihe::core::new_instance<greet::Greeter, NamedEnglishGreeter>(name);
}

TH_EXPORT_CPP_API_makeEnglishGreeter(makeEnglishGreeterImpl)
TH_EXPORT_CPP_API_makeNamedEnglishGreeter(makeNamedEnglishGreeterImpl)
