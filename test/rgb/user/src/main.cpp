#include "rgb.base.abi.hpp"
#include "rgb.show.abi.hpp"

using namespace rgb;

int main() {
    base::RGB const red   = base::convert(base::Color::RED);
    base::RGB const green = base::convert(base::Color::GREEN);
    base::RGB const blue  = base::convert(base::Color::BLUE);
    show::show(red);
    show::show(green);
    show::show(blue);
}
