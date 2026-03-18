$fn = 100;

l = 159.8;
w = 74.5;
h = 8.4;
//measured maximum sizes from some shop page but they seem realistic

thickness = 2;

scaling = 99/100;

speaker_dist = 20;

cam_dist_y = 7;
cam_dist_x = 7;

cam_width = 20; //with tolerance
cam_height = 40; //with tolerance

cam_radius_corners = 5;

dist_sound_button = 30;
dist_power_button = 60;
length_sound_button = 20;
length_power_button = 10;

leftright_bottom_spaces = 10;

color("blue", 0.4)union(){
    translate([w/2, l/2-dist_sound_button-length_sound_button,0])cube([1,length_sound_button,1]);
    
    translate([w/2, l/2-dist_power_button-length_power_button,0])cube([1,length_power_button,1]);
    
    translate([w/2-cam_dist_x-cam_width/2, l/2-cam_dist_y-cam_height/2,-h/2-thickness])hull(){
        translate([cam_width/2-cam_radius_corners,cam_height/2-cam_radius_corners,0])cylinder(h=thickness,r=cam_radius_corners);
    translate([cam_width/2-cam_radius_corners,-cam_height/2+cam_radius_corners,0])cylinder(h=thickness,r=cam_radius_corners);
    translate([-cam_width/2+cam_radius_corners,cam_height/2-cam_radius_corners,0])cylinder(h=thickness,r=cam_radius_corners);
    translate([-cam_width/2+cam_radius_corners,-cam_height/2+cam_radius_corners,0])cylinder(h=thickness,r=cam_radius_corners);
    }
    
    
    
    hull(){
        translate([w/2-h/2, l/2-h/2,0])sphere(h/2);
    translate([-w/2+h/2, l/2-h/2,0])sphere(h/2);
    translate([w/2-h/2, -l/2+h/2,0])sphere(h/2);
    translate([-w/2+h/2, -l/2+h/2,0])sphere(h/2);
    }
    
}



//color("yellow",0.4)cube([l,w,h], center=true); 

//color("yellow", 0.4)translate([w/2-cam_dist_x-cam_width, l/2-cam_dist_y-cam_height,-h/2-thickness])cube([cam_width, cam_height,thickness]);

