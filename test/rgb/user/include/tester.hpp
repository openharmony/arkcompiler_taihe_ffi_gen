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
#include <stdarg.h>
#include <cstddef>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

struct TestResult {
    std::string test_name;
    std::optional<std::string> error_message;
};

class Tester {
    std::vector<TestResult> results;

public:
    static void assert(bool condition, char const *msg, ...)
    {
        if (condition) {
            return;
        }
        char buffer[1024];
        va_list args;
        va_start(args, msg);
        vsnprintf(buffer, sizeof(buffer), msg, args);
        va_end(args);
        throw std::runtime_error(buffer);
    }

    void run(std::string_view test_name, void (*test_func)())
    {
        std::optional<std::string> error_message;
        try {
            test_func();
        } catch (std::exception const &e) {
            error_message = e.what();
        } catch (...) {
            error_message = "Unknown error";
        }

        if (error_message.has_value()) {
            std::cout << ">> " << "Test " << test_name << " failed: " << error_message.value() << std::endl;
        } else {
            std::cout << ">> " << "Test " << test_name << " passed." << std::endl;
        }

        results.push_back({std::string(test_name), error_message});
    }

    int report() const
    {
        size_t failed = 0;

        for (auto const &result : results) {
            failed += result.error_message.has_value();
        }

        if (failed == 0) {
            std::cout << ">> " << "All tests passed." << std::endl;
            return 0;
        } else {
            std::cout << ">> " << failed << " test(s) failed." << std::endl;
            return 1;
        }
    }
};

// NOLINTEND
