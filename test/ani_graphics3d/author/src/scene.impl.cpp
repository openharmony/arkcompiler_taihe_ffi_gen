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

// This file is a test file.
// NOLINTBEGIN
#include "scene.impl.hpp"
#include "scene.proj.hpp"
#include "sceneNodeParameters.h"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

class CameraImpl {
public:
    float fov_ = 5.24;

    CameraImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetFov(float fov)
    {
        this->fov_ = fov;
        return {};
    }

    ::taihe::expected<float, ::taihe::error> GetFov()
    {
        return fov_;
    }
};

class LightImpl {
public:
    float intens_ = 5.24;

    LightImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetIntensity(float intens)
    {
        this->intens_ = intens;
        return {};
    }

    ::taihe::expected<float, ::taihe::error> GetIntensity()
    {
        return intens_;
    }
};

class NodeImpl {
public:
    bool visible_ = true;
    ::taihe::string path = "test\ani_graphics3d";

    NodeImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetVisible(bool visible)
    {
        this->visible_ = visible;
        return {};
    }

    ::taihe::expected<bool, ::taihe::error> GetVisible()
    {
        return visible_;
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetPath()
    {
        return path;
    }
};

class SceneResourceParametersImpl {
public:
    std::string name_ = "Scene";

    SceneResourceParametersImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetName(::taihe::string_view name)
    {
        this->name_ = name;
        return {};
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetName()
    {
        return name_;
    }
};

class MaterialImpl {
public:
    int8_t materialType = 122;

    MaterialImpl()
    {
    }

    ::taihe::expected<int8_t, ::taihe::error> GetMaterialType()
    {
        return materialType;
    }
};

class ShaderImpl {
public:
    ShaderImpl()
    {
    }

    ::taihe::expected<::taihe::map<::taihe::string, int32_t>, ::taihe::error> GetInputs()
    {
        ::taihe::map<::taihe::string, int32_t> res;
        static int32_t const input = 2025;
        res.emplace("banana", input);
        return res;
    }
};

class ImageImpl {
public:
    float width = 800;
    float height = 600;

    ImageImpl()
    {
    }

    ::taihe::expected<float, ::taihe::error> GetWidth()
    {
        return width;
    }

    ::taihe::expected<float, ::taihe::error> GetHeight()
    {
        return height;
    }
};

class EnvironmentImpl {
public:
    EnvironmentImpl()
    {
    }

    ::taihe::expected<int32_t, ::taihe::error> GetBackgroundType()
    {
        int32_t bkType = 0;
        return bkType;
    }
};

class SceneResourceFactoryImpl {
public:
    SceneResourceFactoryImpl()
    {
    }

    ::taihe::expected<::scene::Camera, ::taihe::error> createCameraPro(
        ::sceneNodeParameters::weak::SceneNodeParameters params)
    {
        return taihe::make_holder<CameraImpl, ::scene::Camera>();
    }

    ::taihe::expected<::scene::Light, ::taihe::error> createLightPro(
        ::sceneNodeParameters::weak::SceneNodeParameters params, ::scene::LightType lightType)
    {
        return taihe::make_holder<LightImpl, ::scene::Light>();
    }

    ::taihe::expected<::scene::Node, ::taihe::error> createNodePro(
        ::sceneNodeParameters::weak::SceneNodeParameters params)
    {
        return taihe::make_holder<NodeImpl, ::scene::Node>();
    }

    ::taihe::expected<::scene::Material, ::taihe::error> createMaterialPro(
        ::scene::weak::SceneResourceParameters params, ::scene::MaterialType materialType)
    {
        return taihe::make_holder<MaterialImpl, ::scene::Material>();
    }

    ::taihe::expected<::scene::Shader, ::taihe::error> createShaderPro(::scene::weak::SceneResourceParameters params)
    {
        return taihe::make_holder<ShaderImpl, ::scene::Shader>();
    }

    ::taihe::expected<::scene::Image, ::taihe::error> createImagePro(::scene::weak::SceneResourceParameters params)
    {
        return taihe::make_holder<ImageImpl, ::scene::Image>();
    }

    ::taihe::expected<::scene::Environment, ::taihe::error> createEnvironmentPro(
        ::scene::weak::SceneResourceParameters params)
    {
        return taihe::make_holder<EnvironmentImpl, ::scene::Environment>();
    }
};

::taihe::expected<::scene::SceneResourceFactory, ::taihe::error> GetSceneResourceFactory()
{
    return taihe::make_holder<SceneResourceFactoryImpl, ::scene::SceneResourceFactory>();
}

::taihe::expected<::scene::Camera, ::taihe::error> GetCamera()
{
    return taihe::make_holder<CameraImpl, ::scene::Camera>();
}

::taihe::expected<::scene::Light, ::taihe::error> GetLight()
{
    return taihe::make_holder<LightImpl, ::scene::Light>();
}

::taihe::expected<::scene::Node, ::taihe::error> GetNode()
{
    return taihe::make_holder<NodeImpl, ::scene::Node>();
}

::taihe::expected<::scene::SceneResourceParameters, ::taihe::error> GetSceneResourceParameters()
{
    return taihe::make_holder<SceneResourceParametersImpl, ::scene::SceneResourceParameters>();
}

::taihe::expected<::scene::Material, ::taihe::error> GetMaterial()
{
    return taihe::make_holder<MaterialImpl, ::scene::Material>();
}

::taihe::expected<::scene::Shader, ::taihe::error> GetShader()
{
    return taihe::make_holder<ShaderImpl, ::scene::Shader>();
}

::taihe::expected<::scene::Image, ::taihe::error> GetImage()
{
    return taihe::make_holder<ImageImpl, ::scene::Image>();
}

::taihe::expected<::scene::Environment, ::taihe::error> GetEnvironment()
{
    return taihe::make_holder<EnvironmentImpl, ::scene::Environment>();
}
}  // namespace

TH_EXPORT_CPP_API_GetSceneResourceFactory(GetSceneResourceFactory);
TH_EXPORT_CPP_API_GetCamera(GetCamera);
TH_EXPORT_CPP_API_GetLight(GetLight);
TH_EXPORT_CPP_API_GetNode(GetNode);
TH_EXPORT_CPP_API_GetSceneResourceParameters(GetSceneResourceParameters);
TH_EXPORT_CPP_API_GetMaterial(GetMaterial);
TH_EXPORT_CPP_API_GetShader(GetShader);
TH_EXPORT_CPP_API_GetImage(GetImage);
TH_EXPORT_CPP_API_GetEnvironment(GetEnvironment);
// NOLINTEND
