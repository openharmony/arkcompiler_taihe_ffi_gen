#include <iostream>
#include "object.Bottom.proj.1.hpp"
#include "object.Left.proj.1.hpp"
#include "object.user.hpp"
#include "taihe/callback.hpp"
#include "taihe/map.hpp"
#include "taihe/object.hpp"

class TopImpl {
public:
  TopImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  ~TopImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void top() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }
};

class LeftImpl {
public:
  LeftImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  ~LeftImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void left() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void top() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }
};

class RightImpl {
public:
  RightImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  ~RightImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void right() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void top() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }
};

class BottomImpl {
public:
  BottomImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  ~BottomImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void bottom() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void left() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void right() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void top() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }
};

class TopAndCallbackImpl {
public:
  TopAndCallbackImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  ~TopAndCallbackImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void top() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  int operator()(int a) {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
    return a;
  }
};

using namespace object;
using namespace taihe;

int main() {
  using callback_type_a = callback<void()>;
  using callback_type_b = callback<int(int)>;
  using weak_callback_type_a = callback_view<void()>;
  using weak_callback_type_b = callback_view<int(int)>;

  auto top = make_holder<TopImpl, Top>();
  Top top_as_top = top;
  weak::Top top_as_weak_top = top;

  // Bottom top_as_bottom = top;  // Error
  // weak::Bottom top_as_weak_bottom = top;  // Error
  // Bottom top_as_top_as_bottom = top_as_top;  // Error
  // weak::Bottom top_as_top_as_weak_bottom = top_as_top;  // Error
  // Bottom top_as_weak_top_as_bottom = top_as_weak_top;  // Error
  // Bottom top_as_weak_top_as_weak_bottom = top_as_weak_top;  // Error

  Bottom top_as_weak_top_as_bottom = Bottom(top_as_weak_top);
  weak::Bottom top_as_top_as_weak_bottom = weak::Bottom(top_as_top);

  std::cout << bool(top_as_weak_top_as_bottom) << std::endl;  // false
  std::cout << bool(top_as_top_as_weak_bottom) << std::endl;  // false

  impl_view<TopImpl, Top> top_as_impl_view = top;
  impl_holder<TopImpl, Top> top_as_impl_holder = top_as_impl_view;

  auto lr = make_holder<BottomImpl, Left, Right>();
  Left lr_as_left = lr;
  Right lr_as_right = lr;
  Top lr_as_top = lr;
  weak::Top lr_as_weak_top = lr;
  // Bottom lr_as_bottom = lr;  // Error

  Left lr_as_weak_top_as_left = Left(lr_as_weak_top);
  weak::Right lr_as_top_as_weak_right = weak::Right(lr_as_top);

  std::cout << bool(lr_as_weak_top_as_left) << std::endl;   // true
  std::cout << bool(lr_as_top_as_weak_right) << std::endl;  // true

  auto callback_b = make_holder<TopAndCallbackImpl, Top, callback_type_b>();

  callback_type_b callback_b_as_callback_b = callback_b;
  weak_callback_type_b callback_b_as_weak_callback_b = callback_b;

  // callback_type_b callback_b_as_callback_a = callback_b;  // Error
  // weak_callback_type_a callback_b_as_weak_callback_a = callback_b;  // Error

  weak::Top callback_b_as_weak_top = weak::Top(callback_b);
  data_holder callback_b_as_data_holder = callback_b;
  data_view callback_b_as_data_view = callback_b;
  data_holder callback_b_as_weak_callback_b_as_data_holder =
      callback_b_as_weak_callback_b;
  data_view callback_b_as_callback_b_as_data_view = callback_b_as_callback_b;
  // callback_type_b callback_b_as_weak_top_as_callback_b =
  // callback_type_b(callback_b_as_weak_top); Error: callback type cannot be
  // recovered from non-callback type

  map<callback_type_b, int> callback_b_map;

  callback_b_map.emplace<1>(callback_b, 1);
  callback_b_map.emplace<1>(callback_b_as_callback_b, 2);
  callback_b_map.emplace<0>(callback_b_as_weak_callback_b, 3);

  for (auto const &[key, value] : callback_b_map) {
    std::cout << bool(key) << ": " << value << std::endl;
  }
}
