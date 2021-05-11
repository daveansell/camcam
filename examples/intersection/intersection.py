
# rectangle with 4 holes
W=100
H=100
thickness=9

plane = camcam.add_plane(Plane('xy', cutter='1/8_endmill'))

# add layer

box = plane.add(ArbitraryBox(
                faces={
		    'mid2':{
        		'points':[V(-W,-H+5,0), V(-W,H,0), V(W,H,0), V(W,-H+5,0)],
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



                },
                thickness = 9.0,
                name = "dave",
                fudge = 0.1,
                tab_length = 100,
                hole_spacing =100,
                joint_mode='butt',

))

