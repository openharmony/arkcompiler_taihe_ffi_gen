#include "ohos.xml.proj.hpp"
#include <iostream>

using namespace taihe::core;
using namespace ohos::xml;

char const *content =
    "<bookstore>\n"
    "  <book category=\"COOKING\">\n"
    "    <title lang=\"en\">Everyday Italian</title>\n"
    "    <author>Giada De Laurentiis</author>\n"
    "    <year>2005</year>\n"
    "    <price>30.00</price>\n"
    "  </book>\n"
    "  <book category=\"CHILDREN\">\n"
    "    <title lang=\"en\">Harry Potter</title>\n"
    "    <author>J K. Rowling</author>\n"
    "    <year>2005</year>\n"
    "    <price>29.99</price>\n"
    "  </book>\n"
    "  <book category=\"WEB\">\n"
    "    <title lang=\"en\">Learning XML</title>\n"
    "    <author>Erik T. Ray</author>\n"
    "    <year>2003</year>\n"
    "    <price>39.95</price>\n"
    "  </book>\n"
    "</bookstore>\n";

int main() {
    auto parser = makeXmlPullParser({content}, static_tag_v<OptString::tag_t::UNDEFINED>);

    auto tag_cb = [](taihe::core::string_view name, taihe::core::string_view value) {
        std::cout << "(tag) " << std::string_view(name) << ": " << std::string_view(value) << std::endl;
        return true;
    };
    auto attr_cb = [](taihe::core::string_view name, taihe::core::string_view value) {
        std::cout << "(attribute) " << std::string_view(name) << ": " << std::string_view(value) << std::endl;
        return true;
    };

    parser.parseXml({
        .supportDoctype = static_tag_v<OptBool::tag_t::UNDEFINED>,
        .ignoreNameSpace = static_tag_v<OptBool::tag_t::UNDEFINED>,
        .tagValueCallbackFunction = {
            static_tag_v<OptCallbackStringStringBool::tag_t::value>,
            new_instance<CallbackStringStringBool, decltype(tag_cb)>(tag_cb),
        },
        .attributeValueCallbackFunction = {
            static_tag_v<OptCallbackStringStringBool::tag_t::value>,
            new_instance<CallbackStringStringBool, decltype(attr_cb)>(attr_cb),
        },
        . tokenValueCallbackFunction = {
            static_tag_v<OptCallbackEventTypeParseInfoBool::tag_t::UNDEFINED>,
        },
    });
}
