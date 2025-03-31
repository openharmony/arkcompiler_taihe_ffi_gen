#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>

#include "ohos.xml.proj.hpp"

using namespace taihe;
using namespace ohos::xml;

int main(int argc, char** argv) {
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
          optional<callback<bool(string_view, string_view)>>::make(
              callback<bool(string_view, string_view)>::from(
                  [](string_view name, string_view value) -> bool {
                    std::cout << "(tag) " << name << ": " << value << std::endl;
                    return true;
                  })),
      .attributeValueCallbackFunction =
          optional<callback<bool(string_view, string_view)>>::make(
              callback<bool(string_view, string_view)>::from(
                  [](string_view name, string_view value) -> bool {
                    std::cout << "(attribute) " << name << ": " << value
                              << std::endl;
                    return true;
                  })),
  });
}
