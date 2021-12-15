from gears import *

#import scipy
# rectangle with 4 holes

# variables we might want to edit later

plane = camcam.add_plane(Plane('xy', cutter='1/8_endmill'))
    
plane.add_layer('simpleBorder', 'delrin', 5)#5)#5)#5)#5)#flangeThickness, zoffset=flangeThickness) 
thickness=1.5
width = 440-thickness*2
length = 350
depth = 5.25 * inch
mountSpacing = 3.5 * inch
mountSpacingX=465.1
earLength = (19*inch-width)/2
frontHeight = 3.5 *inch - thickness 
backFoldHeight = 8
frontFoldLength=25.0
fanLength=20.0
print ("earlenght="+str(earLength))
faces={
    'base':{
        'points':[
#            PSharp(V(-width/2, 0.1, 0)),
            PSharp(V(-width/2, fanLength, 0)),
            PSharp(V(width/2, fanLength, 0)),
            PSharp(V(width/2, length, 0)),
            PSharp(V(-width/2, length, 0)),
            ],
        'origin':V(0,0,0),
        'x':V(1,0,0),
        'good_direction':V(0,0,-1),
        'wood_direction':V(0,0,-1),
        'material':'steel',
        'thickness':thickness,
        },
    'front':{
        'points':[
            PSharp(V(width/2, fanLength, 0)),
        #    PSharp(V(width/2-50, fanLength, frontHeight/3)),
            PSharp(V(width/2, fanLength, frontHeight)),
            #PSharp(V(0, fanLength, frontHeight*2)),
            PSharp(V(-width/2, fanLength, frontHeight)),
            PSharp(V(-width/2, fanLength, 0)),
            ],
        'origin':V(0,fanLength,0),
        'x':V(1,0,0),
#        'good_direction':V(0,0,),
 #       'wood_direction':V(0,0,-1),
        'material':'steel',
        'thickness':thickness,
        },
  
}

box = plane.add(ArbitraryBox(
                faces=faces,
                thickness = 9.0,
                name = "dave",
                fudge = 0.1,
                tab_length = 30,
                hole_spacing =30,
                joint_mode='fold',
           #     joint_mode='straight',

))


