#include "export_enum.ani.hpp"
#include "export_iface.ani.hpp"
#include "export_namespace.ani.hpp"
#include "export_struct.ani.hpp"
#include "export_union.ani.hpp"
#include "import_example.ani.hpp"
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
  ani_status status = ANI_OK;
  if (ANI_OK != export_enum::ANIRegister(env)) {
    std::cerr << "Error from export_enum::ANIRegister" << std::endl;
    status = ANI_ERROR;
  }
  if (ANI_OK != export_namespace::ANIRegister(env)) {
    std::cerr << "Error from export_namespace::ANIRegister" << std::endl;
    status = ANI_ERROR;
  }
  if (ANI_OK != export_union::ANIRegister(env)) {
    std::cerr << "Error from export_union::ANIRegister" << std::endl;
    status = ANI_ERROR;
  }
  if (ANI_OK != import_example::ANIRegister(env)) {
    std::cerr << "Error from import_example::ANIRegister" << std::endl;
    status = ANI_ERROR;
  }
  if (ANI_OK != export_struct::ANIRegister(env)) {
    std::cerr << "Error from export_struct::ANIRegister" << std::endl;
    status = ANI_ERROR;
  }
  if (ANI_OK != export_iface::ANIRegister(env)) {
    std::cerr << "Error from export_iface::ANIRegister" << std::endl;
    status = ANI_ERROR;
  }
  *result = ANI_VERSION_1;
  return status;
}
