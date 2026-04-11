/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
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

const abilityInfo = requireNapi('./abilityInfo.so', RequireBaseDir.SCRIPT_DIR);
const applicationInfo = requireNapi('./applicationInfo.so', RequireBaseDir.SCRIPT_DIR);
const bundleInfo = requireNapi('./bundleInfo.so', RequireBaseDir.SCRIPT_DIR);
const elementName = requireNapi('./elementName.so', RequireBaseDir.SCRIPT_DIR);
const extensionAbilityInfo = requireNapi('./extensionAbilityInfo.so', RequireBaseDir.SCRIPT_DIR);
const hapModuleInfo = requireNapi('./hapModuleInfo.so', RequireBaseDir.SCRIPT_DIR);
const metadata = requireNapi('./metadata.so', RequireBaseDir.SCRIPT_DIR);
const overlayModuleInfo = requireNapi('./overlayModuleInfo.so', RequireBaseDir.SCRIPT_DIR);
const skillTest = requireNapi('./skill.so', RequireBaseDir.SCRIPT_DIR);
const ohos = requireNapi('./ohos.so', RequireBaseDir.SCRIPT_DIR);

let intDig = 21474;

// Skill.d.ts
let skill: skillTest.Skill = skillTest.GetSkill();
function test_bundlemanager_interface_skill_with_actions() {
    let info = skill.actions[0];

    console.log("skill.actions is: " + info);
    if (info !== "SkillImpl::getActions") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_skill_with_entities() {
    let info = skill.entities[0];

    console.log("skill.entities is: " + info);
    if (info !== "SkillImpl::getEntities") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_skill_with_domainVerify() {
    let info = skill.domainVerify;

    console.log("skill.domainVerify is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

let skillUri: skillTest.SkillUri = skillTest.GetSkillUri();
function test_bundlemanager_interface_skilluri_with_scheme() {
    let info = skillUri.scheme;

    console.log("skillUri.scheme is: " + info);
    if (info !== "SkillUriImpl::getScheme") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_skilluri_with_host() {
    let info = skillUri.host;

    console.log("skillUri.host is: " + info);
    if (info !== "SkillUriImpl::getHost") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_skilluri_with_port() {
    let info = skillUri.port;

    console.log("skillUri.host is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_skilluri_with_path() {
    let info = skillUri.path;

    console.log("skillUri.path is: " + info);
    if (info !== "SkillUriImpl::getPath") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_skilluri_with_pathStartWith() {
    let info = skillUri.pathStartWith;

    console.log("skillUri.pathStartWith is: " + info);
    if (info !== "SkillUriImpl::getPathStartWith") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_skilluri_with_pathRegex() {
    let info = skillUri.pathRegex;

    console.log("skillUri.pathRegex is: " + info);
    if (info !== "SkillUriImpl::getPathRegex") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_skilluri_with_type() {
    let info = skillUri.type;

    console.log("skillUri.type is: " + info);
    if (info !== "SkillUriImpl::getType") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_skilluri_with_utd() {
    let info = skillUri.utd;

    console.log("skillUri.utd is: " + info);
    if (info !== "SkillUriImpl::getUtd") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_skilluri_with_maxFileSupported() {
    let info = skillUri.maxFileSupported;

    console.log("skillUri.maxFileSupported is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_skilluri_with_linkFeature() {
    let info = skillUri.linkFeature;

    console.log("skillUri.linkFeature is: " + info);
    if (info !== "SkillUriImpl::getLinkFeature") throw new Error(`Unexpected result`);
}

// Abilityinfo.d.ts
let abiInfo: abilityInfo.AbilityInfo = abilityInfo.GetAbilityInfo();
function test_bundlemanager_interface_abilityinfo_with_bundleName() {
    let info = abiInfo.bundleName;

    console.log("abiInfo.bundleName is: " + info);
    if (info !== "abilityInfoImpl::getBundleName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_moduleName() {
    let info = abiInfo.moduleName;

    console.log("abiInfo.moduleName is: " + info);
    if (info !== "abilityInfoImpl::getModuleName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_name() {
    let info = abiInfo.name;

    console.log("abiInfo.name is: " + info);
    if (info !== "abilityInfoImpl::getName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_label() {
    let info = abiInfo.label;

    console.log("abiInfo.label is: " + info);
    if (info !== "abilityInfoImpl::getLabel") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_labelId() {
    let info = abiInfo.labelId;

    console.log("abiInfo.labelId is: " + info);
    if (info !== 506) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_description() {
    let info = abiInfo.description;

    console.log("abiInfo.description is: " + info);
    if (info !== "abilityInfoImpl::getDescription") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_descriptionId() {
    let info = abiInfo.descriptionId;

    console.log("abiInfo.descriptionId is: " + info);
    if (info !== 506) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_icon() {
    let info = abiInfo.icon;

    console.log("abiInfo.icon is: " + info);
    if (info !== "abilityInfoImpl::getIcon") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_iconId() {
    let info = abiInfo.iconId;

    console.log("abiInfo.iconId is: " + info);
    if (info !== 506) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_process() {
    let info = abiInfo.process;

    console.log("abiInfo.process is: " + info);
    if (info !== "abilityInfoImpl::getProcess") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_exported() {
    let info = abiInfo.exported;

    console.log("abiInfo.exported is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_type() {
    let info = abiInfo.type;

    console.log("abiInfo.type is: " + info);
    if (info !== abiInfo.type) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_orientation() {
    let info = abiInfo.orientation;

    console.log("abiInfo.orientation is: " + info);
    if (info !== abiInfo.orientation) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_launchType() {
    let info = abiInfo.launchType;

    console.log("abiInfo.launchType is: " + info);
    if (info !== abiInfo.launchType) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_permissions() {
    let info = abiInfo.permissions[0];

    console.log("abiInfo.permissions is: " + info);
    if (info !== "abilityInfoImpl::getPermissions") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_readPermission() {
    let info = abiInfo.readPermission;

    console.log("abiInfo.readPermission is: " + info);
    if (info !== "abilityInfoImpl::getReadPermission") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_writePermission() {
    let info = abiInfo.writePermission;

    console.log("abiInfo.writePermission is: " + info);
    if (info !== "abilityInfoImpl::getWritePermission") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_uri() {
    let info = abiInfo.uri;

    console.log("abiInfo.uri is: " + info);
    if (info !== "abilityInfoImpl::getUri") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_deviceTypes() {
    let info = abiInfo.deviceTypes[0];

    console.log("abiInfo.deviceTypes is: " + info);
    if (info !== "abilityInfoImpl::getDeviceTypes") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_metadata() {
    let info = abiInfo.metadata[0].name;

    console.log("abiInfo.metadata is: " + info);
    if (info !== "metadate.name") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_enabled() {
    let info = abiInfo.enabled;

    console.log("abiInfo.enabled is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_supportWindowModes() {
    let info = abiInfo.supportWindowModes[0];

    console.log("abiInfo.type is: " + info);
    if (info !== ohos.bundle.bundleManager.SupportWindowMode.FLOATING) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_excludeFromDock() {
    let info = abiInfo.excludeFromDock;

    console.log("abiInfo.excludeFromDock is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_skills() {
    let info = abiInfo.skills[0].actions[0];

    console.log("abiInfo.skills is: " + info);
    if (info !== "SkillImpl::getActions") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_appIndex() {
    let info = abiInfo.appIndex;

    console.log("abiInfo.appIndex is: " + info);
    if (info !== 506) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_abilityinfo_with_orientationId() {
    let info = abiInfo.orientationId;

    console.log("abiInfo.orientationId is: " + info);
    if (info !== 506) throw new Error(`Unexpected result`);
}

// OverlayModuleInfo.d.ts
let overInfo: overlayModuleInfo.OverlayModuleInfo =
    overlayModuleInfo.GetOverlayModuleInfo();
function test_bundlemanager_interface_overlaymoduleinfo_with_bundleName() {
    let info = overInfo.bundleName;

    console.log("overInfo.bundleName is: " + info);
    if (info !== "OverlayModuleInfoImpl::getBundleName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_overlaymoduleinfo_with_moduleName() {
    let info = overInfo.moduleName;

    console.log("overInfo.moduleName is: " + info);
    if (info !== "OverlayModuleInfoImpl::getModuleName") throw new Error(`Unexpected result`);
}

function
test_bundlemanager_interface_overlaymoduleinfo_with_targetModuleName() {
    let info = overInfo.targetModuleName;

    console.log("overInfo.targetModuleName is: " + info);
    if (info !== "OverlayModuleInfoImpl::getTargetModuleName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_overlaymoduleinfo_with_priority() {
    let info = overInfo.priority;

    console.log("overInfo.priority is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_overlaymoduleinfo_with_state() {
    let info = overInfo.state;

    console.log("overInfo.state is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

// Metadata.d.ts
let metadata_: metadata.Metadata = metadata.GetMetadata();
function test_bundlemanager_interface_metadata_with_name() {
    let info = metadata_.name;
    console.log("old metadata.name is: " + info);
    if (info !== "metadate.name") throw new Error(`Unexpected result`);
    
    metadata_.name = "bob";
    info = metadata_.name;
    console.log("new metadata.name is: " + info);
    if (info !== "bob") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_metadata_with_value() {
    let info = metadata_.value;
    console.log("old metadata.value is: " + info);
    if (info !== "metadate.value") throw new Error(`Unexpected result`);
    
    metadata_.value = "apple";
    info = metadata_.value;
    console.log("new metadata.value is: " + info);
    if (info !== "apple") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_metadata_with_resource() {
    let info = metadata_.resource;
    console.log("old metadata.resource is: " + info);
    if (info !== "metadate.resource") throw new Error(`Unexpected result`);
    
    metadata_.resource = "food";
    info = metadata_.resource;
    console.log("new metadata.resource is: " + info);
    if (info !== "food") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_metadata_with_valueId() {
    let info = metadata_.valueId;

    console.log("metadata.valueId is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

// HapModuleInfo.d.ts
let hapInfo: hapModuleInfo.HapModuleInfo = hapModuleInfo.GetHapModuleInfo();
let dependency: hapModuleInfo.Dependency = hapModuleInfo.GetDependency();
let preloadItem: hapModuleInfo.PreloadItem = hapModuleInfo.GetPreloadItem();
let routerItem: hapModuleInfo.RouterItem = hapModuleInfo.GetRouterItem();
let dataItem: hapModuleInfo.DataItem = hapModuleInfo.GetDataItem();
function test_bundlemanager_interface_hapmoduleinfo_with_name() {
    let info = hapInfo.name;

    console.log("hapInfo.name is: " + info);
    if (info !== "HapModuleInfoImpl::getName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_icon() {
    let info = hapInfo.icon;

    console.log("hapInfo.icon is: " + info);
    if (info !== "HapModuleInfoImpl::getIcon") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_iconId() {
    let info = hapInfo.iconId;

    console.log("hapInfo.iconId is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_label() {
    let info = hapInfo.label;

    console.log("hapInfo.label is: " + info);
    if (info !== "HapModuleInfoImpl::getLabel") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_labelId() {
    let info = hapInfo.labelId;

    console.log("hapInfo.labelId is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_description() {
    let info = hapInfo.description;

    console.log("hapInfo.description is: " + info);
    if (info !== "HapModuleInfoImpl::getDescription") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_descriptionId() {
    let info = hapInfo.descriptionId;

    console.log("hapInfo.descriptionId is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_mainElementName() {
    let info = hapInfo.mainElementName;

    console.log("hapInfo.mainElementName is: " + info);
    if (info !== "HapModuleInfoImpl::getMainElementName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_deviceTypes() {
    let info = hapInfo.deviceTypes[0];

    console.log("hapInfo.deviceTypes is: " + info);
    if (info !== "HapModuleInfoImpl::getDeviceTypes") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_installationFree() {
    let info = hapInfo.installationFree;

    console.log("hapInfo.installationFree is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_hashValue() {
    let info = hapInfo.hashValue;

    console.log("hapInfo.hashValue is: " + info);
    if (info !== "HapModuleInfoImpl::getHashValue") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_fileContextMenuConfig() {
    let info = hapInfo.fileContextMenuConfig;

    console.log("hapInfo.fileContextMenuConfig is: " + info);
    if (info !== "HapModuleInfoImpl::getFileContextMenuConfig") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_nativeLibraryPath() {
    let info = hapInfo.nativeLibraryPath;

    console.log("hapInfo.nativeLibraryPath is: " + info);
    if (info !== "HapModuleInfoImpl::getNativeLibraryPath") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_hapmoduleinfo_with_codePath() {
    let info = hapInfo.codePath;

    console.log("hapInfo.codePath is: " + info);
    if (info !== "HapModuleInfoImpl::getCodePath") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_dependency_with_moduleName() {
    let info = dependency.moduleName;

    console.log("dependency.moduleName is: " + info);
    if (info !== "HapModuleInfoImpl::getModuleName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_dependency_with_bundleName() {
    let info = dependency.bundleName;

    console.log("dependency.bundleName is: " + info);
    if (info !== "HapModuleInfoImpl::getBundleName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_dependency_with_versionCode() {
    let info = dependency.versionCode;

    console.log("dependency.versionCode is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_preloaditem_with_moduleName() {
    let info = preloadItem.moduleName;

    console.log("preloadItem.moduleName is: " + info);
    if (info !== "PreloadItemImpl::getModuleName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_routerItem_with_name() {
    let info = routerItem.name;

    console.log("routerItem.name is: " + info);
    if (info !== "RouterItemImpl::getName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_routerItem_with_pageSourceFile() {
    let info = routerItem.pageSourceFile;

    console.log("routerItem.pageSourceFile is: " + info);
    if (info !== "RouterItemImpl::getPageSourceFile") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_routerItem_with_buildFunction() {
    let info = routerItem.buildFunction;

    console.log("routerItem.buildFunction is: " + info);
    if (info !== "RouterItemImpl::getBuildFunction") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_routerItem_with_customData() {
    let info = routerItem.customData;

    console.log("routerItem.customData is: " + info);
    if (info !== "RouterItemImpl::getCustomData") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_dataItem_with_key() {
    let info = dataItem.key;

    console.log("dataItem.key is: " + info);
    if (info !== "DataItemImpl::getKey") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_dataItem_with_value() {
    let info = dataItem.value;

    console.log("dataItem.value is: " + info);
    if (info !== "DataItemImpl::getValue") throw new Error(`Unexpected result`);
}

// ExtensionAbilityInfo.d.ts
let exAbiInfo: extensionAbilityInfo.ExtensionAbilityInfo =
    extensionAbilityInfo.GetExtensionAbilityInfo();
function test_bundlemanager_interface_extensionAbilityInfo_with_bundleName() {
    let info = exAbiInfo.bundleName;

    console.log("exAbiInfo.bundleName is: " + info);
    if (info !== "ExtensionAbilityInfoImpl::getBundleName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_extensionAbilityInfo_with_moduleName() {
    let info = exAbiInfo.moduleName;

    console.log("exAbiInfo.moduleName is: " + info);
    if (info !== "ExtensionAbilityInfoImpl::getModuleName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_extensionAbilityInfo_with_name() {
    let info = exAbiInfo.name;

    console.log("exAbiInfo.name is: " + info);
    if (info !== "ExtensionAbilityInfoImpl::getName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_extensionAbilityInfo_with_labelId() {
    let info = exAbiInfo.labelId;

    console.log("exAbiInfo.labelId is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_extensionAbilityInfo_with_descriptionId() {
    let info = exAbiInfo.descriptionId;

    console.log("abiIexAbiInfonfo.descriptionId is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_extensionAbilityInfo_with_iconId() {
    let info = exAbiInfo.iconId;

    console.log("exAbiInfo.iconId is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_extensionAbilityInfo_with_exported() {
    let info = exAbiInfo.exported;

    console.log("exAbiInfo.exported is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function
test_bundlemanager_interface_extensionAbilityInfo_with_extensionAbilityTypeName() {
    let info = exAbiInfo.extensionAbilityTypeName;

    console.log("exAbiInfo.extensionAbilityTypeName is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_extensionAbilityInfo_with_permissions() {
    let info = exAbiInfo.permissions[0];

    console.log("exAbiInfo.permissions is: " + info);
    if (info !== "ExtensionAbilityInfoImpl::getPermissions") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_extensionAbilityInfo_with_enabled() {
    let info = exAbiInfo.enabled;

    console.log("exAbiInfo.enabled is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_extensionAbilityInfo_with_readPermission() {
    let info = exAbiInfo.readPermission;

    console.log("exAbiInfo.readPermission is: " + info);
    if (info !== "ExtensionAbilityInfoImpl::getReadPermission") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_extensionAbilityInfo_with_writePermission() {
    let info = exAbiInfo.writePermission;

    console.log("exAbiInfo.writePermission is: " + info);
    if (info !== "ExtensionAbilityInfoImpl::getWritePermission") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_extensionAbilityInfo_with_appIndex() {
    let info = exAbiInfo.appIndex;

    console.log("exAbiInfo.appIndex is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

// ApplicationInfo.d.ts
let appLicaInfo: applicationInfo.ApplicationInfo =
    applicationInfo.GetApplicationInfo();
let moudleMData: applicationInfo.ModuleMetadata =
    applicationInfo.GetModuleMetadata();
let multiMode: applicationInfo.MultiAppMode = applicationInfo.GetMultiAppMode();
function test_bundlemanager_interface_applicationInfo_with_name() {
    let info = appLicaInfo.name;

    console.log("appLicaInfo.name is: " + info);
    if (info !== "ApplicationInfoImpl::getName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_description() {
    let info = appLicaInfo.description;

    console.log("appLicaInfo.description is: " + info);
    if (info !== "ApplicationInfoImpl::getDescription") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_descriptionId() {
    let info = appLicaInfo.descriptionId;

    console.log("appLicaInfo.descriptionId is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_enabled() {
    let info = appLicaInfo.enabled;

    console.log("appLicaInfo.enabled is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_label() {
    let info = appLicaInfo.label;

    console.log("appLicaInfo.label is: " + info);
    if (info !== "ApplicationInfoImpl::getLabel") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_labelId() {
    let info = appLicaInfo.labelId;

    console.log("appLicaInfo.labelId is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_icon() {
    let info = appLicaInfo.icon;

    console.log("abiInfo.icon is: " + info);
    if (info !== "ApplicationInfoImpl::getIcon") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_iconId() {
    let info = appLicaInfo.iconId;

    console.log("appLicaInfo.iconId is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_process() {
    let info = appLicaInfo.process;

    console.log("appLicaInfo.process is: " + info);
    if (info !== "ApplicationInfoImpl::getProcess") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_permissions() {
    let info = appLicaInfo.permissions[0];

    console.log("appLicaInfo.permissions is: " + info);
    if (info !== "ApplicationInfoImpl::getPermissions") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_codePath() {
    let info = appLicaInfo.codePath;

    console.log("appLicaInfo.codePath is: " + info);
    if (info !== "ApplicationInfoImpl::getCodePath") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_removable() {
    let info = appLicaInfo.removable;

    console.log("appLicaInfo.removable is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_accessTokenId() {
    let info = appLicaInfo.accessTokenId;

    console.log("appLicaInfo.accessTokenId is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_uid() {
    let info = appLicaInfo.uid;

    console.log("appLicaInfo.uid is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_appDistributionType() {
    let info = appLicaInfo.appDistributionType;

    console.log("appLicaInfo.appDistributionType is: " + info);
    if (info !== "ApplicationInfoImpl::getAppDistributionType") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_appProvisionType() {
    let info = appLicaInfo.appProvisionType;

    console.log("appLicaInfo.appProvisionType is: " + info);
    if (info !== "ApplicationInfoImpl::getAppProvisionType") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_systemApp() {
    let info = appLicaInfo.systemApp;

    console.log("appLicaInfo.systemApp is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_debug() {
    let info = appLicaInfo.debug;

    console.log("appLicaInfo.debug is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_dataUnclearable() {
    let info = appLicaInfo.dataUnclearable;

    console.log("appLicaInfo.dataUnclearable is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_nativeLibraryPath() {
    let info = appLicaInfo.nativeLibraryPath;

    console.log("appLicaInfo.nativeLibraryPath is: " + info);
    if (info !== "ApplicationInfoImpl::getNativeLibraryPath") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_appIndex() {
    let info = appLicaInfo.appIndex;

    console.log("appLicaInfo.appIndex is: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_installSource() {
    let info = appLicaInfo.installSource;

    console.log("appLicaInfo.installSource is: " + info);
    if (info !== "ApplicationInfoImpl::getInstallSource") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_releaseType() {
    let info = appLicaInfo.releaseType;

    console.log("appLicaInfo.releaseType is: " + info);
    if (info !== "ApplicationInfoImpl::getReleaseType") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_applicationInfo_with_cloudFileSyncEnabled() {
    let info = appLicaInfo.cloudFileSyncEnabled;

    console.log("appLicaInfo.cloudFileSyncEnabled is: " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_moduleMetadata_with_moduleName() {
    let info = moudleMData.moduleName;

    console.log("moudleMData.moduleName is: " + info);
    if (info !== "ModuleMetadataImpl::getModuleName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_multiAppMode_with_maxCount() {
    let info = multiMode.maxCount;

    console.log("multiMode.maxCount: " + info);
    if (info !== intDig) throw new Error(`Unexpected result`);
}

// ElementName.d.ts
let eleName: elementName.ElementName = elementName.GetElementName();
function test_bundlemanager_interface_elementName_with_deviceId() {
    let info = eleName.deviceId;
    console.log("old eleName.deviceId is: " + info);
    if (info !== "default_deviceId") throw new Error(`Unexpected result`);

    eleName.deviceId = "DI0428";
    info = eleName.deviceId;
    console.log("new eleName.deviceId is: " + info);
    if (info !== "DI0428") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_elementName_with_bundleName() {
    let info = eleName.bundleName;
    console.log("old eleName.bundleName is: " + info);
    if (info !== "default_bundleName") throw new Error(`Unexpected result`);

    eleName.bundleName = "BN0428";
    info = eleName.bundleName;
    console.log("new eleName.bundleName is: " + info);
    if (info !== "BN0428") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_elementName_with_moduleName() {
    let info = eleName.moduleName;
    console.log("old eleName.moduleName is: " + info);
    if (info !== "default_moduleName") throw new Error(`Unexpected result`);

    eleName.moduleName = "MN0428";
    info = eleName.moduleName;
    console.log("new eleName.moduleName is: " + info);
    if (info !== "MN0428") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_elementName_with_abilityName() {
    let info = eleName.abilityName;
    console.log("old eleName.abilityName is: " + info);
    if (info !== "default_abilityName") throw new Error(`Unexpected result`);

    eleName.abilityName = "AN0428";
    info = eleName.abilityName;
    console.log("new eleName.abilityName is: " + info);
    if (info !== "AN0428") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_elementName_with_uri() {
    let info = eleName.uri;
    console.log("old eleName.uri is: " + info);
    if (info !== "default_uri") throw new Error(`Unexpected result`);

    eleName.uri = "Uri0428";
    info = eleName.uri;
    console.log("new eleName.uri is: " + info);
    if (info !== "Uri0428") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_elementName_with_shortName() {
    let info = eleName.shortName;
    console.log("old eleName.shortName is: " + info);
    if (info !== "default_shortName") throw new Error(`Unexpected result`);

    eleName.shortName = "SN0428";
    info = eleName.shortName;
    console.log("new eleName.shortName is: " + info);
    if (info !== "SN0428") throw new Error(`Unexpected result`);
}

// BundleInfo.d.ts
let bundInfo: bundleInfo.BundleInfo = bundleInfo.GetBundleInfo();
let reqDetail: bundleInfo.ReqPermissionDetail =
    bundleInfo.GetReqPermissionDetail();
let used: bundleInfo.UsedScene = bundleInfo.GetIUsedScene();
let sigInfo: bundleInfo.SignatureInfo = bundleInfo.GetISignatureInfo();
let appClone: bundleInfo.AppCloneIdentity = bundleInfo.GetAppCloneIdentity();
function test_bundlemanager_interface_bundleinfo_with_name() {
    let info = bundInfo.name;

    if (info !== "BundleInfoImpl::getName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_bundleinfo_with_vendor() {
    let info = bundInfo.vendor;

    if (info !== "BundleInfoImpl::getVendor") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_bundleinfo_with_versionCode() {
    let info = bundInfo.versionCode;

    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_bundleinfo_with_versionName() {
    let info = bundInfo.versionName;

    if (info !== "BundleInfoImpl::getVersionName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_bundleinfo_with_minCompatibleVersionCode() {
    let info = bundInfo.minCompatibleVersionCode;

    if (info !== "BundleInfoImpl::getMinCompatibleVersionCode") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_bundleinfo_with_targetVersion() {
    let info = bundInfo.targetVersion;

    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_bundleinfo_with_installTime() {
    let info = bundInfo.installTime;

    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_bundleinfo_with_updateTime() {
    let info = bundInfo.updateTime;

    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_bundleinfo_with_appIndex() {
    let info = bundInfo.appIndex;

    if (info !== intDig) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_ReqPermissionDetail_with_name() {
    let info = reqDetail.name;
    if (info !== "default_name") throw new Error(`Unexpected result`);

    reqDetail.name = "req0428";
    info = reqDetail.name;
    if (info !== "req0428") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_ReqPermissionDetail_with_moduleName() {
    let info = reqDetail.moduleName;
    if (info !== "default_moduleName") throw new Error(`Unexpected result`);

    reqDetail.moduleName = "MN04280428";
    info = reqDetail.moduleName;
    if (info !== "MN04280428") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_ReqPermissionDetail_with_reason() {
    let info = reqDetail.reason;
    if (info !== "default_reason") throw new Error(`Unexpected result`);

    reqDetail.reason = "reason0428";
    info = reqDetail.reason;
    if (info !== "reason0428") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_ReqPermissionDetail_with_reasonId() {
    let info = reqDetail.reasonId;
    if (info !== 0) throw new Error(`Unexpected result`);

    reqDetail.reasonId = 2026;
    info = reqDetail.reasonId;
    if (info !== 2026) throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_usedScene_with_abilities() {
    used.abilities = ["abilities1", "abilities2", "abilities3"];
    let info = used.abilities[0];

    if (info !== "abilities1") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_usedScene_with_when() {
    used.when = "when0428";
    let info = used.when;

    if (info !== "when0428") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_signatureInfo_with_appId() {
    let info = sigInfo.appId;

    if (info !== "SignatureInfoImpl::getAppId") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_signatureInfo_with_fingerprint() {
    let info = sigInfo.fingerprint;

    if (info !== "SignatureInfoImpl::getFingerprint") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_signatureInfo_with_appIdentifier() {
    let info = sigInfo.appIdentifier;

    if (info !== "SignatureInfoImpl::getAppIdentifier") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_signatureInfo_with_certificate() {
    let info = sigInfo.certificate;

    if (info !== "SignatureInfoImpl::getCertificate") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_appCloneIdentity_with_bundleName() {
    let info = appClone.bundleName;

    if (info !== "AppCloneIdentityImpl::getBundleName") throw new Error(`Unexpected result`);
}

function test_bundlemanager_interface_appCloneIdentity_with_appIndex() {
    let info = appClone.appIndex;

    if (info !== intDig) throw new Error(`Unexpected result`);
}

function main() {
    console.log("##############start BundleManager Tests#############");

    // Abilityinfo.d.ts
    test_bundlemanager_interface_abilityinfo_with_bundleName();
    test_bundlemanager_interface_abilityinfo_with_moduleName();
    test_bundlemanager_interface_abilityinfo_with_name();
    test_bundlemanager_interface_abilityinfo_with_label();
    test_bundlemanager_interface_abilityinfo_with_labelId();
    test_bundlemanager_interface_abilityinfo_with_description();
    test_bundlemanager_interface_abilityinfo_with_descriptionId();
    test_bundlemanager_interface_abilityinfo_with_icon();
    test_bundlemanager_interface_abilityinfo_with_iconId();
    test_bundlemanager_interface_abilityinfo_with_process();
    test_bundlemanager_interface_abilityinfo_with_exported();
    test_bundlemanager_interface_abilityinfo_with_type();
    test_bundlemanager_interface_abilityinfo_with_orientation();
    test_bundlemanager_interface_abilityinfo_with_launchType();
    test_bundlemanager_interface_abilityinfo_with_permissions();
    test_bundlemanager_interface_abilityinfo_with_readPermission();
    test_bundlemanager_interface_abilityinfo_with_writePermission();
    test_bundlemanager_interface_abilityinfo_with_uri();
    test_bundlemanager_interface_abilityinfo_with_deviceTypes();
    test_bundlemanager_interface_abilityinfo_with_metadata();
    test_bundlemanager_interface_abilityinfo_with_enabled();
    test_bundlemanager_interface_abilityinfo_with_supportWindowModes();
    test_bundlemanager_interface_abilityinfo_with_excludeFromDock();
    test_bundlemanager_interface_abilityinfo_with_skills();
    test_bundlemanager_interface_abilityinfo_with_appIndex();
    test_bundlemanager_interface_abilityinfo_with_orientationId();

    // ApplicationInfo.d.ts
    test_bundlemanager_interface_applicationInfo_with_name();
    test_bundlemanager_interface_applicationInfo_with_description();
    test_bundlemanager_interface_applicationInfo_with_descriptionId();
    test_bundlemanager_interface_applicationInfo_with_enabled();
    test_bundlemanager_interface_applicationInfo_with_label();
    test_bundlemanager_interface_applicationInfo_with_labelId();
    test_bundlemanager_interface_applicationInfo_with_icon();
    test_bundlemanager_interface_applicationInfo_with_iconId();
    test_bundlemanager_interface_applicationInfo_with_process();
    test_bundlemanager_interface_applicationInfo_with_permissions();
    test_bundlemanager_interface_applicationInfo_with_codePath();
    test_bundlemanager_interface_applicationInfo_with_removable();
    test_bundlemanager_interface_applicationInfo_with_accessTokenId();
    test_bundlemanager_interface_applicationInfo_with_uid();
    test_bundlemanager_interface_applicationInfo_with_appDistributionType();
    test_bundlemanager_interface_applicationInfo_with_appProvisionType();
    test_bundlemanager_interface_applicationInfo_with_systemApp();
    test_bundlemanager_interface_applicationInfo_with_debug();
    test_bundlemanager_interface_applicationInfo_with_dataUnclearable();
    test_bundlemanager_interface_applicationInfo_with_nativeLibraryPath();
    test_bundlemanager_interface_applicationInfo_with_appIndex();
    test_bundlemanager_interface_applicationInfo_with_installSource();
    test_bundlemanager_interface_applicationInfo_with_releaseType();
    test_bundlemanager_interface_applicationInfo_with_cloudFileSyncEnabled();
    test_bundlemanager_interface_moduleMetadata_with_moduleName();
    test_bundlemanager_interface_multiAppMode_with_maxCount();

    // BundleInfo.d.ts
    test_bundlemanager_interface_bundleinfo_with_name();
    test_bundlemanager_interface_bundleinfo_with_vendor();
    test_bundlemanager_interface_bundleinfo_with_versionCode();
    test_bundlemanager_interface_bundleinfo_with_versionName();
    test_bundlemanager_interface_bundleinfo_with_minCompatibleVersionCode();
    test_bundlemanager_interface_bundleinfo_with_targetVersion();
    test_bundlemanager_interface_bundleinfo_with_installTime();
    test_bundlemanager_interface_bundleinfo_with_updateTime();
    test_bundlemanager_interface_bundleinfo_with_appIndex();
    test_bundlemanager_interface_ReqPermissionDetail_with_name();
    test_bundlemanager_interface_ReqPermissionDetail_with_moduleName();
    test_bundlemanager_interface_ReqPermissionDetail_with_reason();
    test_bundlemanager_interface_ReqPermissionDetail_with_reasonId();
    test_bundlemanager_interface_usedScene_with_abilities();
    test_bundlemanager_interface_usedScene_with_when();
    test_bundlemanager_interface_signatureInfo_with_appId();
    test_bundlemanager_interface_signatureInfo_with_fingerprint();
    test_bundlemanager_interface_signatureInfo_with_appIdentifier();
    test_bundlemanager_interface_signatureInfo_with_certificate();
    test_bundlemanager_interface_appCloneIdentity_with_bundleName();
    test_bundlemanager_interface_appCloneIdentity_with_appIndex();

    // ElementName.d.ts
    test_bundlemanager_interface_elementName_with_deviceId();
    test_bundlemanager_interface_elementName_with_bundleName();
    test_bundlemanager_interface_elementName_with_moduleName();
    test_bundlemanager_interface_elementName_with_abilityName();
    test_bundlemanager_interface_elementName_with_uri();
    test_bundlemanager_interface_elementName_with_shortName();

    // ExtensionAbilityInfo.d.ts
    test_bundlemanager_interface_extensionAbilityInfo_with_bundleName();
    test_bundlemanager_interface_extensionAbilityInfo_with_moduleName();
    test_bundlemanager_interface_extensionAbilityInfo_with_name();
    test_bundlemanager_interface_extensionAbilityInfo_with_labelId();
    test_bundlemanager_interface_extensionAbilityInfo_with_descriptionId();
    test_bundlemanager_interface_extensionAbilityInfo_with_iconId();
    test_bundlemanager_interface_extensionAbilityInfo_with_exported();
    test_bundlemanager_interface_extensionAbilityInfo_with_extensionAbilityTypeName();
    test_bundlemanager_interface_extensionAbilityInfo_with_permissions();
    test_bundlemanager_interface_extensionAbilityInfo_with_enabled();
    test_bundlemanager_interface_extensionAbilityInfo_with_readPermission();
    test_bundlemanager_interface_extensionAbilityInfo_with_writePermission();
    test_bundlemanager_interface_extensionAbilityInfo_with_appIndex();

    // HapModuleInfo.d.ts
    test_bundlemanager_interface_hapmoduleinfo_with_name();
    test_bundlemanager_interface_hapmoduleinfo_with_icon();
    test_bundlemanager_interface_hapmoduleinfo_with_iconId();
    test_bundlemanager_interface_hapmoduleinfo_with_label();
    test_bundlemanager_interface_hapmoduleinfo_with_labelId();
    test_bundlemanager_interface_hapmoduleinfo_with_description();
    test_bundlemanager_interface_hapmoduleinfo_with_descriptionId();
    test_bundlemanager_interface_hapmoduleinfo_with_mainElementName();
    test_bundlemanager_interface_hapmoduleinfo_with_deviceTypes();
    test_bundlemanager_interface_hapmoduleinfo_with_installationFree();
    test_bundlemanager_interface_hapmoduleinfo_with_hashValue();
    test_bundlemanager_interface_hapmoduleinfo_with_fileContextMenuConfig();
    test_bundlemanager_interface_hapmoduleinfo_with_nativeLibraryPath();
    test_bundlemanager_interface_hapmoduleinfo_with_codePath();
    test_bundlemanager_interface_dependency_with_moduleName();
    test_bundlemanager_interface_dependency_with_bundleName();
    test_bundlemanager_interface_dependency_with_versionCode();
    test_bundlemanager_interface_preloaditem_with_moduleName();
    test_bundlemanager_interface_routerItem_with_name();
    test_bundlemanager_interface_routerItem_with_pageSourceFile();
    test_bundlemanager_interface_routerItem_with_buildFunction();
    test_bundlemanager_interface_routerItem_with_customData();
    test_bundlemanager_interface_dataItem_with_key();
    test_bundlemanager_interface_dataItem_with_value();

    // Metadata.d.ts
    test_bundlemanager_interface_metadata_with_name();
    test_bundlemanager_interface_metadata_with_value();
    test_bundlemanager_interface_metadata_with_resource();
    test_bundlemanager_interface_metadata_with_valueId();

    // OverlayModuleInfo.d.ts
    test_bundlemanager_interface_overlaymoduleinfo_with_bundleName();
    test_bundlemanager_interface_overlaymoduleinfo_with_moduleName();
    test_bundlemanager_interface_overlaymoduleinfo_with_targetModuleName();
    test_bundlemanager_interface_overlaymoduleinfo_with_priority();
    test_bundlemanager_interface_overlaymoduleinfo_with_state();

    // Skill.d.ts
    test_bundlemanager_interface_skill_with_actions();
    test_bundlemanager_interface_skill_with_entities();
    test_bundlemanager_interface_skill_with_domainVerify();
    test_bundlemanager_interface_skilluri_with_scheme();
    test_bundlemanager_interface_skilluri_with_host();
    test_bundlemanager_interface_skilluri_with_port();
    test_bundlemanager_interface_skilluri_with_path();
    test_bundlemanager_interface_skilluri_with_pathStartWith();
    test_bundlemanager_interface_skilluri_with_pathRegex();
    test_bundlemanager_interface_skilluri_with_type();
    test_bundlemanager_interface_skilluri_with_utd();
    test_bundlemanager_interface_skilluri_with_maxFileSupported();
    test_bundlemanager_interface_skilluri_with_linkFeature();

    console.log("##############end BundleManager Tests#############");
}

main();