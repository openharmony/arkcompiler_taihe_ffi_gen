#pragma once

#include <taihe/string.hpp>

#include <ani.h>

namespace taihe {
// VM and Environment related functions

void set_vm(ani_vm *vm);
ani_vm *get_vm();
ani_env *get_env();

class env_guard {
  ani_env *env;
  bool is_attached;

public:
  env_guard();
  ~env_guard();

  env_guard(env_guard const &) = delete;
  env_guard &operator=(env_guard const &) = delete;
  env_guard(env_guard &&) = delete;
  env_guard &operator=(env_guard &&) = delete;

  ani_env *get_env() {
    return env;
  }
};

// Reference management

class ref_guard {
  ani_ref ref;

public:
  ref_guard(ani_env *env, ani_ref val);
  ~ref_guard();

  ref_guard(ref_guard const &) = delete;
  ref_guard &operator=(ref_guard const &) = delete;
  ref_guard(ref_guard &&) = delete;
  ref_guard &operator=(ref_guard &&) = delete;

  ani_ref get_ref() {
    return ref;
  }
};

// Other utility functions

template<char const *descriptor>
inline ani_module get_module(ani_env *env) {
  static ref_guard ref(env, [env]() -> ani_module {
    ani_module mod;
    if (ANI_OK != env->FindModule(descriptor, &mod)) {
      std::cerr << "Module not found: " << descriptor << std::endl;
      return nullptr;
    }
    return mod;
  }());
  return static_cast<ani_module>(ref.get_ref());
}

template<char const *descriptor>
inline ani_namespace get_namespace(ani_env *env) {
  static ref_guard ref(env, [env]() -> ani_namespace {
    ani_namespace ns;
    if (ANI_OK != env->FindNamespace(descriptor, &ns)) {
      std::cerr << "Namespace not found: " << descriptor << std::endl;
      return nullptr;
    }
    return ns;
  }());
  return static_cast<ani_namespace>(ref.get_ref());
}

template<char const *descriptor>
inline ani_class get_class(ani_env *env) {
  static ref_guard ref(env, [env]() -> ani_class {
    ani_class cls;
    if (ANI_OK != env->FindClass(descriptor, &cls)) {
      std::cerr << "Class not found: " << descriptor << std::endl;
      return nullptr;
    }
    return cls;
  }());
  return static_cast<ani_class>(ref.get_ref());
}

template<char const *descriptor, char const *name, char const *signature>
inline ani_function get_module_function(ani_env *env) {
  static ani_function func = [env]() -> ani_function {
    ani_module mod = get_module<descriptor>(env);
    if (mod == nullptr) {
      return nullptr;
    }
    ani_function fn;
    if (ANI_OK != env->Module_FindFunction(mod, name, signature, &fn)) {
      std::cerr << "Function not found: " << descriptor << "::" << name
                << " with signature: " << signature << std::endl;
      return nullptr;
    }
    return fn;
  }();
  return func;
}

template<char const *descriptor, char const *name, char const *signature>
inline ani_function get_namespace_function(ani_env *env) {
  static ani_function func = [env]() -> ani_function {
    ani_namespace ns = get_namespace<descriptor>(env);
    if (ns == nullptr) {
      return nullptr;
    }
    ani_function fn;
    if (ANI_OK != env->Namespace_FindFunction(ns, name, signature, &fn)) {
      std::cerr << "Function not found: " << descriptor << "::" << name
                << " with signature: " << signature << std::endl;
      return nullptr;
    }
    return fn;
  }();
  return func;
}

template<char const *descriptor, char const *name, char const *signature>
inline ani_method get_class_method(ani_env *env) {
  static ani_method method = [env]() -> ani_method {
    ani_class cls = get_class<descriptor>(env);
    if (cls == nullptr) {
      return nullptr;
    }
    ani_method mtd;
    if (ANI_OK != env->Class_FindMethod(cls, name, signature, &mtd)) {
      std::cerr << "Method not found: " << descriptor << "::" << name
                << " with signature: " << signature << std::endl;
      return nullptr;
    }
    return mtd;
  }();
  return method;
}

template<char const *descriptor, char const *name, char const *signature>
inline ani_static_method get_class_static_method(ani_env *env) {
  static ani_static_method method = [env]() -> ani_static_method {
    ani_class cls = get_class<descriptor>(env);
    if (cls == nullptr) {
      return nullptr;
    }
    ani_static_method mtd;
    if (ANI_OK != env->Class_FindStaticMethod(cls, name, signature, &mtd)) {
      std::cerr << "Static method not found: " << descriptor << "::" << name
                << " with signature: " << signature << std::endl;
      return nullptr;
    }
    return mtd;
  }();
  return method;
}

template<char const *descriptor, char const *name>
inline ani_variable get_module_variable(ani_env *env) {
  static ani_variable var = [env]() -> ani_variable {
    ani_module mod = get_module<descriptor>(env);
    if (mod == nullptr) {
      return nullptr;
    }
    ani_variable v;
    if (ANI_OK != env->Module_FindVariable(mod, name, &v)) {
      std::cerr << "Variable not found: " << descriptor << "::" << name
                << std::endl;
      return nullptr;
    }
    return v;
  }();
  return var;
}

template<char const *descriptor, char const *name>
inline ani_variable get_namespace_variable(ani_env *env) {
  static ani_variable var = [env]() -> ani_variable {
    ani_namespace ns = get_namespace<descriptor>(env);
    if (ns == nullptr) {
      return nullptr;
    }
    ani_variable v;
    if (ANI_OK != env->Namespace_FindVariable(ns, name, &v)) {
      std::cerr << "Variable not found: " << descriptor << "::" << name
                << std::endl;
      return nullptr;
    }
    return v;
  }();
  return var;
}

template<char const *descriptor, char const *name>
inline ani_field get_class_field(ani_env *env) {
  static ani_field field = [env]() -> ani_field {
    ani_class cls = get_class<descriptor>(env);
    if (cls == nullptr) {
      return nullptr;
    }
    ani_field fld;
    if (ANI_OK != env->Class_FindField(cls, name, &fld)) {
      std::cerr << "Field not found: " << descriptor << "::" << name
                << std::endl;
      return nullptr;
    }
    return fld;
  }();
  return field;
}

template<char const *descriptor, char const *name>
inline ani_static_field get_class_static_field(ani_env *env) {
  static ani_static_field field = [env]() -> ani_static_field {
    ani_class cls = get_class<descriptor>(env);
    if (cls == nullptr) {
      return nullptr;
    }
    ani_static_field fld;
    if (ANI_OK != env->Class_FindStaticField(cls, name, &fld)) {
      std::cerr << "Static field not found: " << descriptor << "::" << name
                << std::endl;
      return nullptr;
    }
    return fld;
  }();
  return field;
}

// Error handling functions

void set_error(taihe::string_view msg);
void set_business_error(int32_t err_code, taihe::string_view msg);
void reset_error();
bool has_error();
}  // namespace taihe
