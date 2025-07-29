import * as lib_people from "people";
import * as lib_building from "building";

function main() {
    let g = lib_building.make_group(); 
    console.log(g.member.age, g.member.name, g.number);
    let p = lib_people.make_student();
    console.log(p.age, p.name);
}

main();