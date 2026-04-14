/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// This file is a test file.
// NOLINTBEGIN
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

    SkillUriImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetScheme()
    {
        return "SkillUriImpl::getScheme";
    }

    ::taihe::expected<string, ::taihe::error> GetHost()
    {
        return "SkillUriImpl::getHost";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetPort()
    {
        return skillUriImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetPath()
    {
        return "SkillUriImpl::getPath";
    }

    ::taihe::expected<string, ::taihe::error> GetPathStartWith()
    {
        return "SkillUriImpl::getPathStartWith";
    }

    ::taihe::expected<string, ::taihe::error> GetPathRegex()
    {
        return "SkillUriImpl::getPathRegex";
    }

    ::taihe::expected<string, ::taihe::error> GetType()
    {
        return "SkillUriImpl::getType";
    }

    ::taihe::expected<string, ::taihe::error> GetUtd()
    {
        return "SkillUriImpl::getUtd";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetMaxFileSupported()
    {
        return skillUriImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetLinkFeature()
    {
        return "SkillUriImpl::getLinkFeature";
    }
};

::taihe::expected<Skill, ::taihe::error> GetSkill()
{
    return make_holder<SkillImpl, Skill>();
}

::taihe::expected<SkillUri, ::taihe::error> GetSkillUri()
{
    return make_holder<SkillUriImpl, SkillUri>();
}
}  // namespace

TH_EXPORT_CPP_API_GetSkill(GetSkill);
TH_EXPORT_CPP_API_GetSkillUri(GetSkillUri);
// NOLINTEND
