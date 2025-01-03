#pragma once

#include "ohos.xml.proj.hpp"

#include "expat.h"
#include <cstddef>
#include <cstring>
#include <iostream>
#include <ostream>
#include <string>
#include <vector>
#include <functional>

struct ParserState {
    std::string tag;
};

class ExpatParser {
public:
    ExpatParser(ohos::xml::BufferType const& buffer, ohos::xml::OptString const& encoding)
        : m_buffer(buffer.content.c_str()) {
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

    void parse(ohos::xml::ParseOptions* option) {
        if (option->tagValueCallbackFunction.get_tag() != ohos::xml::OptCallbackStringStringBool::TagType::UNDEFINED) {
            this->setTagValueCallback([&](const char* name, const char* value) {
                if (auto callback = option->tagValueCallbackFunction.get_ptr<ohos::xml::OptCallbackStringStringBool::TagType::value>()) {
                    (*callback)(name, value);
                }
            });
        }
        if (option->tagValueCallbackFunction.get_tag() != ohos::xml::OptCallbackStringStringBool::TagType::UNDEFINED) {
            this->setAttributeValueCallback([&](const char* name, const char* value) {
                if (auto callback = option->tagValueCallbackFunction.get_ptr<ohos::xml::OptCallbackStringStringBool::TagType::value>()) {
                    (*callback)(name, value);
                }
            });
        }
        // TODO handle other properties from ParseOptions

        XML_Parse(m_parser, m_buffer.data(), m_buffer.length(), true);

        this->m_tagValueCallback = nullptr;
        this->m_attributeValueCallback = nullptr;
    }

    void setTagValueCallback(std::function<void(const char*, const char*)>&& callback) {
        this->m_tagValueCallback = callback;
    }

    void setAttributeValueCallback(std::function<void(const char*, const char*)>&& callback) {
        this->m_attributeValueCallback = callback;
    }

private:
    static XMLCALL void StartElementHandler(void *userData, const XML_Char *name, const XML_Char **atts) {
        ((ExpatParser*) userData)->onStartElement(name, atts);
    }
    static XMLCALL void EndElementHandler(void *userData, const XML_Char *name) {
        ((ExpatParser*) userData)->onEndElement(name);
    }
    static XMLCALL void CharacterDataHandler(void *userData, const XML_Char *s, int len) {
        ((ExpatParser*) userData)->onText(s, len);
    }

private:
    void onStartElement(const char* name, const char* attrs[]) {
        ParserState ps = { name };
        m_stack.emplace_back(std::move(ps));

        // Attrs is NULL-terminated array of consecutive attrubute keys and values
        // e.g. for `<tag attr1="val1" attr2="val2">` it will be like ["attr1", "val1", "attr2", "val2", NULL]
        const char** attr = attrs;
        while (*attr) {
            const char* key = *(attr++);
            const char* value = *(attr++);
            if (m_attributeValueCallback) {
                m_attributeValueCallback(key, value);
            }
        }
    }

    void onEndElement(const char* name) {
        m_stack.pop_back();
    }

    void onText(const char* data, size_t len) {
        if (m_tagValueCallback) {
            std::string value(data, len);
            m_tagValueCallback(currentTag(), value.c_str());
        }
    }

    const char* currentTag() const {
        if (m_stack.empty()) return "";

        return m_stack.back().tag.c_str();
    }
private:
    XML_Parser m_parser = XML_ParserCreate("UTF-8");
    std::string m_buffer;
    std::vector<ParserState> m_stack;
    std::function<void(const char*, const char*)> m_tagValueCallback;
    std::function<void(const char*, const char*)> m_attributeValueCallback;
    // std::function<void(const char*, const char*)> m_tokenValueCallback; // TODO implement!
};