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

class Rectangle {
protected:
  float h;
  float w;
  std::string name;

public:
  string getId() {
    return name;
  }

  Rectangle(string_view id, float h, float w) : h(h), w(w), name(id) {
    std::cout << getId() << " made" << std::endl;
  }

  ~Rectangle() {
    std::cout << getId() << " deleted" << std::endl;
  }

  float calculateArea() {
    return h * w;
  }
};

class ColoredRectangle : public Rectangle {
  ColorOrRGBOrName myColor;

public:
  ColoredRectangle(string_view id, float h, float w,
                   ColorOrRGBOrName const &color)
      : Rectangle(id, h, w), myColor(color) {}

  ColorOrRGBOrName getColor() {
    return myColor;
  }

  void setColor(ColorOrRGBOrName const &color) {
    myColor = color;
  }

  void show() {
    std::string content = "rectangle " + name + ": h = " + std::to_string(h) +
                          ", w = " + std::to_string(w);
    if (auto color_ptr = myColor.get_ptr<ColorOrRGBOrName::tag_t::color>()) {
      std::cout << "\033[" << 30 + (int)*color_ptr << "m" << content
                << "\033[39m" << std::endl;
    } else if (auto rgb_ptr = myColor.get_ptr<ColorOrRGBOrName::tag_t::rgb>()) {
      std::cout << "\033[38;2;" << (int)rgb_ptr->r << ";" << (int)rgb_ptr->g
                << ";" << (int)rgb_ptr->b << "m" << content << "\033[39m"
                << std::endl;
    } else if (auto name_ptr =
                   myColor.get_ptr<ColorOrRGBOrName::tag_t::name>()) {
      std::cout << "(" << *name_ptr << ") " << content << std::endl;
    } else {
      std::cout << content << std::endl;
    }
  }
};

void copyColor(weak::IColorable dst, weak::IColorable src) {
  std::cout << "copying color from " << weak::IBase(src)->getId() << " to "
            << weak::IBase(dst)->getId() << "." << std::endl;
  dst->setColor(src->getColor());
}

IShape makeRectangle(string_view id, float h, float w) {
  return taihe::make_holder<Rectangle, IShape>(id, h, w);
}

IShowable makeColoredRectangle(string_view id, ColorOrRGBOrName const &c,
                               float h, float w) {
  return taihe::make_holder<ColoredRectangle, IShowable>(id, h, w, c);
}

array<IBase> exchangeArr(array_view<IBase> dst, array_view<IBase> src) {
  auto n = std::min(dst.size(), src.size());
  auto res = array<IBase>(copy_data, dst.data(), n);
  for (std::size_t i = 0; i < n; i++) {
    dst[i] = src[i];
  }
  return res;
}

optional<string> getIdFromOptional(optional_view<IBase> box) {
  if (box) {
    return optional<string>(std::in_place, (*box)->getId());
  } else {
    return optional<string>(std::nullopt);
  }
}

vector<IBase> makeVec(array_view<IBase> src) {
  size_t n = src.size();
  vector<IBase> res;
  for (std::size_t i = 0; i < n; i++) {
    res.emplace_back(src[i]);
  }
  return res;
}

void fillVec(array_view<IBase> src, vector_view<IBase> dst) {
  size_t n = src.size();
  for (std::size_t i = 0; i < n; i++) {
    dst.emplace_back(src[i]);
  }
}

map<string, IBase> makeMap(array_view<string> keys, array_view<IBase> src) {
  size_t n = std::min(keys.size(), src.size());
  map<string, IBase> res;
  for (std::size_t i = 0; i < n; i++) {
    res.emplace(keys[i], src[i]);
  }
  return res;
}

void fillMap(array_view<string> keys, array_view<IBase> src,
             map_view<string, IBase> dst) {
  size_t n = std::min(keys.size(), src.size());
  for (std::size_t i = 0; i < n; i++) {
    dst.emplace(keys[i], src[i]);
  }
}

set<string> makeSet(array_view<string> src) {
  size_t n = src.size();
  set<string> res;
  for (std::size_t i = 0; i < n; i++) {
    res.emplace(src[i]);
  }
  return res;
}

void fillSet(array_view<string> src, set_view<string> dst) {
  size_t n = src.size();
  for (std::size_t i = 0; i < n; i++) {
    dst.emplace(src[i]);
  }
}

struct CallbackImplInner {
  callback<string(string_view, string_view)> f;
  string s;

  CallbackImplInner(callback_view<string(string_view, string_view)> f,
                    string_view s)
      : f(f), s(s) {}

  string operator()(string_view x) {
    return f(s, x);
  }
};

struct CallbackImplOuter {
  callback<string(string_view, string_view)> f;

  CallbackImplOuter(callback_view<string(string_view, string_view)> f) : f(f) {}

  callback<string(string_view)> operator()(string_view s) {
    return make_holder<CallbackImplInner, callback<string(string_view)>>(f, s);
  }
};

callback<callback<string(string_view)>(string_view)> currying(
    callback_view<string(string_view, string_view)> f) {
  return make_holder<CallbackImplOuter,
                     callback<callback<string(string_view)>(string_view)>>(f);
}

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
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
