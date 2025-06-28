import * as lib_people from "../generated/people";
import * as lib_building from "../generated/building";

function main() {
    let g = lib_building.make_group(); 
    console.log(g.member.age, g.member.name, g.number);
    let p = lib_people.make_student();
    console.log(p.age, p.name);
}

main();