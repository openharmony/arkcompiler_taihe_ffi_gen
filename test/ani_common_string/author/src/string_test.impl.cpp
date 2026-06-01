/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "stringTest.impl.hpp"

#include "stdexcept"

#include <cstdint>
#include <iomanip>
#include <sstream>
#include <string>
#include <string_view>
#include <utility>

#include "taihe/string.hpp"

namespace {
using ExpectedString = ::taihe::expected<::taihe::string, ::taihe::error>;

constexpr std::size_t FIRST_INDEX = 0;
constexpr std::size_t UTF16_HEX_WIDTH = 4;
constexpr std::size_t UTF8_TEXT_SIZE = 6;
constexpr std::size_t SAMPLE_SUBSTR_OFFSET = 1;
constexpr std::size_t UTF8_SUBSTR_SIZE = 3;
constexpr std::size_t ONE_CODE_UNIT = 1;
constexpr std::size_t TWO_CODE_UNITS = 2;
constexpr std::size_t FOUR_CODE_UNITS = 4;
constexpr std::size_t FIVE_CODE_UNITS = 5;
constexpr std::size_t CONVERTED_UTF16_SIZE = 8;
constexpr std::size_t THIRD_CHAR_INDEX = 2;

constexpr int POSITIVE_TO_STRING_VALUE = 42;
constexpr int NEGATIVE_TO_STRING_VALUE = -7;

void Require(bool condition, char const *message)
{
    if (!condition) {
        throw std::runtime_error(message);
    }
}

std::string FormatUtf16(std::u16string_view value)
{
    std::ostringstream out;
    out << "size=" << value.size() << ", units=[";
    for (std::size_t index = FIRST_INDEX; index < value.size(); ++index) {
        if (index != FIRST_INDEX) {
            out << ", ";
        }
        out << "0x" << std::uppercase << std::hex << std::setw(UTF16_HEX_WIDTH) << std::setfill('0')
            << static_cast<uint32_t>(value[index]);
    }
    out << "]";
    return out.str();
}

void RequireUtf16Equal(std::u16string_view actual, std::u16string_view expected, char const *message)
{
    if (actual != expected) {
        throw std::runtime_error(std::string(message) + "; actual {" + FormatUtf16(actual) + "}; expected {" +
                                 FormatUtf16(expected) + "}");
    }
}

ExpectedString StringTest(::taihe::string_view input)
{
    return input;
}

ExpectedString CommonStringTest()
{
    try {
        ::taihe::string text("abcdef");
        Require(!text.empty(), "UTF-8 string should not be empty");
        Require(text.size() == UTF8_TEXT_SIZE, "UTF-8 string size should be measured in bytes");
        Require(text.front() == 'a', "UTF-8 string front() returned unexpected character");
        Require(text.back() == 'f', "UTF-8 string back() returned unexpected character");
        Require(text[THIRD_CHAR_INDEX] == 'c', "UTF-8 string operator[] returned unexpected character");
        Require(std::string_view(text.substr(SAMPLE_SUBSTR_OFFSET, UTF8_SUBSTR_SIZE)) == "bcd",
                "UTF-8 string substr() returned unexpected value");

        ::taihe::string appended("ab");
        appended += "cd";
        Require(std::string_view(appended) == "abcd", "UTF-8 string operator+= returned unexpected value");
        Require(std::string_view(::taihe::concat({"ta", "i", "he"})) == "taihe",
                "UTF-8 string concat() returned unexpected value");
        Require(::taihe::string_view("abc") < ::taihe::string_view("abd"),
                "UTF-8 string comparison returned unexpected result");

        ::taihe::common_string_view commonView = text;
        Require(commonView.is_utf8(), "common_string_view from string should be UTF-8");
        Require(!commonView.is_utf16(), "common_string_view from string should not be UTF-16");
        Require(commonView.encoding() == ::taihe::string_encoding::utf8,
                "encoding() should report UTF-8 for UTF-8 common_string_view");
        Require(std::string_view(::taihe::string_view(commonView)) == "abcdef",
                "UTF-8 common_string_view downcast returned unexpected value");

        ::taihe::common_string copiedCommon(commonView);
        Require(copiedCommon.is_utf8(), "copied UTF-8 common_string should stay UTF-8");
        Require(std::string_view(::taihe::string(copiedCommon)) == "abcdef",
                "copied UTF-8 common_string conversion returned unexpected value");

        std::u16string utf16Source {u'a', u'b', u'\u4F60', u'\u597D'};
        ::taihe::u16string utf16Text(utf16Source);

        Require(!utf16Text.empty(), "UTF-16 string should not be empty");
        Require(utf16Text.size() == utf16Source.size(), "UTF-16 string size should be measured in code units");
        Require(utf16Text.front() == u'a', "UTF-16 string front() returned unexpected character");
        Require(utf16Text.back() == u'\u597D', "UTF-16 string back() returned unexpected character");
        Require(utf16Text[THIRD_CHAR_INDEX] == u'\u4F60', "UTF-16 string operator[] returned unexpected character");
        RequireUtf16Equal(std::u16string_view(utf16Text.substr(SAMPLE_SUBSTR_OFFSET, TWO_CODE_UNITS))
                              .substr(FIRST_INDEX, TWO_CODE_UNITS),
                          std::u16string_view(utf16Source).substr(SAMPLE_SUBSTR_OFFSET, TWO_CODE_UNITS),
                          "UTF-16 string substr() returned unexpected value");

        ::taihe::u16string utf16Appended(std::u16string_view(u"ab", TWO_CODE_UNITS));
        utf16Appended += ::taihe::u16string_view(std::u16string_view(u"cd", TWO_CODE_UNITS));
        RequireUtf16Equal(std::u16string_view(utf16Appended), std::u16string_view(u"abcd", FOUR_CODE_UNITS),
                          "UTF-16 string operator+= returned unexpected value");
        ::taihe::u16string utf16Concatenated = ::taihe::concat({
            ::taihe::u16string_view(std::u16string_view(u"ta", TWO_CODE_UNITS)),
            ::taihe::u16string_view(std::u16string_view(u"i", ONE_CODE_UNIT)),
            ::taihe::u16string_view(std::u16string_view(u"he", TWO_CODE_UNITS)),
        });
        RequireUtf16Equal(std::u16string_view(utf16Concatenated), std::u16string_view(u"taihe", FIVE_CODE_UNITS),
                          "UTF-16 string concat() returned unexpected value");

        ::taihe::common_string utf16Common(utf16Source);
        Require(utf16Common.is_utf16(), "common_string from u16string should be UTF-16");
        Require(!utf16Common.is_utf8(), "common_string from u16string should not be UTF-8");
        Require(utf16Common.encoding() == ::taihe::string_encoding::utf16,
                "encoding() should report UTF-16 for UTF-16 common_string");
        RequireUtf16Equal(std::u16string_view(::taihe::u16string_view(utf16Common)), std::u16string_view(utf16Source),
                          "UTF-16 common_string downcast returned unexpected value");

        std::string utf8Source = std::string("hello ") + "\xE4\xBD\xA0\xE5\xA5\xBD";
        std::u16string expectedConvertedUtf16 {u'h', u'e', u'l', u'l', u'o', u' ', u'\u4F60', u'\u597D'};
        ::taihe::common_string utf8Common(utf8Source);
        ::taihe::u16string convertedUtf16(utf8Common);
        RequireUtf16Equal(std::u16string_view(convertedUtf16).substr(FIRST_INDEX, expectedConvertedUtf16.size()),
                          std::u16string_view(expectedConvertedUtf16), "UTF-8 to UTF-16 conversion content mismatch");
        Require(convertedUtf16.size() == CONVERTED_UTF16_SIZE,
                "UTF-8 to UTF-16 conversion should preserve code-unit length");

        ::taihe::common_string movedUtf16Common(std::move(convertedUtf16));
        ::taihe::string convertedUtf8(movedUtf16Common);
        Require(std::string_view(convertedUtf8) == utf8Source, "UTF-16 to UTF-8 conversion should round trip");

        Require(std::string_view(::taihe::to_string(POSITIVE_TO_STRING_VALUE)) == "42",
                "to_string(int) returned unexpected value");
        Require(std::string_view(::taihe::to_string(NEGATIVE_TO_STRING_VALUE)) == "-7",
                "to_string(negative int) returned unexpected value");

        return ::taihe::string("common string test passed");
    } catch (std::exception const &error) {
        return ::taihe::unexpected<::taihe::error>(::taihe::error(error.what()));
    }
}

}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_StringTest(StringTest);
TH_EXPORT_CPP_API_CommonStringTest(CommonStringTest);
// NOLINTEND
