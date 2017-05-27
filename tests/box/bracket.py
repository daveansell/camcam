import cc3d
fudge = 0.2
box_thickness=12
w=400

plane = camcam.add_plane(Plane('xy', cutter='1/8_endmill'))

plane.add_layer('one', 'delrin', box_thickness, colour='#005000')
plane.add_layer('two', 'delrin', box_thickness, colour='#005000')
plane.add_layer('three', 'delrin', box_thickness, colour='#005000')
plane.add_layer('four', 'delrin', box_thickness, colour='#005000')
plane.add_layer('five', 'delrin', box_thickness, colour='#005000')

box = plane.add(ArbitraryBox(
        faces = {
		'one':{
			'points':[
				V(w,2*w,0),
				V(-w,w,0),
				V(-w,-w,0),
				V(w,-2*w,0),
			],
			'x':V(1.0,0.0,0.0),
#			'origin':V(0, 0, 0),
			'layer':'one',
			'wood_direction':V(0.0,0.0,-1.0),
			'good_direction':V(0.0,0.0,-1.0),
			'thickness':box_thickness,
		},
		'two':{
			'points':[
				V(w,2*w,0),
				V(-w,w,0),
				V(-w,w,w),
				V(w,2*w,w),
			],
#			'x':V(1.0,0.0,0.0),
#			'y':V(0.0,0.0,1.0),
#			'origin':V(-w,w,0),
			'layer':"two",
			'thickness':box_thickness,
		},
		'three':{
			'points':[
				V(w,0,w),
				V(-w,0,w),
				V(-w,0,0),
				V(w,0,0),
			],
			'x':V(1.0,0.0,0.0),
			'y':V(0.0,0.0,1.0),
			'origin':V(-w,0,0),
			'layer':"three",
			'thickness':box_thickness,
			'alt_wood_direction':V(0.0,0.0,-1.0),
			'alt_good_direction':V(0.0,0.0,-1.0),
		},
		'four':{
			'points':[
				V(w,-2*w,0),
				V(-w,-w,0),
				V(-w,-w,w),
				V(w,-2*w,w),
			],
			'layer':"four",
			'thickness':box_thickness,
		},
	},
	fudge = fudge,
	tab_length = 30,
	thickness = box_thickness,
#	joint_mode = "butt",
	hole_spacing = 200,
	holerad = 4.5,
	butt_depression = 0,
	name="steel",
	joint_mode='bracket',
	bracket_args={'bracket_type':'sabrefix60x50'},
        bracket=Bracket,

))
box.face_one.ignore_border=True
box.face_two.ignore_border=True
box.face_three.add(Hole(V(50,50), rad=5))
box.face_two.add(Hole(V(50,50), rad=5))
