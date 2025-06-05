#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>

#include "ohos.xml.user.hpp"

using namespace taihe;
using namespace ohos::xml;

struct CallbackTag {
  CallbackTag() {
    std::cout << "CallbackTag constructor" << std::endl;
  }

  ~CallbackTag() {
    std::cout << "CallbackTag destructor" << std::endl;
  }

  bool operator()(string_view name, string_view value) {
    std::cout << "(tag) " << name << ": " << value << std::endl;
    return true;
  }
};

struct CallbackAttribute {
  CallbackAttribute() {
    std::cout << "CallbackAttribute constructor" << std::endl;
  }

  ~CallbackAttribute() {
    std::cout << "CallbackAttribute destructor" << std::endl;
  }

  bool operator()(string_view name, string_view value) {
    std::cout << "(attribute) " << name << ": " << value << std::endl;
    return true;
  }
};

int main(int argc, char **argv) {
  if (argc != 2) {
    std::cerr << "Should have 1 argument!" << std::endl;
    return 1;
  }
  std::ifstream file(argv[1], std::ios::in);
  if (!file.is_open()) {
    std::cerr << "File not exist!" << std::endl;
    return 1;
  }
  std::stringstream buffer;
  buffer << file.rdbuf();

  BufferType content = {buffer.str()};

  auto parser = makeXmlPullParser(content, {});

  parser->parseXml({
      .tagValueCallbackFunction =
          {std::in_place,
           make_holder<CallbackTag,
                       callback<bool(string_view, string_view)>>()},
      .attributeValueCallbackFunction =
          {std::in_place,
           make_holder<CallbackAttribute,
                       callback<bool(string_view, string_view)>>()},
  });
}
