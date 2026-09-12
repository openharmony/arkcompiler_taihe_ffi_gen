/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
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

#include "shared_containers.impl.hpp"

#include <algorithm>
#include <cstdint>
#include <system_error>
#include <utility>

#include "taihe/array.hpp"
#include "taihe/expected.hpp"
#include "taihe/error.hpp"
#include "taihe/object.hpp"
#include "taihe/shared_map.hpp"
#include "taihe/shared_set.hpp"
#include "taihe/shared_vector.hpp"
#include "taihe/string.hpp"

namespace {
template<typename T>
class ArrayWrapperImpl {
    ::taihe::shared_array<T> arr_;

public:
    explicit ArrayWrapperImpl(::taihe::shared_array<T> arr) : arr_(std::move(arr))
    {
    }

    uint64_t size()
    {
        return arr_.size();
    };

    taihe::expected<T, taihe::error> get(uint64_t i)
    {
        if (i >= size()) {
            return taihe::unexpected(taihe::error("out of bound"));
        }
        return arr_[i];
    }

    taihe::expected<void, taihe::error> set(uint64_t i, T v)
    {
        if (i >= size()) {
            return taihe::unexpected(taihe::error("out of bound"));
        }
        arr_[i] = v;
        return {};
    }
};

using ArrayI8WrapperImpl = ArrayWrapperImpl<int8_t>;
using ArrayU8WrapperImpl = ArrayWrapperImpl<uint8_t>;
using ArrayI32WrapperImpl = ArrayWrapperImpl<int32_t>;
using ArrayU32WrapperImpl = ArrayWrapperImpl<uint32_t>;
using ArrayF64WrapperImpl = ArrayWrapperImpl<double>;

class VectorWrapperImpl {
    taihe::shared_vector<taihe::string> vec_;

public:
    explicit VectorWrapperImpl(taihe::shared_vector<taihe::string> vec) : vec_(std::move(vec))
    {
    }

    ::taihe::expected<uint64_t, ::taihe::error> getSize()
    {
        return vec_.getSize();
    }

    ::taihe::expected<::taihe::array<::taihe::string>, ::taihe::error> getItems()
    {
        return vec_.getItems();
    }

    ::taihe::expected<void, ::taihe::error> forEachItem(
        ::taihe::callback_view<::taihe::expected<bool, ::taihe::error>(uint64_t i, ::taihe::string_view v)> visitor)
    {
        return vec_.forEachItem(visitor);
    }

    ::taihe::expected<::taihe::string, ::taihe::error> get(uint64_t i)
    {
        return vec_.get(i);
    }

    ::taihe::expected<void, ::taihe::error> set(uint64_t i, ::taihe::string_view v)
    {
        return vec_.set(i, v);
    }

    ::taihe::expected<::taihe::string, ::taihe::error> getAndSet(uint64_t i, ::taihe::string_view v)
    {
        return vec_.getAndSet(i, v);
    }

    ::taihe::expected<void, ::taihe::error> insert(uint64_t i, ::taihe::string_view v)
    {
        return vec_.insert(i, v);
    }

    ::taihe::expected<void, ::taihe::error> insertLast(::taihe::string_view v)
    {
        return vec_.insertLast(v);
    }

    ::taihe::expected<void, ::taihe::error> remove(uint64_t i)
    {
        return vec_.remove(i);
    }

    ::taihe::expected<void, ::taihe::error> removeLast()
    {
        return vec_.removeLast();
    }

    ::taihe::expected<::taihe::string, ::taihe::error> getAndRemove(uint64_t i)
    {
        return vec_.getAndRemove(i);
    }

    ::taihe::expected<::taihe::string, ::taihe::error> getAndRemoveLast()
    {
        return vec_.getAndRemoveLast();
    }

    ::taihe::expected<void, ::taihe::error> clear()
    {
        return vec_.clear();
    }
};

class SetWrapperImpl {
    taihe::shared_set<taihe::string> set_;

public:
    explicit SetWrapperImpl(taihe::shared_set<taihe::string> set) : set_(std::move(set))
    {
    }

    ::taihe::expected<uint64_t, ::taihe::error> getSize()
    {
        return set_.getSize();
    }

    ::taihe::expected<::taihe::array<::taihe::string>, ::taihe::error> getKeys()
    {
        return set_.getKeys();
    }

    ::taihe::expected<void, ::taihe::error> forEachKey(
        ::taihe::callback_view<::taihe::expected<bool, ::taihe::error>(::taihe::string_view k)> visitor)
    {
        return set_.forEachKey(visitor);
    }

    ::taihe::expected<bool, ::taihe::error> has(::taihe::string_view k)
    {
        return set_.has(k);
    }

    ::taihe::expected<void, ::taihe::error> insert(::taihe::string_view k)
    {
        return set_.insert(k);
    }

    ::taihe::expected<bool, ::taihe::error> checkedInsert(::taihe::string_view k)
    {
        return set_.checkedInsert(k);
    }

    ::taihe::expected<void, ::taihe::error> remove(::taihe::string_view k)
    {
        return set_.remove(k);
    }

    ::taihe::expected<bool, ::taihe::error> checkedRemove(::taihe::string_view k)
    {
        return set_.checkedRemove(k);
    }

    ::taihe::expected<void, ::taihe::error> clear()
    {
        return set_.clear();
    }
};

class MapWrapperImpl {
    taihe::shared_map<taihe::string, taihe::string> map_;

public:
    explicit MapWrapperImpl(taihe::shared_map<taihe::string, taihe::string> map) : map_(std::move(map))
    {
    }

    ::taihe::expected<uint64_t, ::taihe::error> getSize()
    {
        return map_.getSize();
    }

    ::taihe::expected<::taihe::array<::taihe::string>, ::taihe::error> getKeys()
    {
        return map_.getKeys();
    }

    ::taihe::expected<void, ::taihe::error> forEachKey(
        ::taihe::callback_view<::taihe::expected<bool, ::taihe::error>(::taihe::string_view k)> visitor)
    {
        return map_.forEachKey(visitor);
    }

    ::taihe::expected<::taihe::array<::taihe::string>, ::taihe::error> getValues()
    {
        return map_.getValues();
    }

    ::taihe::expected<void, ::taihe::error> forEachValue(
        ::taihe::callback_view<::taihe::expected<bool, ::taihe::error>(::taihe::string_view v)> visitor)
    {
        return map_.forEachValue(visitor);
    }

    ::taihe::expected<::taihe::array<::shared_containers::MapEntry>, ::taihe::error> getEntries()
    {
        auto entries = TH_TRY(map_.getEntries());
        taihe::array_builder<::shared_containers::MapEntry> builder(entries.size());
        for (auto &&[key, value] : entries) {
            builder.push_back({std::move(key), std::move(value)});
        }
        return std::move(builder).finish();
    }

    ::taihe::expected<void, ::taihe::error> forEachEntry(
        ::taihe::callback_view<::taihe::expected<bool, ::taihe::error>(::taihe::string_view k, ::taihe::string_view v)>
            visitor)
    {
        return map_.forEachEntry(visitor);
    }

    ::taihe::expected<bool, ::taihe::error> has(::taihe::string_view k)
    {
        return map_.has(k);
    }

    ::taihe::expected<::taihe::optional<::taihe::string>, ::taihe::error> tryGet(::taihe::string_view k)
    {
        return map_.tryGet(k);
    }

    ::taihe::expected<void, ::taihe::error> upsert(::taihe::string_view k, ::taihe::string_view v)
    {
        return map_.upsert(k, v);
    }

    ::taihe::expected<bool, ::taihe::error> checkedInsert(::taihe::string_view k, ::taihe::string_view v)
    {
        return map_.checkedInsert(k, v);
    }

    ::taihe::expected<::taihe::optional<::taihe::string>, ::taihe::error> tryGetAndUpsert(::taihe::string_view k,
                                                                                          ::taihe::string_view v)
    {
        return map_.tryGetAndUpsert(k, v);
    }

    ::taihe::expected<::taihe::optional<::taihe::string>, ::taihe::error> tryGetAndInsert(::taihe::string_view k,
                                                                                          ::taihe::string_view v)
    {
        return map_.tryGetAndInsert(k, v);
    }

    ::taihe::expected<void, ::taihe::error> remove(::taihe::string_view k)
    {
        return map_.remove(k);
    }

    ::taihe::expected<bool, ::taihe::error> checkedRemove(::taihe::string_view k)
    {
        return map_.checkedRemove(k);
    }

    ::taihe::expected<::taihe::optional<::taihe::string>, ::taihe::error> tryGetAndRemove(::taihe::string_view k)
    {
        return map_.tryGetAndRemove(k);
    }

    ::taihe::expected<void, ::taihe::error> clear()
    {
        return map_.clear();
    }
};

class RecordWrapperImpl {
    taihe::shared_map<int32_t, taihe::string> map_;

public:
    RecordWrapperImpl(taihe::shared_map<int32_t, taihe::string> map) : map_(std::move(map))
    {
    }

    ::taihe::expected<uint64_t, ::taihe::error> getSize()
    {
        return map_.getSize();
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> getKeys()
    {
        return map_.getKeys();
    }

    ::taihe::expected<void, ::taihe::error> forEachKey(
        ::taihe::callback_view<::taihe::expected<bool, ::taihe::error>(int32_t k)> visitor)
    {
        return map_.forEachKey(visitor);
    }

    ::taihe::expected<::taihe::array<::taihe::string>, ::taihe::error> getValues()
    {
        return map_.getValues();
    }

    ::taihe::expected<void, ::taihe::error> forEachValue(
        ::taihe::callback_view<::taihe::expected<bool, ::taihe::error>(::taihe::string_view v)> visitor)
    {
        return map_.forEachValue(visitor);
    }

    ::taihe::expected<::taihe::array<::shared_containers::RecordEntry>, ::taihe::error> getEntries()
    {
        auto entries = TH_TRY(map_.getEntries());
        taihe::array_builder<::shared_containers::RecordEntry> builder(entries.size());
        for (auto &&[key, value] : entries) {
            builder.push_back({std::move(key), std::move(value)});
        }
        return std::move(builder).finish();
    }

    ::taihe::expected<void, ::taihe::error> forEachEntry(
        ::taihe::callback_view<::taihe::expected<bool, ::taihe::error>(int32_t k, ::taihe::string_view v)> visitor)
    {
        return map_.forEachEntry(visitor);
    }

    ::taihe::expected<bool, ::taihe::error> has(int32_t k)
    {
        return map_.has(k);
    }

    ::taihe::expected<::taihe::optional<::taihe::string>, ::taihe::error> tryGet(int32_t k)
    {
        return map_.tryGet(k);
    }

    ::taihe::expected<void, ::taihe::error> upsert(int32_t k, ::taihe::string_view v)
    {
        return map_.upsert(k, v);
    }

    ::taihe::expected<bool, ::taihe::error> checkedInsert(int32_t k, ::taihe::string_view v)
    {
        return map_.checkedInsert(k, v);
    }

    ::taihe::expected<::taihe::optional<::taihe::string>, ::taihe::error> tryGetAndUpsert(int32_t k,
                                                                                          ::taihe::string_view v)
    {
        return map_.tryGetAndUpsert(k, v);
    }

    ::taihe::expected<::taihe::optional<::taihe::string>, ::taihe::error> tryGetAndInsert(int32_t k,
                                                                                          ::taihe::string_view v)
    {
        return map_.tryGetAndInsert(k, v);
    }

    ::taihe::expected<void, ::taihe::error> remove(int32_t k)
    {
        return map_.remove(k);
    }

    ::taihe::expected<bool, ::taihe::error> checkedRemove(int32_t k)
    {
        return map_.checkedRemove(k);
    }

    ::taihe::expected<::taihe::optional<::taihe::string>, ::taihe::error> tryGetAndRemove(int32_t k)
    {
        return map_.tryGetAndRemove(k);
    }

    ::taihe::expected<void, ::taihe::error> clear()
    {
        return map_.clear();
    }
};

::taihe::expected<::shared_containers::VectorWrapper, ::taihe::error> makeVectorWrapper(
    ::taihe::shared_vector_view<::taihe::string> v)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<VectorWrapperImpl, ::shared_containers::VectorWrapper>(v);
}

::taihe::expected<::shared_containers::SetWrapper, ::taihe::error> makeSetWrapper(
    ::taihe::shared_set_view<::taihe::string> s)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<SetWrapperImpl, ::shared_containers::SetWrapper>(s);
}

::taihe::expected<::shared_containers::MapWrapper, ::taihe::error> makeMapWrapper(
    ::taihe::shared_map_view<::taihe::string, ::taihe::string> m)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<MapWrapperImpl, ::shared_containers::MapWrapper>(m);
}

::taihe::expected<::shared_containers::RecordWrapper, ::taihe::error> makeRecordWrapper(
    ::taihe::shared_map_view<int32_t, ::taihe::string> r)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<RecordWrapperImpl, ::shared_containers::RecordWrapper>(r);
}

::taihe::expected<::shared_containers::ArrayU8Wrapper, ::taihe::error> makeArrayBufferU8Wrapper(
    ::taihe::shared_array_view<uint8_t> a)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<ArrayU8WrapperImpl, ::shared_containers::ArrayU8Wrapper>(a);
}

::taihe::expected<::shared_containers::ArrayU8Wrapper, ::taihe::error> makeUint8ArrayWrapper(
    ::taihe::shared_array_view<uint8_t> a)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<ArrayU8WrapperImpl, ::shared_containers::ArrayU8Wrapper>(a);
}

::taihe::expected<::shared_containers::ArrayI8Wrapper, ::taihe::error> makeArrayBufferI8Wrapper(
    ::taihe::shared_array_view<int8_t> a)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<ArrayI8WrapperImpl, ::shared_containers::ArrayI8Wrapper>(a);
}

::taihe::expected<::shared_containers::ArrayI8Wrapper, ::taihe::error> makeInt8ArrayWrapper(
    ::taihe::shared_array_view<int8_t> a)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<ArrayI8WrapperImpl, ::shared_containers::ArrayI8Wrapper>(a);
}

::taihe::expected<::shared_containers::ArrayI32Wrapper, ::taihe::error> makeInt32ArrayWrapper(
    ::taihe::shared_array_view<int32_t> a)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<ArrayI32WrapperImpl, ::shared_containers::ArrayI32Wrapper>(a);
}

::taihe::expected<::shared_containers::ArrayU32Wrapper, ::taihe::error> makeUint32ArrayWrapper(
    ::taihe::shared_array_view<uint32_t> a)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<ArrayU32WrapperImpl, ::shared_containers::ArrayU32Wrapper>(a);
}

::taihe::expected<::shared_containers::ArrayF64Wrapper, ::taihe::error> makeFloat64ArrayWrapper(
    ::taihe::shared_array_view<double> a)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<ArrayF64WrapperImpl, ::shared_containers::ArrayF64Wrapper>(a);
}

taihe::expected<taihe::string, taihe::error> serializeArrayU8(taihe::shared_array<uint8_t> arr)
{
    static constexpr size_t U8_MAX_DECIMAL_LENGTH = 3;
    taihe::string_builder builder((U8_MAX_DECIMAL_LENGTH + 1) * arr.size());
    auto first = builder.data();
    auto last = builder.data() + builder.capacity();
    auto current = first;
    for (auto v : arr) {
        auto [ptr, ec] = std::to_chars(current, last, v);
        if (ec != std::errc {}) {
            return taihe::unexpected(taihe::error("to_chars error"));
        }
        current = ptr;
        *current++ = ',';
    }
    return std::move(builder).finish(current - first);
}

taihe::expected<taihe::string, taihe::error> serializeArrayI64(taihe::shared_array<int64_t> arr)
{
    static constexpr size_t I64_MAX_DECIMAL_LENGTH = 19 + 1;
    taihe::string_builder builder((I64_MAX_DECIMAL_LENGTH + 1) * arr.size());
    auto first = builder.data();
    auto last = builder.data() + builder.capacity();
    auto current = first;
    for (auto v : arr) {
        auto [ptr, ec] = std::to_chars(current, last, v);
        if (ec != std::errc {}) {
            return taihe::unexpected(taihe::error("to_chars error"));
        }
        current = ptr;
        *current++ = ',';
    }
    return std::move(builder).finish(current - first);
}

taihe::expected<taihe::string, taihe::error> serializeVector(taihe::shared_vector<taihe::string> vec)
{
    auto items = TH_TRY(vec.getItems());
    size_t size = 0;
    for (auto const &item : items) {
        size += item.size();
        size++;
    }
    taihe::string_builder builder(size);
    auto first = builder.data();
    auto current = first;
    for (auto const &item : items) {
        current = std::copy(item.begin(), item.end(), current);
        *current++ = ',';
    }
    return std::move(builder).finish(current - first);
}

taihe::expected<taihe::string, taihe::error> serializeSet(taihe::shared_set<taihe::string> set)
{
    auto keys = TH_TRY(set.getKeys());
    size_t size = 0;
    for (auto const &key : keys) {
        size += key.size();
        size++;
    }
    taihe::string_builder builder(size);
    auto first = builder.data();
    auto current = first;
    for (auto const &key : keys) {
        current = std::copy(key.begin(), key.end(), current);
        *current++ = ',';
    }
    return std::move(builder).finish(current - first);
}

taihe::expected<taihe::string, taihe::error> serializeMap(taihe::shared_map<taihe::string, taihe::string> map)
{
    auto entries = TH_TRY(map.getEntries());
    size_t size = 0;
    for (auto const &[key, value] : entries) {
        size += key.size();
        size++;
        size += value.size();
        size++;
    }
    taihe::string_builder builder(size);
    auto first = builder.data();
    auto current = first;
    for (auto const &[key, value] : entries) {
        current = std::copy(key.begin(), key.end(), current);
        *current++ = ':';
        current = std::copy(value.begin(), value.end(), current);
        *current++ = ',';
    }
    return std::move(builder).finish(current - first);
}

taihe::expected<taihe::string, taihe::error> serializeRecord(taihe::shared_map<int32_t, taihe::string> map)
{
    static constexpr size_t I32_MAX_DECIMAL_LENGTH = 10 + 1;
    auto entries = TH_TRY(map.getEntries());
    size_t size = 0;
    for (auto const &[key, value] : entries) {
        size += I32_MAX_DECIMAL_LENGTH;
        size++;
        size += value.size();
        size++;
    }
    taihe::string_builder builder(size);
    auto first = builder.data();
    auto last = builder.data() + builder.capacity();
    auto current = first;
    for (auto const &[key, value] : entries) {
        auto [ptr, ec] = std::to_chars(current, last, key);
        if (ec != std::errc {}) {
            return taihe::unexpected(taihe::error("to_chars error"));
        }
        current = ptr;
        *current++ = ':';
        current = std::copy(value.begin(), value.end(), current);
        *current++ = ',';
    }
    return std::move(builder).finish(current - first);
}

taihe::expected<taihe::string, taihe::error> serializeAny(shared_containers::ContainerUnion const &u)
{
    switch (u.get_tag()) {
        case shared_containers::ContainerUnion::tag_t::arraybufferValue:
            return serializeArrayU8(u.get_arraybufferValue_ref());
        case shared_containers::ContainerUnion::tag_t::typedarrayValue:
            return serializeArrayI64(u.get_typedarrayValue_ref());
        case shared_containers::ContainerUnion::tag_t::vectorValue:
            return serializeVector(u.get_vectorValue_ref());
        case shared_containers::ContainerUnion::tag_t::setValue:
            return serializeSet(u.get_setValue_ref());
        case shared_containers::ContainerUnion::tag_t::mapValue:
            return serializeMap(u.get_mapValue_ref());
        case shared_containers::ContainerUnion::tag_t::recordValue:
            return serializeRecord(u.get_recordValue_ref());
    }
}

class ContainerSerializerImpl {
public:
    taihe::expected<taihe::string, taihe::error> serialize(shared_containers::ContainerUnion const &u)
    {
        return serializeAny(u);
    }
};

::taihe::expected<::shared_containers::ContainerSerializer, ::taihe::error> getSerializer()
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<ContainerSerializerImpl, ::shared_containers::ContainerSerializer>();
}

::taihe::expected<::taihe::array<::taihe::string>, ::taihe::error> testGenerator(
    ::shared_containers::weak::ContainerGenerator generator, uint64_t count)
{
    taihe::array_builder<taihe::string> builder(count);
    for (uint64_t i = 0; i < count; i++) {
        builder.push_back(TH_TRY(serializeAny(TH_TRY(generator->generate()))));
    }
    return std::move(builder).finish();
}

::taihe::expected<void, ::taihe::error> clearAllInStruct(::shared_containers::ContainerStruct const &containers)
{
    TH_TRY(containers.vectorValue.clear());
    TH_TRY(containers.setValue.clear());
    TH_TRY(containers.mapValue.clear());
    TH_TRY(containers.recordValue.clear());
    std::fill(containers.arraybufferValue.begin(), containers.arraybufferValue.end(), 0);
    std::fill(containers.typedarrayValue.begin(), containers.typedarrayValue.end(), 0);
    return {};
}

::taihe::expected<void, ::taihe::error> clearAnyInUnion(::shared_containers::ContainerUnion const &u)
{
    switch (u.get_tag()) {
        case shared_containers::ContainerUnion::tag_t::arraybufferValue:
            std::fill(u.get_arraybufferValue_ref().begin(), u.get_arraybufferValue_ref().end(), 0);
            return {};
        case shared_containers::ContainerUnion::tag_t::typedarrayValue:
            std::fill(u.get_typedarrayValue_ref().begin(), u.get_typedarrayValue_ref().end(), 0);
            return {};
        case shared_containers::ContainerUnion::tag_t::vectorValue:
            return u.get_vectorValue_ref().clear();
        case shared_containers::ContainerUnion::tag_t::setValue:
            return u.get_setValue_ref().clear();
        case shared_containers::ContainerUnion::tag_t::mapValue:
            return u.get_mapValue_ref().clear();
        case shared_containers::ContainerUnion::tag_t::recordValue:
            return u.get_recordValue_ref().clear();
    }
}

::taihe::expected<void, ::taihe::error> clearAllInArray(
    ::taihe::array_view<::shared_containers::ContainerUnion> containers)
{
    for (auto const &container : containers) {
        TH_TRY(clearAnyInUnion(container));
    }
    return {};
}

::taihe::expected<void, ::taihe::error> clearAllInSharedVector(
    ::taihe::shared_vector_view<::shared_containers::ContainerUnion> containers)
{
    return containers.forEachItem(
        taihe::into_view<::taihe::shared_vector_view<::shared_containers::ContainerUnion>::value_visitor_type>(
            [](size_t, ::shared_containers::ContainerUnion const &container) -> taihe::expected<bool, taihe::error> {
                TH_TRY(clearAnyInUnion(container));
                return true;
            }));
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_makeVectorWrapper(makeVectorWrapper);
TH_EXPORT_CPP_API_makeMapWrapper(makeMapWrapper);
TH_EXPORT_CPP_API_makeRecordWrapper(makeRecordWrapper);
TH_EXPORT_CPP_API_makeSetWrapper(makeSetWrapper);
TH_EXPORT_CPP_API_makeArrayBufferU8Wrapper(makeArrayBufferU8Wrapper);
TH_EXPORT_CPP_API_makeUint8ArrayWrapper(makeUint8ArrayWrapper);
TH_EXPORT_CPP_API_makeArrayBufferI8Wrapper(makeArrayBufferI8Wrapper);
TH_EXPORT_CPP_API_makeInt8ArrayWrapper(makeInt8ArrayWrapper);
TH_EXPORT_CPP_API_makeInt32ArrayWrapper(makeInt32ArrayWrapper);
TH_EXPORT_CPP_API_makeUint32ArrayWrapper(makeUint32ArrayWrapper);
TH_EXPORT_CPP_API_makeFloat64ArrayWrapper(makeFloat64ArrayWrapper);
TH_EXPORT_CPP_API_getSerializer(getSerializer);
TH_EXPORT_CPP_API_testGenerator(testGenerator);
TH_EXPORT_CPP_API_clearAllInStruct(clearAllInStruct);
TH_EXPORT_CPP_API_clearAnyInUnion(clearAnyInUnion);
TH_EXPORT_CPP_API_clearAllInArray(clearAllInArray);
TH_EXPORT_CPP_API_clearAllInSharedVector(clearAllInSharedVector);
// NOLINTEND
