#include "rgb.base.abi.hpp"
#include "rgb.show.abi.hpp"

#include <iostream>

using namespace rgb;

int main() {
    base::RGB red   = base::get_rgb(base::Color::RED);
    base::RGB green = base::get_rgb(base::Color::GREEN);
    base::RGB blue  = base::get_rgb(base::Color::BLUE);
    std::cout << "Red:" << std::endl;
    show::show(red);
    std::cout << "Green:" << std::endl;
    show::show(green);
    std::cout << "Blue:" << std::endl;
    show::show(blue);
    base::invert_rgb(red);
    base::invert_rgb(green);
    base::invert_rgb(blue);
    std::cout << "Opposite of Red:" << std::endl;
    show::show(red);
    std::cout << "Opposite of Green:" << std::endl;
    show::show(green);
    std::cout << "Opposite of Blue:" << std::endl;
    show::show(blue);
}
