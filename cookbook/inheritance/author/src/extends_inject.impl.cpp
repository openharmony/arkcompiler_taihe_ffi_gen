#include "extends_inject.impl.hpp"
#include "stdexcept"
#include "extends_inject.InnerPerson.proj.2.hpp"
#include "core/runtime.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
class InnerPerson {
public:
    uintptr_t getPseron() {
        ani_long ani_vtbl_ptr;
        ani_long ani_data_ptr;
        ani_class ani_obj_cls;
        ani_env* env = get_env();
        env->FindClass("LPerson/Person;", &ani_obj_cls);
        ani_method ani_obj_ctor;
        env->Class_FindMethod(ani_obj_cls, "<ctor>", nullptr, &ani_obj_ctor);
        ani_object ani_obj;
        env->Object_New(ani_obj_cls, ani_obj_ctor, &ani_obj, ani_vtbl_ptr, ani_data_ptr);
        return reinterpret_cast<uintptr_t>(ani_obj);
    }

    ::extends_inject::InnerPerson getInnerPerson() {
        return make_holder<InnerPerson, ::extends_inject::InnerPerson>();
    }
};
::extends_inject::InnerPerson makePerson() {
    return make_holder<InnerPerson, ::extends_inject::InnerPerson>();
}
}
TH_EXPORT_CPP_API_makePerson(makePerson);
