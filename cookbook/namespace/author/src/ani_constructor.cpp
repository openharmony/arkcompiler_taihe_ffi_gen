#include "module1.ani.hpp"
#include "module1.foo.ani.hpp"
#include "module2.bar.ani.hpp"

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
  if (ANI_OK != module2::bar::ANIRegister(env)) {
    std::cerr << "Error from module2::bar::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != module1::ANIRegister(env)) {
    std::cerr << "Error from module1::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  if (ANI_OK != module1::foo::ANIRegister(env)) {
    std::cerr << "Error from module1::foo::ANIRegister" << std::endl;
    return ANI_ERROR;
  }
  *result = ANI_VERSION_1;
  return ANI_OK;
}
