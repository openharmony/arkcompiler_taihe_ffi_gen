#pragma once

#include "core/string.hpp"
#include "ohos.xml.proj.hpp"

#include "expat.h"
#include <cstddef>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

struct ExpatParserState {
    ohos::xml::ParseOptions const& m_option;
    std::vector<taihe::core::string> m_stack;

    void onStartElement(const char* name, const char* attrs[]) {
        m_stack.emplace_back(name);
        for (const char** iter = attrs; *iter; iter += 2) {
            if (auto callback = m_option.attributeValueCallbackFunction.get_value_ptr()) {
                (*callback)(iter[0], iter[1]);
            }
        }
    }

    void onEndElement(const char* name) {
        m_stack.pop_back();
    }

    void onCharacterData(const char* data, size_t len) {
        if (m_stack.empty()) {
            return;
        }
        if (auto callback = m_option.tagValueCallbackFunction.get_value_ptr()) {
            (*callback)(m_stack.back(), taihe::core::string_view_container(data, len));
        }
    }
};

class ExpatParser {
private:
    XML_Parser m_parser;
    ohos::xml::BufferType m_buffer;

public:
    ExpatParser(ohos::xml::BufferType const& buffer, ohos::xml::OptString const& encoding)
        : m_buffer(buffer) {
        if (auto str = encoding.get_ptr<ohos::xml::OptString::tag_t::value>()) {
            this->m_parser = XML_ParserCreate(str->c_str());
        } else {
            this->m_parser = XML_ParserCreate("UTF-8");
        }
        XML_SetStartElementHandler(m_parser, StartElementHandler);
        XML_SetEndElementHandler(m_parser, EndElementHandler);
        XML_SetCharacterDataHandler(m_parser, CharacterDataHandler);
    }

    virtual ~ExpatParser() {
        XML_ParserFree(m_parser);
        std::cerr << "Parser destroy" << std::endl;
    }

    void parse(ohos::xml::ParseOptions const& option) {
        parseXml(option);
    }

    void parseXml(ohos::xml::ParseOptions const& option) {
        ExpatParserState state = {option};
        XML_SetUserData(m_parser, &state);
        XML_Parse(m_parser, m_buffer.content.data(), m_buffer.content.size(), true);
    }

private:
    static XMLCALL void StartElementHandler(void *userData, const XML_Char *name, const XML_Char **atts) {
        ((ExpatParserState*)userData)->onStartElement(name, atts);
    }
    static XMLCALL void EndElementHandler(void *userData, const XML_Char *name) {
        ((ExpatParserState*)userData)->onEndElement(name);
    }
    static XMLCALL void CharacterDataHandler(void *userData, const XML_Char *s, int len) {
        ((ExpatParserState*)userData)->onCharacterData(s, len);
    }
};
