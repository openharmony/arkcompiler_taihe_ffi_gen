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

    auto parser = makeXmlPullParser(content, static_tag<OptString::tag_t::UNDEFINED>);

    parser.parseXml({
        .supportDoctype = OptBool::make_UNDEFINED(),
        .ignoreNameSpace = OptBool::make_UNDEFINED(),
        .tagValueCallbackFunction = OptCallbackKV::make_value(
            into_holder<CallbackKV>(
                [](taihe::core::string_view name, taihe::core::string_view value) {
                    std::cout << "(tag) "
                              << std::string_view(name)
                              << ": "
                              << std::string_view(value)
                              << std::endl;
                    return true;
                }
            )
        ),
        .attributeValueCallbackFunction = OptCallbackKV::make_value(
            into_holder<CallbackKV>(
                [](taihe::core::string_view name, taihe::core::string_view value) {
                    std::cout << "(attribute) "
                              << std::string_view(name)
                              << ": "
                              << std::string_view(value)
                              << std::endl;
                    return true;
                }
            )
        ),
        .tokenValueCallbackFunction = OptCallbackEvent::make_UNDEFINED(),
    });
}
