#include "ohos.xml.proj.hpp"
#include <iostream>
#include <fstream>
#include <sstream>

using namespace taihe::core;
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

    auto parser = makeXmlPullParser(content, nullptr);

    parser->parseXml({
        .supportDoctype = nullptr,
        .ignoreNameSpace = nullptr,
        .tagValueCallbackFunction = optional<callback<bool(string_view, string_view)>>::make(
            callback<bool(string_view, string_view)>::from(
                [](string_view name, string_view value) -> bool {
                    std::cout << "(tag) " << name << ": " << value << std::endl;
                    return true;
                }
            )
        ),
        .attributeValueCallbackFunction = optional<callback<bool(string_view, string_view)>>::make(
            callback<bool(string_view, string_view)>::from(
                [](string_view name, string_view value) -> bool {
                    std::cout << "(attribute) " << name << ": " << value << std::endl;
                    return true;
                }
            )
        ),
        .tokenValueCallbackFunction = nullptr,
    });
}
