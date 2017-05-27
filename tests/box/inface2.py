import cc3d
fudge = 0.2
box_thickness=12
w=100
steelWidth = 1200.0
steelHeight = 2000.0
steelTopWall = 60.0
wallAngle=steelTopWall
steelBottomWall = 220
steelFromFloor = 120.0
wallFromFloor = 10.0
wallTop = math.sqrt((steelHeight+steelFromFloor)**2 - (steelBottomWall-steelTopWall)**2)
wallBottomWall = wallFromFloor

skirtingWidth = 18
skirtingHeight = 200

angle = math.atan((steelBottomWall-steelTopWall)/(steelHeight+steelFromFloor))

trayWidth = 300.0
trayFloorFront = 120.0
trayFloorBack = 70.0
traycorner = V( 0, steelBottomWall, wallFromFloor) + V(0, -math.sin(angle)*trayFloorBack,trayFloorBack)
trayFront = 180

topWidth = 400

box_thickness = 12.0
front_thickness = 18.0

windowThickness = 6

blowerWidth = 60.0
blowerHeight = 2000.0
blowerTopWall = 60.0
blowerBottomWall = 220
blowerFromFloor = 120.0
blowerTubeSpace = blowerWidth

tubeRad = 50/2
tubeLength = 1500

blowerWallBack = (blowerTubeSpace + windowThickness ) * math.cos(angle)
#blowerWallBack =0
windowBack = windowThickness* math.cos(angle)
wallPerp = rotate( (V( steelWidth/2, 0, 0) +traycorner -V( steelWidth/2, steelTopWall, wallTop)).normalize(), 90.0, V(1,0,0))
print "%%"+str(wallPerp)

plane = camcam.add_plane(Plane('xy', cutter='1/8_endmill'))

plane.add_layer('one', 'delrin', box_thickness, colour='#005000')
plane.add_layer('two', 'delrin', box_thickness, colour='#005000')
plane.add_layer('three', 'delrin', box_thickness, colour='#005000')
plane.add_layer('base', 'plywood', box_thickness)
plane.add_layer('mid', 'plywood', box_thickness)



box = plane.add(ArbitraryBox(
        faces = {
                'mid':{
                        'points':[
                #               V(-steelWidth/2, steelBottomWall, wallFromFloor),
                                V( box_thickness, -skirtingWidth, skirtingHeight),
                                V( box_thickness, 0, skirtingHeight),
				V( box_thickness, -200, skirtingHeight),
				V( box_thickness, -200, 0),
                                V( box_thickness, 0, 0),
                                V( box_thickness, 0, 0) +V(0,traycorner[1] + box_thickness,0),
                                V( box_thickness, 0, 0) +traycorner + wallPerp * box_thickness,
                                V( box_thickness, 0, 0) +traycorner
                        ],
                        'x':V(0.0,1.0,0.0),
                        'origin':V(box_thickness, 0, 0),
                        'layer':'mid',
                        'alt_wood_direction':V( 1.0,0.0,0.0),
                        'alt_good_direction':V(-1.0,0.0,0.0),
                        'thickness':box_thickness,
                        'corners':{6:'on', 7:'on'},
                },
                'base':{
                        'points':[
                                V(-steelWidth/2, 0, 0),
                                V(-steelWidth/2, 0, 0) +V(0,traycorner[1] + box_thickness,0),
                                V(steelWidth/2, 0, 0) +V(0,traycorner[1] + box_thickness,0),
                                V(steelWidth/2, 0, 0),
                        ],
                        'x':V(0.0,1.0,0.0),
                        'layer':'base',
                        'thickness':box_thickness,
                        'wood_direction':V( 0.0,0.0,-1.0),
                        'good_direction':V(0,0.0,-1.0),
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

