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
		c=V(-width/2, -height/2)
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
						 '1/8_endmill', auto=True  )))
				t.translate(offsets[s]+pos)
				setattr(self, s, t)
					
class ArbitraryBox(Part):
	""" 
		sides - dict of 'side name' : {'points':[3d point, 3d point, 3d point], 'thickness':thickness}
	"""
	def __init__(faces, *config):
		self.init(config)
		self.faces = faces
		self.sides={}
		self.normals = {}
		self.side_angles={}
		for f, face in faces:
			self.make_sides(f,face['points'])
			self.make_normal(f, face['points'])
		for s, side in self.sides:
			self.find_angle(s, side)

	def make_normal(f, points):
		normal = False
		for p, point in points:
			new_normal = points[(p-1)%len(points)]).cross( (points[(p+1)%len(points)]-point))
			if normal == False:
				normal = new_normal
			elif normal != new_normal:
				raise ValueError( "points in face "+f+" are not in a plane "+str(points) )
		self.faces[f]['normal']=normal
			
	def make_sides(f, points):
		self.faces[f]['sides'] = []
		for p, point in points:
			if (point, points[(p-1)%points.len()]) in self.sides: 
				self.sides[(point, points[(p-1)%points.len()])].append(f)
			else:
				self.sides[(point, points[(p-1)%points.len()])] = [f]
			if ( points[(p-1)%points.len()], point) in self.sides:
				self.sides[(point, points[(p-1)%points.len()])].append(f)
			else:
				self.sides[(point, points[(p-1)%points.len()])] = [f]
			self.faces[f]['sides'].append((point, points[(p-1)%points.len()]))
