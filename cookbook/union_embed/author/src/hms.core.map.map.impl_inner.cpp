#include <cstdlib>

#include "core/array.hpp"
#include "core/runtime.hpp"
#include "core/string.hpp"
#include "hms.core.map.map_inner.Resource.proj.2.hpp"
#include "hms.core.map.map_inner.icons_type.proj.1.hpp"
#include "hms.core.map.map_inner.impl.hpp"
#include "hms.core.map.map_inner.map_inner.proj.2.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe;
namespace {
class Resource {
 public:
  void foo(int32_t a) {
    std::cout << "type_Resource: " << "foo: " << a << std::endl;
  }
};
class map_inner {
 public:
  string getId() { return "ID got"; }
  int32_t getZIndex() { return 5; }
  int32_t getMaxZoom() { return 10; }
  int32_t getMinZoom() { return 0; }
  int32_t setIcons_sync(
      array_view<::hms::core::map::map_inner::icons_type> icons) {
    for (const auto& element : icons) {
      switch (element.get_tag()) {
        case ::hms::core::map::map_inner::icons_type::tag_t::type_string:
          std::cout << "type_string: " << element.get_type_string_ref()
                    << std::endl;
          break;
        case ::hms::core::map::map_inner::icons_type::tag_t::type_Resource:
          element.get_type_Resource_ref()->foo(0);
          break;
        case ::hms::core::map::map_inner::icons_type::tag_t::type_Image: {
          auto& obj = element.get_type_Image_ref();
          ani_class cls;
          ani_boolean res;
          ani_env* env = get_env();
          env->FindClass("L@ohos/multimedia/image/Image_inner;", &cls);
          env->Object_InstanceOf((ani_object)obj, cls, &res);
          std::cout << "type_Image: " << (int)res << std::endl;
          if (!res) {
            abort();
          }
          break;
        }
      }
    }
    return 0;
  }
  void setPositions(
      array_view<array<::hms::core::map::map_inner::Resource>> positions) {
    for (int i = 0; i < positions.size(); i++) {
      for (int j = 0; j < positions[i].size(); j++) {
        positions[i][j]->foo(100);
      }
    }
  }
};
::hms::core::map::map_inner::Resource createResource() {
  return make_holder<Resource, ::hms::core::map::map_inner::Resource>();
}
::hms::core::map::map_inner::map_inner make_map_inner() {
  return make_holder<map_inner, ::hms::core::map::map_inner::map_inner>();
}
}  // namespace
TH_EXPORT_CPP_API_createResource(createResource);
TH_EXPORT_CPP_API_make_map_inner(make_map_inner);
