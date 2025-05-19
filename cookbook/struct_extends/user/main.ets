import * as structext from "structext";
import {BusinessError} from "@ohos.base";

loadLibrary("struct_extends");

function main() {
    let Player1 = structext.addNewPlayer("Tom");
    let Player2 = structext.addNewPlayer("Jimmy");
    console.log("Player1's name is " + Player1.name);
    console.log("Player2's name is " + Player2.name);
    Player2.x += 1;
    Player2.y += 1;
    Player2.z += 1;
    console.log(
        "Player1's position is " + Player1.x + "," + Player1.y + "," +
        Player1.z);
    console.log(
        "Player2's position is " + Player2.x + "," + Player2.y + "," +
        Player2.z);
}