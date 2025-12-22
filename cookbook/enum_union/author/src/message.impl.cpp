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

#include "message.impl.hpp"
#include <iostream>
#include "message.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace message;

namespace {

Message createTextMessage(string_view str) {
  return {MessageType::key_t::Text, MessageData::make_textVal(str)};
}

Message createNumberMessage(int64_t num) {
  return {MessageType::key_t::Num, MessageData::make_numVal(num)};
}

void processMessage(Message const &msg) {
  switch (msg.type.get_key()) {
  case MessageType::key_t::Text:
    std::cout << "text: " << msg.data.get_textVal_ref() << std::endl;
    break;
  case MessageType::key_t::Num:
    std::cout << "num: " << msg.data.get_numVal_ref() << std::endl;
    break;
  }
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_createTextMessage(createTextMessage);
TH_EXPORT_CPP_API_createNumberMessage(createNumberMessage);
TH_EXPORT_CPP_API_processMessage(processMessage);
// NOLINTEND
