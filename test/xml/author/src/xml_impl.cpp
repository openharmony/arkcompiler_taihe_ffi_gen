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

#include "ohos.xml.impl.hpp"
#include "parser_impl.hpp"

using namespace taihe;
using namespace ohos::xml;

XmlPullParser makeXmlPullParserImpl(BufferType const &buffer, optional_view<string> encoding)
{
    return make_holder<ExpatParser, XmlPullParser>(buffer, encoding);
}

XmlSerializer makeXmlSerializerImpl(BufferType const &buffer, optional_view<string> encoding)
{
    throw;
}

// NOLINTBEGIN
TH_EXPORT_CPP_API_makeXmlPullParser(makeXmlPullParserImpl);
TH_EXPORT_CPP_API_makeXmlSerializer(makeXmlSerializerImpl);
// NOLINTEND
