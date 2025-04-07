import * as inherit from "@generated/inherit";
loadLibrary("inherit");

function main() {
    // 初始化银行卡
    let card = inherit.makeCreditCard(1000.0);
    // 查看当前是否可以进行国际交易
    console.log(card.intlEnabled);
    // 设置为可进行国际交易
    card.intlEnabled = true;
    // 查看当前是否可以进行国际交易
    console.log(card.intlEnabled);
    // 查看余额
    console.log(card.balance);
    // 购买一件国际商品
    console.log("Buy an international product")
    card.pay(50.0);
    // 查看余额
    console.log(card.balance);
}
