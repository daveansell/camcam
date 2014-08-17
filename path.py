import os
import math
from minivec import Vec, Mat
import Milling
import pprint
import copy
import collections
import traceback
import re

milling=Milling.Milling()

arg_meanings = {'order':'A field to sort paths by',
	       'transform':"""Transformations you can apply to the object this is a dict, and can include:
		:param rotate: - a list with two members
    		:param 0: - a position to rotate about
    		:param 1: - an angle to rotate""",
    		'side':'side to cut on, can be "on", "in", "out"',
		'z0':'z value to start cutting at', 
		'z1':'z value to end cutting at (less than z0)', 
		'thickness':'thickeness of the material - leads to default z1', 
		'material':'the type of material you are using - defined in Milling.py', 
		'colour':'colour to make svg lines as', 
		'cutter':'the cutter you are using - defined in Milling.py',
		'downmode':'how to move down in z can be "ramp" or "cutdown"',
		'mode':'code production mode - can be gcode, svg, or simplegcode - automatically set',
		'prefix':'prefix for code',
		'postfix':'add to end of code',
		'settool_prefix':'prefix before you set a tool',
		'settool_postfix':'add after setting a tool',
		'rendermode':'original mode defined in Milling.py',
 		'sort':'what to sort by', 
		'toolchange':'how to deal with a toolchange', 
		'linewidth':'svg line width', 
		'stepdown':'maximum stepdown - defined by cutter and material', 
		'forcestepdown':'force the stepdown - normally set to large so svgs only go around once', 
		'forcecolour':'mode where colour is forced by depth etc',
		'border':'A path to act as the border of the part',
		'layer':'The layer the part exists in - it can add things to other layers',
		'name':'The name of the object - str',
		'partial_fill':'cut a step into the path',
		'finishing':'add a roughing pass this far out ',
		'fill_direction':'direction to fill towards',
		'precut_z':'the z position the router can move dow quickly to',
		'ignore_border':'Do not just accept paths inside border',
		'material_shape':'shape the raw material is - flat, rod, tube, square_rod, square_tube',
		'material_length':'length of raw material needed', 
		'material_diameter':'diameter of raw material',
}
def V(x=False,y=False,z=False):
	if x==False:
		x=0
	if y==False:
		y=False
	if z==False:
		z=False
	return Vec(x,y,z)
def rotate(pos, a):
	if type(pos) is Vec:
		M=Mat(1).rotateAxis(a,V(0,0,-1))
		pos=pos.transform(M)
		return pos
	else:
		return False

class Segment(object):
	def __init__(self):
# segment type can be line, arc, bezier
		self.seg_type=False
	def gcode(self,direction=True):
		return {}
	def start(self):
		return {}
	def out(self,direction, mode='svg', zfrom=False, zto=False):
		if mode=='svg':
			return self.svg(direction)
		elif mode=='gcode':
			temp=self.gcode(direction)
			if len(temp)>0 and zfrom!=zto:
				temp[0]['Z']=zto
			return temp
		elif mode=='simplegcode' or mode=='scr':
			temp=self.simplegcode(zfrom, zto, direction)
			return temp	
	def svg(self):
		return {}
	def polygon(self):
		return []
# render the segment in straight lines
	def simplegcode(self, zfrom, zto, direction):
		ret=[]
		polygon=self.polygon(1,direction)
		if zfrom!=zto:
			step=(zto-zfrom)/len(polygon)
			z=zfrom
		else:
			z=0
			step=0
		for p in polygon:
			if step!=0:
				z+=step
				ret.append({"cmd":"G1","X":p[0],"Y":p[1],"Z":z})
			else:
				ret.append({"cmd":"G1","X":p[0],"Y":p[1]})
		return ret

class Line(Segment):
	def __init__(self, cutfrom, cutto):
		self.seg_type='line'
		self.cutto=cutto
		self.cutfrom=cutfrom
	def gcode(self,direction=True):
		if(direction):
			return [{"cmd":"G1","X":self.cutto[0],"Y":self.cutto[1]}]
		else:
			return [{"cmd":"G1","X":self.cutfrom[0],"Y":self.cutfrom[1]}]
	def svg(self,direction=True):
		if(direction):
			return [{"cmd":"L","x":self.cutto[0],"y":self.cutto[1]}] 
		else:
			return [{"cmd":"L","x":self.cutfrom[0],"y":self.cutfrom[1]}] 
	def polygon(self, resolution=1, direction=1):
		return [self.cutto]
class Arc(Segment):
	def __init__(self, cutfrom, cutto,centre,direction, mode='abs'):
		self.seg_type='arc'
		self.cutto=cutto
		self.cutfrom=cutfrom
		self.direction=direction
		if mode=='abs':
			self.centre=centre
		else:
			self.centre=cutfrom+centre
		
	def gcode(self,direction=True):
		if (self.centre-self.cutfrom).length()==0:
			print "Arc of zero length"
			return []
		if(not direction):
			if self.direction=='cw':
				return [{"cmd":"G2","X":self.cutfrom[0],"Y":self.cutfrom[1], "I":self.centre[0]-self.cutto[0], "J":self.centre[1]-self.cutto[1]}]
			else:
				return [{"cmd":"G3","X":self.cutfrom[0],"Y":self.cutfrom[1], "I":self.centre[0]-self.cutto[0], "J":self.centre[1]-self.cutto[1]}]
		else:
			if self.direction=='cw':
				return [{"cmd":"G3","X":self.cutto[0],"Y":self.cutto[1], "I":self.centre[0]-self.cutfrom[0], "J":self.centre[1]-self.cutfrom[1]}]
			else:
				return [{"cmd":"G2","X":self.cutto[0],"Y":self.cutto[1], "I":self.centre[0]-self.cutfrom[0], "J":self.centre[1]-self.cutfrom[1]}]
	def svg(self,direction=True):
		# Find if the arc is long or not
		tempcross=(self.centre-self.cutfrom).cross(self.centre-self.cutto)
		t=tempcross[2]
		if t>0 and self.direction=='cw' or t<0 and self.direction=='ccw':
			longflag="0"
		else:
			longflag="1"
		r=(self.centre-self.cutfrom).length()
		if self.direction=='cw':
			dirflag=1
		else:
			dirflag=0
		if(direction):
			return [{"cmd":"A","rx":r,"ry":r,"x":self.cutto[0],"y":self.cutto[1], '_lf':longflag,'_rot':0,'_dir':dirflag}] 
#			return [{'cmd':'L',"x":self.centre[0],"y":self.centre[1]},{'cmd':'L',"x":self.cutfrom[0],"y":self.cutfrom[1]},{"cmd":"A","rx":r,"ry":r,"x":self.cutto[0],"y":self.cutto[1], '_lf':longflag,'_rot':0,'_dir':dirflag}] 
		else:
			return [{"cmd":"A","rx":r,"ry":r,"x":self.cutfrom[0],"y":self.cutfrom[1], '_lf':longflag,'_rot':0,'_dir':dirflag}] 
#			return [{'cmd':'L',"x":self.centre[0],"y":self.centre[1]},{'cmd':'L',"x":self.cutto[0],"y":self.cutto[1]},{"cmd":"A","rx":r,"ry":r,"x":self.cutfrom[0],"y":self.cutfrom[1], '_lf':longflag,'_rot':0,'_dir':dirflag}] 
	def polygon(self,resolution=1, direction=1):
		if direction:
			cutfrom=self.cutfrom
			cutto=self.cutto
		else:
			cutfrom=self.cutto
			cutto=self.cutfrom
		r1 = cutfrom-self.centre
		r2 = cutto-self.centre
		dtheta = math.atan(resolution/r1.length())/math.pi*180
		if dtheta>45:
			dtheta=45
		if self.direction=='cw':
			dtheta=-dtheta
		if not direction:
			dtheta=-dtheta
		r=r1
		thetasum=0
		hasrisen=0
		dot=r.dot(r2)
		points=[]		
		while thetasum<360:
			r=rotate(r,dtheta)
			newdot=r.dot(r2)		
			if newdot>dot:
				hasrisen=1
			if hasrisen and newdot<dot:
				points.append(cutto)
				break
			points.append(self.centre+r)
			thetasum+=dtheta
			dot=newdot
		if thetasum>360:
			return [self.cutto]
		else:
			return points

		
			
class Quad(Segment):
	def __init__(self, cutfrom, cutto, cp):
		self.seg_type='quad'
		self.cutto=cutto
		self.cutfrom=cutfrom
		self.cp=cp
	def gcode(direction=True):
		if(direction):
			offset = cp - self.cutfrom
			return [{"cmd":"G5.1", "X":self.cutto[0], "Y":self.cutto[1], "I":offset[0], "J":offset[1]}]
		else:
			offset = cp - self.cutto
			return [{"cmd":"G5.1", "X":self.cutfrom[0], "Y":self.cutfrom[1], "I":offset[0], "J":offset[1]}]
	def svg(direction = True):
		if(direction):
                        offset = cp - self.cutfrom
                        return [{"cmd":"Q", "x":self.cutto[0], "y":self.cutto[1], "i":offset[0], "j":offset[1]}]
                else:
                        offset = cp - self.cutto
                        return [{"cmd":"Q", "x":self.cutfrom[0], "y":self.cutfrom[1], "i":offset[0], "j":offset[1]}]

	def polygon(self,resolution=1, direction=1):
		p0=self.cutfrom
		p1=self.cp1
		p2=self.cutto
		ret=[]
		numsteps = ((p2-p1).length()+(p1-p0).length())/resolution
		step = 1/numsteps
		for i in range[1:numsteps-1]:
			t=i*step
			ret.append((1-t)*(1-t)*p0 + 2*(1-t)*t*p1 + t*t*p2 )
		return ret		
		
# Ponint types can be:
# sharp 	- a sharp corner
# incurve	- arc so that the lines point at the point
# centred	- arc centred at this point
# clear		- cut a slot in corner so a sharp corner will fit
class Point(object):
	def __init__(self, pos, point_type, radius=0, cp1=False, cp2=False, direction=False, transform=False):
		self.pos=Vec(pos)
		self.point_type=point_type
		self.radius=radius
		self.cp1=Vec(cp1)
		self.cp2=Vec(cp2)
		self.direction=direction
		self.transform=transform
		self.obType="Point"
	def copy(self):
		return Point( self.pos, self.point_type, self.radius, self.cp1, self.cp2, self.direction, self.transform)
	def point_transform(self,ext_transformations=[]):
		p=self.copy()
		# If we are applying the transfomations the point shouldn't have them as a transform any more
		p.transform=False
		if self.transform!=False:
			transformations=[self.transform]
		else:
			transformations=[]
		transformations.extend(ext_transformations)
#		print "point transform "+str(transformations)
		if type(transformations) is list:
			for t in reversed(transformations):
				if type(t) is dict:
					if 'rotate' in t:
						p.pos=self.rotate(p.pos, t['rotate'])
						p.cp1=self.rotate(p.cp1, t['rotate'])
						p.cp2=self.rotate(p.cp2, t['rotate'])
					if 'translate' in t:
						p.pos += t['translate']
						p.cp1 += t['translate']
						p.cp2 += t['translate']
					if 'mirror' in t:
						p.pos = self.reflect(p.pos, t['mirror'])
						p.cp1 = self.reflect(p.cp1, t['mirror'])
						p.cp2 = self.reflect(p.cp2, t['mirror'])
					if 'scale' in t:
						p.pos = self.scale(p.pos, t['scale'])
						p.cp1 = self.scale(p.cp1, t['scale'])
						p.cp2 = self.scale(p.cp2, t['scale'])
		return p
# rotate point about a point 
	def rotate(self,pos, t):
		if type(pos) is Vec:
			pos = pos - t[0]
			M=Mat(1).rotateAxis(t[1],V(0,0,-1))
#		pos.rotateAxis(t[0],V(0,0,-1))
			pos=pos.transform(M)
			pos = pos + t[0]
			return pos
		else:
			return False

	def reflect(self,pos,t):
		if t is False or t is None or type(t) is list and (t[0] is False or t[0] is None):
			return pos
		if type(pos) is Vec and type(t[0]) is Vec:
			if type(t[1]) is str:
				if t[1]=='y':
					dirvec=V(0,1)
				if t[1]=='x':
					dirvec=V(1,0)
			elif type(t[1]) is Vec:
				dirvec = t[1]
			else:
				print "Reflection direction is not a string or vector"
			out=Vec(pos)
			out-=t[0]
			out=out.reflect(dirvec)
			out+=t[0]
			return out
		else:
			return False
	def scale(self, pos, t):
		if t is False or t is None or type(t) is list and (t[0] is False or t[0] is None):
			return pos
		if type(pos) is Vec and type(t[0]) is Vec:
			out=Vec(pos)
			out-=t[0]
			out*=t[1]
			out+=t[0]

class Path(object):
	def __init__(self, closed=False, **config):
		self.closed = closed
		self.init( config)
	def init(self, config):
		self.obType = "Path"
		self.trace = traceback.extract_stack()

		self.points = []
		self.Fsegments = []
		self.Bsegments = []
		self.transform=False
		self.otherargs=''
		self.varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter', 'partial_fill','finishing']
		for v in self.varlist:
			if v in config:
				setattr(self,v, config[v])
			else:
				setattr(self,v, None)
			self.otherargs+=':param v: '+arg_meanings[v]+"\n"
		self.start=False
		self.extents= {}	
		self.output=[]
		self.boundingBox={}
		self.centre=V(0,0)
		self.polygon={}
		self.changed={}
		self.parent=False
		self.comment("start:"+str(type(self)))
		self.is_copy=False
	
	def __deepcopy__(self,memo):
		obj_copy = object.__new__(type(self))
	#	obj_copy.__dict__ = self.__dict__.copy()
		for v in self.__dict__:
			if v=='parent':
				obj_copy.__dict__[v]=copy.copy(self.parent)
			else:
				obj_copy.__dict__[v]=copy.deepcopy(self.__dict__[v],memo)
		return obj_copy


	def comment(self, comment):
		comment = "".join(x for x in comment if x.isalnum() or x in '-._ ')
		self.add_out([{'_comment':str(comment)}])

	def overwrite(self,ain,b):
		a=copy.copy(ain)
		for i in b.keys():
			if i!='transformations':
				if i in b and b[i] is not False and b[i] is not None:
					a[i] = b[i]
				elif (i not in a or a[i] is False or a[i] is None ) or i not in a:
					a[i] =None
		if 'transformations' not in a or type(a['transformations']) is not list:
			if 'transform' in a:
				a['transformations']=[a['transform']]
			else:
				a['transformations']=[]
		if 'transformations' in b and type(b['transformations']) is list:
			a['transformations'].extend(b['transformations'])
		if 'transform' in b and b['transform'] is not False and b['transform'] is not None:
		#	if type(b['transform']) is list:			
			a['transformations'].append(b['transform'])
		return a
#		for i in b.keys():
#			if b[i] is not False and b[i] is not None:
#				a[i] = b[i]
#			if (b[i] is False or b[i] is None ) and i not in a:
#				a[i] = None

	def rotate(self,pos, angle):
		if self.transform==False or self.transform==None:
			self.transform={}
		self.transform['rotate']=[pos, angle]

	def mirror(self, pos, dirvec):	
		if self.transform==False or self.transform==None:
			self.transform={}
		self.transform['mirror']=[pos,dirvec]

	def translate(self,vec):
		if self.transform==False:
                        self.transform={}
                self.transform['translate']=vec

	def set_cutter(self, config):
		if config['cutter'] in milling.tools:
			tool=milling.tools[config['cutter']]
			config['cutterrad']=tool['diameter']/2
			config['endcut']=tool['endcut']
			config['sidecut']=tool['sidecut']
			if tool['sidecut']==0:
				config['downmode']='down'
			else:
				config['downmode']='ramp'
#		else:
#			print "cutter %s NOT FOUND" % config['cutter']
	def set_material(self, config):
		if config['material'] in milling.materials:
			mat=milling.materials[config['material']]
			config['vertfeed']=mat['vertfeed']
			config['sidefeed']=mat['sidefeed']
			config['stepdown']=mat['stepdown']
			config['kress_setting']=mat['kress_setting']
			if 'spring' in mat:
				config['spring']=mat['spring']
			else:
				config['spring']=0
#		else:
#			print "Material %s NOT FOUND" % config['material']

	def add_point(self,pos, point_type='sharp', radius=0, cp1=False, cp2=False, direction=False, transform=False):
		self.points.append(Point(pos, point_type, radius,cp1, cp2, direction, transform))
		self.has_changed()
	def prepend_point(self,pos, point_type='sharp', radius=0, cp1=False, cp2=False, direction=False, transform=False):
		self.points.insert(0,Point(pos, point_type, radius,cp1, cp2, direction, transform))
		self.has_changed()
	def add_points(self,points, end='end'):
		for p in points:
			if type(p) is Point:
				if end=='end':
					self.points.append(p)
				else:
					self.points.insert(0,p)
			else:
				print "add_points - adding a non-point"
		self.has_changed()
	def has_changed(self):
		for c in self.changed.keys():
			self.changed[c]=True
	def transform_pointlist(self, pointlist,transformations):
		pout=[]
		for p in pointlist:
			pout.append(p.point_transform(transformations))
		return pout

	def make_segments(self, direction,segment_array,config):
		pointlist = self.transform_pointlist(self.points,config['transformations'])
		if direction!=self.find_direction(config):
			pointlist.reverse()
			# this is in the wrong sense as it will be run second in the reversed sense
			self.isreversed=1
		else:
			self.isreversed=0
		for p,point in enumerate(pointlist):
			thispoint = pointlist[p]
			if hasattr(thispoint,'obType') and thispoint.obType=='Point':
				nextpoint=self.get_point(pointlist, p+1, self.closed)
				afternextpoint=self.get_point(pointlist, p+2, self.closed)
				lastpoint=self.get_point(pointlist, p-1, self.closed)
				beforelastpoint=self.get_point(pointlist, p-2, self.closed)
				beforebeforelastpoint=self.get_point(pointlist, p-3, self.closed)
				
			
				if p==0:
					if self.closed:
						frompoint=self.segment_point(lastpoint, beforelastpoint, thispoint,beforebeforelastpoint,nextpoint, segment_array, False, False, config)
					else:
						frompoint=self.segment_point(lastpoint, beforelastpoint, thispoint,beforebeforelastpoint,nextpoint, segment_array, False, False, config)
				frompoint=self.segment_point(thispoint, lastpoint, nextpoint,beforelastpoint,afternextpoint, segment_array, frompoint, True, config)
	def get_point(self, pointlist, pos, closed):
		if closed:
			return pointlist[pos%len(pointlist)]
		else:
			p=pos%(2*(len(pointlist)-1))
			if p>=len(pointlist):
				p=2*(len(pointlist)-1)-p
			return pointlist[p]

	def segment_point(self,thispoint, lastpoint, nextpoint,beforelastpoint, afternextpoint, segment_array, frompoint, do,config):
#		if frompoint is False:
#			frompoint=thispoint.pos#
		if thispoint.pos==lastpoint.pos and thispoint.point_type!='circle':
			return frompoint
		if thispoint.point_type=='sharp':
			if do:
				segment_array.append(Line(frompoint,thispoint.pos))
			frompoint=thispoint.pos
#		elif nextpoint==False:
#			print "No next point"
		elif thispoint.point_type=='incurve':
			angle=(thispoint.pos-lastpoint.pos).angle(nextpoint.pos-thispoint.pos)
			dl=thispoint.radius*math.tan((angle/180)/2*math.pi)
			startcurve=thispoint.pos-(thispoint.pos-lastpoint.pos).normalize()*dl
			endcurve = thispoint.pos+(nextpoint.pos-thispoint.pos).normalize()*dl
			# If these are straight there should be no curve or the maths blows up so just behave like a normal point
			if(((startcurve + endcurve)/2-thispoint.pos).length()==0):
				if do:
					segment_array.append(Line(frompoint,thispoint.pos))
			else:
				d = math.sqrt(dl*dl+thispoint.radius*thispoint.radius)/((startcurve + endcurve)/2-thispoint.pos).length()
				centre = thispoint.pos + ((startcurve + endcurve)/2-thispoint.pos)*d
				if do:
					segment_array.append(Line(frompoint,startcurve))
				tempdir=(thispoint.pos-frompoint).cross(nextpoint.pos-thispoint.pos)
				if tempdir[2]>0:
					tempd='cw'
				elif tempdir[2]<0:
					tempd='ccw'
				else:
			#		print "ERROR - straight arc"
					tempd='cw'	
				if do:
					segment_array.append(Arc(startcurve, endcurve, centre,tempd))
			frompoint=endcurve
		elif thispoint.point_type=='clear':
			# we want to cut so that the edge of the cutter just touches the point requested
			if thispoint.pos==lastpoint.pos:
				angle=(thispoint.pos-beforelastpoint.pos).angle(nextpoint.pos-thispoint.pos)
			elif thispoint.pos == nextpoint.pos:
				angle=(thispoint.pos-lastpoint.pos).angle(afternextpoint.pos-thispoint.pos)
				
			else:
				angle=(thispoint.pos-lastpoint.pos).angle(nextpoint.pos-thispoint.pos)
				
			d=config['cutterrad']*(1/math.sin((180-angle)/2/180*math.pi)-1)
                        extrapoint=thispoint.pos-(((lastpoint.pos-thispoint.pos).normalize()+(nextpoint.pos-thispoint.pos).normalize())/2).normalize()*d

#			extrapoint=thispoint.pos-((lastpoint.pos+nextpoint.pos)/2-thispoint.pos).normalize()*config['cutterrad']
			if do:
				segment_array.append(Line(frompoint,thispoint.pos))
				segment_array.append(Line(thispoint.pos,extrapoint))	
				segment_array.append(Line(extrapoint,thispoint.pos))
			frompoint=thispoint.pos
		elif thispoint.point_type=='doubleclear':
			if lastpoint.pos==thispoint.pos or thispoint.pos==nextpoint.pos or lastpoint.pos==nextpoint.pos:
				d=0
			else:
				angle=(thispoint.pos-lastpoint.pos).angle(nextpoint.pos-thispoint.pos)
				d=config['cutterrad']*(1/math.sin((180-angle)/2/180*math.pi)-1)
                        o=(((lastpoint.pos-thispoint.pos).normalize()+(nextpoint.pos-thispoint.pos).normalize())/2).normalize()*d
			extrapoint1=thispoint.pos-o
			extrapoint2=thispoint.pos+o
			if do:
				segment_array.append(Line(frompoint,thispoint.pos))
				segment_array.append(Line(thispoint.pos,extrapoint1))	
				segment_array.append(Line(thispoint.pos,extrapoint2))	
				segment_array.append(Line(extrapoint2,thispoint.pos))
			frompoint=thispoint.pos
		elif thispoint.point_type=='arc_centred':
			if do:
				if (thispoint.cp-frompoint).length()!=(thispoint.pos-thispoint.cp).length():
					print "Error - centred arc two radiuses are not the same"
				segment_array.append(Arc(frompoint, thispoint.pos, thispoint.cp,thispoint.direction))
			frompoint=thispoint.pos
		elif thispoint.point_type=='arcend':
			if(lastpoint.point_type!='arc'):
				segment_array.append(Line(frompoint,thispoint.pos))
			frompoint=thispoint.pos
		elif thispoint.point_type=='arc' and thispoint.radius>0:
			# draw an arc between two points or radius radius - they should both have the same radius
			if nextpoint.point_type=='arcend' and lastpoint.point_type=='arcend':
				centre=self.findArcCentre(lastpoint.pos,nextpoint.pos, thispoint.radius, thispoint.direction)
				segment_array.append(Arc(frompoint, nextpoint.pos, centre,thispoint.direction))
			else:
				print "ERROR arc point without an arcend point on both sides"	
		elif thispoint.point_type=='quad':
			print "Quadratic curve\n"
			if do:
				segment_array.append(Quad(frompoint, thispoint.pos, thispoint.cp))
			frompoint = thispoint.pos		
		elif thispoint.point_type=='cubic':
			print "Cubic curve\n"
		elif thispoint.point_type=='outcurve':
			if lastpoint.point_type=='outcurve':
				lr=lastpoint.radius
			else:
				lr=0
			if (lastpoint.pos-beforelastpoint.pos).cross(thispoint.pos-lastpoint.pos)[2] <0:
				d1='cw'
			else:
				d1='ccw'
			if (thispoint.pos-lastpoint.pos).cross(nextpoint.pos-thispoint.pos)[2] <0:
				d2='cw'
			else:
				d2='ccw'
			p1=self.tangent_points( lastpoint.pos, lr, d1, thispoint.pos, thispoint.radius, d2)
			if do:
				segment_array.append( Line(p1[0], p1[1]))
			d3=''
			if nextpoint.point_type=="outcurve":
				if (nextpoint.pos-thispoint.pos).cross(afternextpoint.pos-nextpoint.pos)[2] <0:
					d3='cw'
				else:
					d3='ccw'
				
				p2=self.tangent_points( thispoint.pos, thispoint.radius, d2, nextpoint.pos, nextpoint.radius, d3)
				if do:
					segment_array.append( Arc( p1[1],p2[0], thispoint.pos, self.otherDir(d2)))
				frompoint=p2
			else:
				
				p2 = self.tangent_point(nextpoint.pos, thispoint.pos, thispoint.radius, self.otherDir(d2))
				if do:
					segment_array.append( Arc( p1[1],p2, thispoint.pos, self.otherDir(d2)))
				frompoint=p2
				
			#	frompoint = #rerun tangent points for next pair of points...
		elif thispoint.point_type=='circle':
			if self.side=='out':
				d='cw'
			else:
				d='ccw'
			if do:
				segment_array.append(Arc(V(thispoint.pos[0]-thispoint.radius, thispoint.pos[1]),V(thispoint.pos[0]+thispoint.radius, thispoint.pos[1]), thispoint.pos,d))
				segment_array.append(Arc(V(thispoint.pos[0]+thispoint.radius, thispoint.pos[1]),V(thispoint.pos[0]-thispoint.radius, thispoint.pos[1]), thispoint.pos,d))
			frompoint = V(thispoint.pos[0]-thispoint.radius, thispoint.pos[1])
		return frompoint

	def findArcCentre(self,frompos, topos, radius, direction):
		l=(topos-frompos)/2
		
		if l.length()>radius*2:
			print "ERROR arc radius less than distance to travel"
		if direction=='cw':
			a=90
		else:
			a=-90
		if radius-l.length()<0.0001:
			return (topos+frompos)/2
		else:
			d=math.sqrt(radius**2-l.length()**2)
			return (topos+frompos)/2+rotate(l.normalize(),a)*d

	def otherDir(self,direction):
		if direction=='cw':
			return 'ccw'
		else:
			return 'cw'
# Find 2 points joined by a line from r1 from point1 and r2 from point2
	def tangent_points(self, point1, r1, dir1, point2, r2, dir2):
		if dir1!=dir2:
			r=r1+r2
			temp=self.tangent_point(point1, point2, r, dir2)
			rvec=(temp-point2).normalize()
			return [point1-rvec*r1, point2+rvec*r2]
			
		if r1>r2:
			r=r1-r2
			temp=self.tangent_point(point2, point1, r, self.otherDir(dir1))
			rvec=(temp-point1).normalize()
			return [point1+rvec*r1, point2+rvec*r2]
		elif r1<r2:
			r=r2-r1
			temp=self.tangent_point(point1, point2, r, dir1)
			rvec=(temp-point2).normalize()
			return [point1+rvec*r1, point2+rvec*r2]
		else:
			r=r1
			if(dir1=='cw'):
                	        sgn=-90
			else:
				sgn=90
			rvec=rotate((point2-point1).normalize(),sgn)
			return [point1+rvec*r, point2+rvec*r]

# Find the point that makes a tangent about centre when a line is drawn from point to the new point
	def tangent_point(self,point,centre,r, dir='cw'):
		if(dir=='cw'):
#			sgn=1
			a=-90
		else:
			a=90
#			sgn=-1

		diff=centre-point
		offset=rotate(diff.normalize(),a)
#	return centre+offset*r

		d=diff.length()
		l=math.sqrt(d*d-r*r)
		theta= math.acos(r/d)

		rx=-r* math.cos(theta) *diff.normalize()
		ry=r* math.sin(theta) *offset
		return centre+rx+ry
				

		theta = math.atan2(r,l)
#		theta = math.atan2(diff[1],diff[0])
		phi = math.asin(r/d)
			
		rvec = V(l * math.sin(theta+phi*sgn), l * math.cos(theta+phi*sgn), 0)
		if(diff[0]<0):
			rvec[0]*=-1
		return point+rvec

	def offset_path(self,side,distance, config):
		newpath=copy.deepcopy(self)
		newpath.points=[]
		thisdir=self.find_direction(config)
		pointlist=self.points
		if len(pointlist)==1:
			if pointlist[0].point_type=='circle':
				p = copy.copy(pointlist[0])
				if side=='in':
					p.radius-=distance
				elif side=='out':
					p.radius+=distance
				newpath.points.append(p)
				return newpath
		
		if side=='in':
			if thisdir=='cw' and self.mirrored>0 or thisdir=='ccw' and not self.mirrored>0:
				side='right'
			else:
				side='left'
		elif side=='out':
			if thisdir=='cw' and self.mirrored>0 or thisdir=='ccw' and not self.mirrored>0:
				side='left'
			else:
				side='right'
		for p,point in enumerate(pointlist):
			thispoint=point.point_transform()
			if self.closed:
				nextpoint=pointlist[(p+1)%len(pointlist)].point_transform()
				lastpoint=pointlist[(p-1)%len(pointlist)].point_transform()
				beforelastpoint=pointlist[(p-2)%len(pointlist)].point_transform()
				beforebeforelastpoint=pointlist[(p-3)%len(pointlist)].point_transform()
				afternextpoint=pointlist[(p+2)%len(pointlist)].point_transform()
				afterafternextpoint=pointlist[(p+3)%len(pointlist)].point_transform()
			else:
				nextpoint=(pointlist[p+1:p+2] + [None])[0]
				if nextpoint is not None:
					nextpoint=nextpoint.point_transform()
				lastpoint=(pointlist[p-1:p] + [None])[0],
				if lastpoint is not None:
					lastpoint=lastpoint.point_transform()
				beforelastpoint=(pointlist[p-2:p-1] + [None])[0],
				if beforelastpoint is not None:
					beforelastpoint=beforelastpoint.point_transform()
				beforebeforelastpoint=(pointlist[p-3:p-2] + [None])[0],
				if beforebeforelastpoint is not None:
					beforebeforelastpoint=beforebeforelastpoint.point_transform()
				afternextpoint=(pointlist[p+2:p+3] + [None])[0],
				if afternextpoint is not None:
					afternextpoint=afternextpoint.point_transform()
				afterafternextpoint=(pointlist[p+3:p+4] + [None])[0],
				if afternextpoint is not None:
					afternextpoint=afternextpoint.point_transform()
			t=self.offset_point(
				thispoint, 
				beforelastpoint, 
				lastpoint, 
				nextpoint, 
				afternextpoint, 
				self.segment_point(lastpoint, beforelastpoint, thispoint,beforebeforelastpoint, nextpoint, [], False, False, config), 
				self.segment_point(nextpoint, afternextpoint, thispoint,afterafternextpoint, lastpoint, [], False, False, config), 
				side,distance, 
				thisdir)
			if t:
				newpath.points.append(t)
		return newpath


	def offset_point(self, thispoint, beforelastpoint, lastpoint, nextpoint, afternextpoint, frompos, topos, side,distance, thisdir):
		t=copy.copy(thispoint)
		cross=(thispoint.pos-lastpoint.pos).cross(nextpoint.pos-thispoint.pos)[2]
		a=(-(thispoint.pos-lastpoint.pos).normalize()+(thispoint.pos-nextpoint.pos).normalize())
		al=a.length()
		if distance==4:
			print (thispoint.pos-lastpoint.pos).angle(thispoint.pos-nextpoint.pos)
		angle2=((thispoint.pos-lastpoint.pos).angle(thispoint.pos-nextpoint.pos)/2-90)*math.pi/180
#			print math.cos(((thispoint.pos-lastpoint.pos).angle(thispoint.pos-nextpoint.pos)/2-90)*math.pi/180)
		angle=math.atan2(a[1], a[0])
		if cross<0 and side=='left' or cross>0 and side=='right':
			corner='external'
		else:
			corner='internal'
		if thispoint.point_type=='outcurve':
			if corner=='external':
				t.radius+=distance
			else:
				if t.radius>distance:
					t.radius-=distance
				else:
					t.point_type='doubleclear'
					t.radius=0
					t.pos = self.offset_move_point(thispoint.pos, lastpoint.pos, nextpoint.pos, frompos,topos, side, (distance-thispoint.radius)/abs(math.cos(angle)))
		elif thispoint.point_type=='incurve':
			if corner=='external':# and side=='out' or corner=='internal' and side=='in':
				t.radius+=distance
#				if distance==4:
#					print "EXTERNAL ANGLE="+str(angle/math.pi*180)+" cos="+str(abs(math.cos(angle)))+" dist="+str(distance)
				t.pos = self.offset_move_point(thispoint.pos, lastpoint.pos, nextpoint.pos, frompos, topos, side, -distance/abs(math.cos(angle2)))
			else:
#				if distance==4:
#					print "INTERNAL ANGLE="+str(angle/math.pi*180)+" cos="+str(abs(math.cos(angle)))+" dist="+str(distance)
				if t.radius>distance:
					t.radius-=distance
					t.pos = self.offset_move_point(thispoint.pos, lastpoint.pos, nextpoint.pos, frompos, topos, side, distance/abs(math.cos(angle)))
				else:
					t.point_type='sharp'
					t.radius=0
					t.pos = self.offset_move_point(thispoint.pos, lastpoint.pos, nextpoint.pos, frompos, topos, side, distance/abs(math.cos(angle)))
		elif thispoint.point_type=='sharp':
			if corner=='external':# and side=='out' or corner=='internal' and side=='in':
#				t.radius=distance
#				t.point_type='outcurve'
				t.pos = self.offset_move_point(thispoint.pos, lastpoint.pos, nextpoint.pos, frompos, topos, side, -distance/abs(math.cos(angle)))
			else:
				t.point_type='clear'
				t.pos = self.offset_move_point(thispoint.pos, lastpoint.pos, nextpoint.pos, frompos, topos, side, distance/abs(math.cos(angle)))
		elif thispoint.point_type=='clear' or thispoint.point_type=='doubleclear':
				t.point_type='doubleclear'
				t.pos = self.offset_move_point(thispoint.pos, lastpoint.pos, nextpoint.pos, frompos, topos, side, distance/abs(math.cos(angle)))
		elif thispoint.point_type=='circle':
			if corner=='external':
                                t.radius+=distance
			elif radius>distance:
				t.radius-=distance
			elif t.radius==0.05:
				return False
			else:
				t.radius=0.05;

		elif thispoint.point_type=='arcend':
			# PROBLEM doesn't work if lastpoint was a outcurve...
			if lastpoint.point_type=='arc':
				c=self.findArcCentre(beforelastpoint.pos, thispoint.pos, lastpoint.radius, lastpoint.direction)
				rvec=(thispoint.pos-c).normalize()
				if lastpoint.direction=='cw':
					a=-90
				else:
					a=90
				invec=rotate(rvec,a)
			else:
				invec=(thispoint.pos-lastpoint.pos).normalize()

			if nextpoint.point_type=='arc':
				c=self.findArcCentre(thispoint.pos, afternextpoint.pos, nextpoint.radius, nextpoint.direction)
				rvec=(thispoint.pos-c).normalize()
				if nextpoint.direction=='cw':
					a=-90
				else:
					a=90
				outvec=rotate(rvec,a)
			else:
				outvec=(nextpoint.pos-thispoint.pos).normalize()
			cross=(invec).cross(outvec)[2]
		        a=-(invec+outvec)
                	angle=math.atan2(invec[1], invec[0])-math.atan2(outvec[1], outvec[0])
			if angle<0:
				sgn=-1
			else:
				sgn=1
                	if cross<0 and side=='left' or cross>0 and side=='right':
                        	corner='external'
                	else:
                        	corner='internal'
			t.pos = self.offset_move_point(thispoint.pos, lastpoint.pos, nextpoint.pos, thispoint.pos-invec, thispoint.pos+outvec, side, distance/math.cos(angle/2)*sgn)
		elif thispoint.point_type=='arc' and thispoint.radius>0:
			if (side=='left' and thispoint.direction=='cw' or side=='right' and thispoint.direction=='ccw') != self.mirrored:
				t.radius+=distance
			else:
				if t.radius>distance:
					t.radius-=distance
				else:
					t.radius=0
					print "Arc has gone to zero radius - this is broken..."				
		return t

	def offset_move_point(self,thispos, lastpos, nextpos, frompos, topos, side,distance):
		if side=='left':
			a=-90
		else:
			a=90
		vecin=(thispos-frompos).normalize()
		vecout=(topos-thispos).normalize()
		# Find average direction of two vectors
		avvec=(vecin-vecout).normalize()
		# then rotate it 90 degrees towards the requested side
		if avvec.length()<0.001:
			return rotate(vecin,a)+thispos
		return -avvec*distance+thispos
#		return rotate(avvec*distance,a)*2+thispos

# find whether the path is setup clockwise or anticlockwise
	def find_direction(self,config):
		total =V(0,0,0)
		first = True
		if 'transformations' in config:
			t=config['transformations']
		else:
			t=[]
		reverse=0
		for a in t:
			if type(a) is dict and 'mirror' in a:
				reverse+=1
		if reverse%2==1:
			reverse=-1
		else:
			reverse=1
		self.mirrored=reverse
		for p,q in enumerate(self.points):
			total+=(self.points[p].pos-self.points[(p-1)%len(self.points)].pos).normalize().cross((self.points[(p+1)%len(self.points)].pos-self.points[p].pos).normalize())
		# if it is a circle
		if total[2]==0:
			return 'cw'
		elif(total[2]*reverse>0):
			return 'ccw'
		else:
			return 'cw'
	
	def cut_direction(self,side='on'):
		if side=='in':
			return 'cw'
		else:
			return 'ccw'

	
	# converts a shape into a simple polygon
	def polygonise(self,resolution=5):
		ret=[]
		self.Fsegments=[]
		if resolution in self.polygon and (resolution not in self.changed or self.changed[resolution]==False):
			return self.polygon[resolution]
		else:
			config=self.generate_config({'cutterrad':0})
			self.make_segments('cw',self.Fsegments,config)
			for s in self.Fsegments:
				ret.extend(s.polygon(resolution))
			for p in ret:
				if 'bl' not in self.boundingBox:
					self.boundingBox={'bl':[1000000000,1000000000],'tr':[-1000000000,-1000000000]}
				self.boundingBox['bl'][0]=min(self.boundingBox['bl'][0],p[0])
				self.boundingBox['bl'][1]=min(self.boundingBox['bl'][1],p[1])
				self.boundingBox['tr'][0]=max(self.boundingBox['tr'][0],p[0])
				self.boundingBox['tr'][1]=max(self.boundingBox['tr'][1],p[1])
			self.boundingBox['tr']=V(self.boundingBox['tr'][0],self.boundingBox['tr'][1])
			self.boundingBox['bl']=V(self.boundingBox['bl'][0],self.boundingBox['bl'][1])
			self.centre=(self.boundingBox['bl']+self.boundingBox['tr'])/2
			self.polygon[resolution]=ret
			self.changed[resolution]=False
			return ret

	def in_bounding_box(self,point):
		return point[0]>=self.boundingBox['bl'][0] and point[1]>=self.boundingBox['bl'][1] and point[0]<=self.boundingBox['tr'][0] and point[1]<=self.boundingBox['tr'][1]
	def intersect_bounding_box(self,bbox):
		if self.in_bounding_box(bbox['tr']) or self.in_bounding_box(bbox['bl']) or self.in_bounding_box([bbox['tr'][0],bbox['bl'][1]]) or self.in_bounding_box([bbox['bl'][0],bbox['tr'][1]]):
			return True
		else:
			return False


	def contains(self,other):
		if other.obType=="Point":
			if self.in_bounding_box(other):
				if self.contains_point(other, this.polygon):
					return 1
				else:
					return -1
		elif other.obType=="Path" or other.obType=="Part":

			if other.obType=="Part":
				otherpolygon = other.border.polygonise()
			else:
				otherpolygon = other.polygonise()
			thispolygon = self.polygonise()
			if not self.intersect_bounding_box(other.boundingBox):
				return -1
			for tp,a in enumerate(thispolygon):
				for op,b in enumerate(otherpolygon):
					if self.closed_segment_intersect(thispolygon[tp-1%len(thispolygon)], a, otherpolygon[op-1%len(otherpolygon)], b):
						return 0
			if self.contains_point(otherpolygon[0], thispolygon):
				return 1
			else:
				return -1

	def contains_point(self,point, poly):
		n = len(poly)
		inside =False
		x=point[0]
		y=point[1]
		p1x,p1y,p1z = poly[0]
		for i in range(n+1):
			p2x,p2y,p2z = poly[i % n]
			if y > min(p1y,p2y):
				if y <= max(p1y,p2y):
					if x <= max(p1x,p2x):
						if p1y != p2y:
							xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
						if p1x == p2x or x <= xinters:
							inside = not inside
			p1x,p1y = p2x,p2y

		return inside

	def get_side(self,a,b,c):
	    """ Returns a position of the point c relative to the line going through a and b
	        Points a, b are expected to be different
	    """
	    d = (c[1]-a[1])*(b[0]-a[0]) - (b[1]-a[1])*(c[0]-a[0])
	    return 1 if d > 0 else (-1 if d < 0 else 0)
	
	def is_point_in_closed_segment(self,a, b, c):
	    """ Returns True if c is inside closed segment, False otherwise.
	        a, b, c are expected to be collinear
	    """
	    if a[0] < b[0]:
	        return a[0] <= c[0] and c[0] <= b[0]
	    if b[0] < a[0]:
	        return b[0] <= c[0] and c[0] <= a[0]
	
	    if a[1] < b[1]:
	        return a[1] <= c[1] and c[1] <= b[1]
	    if b[1] < a[1]:
	        return b[1] <= c[1] and c[1] <= a[1]
	
	    return a[0] == c[0] and a[1] == c[1]

	#
	def closed_segment_intersect(self,a,b,c,d):
	    """ Verifies if closed segments a, b, c, d do intersect.
	    """
	    if a == b:
	        return a == c or a == d
	    if c == d:
	        return c == a or c == b
	
	    s1 = self.get_side(a,b,c)
	    s2 = self.get_side(a,b,d)
	
	    # All points are collinear
	    if s1 == 0 and s2 == 0:
	        return \
	            self.is_point_in_closed_segment(a, b, c) or self.is_point_in_closed_segment(a, b, d) or \
	            self.is_point_in_closed_segment(c, d, a) or self.is_point_in_closed_segment(c, d, b)
	
	    # No touching and on the same side
	    if s1 and s1 == s2:
	        return False
	
	    s1 = self.get_side(c,d,a)
	    s2 = self.get_side(c,d,b)
	
	    # No touching and on the same side
	    if s1 and s1 == s2:
	        return False
	
	    return True
		



# find depths you should cut at
	def get_depths(self,mode, z0, z1, stepdown):
		if z0==z1:
			return [1,[]]
		if self.mode=='svg' or mode=='laser':
			return [stepdown,[0]]
		if self.mode=='gcode' or self.mode=='simplegcode':
			minsteps=math.ceil(float(abs(z0-z1))/stepdown)
			step=(z1-z0)/minsteps
			ret=[]
			i=1
			while i<=minsteps:
				ret.append(z0+i*step)
				i+=1
			return [step,ret]
		return [stepdown,[0]]
	def get_config(self):
		if self.parent is not False:
			pconfig = self.parent.get_config()
		else:
			pconfig = False
		config = {}
		if pconfig is False or  pconfig['transformations']==False or pconfig['transformations'] is None:
			config['transformations']=[]
		else:
			config['transformations']=pconfig['transformations'][:]
		if self.transform!=None:
			config['transformations'].append(self.transform)
		#	self.transform=None
		self.varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode', 'stepdown','forcestepdown', 'mode','partial_fill','finishing','fill_direction','precut_z']
                for v in self.varlist:
			if v !='transform' and v !='transformations':
	                        if hasattr(self,v) and getattr(self,v) is not None:
					config[v]=getattr(self,v)
	                        elif pconfig is not False and v in pconfig and pconfig[v] is not None:
	                                config[v]=pconfig[v]
				else:
					config[v]=None
		if self.is_copy:
			print "Q"+str(config['transformations'])
		return config

	def generate_config(self, pconfig):
		config={}
		config=self.overwrite(config,pconfig)
		inherited = self.get_config()
#		if('transformations' in config):
		config=self.overwrite(config, inherited)
		
#		if('transformations' in config):
#		for k in inherited.keys():
 #                       if (config[k] is None or config[k] is False) and k in pconfig:
  #                              config[k]=pconfig[k]
		self.set_cutter(config)
		self.set_material(config)
		thisdir=self.find_direction(config)
		if 'direction' not in config or config['direction'] is False:
			if hasattr(self,'direction') and  self.direction!=False:
				config['direction']=self.direction
			elif(config['side'] =='in'):
				config['direction']='cw'
			elif(config['side'] =='out'):
				config['direction']='ccw'
			else:
				config['direction']=thisdir
#		if self.mirrored==-1:
#			config['direction']=self.otherDir(config['direction'])
		if config['side'] is None or config['side'] is False:
			config['side']='on'
		if config['z0'] is None or config['z0'] is False:
			config['z0']=0
		if (config['z1'] is False or config['z1'] is None) and config['z0'] is not None and config['thickness'] is not None:
			if 'z_overshoot' in config:
				config['z1'] = - config['thickness']- config['z_overshoot']
			else:
				config['z1'] = - config['thickness']
		return config
#  output the path
	def render(self,pconfig):
		out=""
# Do something about offsets manually so as not to rely on linuxcnc
		config=self.generate_config(pconfig)
		if hasattr(self,'__render__') and callable(self.__render__):
			self.__render__(config)
		finalpass=False
		if config['side']=='in' or config['side']=='out':
			c =copy.copy(config)
			c['opacity']=0.5
			thepath=self.offset_path(c['side'],c['cutterrad'],c)
			c['side']='on'
			if config['hide_cuts']:
				self.output_path(config)
				return [config['cutter'],self.render_path(self,config)]
			elif config['overview']:
				self.output_path(config)
				#out = thepath.render_path(thepath,c) + self.render_path(self,config)
				out = self.render_path(self,config)
#			else:
#				out = thepath.render_path(thepath,config)
		else:
			thepath=self
			c=config
	#		thepath.output_path(config)
	#		out = thepath.render_path(self,config)
		if 'finishing' in config and config['finishing']>0:
			if 'partial_fill' not in config or config['partial_fill']==None or config['partial_fill']==False:
				config['partial_fill']=config['finishing']
				if config['side']=='out':
					config['fill_direction']='out'
				else:
					config['fill_direction']='in'
				#if c['side']=='out':
				c['z1']=c['z1']+1
				finalpass=True
				finishing=config['finishing']
			else:
				finishing=0
		else:
			finishing=0
	
		if not config['hide_cuts']  and 'partial_fill' in config and config['partial_fill']>0:
			dist=max(config['partial_fill']-config['cutterrad'], finishing)
			if dist<=0:
				numpasses=0
				step=1
			else:
				numpasses = math.ceil(abs(float(dist)/ float(config['cutterrad'])/1.4))
				step = config['partial_fill']/numpasses
			if 'fill_direction' in config:
				ns=config['fill_direction']
			else:
				if config['side']=='in':
					ns='out'
				elif config['side']=='out':
					ns='in'
				elif config['side']=='left':
					ns='right'
				elif config['side']=='right':
					ns='left'
				else:
					ns=c['side']
# need to find the frompos of first and last point, then add this as a sharp point each time adding a new path

# need to break circles into 2 arcs

			fillpath=copy.deepcopy(thepath)
			if(numpasses>0 and fillpath.points[0].point_type=='circle'):
					
					p=fillpath.points[0]
					fillpath.points=[]
					fillpath.add_point(p.pos-V(p.radius,0), point_type='arcend')
					fillpath.add_point(p.pos-V(p.radius,0), point_type='arc',  radius=p.radius, direction='cw')
					fillpath.add_point(p.pos+V(p.radius,0), point_type='arcend')
					fillpath.add_point(p.pos, point_type='arc',radius=p.radius, direction='cw')
					fillpath.add_point(p.pos-V(p.radius,0), point_type='arcend')
			if fillpath.find_direction(c)!=config['direction']:
				reverse=True
				fillpath.points=fillpath.points[::-1]
			else:
				reverse=False
#				fillpath.points=fillpath.points[::-1]
			if numpasses>0:
#(pointlist, p+1, self.closed)
#				frompoint=self.segment_point(lastpoint, beforelastpoint, thispoint,beforebeforelastpoint,nextpoint, segment_array, False, False, config)
			# if it is a circle we need to split it into 2 arcs to be able to fill properly
				fillpath.output_path(config)
				frompos=self.get_frompos(fillpath.points, fillpath.Fsegments, -1, c)
				if frompos!=fillpath.points[-1].pos:
                                	fillpath.add_point(frompos,'sharp')
				else:
					fillpath.points[-1].point_type='sharp'
	                        fillpath.prepend_point(frompos,'sharp')
				
			for d in range(0,int(numpasses)):
				temppath=thepath.offset_path(ns, step*(d+1), c)
				temppath.output_path(config)
				frompos=self.get_frompos(temppath.points, temppath.Fsegments, -1, c)
				if frompos!=temppath.points[-1].pos:
                                	temppath.add_point(frompos,'sharp')
				else:
					temppath.points[-1].point_type='sharp'
	                       	temppath.prepend_point(frompos,'sharp')
#				if temppath.find_direction(c)==fillpath.find_direction(c):
				if reverse:
					fillpath.add_points(temppath.points,'start')
				else:
					fillpath.add_points(temppath.points[::-1],'start')
#				else:
#					fillpath.add_points(temppath.points[::-1],'start')
#			if reverse:
#				fillpath.points = fillpath.points[::-1]
			offpath=thepath
			thepath=fillpath
		thepath.output_path(c)
		out += thepath.render_path(thepath,c)
		if finalpass:
			c['z0']=c['z1']
			c['z1']=config['z1']
			c['partial_fill']=None
			offpath.output_path(c)
			out += offpath.render_path(offpath,c)
		return [config['cutter'],out]

	def get_frompos(self, points, segments, p, config, closed=None):
		if closed is None:
			closed=self.closed
		return self.segment_point(self.get_point(points,p,self.closed), self.get_point(points,p-1,self.closed), self.get_point(points,p+1,closed),  self.get_point(points,p-2,self.closed), self.get_point(points, p+2,self.closed), self.Fsegments, False, False, config)

	def render_path(self,path,config):
		ret=""
		if config['mode']=='svg':
			ret+=self.render_path_svg(self.output,config)
		elif config['mode']=='gcode' or config['mode']=='simplegcode':
			ret+=self.render_path_gcode(self.output,config)
		elif config['mode']=='scr':
			ret+=self.render_path_scr(self.output,config)
# 		elif config['mode']=='simplegcode':
#			ret+=self.render_path_gcode(self.output,config)+'G0Z%0.2f\n'%config['clear_height']
		return ret

	def render_path_svg(self,path,config):
		ret=""
		comments=""
		for point in path:
			if 'cmd' in point:
				ret+=" "+point['cmd']
			if 'rx' in point:
				ret+=" %0.2f"%point['rx']
			if 'ry' in point:
				ret+=",%0.2f"%point['ry']
			if '_rot' in point:
				ret+=",%0.0f"%point['_rot']
			if '_lf' in point:
				ret+=" %s"%point['_lf']
			if '_dir' in point:
				ret+=" %s"%point['_dir']
			if 'x' in point:
				ret+=" %0.2f"%point['x']
			if 'y' in point:
				ret+=",%0.2f"%point['y']
			if 'x2' in point:
				ret+=" %0.2f"%point['x2']
			if 'y2' in point:
				ret+=",%0.2f"%point['y2']
			if '_comment' in point :
				comments+="<!--"+point['_comment']+"-->\n"
			if '_colour' in point and point['_colour'] is not None:
				colour=point['_colour']
			else:
				colour='black'
			if '_opacity' in point:
				opacity = "opacity:"+str(point['_opacity'])
			else:
				opacity = "opacity:1"
			if '_closed' in point and point['_closed']:
				z=' Z'
			else:
				z=''
		ret+=z
		return comments+"<path d=\""+ret+"\"  style='stroke-width:0.1px;"+opacity+"' fill='none' stroke='"+colour+"'/>\n"

	def render_path_gcode(self,path,config):
		ret=""
		for point in path:
			if '_comment' in point and config['comments']:
				ret+="("+point['_comment']+")"
			if 'cmd' in point:
				ret+=point['cmd']
			if 'X' in point:
                                ret+="X%0.4f"%point['X']
			if 'Y' in point:
                                ret+="Y%0.4f"%point['Y']
			if 'Z' in point:
                                ret+="Z%0.4f"%point['Z']
			if 'I' in point:
                                ret+="I%0.4f"%point['I']
			if 'J' in point:
                                ret+="J%0.4f"%point['J']
			if 'K' in point:
                                ret+="K%0.4f"%point['K']
			if 'L' in point:
                                ret+="L%0.4f"%point['L']
			# the x, y, and z are not accurate as it could be an arc, or bezier, but will probably be conservative
			if 'F' in point:
				ret+="F%0.4f"%point['F']
			ret+="\n"
		return ret
 
	def render_path_scr(self, path, config):
		ret=''
		if '_closed' in path[0] and path[0]['_closed']:
			closed=True
		else:
			closed=False
		c=0
		for p,point in enumerate(path):
			if 'X' in point and 'Y' in point:
				if closed:
					ret+='WIRE 0 (%0.2f %0.2f) (%0.2f %0.2f)\n' % ( path[(p-1)%len(path)]['X'], path[(p-1)%len(path)]['Y'], point['X'], point['Y'])
				elif c:
					 ret+='WIRE 0 (%0.2f %0.2f) (%0.2f %0.2f)\n' % ( path[(p-1)%len(path)]['X'], path[(p-1)%len(path)]['Y'], point['X'], point['Y'])
				else:
					c=1
		return ret

	# this gets the feed rate we should be using considering that the cutter may be moving in both Z and horizontally. attempts to make it so that vertfeed and sidefeed are not exceeded.
	def get_feedrate(self, dx, dy, dz, config):
		ds = math.sqrt(dx**2+dy**2)
		if ds>0 and 'sidefeed' not in config or config['sidefeed']==0:
			print "ERROR trying to cut sideways with a cutter with no sidefeed"
		if dz>0 and 'vertfeed' not in config or config['vertfeed']==0:
			print "ERROR trying to cut down with a cutter with no vertfeed"
		dst = abs(ds/config['sidefeed'])
		dzt = abs(dz/config['vertfeed'])
		if dst>dzt:
			return math.sqrt(config['sidefeed']**2+(config['sidefeed']/ds*dz)**2)
		else:
			return math.sqrt(config['vertfeed']**2+(config['vertfeed']/dz*ds)**2)
		
	def add_feedrates(self, config):
		lastpos={'X':0,'Y':0,'Z':0}
		for c,cut in enumerate(self.output):
			if 'X' in cut:
				x=cut['X']-lastpos['X']
				lastpos['X']=cut['X']
			else:
				x=0
			if 'Y' in cut:
				y=cut['Y']-lastpos['Y']
				lastpos['Y']=cut['Y']
			else:
				y=0
			if 'Z' in cut:
				z=cut['Z']-lastpos['Z']
				lastpos['Z']=cut['Z']
			else:
				z=0

			if x!=0 or y!=0 or z!=0:
				cut['F']=self.get_feedrate(x,y,z,config)

	def add_colour(self, config):
		for cut in self.output:
			cut['_colour']=self.get_colour(config)
			if 'opacity' in config:
				cut['_opacity'] = config['opacity']
			if 'closed' in config:
				cut['_closed'] = config['closed']
	# get the colour this path should be cut in
	def get_colour(self,config):
		if 'forcecolour' in config and config['forcecolour']:
			if 'z1' in config and abs(config['z1'])>0 and 'thickness' in config and abs(config['thickness'])>0:
				if config['z1'] is False or abs(config['z1']) > config['thickness']:
					c=1
				else:
					c=int(abs(float(config['z1']))/float(config['thickness'])*255)
				if config['side']=='in':
					d="00"
				elif config['side']=='out':
					d='40'
				elif config['side']=='on':
					d='80'
				elif config['side']=='left':
					d='b0'
				else:
					d='f0'
				return "#"+format(c,'02x')+d+format(256-c, '02x')
				
		else:
				
			if 'colour' in config and config['colour'] is not False:
				return config['colour']
			else:
				return 'black'
	def output_path(self, pconfig):#z0=False,z1=False,side='on',direction=False, stepdown=False, downmode='down', transformations=False):
		""" output a path in whatever the config tells it - pconfig will be inherited from """
		# we want a new list for each call, to make it properly recusive
		self.output=[]
		config=pconfig #self.generate_config(pconfig)
		self.config=config
		mode=pconfig['mode']
		downmode=config['downmode']
		direction=config['direction']
		self.mode=mode
		self.Fsegments=[]
		self.Bsegments=[]
		self.make_segments(direction,self.Fsegments,config)
		self.make_segments(self.otherDir(direction),self.Bsegments,config)
# Runin/ ramp
		step,depths=self.get_depths(config['mode'], config['z0'], config['z1'], config['stepdown'])
		if len(depths)==0:
			return False
# if closed go around and around, if open go back and forth
		firstdepth=1
		if self.closed:
			self.runin(config['cutterrad'],config['direction'],config['downmode'],config['side'])
			segments=self.Fsegments
#			if downmode=='ramp'
#				self.add_out(self.Fsegments[-1].out(self.mode, depths[0]))
			for depth in depths:
				if downmode=='down':
					self.cutdown(depth)
				first=1
				for segment in segments:
					if first==1 and downmode=='ramp' and (mode=='gcode' or mode=='simplegcode'):
						if firstdepth and (mode=='gcode' or mode=='simplegcode'):
							self.add_out(self.quickdown(depth-step+config['precut_z']))
							firstdepth=0
						self.add_out(segment.out(direction,mode,depth-step,depth)) 
					else:
						self.add_out(segment.out(direction,mode))
					first=0
			# if we are in ramp mode, redo the first segment
			if downmode=='ramp' and mode=='gcode' or mode=='simplegcode':
				self.add_out(self.Fsegments[0].out(direction,mode))
			self.runout(config['cutterrad'],config['direction'],config['downmode'],config['side'])
		else:
			self.runin(downmode,self.side)
			d=True
			for depth in depths:
				if d:
					segments=self.Fsegments
				else:
					segments=self.Bsegments
				if downmode=='down':
					self.cutdown(depth)
				first=1
				for segment in segments:
					if first==1 and downmode=='ramp':
						if firstdepth and (mode=='gcode' or mode=='simplemode'):
							self.add_out(self.quickdown(depth-step+config['precut_z']))
							firstdepth=0
						self.add_out(segment.out(direction,mode,depth-step,depth))
					else:
						self.add_out(segment.out(direction,mode))
					first=0
					d= not d
			if downmode=='ramp':
				if d:
					self.add_out(self.Fsegments[0].out(direction,mode))
				else:
					self.add_out(self.Bsegments[0].out(direction,mode))
			self.runout(config['cutterrad'],config['direction'],config['downmode'],config['side'])
		# If we are in a gcode mode, go through all the cuts and add feed rates to them
		if self.mode=='gcode':
			self.add_out( [{"cmd":'G40'}])
		if self.mode=='gcode' or self.mode=='simplegcode':
			self.add_out([{'cmd':'G0','Z':config['clear_height']}])
			self.add_feedrates(config)
		elif self.mode=='svg':
			self.add_colour(config)	
	def quickdown(self,z):
		if self.mode=='gcode' or self.mode=='simplegcode':
			return [{"cmd":"G0", "Z":z}]
		else:
			return[]
		
	def cutdown(self,z):
		if self.mode=='gcode' or self.mode=='simplegcode':
			return [{"cmd":"G1", "Z":z}]
		else:
			return[]
	def add_out(self,stuff):
		if type(stuff) is list:
			self.output.extend(stuff)

	def move(self,moveto):
		if type(moveto) is not Vec:
			print self.trace
		else:
			if self.mode=='gcode' or self.mode=='simplegcode':
				return [{"cmd":"G0","X":moveto[0],"Y":moveto[1]}]
			elif self.mode=='svg':
				return [{"cmd":"M","x":moveto[0],"y":moveto[1]}]
	def setside(self,side, direction):
		if self.mode=='gcode':
			if side=='on':
				return [{"cmd":"G40"}]
#			if side=='in':
#				if direction=='cw':
#					return [{"cmd":"G42"}]
#				else:
#					return [{"cmd":"G41"}]
#			else:
#				if direction=='cw':
#					return [{"cmd":"G41"}]
#				else:
#					return [{"cmd":"G42"}]
	def cut_filled(self,z0=False,z1=False,side='on',dir=False):
		print "cut filled\n"
# find a tangent to the first segment of the path to allow the cutter to work
	def runin(self, cutterrad, direction, mode='down', side='on', ):
		#if self.isreversed:
		#	seg=0
	#		segments=self.Bsegments
	#		cutfrom=segments[seg].cutto
	#		cutto=segments[seg].cutfrom
	#		print "reversed"
	#	else:
		seg=0
		segments=self.Fsegments
		if len(self.Bsegments)==0:
			print self.trace
			print self.points
		cutto=segments[seg].cutto
		cutfrom=segments[seg].cutfrom
		if side=='on':
			self.start=cutfrom
			self.add_out(self.move(cutfrom))
		else:
			if(segments[seg].seg_type=='line'):
				diff = (cutto-cutfrom).normalize()
			
			if(segments[seg].seg_type=='arc'):
				centre=segments[seg].centre
				# find a normalized tangent to the line from the centre to the start point
				p=Point(V(0,0),'sharp')
				if direction=='cw' : 
					angle=90
				else:
					angle=-90
				diff= p.rotate((-centre+cutfrom), [V(0,0),angle])
				# we now need to find out if this is in the right direction
			#	sense = diff.cross(segments[seg].centre-segments[seg].cutfrom).z
			#	if sense[2]>0 and segments[seg].direction=='ccw' or sense[2]<0 and segments[seg].direction=='cw':
			#		diff=-diff

			self.start=cutfrom - diff * cutterrad

			self.add_out(self.move(cutfrom - diff * cutterrad))
			self.add_out(self.setside(side,direction))
			self.add_out(self.move(cutfrom))


	def runout(self, cutterrad, direction, mode='down', side='on', ):
		if self.mode=='gcode':
			return [{'cmd':'G40'}]

class Pathgroup(object):
	def __init__(self, **args):
		self.init( args)
		# List of paths and pathgroups
	def init(self,  args):
		global arg_meanings
		self.obType = "Pathgroup"
		self.paths=[]
		self.trace = traceback.extract_stack()
		self.varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth','forcestepdown', 'stepdown', 'forcecolour', 'rendermode','partial_fill','finishing','fill_direction','cutter','precut_z']
		self.otherargs=''
		for v in self.varlist:
			if v in args:
				setattr(self,v, args[v])
			else:
				setattr(self,v,None)
			self.otherargs+=':param v: '+arg_meanings[v]+"\n"
		self.output=[]
		self.parent=False
		self.comments=[]
		self.is_copy=False

	def __deepcopy__(self,memo):
		conf={}
		ret=copy.copy(self)#type(self)( **conf)
		for v in self.varlist:
			if v !='parent':
				setattr(ret, v, copy.deepcopy(getattr(self,v),memo))
#			conf[v]=copy.deepcopy(getattr(self,v),memo)
#		ret.parent=copy.copy(self.parent)
		ret.paths=copy.deepcopy(self.paths)
		for p in ret.paths:
			p.parent=ret
		return ret

	def get_config(self):
		if self.parent is not False:
			pconfig = self.parent.get_config()
		else:
			print "PATHGROUP has no parent HJK"+str(self)
			pconfig = False
		config = {}
		varslist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth', 'forcestepdown','stepdown', 'forcecolour','rendermode','partial_fill','finishing','fill_direction','cutter','precut_z']
		if pconfig is False or  pconfig['transformations'] is False or pconfig['transformations'] is None:
			config['transformations']=[]
		else:
			config['transformations']=pconfig['transformations'][:]
		if self.transform!=None:
			config['transformations'].append(self.transform)
		#	self.transform=None
                for v in varslist:
			if v !='transform' and v !='transformations':
                	        if getattr(self,v) is not None:
					config[v]=getattr(self,v)
                	        elif pconfig!=False and pconfig[v] is not None:
                	                config[v]=pconfig[v]
				else:
					config[v]=None
		return config

	def comment(self, comment):
		self.comments.append(str(comment))

	def get_comments(self, mode):
		ret=''
		if mode=='gcode' or mode=='simplegcode':
			for comment in self.comments:
				ret+="("+comment+")\n"
		elif mode=="svg":
			for comment in self.comments:
				ret+="<!-- "+comment+" -->\n"
		return ret
	def add(self,path):
		self.add_path(path)
	def add_path(self,path):
		try:
			path.obType
		except NameError:
			print "adding incorrect object to path"
		else:
			if (path.obType=='Path' or path.obType=="Pathgroup"):
				path.parent=self
				self.paths.append(path)
			else:
				print "Attempting to add a non-path or pathgroup to a pathgroup"
		return path	
# return a list of all the path gcode grouped by the ordering parameter
	def output_path(self, pconfig=False):
		# we want a new list for each call, to make it properly recusive
		gcode=[]
		for path in self.paths:
			try:
				path.obType
			except NameError:
				print "adding incorrect object to path"
			else:
				if  (path.obType=='Path'):
					path.output_path(pconfig)
					gcode.append(path.output)
				elif path.obType=='Pathgroup':
					paths = path.output_path(pconfig)
					gcode.extend(paths)
		return gcode

	def get_paths(self,config):
		paths=[]
		if hasattr(self,'__render__') and callable(self.__render__):
                        self.__render__(config)
		for p in self.paths:
			if p.obType=='Path':
				paths.append(p)
			elif p.obType=='Pathgroup':
				paths.extend(p.get_paths(config))
		return paths
	def render(self, pconfig):
		if hasattr(self,'__render__') and callable(self.__render__):
                        self.__render__(pconfig)
		paths = self.output_path( pconfig)
		ret={}
		comments=self.get_comments(pconfig['mode'])
		config=pconfig
		for path in paths:
			if path.obType=='Path':
				(k,p)=path.render(pconfig)
				if config['mode']=='svg':
					ret[p[0]]+="<g>\n"+p[1]+"</g>\n"
				else:
					ret[p[0]]+= p[1] #path.render_path(path,config)
			elif path.obType=='Pathgroup':
				for p in path.render(pconfig):
					if config['mode']=='svg':
	                                        ret[p[0]]+="<g>\n"+p[1]+"</g>\n"
					else:
						ret[p[0]]+= p[1]
		return ret
			
	def render_path(self,path,config):
		ret=""
		if config['mode']=='svg':
			ret+=self.render_path_svg(path)
		elif config['mode']=='gcode' or config['mode']=='simplegcode':
			ret+=self.render_path_gcode(path)+'G0Z%0.2f\n'%config['clear_height']
		return ret
		
	def render_path_svg(self,path):
		ret=""
		comments=""
		for point in path:
			if 'cmd' in point:
				ret+=" "+point['cmd']
			if 'rx' in point:
				ret+=" %0.2f"%point['rx']
			if 'ry' in point:
				ret+=",%0.2f"%point['ry']
			if '_rot' in point:
				ret+=" %0.0f"%point['_rot']
			if '_lf' in point:
				ret+=" %s"%point['_lf']
			if '_dir' in point:
				ret+=" %s"%point['_dir']
			if 'x' in point:
				ret+=" %0.2f"%point['x']
			if 'y' in point:
				ret+=",%0.2f"%point['y']
			if 'x2' in point:
				ret+=" %0.2f"%point['x2']
			if 'y2' in point:
				ret+=",%0.2f"%point['y2']
			if '_comment' in point:
				comments+="<!--"+point['_comment']+"-->\n"
			if '_colour' in point and point['colour'] is not None:
				colour=point['_colour']
			else:
				colour='black'
			if '_closed' in point and point['_closed']:
				z=' Z'
			else:
				z=''
		ret+=z
		return comments+"<path d=\""+ret+"\"  stroke-width='0.1px' fill='none' stroke='"+colour+"'/>\n"

	def render_path_gcode(self,path):
		ret=""
		for point in path:
			if '_comment' in point:
				ret+="("+point['_comment']+")"
			if 'cmd' in point:
				ret+=point['cmd']
			if 'X' in point:
                                ret+="X%0.2f"%point['X']
			if 'Y' in point:
                                ret+="Y%0.2f"%point['Y']
			if 'Z' in point:
                                ret+="Z%0.2f"%point['Z']
			if 'I' in point:
                                ret+="I%0.2f"%point['I']
			if 'J' in point:
                                ret+="J%0.2f"%point['J']
			if 'K' in point:
                                ret+="K%0.2f"%point['K']
			if 'L' in point:
                                ret+="L%0.2f"%point['L']
			if 'F' in point:
                                ret+="F%0.2f"%point['F']
			ret+="\n"
		return ret

	def rotate(self,pos, angle):
		if self.transform==False:
			self.transform={}
		self.transform['rotate']=[pos, angle]

	def translate(self,vec):
		if self.transform==False:
                        self.transform={}
                self.transform['translate']=vec


class Project(object):
	def __init__(name):
		self.name=name
		self.planes={}
	def add_plane(plane):
		self.planes[plane.name]=plane
		self.planes[plane.name].parent=self
class BOM(object):
	def __init__(self,name, number=1):
		self.name=name
		self.number=number
	def init(self):
		self.obType='BOM'

class BOM_part(BOM):
	def __init__(self,name, number=1, part_number=False, description=False, length=False):
		self.name=name
		self.number=number
		self.part_number=part_number
		self.description=description
		self.length=length
		self.init()
	def init(self):
		self.obType='BOM'
	def __str__(self):
		if self.length:
			return str(self.number)+'x '+str(self.length)+"mm of "+str(self.name)+' '+str(self.part_number)+" "+str(self.description)
		else:
			return str(self.number)+'x '+str(self.name)+' '+str(self.part_number)+" "+str(self.description)
class BOM_flat(BOM):
	def __init__(self, name, material, width, height, number, thickness):
		self.name=name
		self.material=material
		self.width=width
		self.height=height
		self.number=number
		self.thickness=thickness
		self.init()
	def __str__(self):
		return str(self.number)+'x '+str(self.name)+' in '+str(self.thickness)+"mm "+str(self.material)+" "+str(self.width)+"x"+str(self.height)
class BOM_rod(BOM):
	def __init__(self, name, material, xsection,  diameter, length, number=1):
		self.name=name
		self.material=material
		self.diameter=diameter
		self.length=length
		self.number=1
		self.description=description
		self.xsection=xsection
		self.init()
		return str(self.number)+'x '+str(self.name)+' in '+str(self.diameter)+"mm diameter "+str(material)+" "+str(xsection)+str(self.material)+" "+str(self.description)

class Part(object):
	"""This a part, if it is given a boudary and a layer it can be independantly rendered, if not it is just a collection of pathgroups, which can exist on specific layers
	"""
	def __init__(self,  **config):
		self.init(config)
	def init(self, config):
		self.obType = "Part"
		self.trace = traceback.extract_stack()
		self.paths = {}
		self.parts = []
		self.copies = []
		self.layer = False
		self.comments = []
		self.parent=False
		self.is_copy=False
		self.internal_borders=[]
		self.transform={}
		self.varlist = ['order','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth', 'forcestepdown','stepdown', 'forcecolour', 'border', 'layer', 'name','partial_fill','finishing','fill_direction','precut_z','ignore_border', 'material_shape', 'material_length', 'material_diameter']
		self.otherargs=''
		for v in self.varlist:
			if v in config:
				setattr(self,v, config[v])
			else:
				setattr(self,v,None)
			self.otherargs+=':param v: '+arg_meanings[v]+"\n"
		self.output=[]
		self.number=1
		if 'transform' in config:
			self.transform=copy.copy(config['transform'])
		if 'border' in config:
			self.add_border(config['border'])
		if not hasattr(self, 'cutoutside'):
			self.cutoutside = 'front'
		self.bom=[]
	def __deepcopy__(self,memo):
		conf={}
		for v in self.varlist:
			conf[v]=copy.deepcopy(getattr(self,v),memo)
		ret=type(self)( **conf)
		ret.parent=copy.copy(self.parent)
		for p in ret.paths:
			p.parent=ret
		for p in ret.parts:
			p.parent=ret
		return ret
	def add_bom(self,name, number=False, part_number=False, description=False, length=False):
		if type(name) is not str:
			if hasattr(name,'obType') and name.obType=='BOM':
				self.bom.append(name)
		else:
			self.bom.append(BOM_part(name, number, part_number, description, length))
	def get_bom(self,config={}):
		ret=[]
		if hasattr(self, 'layer') and self.layer is not None and self.parent is not None and self.parent is not False and self.parent.obType=='Plane':
			config=self.parent.get_layer_config(self.layer)
		config=self.overwrite(config, self.get_config())
		for part in self.parts:
			for b in part.get_bom(config):
				t=copy.copy(b)
				t.number*=self.number
				ret.append(t)
		for c in self.bom:
			t=copy.copy(c)
                        t.number*=self.number
                        ret.append(t)
		if hasattr(self,'material_shape') and (self.material_shape=='rod' or self.material_shape=='square_rod' or self.material_shape=='tube' or self.material_shape=='square_tube'):
			ret.append(BOM_rod(self.name, config['material'], config['material_shape'],  self.material_diameter, self.material_length, number=self.number))
		else:
			if hasattr(self, 'border') and self.border is not None:
				self.border.polygonise()
				bb=self.border.boundingBox
				ret.append(BOM_flat(self.name, config['material'], bb['tr'][0]-bb['bl'][0], bb['tr'][1]-bb['bl'][1], self.number, config['thickness']))
		return ret
	def comment(self,comment):
		self.comments.append(str(comment))
	def get_config(self):
		if self.parent is not False:
			pconfig = self.parent.get_config()
		else:
			pconfig = False
		
		config = {}
		if pconfig is None or pconfig is False or pconfig['transformations'] is None:
			config['transformations']=[]
		else:
			config['transformations']=pconfig['transformations'][:]
		if self.transform is not None:
			config['transformations'].append(self.transform)
		#	self.transform=None
                for v in self.varlist:
			if v !='transform' and v !='transformations':
                        	if hasattr(self,v) and getattr(self,v) is not None:
					config[v]=getattr(self,v)
				else:
					config[v]=None
		return config
	# is this a part we can render or just a multilayer pathgroup	
	def renderable(self):
		if not hasattr(self, 'border') or self.border is False or self.layer is False or self.border is None:
			return False
		else:
			return True

	def getParts(self):
		ret=[]
		for part in self.parts:
			ret.extend(part.getParts())
		if self.renderable():
			ret.append(self)
		return ret

	def get_parts(self):
		"""Returns a list of all the parts which can be rendered within this Part, not itself. Designed to be run from a Plane"""
		parts=[]
		for part in self.parts:
			if part.renderable():
				parts.append(part)
			
		return parts

	def add_border(self,path):
		"""Add a to act as the border of the part, anything outside this will be ignored"""
		#conpute bounding box for speed
		
		try:
			path.obType
		except NameError:
			print "Part border should be a path"
		else:
			#self.add_path(path,self.layer)
			self.border=copy.deepcopy(path)
			if self.border.side==None:
				self.border.side='in'
			self.border.parent=self
			self.is_border=True

	def add_internal_border(self,path):
		if hasattr(path,'obType') and path.obType=='Path':
			p=copy.deepcopy(path)
			p.is_border=True
			p.parent=self
			self.internal_borders.append(p)
			return path
		else:
			print "ERROR and internal border must be a path"
	def add_copy(self,copy_transformations):
		# would 
#		for t in copy_transformations:
			# TODO check this is a real transform
		self.copies.append(copy_transformations)
	def add(self, path, layers=False):
		self.add_path( path, layers)

	def add_path(self,path,layers = False):
		try:
			path.obType
		except NameError:
			print "adding incorrect object to path"
		else:
			if path.obType=='Part':
				path.parent = self
				self.parts.append(path)
				return path		
			elif (path.obType=='Path' or path.obType=="Pathgroup"):
				if layers is False:
					layers = [self.layer]
				if type(layers) is not list:
					layers = [layers]
				for layer in layers:
					# if layer is not used yet add a pathgroup and ant config
					if layer not in self.paths.keys():
						self.paths[layer] = Pathgroup()
						self.paths[layer].parent=self
#						self.paths[layer].parent=self
#						for v in self.varlist:
#							if hasattr(self,v):
#								setattr(self.paths[layer],v,getattr(self,v))

# deepcopy problem:
					p=copy.deepcopy(path)
					p.parent=self.paths[layer]
					path.parent=self.paths[layer]
					self.paths[layer].add_path(p)
				return p

			else:
				print "Attempting to add a non-path or pathgroup to a pathgroup"
	# flatten the parts tree
	def get_layers(self):
		layers={}
		for part in self.parts:
			
			# find all the contents of layers
			part.mode=self.mode
			ls=part.get_layers()
			if(ls is not False and ls is not None):
				for l in ls.keys():
					if l not in layers:
						layers[l]=[]
					# if the part should be copied, copy its parts which aren't in its core layer
					# This means you can add an object in lots of places and mounting holes will be drilled
					if not hasattr(part,'layer') or part.layer==False or l!=part.layer or hasattr(self, 'callmode') and milling.mode_config[self.callmode]['overview']:
						for copytrans in part.copies:
							for p in ls[l]:
								t=copy.deepcopy(p)
								t.is_copy=True		
								t.transform=copytrans
								layers[l].append(t)
					#if not hasattr(part,'layer') or part.layer==False or l!=part.layer:# or milling.mode_config[self.mode]['overview']:
					layers[l].extend(ls[l])

		for l in self.paths.keys():
			if not hasattr(self,'layer') or self.layer==False or l != self.layer:
				self.paths[l].parent=self
				if l not in layers:
					layers[l]=[]
				layers[l].append(self.paths[l])
		return layers

	def get_own_paths(self,config):
                paths=[]
		if hasattr(self, 'layer') and self.layer is not False and self.layer  in self.paths:
	                for p in self.paths[self.layer].paths:
				if p.obType=='Path':
					paths.append(p)
				elif p.obType=='Pathgroup':
					paths.extend(p.get_paths(config))
		paths.extend(self.internal_borders)
                return paths



	def contains(self,path):
		if self.border.contains(path) >-1:
			if len(self.internal_borders):
				for ib in self.internal_borders:
					if ib.contains(path)!=-1:
						return -1
			return 1
		return -1

	def overwrite(self,ain,b):
                a=copy.copy(ain)

		for i in b.keys():
			if i!='transformations':
				if i in b and b[i] is not False and b[i] is not None:
					a[i] = b[i]
				elif (i not in a or a[i] is False or a[i] is None ) or i not in a:
					a[i] =None
		if 'transformations' not in a or type(a['transformations']) is not list:
			if 'transform' in a:
				a['transformations']=[a['transform']]
			else:
				a['transformations']=[]
		if 'transformations' in b and type(b['transformations']) is list:
			a['transformations'].extend(b['transformations'])
		if 'transform' in b and b['transform'] is not False and b['transform'] is not None:
		#	if type(b['transform']) is list:			
			a['transformations'].append(b['transform'])
		return a

# stores a series of parts which can overlap in layers
class Plane(Part):
	def __init__(self,name, **config):
		if 'plane' not in config:
			plane=V(0,0,1)
		else:
			plane=config['plane']
		if 'origin' not in config:
			origin=V(0,0,1)
		else:
			origin=config['origin']
		self.init(name,origin,plane, config)

	def init(self,name,origin=V(0,0,0), plane=V(0,0,1), config=False):
		self.layers={}
		self.origin=origin
		self.plane='Plane'
		self.parts=[]
		self.config={}
		self.paths={}
		self.obType='Plane'
		self.name=name
		self.transform=False
		self.parent=False
		self.varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth', 'forcestepdown','stepdown', 'forcecolour', 'border', 'layer','partial_fill','finishing','fill_direction','precut_z']
		self.out=''
		self.bom=[]
		self.number=1
		for v in self.varlist:
                        if v in config:
				self.config[v]=config[v]
                        else:
				self.config[v]=False
	# A plane can have several layers
	def add_layer(self,name, material, thickness, z0=0,zoffset=0, add_back=False, isback=False, colour=False):
		if add_back:
			self.layers[name+'#back'] = Layer(name,material, thickness, z0, zoffset, isback=True, back=name, colour=colour)
			self.layers[name] = Layer(name,material, thickness, z0, zoffset, isback=False, back=name+'#back', colour=colour)
		else:	
			self.layers[name] = Layer(name,material, thickness, z0, zoffset, isback=isback, colour=colour)
	def render_layer(self,layer):
		"""Render all the parts in a layer"""
	
	def render_all(self,mode,config):
		"""Render all parts in the Plane"""
		for part in self.getParts():
			self.render_part(part, mode,config)
	def list_all(self):
		for part in self.getParts():
			if hasattr(part, 'name'):
				print str(part.name)
 	
	def get_layer_config(self,layer):
		return self.layers[layer].config

	def render_part(self,part, callmode,pconfig=False):
		self.callmode = callmode
		self.modeconfig=milling.mode_config[callmode]
		self.mode=self.modeconfig['mode']
		self.modeconfig['callmode']=callmode
		self.callmode=callmode
		layers = self.get_layers()
		output={} # collections.OrderedDict()
		c=0
		lastcutter=False
		config=copy.copy(self.modeconfig)
		if pconfig is not False:
			config=self.overwrite(config,pconfig)
		config=self.overwrite(config,self.config)
		if part.layer in layers and part.layer is not False and part.layer is not None:
			paths=layers[part.layer]
			config.update(self.get_layer_config(part.layer))
		elif part.layer is not False and part.layer is not None:
			paths=[]
			config.update(self.get_layer_config(part.layer))
		else:
			paths=[]
		# if we are looking at a back layer and we are in a cutting mode then mirror the image
		if part.layer in self.layers and self.layers[part.layer].config['isback'] is True and config['mirror_backs'] is True:
			if 'transformations' in config and config['transformations'] is list:
				config['transformations'].insert(0,{'mirror':[V(0,0),'x']})
			else:
				config['transformations']=[{'mirror':[V(0,0),'x']}]
		# if it has been set to layer 'all' it should be in here
		if 'all' in layers:
			paths.extend(layers['all'])
		paths.extend(part.get_own_paths(config))
		
		# iterate through all the paths in the part's layer
		for path in paths:
			
		# if the path is within the bounds of the part then render it
			if path.obType=="Path" or path.obType=="Part":
				if not hasattr(part, 'border') or part.border is None or part.ignore_border or  part.contains(path)>-1 or hasattr(path,'is_border') and path.is_border:
					(k,pa)=path.render(config)
					if self.modeconfig['group'] is False:
						k=c
						c=c+1
					#else:
					#	k=getattr(path,self.modeconfig['group'])
					#	if (k==False or k==None) and self.modeconfig['group']=='cutter':
					#		k=config['cutter']
					if k not in output.keys():
						output[k]=''
					output[k]+=''.join(pa)
					lastcutter=k
			if path.obType=="Pathgroup":
				for p in path.get_paths(config):
					if not hasattr(part, 'border') or part.ignore_border or part.contains(p)>-1:
						(k,pa)=p.render(config)
						if self.modeconfig['group'] is False:
							k=c
							c=c+1
						#else:
						#	k=config[self.modeconfig['group']]#getattr(p,self.modeconfig['group'])
						if k not in output.keys():
							output[k]=''
						output[k] += ''.join(pa)
						lastcutter = k
					
				# this may be a pathgroup - needs flattening - needs config to propagate earlier or upwards- drill a hole of non-infinite depth through several layers??
				# possibly propagate config by getting from parent, plus feed it a layer config as render arguement
				# make list of rendered paths with metadata, so possibly can sort by cutter
		out=''
		if(part.border is not False and part.border is not None):
			(k,b)=part.border.render(config)

			if self.modeconfig['mode']=='gcode' or self.modeconfig['mode']=="simplegcode":
				if part.cutter==None:
					part.cutter=config['cutter']
				if not config['sep_border']: #1==1 or part.cutter == lastcutter:
					if self.modeconfig['mode'] == 'scr':
						output[k] += "LAYER " + str(self.modeconfig[k])+"\n"
					if not k in output:
						output[k]=''
					output[k]+=b
				else:
					if self.modeconfig['mode'] == 'scr':
						output[k] += "LAYER " + str(self.modeconfig['border_layer'])+"\n"
					output['__border']=b
			else:
				if self.modeconfig['mode'] == 'scr':
					output['__border'] = "LAYER " + str(self.modeconfig['border_layer'])+"\n"
				else:
					output['__border'] = ''
				output['__border']+=b
		for key in sorted(output.iterkeys()):
			if self.modeconfig['mode']=='gcode' or self.modeconfig['mode']=="simplegcode":
				self.writeGcodeFile(part.name,key,output[key], config)
			elif self.modeconfig['mode']=='svg':
				out+="<!-- "+str(part.name)+" - "+str(key)+" -->\n"+output[key]
			elif self.modeconfig['mode']=='scr':
				out+='\n\n'+output[key]
		if self.modeconfig['mode']=='svg' or self.modeconfig['mode']=='scr':	
		#	f=open(parent.name+"_"+self.name+"_"+part.name)
			if self.modeconfig['label'] and  self.modeconfig['mode'] == 'svg':
				out+="<text transform='scale(1,-1)' text-anchor='middle' x='"+str(int(part.border.centre[0]))+"' y='"+str(-int(part.border.centre[1]))+"'>"+str(part.name)+"</text>"
			if self.modeconfig['overview']:
				self.out+='<g>'+out+'</g>'
			elif part.name is not None:
				filename=self.name+"_"+part.name+config['file_suffix']
				f=open(filename,'w')
				f.write( self.modeconfig['prefix'] + out + self.modeconfig['postfix'] )
				f.close()

	def writeGcodeFile(self,partName, key, output, config):
		filename=str(partName)+"_"+str(self.name)+"_"+str(key)
		if len(config['command_args']):
			for k in config['command_args'].keys():
				filename=k+"_"+filename+"-"+config['command_args'][k]	
		if 'cutter' in config:
			filename+="_cutter-"+str(config['cutter'])
		if 'material' in config:
			filename+='_'+str(config['material'])
		if 'thickness' in config:
			filename+="_thickness-"+str(config['thickness'])
		if 'repeatmode' in config:
			repeatmode=config['repeatmode']
		else:
			repeatmode='regexp'
		if 'repeatx' in config and 'repeaty' in config and 'xspacing' in config and 'yspacing' in config:
			output2=''
			if repeatmode=='gcode':
				for y in range(0,int(config['repeaty'])):
					output2+='\nG0X0Y0\nG10 L20 P1'+'Y%0.4f'%(float(config['yspacing']))
					output2+='X%0.4f\n'%(-(float(config['repeatx'])-1)*float(config['xspacing']))
					c=0
					for x in range(0,int(config['repeatx'])):
						if c==0:
							c=1
						else:
							output2+='\nG0X0Y0\nG10 L20 P1'+'X%0.4f'%(float(config['xspacing']))
							output2+='G54\n'
						output2+=output
			elif repeatmode=='regexp':
				# one approach is to just grep through for all Xnumber or Ynumbers and add an offset. This works as I and J are relative unless we do something cunning
				xreg=re.compile('X[\d\.-]+')
				yreg=re.compile('Y[\d\.-]+')
				for y in range(0,int(config['repeaty'])):
					for x in range(0,int(config['repeatx'])):
						tempoutput=output
						matches = xreg.findall(tempoutput)
						for match in matches:
							if len(match):
								val=float(match[1::])
								val+=x*float(config['xspacing'])
								tempoutput=tempoutput.replace(match,'X'+str(val))
						matches=yreg.findall( tempoutput)
                                                for match in matches:
                                                        if len(match):
                                                                val=float(match[1::])
                                                                val+=y*float(config['yspacing'])
                                                                tempoutput=tempoutput.replace(match,'Y'+str(val))
						output2+=tempoutput
		#	output2+='\nG10 L2 P1 X0 Y0\n'
			filename+='_'+str(config['repeatx'])+'x_'+str(config['repeaty'])+'y'
			output=output2
		# if we are making gcode we we should have tool changes in there
		if config['mode']=='gcode':
			toolid=str(milling.tools[config['cutter']]['id'])
			output = "\n"+config['settool_prefix']+toolid+config['settool_postfix']+"\n"+output
		f=open(self.sanitise_filename(filename+config['file_suffix']),'w')
		f.write(config['prefix']+output+config['postfix'])
		f.close()
		if 'dosfile' in config and config['dosfile']:
			os.system("/usr/bin/unix2dos "+self.sanitise_filename(filename+config['file_suffix']))
			
	def sanitise_filename(self,filename):
		return "".join(x for x in filename if x.isalnum() or x in '-._')
class Layer(object):
	def __init__(self,name, material, thickness, z0, zoffset, back=False, isback=False, colour=False):
		self.config={}
		self.config['name']=name
		self.config['material']=material
		self.config['z0']=z0
		self.config['thickness']=thickness
		self.config['zoffset']=zoffset
		# layer that is the other side of this
		self.config['back']=back
		# layer should be mirrored when cut
		self.config['isback']=isback
		self.config['colour']=colour
		self.bom=[]
	def get_config(self):
		return self.config

