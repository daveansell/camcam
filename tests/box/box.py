import cc3d
fudge = 0.2
box_thickness=12
w=100

plane = camcam.add_plane(Plane('xy', cutter='1/8_endmill'))

plane.add_layer('one', 'delrin', box_thickness, colour='#005000')
plane.add_layer('two', 'delrin', box_thickness, colour='#005000')

box = plane.add(ArbitraryBox(
        faces = {
		'one':{
			'points':[
				V(w,w,0),
				V(-w,w,0),
				V(-w,-w,0),
				V(w,-w,0),
			],
			'x':V(1.0,0.0,0.0),
			'origin':V(0, 0, 0),
			'layer':'one',
			'wood_direction':V(0.0,0.0,-1.0),
			'good_direction':V(0.0,0.0,-1.0),
			'thickness':box_thickness,
		},
		'two':{
			'points':[
				V(w,w,0),
				V(-w,w,0),
				V(-w,w,w),
				V(w,w,w),
			],
			'x':V(1.0,0.0,0.0),
			'layer':"two",
			'thickness':box_thickness,
		},
		'three':{
			'points':[
				V(w,-w,w),
				V(-w,-w,w),
				V(-w,-w,0),
				V(w,-w,0),
			],
			'x':V(-1.0,0.0,0.0),
			'layer':"two",
			'thickness':box_thickness,
		},
	},
	fudge = fudge,
	tab_length = 60,
	thickness = box_thickness,
#	joint_mode = "butt",
	hole_spacing = 250,
	holerad = 4.5,
	butt_depression = 0,
	name="steel",
))

