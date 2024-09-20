#include "rgb.base.abi.hpp"
#include "rgb.show.abi.hpp"

using namespace rgb;

int main() {
    base::RGB const color = base::make(255, 255, 255);
    show::show(color);
}
