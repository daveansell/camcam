def rotate(pos, a):
        if type(pos) is Vec:
                M=Mat(1).rotateAxis(a,V(0,0,-1))
                pos=pos.transform(M)
                return pos
        else:
                return False

import math
from minivec import Vec, Mat
from path import *
from segments import *
import traceback

def V(x=False,y=False,z=False):
        if x==False:
                x=0
        if y==False:
                y=False
        if z==False:
                z=False
        return Vec(x,y,z)


class Point(object):
        def __init__(self, pos, point_type, radius=0, cp1=False, cp2=False, direction=False, transform=False):
		self.init()
                self.pos=Vec(pos)
                self.point_type=point_type
                self.radius=radius
                self.cp1=Vec(cp1)
                self.cp2=Vec(cp2)
                self.direction=direction
                self.transform=transform
                self.obType="Point"
	def init(self):
		self.nextpoint=None
		self.lastpoint=None
		self.cp1=V(0,0)
		self.cp2=V(0,0)
		self.radius=0
		if not hasattr(self,'reverse'):
			self.reverse=False	
        def copy(self):
                t = Point( self.pos, self.point_type, self.radius, self.cp1, self.cp2, self.direction, self.transform)
		
        def point_transform(self,ext_transformations=[]):
                p=self.copy()
                # If we are applying the transfomations the point shouldn't have them as a transform any more
                p.transform=False
                if self.transform!=False:
                        transformations=[self.transform]
                else:
                        transformations=[]
                transformations[:0] = ext_transformations
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
	def compile(self):
		return [self]
# rotate point about a point 
        def rotate(self,pos, t):
                if type(pos) is Vec:
                        pos = pos - t[0]
                        M=Mat(1).rotateAxis(t[1],V(0,0,-1))
#               pos.rotateAxis(t[0],V(0,0,-1))
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
                                raise ValueError( "Reflection direction "+str(t[1])+" is not a string or vector")
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

	def next(self):
		if self.reverse:
			self.lastpoint.reverse=1
			return self.lastpoint
		else:
			self.nextpoint.reverse=0
			return self.nextpoint

	def last(self):
		if self.reverse:
			self.nextpoint.reverse=1
			return self.nextpoint
		else:
			self.lastpoint.reverse=0
			return self.lastpoint

	def generateSegment(self, reverse, config):
		self.reverse=reverse
		s = self.makeSegment(config)
		if type(s) is list:
			return s#self.makeSegment(config)
		else:
			print "No segment returned "+str(type(self))
			return []

	def setangle(self):
		b1=(self.pos-self.lastorigin()).normalize()
                b2=(self.nextorigin()-self.pos).normalize()
		self.dot=b1.dot(b2)
                if self.dot>=1:
                        self.angle = 0
                else:
                        self.angle = math.acos(b1.dot(b2))
		a=b2-b1
		self.angle0=math.atan2(a[1], a[0])
#		self.angle2=(b1.angle(-b2)-90)*math.pi/180

	def corner_side(self, side):
		cross=(self.pos-self.lastorigin()).cross(self.nextorigin()-self.pos)[2]
		if abs(cross)<0.0000001:
			return 'external'
		if cross<=0.0000001 and side=='left' or cross>=-0.00000001 and side=='right':
			corner='external'
		else:
			corner='internal'
		return corner

	def offset_move_point(self, frompos, topos, side, distance):
		if distance>100:
                        distance=10
                if side=='left':
                        a=-90
                else:
                        a=90
                vecin=(self.pos-frompos).normalize()
                vecout=(topos-self.pos).normalize()
                # Find average direction of two vectors
		if (vecin-vecout).length()<0.00001:
			avvec=rotate(vecin,a).normalize()
		else:
                	avvec=(vecin-vecout)
                # then rotate it 90 degrees towards the requested side
                if avvec.length()<0.001:
                        return rotate(vecin,a).normalize()*distance+self.pos
                avvec=avvec.normalize()
                return -avvec*distance+self.pos

	def lastorigin(self):
#		if hasattr(self, 'forcelastpoint'):
#			last=self.forcelastpoint
##		else:
		last=self.last()
		if hasattr(last, 'control') and last.control or last.pos is not False and self.pos is not False and last.pos==self.pos:
			return last.lastorigin()
		else:
			return last.origin(False)

	def nextorigin(self):
		next=self.next()
		if hasattr(next, 'control') and next.control or next.pos is not False and self.pos is not False and next.pos==self.pos:
			return next.nextorigin()
		else:
			return next.origin(True)

	def otherDir(self,direction):
                if direction=='cw':
                        return 'ccw'
                else:
                        return 'cw'
	def lineArcIntersect(self, p1, p2, centre, rad):
		d=p2-p1
		dr=d.length()
		p1c=p1-centre
		p2c=p2-centre
		D=p1c[0]*p2c[1]-p1c[1]*p2c[0]
		dis = rad**2*dr**2-D**2
		if d[1]<0:
			s=-1
		else:
			s=1
		if dis<-0.0001:
			print "Dis is less than 0 dis="+str(dis)+" dr="+str(dr)+" D="+str(D)
			return False
		else:
			return centre +	V( (D*d[1]+d[0]*math.sqrt(dis))/dr**2,
				 (-D*d[0]+d[1]*math.sqrt(dis))/dr**2 )
		

class PSharp(Point):
	def __init__(self, pos, radius=0, cp1=False, cp2=False, direction=False, transform=False):
		self.init()
                self.pos=Vec(pos)
                self.point_type='sharp'
                self.radius=radius
                self.cp1=Vec(cp1)
                self.cp2=Vec(cp2)
                self.direction=direction
                self.transform=transform
                self.obType="Point"

	def copy(self):
                t=PSharp( self.pos, self.radius, self.cp1, self.cp2, self.direction, self.transform)
		t.forcelastpoint = self.lastpoint
		t.forcenextpoint = self.nextpoint
		t.lastpoint = self.lastpoint
		t.nextpoint = self.nextpoint
                t.reverse = self.reverse
		return t

	def origin(self, forward=True):
		return self.pos
	def end(self):
		return self.pos
	def start(self):
		return self.start

	def offset(self, side, distance, direction):
		return self.offsetSharp( side, distance, direction)

	def offsetSharp(self, side, distance, direction, sharp=True):
		self.setangle()

		if self.corner_side(side)=='external':# and side=='out' or corner=='internal' and side=='in':
			t = copy.copy(self)
	#		t=POutcurve(self.pos, radius=distance, transform=self.transform)
           		if self.angle==0 and self.dot<0:
      				pass
			elif self.angle==0 and self.point_type in ['sharp', 'clear', 'doubleclear'] and self.next().point_type in ['sharp', 'clear', 'doubleclear']:
					print "No angle so we can skip this one"
					return []
				
                   	else:
				if abs(self.dot-1)<=0.00000001:
					t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, -distance)
                          	elif self.dot<=0:
                                    	if self.angle>math.pi/2:
                                          	a=(math.pi-self.angle)/2
                                     	else:
                                             	a=self.angle/2
                                        t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, -distance/abs(math.sin(a)))
                             	else:
					a=(math.pi-self.angle)/2
                                        t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, -distance/abs(math.sin(a)))
                                    	#t.pos = self.offset_move_point( self.lastorigin(), self.nextorigin(), side, -distance/abs(math.cos((math.pi/4-self.angle0)/2)))

          	else:
#			t = copy.copy(self)
			if sharp==True:
				t = PClear(self.pos, self.transform)
			else:
				t = copy.copy(self)
                     	if self.angle==0 and self.dot<0:
				print "arong angle"
                      		pass
                   	else:
                          	if self.dot<=0:
                                    	if self.angle>math.pi/2:
                                          	a=(math.pi-self.angle)/2
                                     	else:
                                             	a=self.angle/2
                                   	t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, distance/abs(math.sin(a)))
                             	else:
					a=(math.pi-self.angle)/2
                                     	t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, distance/abs(math.sin(a)))
		return [t]

	def makeSegment(self, config):
		if self.last() != None and self.last().end()!=self.pos:
			return [Line(self.last().end(), self.pos)]
		else:
			return []

class PAroundcurve(PSharp):
	def __init__(self, pos, centre=False, radius=0, direction=False, transform=False):
                self.init()
                self.pos=Vec(pos)
                self.point_type='aroundcurve'
                self.radius=radius
                self.direction=direction
                self.transform=transform
		if centre is False:
			self.cp1 = pos
		else:
			self.cp1 = centre
                self.obType="Point"

        def copy(self):
                t= PAroundcurve( self.pos, self.cp1, self.radius, self.direction, self.transform)
                t.reverse=self.reverse
		t.lastpoint=self.lastpoint
		t.nextpoint=self.nextpoint
		t.forcelastpoint = self.lastpoint
		t.forcenextpoint = self.nextpoint
                return t

	def offset(self, side, distance, direction):
		self.setDirection()
#		ret=self.offsetSharp( side, distance, direction)
		ret = [self.copy()]
		if (self.direction=='cw' and side=='left' or self.direction=='ccw' and side=='right') !=self.reverse:
			ret[0].radius+=distance
		else:
			if ret[0].radius>distance:
				ret[0].radius-=distance
			else:
				ret= [PSharp(ret[0].pos)]
		return ret

	def setDirection(self):
		if self.direction is False:
			tempdir=(self.pos-self.lastorigin()).cross(self.nextorigin()-self.pos)
        	        if tempdir[2]>0:
                		self.direction='cw'
                    	elif tempdir[2]<0:
                           	self.direction='ccw'
	

	def makeSegment(self, config):
		self.setDirection()
		if self.last() != None and self.next() !=None:
                        lastpoint=self.lastorigin()
                        nextpoint=self.nextorigin()
			if not self.cp1==self.pos:				
				astart = self.lineArcIntersect(self.pos, lastpoint, self.cp1, self.radius)
				aend   = self.lineArcIntersect(self.pos, nextpoint, self.cp1, self.radius)
	#			astart = self.pos + (lastpoint-self.pos).normalize()*self.radius
	#			aend   = self.pos + (nextpoint-self.pos).normalize()*self.radius
			else:
				astart = self.pos + (lastpoint-self.pos).normalize()*self.radius
				aend   = self.pos + (nextpoint-self.pos).normalize()*self.radius

			if  not self.reverse:
				d=self.otherDir(self.direction)
			else:
				d=self.direction
			return [Line(self.last().end(), astart),
				Arc(astart, aend, self.cp1, d)]

	def start(self):
		lastpoint=self.lastorigin()
		if not self.cp1==self.pos:
			return self.lineArcIntersect(self.pos, lastpoint, self.cp1, self.radius)
		else:
			return self.pos+(lastpoint-self.pos).normalize()*self.radius

	def end(self):
		nextpoint=self.nextorigin()
		if not self.cp1==self.pos:
			return self.lineArcIntersect(self.pos, nextpoint, self.cp1, self.radius)
		else:
			return self.pos+(nextpoint-self.pos).normalize()*self.radius
	def origin(self, forward=True):
		if forward:
			op=self.last().pos
		else:
			op=self.next().pos
		vecin=(op-self.pos).normalize()
		if (self.direction=='cw' and self.reverse==False or self.direction=='ccw' and self.reverse==True)==forward:
			return op+rotate(vecin,-90)
		else:
			return op+rotate(vecin,90)

class PIncurve(PSharp):
	def __init__(self, pos, radius=0, direction=False, transform=False):
		self.init()
                self.pos=Vec(pos)
                self.point_type='incurve'
                self.radius=radius
                self.direction=direction
                self.transform=transform
                self.obType="Point"
	def copy(self):
                t= PIncurve( self.pos, self.radius, self.direction, self.transform)
		t.reverse=self.reverse
		t.lastpoint=self.lastpoint
		t.nextpoint=self.nextpoint
		t.forcelastpoint = self.lastpoint
		t.forcenextpoint = self.nextpoint
		return t
	def origin(self, forward=True):
		return self.pos
	def end(self):
		lastpoint=self.last().origin()
		nextpoint=self.next().origin()
		angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
		dl=self.radius*math.tan((angle/180)/2*math.pi)
		if angle==180 or angle==0:
			return self.pos
		return self.pos+(nextpoint-self.pos).normalize()*dl
	def start(self):
		lastpoint=self.last().origin()
		nextpoint=self.next().origin()
		angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
		dl=self.radius*math.tan((angle/180)/2*math.pi)
		if angle==180 or angle==0:
			return self.pos
		return self.pos+(lastpoint-self.pos).normalize()*dl
	def offset(self, side, distance, direction):
		self.setangle()
		t=copy.copy(self)
		if self.corner_side(side)=='external':
			t=self.offsetSharp( side, distance, direction)
			t[0].radius+=distance
                        #t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, -distance/abs(math.cos(self.angle2)))

		else:
			t=self.offsetSharp( side, distance, direction, False)
			if t[0].radius>distance:
                                        t[0].radius-=distance
                         #               t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, distance/abs(math.cos(self.angle0)))
                        else:
                                        t[0].point_type='sharp'
                                        t[0].radius=0
                         #               t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, distance/abs(math.cos(angle0)))
		return t
	def makeSegment(self, config):
		if self.last() != None and self.next() !=None:
			lastpoint=self.lastorigin()
			nextpoint=self.nextorigin()
			angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
                        dl=self.radius*math.tan((angle/180)/2*math.pi)
                        startcurve=self.pos-(self.pos-lastpoint).normalize()*dl
                        endcurve = self.pos+(nextpoint-self.pos).normalize()*dl
                        # If these are straight there should be no curve or the maths blows up so just behave like a normal point
                        if(((startcurve + endcurve)/2-self.pos).length()==0 or angle==0 or angle==180):
                                return [Line(self.last().end(),self.pos)]
                        else:
                                d = math.sqrt(dl*dl+self.radius*self.radius)/((startcurve + endcurve)/2-self.pos).length()
                                centre = self.pos + ((startcurve + endcurve)/2-self.pos)*d
                                tempdir=(self.pos-self.last().end()).cross(nextpoint-self.pos)
                                if tempdir[2]>0:
                                        tempd='cw'
                                elif tempdir[2]<0:
                                        tempd='ccw'
                                else:
                                        tempd='cw'
                                return [
                                        Line(self.last().end(),startcurve),
                                        Arc(startcurve, endcurve, centre,tempd),
				]
                        frompoint=endcurve
		elif self.next()==None:
			return [Line(self.last().origin(), self.pos)]
		else:
			return []

class PChamfer(Point):
	def __init__(self, pos, chamfer=0, radius=0, direction=False, transform=False):
		self.init()
		self.pos=Vec(pos)
		if chamfer==0:
			self.point_type='sharp'
		else:
                	self.point_type='chamfer'
                self.radius=radius
		self.chamfer=chamfer
                self.direction=direction
                self.transform=transform
                self.obType="Point"
	def copy(self):
                return PChamfer( self.pos, self.chamfer, self.radius, self.direction, self.transform)
	def compile(self):
		invec=self.lastorigin-self.pos
		outvec=self.nextorigin-self.pos
		if invec.length()<self.radius:
			print "Chamfer is larger than the distance to the previous point"
		if outvec.length()<self.radius:
			print "Chamfer is larger than the distance to the next point"
		if radius==0:
			return [PSharp(self.pos+invec.normalize()*self.chamfer), PSharp(self.pos+outvec.normalize()*self.chamfer)]
		elif radius>0:
			return [POutcurve(self.pos+invec.normalize()*self.chamfer, radius=radius), POutcurve(self.pos+outvec.normalize()*self.chamfer, radius=radius)]
	def origin(self, forward=True):
                return self.pos
	def end(self):
		outvec=self.nextorigin()-self.pos
		return self.pos+outvec.normalize()*self.chamfer
	def end(self):
		invec=self.lastorigin()-self.pos
		return self.pos+invec.normalize()*self.chamfer
	def offset(self, side, distance, direction):
		passself.pos+outvec.normalize()*self.radius
	def makeSegment(self, config):
		pass

class POutcurve(Point):
	def __init__(self, pos, radius=0, direction=False, transform=False):
		self.init()
                self.pos=Vec(pos)
                self.point_type='outcurve'
                self.radius=radius
                self.direction=direction
                self.transform=transform
                self.obType="Point"
	def copy(self):
                t=POutcurve( self.pos, self.radius, self.direction, self.transform)
		t.lastpoint=self.lastpoint
		t.nextpoint=self.nextpoint
		t.forcelastpoint = self.lastpoint
		t.forcenextpoint = self.nextpoint
		t.reverse = self.reverse
		return t
	def origin(self, forward=True):
		seg=self.makeSegment({})
		print "arc from="+str(seg[1].cutfrom)+" arc to="+str(seg[1].cutto)+" direction="+str(seg[1].direction)
		if forward:
			return seg[1].cutfrom
		else:
			return seg[1].cutto
	def end(self):
		lastpoint=self.lastorigin()
		nextpoint=self.nextorigin()
		angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
		dl=self.radius*math.tan((angle/180)/2*math.pi)
		return self.pos+(nextpoint-self.pos).normalize()*dl
	def start(self):
		lastpoint=self.lastorigin()
		nextpoint=self.nextorigin()
		angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
		dl=self.radius*math.tan((angle/180)/2*math.pi)
		return self.pos+(lastpoint-self.pos).normalize()*dl
	def offset(self, side, distance, direction):
		t=copy.copy(self)
		if self.corner_side(side)=='external':
			t.radius += distance
		elif(self.radius>=distance):
			t.radius -= distance
		else:
			t.setangle()
			move_point = distance-t.radius
			if t.angle==0 and t.dot<0:
                                return False
                        else:
                                if t.dot<=0:
                                        t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, distance/abs(math.sin((self.angle)/2)))
                                else:
                                        t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, distance/abs(math.cos((math.pi/4-self.angle)/2)))
		return [t]
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
#                       sgn=1
                        a=-90
                else:
                        a=90
#                       sgn=-1

                diff=centre-point
                offset=rotate(diff.normalize(),a)
#       return centre+offset*r

                d=diff.length()
                if d-r<-0.001:
                        print "d="+str(d)+" is less than r="+str(d)
#                       t=d
#                       d=r
#                       r=t
#                       print d<r
			l=0
			return centre
		else:
                	l=math.sqrt(d*d-r*r)
                theta= math.acos(r/d)

                rx=-r* math.cos(theta) *diff.normalize()
                ry=r* math.sin(theta) *offset
                return centre+rx+ry


                theta = math.atan2(r,l)
#               theta = math.atan2(diff[1],diff[0])
                phi = math.asin(r/d)

                rvec = V(l * math.sin(theta+phi*sgn), l * math.cos(theta+phi*sgn), 0)
                if(diff[0]<0):
                        rvec[0]*=-1
                return point+rvec

	def makeSegment(self, config):
		segment_array=[]
		if self.last().point_type=='outcurve':
                        lr=self.last().radius
                else:
                        lr=0
		if self.last() is not None and self.last().point_type not in ['sharp', 'outcurve', 'clear', 'doubleclear']:

			print "Outcurve must be preceeded by a sharp point or another outcurve not a "+str(self.last().point_type)
			return []
		if lr!=0:
			if type(self.last().last()) == None:
				print "OUtcurve must be preceeded by 2 points if previous point is outcurce"
                       	if (self.last().pos-self.last().last().pos).cross(self.pos-self.last().pos)[2] <0:
                       	        d1='cw'
                       	else:
                       	        d1='ccw'
		else:
			# if lr=0 we don't care about the direction
			d1='cw'
                if (self.pos-self.last().pos).cross(self.next().pos-self.pos)[2] <0:
                        d2='cw'
                else:
                        d2='ccw'
                p1=self.tangent_points( self.last().pos, lr, d1, self.pos, self.radius, d2)
                segment_array.append( Line(p1[0], p1[1]))
                d3=''
                if self.next().point_type=="outcurve":
#                        if (self.nextorigin()-self.pos).cross(self.next().nextorigin()-self.nextorigin())[2] <0:
                        if (self.next().pos-self.pos).cross(self.next().next().pos-self.next().pos)[2] <0:
                                d3='cw'
                        else:
                                d3='ccw'
                        p2=self.tangent_points( self.pos, self.radius, d2, self.next().pos, self.next().radius, d3)
                        segment_array.append( Arc( p1[1],p2[0], self.pos, self.otherDir(d2)))
                        frompoint=p2
                else:

                        p2 = self.tangent_point(self.next().pos, self.pos, self.radius, self.otherDir(d2))
                        segment_array.append( Arc( p1[1],p2, self.pos, self.otherDir(d2)))
                        frompoint=p2
		return segment_array	
		
class PClear(PSharp):
	def __init__(self, pos, transform=False):
		self.init()
                self.pos=Vec(pos)
                self.point_type='clear'
                self.transform=transform
                self.obType="Point"
	def copy(self):
                t = PClear( self.pos, self.transform)
		t.lastpoint=self.lastpoint
		t.nextpoint=self.nextpoint
		t.reverse=self.reverse
		return t
	def makeSegment(self, config):
		if self.last() != None and self.next() !=None:
			lastpoint=self.lastorigin()
			if lastpoint==self.pos:
				lastpoint=self.last().lastorigin()
			nextpoint=self.nextorigin()
			if nextpoint==self.pos:
				nextpoint=self.next().nextorigin()
                      	angle=(self.pos-lastpoint).angle(nextpoint-self.pos)

                	d=config['cutterrad']*(1/math.sin((180-angle)/2/180*math.pi)-1)
			
                	extrapoint=self.pos-(((lastpoint-self.pos).normalize()+(nextpoint-self.pos).normalize())/2).normalize()*d

                return [
			Line(self.last().end(),self.pos),
                	Line(self.pos,extrapoint),
                	Line(extrapoint,self.pos),
		]

class PDoubleClear(Point):
	def __init__(self, pos, transform=False):
		self.init()
                self.pos=Vec(pos)
                self.point_type='doubleclear'
                self.transform=transform
                self.obType="Point"
	def copy(self):
                t = PDoubleClear( self.pos, self.transform)
		t.lastpoint=self.lastpoint
		t.nextpoint=self.nextpoint
		t.forcelastpoint = self.lastpoint
		t.forcenextpoint = self.nextpoint
		t.reverse=self.reverse
		return t
	def makeSegment(self, config):
		if self.last() != None and self.next() !=None:
			lastpoint=self.last().origin()
			if lastpoint==self.pos:
				lastpoint=self.last().lastorigin()
			nextpoint=self.next().origin()
			if nextpoint==self.pos:
				nextpoint=self.next().nextorigin()
                      	angle=(self.pos-lastpoint).angle(nextpoint-self.pos)

                	d=config['cutterrad']*(1/math.sin((180-angle)/2/180*math.pi)-1)
			o=(((lastpoint-self.pos).normalize()+(nextpoint-self.pos).normalize())/2).normalize()*d
			extrapoint1=self.pos-o
			extrapoint2=self.pos+o

                return [
			Line(self.last().end(),self.pos),
                	Line(self.pos,extrapoint1),
                	Line(self.pos,extrapoint2),
                	Line(extrapoint2,self.pos),
		]




class PBezierControl(Point):		
	def __init__(self, pos, transform=False):
		self.init()
                self.pos=Vec(pos)
                self.point_type='bcontrol'
                self.transform=transform
                self.obType="Point"
		self.control = True
	def copy(self):
                t = PBezierControl( self.pos,  self.transform)
		t.lastpoint=self.lastpoint
		t.nextpoint=self.nextpoint
		t.reverse=self.reverse
		return t
	def origin(self, forward=True):
		return self.pos
	def end(self):
		return self.next().pos
	def start(self):
		return self.last().pos
	def offset(self, direction, distance, pointlist):
		print "can't do bezier offset"

		return []

	def makeSegment(self, config):
		if self.last().point_type=='sharp' and self.next().point_type=='sharp':
			#quadratic
			return [Quad(self.last().end(), self.pos(), self.next().pos())]
		elif self.last().last().point_type=='sharp' and self.last().point_type=='bcontrol' and self.next().point_type=='sharp':
			#cubic
			return [Cubic(self.last().last().end(), self.last().pos, self.pos, self.next().pos)]
		elif self.next().point_type=='bcontrol':
			return []
		else:
			print "Beiziers should be one or two bcontrol points flanked by sharp points" 
			return []

class PArc(Point):
	def __init__(self, pos=False, radius=False, direction=False, length=False, transform=False):
		"""radius - arc radius, direction - direction of arc, length - [short, long]"""
		self.init()
		self.pos=pos
		self.radius=radius
		self.direction=direction
		self.length=length
		self.transform=transform
		self.point_type='arc'
		self.control = False#True
		self.obType='Point'
	def copy(self):
                t = PArc( self.pos, self.radius, self.direction,self.length, self.transform)
		t.lastpoint=self.lastpoint
		t.nextpoint=self.nextpoint
		t.forcelastpoint = self.lastpoint
		t.forcenextpoint = self.nextpoint
		t.reverse=self.reverse
		return t

	def checkArc(self):
		if self.pos is not False and self.radius is not False:
			if (self.pos-self.last().pos).length()-self.radius>000.1 or (self.next().pos-self.pos).length()-self.radius>0.001:
				print "Arc's radius should be <= distance to the centre"+str(self.next().pos)+"->"+str(self.pos)+"->"+str(self.last().pos)+" radius="+str(self.radius)+" AC-radius="+str((self.pos-self.last().pos).length()-self.radius)+" BC-raiuds="+str((self.next().pos-self.pos).length()-self.radius)
		elif self.radius is not False and self.length is not False and self.pos is False:
			
			l=self.nextorigin() - self.lastorigin()
			print l
			print self.radius
			b=math.sqrt(self.radius**2-l.length()**2/4)
			
			if l.length()>2*self.radius:
				print "Can't make an arc longer than twice its radius"
			if self.direction=='cw' and self.reverse or self.direction=='ccw' and not self.reverse:
				perp=rotate(l.normalize(),-90)
			else:
				perp=rotate(l.normalize(),90)
			self.pos = self.last().pos + l/2 + perp * b
			print "circle centre="+str(self.pos)+" lastorigin="+str(self.lastorigin())+" nextorigin="+str(self.nextorigin())+" radius="+str(self.radius)
		elif self.pos is not False:
			self.radius=min((self.next().pos-self.pos).length(), (self.pos- self.last().pos).length())

	def makeSegment(self, config):
		self.checkArc()
		if self.last().point_type not in ['sharp', 'clear', 'doubleclear'] or self.next().point_type not in ['sharp', 'clear', 'doubleclear']:
			print "points either side of an Arc should be sharp"
			return []
		else:
			l=self.next().pos - self.last().pos
			perp=rotate(l.normalize(),-90)
			centre=self.pos.intersect_lines(self.last().pos, self.next().pos, self.pos, self.pos+perp)
			print "pos="+str(self.pos)+" centre="+str(centre)
			print "radius="+str(self.radius)+" pos - centre = "+str( (self.pos-centre).length())
			print self.radius**2 - (self.pos-centre).length()**2
			c=math.sqrt(self.radius**2 - (self.pos-centre).length()**2)
			a = l.normalize()*c
			if not self.reverse:
				print "REVERSE ARC"
				d=self.otherDir(self.direction)
			else:
				print "NOT REVERSE AEC"
				d=self.direction
			print self.direction+"  "+d
			return [ Line(self.last().pos, centre-a), Arc(centre-a, centre+a, self.pos, d), Line(centre+a, self.next().pos)]
		
        def origin(self, forward=True):
                if forward:
                        op=self.last().pos
                else:
                        op=self.next().pos

		if abs(op.length()-self.radius)>-0.001:
			print "arc at corner WWWWWW"
	                vecin=(op-self.pos).normalize()
	                if (self.direction=='cw' and self.reverse==False or self.direction=='ccw' and self.reverse==True)==forward:
	                        return op+rotate(vecin,90)
	                else:
	                        return op+rotate(vecin,-90)
		else:
			print "HHHHHHHH"
			if forward:
				return self.next().pos
			else:
				return self.last().pos
	
	def end(self):
		self.checkArc()
		l=self.next().pos - self.last().pos
                perp=rotate(l.normalize(),-90)
                centre=self.pos.intersect_lines(self.last().pos, self.next().pos, self.pos, self.pos+perp)
                c=math.sqrt(self.radius**2 - (self.pos-centre).length()**2)
                a = l.normalize()*c
		return centre+a
	def start(self):
		self.checkArc()
		l=self.next().pos - self.last().pos
                perp=rotate(l.normalize(),-90)
                centre=self.pos.intersect_lines(self.last().pos, self.next().pos, self.pos, self.pos+perp)
                c=math.sqrt(self.radius**2 - (self.pos-centre).length()**2)
                a = l.normalize()*c
		return centre-a
		
	def offset(self, side, distance, direction):
		self.checkArc()
		t=copy.copy(self)
#		print "side="+str(side)+" direction="+str(self.direction)
		if side=='left' and self.direction=='cw' or side=='right' and self.direction=='ccw':
			t.radius+=distance
		else:
			if t.radius>=distance:
				t.radius-=distance
			else:
				t.radius=0
		return [t]
class PCircle(Point):
	def __init__(self, pos=False, radius=False, transform = False):
		self.init()
		self.pos=pos
		self.radius=radius
		self.transform=transform
		self.point_type='circle'
		self.obType='Point'
	def copy(self):
                t= PCircle( self.pos, self.radius,  self.transform)
		t.lastpoint=self.lastpoint
		t.nextpoint=self.nextpoint
		t.reverse=self.reverse
		return t
	def makeSegment(self, config):
		r1 = V(self.radius, 0)
		r2 = V(0, self.radius)
		if self.reverse:
			return [ Arc(self.pos-r1, self.pos-r2, self.pos, 'cw'), Arc(self.pos-r2, self.pos+r1, self.pos, 'cw'), Arc(self.pos+r1, self.pos+r2, self.pos, 'cw'), Arc(self.pos+r2, self.pos-r1, self.pos, 'cw') ]
		else:
			return [ Arc(self.pos-r1, self.pos+r2, self.pos, 'ccw'), Arc(self.pos+r2, self.pos+r1, self.pos, 'ccw'), Arc(self.pos+r1, self.pos-r2, self.pos, 'ccw'), Arc(self.pos-r2, self.pos-r1, self.pos, 'ccw') ]
	def offset(self, side, distance, direction):
		t=copy.copy(self)
		if side=='left' and self.direction=='cw' or side=='right' and self.direction=='ccw':
                        t.radius+=distance
		else:
			if t.radius>distance:
				t.radius-=distance
			else:
				return []
		return [t]
