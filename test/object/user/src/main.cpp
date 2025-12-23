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

#include <iostream>
#include <unordered_set>
#include "object.Bottom.proj.1.hpp"
#include "object.Left.proj.1.hpp"
#include "object.user.hpp"
#include "taihe/callback.hpp"
#include "taihe/map.hpp"
#include "taihe/object.hpp"

class Named {
public:
    static inline std::unordered_set<Named *> registry;

    std::string const name;

    Named(std::string_view sv) : name(sv)
    {
        std::cout << name << " made" << std::endl;
        registry.insert(this);
    }

    ~Named()
    {
        std::cout << name << " deleted" << std::endl;
        registry.erase(this);
    }
};

class TopImpl : Named {
public:
    TopImpl(std::string_view sv) : Named(sv)
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    ~TopImpl()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    void top()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }
};

class LeftImpl : Named {
public:
    LeftImpl(std::string_view sv) : Named(sv)
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    ~LeftImpl()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    void left()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    void top()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }
};

class RightImpl : Named {
public:
    RightImpl(std::string_view sv) : Named(sv)
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    ~RightImpl()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    void right()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    void top()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }
};

class BottomImpl : Named {
public:
    BottomImpl(std::string_view sv) : Named(sv)
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    ~BottomImpl()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    void bottom()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    void left()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    void right()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    void top()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }
};

class TopAndCallbackImpl : Named {
public:
    TopAndCallbackImpl(std::string_view sv) : Named(sv)
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    ~TopAndCallbackImpl()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    void top()
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
    }

    int operator()(int a)
    {
        std::cout << __PRETTY_FUNCTION__ << std::endl;
        return a;
    }
};

using namespace object;
using namespace taihe;

using callback_type_a = callback<void()>;
using callback_type_b = callback<int(int)>;
using weak_callback_type_a = callback_view<void()>;
using weak_callback_type_b = callback_view<int(int)>;

void testTop()
{
    auto top = make_holder<TopImpl, Top>("top");
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

    std::cout << top_as_weak_top_as_bottom.is_error() << std::endl;  // true
    std::cout << top_as_top_as_weak_bottom.is_error() << std::endl;  // true

    impl_view<TopImpl, Top> top_as_impl_view = top;
    impl_holder<TopImpl, Top> top_as_impl_holder = top_as_impl_view;
}

void testLR()
{
    auto lr = make_holder<BottomImpl, Left, Right>("lr");
    Left lr_as_left = lr;
    Right lr_as_right = lr;
    Top lr_as_top = lr;
    weak::Top lr_as_weak_top = lr;
    // Bottom lr_as_bottom = lr;  // Error

    Left lr_as_weak_top_as_left = Left(lr_as_weak_top);
    weak::Right lr_as_top_as_weak_right = weak::Right(lr_as_top);

    std::cout << lr_as_weak_top_as_left.is_error() << std::endl;   // false
    std::cout << lr_as_top_as_weak_right.is_error() << std::endl;  // false
}

void testCallbackB()
{
    auto callback_b = make_holder<TopAndCallbackImpl, Top, callback_type_b>("callback_b");

    callback_type_b callback_b_as_callback_b = callback_b;
    weak_callback_type_b callback_b_as_weak_callback_b = callback_b;

    // callback_type_b callback_b_as_callback_a = callback_b;  // Error
    // weak_callback_type_a callback_b_as_weak_callback_a = callback_b;  // Error

    weak::Top callback_b_as_weak_top = weak::Top(callback_b);
    data_holder callback_b_as_data_holder = callback_b;
    data_view callback_b_as_data_view = callback_b;
    data_holder callback_b_as_weak_callback_b_as_data_holder = callback_b_as_weak_callback_b;
    data_view callback_b_as_callback_b_as_data_view = callback_b_as_callback_b;

    map<callback_type_b, int> callback_b_map;

    callback_b_map.emplace<1>(callback_b, 1);
    callback_b_map.emplace<1>(callback_b_as_callback_b, 2);
    callback_b_map.emplace<0>(callback_b_as_weak_callback_b, 3);

    std::cout << "callback_b_map size: " << callback_b_map.size() << std::endl;
}

int main()
{
    testTop();
    testLR();
    testCallbackB();

    bool all_deleted = true;
    for (auto *named : Named::registry) {
        std::cout << named->name << " is still alive" << std::endl;
        all_deleted = false;
    }
    if (all_deleted) {
        std::cout << "All named objects are deleted" << std::endl;
        return 0;
    } else {
        return 1;
    }
}
