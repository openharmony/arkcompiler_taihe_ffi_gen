#include <ani_test.proj.hpp>

int main() {
    auto res = ani_test::split("goodbye", -3);
    std::cout << res._0 << std::endl;
    std::cout << res._1 << std::endl;
}
