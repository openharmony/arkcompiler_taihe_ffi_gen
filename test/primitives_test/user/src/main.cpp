#include <multiply_test.proj.hpp>

using namespace ani_test;
using namespace taihe::core;

int main() {
    auto opt = Foo{
        (int32_t)2147483647,
        string("<source>"),
    };
    optionArg1("<str>", opt);
}
