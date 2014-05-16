from path import *
# create a rectangular path
class Rect(Path):
	def __init__(self, bl,  **config):
		self.init( config)
		self.cut_square(bl, config)

	def cut_square(self, bl, config):
		if 'centred' in config:
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

class ClearRect(Rect):
	def __init__(self, bl,  **config):
		self.init(config)
		if 'side' in config and config['side'] in ['in', 'out']:
			config['cornertype']='sharp'
		else:
			config['cornertype']='clear'
		self.cut_square(bl,config)
	def pre_render(config):
		if 'side' in config and config['side']=='in':
			config['cornertype']='clear'
		self.points=[]	
		
		print "pre-render"
class Polygon(Path):
	def __init__(self, pos, rad, sides, cornertype='sharp', cornerrad=False, **config):
		self.init( config)
		"""Cut a regular polygon with radius to the points :param rad: centred at :param pos:, with :param sides: sides with corners of type :param cornertype:\n"""+self.otherargs
                self.closed=True
		step=360/sides
		for i in range(0,sides):
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
					steps = math.ceil((countersinkrad-holerad)/((cutterconfig['diameter']/2-cutter_config['min_rad'])*0.7))
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
		print "Circle"+str(self.cutter)
		"""Cut a circle centre at :param pos: with radius :param rad:"""+self.otherargs
		self.closed=True
		self.add_point(pos,'circle',rad)
		self.comment("Circle")
		self.comment("pos="+str(pos)+" rad="+str(rad))
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
                        self.add_path(ob(start+step*i, **args),layers)
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
		print "Hole"+str(self.cutter)
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
					self.add_path(Circle(pos, rad[i], config))
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
	def __init__(self,pos,layer_conf, **config):
		self.init(config)
		for c in layer_conf.keys():
			conf = copy.deepcopy(layer_conf[c])
			print "screw:"+str(conf)
			self.add_path(Hole(pos, **conf), c)
class FourScrews(Part):
	def __init__(self, bl, tr, layer_conf, **config):
		self.init(config)
		d=tr-bl
		self.add_path(Screw(bl, layer_conf, **config))
		self.add_path(Screw(bl+V(d[0], 0), layer_conf, **config))
		self.add_path(Screw(bl+V(0, d[1]), layer_conf, **config))
		self.add_path(Screw(tr, layer_conf, **config))

class Bolt(Part):
	def __init__(self,pos,thread='M4',head='button', length=10, **config):
		self.init(config)
		if thread in milling.bolts:
			self.add_path(Hole(pos, milling.inserts[thread]['diams'][0],  side='in' , z1=milling.inserts[thread]['depths'][0]),'base')
			self.add_path(Hole(pos, milling.inserts[thread]['diams'][1],  side='in' , z1=milling.inserts[thread]['depths'][1]),'base')
			self.add_path(Hole(pos, milling.bolts[thread]['clearance']/2, side='in'),'perspex')
			if(head=='countersunk'):
				self.add_path(Countersink(pos, milling.bolts[thread]['clearance'], milling.bolts[thread]['countersunk']['diam']/2, config),'top')
			else:
				self.add_path(Hole(pos, milling.bolts[thread]['clearance'], side='in'),'top')
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
				self.add_path(ClearRect(bl=start-parallel*thickness+cra+crp, tr=start+along+cutin-cra-crp))
			else:
				self.add_path(ClearRect(bl=start-parallel+cra+crp, tr=start+along+cutin-cra-crp))
			m='off'
		else:
			m='on'
		for i in range(1,int(num_tabs)):
			if m=='on':
				# cut a bit extra on first tab if the next tab was off as well
				if i==num_tabs and nextmode=='off':
					self.add_path(ClearRect(bl=start+along*i+cra+crp, tr=start+along*(i+1)+cutin-cra-crp+parallel*thickness))
				else:
					self.add_path(ClearRect(bl=start+along*i+cra+crp, tr=start+along*(i+1)+cutin-cra-crp))
				
				m='off'
			else:
				m='on'
		self.comment("FingerJointMid")

class FingerJointBoxMidSide(Pathgroup):
	def __init__(self, pos, width, height, corners, sidemodes, tab_length, thickness, cutter,**config):
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
		self.init(config)
		self.closed=True
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
			
		cutterrad = milling.tools[cutter]['diameter']/2
		if 'left' in sidemodes and sidemodes['left']=='straight':
			self.add_point(V(0,height))
		else:
			if corners['left']=='off' and corners['bottom']=='off':
				self.add_point(pos+V(-thickness['left']-cutterrad, -thickness['bottom']-cutterrad),'sharp')
			self.add_points(FingerJoint(start=pos+V(0,0), end=pos+V(0,height), side=s, linemode=linemode, startmode=corners['left'], endmode=corners['left'], tab_length=tab_length, thickness=thickness['left'], cutterrad=cutterrad, fudge=fudge))
		if 'top' in sidemodes and sidemodes['top']=='straight':
			self.add_point(V(width,height))
		else:
			if corners['left']=='off' and corners['top']=='off':
				self.add_point(pos+V(-thickness['left']-cutterrad, height+thickness['top']+cutterrad),'sharp')
			self.add_points(FingerJoint(start=pos+V(0,height), end=pos+V(width,height), side=s, linemode=linemode,startmode=corners['top'], endmode=corners['top'], tab_length=tab_length, thickness=thickness['top'], cutterrad=cutterrad, fudge=fudge))
		if 'right' in sidemodes and sidemodes['right']=='straight':
			self.add_point(pos+V(width,0))
		else:
			if corners['top']=='off' and corners['right']=='off':
				self.add_point(pos+V(width+thickness['right']+cutterrad, height+thickness['top']+cutterrad),'sharp')
			self.add_points(FingerJoint(start=pos+V(width,height), end=pos+V(width,0), side=s, linemode=linemode, startmode=corners['right'], endmode=corners['right'], tab_length=tab_length, thickness=thickness['right'], cutterrad=cutterrad, fudge=fudge))
		if 'bottom' in sidemodes and sidemodes['bottom']=='straight':
			self.add_point(pos+V(0,0))
		else:
			if corners['right']=='off' and corners['bottom']=='off':
				self.add_point(pos+V(width+thickness['right']+cutterrad, -thickness['bottom']-cutterrad),'sharp')
			self.add_points(FingerJoint(start=pos+V(width,0), end=pos+V(0,0), side=s, linemode=linemode, startmode=corners['bottom'], endmode=corners['bottom'], tab_length=tab_length, thickness=thickness['bottom'], cutterrad=cutterrad, fudge=fudge))
		self.comment("FingerJointBoxSide")

class Module(Plane):
	def __init__(self, size,  **config):#holesX=False, holesY=False, fromedge=15, fromends=40):
		self.init('module',V(0,0),V(0,0),config)
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
		#name, material, thickness, z0=0,zoffset=0
		self.add_layer('perspex',material='perspex',thickness=3,z0=0,zoffset=3)
		self.add_layer('base',material='plywood',thickness=12,z0=0,zoffset=0, add_back=True)
#		self.add_layer('paper',material='paper',thickness=0.05,z0=0,zoffset=0.05)
		radius=30
		if size=='A3':
			width=297
			height=420
			if holesX==False:
				holesX=3
			if holesY==False:
				holesY=4
		elif size=='A2':
			width=594
			height=420
			if holesX==False:
				holesX=4
			if holesY==False:
				holesY=3
		elif size=='A1':
			width=594
			height=841
			if holesX==False:
				holesX=4
			if holesY==False:
				holesY=5
			
		edge= RoundedRect(bl=V(0,0), tr=V(width, height), rad=radius, side='out')
		if not ('no_perspex' in config and  config['no_perspex']):
			self.perspex = self.add_path(Part(name='perspex', border=edge, layer='perspex',colour="red"))
		self.base = self.add_path(Part(name='base', border=edge, layer='base'))
#		self.paper = self.add_path(Part(name='paper', border=edge, layer='paper'))

		
		self.add_path(Hole(V(radius,radius),rad=13/2,side='in'),['base','perspex','paper'])
		self.add_path(Hole(V(width-radius,radius),rad=13/2,side='in'),['base','perspex','paper'])
		self.add_path(Hole(V(width-radius,height-radius),rad=13/2,side='in'),['base','perspex','paper'])
		self.add_path(Hole(V(radius,height-radius),rad=13/2,side='in'),['base','perspex','paper'])

		if not ('no_holdown' in config and  config['no_holdown']):
			self.add_path(RepeatLine(V(fromends, fromedge), V(width-fromends,fromedge), holesX, Bolt, {},layers=['base','perspex','paper']))
			self.add_path(RepeatLine(V(width-fromedge, fromends), V(width-fromedge,height-fromends), holesY, Bolt, {},layers=['base','perspex','paper']))
			self.add_path(RepeatLine(V(width-fromends, height-fromedge), V(fromends,height-fromedge), holesX, Bolt,{},layers=['base','perspex','paper']))
			self.add_path(RepeatLine(V(fromedge, height-fromends), V(fromedge,fromends), holesY, Bolt,{},layers=['base','perspex','paper']))
			

