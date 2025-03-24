#include "ohos.xml.proj.hpp"
#include "ohos.xml.impl.hpp"
#include "parser_impl.hpp"

using namespace taihe::core;
using namespace ohos::xml;

XmlPullParser makeXmlPullParserImpl(BufferType const& buffer, optional_view<string> encoding) {
    return make_holder<ExpatParser, XmlPullParser>(buffer, encoding);
}

TH_EXPORT_CPP_API_makeXmlPullParser(makeXmlPullParserImpl);

XmlSerializer makeXmlSerializerImpl(BufferType const& buffer, optional_view<string> encoding) {
    throw;
}

TH_EXPORT_CPP_API_makeXmlSerializer(makeXmlSerializerImpl);
