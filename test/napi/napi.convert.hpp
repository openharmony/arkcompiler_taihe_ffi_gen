#ifndef NAPI_CONVERT_H
#define NAPI_CONVERT_H

#include <cstdint>
#include "node/node_api.h"
#include "taihe/map.hpp"
#include "taihe/set.hpp"
#include "taihe/string.hpp"
#include "taihe/vector.hpp"

template<typename th_cpp_t>
struct napi_convert;

template<>
struct napi_convert<int32_t> {
  static inline napi_value create(napi_env env, int32_t &&cpp_obj) {
    napi_value js_obj = nullptr;
    napi_create_int32(env, cpp_obj, &js_obj);
    return js_obj;
  }

  static inline int32_t get(napi_env env, napi_value js_obj) {
    int32_t cpp_obj;
    napi_get_value_int32(env, js_obj, &cpp_obj);
    return cpp_obj;
  }
};

template<>
struct napi_convert<int64_t> {
  static inline napi_value create(napi_env env, int64_t &&cpp_obj) {
    napi_value js_obj = nullptr;
    napi_create_int64(env, cpp_obj, &js_obj);
    return js_obj;
  }

  static inline int64_t get(napi_env env, napi_value js_obj) {
    int64_t cpp_obj;
    napi_get_value_int64(env, js_obj, &cpp_obj);
    return cpp_obj;
  }
};

template<>
struct napi_convert<bool> {
  static inline napi_value create(napi_env env, bool &&cpp_obj) {
    napi_value js_obj = nullptr;
    napi_get_boolean(env, cpp_obj, &js_obj);
    return js_obj;
  }

  static inline bool get(napi_env env, napi_value js_obj) {
    bool cpp_obj;
    napi_get_value_bool(env, js_obj, &cpp_obj);
    return cpp_obj;
  }
};

template<>
struct napi_convert<uint32_t> {
  static inline napi_value create(napi_env env, uint32_t &&cpp_obj) {
    napi_value js_obj = nullptr;
    napi_create_uint32(env, cpp_obj, &js_obj);
    return js_obj;
  }

  static inline uint32_t get(napi_env env, napi_value js_obj) {
    uint32_t cpp_obj;
    napi_get_value_uint32(env, js_obj, &cpp_obj);
    return cpp_obj;
  }
};

template<>
struct napi_convert<double> {
  static inline napi_value create(napi_env env, double &&cpp_obj) {
    napi_value js_obj = nullptr;
    napi_create_double(env, cpp_obj, &js_obj);
    return js_obj;
  }

  static inline double get(napi_env env, napi_value js_obj) {
    double cpp_obj;
    napi_get_value_double(env, js_obj, &cpp_obj);
    return cpp_obj;
  }
};

template<>
struct napi_convert<taihe::string> {
  static inline napi_value create(napi_env env, taihe::string &&cpp_obj) {
    napi_value js_obj = nullptr;
    napi_create_string_utf8(env, cpp_obj.c_str(), cpp_obj.size(), &js_obj);
    return js_obj;
  }

  static inline taihe::string get(napi_env env, napi_value js_obj) {
    size_t len_cpp_obj = 0;
    napi_get_value_string_utf8(env, js_obj, nullptr, 0, &len_cpp_obj);
    char char_cpp_obj[len_cpp_obj + 1];
    napi_get_value_string_utf8(env, js_obj, char_cpp_obj, len_cpp_obj + 1,
                               &len_cpp_obj);
    taihe::string cpp_obj(char_cpp_obj);
    return cpp_obj;
  }
};

template<typename T>
struct napi_convert<taihe::vector<T>> {
  static napi_value create(napi_env env, taihe::vector<T> &&cpp_obj) {
    napi_value js_obj = nullptr;
    napi_create_array_with_length(env, cpp_obj.size(), &js_obj);

    for (uint32_t i = 0; i < cpp_obj.size(); i++) {
      napi_value element = napi_convert<T>::create(env, std::move(cpp_obj[i]));
      napi_set_element(env, js_obj, i, element);
    }

    return js_obj;
  }

  static taihe::vector<T> get(napi_env env, napi_value js_obj) {
    uint32_t length;
    napi_get_array_length(env, js_obj, &length);
    ::taihe::vector<T> cpp_obj;

    for (uint32_t i = 0; i < length; i++) {
      napi_value element;
      napi_get_element(env, js_obj, i, &element);

      T cpp_element = napi_convert<T>::get(env, element);
      cpp_obj.push_back(cpp_element);
    }

    return cpp_obj;
  }
};

template<typename K, typename V>
struct napi_convert<taihe::map<K, V>> {
  static napi_value create(napi_env env, taihe::map_view<K, V> &&cpp_obj) {
    // 获取全局对象
    napi_value global = nullptr;
    napi_get_global(env, &global);

    // 获取 Map 构造函数
    napi_value map_constructor = nullptr;
    napi_get_named_property(env, global, "Map", &map_constructor);

    // 创建一个新的 Map 对象
    napi_value js_obj = nullptr;
    napi_new_instance(env, map_constructor, 0, nullptr, &js_obj);

    // 获取 Map 的 set 方法
    napi_value set_fn = nullptr;
    napi_get_named_property(env, map_constructor, "prototype", &set_fn);
    napi_get_named_property(env, set_fn, "set", &set_fn);

    cpp_obj.accept([env, js_obj, set_fn](K key, V value) {
      napi_value js_key = napi_convert<K>::create(env, std::move(key));
      napi_value js_value = napi_convert<V>::create(env, std::move(value));
      // 调用 Map 的 set 方法
      napi_value args[2] = {js_key, js_value};
      napi_call_function(env, js_obj, set_fn, 2, args, nullptr);
    });

    return js_obj;
  }

  static taihe::map<K, V> get(napi_env env, napi_value js_obj) {
    taihe::map<K, V> cpp_obj;

    napi_value global = nullptr;
    napi_get_global(env, &global);

    napi_value map_constructor = nullptr;
    napi_get_named_property(env, global, "Map", &map_constructor);

    napi_value entries_fn = nullptr;
    napi_get_named_property(env, map_constructor, "prototype", &entries_fn);
    napi_get_named_property(env, entries_fn, "entries", &entries_fn);

    // 调用 entries 方法，获取迭代器
    napi_value entries_iter = nullptr;
    napi_call_function(env, js_obj, entries_fn, 0, nullptr, &entries_iter);

    // 将迭代器转换为数组
    napi_value array_from_fn = nullptr;
    napi_get_named_property(env, global, "Array", &array_from_fn);
    napi_get_named_property(env, array_from_fn, "from", &array_from_fn);

    napi_value entries_array = nullptr;
    napi_call_function(env, global, array_from_fn, 1, &entries_iter,
                       &entries_array);

    // 获取数组长度
    uint32_t length = 0;
    napi_get_array_length(env, entries_array, &length);

    for (uint32_t i = 0; i < length; i++) {
      napi_value entry = nullptr;
      napi_get_element(env, entries_array, i, &entry);

      napi_value js_key = nullptr;
      napi_get_element(env, entry, 0, &js_key);

      napi_value js_value = nullptr;
      napi_get_element(env, entry, 1, &js_value);

      K key = napi_convert<K>::get(env, js_key);
      V value = napi_convert<V>::get(env, js_value);
      cpp_obj.emplace(key, value);
    }

    return cpp_obj;
  }
};

template<typename T>
struct napi_convert<taihe::set<T>> {
  static napi_value create(napi_env env, taihe::set<T> &&cpp_obj) {
    // 获取全局对象
    napi_value global = nullptr;
    napi_get_global(env, &global);

    // 获取 Set 构造函数
    napi_value set_constructor = nullptr;
    napi_get_named_property(env, global, "Set", &set_constructor);

    // 创建一个新的 Set 对象
    napi_value js_obj = nullptr;
    napi_new_instance(env, set_constructor, 0, nullptr, &js_obj);

    // 获取 Set 的 add 方法
    napi_value add_fn = nullptr;
    napi_get_named_property(env, set_constructor, "prototype", &add_fn);
    napi_get_named_property(env, add_fn, "add", &add_fn);

    cpp_obj.accept([env, js_obj, add_fn](T element) {
      napi_value js_element = napi_convert<T>::create(env, std::move(element));

      // 调用 Set 的 add 方法
      napi_value args[1] = {js_element};
      napi_call_function(env, js_obj, add_fn, 1, args, nullptr);
    });

    return js_obj;
  }

  static taihe::set<T> get(napi_env env, napi_value js_obj) {
    taihe::set<T> cpp_obj;

    napi_value global = nullptr;
    napi_get_global(env, &global);

    napi_value set_constructor = nullptr;
    napi_get_named_property(env, global, "Set", &set_constructor);

    napi_value values_fn = nullptr;
    napi_get_named_property(env, set_constructor, "prototype", &values_fn);
    napi_get_named_property(env, values_fn, "values", &values_fn);

    // 调用 values 方法，获取迭代器
    napi_value values_iter = nullptr;
    napi_call_function(env, js_obj, values_fn, 0, nullptr, &values_iter);

    // 将迭代器转换为数组
    napi_value array_from_fn = nullptr;
    napi_get_named_property(env, global, "Array", &array_from_fn);
    napi_get_named_property(env, array_from_fn, "from", &array_from_fn);

    napi_value values_array = nullptr;
    napi_call_function(env, global, array_from_fn, 1, &values_iter,
                       &values_array);

    uint32_t length = 0;
    napi_get_array_length(env, values_array, &length);

    for (uint32_t i = 0; i < length; i++) {
      napi_value js_element = nullptr;
      napi_get_element(env, values_array, i, &js_element);

      // 将值转换为 C++ 类型
      T cpp_element = napi_convert<T>::get(env, js_element);
      cpp_obj.emplace(cpp_element);
    }

    return cpp_obj;
  }
};

#endif