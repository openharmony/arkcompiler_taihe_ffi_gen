#include <ani_test.impl.hpp>

using namespace ani_test;
using namespace taihe::core;

static int32_t GetNumberArg0() {
  static int counter = 0;
  return ++counter;
}

static int32_t GetNumberArg4(int32_t x, int32_t y, int32_t z, int32_t w) {
  return x + y + z + w;
}

static void parseOption(Option const& opt) {
  // std::cout << "src: " << opt.src << std::endl;
  // std::cout << "dest: " << opt.dest << std::endl;
  // for (const auto &s : opt.files) {
  //   std::cout << "files: " << s.c_str() << std::endl;
  // }
}

static void optionArg1(string str, Option const& obj1) {
  parseOption(obj1);
}

static void optionArg2(string str, Option const& obj1, Option const& obj2) {
  parseOption(obj1);
  parseOption(obj2);
}

static void optionArg3(string str, Option const& obj1, Option const& obj2, Option const& obj3) {
  parseOption(obj1);
  parseOption(obj2);
  parseOption(obj3);
}

static void optionPrim(double num) {
  double res = num;
}

TH_EXPORT_CPP_API_getNumberArg0(GetNumberArg0)
TH_EXPORT_CPP_API_getNumberArg4(GetNumberArg4)

TH_EXPORT_CPP_API_optionPrim(optionPrim)
TH_EXPORT_CPP_API_optionArg1(optionArg1)
TH_EXPORT_CPP_API_optionArg2(optionArg2)
TH_EXPORT_CPP_API_optionArg3(optionArg3)


