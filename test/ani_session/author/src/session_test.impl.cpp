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
#include "session_test.impl.hpp"

#include <cstdint>
#include <iostream>

#include "session_test.IfaceD.proj.2.hpp"
#include "session_test.IfaceE.proj.2.hpp"
#include "session_test.session_type.proj.1.hpp"
#include "stdexcept"
#include "taihe/callback.hpp"
#include "taihe/runtime.hpp"
#include "taihe/string.hpp"

using namespace taihe;

namespace {
class IfaceA {
public:
    ::taihe::expected<void, ::taihe::error> func_a()
    {
        throw std::runtime_error("Function IfaceA::func_a Not implemented");
        return {};
    }
};

class IfaceB {
public:
    ::taihe::expected<void, ::taihe::error> func_b()
    {
        throw std::runtime_error("Function IfaceB::func_b Not implemented");
        return {};
    }

    ::taihe::expected<void, ::taihe::error> func_a()
    {
        throw std::runtime_error("Function IfaceB::func_a Not implemented");
        return {};
    }
};

class IfaceC {
public:
    ::taihe::expected<void, ::taihe::error> func_c()
    {
        throw std::runtime_error("Function IfaceC::func_c Not implemented");
        return {};
    }

    ::taihe::expected<void, ::taihe::error> func_a()
    {
        throw std::runtime_error("Function IfaceC::func_a Not implemented");
        return {};
    }
};

class IfaceD {
    string name_ {"IfaceD"};

public:
    ::taihe::expected<string, ::taihe::error> func_d()
    {
        return "d";
    }

    ::taihe::expected<string, ::taihe::error> func_b()
    {
        return "b";
    }

    ::taihe::expected<string, ::taihe::error> func_a()
    {
        return "a";
    }

    ::taihe::expected<string, ::taihe::error> func_c()
    {
        return "c";
    }

    ::taihe::expected<string, ::taihe::error> getName()
    {
        return name_;
    }

    ::taihe::expected<void, ::taihe::error> setName(string_view name)
    {
        name_ = name;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> onSet(callback_view<::taihe::expected<void, ::taihe::error>()> a)
    {
        a();
        std::cout << "IfaceD::onSet" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> offSet(callback_view<::taihe::expected<void, ::taihe::error>()> a)
    {
        a();
        std::cout << "IfaceD::offSet" << std::endl;
        return {};
    }
};

::taihe::expected<::session_test::IfaceD, ::taihe::error> getIfaceD()
{
    return make_holder<IfaceD, ::session_test::IfaceD>();
}

class IfaceE {
public:
    ::taihe::expected<string, ::taihe::error> func_e()
    {
        return "ee";
    }

    ::taihe::expected<string, ::taihe::error> func_b()
    {
        return "bb";
    }

    ::taihe::expected<string, ::taihe::error> func_a()
    {
        return "aa";
    }

    ::taihe::expected<string, ::taihe::error> func_c()
    {
        return "cc";
    }
};

::taihe::expected<::session_test::IfaceE, ::taihe::error> getIfaceE()
{
    return make_holder<IfaceE, ::session_test::IfaceE>();
}

class Session {
public:
    ::taihe::expected<void, ::taihe::error> beginConfig()
    {
        throw std::runtime_error("Function Session::beginConfig Not implemented");
        return {};
    }
};

class PhotoSession {
public:
    ::taihe::expected<bool, ::taihe::error> canPreconfig()
    {
        return true;
    }

    ::taihe::expected<void, ::taihe::error> beginConfig()
    {
        std::cout << "PhotoSession" << std::endl;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> func_a()
    {
        std::cout << "func_a in PhotoSession" << std::endl;
        return "psa";
    }

    ::taihe::expected<string, ::taihe::error> func_c()
    {
        std::cout << "func_c in PhotoSession" << std::endl;
        return "psc";
    }
};

class VideoSession {
public:
    ::taihe::expected<bool, ::taihe::error> canPreconfig()
    {
        return true;
    }

    ::taihe::expected<void, ::taihe::error> beginConfig()
    {
        std::cout << "VideoSession" << std::endl;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> func_a()
    {
        std::cout << "func_a in VideoSession" << std::endl;
        return "vsa";
    }

    ::taihe::expected<string, ::taihe::error> func_c()
    {
        std::cout << "func_c in VideoSession" << std::endl;
        return "vsc";
    }
};

::taihe::expected<::session_test::session_type, ::taihe::error> getSession(int32_t ty)
{
    if (ty == 1) {
        return ::session_test::session_type::make_ps(make_holder<PhotoSession, ::session_test::PhotoSession>());
    } else {
        return ::session_test::session_type::make_vs(make_holder<VideoSession, ::session_test::VideoSession>());
    }
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_getIfaceD(getIfaceD);
TH_EXPORT_CPP_API_getIfaceE(getIfaceE);
TH_EXPORT_CPP_API_getSession(getSession);
// NOLINTEND
