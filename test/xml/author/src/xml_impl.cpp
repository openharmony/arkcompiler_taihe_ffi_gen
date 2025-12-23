#include "ohos.xml.impl.hpp"
#include "parser_impl.hpp"

using namespace taihe;
using namespace ohos::xml;

XmlPullParser makeXmlPullParserImpl(BufferType const &buffer,
                                    optional_view<string> encoding) {
  return make_holder<ExpatParser, XmlPullParser>(buffer, encoding);
}

XmlSerializer makeXmlSerializerImpl(BufferType const &buffer,
                                    optional_view<string> encoding) {
  throw;
}

// NOLINTBEGIN
TH_EXPORT_CPP_API_makeXmlPullParser(makeXmlPullParserImpl);
TH_EXPORT_CPP_API_makeXmlSerializer(makeXmlSerializerImpl);
// NOLINTEND
