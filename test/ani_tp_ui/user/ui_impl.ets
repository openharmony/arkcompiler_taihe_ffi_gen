"use static";

import * as ui_taihe from "ui";

export class AntUserModalControllerClz implements
    ui_taihe.AntUserModalController {
    name: string = ""

    constructor(name: string) {
        this.name = name;
    }

    dismiss(): void {
        console.log(this.name + ": Dialog dismissed");
    }
}

export class AntUserUIProviderClz implements ui_taihe.AntUserUIProvider {
    controller: ui_taihe.AntUserModalController;

    constructor(controller: ui_taihe.AntUserModalController) {
        this.controller = controller;
    }

    showLoading(): ui_taihe.AntUserModalController {
        console.log("showLoading()");
        return this.controller;
    }

    showToast(text: string): ui_taihe.AntUserModalController {
        console.log("showToast()");
        return this.controller;
    }

    showDialog(
        body: ui_taihe.AntUserDialogBody,
        actions: ui_taihe.AntUserDialogAction[]):
        ui_taihe.AntUserModalController {
        console.log("Show dialog:", body.title, body.detail);
        actions.forEach((action, idx) => {
            console.log(`Action ${idx}: ${action.name}`);
        });
        for (let i = 0; i < actions.length; i++) {
            actions[i].action();
        }
        return this.controller;
    }
}