#pragma once

#include "ohos.xml.proj.hpp"

#include "expat.h"
#include <cstddef>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

class ExpatParser {
public:
    ExpatParser(ohos::xml::BufferType const& buffer, ohos::xml::OptString const& encoding)
        : m_buffer(buffer)
        , p_option(nullptr) {
        if (auto str = encoding.get_ptr<ohos::xml::OptString::tag_t::value>()) {
            this->m_parser = XML_ParserCreate(str->c_str());
        } else {
            this->m_parser = XML_ParserCreate("UTF-8");
        }
        XML_SetUserData(m_parser, this);
        XML_SetStartElementHandler(m_parser, StartElementHandler);
        XML_SetEndElementHandler(m_parser, EndElementHandler);
        XML_SetCharacterDataHandler(m_parser, CharacterDataHandler);
    }

    virtual ~ExpatParser() {
        XML_ParserFree(m_parser);
        std::cerr << "Parser destroy" << std::endl;
    }

    ExpatParser(const ExpatParser&) = delete;
    ExpatParser& operator=(const ExpatParser&) = delete;
    ExpatParser(const ExpatParser&&) = delete;
    ExpatParser& operator=(const ExpatParser&&) = delete;

    void parse(ohos::xml::ParseOptions const& option) {
        this->p_option = &option;
        XML_Parse(m_parser, m_buffer.content.data(), m_buffer.content.size(), true);
        this->p_option = nullptr;
        m_stack.clear();
    }

    void parseXml(ohos::xml::ParseOptions const& option) {
        this->p_option = &option;
        XML_Parse(m_parser, m_buffer.content.data(), m_buffer.content.size(), true);
        this->p_option = nullptr;
        m_stack.clear();
    }

private:
    static XMLCALL void StartElementHandler(void *userData, const XML_Char *name, const XML_Char **atts) {
        ((ExpatParser*)userData)->onStartElement(name, atts);
    }
    static XMLCALL void EndElementHandler(void *userData, const XML_Char *name) {
        ((ExpatParser*)userData)->onEndElement(name);
    }
    static XMLCALL void CharacterDataHandler(void *userData, const XML_Char *s, int len) {
        ((ExpatParser*)userData)->onText(s, len);
    }

private:
    void onStartElement(const char* name, const char* attrs[]) {
        m_stack.emplace_back(name);
        for (const char** iter = attrs; *iter; iter += 2) {
            if (auto callback = p_option->attributeValueCallbackFunction.get_ptr<ohos::xml::OptCallbackStringStringBool::tag_t::value>()) {
                (*callback)(iter[0], iter[1]);
            }
        }
    }

    void onEndElement(const char* name) {
        m_stack.pop_back();
    }

    void onText(const char* data, size_t len) {
        if (m_stack.empty()) {
            return;
        }
        if (auto callback = p_option->tagValueCallbackFunction.get_ptr<ohos::xml::OptCallbackStringStringBool::tag_t::value>()) {
            (*callback)(m_stack.back(), taihe::core::string_view(data, len));
        }
    }

private:
    XML_Parser m_parser;
    ohos::xml::BufferType m_buffer;
    ohos::xml::ParseOptions const* p_option;
    std::vector<taihe::core::string> m_stack;
};
