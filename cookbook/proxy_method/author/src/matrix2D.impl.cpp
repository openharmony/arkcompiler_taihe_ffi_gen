#include <cstdint>
#include <iostream>

#include "core/optional.hpp"
#include "matrix2D__.Matrix2D.proj.1.hpp"
#include "matrix2D__.impl.hpp"
using namespace taihe::core;
namespace {

::matrix2D__::Matrix2D identity(::matrix2D__::Matrix2D const& thiz) {
  return ::matrix2D__::Matrix2D{
      optional<int32_t>::make(2), optional<int32_t>::make(2),
      optional<int32_t>::make(0), optional<int32_t>::make(0),
      optional<int32_t>::make(0), optional<int32_t>::make(0)};
}
::matrix2D__::Matrix2D invert(::matrix2D__::Matrix2D const& thiz) {
  if (*thiz.scaleX != 0 || *thiz.scaleY != 0) {
    int32_t scaleX = 1 / *thiz.scaleX;
    int32_t scaleY = 1 / *thiz.scaleY;
    int32_t rotateX = -*thiz.rotateX;
    int32_t rotateY = -*thiz.rotateY;
    int32_t translateX = -*thiz.translateX;
    int32_t translateY = -*thiz.translateY;
    return ::matrix2D__::Matrix2D{optional<int32_t>::make(scaleX),
                                  optional<int32_t>::make(scaleY),
                                  optional<int32_t>::make(rotateX),
                                  optional<int32_t>::make(rotateY),
                                  optional<int32_t>::make(translateX),
                                  optional<int32_t>::make(translateY)};
  } else {
    return thiz;
  }
}
::matrix2D__::Matrix2D multiply(::matrix2D__::Matrix2D const& thiz,
                                optional_view<::matrix2D__::Matrix2D> other) {
  if (!other) {
    return thiz;
  }
  ::matrix2D__::Matrix2D result = ::matrix2D__::Matrix2D();
  result.scaleX = optional<int32_t>::make(*thiz.scaleX * *other->scaleX);
  result.scaleY = optional<int32_t>::make(*thiz.scaleY * *other->scaleY);
  result.rotateX = optional<int32_t>::make(*thiz.rotateX + *other->rotateX);
  result.rotateY = optional<int32_t>::make(*thiz.rotateY + *other->rotateY);
  result.translateX =
      optional<int32_t>::make(*thiz.translateX + *other->translateX);
  result.translateY =
      optional<int32_t>::make(*thiz.translateY + *other->translateY);
  return result;
}
::matrix2D__::Matrix2D rotate(::matrix2D__::Matrix2D const& thiz,
                              optional_view<int32_t> rx,
                              optional_view<int32_t> ry) {
  if (!rx || !ry) {
    return thiz;
  }
  ::matrix2D__::Matrix2D result = ::matrix2D__::Matrix2D();
  result.rotateX = optional<int32_t>::make(*thiz.rotateX + *rx);
  result.rotateY = optional<int32_t>::make(*thiz.rotateY + *ry);
  result.scaleX = thiz.scaleX;
  result.scaleY = thiz.scaleY;
  result.translateX = thiz.translateX;
  result.translateY = thiz.translateY;
  return result;
}
::matrix2D__::Matrix2D translate(::matrix2D__::Matrix2D const& thiz,
                                 optional_view<int32_t> tx,
                                 optional_view<int32_t> ty) {
  if (!tx || !ty) {
    return thiz;
  }
  ::matrix2D__::Matrix2D result = ::matrix2D__::Matrix2D();
  result.translateX = optional<int32_t>::make(*thiz.translateX + *tx);
  result.translateY = optional<int32_t>::make(*thiz.translateY + *ty);
  result.scaleX = thiz.scaleX;
  result.scaleY = thiz.scaleY;
  result.rotateX = thiz.rotateX;
  result.rotateY = thiz.rotateY;
  return result;
}
::matrix2D__::Matrix2D scale(::matrix2D__::Matrix2D const& thiz,
                             optional_view<int32_t> sx,
                             optional_view<int32_t> sy) {
  if (!sx || !sy) {
    return thiz;
  }
  ::matrix2D__::Matrix2D result = ::matrix2D__::Matrix2D();
  result.scaleX = optional<int32_t>::make(*thiz.scaleX + *sx);
  result.scaleY = optional<int32_t>::make(*thiz.scaleY + *sy);
  result.rotateX = thiz.rotateX;
  result.rotateY = thiz.rotateY;
  result.translateX = thiz.translateX;
  result.translateY = thiz.translateY;
  return result;
}

}  // namespace

TH_EXPORT_CPP_API_identity(identity);
TH_EXPORT_CPP_API_invert(invert);
TH_EXPORT_CPP_API_multiply(multiply);
TH_EXPORT_CPP_API_rotate(rotate);
TH_EXPORT_CPP_API_translate(translate);
TH_EXPORT_CPP_API_scale(scale);
