import {BusinessError} from "@ohos.base";
import * as cookies from "cookies"
import * as cookies_impl from "cookies_impl";
import * as cookies_user from "cookies_user";

loadLibrary("ani_tp_cookies");

function main() {
    let cookieProvider = new cookies_impl.AntUserCookiesProviderClz();
    cookies_user.runNativeBusiness(cookieProvider);
}