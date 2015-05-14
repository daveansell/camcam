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
		print "length="+str(length)+" width="+str(width)+" centre_height="+str(centre_height)+" centre_holerad="+str(centre_holerad)+" side_height="+str(side_height)
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
		for p in self.side.border.points:
			print str(p.pos)+" "+str(p.point_type)
		self.side.number=2
		self.bottom=self.add(Part(name=name+'_bottom', layer=layers['bottom'], border=FingerJointBoxSide( V(0,0), width, length, 'out', {'left':'on', 'bottom':'on', 'right':'on','top':'on'}, bottom_modes, tab_length, thickness, cutter, auto=True,centred=True)))



class Turret(Part):
	def __init__(self, pos, plane, name, turret_type, thickness, fudge, **config):
		self.init(config)
		p_layers={'side':'_side', 'end':'end', 'end2':'_end2', 'bottom':'_bottom','end_plate':'_end_plate', 'bearing_ring':'_bearing_ring', 'tube_insert':'_tube_insert', 'tube_insert_in':'_tube_insert_in'}
		layers = {}
		
		for i, l in p_layers.iteritems():
			plane.add_layer(name+l, material='pvc', thickness=thickness, z0=0)
			layers[i] = name+l
		self.translate(pos)
		data={
			'camera':{'length':70, 'edge_width':10, 'centre_height':60, 'centre_rad':56/2, 'centre_inner_rad':51.3/2, 'centre_holerad':10.2/2, 'side_height':50, 'bend_rad':5, 'tab_length':10, 'piviot_hole_rad':20/2, 'square_hole_side':10},
			'lamp':{'length':50, 'edge_width':10, 'centre_height':35, 'centre_rad':56/2, 'centre_inner_rad':51.3/2, 'centre_holerad':10.2/2, 'side_height':50, 'bend_rad':5, 'tab_length':10, 'piviot_hole_rad':20/2, 'square_hole_side':10},
		}
		assert turret_type in data
		d=data[turret_type]
		width = math.sqrt(d['centre_rad']**2-(d['centre_height']-d['side_height'])**2)*2
		box=self.add(RoundedBox(V(0,0), layers, name, d['length'], width, d['centre_height'], d['centre_rad'], 0, d['side_height'], d['bend_rad'], thickness, d['tab_length'], fudge, blank_end =True, centre_holerad2=0))
		self.bottom=box.bottom
		self.end=box.end
		self.end.add(Rect(V(0,0), centred=True, width=d['square_hole_side'], height=d['square_hole_side'], side='in'))
		self.side=box.side
		self.bottom.add(Hole(V(0,0), rad=d['piviot_hole_rad']))
		self.bearing_ring = self.add(Part(name = name+'_bearing_ring', layer = name+'_bearing_ring', border = Circle(V(0,0), rad=d['centre_inner_rad']-0.2, side='out')))
		for i in range(0,4):
			t=self.bearing_ring.add(Bolt(V(d['centre_inner_rad']*2/3, 0), 'M4', insert_layer=[], clearance_layers=name+'_end2', thread_layer=name+'_bearing_ring'))
			t.rotate(V(0,0), i*90)

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
		self.end_plate.add(Bolt(V(width/2-d['edge_width']/2, -d['centre_height'] + d['side_height']-d['edge_width']-4), 'M4', insert_layer=[], thread_layer=name+'_end_plate', clearance_layers=name+'_end2'))
		self.end_plate.add(Bolt(V(-width/2+d['edge_width']/2, -d['centre_height'] + d['side_height']-d['edge_width']-4), 'M4', insert_layer=[], thread_layer=name+'_end_plate', clearance_layers=name+'_end2'))

		self.end_plate.add(Bolt(V(width/2-d['edge_width']/2, -d['centre_height'] +d['edge_width']/2), 'M4', insert_layer=[], thread_layer=name+'_end_plate', clearance_layers=name+'_end2'))
		self.end_plate.add(Bolt(V(-width/2+d['edge_width']/2, -d['centre_height'] +d['edge_width']/2), 'M4', insert_layer=[], thread_layer=name+'_end_plate', clearance_layers=name+'_end2'))

		self.tube_insert = self.add(Part(name = name+'_tube_insert', layer= name+'_tube_insert', border = Circle(V(0,0), rad=d['centre_rad'])))
		self.tube_insert_in = self.add(Part(name = name+'_tube_insert_in', layer= name+'_tube_insert_in', border = Circle(V(0,0), rad=d['centre_inner_rad'])))
		self.tube_insert.add(Hole(V(0,0), rad=d['centre_holerad']), [ name+'_tube_insert',  name+'_tube_insert_in'])

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
		scount=0
		for s, side in self.sides.iteritems():
			self.find_angle(s, side)
			scount+=1
		self.propagate_direction('good_direction', good_direction_face,0)
		self.propagate_direction('wood_direction', wood_direction_face,0)

		for f, face in faces.iteritems():
			self.get_cut_side(f, face)
			scount = 0
			for s in face['sides']:
				self.set_corners(self.sides[s], f, scount)
				scount+=1

			if 'x' in face:
				if face['x'].dot(face['normal']) !=0:
					raise ValueError('face[x] in face '+str(f)+' not in plane')
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
				face['ppoints'].append(V(p.dot(face['x']), p.dot(face['y'])))

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
					if angle!=0:
						# this is being cut from the side we are cutting:
						if mode == 'internal':
							intfact = -1
							corner = self.other_side_mode(face['corners'][scount])
						else:
							intfact = 1
							corner = face['corners'][scount]

						if face['wood_direction'] * face['good_direction']*intfact>0:
							lineside='front'
						else:
							lineside = 'back';
						if thisside[3]*face['good_direction']*intfact>0:
# THIS PUTS THE SLOPE ON THE WRONG PART OF THE JOINT
# create a new mode in finger joints called int and have it behave properly
							newpoints = AngledFingerJoint(lastpoint, point, cutside, mode, corner, corner, self.tab_length, otherface['thickness'], 0, angle, lineside, self.fudge, material_thickness=face['thickness'])
							part.add( AngledFingerJointSlope(lastpoint, point, cutside, mode, corner, corner, self.tab_length, otherface['thickness'], 3.17/2, angle, lineside, self.fudge, material_thickness=face['thickness']))
						else:
							newpoints = AngledFingerJointNoSlope(lastpoint, point, cutside, mode, corner, corner, self.tab_length, otherface['thickness'], 0, angle, lineside, self.fudge, material_thickness=face['thickness'])
					else:
						newpoints = FingerJoint(lastpoint, point, 'right', 'external', corner, corner, self.tab_length, face['thickness'], 0, self.fudge)
			if first or len(newpoints)<2:
				first = False
				path.add_points(newpoints)
			else:
				path.add_points_intersect(newpoints)
			p += 1
		if len(newpoints) >1:
			path.close_intersect()
		simplepath.add_points(simplepoints)
	 	part.add(simplepath)
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
		print f
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
			print cutside * good_direction
				# this means we should be cutting from this side
		print need_cut_from	
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
		print f
		for point in points:
			new_normal = (points[(p-1)%len(points)]-point).normalize().cross( (points[(p+1)%len(points)]-point).normalize())
			print new_normal
			if type(normal) is bool and normal == False:
				normal = new_normal
			elif normal != new_normal and normal != - new_normal:
				raise ValueError( "points in face "+f+" are not in a plane "+str(points) )
			p += 1
		if 'origin' in self.faces[f]:
			o = self.faces[f]['origin']
			p = points[0]
			p2 = points[1]
			new_normal = (p-o).normalize().cross( (p2-o).normalize())
			if new_normal.length()!=0 and not new_normal.almost(normal) and not new_normal.almost(-normal):
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
		print 'baseAngle='+str(baseAngle)
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
