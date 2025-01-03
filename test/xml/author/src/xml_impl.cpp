#include "ohos.xml.proj.hpp"
#include "ohos.xml.impl.hpp"
#include "parser_impl.hpp"

ohos::xml::XmlSerializer makeXmlSerializerImpl(
    ohos::xml::BufferType const& buffer,
    ohos::xml::OptString const& encoding)
{
    throw;
}

ohos::xml::XmlPullParser makeXmlPullParserImpl(
    ohos::xml::BufferType const& buffer,
    ohos::xml::OptString const& encoding)
{
    return taihe::core::new_instance<ohos::xml::XmlPullParser, ExpatParser>(buffer, encoding);
}

TH_EXPORT_CPP_API_makeXmlPullParser(makeXmlPullParserImpl)
TH_EXPORT_CPP_API_makeXmlSerializer(makeXmlSerializerImpl)
