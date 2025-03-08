#include <ani_test.proj.hpp>

using namespace ani_test;
using namespace taihe::core;

int main() {
    auto opt = Option{
        string("<source>"),
        (double)1.0,
        array<string>::make(10, string("<file>")),
    };
    optionArg1("<str>", opt);
}
