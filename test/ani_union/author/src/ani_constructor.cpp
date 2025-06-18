#include "test_union.ani.hpp"
#include "union_ani.ani.hpp"

#if __has_include(<ani.h>)
#include <ani.h>
#elif __has_include(<ani/ani.h>)
#include <ani/ani.h>
#else
#error "ani.h not found. Please ensure the Ani SDK is correctly installed."
#endif

ANI_EXPORT ani_status ANI_Constructor(ani_vm *vm, uint32_t *result) {
  ani_env *env;
  if (ANI_OK != vm->GetEnv(ANI_VERSION_1, &env)) {
    return ANI_ERROR;
  }
  if (ANI_OK != union_ani::ANIRegister(env)) {
    std::cerr << "Error from union_ani::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != test_union::ANIRegister(env)) {
    std::cerr << "Error from test_union::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  *result = ANI_VERSION_1;
  return ANI_OK;
}
