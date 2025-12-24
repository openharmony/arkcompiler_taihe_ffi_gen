/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
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

// This file is a test file.
// NOLINTBEGIN
#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>

#include "ohos.xml.user.hpp"

using namespace taihe;
using namespace ohos::xml;

struct CallbackTag {
    CallbackTag()
    {
        std::cout << "CallbackTag constructor" << std::endl;
    }

    ~CallbackTag()
    {
        std::cout << "CallbackTag destructor" << std::endl;
    }

    bool operator()(string_view name, string_view value)
    {
        std::cout << "(tag) " << name << ": " << value << std::endl;
        return true;
    }
};

struct CallbackAttribute {
    CallbackAttribute()
    {
        std::cout << "CallbackAttribute constructor" << std::endl;
    }

    ~CallbackAttribute()
    {
        std::cout << "CallbackAttribute destructor" << std::endl;
    }

    bool operator()(string_view name, string_view value)
    {
        std::cout << "(attribute) " << name << ": " << value << std::endl;
        return true;
    }
};

int main(int argc, char **argv)
{
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
        .tagValueCallbackFunction = {std::in_place,
                                     make_holder<CallbackTag, callback<bool(string_view, string_view)>>()},
        .attributeValueCallbackFunction = {std::in_place,
                                           make_holder<CallbackAttribute, callback<bool(string_view, string_view)>>()},
    });
}

// NOLINTEND
