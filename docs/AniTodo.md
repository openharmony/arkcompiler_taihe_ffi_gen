# ANI Cookbook 里程碑

## 混合开发: ANI + STS 代码

- d.ts 场景：ohos.app.ability.Want

```typescript
export default class Want {
    bundleName?: string;
    abilityName?: string;
    deviceId?: string;
    uri?: string;
    type?: string;
    flags?: number;
    action?: string;
    parameters?: Record<string, Object>;
    entities?: Array<string>;
    moduleName?: string;
}
```

- 现有 ANI 代码：使用 STS 编写高级语言逻辑，见 https://gitee.com/openharmony/ability_ability_runtime/blob/OpenHarmony_feature_20241108/frameworks/ets/ani/ui_ability/ets/%40ohos.app.ability.Want.ets#L188
- 案例目标：用 STS 高级逻辑来操作 Taihe 生成的数据结构

## Class: 值类型

- d.ts 场景：Matrix2D (@internal/full/canvaspattern.d.ts)

```typescript
export class Matrix2D {
    scaleX?: number;
    rotateY?: number;
    rotateX?: number;
    scaleY?: number;
    translateX?: number;
    translateY?: number;
    identity(): Matrix2D;
    invert(): Matrix2D;
    multiply(other?: Matrix2D): Matrix2D;
    rotate(rx?: number, ry?: number): Matrix2D;
    translate(tx?: number, ty?: number): Matrix2D;
    scale(sx?: number, sy?: number): Matrix2D;
    constructor();
}
```

- 案例目标：用 Taihe 生成带有 property 和 method 的 Class

## Class: 继承

- d.ts 场景（application/UIAbilityContext.d.ts）

```typescript
export default class UIAbilityContext extends Context {
    abilityInfo: AbilityInfo;
    currentHapModuleInfo: HapModuleInfo;
    config: Configuration;
    windowStage: window.WindowStage;

    restoreWindowStage(localStorage: LocalStorage): void;
    isTerminating(): boolean;
    // ...
}
```

- 现有 ANI 实现：https://gitee.com/openharmony/ability_ability_runtime/blob/OpenHarmony_feature_20241108/frameworks/ets/ani/ui_ability/ets/application/UIAbilityContext.ets#L37

## Interface: 方法型

```typescript
// @ohos.abilityAccessCtrl.d.ts
interface AtManager {
    verifyAccessToken(tokenID: number, permissionName: Permissions): Promise<GrantStatus>;
    verifyAccessToken(tokenID: number, permissionName: string): Promise<GrantStatus>;
    verifyAccessTokenSync(tokenID: number, permissionName: Permissions): GrantStatus;
    checkAccessToken(tokenID: number, permissionName: Permissions): Promise<GrantStatus>;
    checkAccessTokenSync(tokenID: number, permissionName: Permissions): GrantStatus;
    requestPermissionsFromUser(context: Context, permissionList: Array<Permissions>, requestCallback: AsyncCallback<PermissionRequestResult>): void;
    requestPermissionsFromUser(context: Context, permissionList: Array<Permissions>): Promise<PermissionRequestResult>;
    requestPermissionOnSetting(context: Context, permissionList: Array<Permissions>): Promise<Array<GrantStatus>>;
    requestGlobalSwitch(context: Context, type: SwitchType): Promise<boolean>;
}
```

## Async 代理

- d.ts 场景：将 Sync 函数封装为 Async 版本

```typescript
  export function importKeyItem(keyAlias: string, options: HuksOptions, callback: AsyncCallback<void>): void {
    let p1 = taskpool.execute(importKeyItemSync, keyAlias, options);
    p1.then<void>((ret : NullishType) => {
        let retInner = ret as HuksResult;
        let errMsg = '';
        if (errMsg != undefined) {
          errMsg = retInner.error as string;
        }
        let eNull = new BusinessError(retInner.result, errMsg);
        callback(eNull);
    });
  }
```

- 模板化代码，可自动生成

## Namespace: 嵌套

```typescript
// @ohos.request.d.ts
declare namespace request {
    namespace agent {
        enum Action {
            DOWNLOAD,
            UPLOAD
        }
    }
}
```

## Namespace: 合并其他类型
```typescript
// @ohos.app.form.formBindingData.d.ts
declare namespace formBindingData {
    function createFormBindingData(obj?: Object | string): FormBindingData;
    interface FormBindingData {
        data: Object;
        proxies?: Array<ProxyData>;
    }
    interface ProxyData {
        key: string;
        subscriberId?: string;
    }
}
export default formBindingData;
```

## Constants: Enum with String

```typescript
// ./@ohos.app.ability.wantConstant.d.ts
declare namespace wantConstant {
    export enum Params {
        ABILITY_BACK_TO_OTHER_MISSION_STACK = 'ability.params.backToOtherMissionStack',
        ABILITY_RECOVERY_RESTART = 'ohos.ability.params.abilityRecoveryRestart',
        CONTENT_TITLE_KEY = 'ohos.extra.param.key.contentTitle',
        SHARE_ABSTRACT_KEY = 'ohos.extra.param.key.shareAbstract',
        SHARE_URL_KEY = 'ohos.extra.param.key.shareUrl',
        SUPPORT_CONTINUE_PAGE_STACK_KEY = 'ohos.extra.param.key.supportContinuePageStack',
        SUPPORT_CONTINUE_SOURCE_EXIT_KEY = 'ohos.extra.param.key.supportContinueSourceExit',
        SHOW_MODE_KEY = 'ohos.extra.param.key.showMode',
        PARAMS_STREAM = 'ability.params.stream',
        APP_CLONE_INDEX_KEY = 'ohos.extra.param.key.appCloneIndex',
        CALLER_REQUEST_CODE = 'ohos.extra.param.key.callerRequestCode',
        PAGE_PATH = 'ohos.param.atomicservice.pagePath',
        ROUTER_NAME = 'ohos.param.atomicservice.routerName',
        PAGE_SOURCE_FILE = 'ohos.param.atomicservice.pageSourceFile',
        BUILD_FUNCTION = 'ohos.param.atomicservice.buildFunction',
        SUB_PACKAGE_NAME = 'ohos.param.atomicservice.subpackageName'
    }
    export enum Flags {
        FLAG_AUTH_READ_URI_PERMISSION = 0x00000001,
        FLAG_AUTH_WRITE_URI_PERMISSION = 0x00000002,
        FLAG_AUTH_PERSISTABLE_URI_PERMISSION = 0x00000040,
        FLAG_INSTALL_ON_DEMAND = 0x00000800,
        FLAG_START_WITHOUT_TIPS = 0x40000000
    }
    export enum ShowMode {
        WINDOW = 0,
        EMBEDDED_FULL = 1
    }
}
export default wantConstant;
```

## Constants: `static readonly`
```
// @ohos.contact.d.ts
class ImAddress {
    static readonly CUSTOM_LABEL: -1;
    static readonly IM_AIM: 0;
    static readonly IM_MSN: 1;
    static readonly IM_YAHOO: 2;
    static readonly IM_SKYPE: 3;
    static readonly IM_QQ: 4;
    static readonly IM_ICQ: 6;
    static readonly IM_JABBER: 7;
    static readonly INVALID_LABEL_ID: -2;
    imAddress: string;
    labelName?: string;
    labelId?: number;
}
```

### Function: 重载

```typescript
// @ohos.intl.d.ts
export class Collator {
    constructor();
    constructor(locale: string | Array<string>, options?: CollatorOptions);
    compare(first: string, second: string): number;
    resolvedOptions(): CollatorOptions;
}
```

### Callback
```typescript
function on(type: 'locationChange', request: LocationRequest | ContinuousLocationRequest, callback: Callback<Location>): void;
function off(type: 'locationChange', callback?: Callback<Location>): void;
```
