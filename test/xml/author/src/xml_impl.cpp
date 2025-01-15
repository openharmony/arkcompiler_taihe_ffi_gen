#include "ohos.xml.proj.hpp"
#include "ohos.xml.impl.hpp"
#include "parser_impl.hpp"

ohos::xml::XmlPullParser makeXmlPullParserImpl(
    ohos::xml::BufferType const& buffer,
    ohos::xml::OptString const& encoding)
{
    return taihe::core::make_holder<ExpatParser, ohos::xml::XmlPullParser>(buffer, encoding);
}

TH_EXPORT_CPP_API_makeXmlPullParser(makeXmlPullParserImpl)

ohos::xml::XmlSerializer makeXmlSerializerImpl(
    ohos::xml::BufferType const& buffer,
    ohos::xml::OptString const& encoding)
{
    throw;
}

TH_EXPORT_CPP_API_makeXmlSerializer(makeXmlSerializerImpl)
