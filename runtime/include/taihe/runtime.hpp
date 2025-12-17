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

#ifndef TAIHE_RUNTIME_HPP
#define TAIHE_RUNTIME_HPP

#if !defined(USE_ANI_RUNTIME) && !defined(USE_NAPI_RUNTIME)
#define USE_ANI_RUNTIME
#endif

#if defined(USE_ANI_RUNTIME)
#include <taihe/runtime_ani.hpp>
#elif defined(USE_NAPI_RUNTIME)
#include <taihe/runtime_napi.hpp>
#endif

#endif  // TAIHE_RUNTIME_HPP
