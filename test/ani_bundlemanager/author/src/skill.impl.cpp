#include "skill.impl.hpp"
#include <iostream>
#include "skill.h"
#include "skill.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace skill;

namespace {
// To be implemented.

class SkillUriImpl {
public:
  int32_t skillUriImpl = 21474;

  SkillUriImpl() {}

  string GetScheme() {
    return "SkillUriImpl::getScheme";
  }

  string GetHost() {
    return "SkillUriImpl::getHost";
  }

  int32_t GetPort() {
    return skillUriImpl;
  }

  string GetPath() {
    return "SkillUriImpl::getPath";
  }

  string GetPathStartWith() {
    return "SkillUriImpl::getPathStartWith";
  }

  string GetPathRegex() {
    return "SkillUriImpl::getPathRegex";
  }

  string GetType() {
    return "SkillUriImpl::getType";
  }

  string GetUtd() {
    return "SkillUriImpl::getUtd";
  }

  int32_t GetMaxFileSupported() {
    return skillUriImpl;
  }

  string GetLinkFeature() {
    return "SkillUriImpl::getLinkFeature";
  }
};

Skill GetSkill() {
  return make_holder<SkillImpl, Skill>();
}

SkillUri GetSkillUri() {
  return make_holder<SkillUriImpl, SkillUri>();
}
}  // namespace

TH_EXPORT_CPP_API_GetSkill(GetSkill);
TH_EXPORT_CPP_API_GetSkillUri(GetSkillUri);