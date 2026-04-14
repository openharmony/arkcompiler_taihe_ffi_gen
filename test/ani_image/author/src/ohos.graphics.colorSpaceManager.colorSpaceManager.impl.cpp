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
#include "ohos.graphics.colorSpaceManager.colorSpaceManager.impl.hpp"
#include "ohos.graphics.colorSpaceManager.colorSpaceManager.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace ohos::graphics::colorSpaceManager::colorSpaceManager;

namespace {
ColorSpacePrimaries SRGB_PRIMARIES = {0.64, 0.33, 0.30, 0.60, 0.15, 0.06, 0.3127, 0.3290};

ColorSpacePrimaries DISPLAY_P3_PRIMARIES = {0.68, 0.32, 0.265, 0.69, 0.15, 0.06, 0.3127, 0.3290};

class ColorSpaceManagerImpl {
public:
    ColorSpaceManagerImpl(ColorSpace space, ColorSpacePrimaries const &primaries, double gamma)
        : m_spaceName(space), m_primaries(primaries), m_gamma(gamma)
    {
    }

    ::taihe::expected<ColorSpace, ::taihe::error> getColorSpaceName()
    {
        return this->m_spaceName;
    }

    ::taihe::expected<array<double>, ::taihe::error> getWhitePoint()
    {
        return {this->m_primaries.whitePointX, this->m_primaries.whitePointY};
    }

    ::taihe::expected<double, ::taihe::error> getGamma()
    {
        return this->m_gamma;
    }

private:

private:
    ColorSpace m_spaceName;
    ColorSpacePrimaries m_primaries;
    double m_gamma;
};
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTEND
