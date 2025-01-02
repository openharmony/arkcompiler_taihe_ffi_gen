#include "ohos.xml.proj.hpp"
#include "ohos.xml.impl.hpp"
#include "expat.h"

struct XmlSerializer {};

ohos::xml::XmlSerializer makeXmlSerializerImpl(ohos::xml::BufferType const& buffer, ohos::xml::OptString const& encoding) {
    // ...
}

struct XmlPullParser {};

ohos::xml::XmlPullParser makeXmlPullParserImpl(ohos::xml::BufferType const& buffer, ohos::xml::OptString const& encoding) {
    // ...
}

TH_EXPORT_CPP_API_makeXmlPullParser(makeXmlPullParserImpl)
TH_EXPORT_CPP_API_makeXmlSerializer(makeXmlSerializerImpl)
