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

#ifndef TAIHE_PLATFORM_ANI_HPP
#define TAIHE_PLATFORM_ANI_HPP

#include <taihe/object.hpp>
#include <taihe/runtime_ani.hpp>

#include <taihe.platform.ani.proj.hpp>

namespace taihe {
// convert between ani types and taihe types

template<typename cpp_owner_t>
struct from_ani_t;

template<typename cpp_owner_t>
struct into_ani_t;

template<typename cpp_owner_t>
constexpr inline from_ani_t<cpp_owner_t> from_ani;

template<typename cpp_owner_t>
constexpr inline into_ani_t<cpp_owner_t> into_ani;
}  // namespace taihe

namespace taihe {
// Reference management

class sref_guard {
protected:
    ani_ref ref = nullptr;

public:
    sref_guard(ani_env *env, ani_ref val)
    {
        env->GlobalReference_Create(val, &ref);
    }

    ~sref_guard()
    {
    }

    sref_guard(sref_guard const &) = delete;
    sref_guard &operator=(sref_guard const &) = delete;
    sref_guard(sref_guard &&) = delete;
    sref_guard &operator=(sref_guard &&) = delete;

    ani_ref get_ref()
    {
        return ref;
    }
};

class dref_guard {
protected:
    ani_ref ref = nullptr;

public:
    dref_guard(ani_env *env, ani_ref val)
    {
        env->GlobalReference_Create(val, &ref);
    }

    ~dref_guard()
    {
        env_guard guard;
        ani_env *env = guard.get_env();
        env->GlobalReference_Delete(ref);
    }

    dref_guard(dref_guard const &) = delete;
    dref_guard &operator=(dref_guard const &) = delete;
    dref_guard(dref_guard &&) = delete;
    dref_guard &operator=(dref_guard &&) = delete;
};

template<typename AniRefGuard>
struct same_impl_t<AniRefGuard, std::enable_if_t<std::is_base_of_v<dref_guard, AniRefGuard>>> {
    bool operator()(data_view lhs, data_view rhs) const
    {
        auto lhs_as_ani = taihe::platform::ani::weak::AniObject(lhs);
        auto rhs_as_ani = taihe::platform::ani::weak::AniObject(rhs);
        if (lhs_as_ani.is_error() || rhs_as_ani.is_error()) {
            return same_impl<void>(lhs, rhs);
        }
        env_guard guard;
        ani_env *env = guard.get_env();
        ani_ref lhs_ref = reinterpret_cast<ani_ref>(lhs_as_ani->getGlobalReference());
        ani_ref rhs_ref = reinterpret_cast<ani_ref>(rhs_as_ani->getGlobalReference());
        ani_boolean result;
        return env->Reference_Equals(lhs_ref, rhs_ref, &result) == ANI_OK && result;
    }
};

template<typename AniRefGuard>
struct hash_impl_t<AniRefGuard, std::enable_if_t<std::is_base_of_v<dref_guard, AniRefGuard>>> {
    std::size_t operator()(data_view val) const
    {
        auto val_as_ani = taihe::platform::ani::weak::AniObject(val);
        if (val_as_ani.is_error()) {
            return hash_impl<void>(val);
        }
        TH_THROW(std::runtime_error, "Hashing of ani_ref is not implemented yet.");
    }
};
}  // namespace taihe

namespace taihe {
inline __attribute__((noinline)) ani_module ani_find_module(ani_env *env, char const *descriptor)
{
    ani_module mod;
    if (ANI_OK != env->FindModule(descriptor, &mod)) {
        std::cerr << "Module not found: " << descriptor << std::endl;
        return nullptr;
    }
    return mod;
}

inline __attribute__((noinline)) ani_namespace ani_find_namespace(ani_env *env, char const *descriptor)
{
    ani_namespace ns;
    if (ANI_OK != env->FindNamespace(descriptor, &ns)) {
        std::cerr << "Namespace not found: " << descriptor << std::endl;
        return nullptr;
    }
    return ns;
}

inline __attribute__((noinline)) ani_class ani_find_class(ani_env *env, char const *descriptor)
{
    ani_class cls;
    if (ANI_OK != env->FindClass(descriptor, &cls)) {
        std::cerr << "Class not found: " << descriptor << std::endl;
        return nullptr;
    }
    return cls;
}

inline __attribute__((noinline)) ani_enum ani_find_enum(ani_env *env, char const *descriptor)
{
    ani_enum enm;
    if (ANI_OK != env->FindEnum(descriptor, &enm)) {
        std::cerr << "Enum not found: " << descriptor << std::endl;
        return nullptr;
    }
    return enm;
}

inline __attribute__((noinline)) ani_function ani_find_module_function(ani_env *env, ani_module mod, char const *name,
                                                                       char const *signature)
{
    ani_function fn;
    if (mod == nullptr) {
        return nullptr;
    }
    if (ANI_OK != env->Module_FindFunction(mod, name, signature, &fn)) {
        std::cerr << "Function not found: " << name << " with signature: " << (signature ? signature : "<nullptr>")
                  << std::endl;

        return nullptr;
    }
    return fn;
}

inline __attribute__((noinline)) ani_function ani_find_namespace_function(ani_env *env, ani_namespace ns,
                                                                          char const *name, char const *signature)
{
    ani_function fn;
    if (ns == nullptr) {
        return nullptr;
    }
    if (ANI_OK != env->Namespace_FindFunction(ns, name, signature, &fn)) {
        std::cerr << "Function not found: " << name << " with signature: " << (signature ? signature : "<nullptr>")
                  << std::endl;
        return nullptr;
    }
    return fn;
}

inline __attribute__((noinline)) ani_method ani_find_class_method(ani_env *env, ani_class cls, char const *name,
                                                                  char const *signature)
{
    ani_method mtd;
    if (cls == nullptr) {
        return nullptr;
    }
    if (ANI_OK != env->Class_FindMethod(cls, name, signature, &mtd)) {
        std::cerr << "Method not found: " << name << " with signature: " << (signature ? signature : "<nullptr>")
                  << std::endl;
        return nullptr;
    }
    return mtd;
}

inline __attribute__((noinline)) ani_static_method ani_find_class_static_method(ani_env *env, ani_class cls,
                                                                                char const *name, char const *signature)
{
    ani_static_method mtd;
    if (cls == nullptr) {
        return nullptr;
    }
    if (ANI_OK != env->Class_FindStaticMethod(cls, name, signature, &mtd)) {
        std::cerr << "Static method not found: " << name << " with signature: " << (signature ? signature : "<nullptr>")
                  << std::endl;
        return nullptr;
    }
    return mtd;
}

inline __attribute__((noinline)) ani_variable ani_find_module_variable(ani_env *env, ani_module mod, char const *name)
{
    ani_variable var;
    if (ANI_OK != env->Module_FindVariable(mod, name, &var)) {
        std::cerr << "Variable not found: " << name << std::endl;
        return nullptr;
    }
    return var;
}

inline __attribute__((noinline)) ani_variable ani_find_namespace_variable(ani_env *env, ani_namespace ns,
                                                                          char const *name)
{
    ani_variable var;
    if (ns == nullptr) {
        return nullptr;
    }
    if (ANI_OK != env->Namespace_FindVariable(ns, name, &var)) {
        std::cerr << "Variable not found: " << name << std::endl;
        return nullptr;
    }
    return var;
}

inline __attribute__((noinline)) ani_field ani_find_class_field(ani_env *env, ani_class cls, char const *name)
{
    ani_field fld;
    if (cls == nullptr) {
        return nullptr;
    }
    if (ANI_OK != env->Class_FindField(cls, name, &fld)) {
        std::cerr << "Field not found: " << name << std::endl;
        return nullptr;
    }
    return fld;
}

inline __attribute__((noinline)) ani_static_field ani_find_class_static_field(ani_env *env, ani_class cls,
                                                                              char const *name)
{
    ani_static_field fld;
    if (cls == nullptr) {
        return nullptr;
    }
    if (ANI_OK != env->Class_FindStaticField(cls, name, &fld)) {
        std::cerr << "Static field not found: " << name << std::endl;
        return nullptr;
    }
    return fld;
}
}  // namespace taihe

namespace taihe {
template<typename Descriptor>
inline ani_module ani_cache_module(ani_env *env)
{
    static sref_guard guard(env, ani_find_module(env, TH_AS_C_STR(Descriptor)));
    return static_cast<ani_module>(guard.get_ref());
}

template<typename Descriptor>
inline ani_namespace ani_cache_namespace(ani_env *env)
{
    static sref_guard guard(env, ani_find_namespace(env, TH_AS_C_STR(Descriptor)));
    return static_cast<ani_namespace>(guard.get_ref());
}

template<typename Descriptor>
inline ani_class ani_cache_class(ani_env *env)
{
    static sref_guard guard(env, ani_find_class(env, TH_AS_C_STR(Descriptor)));
    return static_cast<ani_class>(guard.get_ref());
}

template<typename Descriptor>
inline ani_enum ani_cache_enum(ani_env *env)
{
    static sref_guard guard(env, ani_find_enum(env, TH_AS_C_STR(Descriptor)));
    return static_cast<ani_enum>(guard.get_ref());
}

template<typename Descriptor, typename Name, typename Signature>
inline ani_function ani_cache_module_function(ani_env *env)
{
    static ani_function function =
        ani_find_module_function(env, ani_cache_module<Descriptor>(env), TH_AS_C_STR(Name), TH_AS_C_STR(Signature));
    return function;
}

template<typename Descriptor, typename Name, typename Signature>
inline ani_function ani_cache_namespace_function(ani_env *env)
{
    static ani_function function = ani_find_namespace_function(env, ani_cache_namespace<Descriptor>(env),
                                                               TH_AS_C_STR(Name), TH_AS_C_STR(Signature));
    return function;
}

template<typename Descriptor, typename Name, typename Signature>
inline ani_method ani_cache_class_method(ani_env *env)
{
    static ani_method method =
        ani_find_class_method(env, ani_cache_class<Descriptor>(env), TH_AS_C_STR(Name), TH_AS_C_STR(Signature));
    return method;
}

template<typename Descriptor, typename Name, typename Signature>
inline ani_static_method ani_cache_class_static_method(ani_env *env)
{
    static ani_static_method method =
        ani_find_class_static_method(env, ani_cache_class<Descriptor>(env), TH_AS_C_STR(Name), TH_AS_C_STR(Signature));
    return method;
}

template<typename Descriptor, typename Name>
inline ani_variable ani_cache_module_variable(ani_env *env)
{
    static ani_variable variable = ani_find_module_variable(env, ani_cache_module<Descriptor>(env), TH_AS_C_STR(Name));
    return variable;
}

template<typename Descriptor, typename Name>
inline ani_variable ani_cache_namespace_variable(ani_env *env)
{
    static ani_variable variable =
        ani_find_namespace_variable(env, ani_cache_namespace<Descriptor>(env), TH_AS_C_STR(Name));
    return variable;
}

template<typename Descriptor, typename Name>
inline ani_field ani_cache_class_field(ani_env *env)
{
    static ani_field field = ani_find_class_field(env, ani_cache_class<Descriptor>(env), TH_AS_C_STR(Name));
    return field;
}

template<typename Descriptor, typename Name>
inline ani_static_field ani_cache_class_static_field(ani_env *env)
{
    static ani_static_field field =
        ani_find_class_static_field(env, ani_cache_class<Descriptor>(env), TH_AS_C_STR(Name));
    return field;
}
}  // namespace taihe

#define TH_ANI_FIND_MODULE(env, descriptor) taihe::ani_cache_module<TH_AS_CT_STRING_T(descriptor)>(env)
#define TH_ANI_FIND_NAMESPACE(env, descriptor) taihe::ani_cache_namespace<TH_AS_CT_STRING_T(descriptor)>(env)
#define TH_ANI_FIND_CLASS(env, descriptor) taihe::ani_cache_class<TH_AS_CT_STRING_T(descriptor)>(env)
#define TH_ANI_FIND_ENUM(env, descriptor) taihe::ani_cache_enum<TH_AS_CT_STRING_T(descriptor)>(env)

#define TH_ANI_FIND_MODULE_FUNCTION(env, descriptor, name, signature)                        \
    taihe::ani_cache_module_function<TH_AS_CT_STRING_T(descriptor), TH_AS_CT_STRING_T(name), \
                                     TH_AS_CT_STRING_T(signature)>(env)
#define TH_ANI_FIND_NAMESPACE_FUNCTION(env, descriptor, name, signature)                        \
    taihe::ani_cache_namespace_function<TH_AS_CT_STRING_T(descriptor), TH_AS_CT_STRING_T(name), \
                                        TH_AS_CT_STRING_T(signature)>(env)
#define TH_ANI_FIND_CLASS_METHOD(env, descriptor, name, signature)                        \
    taihe::ani_cache_class_method<TH_AS_CT_STRING_T(descriptor), TH_AS_CT_STRING_T(name), \
                                  TH_AS_CT_STRING_T(signature)>(env)
#define TH_ANI_FIND_CLASS_STATIC_METHOD(env, descriptor, name, signature)                        \
    taihe::ani_cache_class_static_method<TH_AS_CT_STRING_T(descriptor), TH_AS_CT_STRING_T(name), \
                                         TH_AS_CT_STRING_T(signature)>(env)

#define TH_ANI_FIND_MODULE_VARIABLE(env, descriptor, name) \
    taihe::ani_cache_module_variable<TH_AS_CT_STRING_T(descriptor), TH_AS_CT_STRING_T(name)>(env)
#define TH_ANI_FIND_NAMESPACE_VARIABLE(env, descriptor, name) \
    taihe::ani_cache_namespace_variable<TH_AS_CT_STRING_T(descriptor), TH_AS_CT_STRING_T(name)>(env)
#define TH_ANI_FIND_CLASS_FIELD(env, descriptor, name) \
    taihe::ani_cache_class_field<TH_AS_CT_STRING_T(descriptor), TH_AS_CT_STRING_T(name)>(env)
#define TH_ANI_FIND_CLASS_STATIC_FIELD(env, descriptor, name) \
    taihe::ani_cache_class_static_field<TH_AS_CT_STRING_T(descriptor), TH_AS_CT_STRING_T(name)>(env)

#endif  // TAIHE_PLATFORM_ANI_HPP
