import {window, get_interface, check_interface} from "../author_generated/interface"

loadLibrary("interface")
function main() {
    let win: window = get_interface();
    let res = win.getheight();
    console.log(res);
    win.setheight(20);
    res = win.getheight();
    console.log(res);

    check_interface(win)
}