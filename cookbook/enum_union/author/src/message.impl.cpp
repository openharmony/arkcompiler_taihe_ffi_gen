#include "message.proj.hpp"
#include "message.impl.hpp"
#include "taihe/runtime.hpp"
#include "stdexcept"
#include <iostream>

using namespace taihe;
using namespace message;

namespace {

Message createTextMessage(string_view str) {
    return {MessageType::key_t::Text, MessageData::make_textVal(str)};
}

Message createNumberMessage(int64_t num) {
    return {MessageType::key_t::Number, MessageData::make_numVal(num)};
}

void processMessage(Message const& msg) {
    switch(msg.type.get_key()) {
        case MessageType::key_t::Text:
            std::cout << "text: " << msg.data.get_textVal_ref() << std::endl;
            break;
        case MessageType::key_t::Number:
            std::cout << "num: " << msg.data.get_numVal_ref() << std::endl;
            break;
    }
}
}  // namespace

TH_EXPORT_CPP_API_createTextMessage(createTextMessage);
TH_EXPORT_CPP_API_createNumberMessage(createNumberMessage);
TH_EXPORT_CPP_API_processMessage(processMessage);
