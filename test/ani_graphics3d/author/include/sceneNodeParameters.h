#ifndef SCENENODEPARAMETERS_H
#define SCENENODEPARAMETERS_H

#include <string>
#include "stdexcept"

using namespace taihe;

class SceneNodeParametersImpl {
public:
  string name = "name";
  optional<string> path;

  SceneNodeParametersImpl() {}

  string GetName() {
    return name;
  }

  void SetName(string_view name) {
    this->name = name;
  }

  optional<string> GetPath() {
    return path;
  }

  void SetPath(optional_view<string> path) {
    this->path = path;
  }
};
#endif