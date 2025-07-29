import * as lib from "enum_test";

function main() {
  let color = lib.Color.GREEN;
  let nextColor = lib.nextEnum(color);
  console.log("nextColor: ", nextColor);
  let enum_v = lib.getValueOfEnum(color);
  console.log(enum_v);
  let value_e = lib.fromValueToEnum("Blue");
  console.log(value_e, value_e === lib.Color.BLUE)

  let weekday = lib.Weekday.THURSDAY;
  let nextday = lib.nextEnumWeekday(weekday);
  console.log("nextDay: ", nextday)
  let weekday_v = lib.getValueOfEnumWeekday(weekday);
  console.log(weekday_v);
  let value_w = lib.fromValueToEnumWeekday(1);
  console.log(value_w, value_w === lib.Weekday.MONDAY);

  console.log("const value: ", lib.FLAG_F32_A, lib.FLAG_STRING_ONE);
  console.log(lib.FLAG_F32_A === 1, lib.FLAG_STRING_ONE === "hello");
}

main();
