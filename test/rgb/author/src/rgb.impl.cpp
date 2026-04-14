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
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <string>
#include <variant>

#include "rgb.base.impl.hpp"
#include "rgb.show.impl.hpp"

using namespace rgb::base;
using namespace rgb::show;
using namespace taihe;

using expected_string = ::taihe::expected<string, ::taihe::error>;
using expected_callback = callback<expected_string(string_view)>;

class Rectangle {
protected:
    float h;
    float w;
    std::string name;

public:
    ::taihe::expected<string, ::taihe::error> getId()
    {
        return name;
    }

    Rectangle(string_view id, float h, float w) : h(h), w(w), name(id)
    {
        auto id_res = getId();
        if (id_res.has_value()) {
            std::cout << id_res.value() << " made" << std::endl;
        }
    }

    ~Rectangle()
    {
        auto id_res = getId();
        if (id_res.has_value()) {
            std::cout << id_res.value() << " deleted" << std::endl;
        }
    }

    ::taihe::expected<float, ::taihe::error> calculateArea()
    {
        return h * w;
    }
};

class ColoredRectangle : public Rectangle {
    ColorOrRGBOrName myColor;

public:
    ColoredRectangle(string_view id, float h, float w, ColorOrRGBOrName const &color)
        : Rectangle(id, h, w), myColor(color)
    {
    }

    ::taihe::expected<ColorOrRGBOrName, ::taihe::error> getColor()
    {
        return myColor;
    }

    ::taihe::expected<void, ::taihe::error> setColor(ColorOrRGBOrName const &color)
    {
        myColor = color;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> show()
    {
        std::string content = "rectangle " + name + ": h = " + std::to_string(h) + ", w = " + std::to_string(w);
        if (auto color_ptr = myColor.get_ptr<ColorOrRGBOrName::tag_t::color>()) {
            std::cout << "\033[" << 30 + (int)*color_ptr << "m" << content << "\033[39m" << std::endl;
        } else if (auto rgb_ptr = myColor.get_ptr<ColorOrRGBOrName::tag_t::rgb>()) {
            std::cout << "\033[38;2;" << (int)rgb_ptr->r << ";" << (int)rgb_ptr->g << ";" << (int)rgb_ptr->b << "m"
                      << content << "\033[39m" << std::endl;
        } else if (auto name_ptr = myColor.get_ptr<ColorOrRGBOrName::tag_t::name>()) {
            std::cout << "(" << *name_ptr << ") " << content << std::endl;
        } else {
            std::cout << content << std::endl;
        }
        return {};
    }
};

::taihe::expected<void, ::taihe::error> copyColor(weak::IColorable dst, weak::IColorable src)
{
    auto src_id = weak::IBase(src)->getId();
    auto dst_id = weak::IBase(dst)->getId();
    if (src_id.has_value() && dst_id.has_value()) {
        std::cout << "copying color from " << src_id.value() << " to " << dst_id.value() << "." << std::endl;
    }
    auto color = src->getColor();
    if (color.has_value()) {
        dst->setColor(color.value());
    }
    return {};
}

::taihe::expected<IShape, ::taihe::error> makeRectangle(string_view id, float h, float w)
{
    return taihe::make_holder<Rectangle, IShape>(id, h, w);
}

::taihe::expected<IShowable, ::taihe::error> makeColoredRectangle(string_view id, ColorOrRGBOrName const &c, float h,
                                                                  float w)
{
    return taihe::make_holder<ColoredRectangle, IShowable>(id, h, w, c);
}

::taihe::expected<array<IBase>, ::taihe::error> exchangeArr(array_view<IBase> dst, array_view<IBase> src)
{
    auto n = std::min(dst.size(), src.size());
    auto res = array<IBase>(copy_data, dst.data(), n);
    for (std::size_t i = 0; i < n; i++) {
        dst[i] = src[i];
    }
    return res;
}

::taihe::expected<optional<string>, ::taihe::error> getIdFromOptional(optional_view<IBase> box)
{
    if (box) {
        auto id = (*box)->getId();
        if (id.has_value()) {
            return optional<string>(std::in_place, id.value());
        } else {
            return optional<string>(std::nullopt);
        }
    } else {
        return optional<string>(std::nullopt);
    }
}

::taihe::expected<vector<IBase>, ::taihe::error> makeVec(array_view<IBase> src)
{
    size_t n = src.size();
    vector<IBase> res;
    for (std::size_t i = 0; i < n; i++) {
        res.emplace_back(src[i]);
    }
    return res;
}

::taihe::expected<void, ::taihe::error> fillVec(array_view<IBase> src, vector_view<IBase> dst)
{
    size_t n = src.size();
    for (std::size_t i = 0; i < n; i++) {
        dst.emplace_back(src[i]);
    }
    return {};
}

::taihe::expected<map<string, IBase>, ::taihe::error> makeMap(array_view<string> keys, array_view<IBase> src)
{
    size_t n = std::min(keys.size(), src.size());
    map<string, IBase> res;
    for (std::size_t i = 0; i < n; i++) {
        res.emplace(keys[i], src[i]);
    }
    return res;
}

::taihe::expected<void, ::taihe::error> fillMap(array_view<string> keys, array_view<IBase> src,
                                                map_view<string, IBase> dst)
{
    size_t n = std::min(keys.size(), src.size());
    for (std::size_t i = 0; i < n; i++) {
        dst.emplace(keys[i], src[i]);
    }
    return {};
}

::taihe::expected<set<string>, ::taihe::error> makeSet(array_view<string> src)
{
    size_t n = src.size();
    set<string> res;
    for (std::size_t i = 0; i < n; i++) {
        res.emplace(src[i]);
    }
    return res;
}

::taihe::expected<void, ::taihe::error> fillSet(array_view<string> src, set_view<string> dst)
{
    size_t n = src.size();
    for (std::size_t i = 0; i < n; i++) {
        dst.emplace(src[i]);
    }
    return {};
}

struct CallbackImplInner {
    callback<::taihe::expected<string, ::taihe::error>(string_view, string_view)> f;
    string s;

    CallbackImplInner(callback_view<::taihe::expected<string, ::taihe::error>(string_view, string_view)> f,
                      string_view s)
        : f(f), s(s)
    {
    }

    ::taihe::expected<string, ::taihe::error> operator()(string_view x)
    {
        return f(s, x);
    }
};

struct CallbackImplOuter {
    callback<::taihe::expected<string, ::taihe::error>(string_view, string_view)> f;

    CallbackImplOuter(callback_view<::taihe::expected<string, ::taihe::error>(string_view, string_view)> f) : f(f)
    {
    }

    ::taihe::expected<callback<::taihe::expected<string, ::taihe::error>(string_view)>, ::taihe::error> operator()(
        string_view s)
    {
        return make_holder<CallbackImplInner, callback<::taihe::expected<string, ::taihe::error>(string_view)>>(f, s);
    }
};

::taihe::expected<callback<::taihe::expected<expected_callback, ::taihe::error>(string_view)>, ::taihe::error> currying(
    callback_view<::taihe::expected<string, ::taihe::error>(string_view, string_view)> f)
{
    return make_holder<CallbackImplOuter, callback<::taihe::expected<expected_callback, ::taihe::error>(string_view)>>(
        f);
}

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_copyColor(copyColor);
TH_EXPORT_CPP_API_makeRectangle(makeRectangle);
TH_EXPORT_CPP_API_makeColoredRectangle(makeColoredRectangle);
TH_EXPORT_CPP_API_exchangeArr(exchangeArr);
TH_EXPORT_CPP_API_getIdFromOptional(getIdFromOptional);
TH_EXPORT_CPP_API_makeVec(makeVec);
TH_EXPORT_CPP_API_fillVec(fillVec);
TH_EXPORT_CPP_API_makeMap(makeMap);
TH_EXPORT_CPP_API_fillMap(fillMap);
TH_EXPORT_CPP_API_makeSet(makeSet);
TH_EXPORT_CPP_API_fillSet(fillSet);
TH_EXPORT_CPP_API_currying(currying);
// NOLINTEND
