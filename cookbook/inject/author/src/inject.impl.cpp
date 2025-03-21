#include "inject.impl.hpp"
#include "stdexcept"
#include "core/string.hpp"
#include "inject.Foo.proj.2.hpp"
#include <iostream>
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
class Foo {
public:
    void with_name(string_view name) {
        std::cout << name << std::endl;
    }
    void with_this(uintptr_t thiz) {
        std::cout << thiz << std::endl;
    }
};
::inject::Foo makeFoo() {
    return make_holder<Foo, ::inject::Foo>();
}
}
TH_EXPORT_CPP_API_makeFoo(makeFoo)
