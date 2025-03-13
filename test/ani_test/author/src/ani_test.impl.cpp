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
  std::cout << "src: " << opt.src << std::endl;
  std::cout << "dest: " << opt.dest << std::endl;
  for (const auto &s : opt.files) {
    std::cout << "files: " << s.c_str() << std::endl;
  }
}

static void optionArg1(string_view str, Option const& obj1) {
  parseOption(obj1);
}

static void optionArg2(string_view str, Option const& obj1, Option const& obj2) {
  parseOption(obj1);
  parseOption(obj2);
}

static void optionArg3(string_view str, Option const& obj1, Option const& obj2, Option const& obj3) {
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

static void testUnion(Union u) {
  if (auto iPtr = u.get_iValue_ptr()) {
    std::cout << "i " << *iPtr << std::endl;
  } else if (auto fPtr = u.get_fValue_ptr()) {
    std::cout << "f " << *fPtr << std::endl;
  } else if (auto sPtr = u.get_sValue_ptr()) {
    std::cout << "s " << *sPtr << std::endl;
  } else {
    std::cout << "e" << std::endl;
  }
}

static Union getUnion(int32_t v) {
  switch (v) {
    case 1:
      return Union::make_iValue(100);
    case 2:
      return Union::make_fValue(0.5);
    case 3:
      return Union::make_sValue("Hello from C++!");
    default:
      return Union::make_empty();
  }
}

static Option getOption() {
  return Option{string("C++ Object"), (float)1.0, array<string>::make(2, "file.txt"), };
}

static void testOptionalDouble(optional_view<double> test) {
  if (test) {
    std::cout << *test << std::endl;
  } else {
    std::cout << "Error" << std::endl;
  }
}

TH_EXPORT_CPP_API_testUnion(testUnion)
TH_EXPORT_CPP_API_getUnion(getUnion)
TH_EXPORT_CPP_API_getOption(getOption)
TH_EXPORT_CPP_API_testOptionalDouble(testOptionalDouble)
