#ifndef METADATA_H
#define METADATA_H

#include <string>
#include "stdexcept"

using namespace taihe;

class MetadataImpl {
public:
  std::string name = "metadate.name";
  std::string value = "metadate.value";
  std::string resource = "metadate.resource";
  int32_t metadataImpl = 21474;

  MetadataImpl() {}

  std::string GetName() {
    return name;
  }

  void SetName(string_view name) {
    this->name = name;
  }

  std::string GetValue() {
    return value;
  }

  void SetValue(string_view value) {
    this->value = value;
  }

  std::string GetResource() {
    return resource;
  }

  void SetResource(string_view resource) {
    this->resource = resource;
  }

  int32_t GetValueId() {
    return metadataImpl;
  }
};

#endif