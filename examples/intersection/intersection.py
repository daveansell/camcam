
# rectangle with 4 holes
w=400
W=100
H=100
x1=200
thickness=9

plane = camcam.add_plane(Plane('xy', cutter='1/8_endmill'))

# add layer

box = plane.add(ArbitraryBox(
                faces={
		    'mid2':{
        		'points':[V(-w,-H+5,0), V(-w,H+5,0), V(w,H+25,0), V(w,-H+5,0)],
        		'origin':V(0,0,0),
        		'x':V(1,0,0),
        		'good_direction':V(0,0,1),
        		'wood_direction':V(0,0,1),
        		'material':'plywood',
        		'thickness':thickness,
			},
		    'mid1':{
        		'points':[V(0,-H,W), V(0,H,W), V(0,H,-W), V(0,-H,-W)],
        		'origin':V(0,0,0),
        		'x':V(0,1,0),
        		'good_direction':V(1,0,0),
        		'wood_direction':V(1,0,0),
        		'material':'plywood',
        		'thickness':thickness,
			},
		    'mid3':{
        		'points':[V(x1,-H,W), V(x1,H,W), V(x1,H,-W), V(x1,-H,-W)],
        		'origin':V(x1,0,0),
        		'x':V(0,1,0),
        		'good_direction':V(1,0,0),
        		'wood_direction':V(1,0,0),
        		'material':'plywood',
        		'thickness':thickness,
			},
		    'mid4':{
        		'points':[V(w+W,-H/2,W), V(w-W,-H/2,W), V(w-W,-H/2,-W), V(w+W,-H/2,-W)],
        		'origin':V(w,-H/2,0),
        		'x':V(1,0,0),
        		'good_direction':V(0,1,0),
        		'wood_direction':V(0,1,0),
        		'material':'plywood',
        		'thickness':thickness,
			},



                },
                thickness = 9.0,
                name = "dave",
                fudge = 0.1,
                tab_length = 100,
                hole_spacing =100,
                joint_mode='butt',

))

