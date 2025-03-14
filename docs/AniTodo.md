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

## Class: 方法型

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

- 案例目标：用 Taihe 生成带有 property 和 method 的 Class

## Interface: 方法型

```typescript
export interface CommonEventSubscriber {
    getCode(callback: AsyncCallback<number>): void;
    getCode(): Promise<number>;
    getCodeSync(): number;
    setCode(code: number, callback: AsyncCallback<void>): void;
    setCode(code: number): Promise<void>;
    setCodeSync(code: number): void;
    getData(callback: AsyncCallback<string>): void;
    getData(): Promise<string>;
    getDataSync(): string;
    setData(data: string, callback: AsyncCallback<void>): void;
    setData(data: string): Promise<void>;
    setDataSync(data: string): void;
    setCodeAndData(code: number, data: string, callback: AsyncCallback<void>): void;
    setCodeAndData(code: number, data: string): Promise<void>;
    setCodeAndDataSync(code: number, data: string): void;
    isOrderedCommonEvent(callback: AsyncCallback<boolean>): void;
    isOrderedCommonEvent(): Promise<boolean>;
    isOrderedCommonEventSync(): boolean;
    isStickyCommonEvent(callback: AsyncCallback<boolean>): void;
    isStickyCommonEvent(): Promise<boolean>;
    isStickyCommonEventSync(): boolean;
    abortCommonEvent(callback: AsyncCallback<void>): void;
    abortCommonEvent(): Promise<void>;
    abortCommonEventSync(): void;
    clearAbortCommonEvent(callback: AsyncCallback<void>): void;
    clearAbortCommonEvent(): Promise<void>;
    clearAbortCommonEventSync(): void;
    getAbortCommonEvent(callback: AsyncCallback<boolean>): void;
    getAbortCommonEvent(): Promise<boolean>;
    getAbortCommonEventSync(): boolean;
    getSubscribeInfo(callback: AsyncCallback<CommonEventSubscribeInfo>): void;
    getSubscribeInfo(): Promise<CommonEventSubscribeInfo>;
    getSubscribeInfoSync(): CommonEventSubscribeInfo;
    finishCommonEvent(callback: AsyncCallback<void>): void;
    finishCommonEvent(): Promise<void>;
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

## Namespace

- d.ts 场景：@ohos.request.d.ts

```typescript
declare namespace request {
    namespace agent {
        enum Action {
            DOWNLOAD,
            UPLOAD
        }
    }
}
```

## Others
- wantConstants: enum with string
- ohos.application.formBindingData: namespace
- const
- callback: on/off
- @ohos.contract.d.ts
  - static readonly
- @ohos.intl.d.ts: multiple constructors and overload
