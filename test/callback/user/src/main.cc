#include "greet.proj.hpp"

#include <iostream>

int main() {
    auto en_greeter = greet::makeEnglishGreeter();
    auto named_en_greeter = greet::makeNamedEnglishGreeter("Simon");

    auto cn_greeter_impl = [](taihe::core::string_view target) {
        std::cout << target.c_str() << "，你好！" << std::endl;
    };
    auto cn_greeter = taihe::core::new_instance<greet::Greeter, decltype(cn_greeter_impl)>(cn_greeter_impl);

    en_greeter("world");
    named_en_greeter("David");
    cn_greeter("世界");
}
