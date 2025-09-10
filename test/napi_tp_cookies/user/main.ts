import * as cookies_impl from "./cookies_impl";
import * as cookies_user from "cookies_user";

function main() {
    let cookieProvider = new cookies_impl.AntUserCookiesProviderClz();
    cookies_user.RunNativeBusiness(cookieProvider);
}

main()