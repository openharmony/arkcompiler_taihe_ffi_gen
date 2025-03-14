#include "huks.ani.hpp"

ANI_EXPORT ani_status ANI_Constructor(ani_vm *vm, uint32_t *result) {
    ani_env *env;
    if (ANI_OK != vm->GetEnv(ANI_VERSION_1, &env)) {
        return ANI_ERROR;
    }
    if (ANI_OK != huks::ANIRegister(env)) {
        return ANI_ERROR;
    }
    *result = ANI_VERSION_1;
    return ANI_OK;
}
