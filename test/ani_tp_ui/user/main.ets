import {BusinessError} from "@ohos.base";
import * as ui from "ui"
import * as ui_impl from "ui_impl";
import * as ui_user from "ui_user";

loadLibrary("ani_tp_ui");

function main() {
    let body: ui.AntUserDialogBody = {
        title: "body_title",
        detail: "body_detail",
        traceParams: undefined
    };

    let controller: ui_impl.AntUserModalControllerClz =
        new ui_impl.AntUserModalControllerClz("controller1");
    let provider: ui_impl.AntUserUIProviderClz =
        new ui_impl.AntUserUIProviderClz(controller);
    ui_user.runNativeBusiness(provider, body);
}