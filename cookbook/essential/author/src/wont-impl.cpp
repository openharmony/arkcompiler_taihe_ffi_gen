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
#include "ohos.book.store.impl.hpp"
#include "taihe/string.hpp"

using namespace taihe;
using namespace ::ohos::book::store;

// Won't Implement
namespace {
void SaveBookToInternet(string_view url)
{
    TH_THROW(std::runtime_error, "SaveBookToInternet not implemented");
}

void SaveBookToFile(weak::Path p)
{
    TH_THROW(std::runtime_error, "SaveBookToFile not implemented");
}

string uploadBook(Book const &b)
{
    TH_THROW(std::runtime_error, "uploadBook not implemented");
}

void onBookSold()
{
    TH_THROW(std::runtime_error, "onBookSold not implemented");
}

void onNewBook()
{
    TH_THROW(std::runtime_error, "onNewBook not implemented");
}
}  // namespace

TH_EXPORT_CPP_API_SaveBookToInternet(SaveBookToInternet);
TH_EXPORT_CPP_API_SaveBookToFile(SaveBookToFile);
TH_EXPORT_CPP_API_uploadBook(uploadBook);
TH_EXPORT_CPP_API_onBookSold(onBookSold);
TH_EXPORT_CPP_API_onNewBook(onNewBook);
// NOLINTEND
