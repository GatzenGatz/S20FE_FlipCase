l = 159.8;
w = 74.5;
h = 8.4;
//measured maximum sizes from some shop page but they seem realistic


color("yellow",0.4)cube([l,w,h], center=true); 



color("green", 0.8){
    translate([l/2-h/2, w/2-h/2,0])sphere(h/2);
    translate([-l/2+h/2, w/2-h/2,0])sphere(h/2);
    translate([l/2-h/2, -w/2+h/2,0])sphere(h/2);
    translate([-l/2+h/2, -w/2+h/2,0])sphere(h/2);
}


