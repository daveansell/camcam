import os
import math
from minivec import Vec, Mat
import Milling
import pprint
import copy
import collections
import traceback

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
		'fill_direction':'direction to fill towards',
		'precut_z':'the z position the router can move dow quickly to',
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
			if zfrom!=zto:
				temp[0]['Z']=zto
			return temp
		elif mode=='simplegcode':
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
			for t in transformations:
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
#		print side
#		print cutter
		self.transform=False
		self.otherargs=''
		self.varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter', 'partial_fill']
		for v in self.varlist:
			if v in config:
				setattr(self,v, config[v])
			else:
				setattr(self,v, None)
			self.otherargs+=':param v: '+arg_meanings[v]+"\n"
		self.start=False
		self.extents= {}	
		self.output=[]
		self.parent=False
		self.comment("start:"+str(type(self)))
	
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

	def overwrite(self,a,b):
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
	def add_points(self,points):
		for p in points:
			if type(p) is Point:
				self.points.append(p)
			else:
				print "add_points - adding a non-point"
	def transform_pointlist(self, pointlist,transformations):
		pout=[]
		for p in pointlist:
			pout.append(p.point_transform(transformations))
		return pout

	def make_segments(self, direction,segment_array,config):
		pointlist = self.transform_pointlist(self.points,config['transformations'])
		if direction!=self.find_direction():
			pointlist.reverse()
			# this is in the wrong sense as it will be run second in the reversed sense
			self.isreversed=0
		else:
			self.isreversed=1
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
					print "ERROR - straight arc"
					tempd='cw'	
				if do:
					segment_array.append(Arc(startcurve, endcurve, centre,tempd))
			frompoint=endcurve
		elif thispoint.point_type=='clear':
			# we want to cut so that the edge of the cutter just touches the point requested
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
		elif thispoint.point_type=='arc':
			# draw an arc between two points or radius radius - they should both have the same radius
			if nextpoint.point_type=='arcend' and lastpoint.point_type=='arcend':
				centre=self.findArcCentre(lastpoint.pos,nextpoint.pos, thispoint.radius, thispoint.direction)
				segment_array.append(Arc(frompoint, thispoint.pos, centre,thispoint.direction))
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
			print "outcutve lastpoint"+str(lastpoint.pos)+" thispoint"+str(thispoint.pos)+" nextpoint"+str(nextpoint.pos)
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
#					if( abs((thispoint.pos-p2[0]).length()-thispoint.radius)>0.1 or abs((thispoint.pos-p1[1]).length()-thispoint.radius)>0.1):
#						print "Arc1:"+str(p1[1])+","+str(p2[0])+','+str(thispoint.pos)+' '+d2+" r"+str((thispoint.pos-p1[1]).length())+" r"+str((thispoint.pos-p2[0]).length())
#						print thispoint.radius
#						print nextpoint.pos
					segment_array.append( Arc( p1[1],p2[0], thispoint.pos, self.otherDir(d2)))
				frompoint=p2
			else:
				
				p2 = self.tangent_point(nextpoint.pos, thispoint.pos, thispoint.radius, self.otherDir(d2))
				if do:
#					if( abs((thispoint.pos-p2).length()-thispoint.radius)>0.1 or abs((thispoint.pos-p1[1]).length()-thispoint.radius)>0.1):
#						print "Arc2:"+str(p1[1])+","+str(p2)+','+str(thispoint.pos)+' '+d2+" r"+str((thispoint.pos-p1[1]).length())+" r"+str((thispoint.pos-p2).length())
#						print thispoint.radius
#						print lastpoint.pos
#						print thispoint.pos
#						print nextpoint.pos
					segment_array.append( Arc( p1[1],p2, thispoint.pos, self.otherDir(d2)))
				frompoint=p2
				
			#	frompoint = #rerun tangent points for next pair of points...
		elif thispoint.point_type=='circle':
			if do:
				segment_array.append(Arc(V(thispoint.pos[0]-thispoint.radius, thispoint.pos[1]),V(thispoint.pos[0]+thispoint.radius, thispoint.pos[1]), thispoint.pos,'cw'))
				segment_array.append(Arc(V(thispoint.pos[0]+thispoint.radius, thispoint.pos[1]),V(thispoint.pos[0]-thispoint.radius, thispoint.pos[1]), thispoint.pos,'cw'))
		return frompoint

	def findArcCentre(frompos, topos, radius, direction):
		l=(topos-frompos)/2
		if l.length()>radius/2:
			print "ERROR arc radius less than distance to travel"
		if direction=='cw':
			a=90
		else:
			a=-90
		return (topos+frompos)/2+rotate(l,a)

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
			print "r1>r2 "+str(r1)+" "+str(r2)
			r=r1-r2
			temp=self.tangent_point(point2, point1, r, self.otherDir(dir1))
			rvec=(temp-point1).normalize()
			#print "rvec"+str(rvec)
			return [point1+rvec*r1, point2+rvec*r2]
		elif r1<r2:
			print "r1<r2 "+str(r1)+" "+str(r2)
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
		thisdir=self.find_direction()
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
			if thisdir=='cw':
				side='right'
			else:
				side='left'
		elif side=='out':
			if thisdir=='cw':
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
#	if al=0:
#		print "ERROR from a tn points are the same"
#		print self.trace
#		print thispoint.pos, 
			
#	ca=math.sqrt(4/al/al -1)
		angle=math.atan2(a[1], a[0])
		if cross<0 and side=='left' or cross>0 and side=='right':
			corner='external'
#			print "EXTERNAL"+str(side)+" "+str(cross)+" "+str(thisdir)+" "+str(side)
		else:
			corner='internal'
#			print "INTERNAL"+str(side)+" "+str(cross)+" "+str(thisdir)+" "+str(side)
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
				t.pos = self.offset_move_point(thispoint.pos, lastpoint.pos, nextpoint.pos, frompos, topos, side, -distance/abs(math.cos(angle)))
			else:
				if t.radius>distance:
					t.radius-=distance
					t.pos = self.offset_move_point(thispoint.pos, lastpoint.pos, nextpoint.pos, frompos, topos, side, distance/abs(math.cos(angle)))
				else:
					t.point_type='doubleclear'
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
			if lastpoint=='arc':
				c=self.findArcCentre(beforelastpoint.pos, thispoint.pos, lastpoint.radius, lastpoint.direction)
				rvec=(thispoint.pos-c).normalize()
				if lastpoint.direction=='cw':
					a=-90
				else:
					a=90
				invec=rotate(rvec,a)
			else:
				invec=thispoint.pos-lastpoint.pos

			if nextpoint=='arc':
				c=self.findArcCentre(thispoint.pos, afternextpoint.pos, nextpoint.radius, nextpoint.direction)
				rvec=(thispoint.pos-c).normalize()
				if nextpoint.direction=='cw':
					a=-90
				else:
					a=90
				outvec=rotate(rvec,a)
			else:
				outvec=nextpoint.pos-lastpoint.pos	
			t.pos = self.offset_move_point(thispoint.pos, thispoint.pos-invec, thispoint.pos+outvec, frompos, topos, side, distance)
		elif thispoint.point_type=='arc':
			if side=='left' and thispoint.direction=='cw' or side=='right' and thispoint.direction=='ccw':
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
#		print "offse_move_point"+str(distance)
#		print vecin
#		print vecout
		# Find average direction of two vectors
		avvec=(vecin-vecout).normalize()
		# then rotate it 90 degrees towards the requested side
		return -avvec*distance+thispos
#		return rotate(avvec*distance,a)*2+thispos

# find whether the path is setup clockwise or anticlockwise
	def find_direction(self):
		total =V(0,0,0)
		first = True
		for p,q in enumerate(self.points):
			total+=(self.points[p].pos-self.points[(p-1)%len(self.points)].pos).normalize().cross((self.points[(p+1)%len(self.points)].pos-self.points[p].pos).normalize())
		if(total[2]>0):
			return 'ccw'
		else:
			return 'cw'
	
	def cut_direction(self,side='on'):
		if side=='in':
			return 'ccw'
		else:
			return 'cw'

	
	# converts a shape into a simple polygon
	def polygonise(self,resolution=5):
		ret=[]
		self.Fsegments=[]
		config=self.generate_config({'cutterrad':0})
		self.make_segments('cw',self.Fsegments,config)
		for s in self.Fsegments:
			ret.extend(s.polygon(resolution))
		return ret
 
	def contains(self,other):
		if other.obType=="Point":
			if self.contains_point(other, thispolygon):
				return 1
			else:
				return -1
		elif other.obType=="Path" or other.obType=="Part":
			if other.obType=="Part":
				otherpolygon = other.border.polygonise()
			else:
				otherpolygon = other.polygonise()
			thispolygon = self.polygonise()
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
			self.transform=None
		self.varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode', 'stepdown','forcestepdown', 'mode','partial_fill','fill_direction','precut_z']
                for v in self.varlist:
                        if hasattr(self,v) and getattr(self,v) is not None:
				config[v]=getattr(self,v)
                        elif pconfig is not False and v in pconfig and pconfig[v] is not None:
                                config[v]=pconfig[v]
			else:
				config[v]=None
		return config

	def generate_config(self, pconfig):
		config={}
		self.overwrite(config,pconfig)
		inherited = self.get_config()
#		if('transformations' in config):
		self.overwrite(config, inherited)
#		if('transformations' in config):
#		for k in inherited.keys():
 #                       if (config[k] is None or config[k] is False) and k in pconfig:
  #                              config[k]=pconfig[k]
		self.set_cutter(config)
		self.set_material(config)
		thisdir=self.find_direction()
		if 'direction' not in config or config['direction'] is False:
			if hasattr(self,'direction') and  self.direction!=False:
				config['direction']=self.direction
			elif(config['side'] =='in'):
				config['direction']='cw'
			elif(config['side'] =='out'):
				config['direction']='ccw'
			else:
				config['direction']=thisdir
		if config['side'] is None or config['side'] is False:
			config['side']='on' 
		if config['z0'] is None or config['z0'] is False:
			config['z0']=0
		if (config['z1'] is False or config['z1'] is None) and config['z0'] is not None and config['thickness'] is not None:
			config['z1'] = config['z0'] - config['thickness']
		return config
#  output the path
	def render(self,pconfig):
# Do something about offsets manually so as not to rely on linuxcnc
		config=self.generate_config(pconfig)
		if config['side']=='in' or config['side']=='out':
			c =copy.copy(config)
			c['opacity']=0.5
			thepath=self.offset_path(c['side'],c['cutterrad'],c)
			thepath.output_path(c)
			c['side']='on'
			if config['hide_cuts']:
				self.output_path(config)
				out = self.render_path(self,config)
			elif config['overview']:
				self.output_path(config)
				out = thepath.render_path(thepath,c) + self.render_path(self,config)
			else:
				out = thepath.render_path(thepath,config)
		else:
			thepath=self
			thepath.output_path(config)
			out = thepath.render_path(self,config)

		if not config['hide_cuts']  and 'partial_fill' in config and config['partial_fill']>0:
			dist=config['partial_fill']-config['cutterrad']
			numpasses = math.ceil(float(dist)/ config['cutterrad']/0.9)
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
			for d in range(1,int(numpasses)):
				fillpath=thepath.offset_path(ns, step*d, c)
				fillpath.output_path(c)
				out += fillpath.render_path(fillpath,c)
		return out

	def render_path(self,path,config):
		ret=""
		if config['mode']=='svg':
			ret+=self.render_path_svg(self.output,config)
		elif config['mode']=='gcode' or config['mode']=='simplegcode':
			ret+=self.render_path_gcode(self.output,config)
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
				print "COLOUR"+str(colour)
			else:
				colour='black'
			if '_opacity' in point:
				opacity = "opacity:"+str(point['_opacity'])
			else:
				opacity = "opacity:1"
		return comments+"<path d=\""+ret+"\"  style='stroke-width:0.1px;"+opacity+"' fill='none' stroke='"+colour+"'/>\n"

	def render_path_gcode(self,path,config):
		ret=""
		for point in path:
			if '_comment' in point and config['comments']:
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
			# the x, y, and z are not accurate as it could be an arc, or bezier, but will probably be conservative
			if 'F' in point:
				ret+="F%0.2f"%point['F']
			ret+="\n"
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
		for cut in self.output:
			if 'X' in cut:
				x=cut['X']
			else:
				x=0
			if 'Y' in cut:
				y=cut['Y']
			else:
				y=0
			if 'Z' in cut:
				z=cut['Z']
			else:
				z=0
			if x!=0 or y!=0 or z!=0:
				cut['F']=self.get_feedrate(x,y,z,config)

	def add_colour(self, config):
		for cut in self.output:
			cut['_colour']=self.get_colour(config)
			if 'opacity' in config:
				cut['_opacity']=config['opacity']
	# get the colour this path should be cut in
	def get_colour(self,config):
		if 'forcecolour' in config and config['forcecolour']:
			if 'z1' in config and abs(config['z1'])>0 and 'thickness' in config and abs(config['thickness'])>0:
				if config['z1'] is False or abs(config['z1']) > config['thickness']:
					c=1
				else:
					c=int(abs(float(config['z1']))/float(config['thickness'])*255)
				print "COLOUrget "+str(c)
				return "#"+format(c,'02x')+"00"+format(256-c, '02x')
				
		else:
				
			if 'colour' in config and config['colour'] is not False:
				return config['colour']
			else:
				return 'black'
	def output_path(self, pconfig):#z0=False,z1=False,side='on',direction=False, stepdown=False, downmode='down', transformations=False):
		""" output a path in whatever the config tells it - pconfig will be inherited from """
		# we want a new list for each call, to make it properly recusive
		config=self.generate_config(pconfig)
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
				
#			if downmode=='ramp'
#				self.add_out(self.Fsegments[-1].out(self.mode, depths[0]))
			for depth in depths:
				if downmode=='down':
					self.cutdown(depth)
				first=1
				for segment in self.Fsegments:
					if first==1 and downmode=='ramp':
						if firstdepth and (mode=='gcode' or mode=='simplemode'):
							self.add_out(self.quickdown(depth-step+config['precut_z']))
							firstdepth=0
						self.add_out(segment.out(direction,mode,depth-step,depth)) 
					else:
						self.add_out(segment.out(direction,mode))
					first=0
			# if we are in ramp mode, redo the first segment
			if downmode=='ramp':
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
#		print self.output
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
		if self.isreversed:
			seg=0
			segments=self.Bsegments
			cutfrom=segments[seg].cutto
			cutto=segments[seg].cutfrom
		else:
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
	#	print "runout"
		if self.mode=='gcode':
	#		print "runout2"
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
		self.varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth','forcestepdown', 'stepdown', 'forcecolour', 'rendermode','partial_fill','fill_direction','cutter','precut_z']
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

	def __deepcopy__(self,memo):
		conf={}
		ret=copy.copy(self)#type(self)( **conf)
		for v in self.varlist:
			if v !='parent':
				setattr(ret, v, copy.deepcopy(getattr(self,v),memo))
#			conf[v]=copy.deepcopy(getattr(self,v),memo)
#		ret.parent=copy.copy(self.parent)
		return ret

	def get_config(self):
		if self.parent is not False:
			pconfig = self.parent.get_config()
		else:
			print "PATHGROUP has no parent HJK"+str(self)
			pconfig = False
		config = {}
		varslist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth', 'forcestepdown','stepdown', 'forcecolour','rendermode','partial_fill','fill_direction','cutter','precut_z']
		if pconfig is False or  pconfig['transformations'] is False or pconfig['transformations'] is None:
			config['transformations']=[]
		else:
			config['transformations']=pconfig['transformations'][:]
		if self.transform!=None:
			config['transformations'].append(self.transform)
			self.transform=None
                for v in varslist:
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
#					pprint.pprint(groups) 
					gcode.extend(paths)
		return gcode

	def get_paths(self):
		paths=[]
		for p in self.paths:
			if p.obType=='Path':
				paths.append(p)
			elif p.obType=='Pathgroup':
				paths.extend(p.get_paths())
		return paths
	def render(self, pconfig):
		paths = self.output_path( pconfig)
		ret=self.get_comments(pconfig['mode'])
		config=pconfig
		for path in paths:
			if config['mode']=='svg':
				ret+="<g>\n"+path.render_path(path,config)+"</g>\n"
			else:
				ret+= path.render_path(path,config)
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
		self.internal_borders=[]
		self.varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth', 'forcestepdown','stepdown', 'forcecolour', 'border', 'layer', 'name','partial_fill','fill_direction','precut_z']
		self.otherargs=''
		for v in self.varlist:
			if v in config:
				setattr(self,v, config[v])
			else:
				setattr(self,v,None)
			self.otherargs+=':param v: '+arg_meanings[v]+"\n"
		self.output=[]
		self.transformations=[]
		if 'border' in config:
			self.add_border(config['border'])
		if not hasattr(self, 'cutoutside'):
			self.cutoutside = 'front'

	def __deepcopy__(self,memo):
		conf={}
		for v in self.varlist:
			conf[v]=copy.deepcopy(getattr(self,v),memo)
		ret=type(self)( **conf)
		ret.parent=copy.copy(self.parent)
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
			self.transform=None
                for v in self.varlist:
                        if hasattr(self,v) and getattr(self,v) is not None:
				config[v]=getattr(self,v)
			else:
				config[v]=None
		return config
	# is this a part we can render or just a multilayer pathgroup	
	def renderable(self):
		if self.border is False or self.layer is False or self.border is None:
			return False
		else:
			return True

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
			self.border.parent=self

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
					if not hasattr(part,'layer') or part.layer==False or l!=part.layer or milling.mode_config[self.callmode]['overview']:
						for copytrans in part.copies:
							for p in ls[l]:
								t=copy.deepcopy(p)
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

	def get_own_paths(self):
                paths=[]
		if hasattr(self, 'layer') and self.layer is not False and self.layer  in self.paths:
	                for p in self.paths[self.layer].paths:
				if p.obType=='Path':
					paths.append(p)
				elif p.obType=='Pathgroup':
					paths.extend(p.get_paths())
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
		self.varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth', 'forcestepdown','stepdown', 'forcecolour', 'border', 'layer','partial_fill','fill_direction','precut_z']
		self.out=''
		for v in self.varlist:
                        if v in config:
				self.config[v]=config[v]
                        else:
				self.config[v]=False
	def overwrite(self,a,b):
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
	# A plane can have several layers
	def add_layer(self,name, material, thickness, z0=0,zoffset=0, add_back=False, isback=True, colour=False):
		if add_back:
			self.layers[name+'#back'] = Layer(name,material, thickness, z0, zoffset, isback=True, back=name, colour=colour)
			self.layers[name] = Layer(name,material, thickness, z0, zoffset, isback=False, back=name+'#back', colour=colour)
		else:	
			self.layers[name] = Layer(name,material, thickness, z0, zoffset, isback=isback, colour=colour)
	def render_layer(self,layer):
		"""Render all the parts in a layer"""
	
	def render_all(self,mode):
		"""Render all parts in the Plane"""
		for part in self.parts:
			self.render_part(part, mode)
	def list_all(self):
		for part in self.parts:
			if hasattr(part, 'name'):
				print str(part.name)
 	
	def get_layer_config(self,layer):
		return self.layers[layer].config

	def render_part(self,part, callmode):
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
		self.overwrite(config,self.config)
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
		paths.extend(part.get_own_paths())
		
		# iterate through all the paths in the part's layer
		for path in paths:
			
		# if the path is within the bounds of the part then render it
			if path.obType=="Path" or path.obType=="Part":
				if not hasattr(path, 'border') or part.contains(path)>-1 or hasattr(path,'is_border') and path.is_border:
					if self.modeconfig['group'] is False:
						k=c
						c=c+1
					else:
						k=getattr(path,self.modeconfig['group'])
						if (k==False or k==None) and self.modeconfig['group']=='cutter':
							k=config['cutter']
					if k not in output.keys():
						output[k]=''
					output[k]+=''.join(path.render(config))
					lastcutter=k
			if path.obType=="Pathgroup":
				for p in path.get_paths():
					if not hasattr(path, 'border') or part.contains(p)>-1:
						if self.modeconfig['group'] is False:
							k=c
							c=c+1
						else:
							k=config[self.modeconfig['group']]#getattr(p,self.modeconfig['group'])
						if k not in output.keys():
							output[k]=''
						output[k]+=''.join(p.render(config))
						lastcutter=k
					
				# this may be a pathgroup - needs flattening - needs config to propagate earlier or upwards- drill a hole of non-infinite depth through several layers??
				# possibly propagate config by getting from parent, plus feed it a layer config as render arguement
				# make list of rendered paths with metadata, so possibly can sort by cutter
		out=''
		if(part.border is not False and part.border is not None):
			b=part.border.render(config)
			if self.modeconfig['mode']=='gcode' or self.modeconfig['mode']=="simplegcode":
				if part.cutter==None:
					part.cutter=config['cutter']
				if part.cutter == lastcutter:
					output[lastcutter]+=b
				else:
					output['__border']=b
			else:
				output['__border']=b
		for key in sorted(output.iterkeys()):
			if self.modeconfig['mode']=='gcode' or self.modeconfig['mode']=="simplegcode":
				self.writeGcodeFile(part.name,key,self.modeconfig['prefix']+output[key]+self.modeconfig['postfix'], config)
			elif self.modeconfig['mode']=='svg':
				out+="<!-- "+str(part.name)+" - "+str(key)+" -->\n"+output[key]
		if self.modeconfig['mode']=='svg':	
		#	f=open(parent.name+"_"+self.name+"_"+part.name)
			if self.modeconfig['overview']:
				self.out+='<g>'+out+'</g>'
			elif part.name is not None:
				print self.name
				print part.name
				print "WRITE PAET\n"+out
				filename=self.name+"_"+part.name+".svg"
				f=open(filename,'w')
				f.write( self.modeconfig['prefix'] + out + self.modeconfig['postfix'] )
				f.close()

	def writeGcodeFile(self,partName, key, output, config):
		filename=str(partName)+"_"+str(self.name)+"_"+str(key)
		if 'cutter' in config:
			filename+="_cutter-"+str(config['cutter'])
		if 'material' in config:
			filename+='_'+str(config['material'])
		if 'thickness' in config:
			filename+="_thickness-"+str(config['thickness'])
		f=open(self.sanitise_filename(filename+config['file_suffix']),'w')
	#	print output
		f.write(output)
		f.close()
		if 'dosfile' in config and config['dosfile']:
			print "/usr/bin/unix2dos "+filename+config['file_suffix']
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

	def get_config(self):
		return self.config

