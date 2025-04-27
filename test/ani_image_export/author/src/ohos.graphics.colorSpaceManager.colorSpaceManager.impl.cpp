#include "ohos.graphics.colorSpaceManager.colorSpaceManager.proj.hpp"
#include "ohos.graphics.colorSpaceManager.colorSpaceManager.impl.hpp"
#include "taihe/runtime.hpp"
#include "stdexcept"

using namespace taihe;
using namespace ohos::graphics::colorSpaceManager::colorSpaceManager;

namespace {
ColorSpacePrimaries SRGB_PRIMARIES = {
    0.64, 0.33,
    0.30, 0.60,
    0.15, 0.06,
    0.3127, 0.3290
};

ColorSpacePrimaries DISPLAY_P3_PRIMARIES = {
    0.68, 0.32,
    0.265, 0.69,
    0.15, 0.06,
    0.3127, 0.3290
};

class ColorSpaceManagerImpl {
public:
    ColorSpaceManagerImpl(ColorSpace space, const ColorSpacePrimaries& primaries, double gamma)
    : m_spaceName(space), m_primaries(primaries), m_gamma(gamma) {}

    ColorSpace getColorSpaceName() {
        return this->m_spaceName;
    }

    array<double> getWhitePoint() {
        return {this->m_primaries.whitePointX, this->m_primaries.whitePointY};
    }

    double getGamma() {
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
// NOLINTBEGIN
// NOLINTEND
