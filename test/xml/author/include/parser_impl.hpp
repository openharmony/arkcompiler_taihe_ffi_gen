#pragma once

#include <taihe/string.hpp>

#include <expat.h>

#include <cstddef>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

#include "ohos.xml.proj.hpp"

struct ExpatParserState {
  ohos::xml::ParseOptions const& m_option;
  std::vector<taihe::string> m_stack;

  void onStartElement(char const* name, char const* attrs[]) {
    m_stack.emplace_back(name);
    for (char const** iter = attrs; *iter; iter += 2) {
      if (m_option.attributeValueCallbackFunction) {
        (*m_option.attributeValueCallbackFunction)(iter[0], iter[1]);
      }
    }
  }

  void onEndElement(char const* name) {
    m_stack.pop_back();
  }

  void onCharacterData(char const* data, size_t len) {
    if (m_stack.empty()) {
      return;
    }
    if (m_option.tagValueCallbackFunction) {
      (*m_option.tagValueCallbackFunction)(m_stack.back(),
                                           taihe::string_view(data, len));
    }
  }
};

class ExpatParser {
private:
  XML_Parser m_parser;
  ohos::xml::BufferType m_buffer;

public:
  ExpatParser(ohos::xml::BufferType const& buffer,
              taihe::optional_view<taihe::string> encoding)
      : m_buffer(buffer) {
    if (encoding) {
      this->m_parser = XML_ParserCreate(encoding->c_str());
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
  static XMLCALL void StartElementHandler(void* userData, XML_Char const* name,
                                          XML_Char const** atts) {
    ((ExpatParserState*)userData)->onStartElement(name, atts);
  }

  static XMLCALL void EndElementHandler(void* userData, XML_Char const* name) {
    ((ExpatParserState*)userData)->onEndElement(name);
  }

  static XMLCALL void CharacterDataHandler(void* userData, XML_Char const* s,
                                           int len) {
    ((ExpatParserState*)userData)->onCharacterData(s, len);
  }
};
