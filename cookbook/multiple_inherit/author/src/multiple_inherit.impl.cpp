#include "multiple_inherit.impl.hpp"
#include <iostream>
#include "multiple_inherit.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
class IBaseImpl {
public:
  IBaseImpl() {}

  void baseFunc() {
    std::cout << "IBase" << std::endl;
  }
};

class IColorableImpl {
public:
  IColorableImpl() : m_color("None") {}

  IColorableImpl(::taihe::string color) : m_color(color) {}

  ::taihe::string getColor() {
    return this->m_color;
  }

  void baseFunc() {
    std::cout << "IColor" << std::endl;
  }

private:
  ::taihe::string m_color;
};

class IShapeImpl {
public:
  IShapeImpl() : m_shape("None") {}

  IShapeImpl(::taihe::string shape) : m_shape(shape) {}

  ::taihe::string getShape() {
    return this->m_shape;
  }

  void baseFunc() {
    std::cout << "IShape" << std::endl;
  }

private:
  ::taihe::string m_shape;
};

class IRectImpl {
public:
  IRectImpl() : m_color("None"), m_shape("None") {}

  IRectImpl(::taihe::string color, ::taihe::string shape)
      : m_color(color), m_shape(shape) {}

  ::taihe::string getMessage() {
    return "It's Rect";
  }

  ::taihe::string getColor() {
    return this->m_color;
  }

  void baseFunc() {
    std::cout << "IRect" << std::endl;
  }

  ::taihe::string getShape() {
    return this->m_shape;
  }

private:
  ::taihe::string m_color;
  ::taihe::string m_shape;
};

::multiple_inherit::IColorable createIColorable(::taihe::string_view color) {
  return taihe::make_holder<IColorableImpl, ::multiple_inherit::IColorable>(
      color);
}

::multiple_inherit::IShape createIShape(::taihe::string_view shape) {
  return taihe::make_holder<IShapeImpl, ::multiple_inherit::IShape>(shape);
}

::multiple_inherit::IRect createIRect(::taihe::string_view color,
                                      ::taihe::string_view shape) {
  return taihe::make_holder<IRectImpl, ::multiple_inherit::IRect>(color, shape);
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_createIColorable(createIColorable);
TH_EXPORT_CPP_API_createIShape(createIShape);
TH_EXPORT_CPP_API_createIRect(createIRect);
// NOLINTEND
