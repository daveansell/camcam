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
		self.nextpoint=None
		self.lastpoint=None
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
#               print "point transform "+str(transformations)
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
		return self.nextpoint
	def last(self):
		return self.lastpoint

	def angle(self):
		b1=(thispoint.pos-lastpoint.pos).normalize()
                b2=(nextpoint.pos-thispoint.pos).normalize()
		self.dot=b1.dot(b2)
                if self.dot>=1:
                        self.angle = 0
                else:
                        self.angle = math.acos(b1.dot(b2))

	def corner_side(self):
		cross=(self.pos-self.last().pos).cross(self.next().pos-self.pos)[2]
		if cross<0 and side=='left' or cross>0 and side=='right':
			corner='external'
		else:
			corner='internal'

	def offset_move_point(self, frompos, topos, side, distance):
		if distance>10:
                        distance=10
                if side=='left':
                        a=-90
                else:
                        a=90
                vecin=(self.pos-frompos).normalize()
                vecout=(topos-self.pos).normalize()
                # Find average direction of two vectors
                avvec=(vecin-vecout)
                # then rotate it 90 degrees towards the requested side
                if avvec.length()<0.001:
                        return rotate(vecin,a).normalize()*distance+self.pos
                avvec=avvec.normalize()
                return -avvec*distance+self.pos

class PSharp(Point):
	def __init__(self, pos, radius=0, cp1=False, cp2=False, direction=False, transform=False):
                self.pos=Vec(pos)
                self.point_type='sharp'
                self.radius=radius
                self.cp1=Vec(cp1)
                self.cp2=Vec(cp2)
                self.direction=direction
                self.transform=transform
                self.obType="Point"
	def origin(self):
		return self.pos
	def end(self):
		return self.pos

	def offset(self, direction, distance, pointlist):
		self.angle()
		t = copy.copy(self)
		if self.corner_side()=='external':# and side=='out' or corner=='internal' and side=='in':
            		if self.angle==0 and self.dot<0:
      				return False
                   	else:
                          	if self.dot<=0:
                                   	if self.angle>math.pi/2:
                                          	a=(math.pi-angle3)/2
                                     	else:
                                             	a=self.angle
                                        t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, -distance/abs(math.sin(a)))
                             	else:
                                    	t.pos = self.offset_move_point( self.lastorigin(), self.nextorigin(), side, -distance/abs(math.cos((math.pi/4-angle3)/2)))
          	else:
                     	if self.angle==0 and self.dot<0:
                      		return False
                   	else:
                          	if self.dot<=0:
                                   	t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, distance/abs(math.sin((self.angle)/2)))
                             	else:
                                     	t.pos = self.offset_move_point(self.lastorigin(), self.nextorigin(), side, distance/abs(math.cos((math.pi/4-self.angle)/2)))
		return t

	def makeSegment(self, config):
		if self.last() != None and self.last().end()!=self.pos:
			return [Line(self.last().end(), self.pos)]
		else:
			return []
			
class PIncurve(Point):
	def __init__(self, pos, radius=0, direction=False, transform=False):
                self.pos=Vec(pos)
                self.point_type='incurve'
                self.radius=radius
                self.direction=direction
                self.transform=transform
                self.obType="Point"
	def origin(self, pointlist=False):
		return self.pos
	def end(self):
		lastpoint=self.last().origin()
		nextpoint=self.next().origin()
		angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
		dl=self.radius*math.tan((angle/180)/2*math.pi)
		return self.pos+(nextpoint-self.pos).normalize()*dl
	def offset(self, direction, distance, pointlist):
	def makeSegment(self, config):
		if self.last() != None and self.next() !=None:
			lastpoint=self.last().origin()
			nextpoint=self.next().origin()
			angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
                        dl=self.radius*math.tan((angle/180)/2*math.pi)
                        startcurve=self.pos-(self.pos-lastpoint).normalize()*dl
                        endcurve = self.pos+(nextpoint-self.pos).normalize()*dl
                        # If these are straight there should be no curve or the maths blows up so just behave like a normal point
                        if(((startcurve + endcurve)/2-self.pos).length()==0):
                                return [Line(self.last().end(),thispoint.pos)]
                        else:
                                d = math.sqrt(dl*dl+thispoint.radius*thispoint.radius)/((startcurve + endcurve)/2-thispoint.pos).length()
                                centre = thispoint.pos + ((startcurve + endcurve)/2-thispoint.pos)*d
                                tempdir=(thispoint.pos-frompoint).cross(nextpoint.pos-thispoint.pos)
                                if tempdir[2]>0:
                                        tempd='cw'
                                elif tempdir[2]<0:
                                        tempd='ccw'
                                else:
                        #               print "ERROR - straight arc"
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
	def __init__(self, pos, distance=0, direction=False, transform=False):
		self.pos=Vec(pos)
                self.point_type='chamfer'
                self.radius=radius
                self.direction=direction
                self.transform=transform
                self.obType="Point"
	def origin(self, pointlist=False):
                return self.pos
	def end(self):
		pass
	def offset(self, direction, distance, pointlist):
		pass
	def makeSegment(self, config):
		pass

class POutcurve(Point):
	def __init__(self, pos, radius=0, direction=False, transform=False):
                self.pos=Vec(pos)
                self.point_type='outcurve'
                self.radius=radius
                self.direction=direction
                self.transform=transform
                self.obType="Point"
	def origin(self, pointlist=False):
		return self.pos
	def end(self):
		lastpoint=self.last().origin()
		nextpoint=self.next().origin()
		angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
		dl=self.radius*math.tan((angle/180)/2*math.pi)
		return self.pos+(nextpoint-self.pos).normalize()*dl
	def offset(self, direction, distance, pointlist):
		
	def makeSegment(self, config):
		segment_array=[]
		if self.last().point_type=='outcurve':
                        lr=lastpoint.radius
                else:
                        lr=0
		if self.last() is not None and self.last().point_type not in ['sharp', 'outcurve']:
			print "Outcurve must be preceeded by a sharp point or another outcurve"
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
			

class PClear(Point):
	def __init__(self, pos, transform=False):
                self.pos=Vec(pos)
                self.point_type='clear'
                self.transform=transform
                self.obType="Point"
	def origin(self):
		return self.pos
	def end(self):
		return self.pos
	def offset(self, direction, distance, pointlist):
		print "do offset"
	def makeSegment(self, config):
		if self.last() != None and self.next() !=None:
			lastpoint=self.last().origin()
			if lastpoint==self.pos:
				lastpoint=self.last().last().origin()
			nextpoint=self.next().origin()
			if nextpoint==self.pos:
				nextpoint=self.next().next().origin()
                      	angle=(thispoint.pos-lastpoint.pos).angle(nextpoint.pos-thispoint.pos)

                	d=config['cutterrad']*(1/math.sin((180-angle)/2/180*math.pi)-1)
                	extrapoint=self.pos-(((lastpoint-self.pos).normalize()+(nextpoint-self.pos).normalize())/2).normalize()*d

                return [
			Line(self.last().end(),self.pos),
                	Line(self.pos,extrapoint),
                	Line(extrapoint,self.pos),
		]

class PDoubleClear(Point):
	def __init__(self, pos, transform=False):
                self.pos=Vec(pos)
                self.point_type='clear'
                self.transform=transform
                self.obType="Point"
	def origin(self):
		return self.pos
	def end(self):
		return self.pos
	def offset(self, direction, distance, pointlist):
		print "do offset"
	def makeSegment(self, config):
		if self.last() != None and self.next() !=None:
			lastpoint=self.last().origin()
			if lastpoint==self.pos:
				lastpoint=self.last().last().origin()
			nextpoint=self.next().origin()
			if nextpoint==self.pos:
				nextpoint=self.next().next().origin()
                      	angle=(thispoint.pos-lastpoint.pos).angle(nextpoint.pos-thispoint.pos)

                	d=config['cutterrad']*(1/math.sin((180-angle)/2/180*math.pi)-1)
			o=(((lastpoint-self.pos).normalize()+(nextpoint-self.pos).normalize())/2).normalize()*d
			extrapoint1=thispoint.pos-o
			extrapoint2=thispoint.pos+o

                return [
			Line(self.last().end(),self.pos),
                	Line(self.pos,extrapoint1),
                	Line(self.pos,extrapoint2),
                	Line(extrapoint2,self.pos),
		]




class PBezierControl(Point):		
	def __init__(self, pos, transform=False):
                self.pos=Vec(pos)
                self.point_type='bcontrol'
                self.transform=transform
                self.obType="Point"
	def origin(self):
		return self.pos
	def end(self):
		return self.next().pos
	def offset(self, direction, distance, pointlist):
		print "do offset"

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

class Arc(Point):
	def __init__(self, pos=False, radius=False, direction=False, length=False):
		self.pos=pos
		self.radius=radius
		self.direction=direction
		self.length=length
		self.point_type='arc'
		self.obType='Point'
	def checkArc(self):
		if self.pos and radius:
			if (self.pos-self.last().pos).length()<radius or (self.next().pos-self.pos).length()<radius:
				print "Arc's radius should be <= distance to the "
		elif radius and length:

		elif self.pos:
			self.radius=min((self.next()-self.pos).length(), (self.pos- self.last().pos))
	def makeSegment(self, config):
		if self.last().point_type=='sharp' and self.next().point_type=='sharp':
			
		
			
