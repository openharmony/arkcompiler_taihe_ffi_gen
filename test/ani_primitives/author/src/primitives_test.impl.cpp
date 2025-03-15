#include "primitives_test.impl.hpp"
// Please delete this include when you implement
using namespace taihe::core;
namespace
{

  static void parseOption(::primitives_test::Foo const &opt)
  {
    std::cout << "num: " << opt.testNum << std::endl;
    std::cout << "str: " << opt.testStr << std::endl;
  }

  int32_t multiply(int32_t a, int32_t b)
  {
    return a * b;
  }

  bool baseCFunc(int32_t testBoolean)
  {
    if (testBoolean == 10)
    {
      return true;
    }
    else
    {
      return false;
    }
  }

  void baseAFunc(bool testBoolean)
  {
    if (testBoolean)
    {
      std::cout << "testBoolean is true " << testBoolean << std::endl;
    }
    else
    {
      std::cout << "testBoolean is false  " << testBoolean << std::endl;
    }
  }
  bool baseBFunc(bool testBoolean)
  {
    if (testBoolean)
    {
      return false;
    }
    else
    {
      return true;
    }
  }
  bool baseDFunc(string_view testBoolean)
  {
    if (testBoolean == "test123")
    {
      return true;
    }
    else
    {
      return false;
    }
  }

  string baseEFunc(::primitives_test::Foo const &b)
  {
    parseOption(b);
    return "success";
  }
  string baseHFunc(int32_t a, int64_t b)
  {
    int64_t sum = static_cast<int64_t>(a) + b;
    return std::to_string(sum);
  }
  string baseIFunc(double a, float b)
  {
    double sum = static_cast<double>(a) + b;
    return std::to_string(sum);
  }

  float baseFunc1(float b)
  {
    return b + 1.0;
  }

  void baseFunc2(float b)
  {
    if (b == 1.2)
    {
      std::cout << "baseFunc2 is true " << b << std::endl;
    }
    else
    {
      std::cout << "baseFunc2 is false  " << b << std::endl;
    }
  }

  double baseFunc3(float a, double b)
  {
    return static_cast<double>(a) + b;
  }

  double baseFunc4(double b)
  {
    return b + 1.0;
  }

  void baseFunc5(double b)
  {
    if (b == 3.14159)
    {
      std::cout << "baseFunc5 is true " << b << std::endl;
    }
    else
    {
      std::cout << "baseFunc5 is false  " << b << std::endl;
    }
  }

  void baseFunc6(string_view a)
  {
    if (a == "testbaseFunc6")
    {
      std::cout << "baseFunc6 is true " << a << std::endl;
    }
    else
    {
      std::cout << "baseFunc6 is false  " << a << std::endl;
    }
  }
  string baseFunc7(string_view a)
  {
    if (a == "testbaseFunc7")
    {
      return std::string(a); // 返回 a
    }
    else
    {
      return std::string(a) + "false"; // 返回 a + "false";
    }
  }
  string baseFunc8(string_view a, int32_t b)
  {
    if (a == "testbaseFunc8")
    {
      return std::string(a) + std::to_string(b); // 返回 a + b（b 转换为字符串）
    }
    else
    {
      return std::string(a); // 返回 a
    }
  }
  void baseFunc9(string_view a, int32_t b, int64_t c, bool d, float e)
  {
    if (a == "testbaseFunc9")
    {
      std::cout << "str: " << a << std::endl;
    }
    else if (b == 32)
    {
      std::cout << "int32: " << b << std::endl;
    }
    else if (c == 9223372036854775807)
    {
      std::cout << "int64: " << c << std::endl;
    }
    else if (d)
    {
      std::cout << "boolean: " << d << std::endl;
    }
    else if (e == 3.1)
    {
      std::cout << "testFloat: " << e << std::endl;
    }
    else
    {
      std::cout << "testError: " << std::endl;
    }
  }

  void baseFunc10()
  {
    std::cout << "baseFunc10 is true " << std::endl;
  }
  
  void baseFunc11(int32_t a, bool b)
  {
    if (b)
    {
      std::cout << "baseFunc11 is a  " << a << std::endl;
      std::cout << "baseFunc11 is b  " << b << std::endl;
    }
    else
    {
      std::cout << "baseFunc11 is a  " << a << std::endl;
      std::cout << "baseFunc11 is b  " << b << std::endl;
    }
  }
  void baseFunc12(int32_t a, int64_t b)
  {
    std::cout << "baseFunc12 is a  " << a << std::endl;
    std::cout << "baseFunc12 is b  " << b << std::endl;
  }
  void baseFunc13(int32_t a, string_view b)
  {
    std::cout << "baseFunc13 is a  " << a << std::endl;
    std::cout << "baseFunc13 is b  " << b << std::endl;
  }
  void baseFunc14(int64_t a, bool b)
  {
    if (b)
    {
      std::cout << "baseFunc14 is a  " << a << std::endl;
      std::cout << "baseFunc14 is b  " << b << std::endl;
    }
    else
    {
      std::cout << "baseFunc14 is a  " << a << std::endl;
      std::cout << "baseFunc14 is b  " << b << std::endl;
    }
  }
  void baseFunc15(int64_t a, float b)
  {
    std::cout << "baseFunc15 is a  " << a << std::endl;
    std::cout << "baseFunc15 is b  " << b << std::endl;
  }
  void baseFunc16(int64_t a, double b)
  {
    std::cout << "baseFunc16 is a  " << a << std::endl;
    std::cout << "baseFunc16 is b  " << b << std::endl;
  }
  void baseFunc17(float a, bool b)
  {
    if (b)
    {
      std::cout << "baseFunc17 is a  " << a << std::endl;
      std::cout << "baseFunc17 is b  " << b << std::endl;
    }
    else
    {
      std::cout << "baseFunc17 is a  " << a << std::endl;
      std::cout << "baseFunc17 is b  " << b << std::endl;
    }
  }
  void baseFunc18(float a, string_view b)
  {
    std::cout << "baseFunc18 is a  " << a << std::endl;
    std::cout << "baseFunc18 is b  " << b << std::endl;
  }
  void baseFunc19(double a, string_view b)
  {
    std::cout << "baseFunc19 is a  " << a << std::endl;
    std::cout << "baseFunc19 is b  " << b << std::endl;
  }
}
void baseFunc20(double a, bool b)
{
  if (b)
  {
    std::cout << "baseFunc20 is a  " << a << std::endl;
    std::cout << "baseFunc20 is b  " << b << std::endl;
  }
  else
  {
    std::cout << "baseFunc20 is a  " << a << std::endl;
    std::cout << "baseFunc20 is b  " << b << std::endl;
  }
}

TH_EXPORT_CPP_API_multiply(multiply)
TH_EXPORT_CPP_API_baseCFunc(baseCFunc)
TH_EXPORT_CPP_API_baseAFunc(baseAFunc)
TH_EXPORT_CPP_API_baseBFunc(baseBFunc)
TH_EXPORT_CPP_API_baseDFunc(baseDFunc)
TH_EXPORT_CPP_API_baseEFunc(baseEFunc)
TH_EXPORT_CPP_API_baseHFunc(baseHFunc)
TH_EXPORT_CPP_API_baseIFunc(baseIFunc)
TH_EXPORT_CPP_API_baseFunc1(baseFunc1)
TH_EXPORT_CPP_API_baseFunc2(baseFunc2)
TH_EXPORT_CPP_API_baseFunc3(baseFunc3)
TH_EXPORT_CPP_API_baseFunc4(baseFunc4)
TH_EXPORT_CPP_API_baseFunc5(baseFunc5)
TH_EXPORT_CPP_API_baseFunc6(baseFunc6)
TH_EXPORT_CPP_API_baseFunc7(baseFunc7)
TH_EXPORT_CPP_API_baseFunc8(baseFunc8)
TH_EXPORT_CPP_API_baseFunc9(baseFunc9)
TH_EXPORT_CPP_API_baseFunc10(baseFunc10)
TH_EXPORT_CPP_API_baseFunc11(baseFunc11)
TH_EXPORT_CPP_API_baseFunc12(baseFunc12)
TH_EXPORT_CPP_API_baseFunc13(baseFunc13)
TH_EXPORT_CPP_API_baseFunc14(baseFunc14)
TH_EXPORT_CPP_API_baseFunc15(baseFunc15)
TH_EXPORT_CPP_API_baseFunc16(baseFunc16)
TH_EXPORT_CPP_API_baseFunc17(baseFunc17)
TH_EXPORT_CPP_API_baseFunc18(baseFunc18)
TH_EXPORT_CPP_API_baseFunc19(baseFunc19)
TH_EXPORT_CPP_API_baseFunc20(baseFunc20)