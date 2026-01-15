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
const customizeData = requireNapi('./customizeData.so', RequireBaseDir.SCRIPT_DIR);
const elementName = requireNapi('./elementName.so', RequireBaseDir.SCRIPT_DIR);
const hapModuleInfo = requireNapi('./hapModuleInfo.so', RequireBaseDir.SCRIPT_DIR);
const moduleInfo = requireNapi('./moduleInfo.so', RequireBaseDir.SCRIPT_DIR);
const wantInfo = requireNapi('./ohos_app_ability_want.so', RequireBaseDir.SCRIPT_DIR);
const ohosBundle = requireNapi('./ohos_bundle.so', RequireBaseDir.SCRIPT_DIR);
const shortcutInfo = requireNapi('./shortcutInfo.so', RequireBaseDir.SCRIPT_DIR);

//@ohos.bundle.d.ts
let bundleName = "ohos.bundle";
let bundleFlags = 419;
let userId = 391550;
let abilityName = "abilityName";
let uid = 2147483647;
let hapFilePath = "/home/taihe";
let arrString = ["this", "is", "bundle"];

function test_bundle_enum_BundleFlag_with_DEFAULT() {
    const first = ohosBundle.BundleFlag.GET_BUNDLE_DEFAULT;

    console.log("BundleFlag.GET_BUNDLE_DEFAULT is : " + first);
    if (first !== ohosBundle.BundleFlag.GET_BUNDLE_DEFAULT) throw new Error(`Unexpected result`);
}

function test_bundle_enum_BundleFlag_with_INFO() {
    const first = ohosBundle.BundleFlag.GET_ALL_APPLICATION_INFO;

    console.log("BundleFlag.GET_ALL_APPLICATION_INFO is : " + first);
    if (first !== ohosBundle.BundleFlag.GET_ALL_APPLICATION_INFO) throw new Error(`Unexpected result`);
}

function test_bundle_enum_BundleFlag_with_DISABLE() {
    const first = ohosBundle.BundleFlag.GET_APPLICATION_INFO_WITH_DISABLE;

    console.log("BundleFlag.GET_APPLICATION_INFO_WITH_DISABLE is : " + first);
    if (first !== ohosBundle.BundleFlag.GET_APPLICATION_INFO_WITH_DISABLE) throw new Error(`Unexpected result`);
}

function test_bundle_enum_with_colorMode() {
    const first = ohosBundle.ColorMode.AUTO_MODE;

    console.log("ColorMode.AUTO_MODE is : " + first);
    if (first !== ohosBundle.ColorMode.AUTO_MODE) throw new Error(`Unexpected result`);
}

function test_bundle_enum_with_grantStatus() {
    const first = ohosBundle.GrantStatus.PERMISSION_DENIED;

    console.log("GrantStatus.PERMISSION_DENIED is : " + first);
    if (first !== ohosBundle.GrantStatus.PERMISSION_DENIED) throw new Error(`Unexpected result`);
}

function test_bundle_enum_with_abilityType() {
    let first = ohosBundle.AbilityType.UNKNOWN;

    console.log("AbilityType.UNKNOWN is : " + first);
    if (first !== ohosBundle.AbilityType.UNKNOWN) throw new Error(`Unexpected result`);
}

function test_bundle_enum_with_abilitySubType() {
    const first = ohosBundle.AbilitySubType.UNSPECIFIED;

    console.log("AbilitySubType.UNSPECIFIED is : " + first);
    if (first !== ohosBundle.AbilitySubType.UNSPECIFIED) throw new Error(`Unexpected result`);
}

function test_bundle_enum_with_displayOrientation() {
    const first = ohosBundle.DisplayOrientation.UNSPECIFIED;

    console.log("DisplayOrientation.UNSPECIFIED is : " + first);
    if (first !== ohosBundle.DisplayOrientation.UNSPECIFIED) throw new Error(`Unexpected result`);
}

function test_bundle_enum_with_launchMode() {
    const first = ohosBundle.LaunchMode.SINGLETON;

    console.log("LaunchMode.SINGLETON is : " + first);
    if (first !== ohosBundle.LaunchMode.SINGLETON) throw new Error(`Unexpected result`);
}

function test_bundle_enum_with_installErrorCode_SUCCESS() {
    const first = ohosBundle.InstallErrorCode.SUCCESS;

    console.log("InstallErrorCode.SUCCESS is : " + first);
    if (first !== ohosBundle.InstallErrorCode.SUCCESS) throw new Error(`Unexpected result`);
}

function test_bundle_enum_with_installErrorCode_TIMEOUT() {
    const first =
        ohosBundle.InstallErrorCode.STATUS_INSTALL_FAILURE_DOWNLOAD_TIMEOUT;

    console.log(
        "InstallErrorCode.STATUS_INSTALL_FAILURE_DOWNLOAD_TIMEOUT is : " +
        first);
    if (first !== ohosBundle.InstallErrorCode.STATUS_INSTALL_FAILURE_DOWNLOAD_TIMEOUT) throw new Error(`Unexpected result`);
}

function test_bundle_enum_with_installErrorCode_FOUND() {
    const first = ohosBundle.InstallErrorCode.STATUS_ABILITY_NOT_FOUND;

    console.log("InstallErrorCode.STATUS_ABILITY_NOT_FOUND is : " + first);
    if (first !== ohosBundle.InstallErrorCode.STATUS_ABILITY_NOT_FOUND) throw new Error(`Unexpected result`);
}

let bundleOpt: ohosBundle.BundleOptions = ohosBundle.GetBundleOptions();
function test_bundle_interface_bundleOptions_with_userId_noSet() {
    let id = bundleOpt.userId;

    console.log("BundleOptions userId is : " + id);
    if (id !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_interface_bundleOptions_with_userId() {
    bundleOpt.userId = userId;
    let id = bundleOpt.userId;

    console.log("BundleOptions userId is : " + id);
    if (id !== userId) throw new Error(`Unexpected result`);
}

function test_bundle_function_with_getBundleInfo() {
    ohosBundle.GetBundleInfo("getBundleInfo", bundleFlags);

    console.log("ohos bundle function is : getBundleInfo ");
}

function test_bundle_function_with_queryAbilityByWant() {
    ohosBundle.QueryAbilityByWant(bundleFlags, userId);

    console.log("ohos bundle function is : queryAbilityByWant ");
}

function test_bundle_function_with_getAllBundleInfo() {
    ohosBundle.GetAllBundleInfo(userId);

    console.log("ohos bundle function is : getAllBundleInfo ");
}

function test_bundle_function_with_getAllApplicationInfo() {
    ohosBundle.GetAllApplicationInfo(bundleFlags, userId);

    console.log("ohos bundle function is : getAllApplicationInfo ");
}

function test_bundle_function_with_getNameForUid() {
    ohosBundle.GetNameForUid(uid);

    console.log("ohos bundle function is : getNameForUid ");
}

function test_bundle_function_with_getBundleArchiveInfo() {
    ohosBundle.GetBundleArchiveInfo(hapFilePath, bundleFlags);

    console.log("ohos bundle function is : getBundleArchiveInfo ");
}

function test_bundle_function_with_getLaunchWantForBundle() {
    ohosBundle.GetLaunchWantForBundle(bundleName);

    console.log("ohos bundle function is : getLaunchWantForBundle ");
}

function test_bundle_function_with_getAbilityLabel() {
    ohosBundle.GetAbilityLabel(bundleName, abilityName);

    console.log("ohos bundle function is : getAbilityLabel ");
}

function test_bundle_function_with_getAbilityIcon() {
    ohosBundle.GetAbilityIcon(bundleName, abilityName);

    console.log("ohos bundle function is : getAbilityIcon ");
}

function test_bundle_function_with_isAbilityEnabled() {
    ohosBundle.IsAbilityEnabled();

    console.log("ohos bundle function is : isAbilityEnabled ");
}

function test_bundle_function_with_isApplicationEnabled() {
    ohosBundle.IsApplicationEnabled(bundleName);

    console.log("ohos bundle function is : isApplicationEnabled ");
}

// abilityInfo.d.ts
let abInfo: abilityInfo.AbilityInfo = abilityInfo.GetAbilityInfo();
function test_abilityinfo_with_bundleName() {
    let info = abInfo.bundleName;

    console.log("abInfo.bundleName is : " + info);
    if (info !== "AbilityInfo::getBundleName") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_name() {
    let info = abInfo.name;

    console.log("abInfo.name is : " + info);
    if (info !== "AbilityInfo::getName") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_label() {
    let info = abInfo.label;

    console.log("abInfo.label is : " + info);
    if (info !== "AbilityInfo::getLabel") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_description() {
    let info = abInfo.description;

    console.log("abInfo.description is : " + info);
    if (info !== "AbilityInfo::getDescription") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_icon() {
    let info = abInfo.icon;

    console.log("abInfo.icon is : " + info);
    if (info !== "AbilityInfo::getIcon") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_labelId() {
    let info = abInfo.labelId;

    console.log("abInfo.labelId is : " + info);
    if (info !== 100) throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_descriptionId() {
    let info = abInfo.descriptionId;

    console.log("abInfo.descriptionId is : " + info);
    if (info !== 100) throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_iconId() {
    let info = abInfo.iconId;

    console.log("abInfo.iconId is : " + info);
    if (info !== 100) throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_moduleName() {
    let info = abInfo.moduleName;

    console.log("abInfo.moduleName is : " + info);
    if (info !== "AbilityInfo::getModuleName") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_process() {
    let info = abInfo.process;

    console.log("abInfo.process is : " + info);
    if (info !== "AbilityInfo::getProcess") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_targetAbility() {
    let info = abInfo.targetAbility;

    console.log("abInfo.targetAbility is : " + info);
    if (info !== "AbilityInfo::getTargetAbility") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_backgroundModes() {
    let info = abInfo.backgroundModes;

    console.log("abInfo.backgroundModes is : " + info);
    if (info !== 100) throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_isVisible() {
    let info = abInfo.isVisible;

    console.log("abInfo.isVisible is : " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_formEnabled() {
    let info = abInfo.formEnabled;

    console.log("abInfo.formEnabled is : " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_permissions() {
    let info = abInfo.permissions[0];

    console.log("abInfo.permissions is : " + info);
    if (info !== "AbilityInfo::getTargetAbility") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_deviceTypes() {
    let info = abInfo.deviceTypes[0];

    console.log("abInfo.deviceTypes is : " + info);
    if (info !== "AbilityInfo::getDeviceTypes") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_deviceCapabilities() {
    let info = abInfo.deviceCapabilities[0];

    console.log("abInfo.deviceCapabilities is : " + info);
    if (info !== "AbilityInfo::getDeviceCapabilities") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_readPermission() {
    let info = abInfo.readPermission;

    console.log("abInfo.readPermission is : " + info);
    if (info !== "AbilityInfo::getReadPermission") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_writePermission() {
    let info = abInfo.writePermission;

    console.log("abInfo.writePermission is : " + info);
    if (info !== "AbilityInfo::getWritePermission") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_uri() {
    let info = abInfo.uri;

    console.log("abInfo.uri is : " + info);
    if (info !== "AbilityInfo::getUri") throw new Error(`Unexpected result`);
}

function test_abilityinfo_with_enabled() {
    let info = abInfo.enabled;

    console.log("abInfo.enabled is : " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

// bundleInfo.d.ts
let usedScene: bundleInfo.UsedScene = bundleInfo.GetUsedScene();
let reqPerDetail: bundleInfo.ReqPermissionDetail =
    bundleInfo.GetReqPermissionDetail();
let bunInfo: bundleInfo.BundleInfo = bundleInfo.GetBundleInfo();

function test_bundleinfo_interface_usedScene_with_abilities() {
    usedScene.abilities = ["this ", "is ", "abilities"];
    let info = usedScene.abilities[2];

    console.log("usedScene.abilities is : " + info);
    if (info !== "abilities") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_usedScene_with_when() {
    usedScene.when = "this is when";
    let info = usedScene.when;

    console.log("usedScene.when is : " + info);
    if (info !== "this is when") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_reqperdetail_with_name() {
    reqPerDetail.name = "this is name";
    let info = reqPerDetail.name;

    console.log("reqPerDetail.name is : " + info);
    if (info !== "this is name") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_reqperdetail_with_reason() {
    reqPerDetail.reason = "this is reason";
    let info = reqPerDetail.reason;

    console.log("reqPerDetail.reason is : " + info);
    if (info !== "this is reason") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_name() {
    let info = bunInfo.name;

    console.log("bunInfo.name is : " + info);
    if (info !== "bundleInfo::getName") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_type() {
    let info = bunInfo.type;

    console.log("bunInfo.type is : " + info);
    if (info !== "bundleInfo::getType") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_appId() {
    let info = bunInfo.appId;

    console.log("bunInfo.appId is : " + info);
    if (info !== "bundleInfo::getAppId") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_withuid() {
    let info = bunInfo.uid;

    console.log("bunInfo.uid is : " + info);
    if (info !== 127) throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_installTime() {
    let info = bunInfo.installTime;

    console.log("bunInfo.installTime is : " + info);
    if (info !== 127) throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_updateTime() {
    let info = bunInfo.updateTime;

    console.log("bunInfo.updateTime is : " + info);
    if (info !== 127) throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_reqPermissions() {
    let info = bunInfo.reqPermissions[0];

    console.log("bunInfo.reqPermissions is : " + info);
    if (info !== "bundleInfo::getReqPermissions") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_vendor() {
    let info = bunInfo.vendor;

    console.log("bunInfo.vendor is : " + info);
    if (info !== "bundleInfo::getVendor") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_versionCode() {
    let info = bunInfo.versionCode;

    console.log("bunInfo.versionCode is : " + info);
    if (info !== 127) throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_versionName() {
    let info = bunInfo.versionName;

    console.log("bunInfo.versionName is : " + info);
    if (info !== "bundleInfo::getVersionName") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_compatibleVersion() {
    let info = bunInfo.compatibleVersion;

    console.log("bunInfo.compatibleVersion is : " + info);
    if (info !== 127) throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_targetVersion() {
    let info = bunInfo.targetVersion;

    console.log("bunInfo.targetVersion is : " + info);
    if (info !== 127) throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_isCompressNativeLibs() {
    let info = bunInfo.isCompressNativeLibs;

    console.log("bunInfo.isCompressNativeLibs is : " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_entryModuleName() {
    let info = bunInfo.entryModuleName;

    console.log("bunInfo.entryModuleName is : " + info);
    if (info !== "bundleInfo::getEntryModuleName") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_cpuAbi() {
    let info = bunInfo.cpuAbi;

    console.log("bunInfo.cpuAbi is : " + info);
    if (info !== "bundleInfo::getCpuAbi") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_isSilentInstallation() {
    let info = bunInfo.isSilentInstallation;

    console.log("bunInfo.isSilentInstallation is : " + info);
    if (info !== "bundleInfo::getIsSilentInstallation") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_minCompatibleVersionCode() {
    let info = bunInfo.minCompatibleVersionCode;

    console.log("bunInfo.minCompatibleVersionCode is : " + info);
    if (info !== 127) throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_entryInstallationFree() {
    let info = bunInfo.entryInstallationFree;

    console.log("bunInfo.entryInstallationFree is : " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_with_reqPermissionStates() {
    let info = bunInfo.reqPermissionStates[0];

    console.log("bunInfo.reqPermissionStates is : " + info);
    if (info !== 127) throw new Error(`Unexpected result`);
}

// customizeData.d.ts
let custData: customizeData.CustomizeData = customizeData.GetCustomizeData();
function test_bundleinfo_interface_custdata_with_name() {
    custData.name = "tom";
    let info = custData.name;

    console.log("custData.name is : " + info);
    if (info !== "tom") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_custdata_with_value() {
    custData.value = "tom";
    let info = custData.value;

    console.log("custData.value is : " + info);
    if (info !== "tom") throw new Error(`Unexpected result`);
}

function test_bundleinfo_interface_custdata_with_extra() {
    custData.extra = "tom";
    let info = custData.extra;

    console.log("custData.extra is : " + info);
    if (info !== "tom") throw new Error(`Unexpected result`);
}

// hapModuleInfo.d.ts
let hapInfo: hapModuleInfo.HapModuleInfo = hapModuleInfo.GetHapModuleInfo();
function test_bundle_interface_hapModuleInfo_with_name() {
    let info = hapInfo.name;

    console.log("hapInfo.name is : " + info);
    if (info !== "HapModuleInfo::getName") throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_description() {
    let info = hapInfo.description;

    console.log("hapInfo.description is : " + info);
    if (info !== "HapModuleInfo::getDescription") throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_descriptionid() {
    let info = hapInfo.descriptionId;

    console.log("hapInfo.descriptionId is : " + info);
    if (info !== 1024) throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_icon() {
    let info = hapInfo.icon;

    console.log("hapInfo.icon is : " + info);
    if (info !== "HapModuleInfo::getIcon") throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_label() {
    let info = hapInfo.label;

    console.log("hapInfo.label is : " + info);
    if (info !== "HapModuleInfo::getLabel") throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_labelid() {
    let info = hapInfo.labelId;

    console.log("hapInfo.labelId is : " + info);
    if (info !== 1024) throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_iconid() {
    let info = hapInfo.iconId;

    console.log("hapInfo.iconId is : " + info);
    if (info !== 1024) throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_backgroundImg() {
    let info = hapInfo.backgroundImg;

    console.log("hapInfo.backgroundImg is : " + info);
    if (info !== "HapModuleInfo::getBackgroundImg") throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_supportedModes() {
    let info = hapInfo.supportedModes;

    console.log("hapInfo.supportedModes is : " + info);
    if (info !== 1024) throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_reqCapabilities() {
    let info = hapInfo.reqCapabilities[0];

    console.log("hapInfo.reqCapabilities is : " + info);
    if (info !== "HapModuleInfo::getReqCapabilities") throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_deviceTypes() {
    let info = hapInfo.deviceTypes[0];

    console.log("hapInfo.deviceTypes is : " + info);
    if (info !== "HapModuleInfo::getDeviceTypes") throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_moduleName() {
    let info = hapInfo.moduleName;

    console.log("hapInfo.moduleName is : " + info);
    if (info !== "HapModuleInfo::getModuleName") throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_mainAbilityName() {
    let info = hapInfo.mainAbilityName;

    console.log("hapInfo.mainAbilityName is : " + info);
    if (info !== "HapModuleInfo::getMainAbilityName") throw new Error(`Unexpected result`);
}

function test_bundle_interface_hapModuleInfo_with_installationFree() {
    let info = hapInfo.installationFree;

    console.log("hapInfo.installationFree is : " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

// moduleInfo.d.ts
let moInfo: moduleInfo.ModuleInfo = moduleInfo.GetModuleInfo();
function test_bundle_interface_moduleInfo_with_moduleName() {
    let info = moInfo.moduleName;

    console.log("moInfo.moduleName is : " + info);
    if (info !== "this is moduleinfo with name") throw new Error(`Unexpected result`);
}

function test_bundle_interface_moduleInfo_with_moduleSourceDir() {
    let info = moInfo.moduleSourceDir;

    console.log("moInfo.moduleSourceDir is : " + info);
    if (info !== "this is moduleinfo with moduleSourceDir") throw new Error(`Unexpected result`);
}

// shortcutInfo.d.ts
let shortInfo: shortcutInfo.ShortcutInfo = shortcutInfo.GetShortcutInfo();
function test_bundle_interface_shortcutInfo_with_id() {
    let info = shortInfo.id;

    console.log("shortInfo.id is : " + info);
    if (info !== "ShortcutInfo::GetId") throw new Error(`Unexpected result`);
}

function test_bundle_interface_shortcutInfo_with_bundleName() {
    let info = shortInfo.bundleName;

    console.log("shortInfo.bundleName is : " + info);
    if (info !== "ShortcutInfo::GetBundleName") throw new Error(`Unexpected result`);
}

function test_bundle_interface_shortcutInfo_with_hostAbility() {
    let info = shortInfo.hostAbility;

    console.log("shortInfo.hostAbility is : " + info);
    if (info !== "ShortcutInfo::GetHostAbility") throw new Error(`Unexpected result`);
}

function test_bundle_interface_shortcutInfo_with_icon() {
    let info = shortInfo.icon;

    console.log("shortInfo.icon is : " + info);
    if (info !== "ShortcutInfo::GetIcon") throw new Error(`Unexpected result`);
}

function test_bundle_interface_shortcutInfo_with_iconId() {
    let info = shortInfo.iconId;

    console.log("shortInfo.iconId is : " + info);
    if (info !== 4096) throw new Error(`Unexpected result`);
}

function test_bundle_interface_shortcutInfo_with_label() {
    let info = shortInfo.label;

    console.log("shortInfo.label is : " + info);
    if (info !== "ShortcutInfo::GetLabel") throw new Error(`Unexpected result`);
}

function test_bundle_interface_shortcutInfo_with_labelId() {
    let info = shortInfo.labelId;

    console.log("shortInfo.labelId is : " + info);
    if (info !== 4096) throw new Error(`Unexpected result`);
}

function test_bundle_interface_shortcutInfo_with_disableMessage() {
    let info = shortInfo.disableMessage;

    console.log("shortInfo.disableMessage is : " + info);
    if (info !== "ShortcutInfo::GetDisableMessage") throw new Error(`Unexpected result`);
}

function test_bundle_interface_shortcutInfo_with_isStatic() {
    let info = shortInfo.isStatic;

    console.log("shortInfo.isStatic is : " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundle_interface_shortcutInfo_with_isHomeShortcut() {
    let info = shortInfo.isHomeShortcut;

    console.log("shortInfo.isHomeShortcut is : " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundle_interface_shortcutInfo_with_isEnabled() {
    let info = shortInfo.isEnabled;

    console.log("shortInfo.isEnabled is : " + info);
    if (info !== true) throw new Error(`Unexpected result`);
}

// elementName.d.ts
function test_bundle_interface_elementName_with_deviceId_noSet() {
    let eleName: elementName.ElementName = elementName.GetElementName()
    let info = eleName.deviceId;
    console.log("eleName.deviceId: " + info)
    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_interface_elementName_with_deviceId() {
    let eleName: elementName.ElementName = elementName.GetElementName()
    eleName.deviceId = "ID20250422";
    let info = eleName.deviceId;
    console.log("eleName.deviceId: " + info)
    if (info !== "ID20250422") throw new Error(`Unexpected result`);
}

function test_bundle_interface_elementName_with_bundleName() {
    let eleName: elementName.ElementName = elementName.GetElementName()
    eleName.bundleName = "ID20250422";
    let info = eleName.bundleName;

    if (info !== "ID20250422") throw new Error(`Unexpected result`);
}

function test_bundle_interface_elementName_with_abilityName() {
    let eleName: elementName.ElementName = elementName.GetElementName()
    eleName.abilityName = "ID20250422";
    let info = eleName.abilityName;

    if (info !== "ID20250422") throw new Error(`Unexpected result`);
}

function test_bundle_interface_elementName_with_uri_noSet() {
    let eleName: elementName.ElementName = elementName.GetElementName()
    let info = eleName.uri;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_interface_elementName_with_uri() {
    let eleName: elementName.ElementName = elementName.GetElementName()
    eleName.uri = "ID20250422";
    let info = eleName.uri;

    if (info !== "ID20250422") throw new Error(`Unexpected result`);
}

function test_bundle_interface_elementName_with_shortName_noSet() {
    let eleName: elementName.ElementName = elementName.GetElementName()
    let info = eleName.shortName;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_interface_elementName_with_shortName() {
    let eleName: elementName.ElementName = elementName.GetElementName()
    eleName.shortName = "ID20250422";
    let info = eleName.shortName;

    if (info !== "ID20250422") throw new Error(`Unexpected result`);
}

// applicationInfo.d.ts
let appInfo: applicationInfo.ApplicationInfo =
    applicationInfo.GetApplicationInfo();
function test_bundle_interface_applicationInfo_with_name() {
    let info = appInfo.name;
    
    if (info !== "ApplicationInfo::getName") throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_description() {
    let info = appInfo.description;

    if (info !== "ApplicationInfo::getDescription") throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_descriptionId() {
    let info = appInfo.descriptionId;

    if (info !== 102) throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_systemApp() {
    let info = appInfo.systemApp;

    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_enabled() {
    let info = appInfo.enabled;

    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_label() {
    let info = appInfo.label;

    if (info !== "ApplicationInfo::getLabel") throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_labelId() {
    let info = appInfo.labelId;

    if (info !== "ApplicationInfo::getLabelId") throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_icon() {
    let info = appInfo.icon;

    if (info !== "ApplicationInfo::getIcon") throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_iconId() {
    let info = appInfo.iconId;

    if (info !== 102) throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_process() {
    let info = appInfo.process;

    if (info !== "ApplicationInfo::getProcess") throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_supportedModes() {
    let info = appInfo.supportedModes;

    if (info !== 102) throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_moduleSourceDirs() {
    let info = appInfo.moduleSourceDirs[0];

    if (info !== "ApplicationInfo::getProcess") throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_permissions() {
    let info = appInfo.permissions[0];

    if (info !== "ApplicationInfo::getPermissions") throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_entryDir() {
    let info = appInfo.entryDir;

    if (info !== "ApplicationInfo::getEntryDir") throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_codePath() {
    let info = appInfo.codePath;

    if (info !== "ApplicationInfo::getCodePath") throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_removable() {
    let info = appInfo.removable;

    if (info !== true) throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_accessTokenId() {
    let info = appInfo.accessTokenId;

    if (info !== 102) throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_uid() {
    let info = appInfo.uid;

    if (info !== 102) throw new Error(`Unexpected result`);
}

function test_bundle_interface_applicationInfo_with_entityType() {
    let info = appInfo.entityType;

    if (info !== "ApplicationInfo::getEntityType") throw new Error(`Unexpected result`);
}

// ohos.app.ability.Want.d.ts
function test_bundle_class_want_with_bundleName_noSet() {
    let wantTest = new wantInfo.Want();
    let info = wantTest.bundleName;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_bundleName() {
    let wantTest = new wantInfo.Want();
    wantTest.bundleName = bundleName;
    let info = wantTest.bundleName;

    if (info !== bundleName) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_abilityName_noSet() {
    let wantTest = new wantInfo.Want();
    let info = wantTest.abilityName;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_abilityName() {
    let wantTest = new wantInfo.Want();
    wantTest.abilityName = bundleName;
    let info = wantTest.abilityName;

    if (info !== bundleName) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_deviceId_noSet() {
    let wantTest = new wantInfo.Want();
    let info = wantTest.deviceId;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_deviceId() {
    let wantTest = new wantInfo.Want();
    wantTest.deviceId = bundleName;
    let info = wantTest.deviceId;

    if (info !== bundleName) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_uri_noSet() {
    let wantTest = new wantInfo.Want();
    let info = wantTest.uri;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_uri() {
    let wantTest = new wantInfo.Want();
    wantTest.uri = bundleName;
    let info = wantTest.uri;

    if (info !== bundleName) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_type_noSet() {
    let wantTest = new wantInfo.Want();
    let info = wantTest.type;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_type() {
    let wantTest = new wantInfo.Want();
    wantTest.type = bundleName;
    let info = wantTest.type;

    if (info !== bundleName) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_flags_noSet() {
    let wantTest = new wantInfo.Want();
    let info = wantTest.flags;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_flags() {
    let wantTest = new wantInfo.Want();
    wantTest.flags = 16.08;
    let info = wantTest.flags;

    if (info !== 16.08) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_action_noSet() {
    let wantTest = new wantInfo.Want();
    let info = wantTest.action;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_action() {
    let wantTest = new wantInfo.Want();
    wantTest.action = bundleName;
    let info = wantTest.action;

    if (info !== bundleName) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_parameters_noSet() {
    let wantTest = new wantInfo.Want();
    let info = wantTest.parameters;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

class A {
    constructor() {}
}

function test_bundle_class_want_with_parameters() {
    let wantTest = new wantInfo.Want();
    const a = new A();
    let Settings: Record<string, object> = {
        "theme": a,
        "fontSize": a,
        "language": a,
    };
    wantTest.parameters = Settings;
    let info: Record<string, object>|undefined = wantTest.parameters;

    if (info?.["theme"] !== Settings["theme"]) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_entities_noSet() {
    let wantTest = new wantInfo.Want();
    let info = wantTest.entities;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_entities() {
    let wantTest = new wantInfo.Want();
    wantTest.entities = arrString;
    let info = wantTest.entities;

    if (info?.[0] !== arrString[0]) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_moduleName_noSet() {
    let wantTest = new wantInfo.Want();
    let info = wantTest.moduleName;

    if (info !== undefined) throw new Error(`Unexpected result`);
}

function test_bundle_class_want_with_moduleName() {
    let wantTest = new wantInfo.Want();
    wantTest.moduleName = bundleName;
    let info = wantTest.moduleName;

    if (info !== bundleName) throw new Error(`Unexpected result`);
}

function main() {
    console.log("##############start BundleTest Tests#############");

    //@ohos.bundle.d.ts
    test_bundle_enum_BundleFlag_with_DEFAULT();
    test_bundle_enum_BundleFlag_with_DISABLE();
    test_bundle_enum_BundleFlag_with_INFO();
    test_bundle_enum_with_colorMode();
    test_bundle_enum_with_grantStatus();
    test_bundle_enum_with_abilityType();
    test_bundle_enum_with_abilitySubType();
    test_bundle_enum_with_displayOrientation();
    test_bundle_enum_with_launchMode();
    test_bundle_enum_with_installErrorCode_FOUND();
    test_bundle_enum_with_installErrorCode_SUCCESS();
    test_bundle_enum_with_installErrorCode_TIMEOUT();
    test_bundle_interface_bundleOptions_with_userId_noSet();
    test_bundle_interface_bundleOptions_with_userId();
    test_bundle_function_with_getBundleInfo();
    test_bundle_function_with_queryAbilityByWant();
    test_bundle_function_with_getAllBundleInfo();
    test_bundle_function_with_getAllApplicationInfo();
    test_bundle_function_with_getNameForUid();
    test_bundle_function_with_getBundleArchiveInfo();
    test_bundle_function_with_getLaunchWantForBundle();
    test_bundle_function_with_getAbilityLabel();
    test_bundle_function_with_getAbilityIcon();
    test_bundle_function_with_isAbilityEnabled();
    test_bundle_function_with_isApplicationEnabled();

    // abilityInfo.d.ts
    test_abilityinfo_with_bundleName();
    test_abilityinfo_with_name();
    test_abilityinfo_with_label();
    test_abilityinfo_with_description();
    test_abilityinfo_with_icon();
    test_abilityinfo_with_labelId();
    test_abilityinfo_with_descriptionId();
    test_abilityinfo_with_iconId();
    test_abilityinfo_with_moduleName();
    test_abilityinfo_with_process();
    test_abilityinfo_with_targetAbility();
    test_abilityinfo_with_backgroundModes();
    test_abilityinfo_with_isVisible();
    test_abilityinfo_with_formEnabled();
    test_abilityinfo_with_permissions();
    test_abilityinfo_with_deviceTypes();
    test_abilityinfo_with_deviceCapabilities();
    test_abilityinfo_with_readPermission();
    test_abilityinfo_with_writePermission();
    test_abilityinfo_with_uri();
    test_abilityinfo_with_enabled();

    // applicationInfo.d.ts
    test_bundle_interface_applicationInfo_with_name();
    test_bundle_interface_applicationInfo_with_description();
    test_bundle_interface_applicationInfo_with_descriptionId();
    test_bundle_interface_applicationInfo_with_systemApp();
    test_bundle_interface_applicationInfo_with_enabled();
    test_bundle_interface_applicationInfo_with_label();
    test_bundle_interface_applicationInfo_with_labelId();
    test_bundle_interface_applicationInfo_with_icon();
    test_bundle_interface_applicationInfo_with_iconId();
    test_bundle_interface_applicationInfo_with_process();
    test_bundle_interface_applicationInfo_with_supportedModes();
    test_bundle_interface_applicationInfo_with_moduleSourceDirs();
    test_bundle_interface_applicationInfo_with_permissions();
    test_bundle_interface_applicationInfo_with_entryDir();
    test_bundle_interface_applicationInfo_with_codePath();
    test_bundle_interface_applicationInfo_with_removable();
    test_bundle_interface_applicationInfo_with_accessTokenId();
    test_bundle_interface_applicationInfo_with_uid();
    test_bundle_interface_applicationInfo_with_entityType();

    // bundleInfo.d.ts
    test_bundleinfo_interface_usedScene_with_when();
    test_bundleinfo_interface_usedScene_with_abilities();
    test_bundleinfo_interface_reqperdetail_with_name();
    test_bundleinfo_interface_reqperdetail_with_reason();
    test_bundleinfo_interface_with_name();
    test_bundleinfo_interface_with_type();
    test_bundleinfo_interface_with_appId();
    test_bundleinfo_interface_withuid();
    test_bundleinfo_interface_with_installTime();
    test_bundleinfo_interface_with_updateTime();
    test_bundleinfo_interface_with_reqPermissions();
    test_bundleinfo_interface_with_vendor();
    test_bundleinfo_interface_with_versionCode();
    test_bundleinfo_interface_with_versionName();
    test_bundleinfo_interface_with_compatibleVersion();
    test_bundleinfo_interface_with_targetVersion();
    test_bundleinfo_interface_with_isCompressNativeLibs();
    test_bundleinfo_interface_with_entryModuleName();
    test_bundleinfo_interface_with_cpuAbi();
    test_bundleinfo_interface_with_isSilentInstallation();
    test_bundleinfo_interface_with_minCompatibleVersionCode();
    test_bundleinfo_interface_with_entryInstallationFree();
    test_bundleinfo_interface_with_reqPermissionStates();

    // customizeData.d.ts
    test_bundleinfo_interface_custdata_with_name();
    test_bundleinfo_interface_custdata_with_value();
    test_bundleinfo_interface_custdata_with_extra();

    // elementName.d.ts
    test_bundle_interface_elementName_with_deviceId_noSet();
    test_bundle_interface_elementName_with_deviceId();
    test_bundle_interface_elementName_with_bundleName();
    test_bundle_interface_elementName_with_abilityName();
    test_bundle_interface_elementName_with_uri_noSet();
    test_bundle_interface_elementName_with_uri();
    test_bundle_interface_elementName_with_shortName_noSet();
    test_bundle_interface_elementName_with_shortName();

    // hapModuleInfo.d.ts
    test_bundle_interface_hapModuleInfo_with_name();
    test_bundle_interface_hapModuleInfo_with_description();
    test_bundle_interface_hapModuleInfo_with_descriptionid();
    test_bundle_interface_hapModuleInfo_with_icon();
    test_bundle_interface_hapModuleInfo_with_label();
    test_bundle_interface_hapModuleInfo_with_labelid();
    test_bundle_interface_hapModuleInfo_with_iconid();
    test_bundle_interface_hapModuleInfo_with_backgroundImg();
    test_bundle_interface_hapModuleInfo_with_supportedModes();
    test_bundle_interface_hapModuleInfo_with_reqCapabilities();
    test_bundle_interface_hapModuleInfo_with_deviceTypes();
    test_bundle_interface_hapModuleInfo_with_moduleName();
    test_bundle_interface_hapModuleInfo_with_mainAbilityName();
    test_bundle_interface_hapModuleInfo_with_installationFree();

    // moduleInfo.d.ts
    test_bundle_interface_moduleInfo_with_moduleName();
    test_bundle_interface_moduleInfo_with_moduleSourceDir();

    // shortcutInfo.d.ts
    test_bundle_interface_shortcutInfo_with_id();
    test_bundle_interface_shortcutInfo_with_bundleName();
    test_bundle_interface_shortcutInfo_with_hostAbility();
    test_bundle_interface_shortcutInfo_with_icon();
    test_bundle_interface_shortcutInfo_with_iconId();
    test_bundle_interface_shortcutInfo_with_label();
    test_bundle_interface_shortcutInfo_with_labelId();
    test_bundle_interface_shortcutInfo_with_disableMessage();
    test_bundle_interface_shortcutInfo_with_isStatic();
    test_bundle_interface_shortcutInfo_with_isHomeShortcut();
    test_bundle_interface_shortcutInfo_with_isEnabled();

    // ohos.app.ability.Want.d.ts
    test_bundle_class_want_with_bundleName_noSet();
    test_bundle_class_want_with_bundleName();
    test_bundle_class_want_with_abilityName_noSet();
    test_bundle_class_want_with_abilityName();
    test_bundle_class_want_with_deviceId_noSet();
    test_bundle_class_want_with_deviceId();
    test_bundle_class_want_with_uri_noSet();
    test_bundle_class_want_with_uri();
    test_bundle_class_want_with_type_noSet();
    test_bundle_class_want_with_type();
    test_bundle_class_want_with_flags_noSet();
    test_bundle_class_want_with_flags();
    test_bundle_class_want_with_action_noSet();
    test_bundle_class_want_with_action();
    test_bundle_class_want_with_parameters_noSet();
    test_bundle_class_want_with_parameters();
    test_bundle_class_want_with_entities_noSet();
    test_bundle_class_want_with_entities();
    test_bundle_class_want_with_moduleName_noSet();
    test_bundle_class_want_with_moduleName();

    console.log("##############end BundleTest Tests#############");
}

main();
