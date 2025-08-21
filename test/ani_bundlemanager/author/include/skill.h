#ifndef SKILL_H
#define SKILL_H

#include <string>
#include "stdexcept"

using namespace taihe;

class SkillImpl {
public:
  SkillImpl() {}

  array<string> GetActions() {
    array<string> str = {"SkillImpl::getActions"};
    return str;
  }

  array<string> GetEntities() {
    array<string> str = {"SkillImpl::getEntities"};
    return str;
  }

  bool GetdomainVerify() {
    return true;
  }
};

#endif