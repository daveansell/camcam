from path import *
# create a rectangular path
class Rect(Path):
	def __init__(self, bl,  **config):
		self.init( config)
		self.cut_square(bl, config)
		"""Cut a rectanngle
		"""+self.otherargs

	def cut_square(self, bl, config):
		self.otherargs+="""
		:param bl: bottom left or centre if centred
		:param tr: top right if not centred
		:param centred: true if you want the rectangle to be centred
		:param cornertype: type of corner points sharp, incurve, outcurve
		:param rad: radius of cornwer curves if you have them"""
		if 'centred' in config and config['centred']:
			if 'width' in config and 'height' in config:
				pos=bl
				bl=pos-V(config['width']/2, config['height']/2)
				tr=pos+V(config['width']/2, config['height']/2)
			else:
				print "Rounded square is centred but no width or height"
		else:	
			if 'tr' in config:
				tr=config['tr']
			else:
				print "Rounded square is not centred but no tr value"
		if 'cornertype' in config:
			ct=config['cornertype']
		else:
			ct='sharp'
		self.closed=True
		if 'rad' not in config or config['rad'] is False:
			rad = 0.01
		else:
			rad = config['rad']
                self.closed=True
                if rad==False:
                        rad = self.cutterrad
		self.comment("Rounded Square")
		self.comment("bl="+str(bl)+" tr="+str(tr)+" rad="+str(rad))
                self.add_point(bl,ct, radius=rad)
                self.add_point(V(bl[0],tr[1],0),ct,radius=rad)
                self.add_point(tr,ct,radius=rad)
                self.add_point(V(tr[0],bl[1],0),ct,radius=rad)

class RoundedRect(Rect):
	def __init__(self, bl,  **config):
		self.init(config)
		config['cornertype']='incurve'
		self.cut_square(bl,config)
		"""Cut a rectangle with incurve corners
		"""+self.otherargs

class ClearRect(Rect):
	def __init__(self, bl,  **config):
		self.init(config)
		if 'side' in config and config['side'] in ['in', 'out']:
			config['cornertype']='sharp'
		else:
			config['cornertype']='clear'
		self.cut_square(bl,config)
		"""Cut a rectangle with sharp or clear corners depending on the side you are cutting
		"""+self.otherargs
	def pre_render(config):
		if 'side' in config and config['side']=='in':
			config['cornertype']='clear'
		self.points=[]	
		
class Polygon(Path):
	def __init__(self, pos, rad, sides, cornertype='sharp', cornerrad=False, **config):
		self.init( config)
		"""Cut a regular polygon with radius to the points :param rad: centred at :param pos:, with :param sides: sides with corners of type :param cornertype:\n"""+self.otherargs
                self.closed=True
		step=360/sides
		for i in range(0,int(sides)):
			self.add_point(pos+V(rad,0),cornertype,cornerrad,transform={'rotate':[pos,i*step]})
		self.comment("Polygon")
		self.comment("pos="+str(pos)+" rad="+str(rad)+" sides="+str(sides)+" cornertype="+cornertype)

class CountersinkHole(Pathgroup):
	def __init__(pos, holerad, countersinkrad,  **config):
		if 'cutter' in config:
			cutter=config['cutter']
		else:
			cutter='countersink'
			config['cutter']='countersink'
		self.init(config)
		"""Countersink an existing hole of radius :param holeRad: at :param pos: to a radius of :param countersinkrad: 
if :param cutter: is not explicitly specified it will use the countersink cutter\n"""+self.otherargs
		if cutter in milling.tools:
			cutterconfig=milling.tools[self.cutter]
			if 'min_diameter' in cutterconfig:
				if holerad<=cutterconfig['min_diameter']/2:
					self.add_path(Drill(pos,  z1=countersinkrad))
				# if the requesed countersink is too big, we will have to chop it into chunks
				elif countersinkrad-holerad>(cutterconfig['diameter']/2-cutter_config['min_rad'])*0.7:
					steps = math.ceil(float(countersinkrad-holerad)/((cutterconfig['diameter']/2-cutter_config['min_rad'])*0.7))
					step  = (countersinkrad-holerad)/steps
					for i in reversed(range(0,steps)):
						self.add_path(Circle(pos, rad=countersinkrad-(cutterconfig['diameter']/2-cutter_config['min_rad'])*0.7-step*i, z1=-(cutterconfig['diameter']/2-cutter_config['min_rad'])*0.7-step*i,cutter=cutter))
				else:
					self.add_path(Circle(pos, rad=holerad-cutter_config['min_rad'], z1=countersinkrad-holerad+cutter_config['min_rad'])),
		
		self.comment("CountersinkHole")
		self.comment("pos="+str(pos)+" holerad="+str(holerad)+" countersinkrad="+str(countersinkrad))
				
				

# create a circular path
class Circle(Path):
	def __init__(self, pos, rad, **config):
		self.init( config)
		"""Cut a circle centre at :param pos: with radius :param rad:"""+self.otherargs
		if rad==0:
			print "circle of zero radius"
			raise
		else:	
			self.closed=True
			self.add_point(pos,'circle',rad)
			self.comment("Circle")
			self.comment("pos="+str(pos)+" rad="+str(rad))

class RoundSpeakerGrill(Pathgroup):
	def __init__(self,pos, rad, holerad, spacing, **config):
		self.init(config)
		"""Cut a circular grid with radius :param rad: of holes with radius :param holerad: and :param spacing:"""+self.otherargs
		yspacing=spacing*math.cos(math.pi/6)
		numholesx = int(math.ceil(rad/spacing)+1)
		numholesy = int(math.ceil(rad/yspacing))
		for x in range(-numholesx,numholesx):
			for y in range(-numholesy,numholesy):
				if y%2:
					p=V(x*spacing, y*yspacing)
				else:
					p=V((x+0.5)*spacing, y*yspacing)
				if p.length()<rad-holerad:
					self.add_path(Hole(pos+p, rad=holerad))


class FilledCircle(Pathgroup):

	def __init__(self, pos, rad, **config):
		self.init(config)
		self.rad=rad
		self.pos=pos
#		sides=int(max(8, rad))
		
#		self.add_path(Polygon(pos, rad, sides, partial_fill=rad-0.5, fill_direction='in', side='in'))
		self.circle=self.add_path(Circle(pos, rad, side='in'))
	def __render__(self,config): 
		c=self.circle.generate_config(config)
                self.paths=[]
		r=self.rad-c['cutterrad']
		steps=math.ceil(r/c['cutterrad']/1.2)
		step=r/steps
		for i in range(0,int(steps)+1):
			print str(self.rad)+" "+str(self.rad-(steps-i)*step)+" "+str(i)
			self.add_path(Circle(self.pos, self.rad-(steps-i)*step, side='in'))
class Chamfer(Pathgroup):
	def __init__(self, path, chamfer_side, **config):
		if 'chamfer_depth' not in config:
			self.chamfer_depth=False
		else:
			self.chamfer_depth=config['chamfer_depth']
		if 'chamfer_angle' not in config:
                        self.chamfer_angle=None
                else:
                        self.chamfer_depth=config['chamfer_angle']
		if 'chamfer_ref' not in config:
			self.chamfer_ref='top'
		elif config['chamfer_ref'] in ['top', 'bottom']:
			self.chamfer_ref=config['chamfer_ref']
		else:
			raise('Chamfer: chamfer_ref should be top or bottom')
		if 'chamfer_offset' in config:
                        self.chamfer_offset=config['chamfer_offset']
                else:
                        self.chamfer_offset=0

		self.chamfer_side=chamfer_side
		self.init(config)
		self.chamfer_path=path
#		self.add_path(path)
		
	def __render__(self,config):
		c=self.chamfer_path.generate_config(config)
		self.paths=[]
		if hasattr(self, 'cutter') and self.cutter is not None:
			cutter=self.cutter
		elif 'cutter' in c and c['cutter'] is not None:
			cutter=c.cutter
		else: 
			print "No cutter"
			cutter=None
		if self.chamfer_angle==None:
			if c['cutter'] and 'angle' in milling.tools[c['cutter']]:
				self.chamfer_angle= milling.tools[c['cutter']]['angle']
		if 'cutterrad' in c and c['cutterrad']:
			cutterrad=c['cutterrad']
		elif cutter is not None:
			cutterrad=milling.tools[cutter]['diameter']/2
		if 'z0' not in c or c['z0']==None:
			z0=0
		else:
			z0=c['z0']
		if 'z1' not in c or c['z1']==None:
			if 'thickness' in c:
	                        z1=-c['thickness']-0.5
			else:
				print "CHamfer: z1 not definined and no thickness"
				z1=z0
                else:
                        z1=c['z1']
		if self.chamfer_angle==None:
			if 'angle' in milling.tools[cutter]:
				self.chamfer_angle=milling.tools[cutter]['angle']
			else:
				self.chamfer_angle=45
				print "Chamfer angel is not set so assuming 45"

		if self.chamfer_depth==False or self.chamfer_depth==None:
			zdiff= z1-z0
		else:
		 	zdiff=-self.chamfer_depth-z0
		xdiff= zdiff*math.tan(float(self.chamfer_angle)/180*math.pi)
		if c['stepdown'] is not None:
			stepdown=c['stepdown']
		elif 'material' in c and milling.materials[c['material']]:
			stepdown = milling.materials[c['material']]['stepdown']
		steps=max( math.ceil(abs(float(zdiff)/stepdown)), math.ceil(abs(float(xdiff)/cutterrad*0.8)) )
		zstep=zdiff/steps
		xstep=xdiff/steps
		xoffset=self.chamfer_offset/zdiff*xdiff
		if self.chamfer_ref=='bottom':
			startpath=copy.copy(self.chamfer_path.offset_path(side=self.chamfer_side, distance=xdiff, config=c))
		else:
			startpath=copy.copy(self.chamfer_path)
		for i in range(1, int(steps+1)):
			tc=copy.copy(c)
			startpath.z0=0#(i-1)*-zstep
			startpath.z1=i*zstep
#			tc['partial_fill']=xstep*(steps-i)-0.1
#			tc['fill_direction']=self.chamfer_path.otherDir(self.chamfer_side)
			temp=startpath.offset_path(side=self.chamfer_side, distance=abs(xstep*(i))+abs(xoffset), config=tc)
#			print temp
#			print callable(self.add_path)
			self.add_path(temp)
class DoubleFlat(Path):
	def __init__(self, pos, rad, flat_rad, **config):
		"""Cut a circle with two flats, centred at :param pos: with radius :param rad: and :param flat_rad: is half the distance between the flats"""
		self.init(config)
		self.closed=True
		y=math.sqrt(rad**2 - flat_rad**2)
		self.add_point(pos+V(flat_rad, y), direction='ccw', point_type='arcend')
		self.add_point(pos, radius=rad, point_type='arc')
		self.add_point(pos+V(-flat_rad,y), point_type='arcend')
		self.add_point(pos+V(-flat_rad,-y), point_type='arcend')
		self.add_point(pos, radius=rad, direction='ccw', point_type='arc')
		self.add_point(pos+V(flat_rad, -y), point_type='arcend')

class Cross(Pathgroup):
	def __init__(self, pos, rad, **config):
		self.init(config)
		"""Cut a cross with radius :param rad: at :param pos: oriented NS EW"""+self.otherargs
		a=self.add_path(Path(closed=False,**config))
		b=self.add_path(Path(closed=False,**config))
		a.add_point(V(pos[0]+rad, pos[1]))
		a.add_point(V(pos[0]-rad, pos[1]))
		b.add_point(V(pos[0], pos[1]+rad))
		b.add_point(V(pos[0], pos[1]-rad))
		self.comment("Cross")
		self.comment("pos="+str(pos)+" rad="+str(rad))
		
class RepeatLine(Part):
	def __init__(self, start, end, number, ob, args, **config):
                self.init(config)
		if 'layers' in config:
			layers=config['layers']
		else:
			layers=False
		"""Repeat :param number: objects of type :param ob: in a line from :param start: to :param end:"""+self.otherargs
                step=(end-start)/(number-1)
                for i in range(0,number):
                	t=self.add_path(ob(start+step*i, **args),layers).paths
			if 'pibarn' in t:
				print t['base']
				print t['base'].paths
				print t['base'].paths[0].paths
		self.comment("RepeatLine")
		self.comment("start="+str(start)+" end="+str(end)+" number="+str(number))

class RepeatSpacedGrid(Part):
	def __init__(self, start, dx, dy, numberx, numbery, ob, args,layers, **config):
                self.init(config)
		"""Repeat objects of type :param ob: in a grid this can be rectangular if :param dx: and :param dy: are perpendicular or skewed if the are not
:param start: - position grid is started at
:param dx: - the step between objects in one direction
:param dy: - the step in the other direction
:param numberx: - the number of objects in x direction
:param numbery: - the number of objects in y direction
:param ob: - the object type
:param args: - arguments to initialise ob (dict)
:param centred: - the grid is centred rather than starting at a corner
"""+self.otherargs
		numberx = int(numberx)
		numbery = int(numbery)
		if 'centred' in config and config['centred'] is True:
			start= start -((dx*(numberx-1))/2+dy*(numbery-1)/2)
                for i in range(0,numberx):
			for j in range(0,numbery):
                        	self.add_path(ob(start+dx*i+dy*j, **args),layers)
		self.comment("RepeatSpacedGrid")
		self.comment("start="+str(start)+" dx="+str(dx)+" dy="+str(dy)+" numberx"+str(numberx)+" numbery"+str(numbery))

class Hole(Pathgroup):
	def __init__(self, pos, rad, **config):
		self.init(config)
		"""Cut a hole at :param pos: with radius :param rad:
:param rad: can be a list as can :param z1:"""+self.otherargs
		if 'side' not in config:
			config['side']='in'
		if type(rad) is list:
			for i,r in enumerate(rad):
				if type(config['z1']) is list:
					c=copy.copy(config)
					if i <= len(config['z1']):
						c['z1']=config['z1'][i]
						self.add_path(Circle(pos, rad[i],  **c))
					else:
						c['z1']=config['z1'][len(config['z1'])]
						self.add_path(Circle(pos, rad[i],  **c))
				else:
					self.add_path(Circle(pos, rad[i], **config))
		else:
			if 'z1' in config and type(config['z1']) is list:
				print "z1 should only be a list if rad is also  a list "+str(config['z1'])
			self.add_path(Circle(pos, rad, **config))
		self.comment("Hole")
		self.comment("pos="+str(pos)+" rad="+str(rad))

class HoleLine(Pathgroup):
	def __init__(self, start, end, number, rad, **config):
		self.init(config)
		step=(end-start)/(number-1)
		for i in range(0,number-1):
			self.add_path(Hole(start+step*i, rad, 'in'))
		self.comment("HoleLine")
		self.comment("start="+str(start)+" end="+str(end)+" number="+str(number)+" rad="+str(rad))

class Screw(Part):
	def __init__(self,pos, **config):
		self.init(config)
		if 'layer_config' in config:
			layer_conf=config['layer_config']
			for c in layer_conf.keys():
				conf = copy.deepcopy(layer_conf[c])
				self.add_path(Hole(pos, **conf), c)
class FourScrews(Part):
	def __init__(self, bl, tr, layer_conf, **config):
		self.init(config)
		d=tr-bl
		self.add_path(Screw(bl, layer_config=layer_conf, **config))
		self.add_path(Screw(bl+V(d[0], 0), layer_config=layer_conf, **config))
		self.add_path(Screw(bl+V(0, d[1]), layer_config=layer_conf, **config))
		self.add_path(Screw(tr, layer_config=layer_conf, **config))

class Bolt(Part):
	def __init__(self,pos,thread='M4',head='button', length=10, **config):
		self.init(config)
		self.add_bom("Machine screw", 1, str(length)+"mm "+str(thread)+" "+str(head),'')
		if 'insert_layer' in config:
			insert_layer = config['insert_layer']
		else:
			insert_layer = 'base'
		if 'clearance_layers' in config:
			clearance_layers = config['clearance_layers']
		else:
			clearance_layers = 'perspex'
		if 'head_layer' in config:
			head_layer = config['head_layer']
		else:
			head_layer = 'top'
		if thread in milling.bolts:
			if 'insert_type' in config and config['insert_type'] in milling.inserts[thread]:
				insert=milling.inserts[thread][config['insert_type']]
			else:
				insert=milling.inserts[thread]
			self.add_bom("Wood insert", 1, str(thread)+"insert",'')
			for i,diam in enumerate(insert['diams']):
				self.add_path(Hole(pos, insert['diams'][i],  side='in' , z1=insert['depths'][i]),insert_layer)

			self.add_path(Hole(pos, (milling.bolts[thread]['clearance']+0.5)/2, side='in'),clearance_layers)
			if(head=='countersunk'):
				self.add_path(Countersink(pos, milling.bolts[thread]['clearance'], milling.bolts[thread]['countersunk']['diam']/2, config),head_layer)
			else:
				self.add_path(Hole(pos, milling.bolts[thread]['clearance']/2, side='in'),head_layer)
			self.add_path(Hole(pos, milling.bolts[thread]['tap'], side='in'),'back')

class FingerJointMid(Pathgroup):
	def __init__(self, start, end, side,linemode, startmode, endmode, tab_length, thickness, cutterrad, prevmode, nextmode, **config):
		"""Produce points for a finger joint cut on :param side: of a line from :param start: to :param end:
The line defines the 
:param linemode: 'internal' - for a joint that is in a hole in a piece of wood 'external' is a side of a box
:param start: Point to start reference line
:param end: Point to end reference line
:param side: side to cut into wood of the reference line
:param startmode: start 'on' or 'off' the reference line
:param endmode: end 'on' or 'off' the reference line
:param tab_length: approximate tab length
:param thickness: thickness of the material
:param cutterrad: radius of the cutter you are using
:param fudge: a fudge factor that increases the gap along the finger joint when negative - it should be 1/4 of the gap you want\n"""
		self.init( config)
		if 'fudge' in config:
			fudge=config['fudge']
		else:
			fudge=0
		num_tab_pairs= math.floor((end-start).length()/tab_length/2)
		if startmode==endmode:
			num_tabs = num_tab_pairs*2+1
		else:
			num_tabs = num_tab_pairs*2
		tab_length = (end-start).length()/num_tabs
		if side=='left':
			perp = rotate((end-start).normalize(),-90)
		else:
			perp = rotate((end-start).normalize(),90)
		parallel=(end-start).normalize( )
		along=parallel*tab_length
		cra=(end-start).normalize()*(cutterrad+fudge)
		crp=perp*cutterrad
		cutin=perp*thickness
		if startmode=='on':
			# cut a bit extra on first tab if the previous tab was off as well
			if prevmode=='on':
				self.add_path(ClearRect(bl=start-parallel*thickness+cra+crp, tr=start+along+cutin-cra-crp, direction='cw'))
			else:
				self.add_path(ClearRect(bl=start-parallel+cra+crp, tr=start+along+cutin-cra-crp, direction='cw'))
			m='off'
		else:
			m='on'
		for i in range(1,int(num_tabs)):
			if m=='on':
				# cut a bit extra on first tab if the next tab was off as well
				if i==num_tabs and nextmode=='off':
					self.add_path(ClearRect(bl=start+along*i+cra+crp, tr=start+along*(i+1)+cutin-cra-crp+parallel*thickness, direction='cw'))
				else:
					self.add_path(ClearRect(bl=start+along*i+cra+crp, tr=start+along*(i+1)+cutin-cra-crp, direction='cw'))
				
				m='off'
			else:
				m='on'
		self.comment("FingerJointMid")

class FingerJointBoxMidSide(Pathgroup):
	def __init__(self, pos, width, height, corners, sidemodes, tab_length, thickness, cutter,**config):
		config['direction']='ccw'
		self.init(config)
		if 'centred' in config:
			pos=pos - V(width, height)/2
		self.closed=True
		s='left'
		if sidemodes==True:
			sidemodes={'left':True, 'top':True, 'right':True, 'bottom':True}
		linemode='internal'
		cutterrad = milling.tools[cutter]['diameter']/2
		if 'fudge' in config:
			fudge=config['fudge']
		else:
			fudge=0
		if sidemodes['left']:
			self.add_path(FingerJointMid(start=pos+V(0,0), end=pos+V(0,height), side=s, linemode=linemode, startmode=corners['left'], endmode=corners['left'], tab_length=tab_length, thickness=thickness, cutterrad=cutterrad, prevmode=corners['bottom'], nextmode=corners['top'], fudge=fudge))
		if sidemodes['top']:
			self.add_path(FingerJointMid(start=pos+V(0,height), end=pos+V(width,height), side=s, linemode=linemode, startmode=corners['top'], endmode=corners['top'], tab_length=tab_length, thickness=thickness, cutterrad=cutterrad, prevmode=corners['left'], nextmode=corners['right'], fudge=fudge))
		if sidemodes['right']:
			self.add_path(FingerJointMid(start=pos+V(width, height), end=pos+V(width,0), side=s, linemode=linemode, startmode=corners['right'], endmode=corners['right'], tab_length=tab_length, thickness=thickness, cutterrad=cutterrad, prevmode=corners['top'], nextmode=corners['bottom'], fudge=fudge))
		if sidemodes['bottom']:
			self.add_path(FingerJointMid(start=pos+V(width,0), end=pos+V(0,0), side=s, linemode=linemode, startmode=corners['bottom'], endmode=corners['bottom'], tab_length=tab_length, thickness=thickness, cutterrad=cutterrad, prevmode=corners['right'], nextmode=corners['left'], fudge=fudge))
		self.comment("FingerJointBoxMidSide")



class FingerJoint(list):
	def __init__(self, start, end, side,linemode, startmode, endmode, tab_length, thickness, cutterrad, fudge=0):
		"""Produce points for a finger joint cut on :param side: of a line from :param start: to :param end:
The line defines the 
:param linemode: 'internal' - for a joint that is in a hole in a piece of wood 'external' is a side of a box
:param start: Point to start reference line
:param end: Point to end reference line
:param side: side to cut into wood of the reference line
:param startmode: start 'on' or 'off' the reference line
:param endmode: end 'on' or 'off' the reference line
:param tab_length: approximate tab length
:param thickness: thickness of the material
:param cutterrad: radius of the cutter you are using
:param fudge: a fudge factor that increases the gap along the finger joint when negative - it should be 1/4 of the gap you want\n"""
		num_tab_pairs= math.floor((end-start).length()/tab_length/2)
		if startmode==endmode:
			num_tabs = num_tab_pairs*2+1
		else:
			num_tabs = num_tab_pairs*2
		tab_length = (end-start).length()/num_tabs
		if side=='left':
			perp = rotate((end-start).normalize(),-90)
		else:
			perp = rotate((end-start).normalize(),90)
		along=tab_length*(end-start).normalize()
		cra=(end-start).normalize()*(cutterrad+fudge)
		crp=perp*cutterrad
		cutin=perp*thickness
		if linemode=='external':
			onpointmode='clear'
			offpointmode='sharp'
		if linemode=='internal':
			onpointmode='sharp'
			offpointmode='clear'
			cra=-cra
			crp=-crp
		if startmode=='on':
			self.append(Point(start+crp-cra, onpointmode))
			m='on'
		elif startmode=='off':
			self.append(Point(start+cutin+crp-cra, offpointmode))
			m='off'
		for i in range(1,int(num_tabs)):
			if m=='on':
				self.append(Point(start+along*i-cra+crp,  onpointmode))
			#	if(i!=num_tabs):
				self.append(Point(start+along*i+crp-cra+cutin, offpointmode))
				m='off'
			else:
				self.append(Point(start+along*i+crp+cra+cutin,offpointmode))
				self.append(Point(start+along*i+crp+cra,onpointmode))
				m='on'
		if endmode=='on':
			self.append(Point(end+crp+cra, onpointmode))
		elif endmode=='off':
			self.append(Point(end+cutin+crp+cra, offpointmode))

class FingerJointBoxSide(Path):
	def __init__(self, pos, width, height, side, corners, sidemodes, tab_length, thickness, cutter,**config):
	#	config['side']='on'
		self.init(config)
		self.closed=True
		self.side='on'
		if 'fudge' in config:
			fudge=config['fudge']
		else:
			fudge=0
		if 'centred' in config and config['centred'] is True:
			pos-=V(width/2, height/2)
		if side=='in':
			s='left'
			linemode='external'
		else:
			s='left'
			linemode='internal'
		if type(thickness) is not dict:
			thickness={'left':thickness, 'top':thickness, 'right':thickness, 'bottom':thickness}

		c={}			
		cutterrad = milling.tools[cutter]['diameter']/2
		for k in thickness.keys():
			if k in corners and corners[k]=='on':
				c[k] = cutterrad
			else:
				c[k] = cutterrad+thickness[k]

		if 'left' in sidemodes and sidemodes['left']=='straight':
			self.add_point(pos+V(-c['left'],height+c['top']))
		else:
			if corners['left']=='off' and corners['bottom']=='off':
				self.add_point(pos+V(-thickness['left']-cutterrad, -thickness['bottom']-cutterrad),'sharp')
			self.add_points(FingerJoint(start=pos+V(0,0), end=pos+V(0,height), side=s, linemode=linemode, startmode=corners['left'], endmode=corners['left'], tab_length=tab_length, thickness=thickness['left'], cutterrad=cutterrad, fudge=fudge))
		if 'top' in sidemodes and sidemodes['top']=='straight':
			self.add_point(pos+V(width+c['right'],height+c['top']))
		else:
			if corners['left']=='off' and corners['top']=='off':
				self.add_point(pos+V(-thickness['left']-cutterrad, height+thickness['top']+cutterrad),'sharp')
			self.add_points(FingerJoint(start=pos+V(0,height), end=pos+V(width,height), side=s, linemode=linemode,startmode=corners['top'], endmode=corners['top'], tab_length=tab_length, thickness=thickness['top'], cutterrad=cutterrad, fudge=fudge))
		if 'right' in sidemodes and sidemodes['right']=='straight':
			self.add_point(pos+V(width+c['right'],-c['bottom']))
		else:
			if corners['top']=='off' and corners['right']=='off':
				self.add_point(pos+V(width+thickness['right']+cutterrad, height+thickness['top']+cutterrad),'sharp')
			self.add_points(FingerJoint(start=pos+V(width,height), end=pos+V(width,0), side=s, linemode=linemode, startmode=corners['right'], endmode=corners['right'], tab_length=tab_length, thickness=thickness['right'], cutterrad=cutterrad, fudge=fudge))
		if 'bottom' in sidemodes and sidemodes['bottom']=='straight':
			
			self.add_point(pos+V(-c['bottom'],-c['left']))
		else:
			if corners['right']=='off' and corners['bottom']=='off':
				self.add_point(pos+V(width+thickness['right']+cutterrad, -thickness['bottom']-cutterrad),'sharp')
			self.add_points(FingerJoint(start=pos+V(width,0), end=pos+V(0,0), side=s, linemode=linemode, startmode=corners['bottom'], endmode=corners['bottom'], tab_length=tab_length, thickness=thickness['bottom'], cutterrad=cutterrad, fudge=fudge))
		self.comment("FingerJointBoxSide")



class Module(Plane):
	def __init__(self, size,  **config):#holesX=False, holesY=False, fromedge=15, fromends=40):
		"""Create a module
:param size: A1, A2, A3
:param fromedge: distance holdowns should be from edge of board
:param orientation: portrait, landscape
:param fromends: distance holdowns from ends
:param holesY: number of holes in Y direction
:param holesX: number of holes in X direction
:param base_thicknesss: thickenss of base layer
:param insert_type:  the type of insert - default screw in, or hammer
:param no_perspex: if rue don't create perspex layer
:param no_holdowns: if True no holdowns
"""
		self.init('module',V(0,0),V(0,0),config)
		self.bom=[]
		bolt_config={}
		if('fromends' in config):
			fromends=config['fromemds']
		else:
			fromends=40
		if('fromedge' in config):
			fromedge=config['fromedge']
		else:
			fromedge=16
		if('holesY' in config):
			holesY=config['holesX']
		else:
			holesY=False
		if('holesX' in config):
			holesX=config['holesX']
		else:
			holesX=False
		if 'base_thickness' in config:
			base_thickness=config['base_thickness']
		else:
			base_thickness=12
		if 'perspex_thickness' in config:
			perspex_thickness=config['perspex_thickness']
			if perspex_thickness>3:
				bolt_config['length']=16
		else:
			perspex_thickness=12
		if 'insert_type' in config:
			bolt_config['insert_type']=config['insert_type']
		#name, material, thickness, z0=0,zoffset=0
		self.perspex_layer=self.add_layer('perspex',material='perspex',thickness=perspex_thickness,z0=0,zoffset=3)
		self.base_layer=self.add_layer('base',material='plywood', thickness=base_thickness, z0=0,zoffset=0, add_back=True)
		self.pibarn_layer=self.add_layer('pibarn',material='perspex', thickness=6, z0=0,zoffset=30, add_back=False)
#		self.add_layer('paper',material='paper',thickness=0.05,z0=0,zoffset=0.05)
		radius=30
		if 'orientation' in config and config['orientation'] in ['landscape', 'portrait']:
			orientation=config['orientation']
		else:
			orientation='landscape'
		if size=='A3':
			width=420
			height=297
			if holesX==False:
				holesX=4
			if holesY==False:
				holesY=3
		elif size=='A2':
			width=594
			height=420
			if holesX==False:
				holesX=4
			if holesY==False:
				holesY=3
		elif size=='A1':
			width=841
			height=594
			if holesX==False:
				holesX=4
			if holesY==False:
				holesY=4
		if orientation!='landscape':
			width,height = height,width
			holesX, holesY = holesY, holesX

		edge= RoundedRect(bl=V(0,0), tr=V(width, height), rad=radius, side='out')
		if not ('no_perspex' in config and not config['no_perspex']):
			self.perspex = self.add_path(Part(name='perspex', border=edge, layer='perspex',colour="red"))
		self.base = self.add_path(Part(name='base', border=edge, layer='base'))
#		self.paper = self.add_path(Part(name='paper', border=edge, layer='paper'))

		
		self.add_path(Hole(V(radius,radius),rad=13/2,side='in'),['base','perspex','paper'])
		self.add_path(Hole(V(width-radius,radius),rad=13/2,side='in'),['base','perspex','paper'])
		self.add_path(Hole(V(width-radius,height-radius),rad=13/2,side='in'),['base','perspex','paper'])
		self.add_path(Hole(V(radius,height-radius),rad=13/2,side='in'),['base','perspex','paper'])
		if size=='A1':
			if orientation=='landscape':
				self.add_path(Hole(V(width/2,radius),rad=13/2,side='in'),['base','perspex','paper'])
		                self.add_path(Hole(V(width/2,height-radius),rad=13/2,side='in'),['base','perspex','paper'])
			else:
				self.add_path(Hole(V(radius,height/2),rad=13/2,side='in'),['base','perspex','paper'])
                                self.add_path(Hole(V(width-radius,height/2),rad=13/2,side='in'),['base','perspex','paper'])

		if not ('no_holdown' in config and  config['no_holdown']):
			self.add_path(RepeatLine(V(fromends, fromedge), V(width-fromends,fromedge), holesX, Bolt, bolt_config,layers=['base','perspex','paper']))
			self.add_path(RepeatLine(V(width-fromedge, fromends), V(width-fromedge,height-fromends), holesY, Bolt, bolt_config,layers=['base','perspex','paper']))
			self.add_path(RepeatLine(V(width-fromends, height-fromedge), V(fromends,height-fromedge), holesX, Bolt, bolt_config,layers=['base','perspex','paper']))
			self.add_path(RepeatLine(V(fromedge, height-fromends), V(fromedge,fromends), holesY, Bolt,bolt_config,layers=['base','perspex','paper']))

class ModuleClearBack(Part):
	def __init__(self, size, layer, **config):
		self.init(config)
		self.add_border(ModuleClearBackPath(size))
		b=self.border
		self.layer=layer
		
		fromedge=b.side+15
		fromends=b.corner+25
		fend=25
		if size=='A3':
                                holesX=4
                                holesY=3
                elif size=='A2':
                                holesX=4
                                holesY=3
                elif size=='A1':
                                holesX=4
                                holesY=4
		if 'screw_config' in config:
			screw_config=config['screw_config']
			self.add_path(RepeatLine(V(fromends, fromedge), V(b.width-fromends,fromedge), holesX, Screw, screw_config))
			self.add_path(RepeatLine(V(b.width-fromedge, fromends), V(b.width-fromedge,b.height-fromends), holesY, Screw, screw_config))
			self.add_path(RepeatLine(V(b.width-fromends, b.height-fromedge), V(fromends,b.height-fromedge), holesX, Screw, screw_config))
			self.add_path(RepeatLine(V(fromedge, b.height-fromends), V(fromedge,fromends), holesY, Screw,screw_config))
		if 'bolt_config' in config:
			bolt_config=config['bolt_config']
			self.add_path(RepeatLine(V(fromends, fromedge), V(b.width-fromends,fromedge), holesX, Bolt, bolt_config))
			self.add_path(RepeatLine(V(b.width-fromedge, fromends), V(b.width-fromedge,b.height-fromends), holesY, Bolt, bolt_config))
			self.add_path(RepeatLine(V(b.width-fromends, b.height-fromedge), V(fromends,b.height-fromedge), holesX, Bolt, bolt_config))
			self.add_path(RepeatLine(V(fromedge, b.height-fromends), V(fromedge,fromends), holesY, Bolt,bolt_config))
			
class ModuleClearBackPath(Path):
	def __init__(self,size,**config):
			
		self.init(config)
		if 'side' not in config:
			self.side='out'	
		self.closed=True

		self.side=17
		self.corner=51+self.side
		self.mid_height=120/2
		self.mid_width=39+self.side
		self.mid_edge=9
		self.mid_mid=60/2
		if size=='A3':
                        self.self.width=420
                        self.height=297
                elif size=='A2':
                        self.width=594
                        self.height=420
                elif size=='A1':
                        self.width=841
                        self.height=594
		self.add_point(V(self.side,self.corner))
		self.add_point(V(self.corner,self.side))
		self.add_point(V(self.width-self.corner,self.side))
		self.add_point(V(self.width-self.side,self.corner))
		if(size=='A1'):
			self.add_point(V(self.width-self.side,self.height/2-self.mid_height))
			self.add_point(V(self.width-self.side-self.mid_edge,self.height/2-self.mid_height))
			self.add_point(V(self.width-mid_self.width,self.height/2-mid_mid))
			self.add_point(V(self.width-mid_self.width,self.height/2+mid_mid))
			self.add_point(V(self.width-self.side-self.mid_edge,self.height/2+self.mid_height))
			self.add_point(V(self.width-self.side,self.height/2+self.mid_height))
		self.add_point(V(self.width-self.side,self.height-self.corner))
		self.add_point(V(self.width-self.corner,self.height-self.side))
		self.add_point(V(self.corner,self.height-self.side))
		self.add_point(V(self.side,self.height-self.corner))
		if(size=='A1'):
			self.add_point(V(self.side,self.height/2+self.mid_height))
			self.add_point(V(self.side-self.mid_edge,self.height/2+self.mid_height))
			self.add_point(V(mid_self.width,self.height/2+mid_mid))
			self.add_point(V(mid_self.width,self.height/2-mid_mid))
			self.add_point(V(self.side-self.mid_edge,self.height/2-self.mid_height))
			self.add_point(V(self.side,self.height/2-self.mid_height))
