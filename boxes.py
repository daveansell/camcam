from path import *
from shapes import *

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
		self.border.add_point(self.centrepos+V(-width/2-thickness, side_height-centre_height+0.01), radius=bend_rad)
		self.border.add_point(POutcurve(self.centrepos, radius=centre_rad))
		self.border.add_point(self.centrepos+V(width/2+thickness, side_height-centre_height+0.01), radius=bend_rad)
		self.border.add_point(self.centrepos+V(width/2+thickness, side_height-centre_height))
#		self.border.add_point(self.centrepos+V(width/2+thicknes, side_height-centre_height))
		self.border.add_points_intersect(FingerJoint(self.centrepos+V(width/2, side_height-centre_height),
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
		self.border.add_point(self.centrepos+V(-width/2-thickness, side_height-centre_height))
		if centre_holerad>0:
			self.add(Hole(V(0,0), rad=centre_holerad))

class RoundedBox(Part):
	def __init__(self,pos, layers, name, length, width, centre_height, centre_rad, centre_holerad, side_height, bend_rad=0, thickness=6, tab_length=False,  fudge=0, **config):
		self.init(config)
		print "length="+str(length)+" width="+str(width)+" centre_height="+str(centre_height)+" centre_holerad="+str(centre_holerad)+" side_height="+str(side_height)
		cutter=False
		self.translate(pos)
		self.end=self.add(RoundedBoxEnd(V(0,0), layers['end'], name+'_end', width, centre_height, centre_rad, centre_holerad, side_height, bend_rad,  {'right':'off', 'bottom':'off', 'left':'off'}, thickness, tab_length,  fudge))
		if 'centre_holerad2' in config:
			self.end2=self.add(RoundedBoxEnd(V(0,0), layers['end2'], name+'_end2', width, centre_height, centre_rad, config['centre_holerad2'], side_height, bend_rad,  {'right':'off', 'bottom':'off', 'left':'off'}, thickness, tab_length,  fudge))
		else:
			self.end.number=2
		self.side=self.add(Part(name=name+'_side', layer=layers['side'], border=FingerJointBoxSide( V(0,0), length, side_height, 'out', {'left':'on', 'bottom':'off', 'right':'on', 'top':'on'}, {'top':'straight'}, tab_length, thickness, cutter, auto=True)))
		self.side.number=2
		self.bottom=self.add(Part(name=name+'_bottom', layer=layers['bottom'], border=FingerJointBoxSide( V(0,0), width, length, 'out', {'left':'on', 'bottom':'on', 'right':'on','top':'on'}, {}, tab_length, thickness, cutter, auto=True,centred=True)))

class Turret(Part):
	def __init__(self, pos, layers, name, turret_type, thickness, fudge, **config):
		self.init(config)
		data={
			'camera':{'length':60, 'width':51.5, 'centre_height':50, 'centre_rad':51.5/2, 'centre_holerad':10.2/2, 'side_height':50, 'bend_rad':5, 'tab_length':10, 'piviot_hole_rad':20/2},
			'lamp':{'length':50, 'width':51.5, 'centre_height':35, 'centre_rad':51.5/2, 'centre_holerad':10.2/2, 'side_height':50, 'bend_rad':5, 'tab_length':10, 'piviot_hole_rad':20/2},
		}
		assert turret_type in data
		d=data['turret_type']
		box=self.add(RoundedBox(pos, layers, name, d['length'], d['width'], d['centre_height'], d['centre_rad'], d['centre_holerad'], d['side_height'], d['bend_rad'], thickness, d['tab_length'], fudge))
		self.bottom=box.bottom
		self.end=box.end
		self.side=box.side
		self.bottom.add(Hole(V(0,0), rad=d['piviot_hole_rad']))
			
