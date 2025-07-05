"use static"
import{AsyncCallback} from "@ohos.base";
import {BusinessError} from "@ohos.base";

import * as cookies_taihe from "cookies"

export class AntUserCookiesProviderClz implements
    cookies_taihe.AntUserCookiesProvider {
    cookieStore: Map<string, cookies_taihe.AntUserCookie[]> =
        new Map<string, cookies_taihe.AntUserCookie[]>();

    getCookiesString(url: string): string|undefined {
        let cookies = this.cookieStore.get(url);
        if (!cookies || cookies.length === 0) return undefined;
        return "Get";
    }

    hasCookies(url: string): boolean {
        let cookies = this.cookieStore.get(url);
        return cookies !== undefined && cookies.length > 0;
    }

    setCookies(cookies: cookies_taihe.AntUserCookie[]): boolean {
        for (let cookie of cookies) {
            let key = cookie.domain;
            let list = this.cookieStore.get(key) ??
                [] as cookies_taihe.AntUserCookie[];
            list.push(cookie);
            this.cookieStore.set(key, list);
        }
        return true;
    }

    setCookiesAsync(
        cookies: cookies_taihe.AntUserCookie[],
        callback: (res: boolean) => void): void {
        setTimeout(() => {
            let result = this.setCookies(cookies);
            callback(result);
        }, 0);
    }

    removeCookies(url: string): boolean {
        return this.cookieStore.delete(url);
    }

    clearCookies(): boolean {
        this.cookieStore.clear();
        return true;
    }

    clearCookiesAsync(callback: (res: boolean) => void): void {
        setTimeout(() => {
            this.clearCookies();
            callback(true);
        }, 0);
    }

    saveCookies(): boolean {
        console.log("Simulated saving cookies...");
        return true;
    }

    saveCookiesAsync(callback: (res: boolean) => void): boolean {
        setTimeout(() => {
            console.log("Simulated async save");
            callback(true);
        }, 0);
        return true;
    }
}
