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

#include "test.impl.hpp"

namespace {
template<typename Iterator, typename Converter>
auto converte_iterator(Iterator it, Converter converter)
{
    struct ConvertedIterator {
        Iterator it;
        Converter converter;

        using value_type = decltype(converter(*it));
        using difference_type = std::ptrdiff_t;
        using pointer = value_type *;
        using reference = value_type &;
        using iterator_category = std::input_iterator_tag;

        ConvertedIterator &operator++()
        {
            ++it;
            return *this;
        }

        ConvertedIterator operator++(int)
        {
            ConvertedIterator tmp = *this;
            ++it;
            return tmp;
        }

        bool operator==(ConvertedIterator const &other) const
        {
            return it == other.it;
        }

        bool operator!=(ConvertedIterator const &other) const
        {
            return it != other.it;
        }

        value_type operator*() const
        {
            return converter(*it);
        }
    };

    return ConvertedIterator {it, converter};
}

::taihe::map<::taihe::string, ::taihe::string> deserializeMap(::taihe::array_view<::test::Pair> serialized)
{
    taihe::map<::taihe::string, ::taihe::string> m;
    for (auto const &[k, v] : serialized) {
        m.emplace(k, v);
    }
    return m;
}

::taihe::array<::test::Pair> serializeMap(::taihe::map_view<::taihe::string, ::taihe::string> m)
{
    auto arr = taihe::array<::test::Pair>(taihe::copy_data,
                                          converte_iterator(m.begin(),
                                                            [](auto &kv) -> ::test::Pair {
                                                                return ::test::Pair {std::move(kv.first),
                                                                                     std::move(kv.second)};
                                                            }),
                                          m.size());
    return arr;
}

::taihe::set<::taihe::string> deserializeSet(::taihe::array_view<::taihe::string> serialized)
{
    taihe::set<::taihe::string> s;
    for (auto const &v : serialized) {
        s.emplace(v);
    }
    return s;
}

::taihe::array<::taihe::string> serializeSet(::taihe::set_view<::taihe::string> s)
{
    return taihe::array<::taihe::string>(taihe::copy_data,
                                         converte_iterator(s.begin(),
                                                           [](auto &item) -> ::taihe::string {
                                                               return std::move(item);
                                                           }),
                                         s.size());
}

::taihe::vector<::taihe::string> deserializeVector(::taihe::array_view<::taihe::string> serialized)
{
    taihe::vector<::taihe::string> v;
    for (auto const &item : serialized) {
        v.push_back(item);
    }
    return v;
}

::taihe::array<::taihe::string> serializeVector(::taihe::vector_view<::taihe::string> v)
{
    return taihe::array<::taihe::string>(taihe::copy_data,
                                         converte_iterator(v.begin(),
                                                           [](auto &item) -> ::taihe::string {
                                                               return std::move(item);
                                                           }),
                                         v.size());
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_deserializeMap(deserializeMap);
TH_EXPORT_CPP_API_serializeMap(serializeMap);
TH_EXPORT_CPP_API_deserializeSet(deserializeSet);
TH_EXPORT_CPP_API_serializeSet(serializeSet);
TH_EXPORT_CPP_API_deserializeVector(deserializeVector);
TH_EXPORT_CPP_API_serializeVector(serializeVector);
// NOLINTEND
