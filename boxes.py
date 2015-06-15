from path import *
from shapes import *
from parts import *

class RoundedBoxEnd(Part):
	def __init__(self,pos, layer, name, width, centre_height, centre_rad, centre_holerad, side_height, bend_rad=0,  sidemodes=False, thickness=6, tab_length=False,  fudge=0, **config):
		self.init(config)
		self.translate(pos)
		if sidemodes==False:
			sidemodes={'right':'off', 'bottom':'off', 'left':'off'}
		if tab_length==False:
			tab_length=20
		self.name=name
		self.layer=layer
		self.add_border(Path(closed=True, side='out'))
		self.centrepos=V(0,0)
		self.border.add_point(self.centrepos+V(-width/2-thickness, side_height-centre_height))
#		self.border.add_point(self.centrepos+V(-width/2-thickness, side_height-centre_height+0.01), radius=bend_rad)
		self.border.add_point(POutcurve(self.centrepos, direction='cw', radius=centre_rad))
#		self.border.add_point(self.centrepos+V(width/2+thickness, side_height-centre_height+0.01), radius=bend_rad)
		self.border.add_point(self.centrepos+V(width/2+thickness, side_height-centre_height))
#		self.border.add_point(self.centrepos+V(width/2+thicknes, side_height-centre_height))
		self.border.add_points(FingerJoint(self.centrepos+V(width/2, side_height-centre_height),
						self.centrepos+V(width/2,-centre_height),
						'left',	
						'external',
						sidemodes['right'],
						sidemodes['right'],
						tab_length, 
						thickness,
						0, 
						fudge))
		self.border.add_points_intersect(FingerJoint(self.centrepos+V(width/2, -centre_height),
						self.centrepos+V(-width/2,-centre_height),
						'left',	
						'external',
						sidemodes['bottom'],
						sidemodes['bottom'],
						tab_length, 
						thickness,
						0, 
						fudge))
		self.border.add_points_intersect(FingerJoint(self.centrepos+V(-width/2, -centre_height),
						self.centrepos+V(-width/2,side_height-centre_height),
						'left',	
						'external',
						sidemodes['right'],
						sidemodes['right'],
						tab_length, 
						thickness,
						0, 
						fudge))
		if centre_holerad>0:
			self.add(Hole(V(0,0), rad=centre_holerad))

class RoundedBox(Part):
	def __init__(self,pos, layers, name, length, width, centre_height, centre_rad, centre_holerad, side_height, bend_rad=0, thickness=6, tab_length=False,  fudge=0, **config):
		self.init(config)
		cutter=False
		self.translate(pos)
		self.end=self.add(RoundedBoxEnd(V(0,0), layers['end'], name+'_end', width, centre_height, centre_rad, centre_holerad, side_height, bend_rad,  {'right':'off', 'bottom':'off', 'left':'off'}, thickness, tab_length,  fudge))
		if 'blank_end' in config:
			self.end2=self.add(RoundedBoxEnd(V(0,0), layers['end2'], name+'_end2', width, centre_height, centre_rad, config['centre_holerad2'], side_height, bend_rad,  {'right':'off', 'bottom':'off', 'left':'off'}, thickness, centre_height+20,  fudge))
			side_modes = {'top':'straight', 'left':'straight'}
			bottom_modes = {'bottom':'straight'}
		elif 'centre_holerad2' in config:
			self.end2=self.add(RoundedBoxEnd(V(0,0), layers['end2'], name+'_end2', width, centre_height, centre_rad, config['centre_holerad2'], side_height, bend_rad,  {'right':'off', 'bottom':'off', 'left':'off'}, thickness, tab_length,  fudge))
			side_modes={'top':'straight'}
			bottom_modes={}
		else:
			self.end.number=2
			side_modes={'top':'straight'}
			bottom_modes={}
		self.side=self.add(Part(name=name+'_side', layer=layers['side'], border=FingerJointBoxSide( V(0,0), length, side_height, 'out', {'left':'on', 'bottom':'off', 'right':'on', 'top':'on'}, side_modes, tab_length, thickness, cutter, auto=True)))
		self.side.number=2
		self.bottom=self.add(Part(name=name+'_bottom', layer=layers['bottom'], border=FingerJointBoxSide( V(0,0), width, length, 'out', {'left':'on', 'bottom':'on', 'right':'on','top':'on'}, bottom_modes, tab_length, thickness, cutter, auto=True,centred=True)))



class Turret(Part):
	def __init__(self, pos, plane, name, turret_type, thickness, fudge, **config):
		self.init(config)
		self.init_turret(pos, plane, name, turret_type, thickness, fudge, config)

	def init_turret(self, pos, plane, name, turret_type, thickness, fudge, config):
		p_layers={'side':'_side', 'end':'end', 'end2':'_end2', 'bottom':'_bottom', 'bearing_ring':'_bearing_ring', 'tube_insert':'_tube_insert', 'tube_insert_in':'_tube_insert_in', 'base':'_base', 'under_base':'_under_base', 'base_protector':'_base_protector'}
		layers = {}
		
		for i, l in p_layers.iteritems():
			plane.add_layer(name+l, material='pvc', thickness=thickness, z0=0)
			layers[i] = name+l
		self.translate(pos)
		plane.add_layer(name+'_end_plate', material='pvc', thickness = 12.3, z0=0)
		data={
			'camera':{'length':85, 'edge_width':10, 'centre_height':60, 'centre_rad':56/2, 'centre_inner_rad':51.3/2, 'centre_holerad':10.2/2, 'side_height':50, 'bend_rad':5, 'tab_length':10, 'piviot_hole_rad':20/2, 'square_hole_side':10},
			'thermal':{'length':85, 'edge_width':10, 'centre_height':60, 'centre_rad':56/2, 'centre_inner_rad':51.3/2, 'centre_holerad':10.2/2, 'side_height':50, 'bend_rad':5, 'tab_length':10, 'piviot_hole_rad':20/2, 'square_hole_side':10},
			'lamp':{'length':50, 'edge_width':10, 'centre_height':35, 'centre_rad':56/2, 'centre_inner_rad':51.3/2, 'centre_holerad':10.2/2, 'side_height':50, 'bend_rad':5, 'tab_length':10, 'piviot_hole_rad':20/2, 'square_hole_side':10},
		}
		assert turret_type in data
		d=data[turret_type]
		self.d = d
		width = math.sqrt(d['centre_rad']**2-(d['centre_height']-d['side_height'])**2)*2
		base_protector_rad=40
		base_rad = math.sqrt((d['length']/2+thickness)**2 + (width/2+thickness)**2)+5
		box=self.add(RoundedBox(V(0,0), layers, name, d['length'], width, d['centre_height'], d['centre_rad'], 0, d['side_height'], d['bend_rad'], thickness, d['tab_length'], fudge, blank_end =True, centre_holerad2=0))
		self.bottom=box.bottom
		self.end=box.end
		# holes for cable clamps inside base
		self.bottom.add(Hole(V(0, -d['length']/2+20), rad=3.3/2))
		self.bottom.add(Hole(V(width/3, -d['length']/2+26), rad=3.3/2))
		self.bottom.add(Hole(V(-width/5, -d['length']/2+20), rad=3.3/2))
		self.bottom.add(Hole(V(-width/4, -width/4), rad=3.3/2))


		# Square for coach bolt
		self.end.add(Rect(V(0,0), centred=True, width=d['square_hole_side'], height=d['square_hole_side'], side='in'))
		self.side=box.side

		self.side.add(Hole(V(6, 8), 4.3/2))
		self.side.add(Hole(V(6, d['side_height']-10), 4.3/2))

		# piviot hole through middle
		self.bottom.add(Hole(V(0,0), rad=d['piviot_hole_rad']), [name+'_bottom', name+'_base', name+'_under_base'])
		self.bottom.add(Hole(V(0,0), rad=d['piviot_hole_rad']+1), ['base', 'perspex', 'paper'])

		# magnet slots
		t=self.bottom.add(Rect(V((base_rad+d['piviot_hole_rad'])/2,0), centred = True, width = base_rad-d['piviot_hole_rad']-10, height = 6, z1 = -6, side='in'), 'base')
		t.rotate(V(0,0),15)
		t=self.bottom.add(Rect(V(-(base_rad+d['piviot_hole_rad'])/2,0), centred = True, width = base_rad-d['piviot_hole_rad']-10, height = 6, z1 = -6, side='in'), 'base')
		t.rotate(V(0,0),15)

		# bearing ring sits inside open end of tube
		self.bearing_ring = self.add(Part(name = name+'_bearing_ring', layer = name+'_bearing_ring', border = Circle(V(0,0), rad=d['centre_inner_rad']-0.2, side='out')))
		for i in range(0,4):
			t=self.bearing_ring.add(Bolt(V(d['centre_inner_rad']*2/3, 0), 'M4', insert_layer=[], clearance_layers=name+'_end2', thread_layer=name+'_bearing_ring'))
			t.rotate(V(0,0), i*90)
		# end plate sits inside the opening end to allow it to be attached
		end_plate_border = Path(side='out', closed=True)
		end_plate_border.add_point(V(-width/2, -d['centre_height'] + d['side_height']-4))
		end_plate_border.add_point(V(-width/2, -d['centre_height']))
		end_plate_border.add_point(V(width/2, -d['centre_height']))
		end_plate_border.add_point(V(width/2, -d['centre_height'] + d['side_height']-4))
		end_plate_border.add_point(PIncurve(V(width/2-d['edge_width'], -d['centre_height'] + d['side_height']-d['edge_width']-4), radius=d['edge_width']))
		end_plate_border.add_point(PIncurve(V(width/2-d['edge_width'], -d['centre_height']+d['edge_width'] ), radius=d['edge_width']))
		end_plate_border.add_point(PIncurve(V(-width/2+d['edge_width'], -d['centre_height']+d['edge_width'] ), radius=d['edge_width']))
		end_plate_border.add_point(PIncurve(V(-width/2+d['edge_width'], -d['centre_height'] + d['side_height']-d['edge_width']-4), radius=d['edge_width']))
		self.end_plate = self.add(Part(name = name+'_end_plate', layer =  name+'_end_plate', border = end_plate_border))
		# Holes to hold end_plate while gluing 
		self.end_plate.add(Bolt(V(width/2-d['edge_width']/2, -d['centre_height'] + d['side_height']-d['edge_width']-16), 'M4', insert_layer=[], clearance_layers=name+'_end_plate', thread_layer=name+'_end2', thread_depth=4))
		self.end_plate.add(Bolt(V(-width/2+d['edge_width']/2, -d['centre_height'] + d['side_height']-d['edge_width']-16), 'M4', insert_layer=[], clearance_layers=name+'_end_plate', thread_layer=name+'_end2', thread_depth=4))

		self.end_plate.add(Bolt(V(width/2-d['edge_width']/2, -d['centre_height'] +d['edge_width']/2), 'M4', insert_layer=[], clearance_layers=name+'_end_plate', thread_layer=name+'_end2', thread_depth=4))
		self.end_plate.add(Bolt(V(-width/2+d['edge_width']/2, -d['centre_height'] +d['edge_width']/2), 'M4', insert_layer=[], clearance_layers=name+'_end_plate', thread_layer=name+'_end2', thread_depth=4))

		# Tube insert is a double layer circle that glues into closed end of tube
		self.tube_insert = self.add(Part(name = name+'_tube_insert', layer= name+'_tube_insert', border = Circle(V(0,0), rad=d['centre_rad']+0.5)))
		self.tube_insert_in = self.add(Part(name = name+'_tube_insert_in', layer= name+'_tube_insert_in', border = Circle(V(0,0), rad=d['centre_inner_rad'])))
		self.tube_insert.add(Hole(V(0,0), rad=d['centre_holerad']), [ name+'_tube_insert',  name+'_tube_insert_in'])

		# under base is a ring under the board to act as bearing on piviot
		self.under_base = self.add(Part(name=name+'_under_base', layer = name+'_under_base', border = Circle(V(0,0), rad=base_rad, side='out')))
		# base sits above board to act as bearing and constrain rotation
		self.base = self.add(Part(name=name+'_base', layer = name+'_base', border = Circle(V(0,0), rad=base_rad, side='out', cutter='1/8_endmill')))
		self.base.add(AngleConstraint(V(0,0), width/2-4, 320, 'M4', name+'_base', name+'_bottom', side='on'))

		# base protector sits on standoffs and has cable cable-tied to it protecting and holding the cable
		self.base_protector = self.add(Part(name=name+'_base_protector', layer = name+'_base_protector', border = Circle(V(0,0), rad=base_protector_rad, side='out')))
		self.base_protector.add(Lines([V(-5, base_protector_rad-12), V(-5, base_protector_rad-8)]))
		self.base_protector.add(Lines([V(5, base_protector_rad-12), V(5, base_protector_rad-8)]))
		self.base_protector.add(Lines([V(-5, base_protector_rad-20), V(-5, base_protector_rad-24)]))
		self.base_protector.add(Lines([V(5, base_protector_rad-20), V(5, base_protector_rad-24)]))
		for i in range(0,6):
			t=self.base.add(Bolt(V(0, base_rad-8), 'M4', clearance_layers=['perspex', 'paper', name+'_base']))
			t.rotate(V(0,0), i*60)
			t=self.under_base.add(Bolt(V(0, base_rad-8), 'M4', clearance_layers=[ name+'_under_base']))
			t.rotate(V(0,0), 30+i*60)
			t=self.base_protector.add(Bolt(V(0, base_protector_rad-7), 'M4', clearance_layers=name+'_base_protector', thread_layer=name+'_under_base', insert_layer=[]))
			self.add_bom('standoff',1, 'M4 standooff MF 30mm', description='30mm standoff')
			t.rotate(V(0,0), 30+i*60)
		self.add_bom('M20 hollow',1,'M20_hollow', description='M20 hollow bolt')
		self.add_bom('M20 wavy washer',1, 'M20_wavy_washer', description='M20 wavy washer')
		self.add_bom('M20 washer',3, 'M20_washer', description='M20 washer')
		self.add_bom('M20 conduit locknut',3,'M20_conduit_locknut', description='M20 condut locknut')
		self.add_bom('20mm thrust bearing',1, '20mm_thrust_bearing', description='20mm thrust bearing')
		self.add_bom(BOM_rod('tube', 'black pvc', 'round tube', d['centre_rad']*2, d['length']-thickness-1, 1, 'Tube to make up-down part of turret should have holes drilled to take camera holder, sometimes camera and cable'))

class PiCamTurret(Turret):
	def __init__(self, pos, plane, name, thickness, fudge, **config):
                self.init(config)
                self.init_turret(pos, plane, name, 'camera', thickness, fudge, config)
		rod_rad = 51.5/2
		cam_yoff = 5.0
		cam_width=25.0
		cam_height=28.0
		cam_hole_from_side=2.0
		cam_hole_from_bottom=9.5
		cam_ribbon_width = 16.0
		cable_slot_depth = 40.0
		cable_slot_height = cam_yoff*2
		cable_slot_width=cam_ribbon_width+8.0
		mount_hole_from_edge = (rod_rad-(cam_height+cam_yoff*2)/2)/2
		window_rad = rod_rad-mount_hole_from_edge-2
		view_rad = window_rad -2
		accel_width = 22
                accel_depth = 17.5
		if 'window_thickness' in config:
			window_thickness = config['window_thickness']
		else:
			window_thickness = 3
		if 'face_thickness' in config:
			face_thickness = config['face_thckness']
		else:
			face_thickness = 6.5

		plane.add_layer(name+'_camera_holder', material='pvc', thickness=thickness, z0=0)
		plane.add_layer(name+'_camera_face', material='pvc', thickness=face_thickness, z0=0)
		plane.add_layer(name+'_camera_window', material='perspex', thickness=window_thickness, z0=0)
		self.camera_face = self.add(Part(name=name+'_camera_face', layer= name+'_camera_face', border = Circle(V(0,0), rad=rod_rad+1)))
		self.camera_face.add(Hole(V(0,0), rad=view_rad))
		self.camera_face.add(Hole(V(0,0), rad=window_rad, z1=-window_thickness))
		self.camera_window = self.add(Part(name=name+'_camera_window', layer= name+'_camera_window', border = Circle(V(0,0), rad=rod_rad+1)))		

		self.camera_holder = self.add(Part(name=name+'_camera_holder', layer= name+'_camera_holder', ignore_border=True))
		if 'cam_depth' in config:
			cam_depth = config['cam_depth']
		else:
			cam_depth = 26.0


		cam_centre= V(0, cam_yoff)
		self.camera_holder.add(Circle(V(0,0), rad=rod_rad), 'paper')
		self.camera_holder.add(Rect(cam_centre, centred=True, width = cam_width+2, height=cam_height+1, z1=-cam_depth-1, partial_fill=cam_width/2-4, cutter='6mm_endmill', side='in'))
		self.camera_holder.add(Rect(cam_centre+V(0,-cam_height/2-cable_slot_height/2), centred=True, width= cable_slot_width, height=cable_slot_height, z1=-cable_slot_depth, cutter='6mm_endmill', rad=3.1, partial_fill=cable_slot_height/2-7, side='in'))
		
		self.camera_holder.add(Drill(cam_centre+V(cam_width/2-cam_hole_from_side, cam_height/2-cam_hole_from_side), z0= -cam_depth-1, z1=-cam_depth-1, rad=1.5/2))
		self.camera_holder.add(Drill(cam_centre+V(-cam_width/2+cam_hole_from_side, cam_height/2-cam_hole_from_side), z0= -cam_depth-1, z1=-cam_depth-1, rad=1.5/2))
		self.camera_holder.add(Drill(cam_centre+V(cam_width/2-cam_hole_from_side, -cam_height/2+cam_hole_from_bottom), z0= -cam_depth-1, z1=-cam_depth-1, rad=1.5/2))
		self.camera_holder.add(Drill(cam_centre+V(-cam_width/2+cam_hole_from_side, -cam_height/2+cam_hole_from_bottom), z0= -cam_depth-1, z1=-cam_depth-1, rad=1.5/2))
		for i in range(0,6):
			t=self.camera_holder.add(Drill(V(0,rod_rad-mount_hole_from_edge), z1=-1, rad=1.5/2))
			t.rotate(V(0,0), i*60)
			t=self.camera_holder.add(Hole(V(0,rod_rad-mount_hole_from_edge),  rad=3.3/2), name+'_camera_face')
			t.rotate(V(0,0), i*60)
		cone_rad = rod_rad - 2*mount_hole_from_edge
		cone_inner_rad = cam_width/2
		cone_depth = cam_depth/2
		rstep = 4
		steps = int(math.ceil((cone_rad-cone_inner_rad)/rstep))
		rstep = (cone_rad-cone_inner_rad)/steps
		dstep = cone_depth / steps
		for i in range(0, steps):
			 self.camera_holder.add(Circle(V(0,0), rad = cone_rad-rstep*i, z1 = -dstep*(i+1), side='in', cutter='6mm_endmill'))
		#               accelerometer
                self.camera_holder.add(RoundedRect(cam_centre, rad=3.1, centred=True, height = accel_width, width=6.5, z0 = -cam_depth, z1=-cam_depth-accel_depth, cutter="6mm_endmill", side='in'))
                self.camera_holder.add(RoundedRect(cam_centre+V(6.5/2,0), tr=V(-6.5/2, -cam_height/2-cable_slot_height/2), z0 = -cam_depth, z1=-cam_depth-6, cutter="6mm_endmill", rad=3.1, side='in'))
		self.add_bom(BOM_rod('rod', 'black pvc', 'round', rod_rad*2, 58, 1, 'rod for camera, should have a bite takenout of the middle of one side of radius the tube, and depth 14mm'))
	
class ThermalTurret(Turret):
        def __init__(self, pos, plane, name, thickness, fudge, **config):
                self.init(config)
                self.init_turret(pos, plane, name, 'thermal', thickness, fudge, config)
                cam_rad=25.0/2
                cam_height=45.0
                cam_lens_depth = 20
                cam_depth=14
                cam_top_to_connector = 2
		cam_front_z = -8
		cam_back_z = cam_front_z - cam_lens_depth
		
                centre_rad=56/2
                centre_inner_rad=51.3/2
                tube_wall = centre_rad-centre_inner_rad

                rod_rad = 51.5/2
                rod_length = 57
                window_holder_thickness = 6.5
                window_holder_rad = rod_rad - 2

                window_rad=28/2
		window_hole_rad = 20/2

                accel_width = 22
                accel_depth = 17.5

	 	if 'window_thickness' in config:
                        window_thickness = config['window_thckness']
                else:
                        window_thickness = 2
                if 'face_thickness' in config:
                        face_thickness = config['face_thckness']
                else:
                        face_thickness = 6.5


                minimum_bite_depth = rod_rad - cam_top_to_connector + tube_wall
                self.comment("Minimum bite depth = "+str(minimum_bite_depth))
                camera_centre = V(0, 0)

                hole_y = math.sqrt((rod_rad-2)**2 - cam_rad**2)
                plane.add_layer(name+'_camera_holder', material='pvc', thickness=50, z0=0)
                plane.add_layer(name+'_window_holder', material='pvc', thickness=window_holder_thickness, z0=0)
                self.camera_holder = self.add(Part(name=name+'_camera_holder', layer= name+'_camera_holder', ignore_border=True))
                self.window_holder = self.add(Part(name=name+'_window_holder', layer= name+'_window_holder', border = Circle(V(0,0), rad=window_holder_rad)))
		
		plane.add_layer(name+'_camera_face', material='pvc', thickness=face_thickness, z0=0)
                self.camera_face = self.add(Part(name=name+'_camera_face', layer= name+'_camera_face', border = Circle(V(0,0), rad=rod_rad+1)))
                self.camera_face.add(Hole(V(0,0), rad=window_hole_rad))

                camera_cutout = Path(closed=True, side='in', partial_fill= cam_rad-4, cutter='6mm_endmill', z1=cam_back_z, )
                camera_cutout.add_point(PSharp(V(-cam_rad, -hole_y/2)))
                camera_cutout.add_point(POutcurve(V(0,0), radius = cam_rad))
                camera_cutout.add_point(PSharp(V(cam_rad, -hole_y/2)))
                camera_cutout.add_point(PIncurve(V(cam_rad, -hole_y), radius=3.5))
                camera_cutout.add_point(PIncurve(V(-cam_rad, -hole_y), radius=3.5))
                self.camera_holder.add(camera_cutout)
                self.camera_holder.add(FilledCircle(V(0,0), rad=window_holder_rad + 0.5, z1 = -window_holder_thickness, cutter="6mm_endmill"))

#               accelerometer
                self.camera_holder.add(RoundedRect(V(0,0), rad=3.1, centred=True, width = accel_width, height=6.5, z0 = cam_back_z, z1=cam_back_z-accel_depth, cutter="6mm_endmill", side='in'))
                self.camera_holder.add(RoundedRect(V(6.5/2,0), tr=V(-6.5/2, -hole_y), z0 = cam_back_z, z1=cam_back_z-6, cutter="6mm_endmill", rad=3.1, side='in'))

                for i in range(-2,3):
                        t=self.camera_holder.add(Hole(V(0, window_holder_rad -3), rad=3.3/2, z1=-12))
                        t.rotate(V(0,0),i*60)
                        t=self.window_holder.add(Hole(V(0, window_holder_rad -3), rad=4.3/2), name+'_camera_face')
                        t.rotate(V(0,0), i*60)
                        t=self.window_holder.add(Hole(V(0, window_holder_rad -3), rad=4.3/2),  name+'_window_holder')
                        t.rotate(V(0,0), i*60)
                self.window_holder.add(Hole(V(0,0), rad=window_rad+0.5, z1=-window_thickness))
                self.window_holder.add(Hole(V(0,0), rad= window_rad-1))
                self.add_bom(BOM_rod('rod', 'black pvc', 'round', rod_rad*2, 58, 1, 'rod for camera, should have a bite takenout of the middle of one side of radius the tube, and depth '+str(minimum_bite_depth)+'mm'))

	
class PlainBox(Part):
	"""pos       - position
	   name      - part base name - the subparts will be called name_back etc
	   layers    - layers if a string everything will be in one layer if a dict of 'top':'top_layer_name' etc they can be different layers
	   width     - width in x 
	   height    - height in y
	   depth     - depth in z 
		     - all internal dimensions
	   thickness - of material

	   cornermodes - dict of ('left', 'top'):'on' (on the 'left part' whree it meets the 'top' part this sets the ends to on the line defining it. the 'top' part where it meets the 'left' part will be set to be the opposite
"""
	def __init__(self, pos, name, layers, width, height, depth, thickness, tab_length, **config):
		self.init(config)
		sides = ['top', 'bottom', 'left', 'right', 'front', 'back']
		conns = { 
			'front':['left', 'top', 'right', 'bottom'],
			'back':['left', 'top', 'right', 'bottom'],
			'top':['left', 'front', 'right', 'back'],
			'bottom':['left', 'front', 'right', 'back'],
			'left':['front', 'bottom', 'back', 'top'],
			'right':['front', 'bottom', 'back', 'top'],  
		}
		dims = {
			'front':[width, height],
			'back':[width, height],
			'top':[width, depth],
			'bottom':[width, depth],
			'left':[ depth, height],
			'right':[depth, height],
		}  
		if 'cornermodes' in config:
			cornermodes = config['cornermodes']
		else:
			cornermodes = {}
		for s1 in sides:
			for s2 in conns[s1]:
				if (s1,s2) in cornermodes:
					if (s2,s1) not in cornermodes:
						if(cornermodes[(s1,s2)]=='on'):
							cornermodes[(s2,s1)]='off'
						else:
							cornermodes[(s2,s1)]='on'
				elif (s2,s1) in cornermodes:
					if cornermodes[(s2,s1)]=='on':
						cornermodes[(s1, s2)]='off'
					else:
						cornermodes[(s1, s2)]='on'
				else:
					cornermodes[(s1,s2)] = 'on' 
					cornermodes[(s2,s1)] = 'off'
		if type(thickness) is dict:
			side_thickness = thickness
		else:
			side_thickness = {} 
			for s in sides:
				side_thickness[s]=thickness
		c=V(0,0)#-width/2, -height/2)
		offsets = {
				'front':V(0,0),
				 'back':V(0,0),
				'top':V(0, height/2+depth/2+side_thickness['top']+side_thickness['front']+10),
				'bottom':V(0, -height/2-depth/2- (side_thickness['bottom']+side_thickness['front']+10)),
				'left':V(-width/2-depth/2-(side_thickness['top']+side_thickness['left']+10),0),
				'right':V(width/2+depth/2+(side_thickness['top']+side_thickness['left']+10),0),
		}
		for s in sides:
			if side_thickness[s]!=0:
				temp=['left', 'top', 'right', 'bottom']
				i=0
				sm={}
				corners={}
				th={}
				for con in conns[s]:
					corners[temp[i]]=cornermodes[(s, con)]	
					if side_thickness[con]==0:
						sm[temp[i]]='straight'
					th[temp[i]]=side_thickness[con]
					i+=1
				if type(layers) is dict:
					l= layers[s]
				else:
					l=layers

				t= self.add(Part(layer=l, name=name+'_'+s, 
					border = FingerJointBoxSide(
						c, 
						dims[s][0], 
						dims[s][1],  
						'in', 
						corners, 
						sm, 
						tab_length, 
						th ,
						 '1/8_endmill', auto=True , centred=True )))
				t.translate(offsets[s])
				setattr(self, s, t)
		self.translate(pos)
					
class ArbitraryBox(Part):
	""" 
		faces - dict of 'side name' : {'points':[3d point, 3d point, 3d point], 
						'thickness':thickness
						'x': 3d vector setting x direction in this face
						'origin': 3d point setting origin of face
						'layer': layer part should be in
						'corners': { side_no: 'on' or 'off' } side_no is defined as point 0->1 is side 0 etc. 
                                                        - if undefined will just be made up.
						'wood_direction': vector - only defined on one face will set which side of the polyhedron the wood is
						'good_direction': vector - direction that is going to be finished well
						'internal' : True/False - is a hole cut into another part should be added to that part
                'tab_lendth' - defaule tab length
                'fudge' - fudge for finger joints

		}
	"""
	def __init__(self, faces, tab_length, fudge, *config):
		self.init(config)
		self.tab_length = tab_length
		self.fudge = fudge
		self.faces = faces
		self.sides={}
		self.normals = {}
		self.side_angles={}
		wood_direction_face = None
		good_direction_face = None
		for f, face in faces.iteritems():
			self.make_sides(f,face['points'])
			self.make_normal(f, face['points'])
#			self.check_layer(face)
			if 'corners' not in face:
                                face['corners'] = {}
			if 'wood_direction' in face:
				if wood_direction_face is not None or wood_direction_face !=None:
					raise ValueError('wood direction defined more than once')
				wood_direction_face = f
			if 'good_direction' in face:
				if good_direction_face is not None or good_direction_face !=None:
					raise ValueError('good direction defined more than once')
				good_direction_face = f
		if wood_direction_face is None:
			raise ValueError("No face with wood_direction set")
		if good_direction_face is None:
			raise ValueError("No face with good_direction set")

		scount=0
		for s, side in self.sides.iteritems():
			self.find_angle(s, side)
			scount+=1
		# on internal faces you define the good direction the wrong way
		if 'internal' in self.faces[good_direction_face] and self.faces[good_direction_face]['internal']:
			self.faces[good_direction_face]['good_direction'] *= -1
		self.propagate_direction('good_direction', good_direction_face,0)
		self.propagate_direction('wood_direction', wood_direction_face,0)

		for f, face in faces.iteritems():
			self.get_cut_side(f, face)
			scount = 0
			for s in face['sides']:
				self.set_corners(self.sides[s], f, scount)
				scount+=1

			if 'x' in face:
				if abs(face['x'].dot(face['normal'])) > 0.0000001 :
					raise ValueError('face[x] in face '+str(f)+' not in plane')
				face['x'] = face['x'].normalize()
			else: 
#				print str(self.tuple_to_vec(face['sides'][0]
				face['x'] = (self.tuple_to_vec(face['sides'][0][1])- self.tuple_to_vec(face['sides'][0][0])).normalize()
			face['y'] = face['x'].cross(face['normal']).normalize()
			# if we are cutting from the back flip x
			if face['good_direction'] == -1:
				 face['x'] = - face['x']


			if 'origin' not in face:
				face['origin'] = face['points'][0]
			face['ppoints'] = []
			for p in face['points']:
				p2 = p-face['origin']
				face['ppoints'].append(V(p2.dot(face['x']), p2.dot(face['y'])))

		# if we are cutting an internal hole then don't make it the part border
			if "layer" not in face:
				raise ValueError( "Face "+f+" does not have a layer") 
			if 'internal' in face and face['internal']:
				border = Path(closed=True, side='in')

			# add points here

				p = Part(name = f, layer = face['layer'])
				self.get_border(p,  f, face, 'internal')
			else:
				p = Part(name = f, layer = face['layer'])
				self.get_border(p,  f, face, 'external')
			# DECIDE WHICH SISDE WE ARE CUttng FROM
			# CHECK THE DIRECTION OF THR LOOP
			
			setattr(self, 'face_' + f, self.add(p))

	def tuple_to_vec(self, t):
		return V(t[0], t[1], t[2])

	def get_border(self, part, f, face, mode):
	 	if mode == 'internal':
                        path = Path(closed=True, side='in')
         	else:
                        path = Path(closed=True, side='out')
		simplepath = Path(closed=True, side='on')

		p=0
		first = True
		lastpoly = False
		simplepoints = []
		if self.find_direction(face['ppoints'])=='cw':
			cutside='left'
		else:
			cutside='right'
         	for point in face['ppoints']:
			lastpoint = face['ppoints'][(p-1)%len(face['sides'])]
			scount = (p)%len(face['sides'])
             		s = face['sides'][scount]
			side = self.sides[s]
			(thisside, otherside) = self.get_side_parts(side, f)
			otherface = self.faces[otherside[0]]
			simplepoints.append(PSharp(point))
              		if len(side)==1:
                		newpoints = [PSharp(point)]
           		else:
#               	 	if mode=='internal':
 #              	            	newpoints = [PSharp(point)]
					
  #             	    	else: 
					angle = thisside[4]
#					print "angle="+str(angle)
#					angle = 15
					if mode == 'internal':
						intfact = -1
						corner = self.other_side_mode(face['corners'][scount])
					else:
						intfact = 1
						corner = face['corners'][scount]
					if angle!=0:
						# this is being cut from the side we are cutting:

						if face['wood_direction'] * face['good_direction']*intfact<0:
							lineside='front'
						else:
							lineside = 'back';
						if thisside[3]*face['good_direction']*intfact<0:
# THIS PUTS THE SLOPE ON THE WRONG PART OF THE JOINT
# create a new mode in finger joints called int and have it behave properly
							newpoints = AngledFingerJoint(lastpoint, point, cutside, mode, corner, corner, self.tab_length, otherface['thickness'], 0, angle, lineside, self.fudge, material_thickness=face['thickness'])
							part.add( AngledFingerJointSlope(lastpoint, point, cutside, mode, corner, corner, self.tab_length, otherface['thickness'], 3.17/2, angle, lineside, self.fudge, material_thickness=face['thickness']))
						else:
							newpoints = AngledFingerJointNoSlope(lastpoint, point, cutside, mode, corner, corner, self.tab_length, otherface['thickness'], 0, angle, lineside, self.fudge, material_thickness=face['thickness'])
					else:
						newpoints = FingerJoint(lastpoint, point, cutside, 'external', corner, corner, self.tab_length, face['thickness'], 0, self.fudge)
			if first or len(newpoints)<2:
				first = False
				path.add_points(newpoints)
			else:
				path.add_points_intersect(newpoints)
			p += 1
		if len(newpoints) >1:
			path.close_intersect()
		simplepath.add_points(simplepoints)
	 #	part.add(simplepath)
		if mode=='internal':
			part.add(path)
		else:
			part.add_border(path)	

	def find_direction(self, points):
		total = 0
		for p,q in enumerate(points):
                        total+=(points[p]-points[(p-1)%len(points)]).normalize().cross((points[(p+1)%len(points)]-points[p]).normalize())
                # if it is a circle
		if total[2] ==0:
			print "side doesn't have a direction"
                elif(total[2]>0):
                        return 'ccw'
                else:
                        return 'cw'


	def get_side_parts(self, side, f):
		if side[0][0]==f:
                                thisside= side[0]
				otherside = side[1]
                else:
                                thisside = side[1]
				otherside = side[0]
		return (thisside, otherside)

	def get_cut_side(self, f, face):
		good_direction = face['wood_direction']
		need_cut_from={}
		pref_cut_from = False
		for s in face['sides']:
			side = self.sides[s]
			if side[0][0]==f:
				thisside= side[0]
			else:
				thisside = side[1]
			cutside = thisside[3]
			if cutside * good_direction>0.0001:
				need_cut_from[self.sign(cutside)]=True
			elif cutside!=0:
				pref_cut_from = cutside
				# this means we should be cutting from this side
		if len(need_cut_from)>1:
			raise ValueError(str(f) + " cannot be cut without cavities as slopes can only be cut from one side ")
		elif len(need_cut_from)>0:
			face['cut_from'] = need_cut_from[need_cut_from.keys()[0]]
		elif type(pref_cut_from) is not False:
			face['cut_from'] = pref_cut_from 
		else:
			face['cut_from'] = 1
	
	def sign(self, val):
		if val>0: 
			return 1
		elif val<0:
			return -1
		else:
			return 0

# t - type of direction - face key
# f - face that has it to start with
	def propagate_direction(self, t, f, recursion):
		face = self.faces[f]
		if recursion==0:
			if face[t].dot(face['normal'])>0:
				face[t]=1
			elif face[t].dot(face['normal'])<0:
				face[t]=-1
			else:
				raise ValueError(t+" is perpendicular to the normal")
		recursion += 1
		for s in face['sides']:
			side = self.sides[s]
			if side[0][0]==f:
				newf = side[1][0]
				d = side[0][2]	
			else:
				newf = side[0][0]
				d = side[1][2]

  			newface = self.faces[newf]
			if t not in newface:
				self.faces[newf][t] = d * face[t]
				self.propagate_direction(t, newf, recursion)

	def set_corners(self, side, f, scount):
		face = self.faces[f]
		if len(side)==0:
			raise ValueError( "Side "+str(side)+" has no values")
		elif len(side) ==1:
			face['corners'][scount] = 'straight'
		else:
			if side[0][0]==f:
				otherf = side[1][0]
				otherscount = side[1][1]
			else:
				otherf = side[0][0]
				otherscount = side[0][1]

			otherface = self.faces[otherf]
			if scount in face['corners']:
				otherface['corners'][otherscount] = self.other_side_mode(face['corners'][scount])
			elif otherscount in otherface['corners']:
				face['corners'][scount] = self.other_side_mode(otherface['corners'][otherscount])
			else:
				face['corners'][scount] = 'off'
				otherface['corners'][otherscount] = 'on'
			
	def other_side_mode(self, mode):
		if mode=='on':
			return 'off'
		else:
			return 'on'

	def make_normal(self, f, points):
		normal = False
		p = 0
		for point in points:
			new_normal = (points[(p-1)%len(points)]-point).normalize().cross( (points[(p+1)%len(points)]-point).normalize())
			if type(normal) is bool and normal == False:
				normal = new_normal
			elif (normal.normalize() - new_normal.normalize()).length() > 0.00001: #and normal.normalize() != - new_normal.normalize():
				raise ValueError( "points in face "+f+" are not in a plane "+str(points) )
			p += 1
		if 'origin' in self.faces[f]:
			o = self.faces[f]['origin']
			p = points[0]
			p2 = points[1]
			new_normal = (p-o).normalize().cross( (p2-o).normalize()).normalize()
			if new_normal.length()>0.000001 and not new_normal.almost(normal) and not new_normal.almost(-normal):
				raise ValueError( "origin of face "+f+" are not in a plane origin="+str(o)+ "  points="+str(points) +" normal="+str(normal) + "new_normal="+str(new_normal) )
		self.faces[f]['normal']=normal
			
	def get_sid(self, p1, p2):
		# if the points are the same to n dp they treat them as the same
		ndp = 3
		r1 = V(round(p1[0],ndp), round(p1[1],ndp), round(p1[2],ndp))
		r2 = V(round(p2[0],ndp), round(p2[1],ndp), round(p2[2],ndp))

		if r1>r2:
			return (r1, r2)
		else:
			return (r2, r1)
	def make_sides(self, f, points):
		self.faces[f]['sides'] = []
		p =0
		for point in points:
			sval = [f, p]
			sid = self.get_sid(point, points[(p-1)%len(points)])
			
			if sid in self.sides: 
				self.sides[sid].append(sval)
			else:
				self.sides[sid] = [sval]
			self.faces[f]['sides'].append(sid)
			p+=1
		if len(self.sides[sid]) > 2:
			raise ValueError("more than 2 faces with the same side "+str(self.sides[sid1]))

	def find_angle(self, s,side):
		if len(side)!=2:
			print "side with only one face"
			return False
		face1 = self.faces[side[0][0]]
		face2 = self.faces[side[1][0]]
		# The edge cross the normal gives you a vector that is in the plane and perpendicular to the edge
		svec1 = (face1['points'][ (side[0][1]-1)%len(face1['points']) ] - face1['points'][side[0][1]]).cross( face1['normal'] ).normalize()

		svec2 = (face2['points'][ (side[1][1]-1)%len(face2['points']) ] - face2['points'][side[1][1]]).cross( face2['normal'] ).normalize()

		# base angle is angle between the two svecs

		baseAngle = math.acos(svec1.normalize().dot(svec2.normalize())) / math.pi *180
		if baseAngle < 45:
			cutsign = -1
			angle = abs(baseAngle)
		elif baseAngle < 90:
			cutsign = -1
			angle = abs(90-baseAngle)
		elif baseAngle==90:
			cutsign = 0
			angle =0
		elif baseAngle <135:
			cutsign = 1
			angle = abs(baseAngle-90)
		else:
			cutsign = 1
                        angle = abs(180-baseAngle)
		
		# if this is +ve cut on same side as positive normal otherwse opposite direction to normal
		avSvec = (svec1 + svec2).normalize()
		

		# Is the normal of both faces in the same directions vs inside and outside 
		# will only break with zero if  if planes are parallel
		t = face1['normal'].dot(avSvec) * avSvec.dot(face2['normal'] )
		if t>0:
			sideSign = 1
		elif t<0:
			sideSign = -1
		else:
			raise ValueError( " Two adjoinig faces are parallel")
		side[0].append(sideSign)
		side[1].append(sideSign)
		side[0].append( avSvec.dot ( face1['normal'] ) * cutsign)
		side[1].append( avSvec.dot ( face2['normal'] ) * cutsign)

		

		side[0].append( angle )
		side[1].append( angle )
