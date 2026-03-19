$fn = 100;

l = 159.8;
w = 74.5;
h = 8.4;
//measured maximum sizes from some shop page but they seem realistic

thickness = 1.5;
outer_thickness = 3;

speaker_dist = 20;

cam_dist_y = 7;
cam_dist_x = 7;

cam_width = 20; //with tolerance
cam_length = 40; //with tolerance
cam_height = 2;

cam_radius_corners = 5;

dist_sound_button = 30;
dist_power_button = 60;
length_sound_button = 20;
length_power_button = 10;

leftright_bottom_spaces = 10;

magnet_flip_width = 15;

tolerance = 0.1;

eta = 0.05;

pi = 3.141592653589793238462643383279502884197169399375105820974944592307816406286208;


module rounded_box(w,l,h,r){
    hull(){
        translate([w/2-r,l/2-r,0])cylinder(h=h,r=r);
    translate([w/2-r,-l/2+r,0])cylinder(h=h,r=r);
    translate([-w/2+r,l/2-r,0])cylinder(h=h,r=r);
    translate([-w/2+r,-l/2+r,0])cylinder(h=h,r=r);
    }
}


module rounded_cube(w,l,h){
    hull(){
    translate([w/2-h/2, l/2-h/2,0])sphere(h/2);
    translate([-w/2+h/2, l/2-h/2,0])sphere(h/2);
    translate([w/2-h/2, -l/2+h/2,0])sphere(h/2);
    translate([-w/2+h/2, -l/2+h/2,0])sphere(h/2);
    }
}


module phone(){
    union(){
    translate([w/2, l/2-dist_sound_button-length_sound_button,0])cube([1,length_sound_button,1]);
    
    translate([w/2, l/2-dist_power_button-length_power_button,0])cube([1,length_power_button,1]);
    
    translate([w/2-cam_dist_x-cam_width/2, l/2-cam_dist_y-cam_length/2,-h/2-cam_height])rounded_box(cam_width, cam_length, cam_height, cam_radius_corners);
    rounded_cube(w,l,h);
}
}


module case(){
    union(){
    difference(){
    rounded_cube(w+2*thickness,l+2*thickness,h+2*thickness);
    rounded_cube(w,l,h);
    translate([0,0,h/2-thickness])rounded_box(w-h/3,l-h/3,thickness*2, h/2);//TODO
    translate([-w/2+leftright_bottom_spaces,-l/2-thickness,thickness-h/2])cube([w-2*leftright_bottom_spaces,h+thickness,h]);
    translate([w/2-cam_dist_x-cam_width/2, l/2-cam_dist_y-cam_length/2,-h/2-thickness])rounded_box(cam_width, cam_length, thickness*2, cam_radius_corners);
    translate([w/2-thickness/2, l/2-dist_sound_button-length_sound_button/2,0])rotate([0,90,0])rounded_box(3, length_sound_button, thickness*2, 1);
    translate([w/2-thickness/2, l/2-dist_power_button-length_power_button/2,0])rotate([0,90,0])rounded_box(3, length_power_button, thickness*2, 1);
    translate([w/2-speaker_dist-2.5, l/2+thickness,0])rotate([90,0,0])rounded_box(5, 3, thickness*2, 1);
    }
    
    translate([w/2+thickness/2, l/2-dist_sound_button-length_sound_button/2,0])rotate([0,90,0])rounded_box(3, length_sound_button, thickness, 1);
    translate([w/2+thickness/2, l/2-dist_power_button-length_power_button/2,0])rotate([0,90,0])rounded_box(3, length_power_button, thickness, 1);
}
}



module flipcase(){
    difference(){
    union(){
    translate([w/2+thickness,0,h/2+thickness])case();
    difference(){
    translate([w/2+thickness, 0, -outer_thickness])rounded_box(w+2*thickness, l+2*thickness, outer_thickness, h/2+thickness);
    translate([-eta,-l/2-thickness-eta, -outer_thickness-eta])cube([h/2+thickness+eta, l+2*thickness+2*eta,outer_thickness+2*eta]);
    translate([w+thickness-cam_dist_x-cam_width/2, l/2-cam_dist_y-cam_length/2,-outer_thickness*2])rounded_box(cam_width, cam_length, outer_thickness*3, cam_radius_corners);
    }
    translate([h/2+thickness-pi/2*(h+thickness*2+outer_thickness*2)-2*tolerance,-l/2-thickness, -outer_thickness])cube([pi/2*(h+thickness*2+outer_thickness*2)+2*tolerance, l+2*thickness, outer_thickness/2]);
    
    translate([h+2*thickness-pi/2*(h+thickness*2+outer_thickness*2)-2*tolerance,0,-outer_thickness])rotate([0,180,0])difference(){
    translate([w/2+thickness, 0, -outer_thickness])rounded_box(w+2*thickness, l+2*thickness, outer_thickness, h/2+thickness);
    translate([-eta,-l/2-thickness-eta, -outer_thickness-eta])cube([h/2+thickness+eta, l+2*thickness+2*eta,outer_thickness+2*eta]);
    }
    translate([w+2*thickness,-magnet_flip_width/2, -outer_thickness])cube([h+2*thickness+2*outer_thickness+2*tolerance, magnet_flip_width, outer_thickness/2]);
    translate([w+2*thickness,-magnet_flip_width/2, -outer_thickness])cube([h+2*thickness+2*outer_thickness+2*tolerance, magnet_flip_width, outer_thickness/2]);
    translate([h+4*thickness+2*outer_thickness+w,-magnet_flip_width/2, -outer_thickness])cube([(h+2*thickness+2*outer_thickness)/2, magnet_flip_width, outer_thickness]);
    translate([w+4*thickness+h+2*outer_thickness+(h+2*thickness+2*outer_thickness)/2,0, -outer_thickness])rounded_box(h+2*thickness+2*outer_thickness, magnet_flip_width, outer_thickness,magnet_flip_width/2);   
    }
    // magnets
    translate([w+4*thickness+h+2*outer_thickness+h+2*thickness+2*outer_thickness-magnet_flip_width/2,0,-outer_thickness+(outer_thickness-2)/2-tolerance])cylinder(h=2+tolerance,r=3+tolerance*2);
    translate([h/2+thickness-pi/2*(h+thickness*2+outer_thickness*2)-2*tolerance-w+2*thickness+magnet_flip_width/2,0,-outer_thickness+(outer_thickness-2)/2-tolerance])cylinder(h=2+tolerance,r=3+tolerance*2);
    }
}



translate([w+4*thickness+h+2*outer_thickness+h+2*thickness+2*outer_thickness-magnet_flip_width/2,0,-outer_thickness+(outer_thickness-2)/2-tolerance])cylinder(h=2+tolerance,r=3+tolerance*2);
    translate([h/2+thickness-pi/2*(h+thickness*2+outer_thickness*2)-2*tolerance-w+2*thickness+magnet_flip_width/2,0,-outer_thickness+(outer_thickness-2)/2-tolerance])cylinder(h=2+tolerance,r=3+tolerance*2);








flipcase();







//TODO look if bottom plate needs to be wider

//translate([-w/2, -l/2,0])cube([w,l,(h+thickness)*2]);
//color("yellow",0.4)cube([l,w,h], center=true); 

//color("yellow", 0.4)translate([w/2-cam_dist_x-cam_width, l/2-cam_dist_y-cam_height,-h/2-thickness])cube([cam_width, cam_height,thickness]);

