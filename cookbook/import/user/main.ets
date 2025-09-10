import {BusinessError} from "@ohos.base";
import * as notification from "notification";
import * as user from "user";

loadLibrary("import");

function main() {
    let userA = user.makeUser("12345@huawei.com");
    let userB = user.makeUser("67890@outlook.com");
    let noter = notification.makeNotificationService();
    noter.sendMessage(userA);
    noter.sendMessage(userB);
}