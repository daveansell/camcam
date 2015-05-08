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
		faces - dict of 'side name' : {'points':[3d point, 3d point, 3d point], 
						'thickness':thickness
						'x': 3d vector setting x direction in this face
						'origin': 3d point setting origin of face
						'layer': layer part should be in
						'corners': { side_no: 'on' or 'off' } side_no is defined as point 0->1 is side 0 etc. 
                                                        - if undefined will just be made up.
                'tab_lendth' - defaule tab length
                'fudge' - fudge for finger joints

		}
	"""
	def __init__(faces, tab_length, fudge, *config):
		self.init(config)
		self.faces = faces
		self.sides={}
		self.normals = {}
		self.side_angles={}
		for f, face in faces:
			self.make_sides(f,face['points'])
			self.make_normal(f, face['points'])
			self.check_layer(face)
			if 'corners' not in face:
                                self.faces['corners'] = {}
		scount=0
		for s, side in self.sides:
			self.find_angle(s, side)
			self.set_corners(side, f, scount)
			scount+=1
		for f, face in faces:
			if 'x' in face:
				if face['x'].dot(face.normal) !=0:
					raise ValueError('face[x] in face '+str(f)+' not in plane')
			else:  
				face['x'] = face['sides'][0].normalize()
			face['y'] = rotate(face['x'], 90)
			if 'origin' not in face:
				face['origin'] = face['points'][0]
			face.ppoints = []
			for p in face.points:
				face.ppoints.append(V(p.dot(face['x']), p.dot(face['y'])))
			border = Path(closed = True, side = 'out') 
			# DECIDE WHICH SISDE WE ARE CUttng FROM
			# CHECK THE DIRECTION OF THR LOOP
			
			setattr(self, 'face_' + f, self.add(Part(name = f, layer = face['layer'], border = border)))

	def set_corners(side,f,scount):
		face = self.faces[f]
		if side[0]==f:
			(otherf, otherscount) = side[1][0]
		else:
			(otherf, otherscount) = side[0][0]
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

	def make_normal(f, points):
		normal = False
		for p, point in points:
			new_normal = (points[(p-1)%len(points)]-point).normalize().cross( (points[(p+1)%len(points)]-point).normalize())
			if normal == False and normal.length()>0:
				normal = new_normal
			elif normal != new_normal and normal != - new_normal:
				raise ValueError( "points in face "+f+" are not in a plane "+str(points) )
		if 'origin' in self.faces[f]:
			o = self.faces[f]['origin']
			p = points[0]
			p2 = points[1]
			new_normal = (p-o).normalize().cross( (p2-o).normalize())
			if new_normal.length()!=0 and new_normal!=normal and new_normal !=-normal:
				raise ValueError( "origin of face "+f+" are not in a plane "+str(points) )
		self.faces[f]['normal']=normal
			
	def make_sides(f, points):
		self.faces[f]['sides'] = []
		scount =0
		for p, point in points:
			sid = (f, scount)
			if (point, points[(p-1)%points.len()]) in self.sides: 
				self.sides[(point, points[(p-1)%points.len()])].append(sid)
			else:
				self.sides[(point, points[(p-1)%points.len()])] = [sid]
			if ( points[(p-1)%points.len()], point) in self.sides:
				self.sides[(point, points[(p-1)%points.len()])].append(sid)
			else:
				self.sides[(point, points[(p-1)%points.len()])] = [sid]
			self.faces[f]['sides'].append((point, points[(p-1)%points.len()]))
			scount+=1

	def find_angle(s,side):
		if len(side)!=2:
			print "side with only one face"
			return False
		face1 = self.faces[side[0][0]]
		face2 = self.faces[side[1][0]]
		
		# The edge cross the normal gives you a vector that is in the plane and perpendicular to the edge

		svec1 = (face1['points'][side[0][1]+1]-face1['points'][side[0][1]]).cross(face1['normal'])
		svec2 = (face2['points'][side[1][1]+1]-face2['points'][side[1][1]]).cross(face2['normal'])

		# base angle is angle between the two svecs

		baseAngle = math.acos(svec1.normalize().dot(svec2.normalize())) / math.pi *180
		angle = abs(baseAngle -90)

		if baseAngle < 90:
			cutsign = -1
		elif baseAngle > 90:
			cutsign = 1
		else:
			cutsign = 0
		
		# if this is +ve cut on same side as positive normal otherwse opposite direction to normal
		avSvec = (svec1 + svec2)
		cutside1 = avSvec.dot ( face1['normal'] ) * cutsign
		cutside2 = avSvec.dot ( face2['normal'] ) * cutsign

		# Is the normal of both faces in the same directions vs inside and outside 
		# will only break with zero if  if planes are parallel
		t = face1['normal'].dot(avSvec).face2['normal'] 
		if t>0:
			sideSign = 1
		elif t<0:
			sideSign = -1
		else:
			raise ValueError( " Two adjoinig faces are parallel")

#		WHICH SIDE IS THE REFERENCE?			
# 		Which side of the polygon is the wood?		
		
		
