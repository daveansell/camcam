# This file is part of CamCam.

#    CamCam is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with CamCam.  If not, see <http://www.gnu.org/licenses/>.

#    Author Dave Ansell



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
    def __init__(self, pos, point_type, radius=0, cp1=False, cp2=False, direction=False, transform=False, invert=False):
        self.init()
        self.pos=Vec(pos)
        self.point_type=point_type
        self.radius=radius
        self.cp1=Vec(cp1)
        self.cp2=Vec(cp2)
        self.direction=direction
        self.transform=transform
        self.obType="Point"
        self.invert = invert
    def init(self):
        self.nextpoint=None
        self.lastpoint=None
        self.cp1=V(0,0)
        self.cp2=V(0,0)
        self.radius=0
        self.setup=False
        self.path=False # for debug
        if not hasattr(self,'reverse'):
            self.reverse=False
        self.invert = False
        self.dirpoint = True
        self.isRapid = False
    def _setup(self):
        self.setup=True
    def setPos(self, pos):
        self.pos = pos

    def copy(self):
        t = Point( self.pos, self.point_type, self.radius, self.cp1, self.cp2, self.direction, self.transform, self.invert)
        t.invert = self.invert
        t.path = self.path
        return t
    def __deepcopy__(self,memo):
        obj_copy = object.__new__(type(self))
        for v in self.__dict__:
            if v in ['parent', 'nextpoint', 'lastpoint']:
                obj_copy.__dict__[v]=copy.copy(self.__dict__[v])
            else:
                obj_copy.__dict__[v]=copy.deepcopy(self.__dict__[v],memo)
        return obj_copy
    def point_transform(self,ext_transformations=[]):
        p=self.copy()
        # If we are applying the transfomations the point shouldn't have them as a transform any more
        p.transform=False
        if self.transform!=False:
            transformations=[self.transform]
        else:
            transformations=[]
        transformations[:0] = ext_transformations
        self.invert = False
        if type(transformations) is list:
            for t in reversed(transformations):
                if type(t) is dict and p.pos is not None:
                    if 'rotate' in t:
                        p.pos=self.rotate(p.pos, t['rotate'])
                        p.cp1=self.rotate(p.cp1, t['rotate'])
                        p.cp2=self.rotate(p.cp2, t['rotate'])
                    if 'translate' in t:
                        p.pos += t['translate']
                        p.cp1 += t['translate']
                        p.cp2 += t['translate']
                    if 'mirror' in t:
                        p.invert = not p.invert
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
            return out

    def __next__(self):
        if self.reverse:
            self.lastpoint.reverse=1
        #       self.lastpoint._setup()
            return self.lastpoint
        else:
            self.nextpoint.reverse=0
        #       self.lastpoint._setup()
            return self.nextpoint
    def next(self):
        return self.__next__()

    def last(self):
        if self.reverse:
            self.nextpoint.reverse=1
            return self.nextpoint
        else:
            self.lastpoint.reverse=0

            #self.lastpoint._setup()
            return self.lastpoint

    def generateSegment(self, reverse, config):
        self.reverse=reverse
        s = self.makeSegment(config)
        if type(s) is list:
            return s#self.makeSegment(config)
        else:
            print("No segment returned "+str(type(self)))
            return []

    def setangle(self):
        self._setup()
        b1=(self.pos-self.lastorigin()).normalize()
        b2=(self.nextorigin()-self.pos).normalize()
        self.dot=b1.dot(b2)
        if self.dot>=1:
            self.angle = 0
        elif self.dot<=-1:
            self.angle = math.pi
        else:
            self.angle = math.acos(b1.dot(b2))
        a=b2-b1
        self.angle0=math.atan2(a[1], a[0])
#               self.angle2=(b1.angle(-b2)-90)*math.pi/180

# side - side we are cutting on, direction overall direction of cut (cw/ccw)
    def corner_side(self, side, direction):
        cross=(self.pos-self.lastorigin()).cross(self.nextorigin()-self.pos)[2]
        if abs(cross)<0.0000001:
            return 'external'
# Am changing this which may be wrong, but
        if (cross<=-0.0000001 and side=='left' or cross>=0.00000001 and side=='right'):# == (direction=='cw'):
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
#               if hasattr(self, 'forcelastpoint'):
#                       last=self.forcelastpoint
##              else:
        last=self.last()
        if hasattr(last, 'control') and last.control or last.pos is not None and self.pos is not None and last.pos==self.pos:
            return last.lastorigin()
        else:
            return last.origin(False)

    def nextorigin(self):
        nnext=next(self)
        if hasattr(nnext, 'control') and nnext.control or nnext.pos is not None and self.pos is not None and nnext.pos==self.pos:
            return nnext.nextorigin()
        else:
            return nnext.origin(True)

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
        if dis<0.0001:
            print("Dis is less than 0 dis="+str(dis)+" dr="+str(dr)+" D="+str(D)+" p1="+str(p1)+" p2="+str(p2)+" centre="+str(centre))
            return False
        else:
            if dis<0:
                dis=0
            return centre + V( (D*d[1]+d[0]*math.sqrt(dis))/dr**2,
                     (-D*d[0]+d[1]*math.sqrt(dis))/dr**2 )
    def end(self):
        return self.pos
    def start(self):
        return self.start


class PSharp(Point):
    def __init__(self, pos, radius=0, cp1=False, cp2=False, direction=False, transform=False, sharp=True, isRapid=False):
        """Create a sharp point at position=pos"""
        self.init()
        self.pos=Vec(pos)
        self.point_type='sharp'
        self.radius=radius
        self.cp1=Vec(cp1)
        self.cp2=Vec(cp2)
        self.direction=direction
        self.transform=transform
        self.obType="Point"
        self.sharp=sharp
        self.isRapid=isRapid

    def copy(self):
        t=PSharp( self.pos, self.radius, self.cp1, self.cp2, self.direction, self.transform)
        t.forcelastpoint = self.lastpoint
        t.forcenextpoint = self.nextpoint
        t.lastpoint = self.lastpoint
        t.nextpoint = self.nextpoint
        t.reverse = self.reverse
        t.sharp = self.sharp
        t.invert = self.invert
        t.isRapid = self.isRapid
        return t

    def origin(self, forward=True):
        return self.pos
    def end(self):
        return self.pos
    def start(self):
        return self.start

    def offset(self, side, distance, direction):
        return self.offsetSharp( side, distance, direction, self.sharp)

    def offsetSharp(self, side, distance, direction, sharp=True):
        self.setangle()
        if self.corner_side(side, direction)=='external':# and side=='out' or corner=='internal' and side=='in':
            t = copy.copy(self)
    #               t=POutcurve(self.pos, radius=distance, transform=self.transform)
            if (self.angle==0 or self.angle==math.pi and self.dot<0) and self.last().point_type in ['sharp', 'clear', 'doubleclear'] and self.next().point_type in ['sharp', 'clear', 'doubleclear'] and self.point_type in ['sharp', 'clear', 'doubleclear']:
                pass
            elif self.angle==0  and self.point_type in ['sharp', 'clear', 'doubleclear'] and self.next().point_type in ['sharp', 'clear', 'doubleclear']:
                return []
            else:
                if abs(self.dot-1)<=0.00000001 or abs(self.dot+1) <=0.00000001:
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
#                       t = copy.copy(self)
            if sharp==True:
                t = PClear(self.pos, self.transform)
            else:
                t = copy.copy(self)
            if self.angle==0 and self.dot<0:
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
        l= self.last()
        if type(l) is not None and l.end()!=self.pos:
            if self.isRapid==True:
                return [Line(self.last().end(), self.pos, rapid=True)]
            else:
                return [Line(self.last().end(), self.pos)]
        else:
#                       print "No segnmet" + str(l.end())+"&&"
#                       print "No segnmet" + str(self.last())+"&&"
            if l is not None:
                pass
                #print "&&"+str(l.end())+" self.pos="+str(self.pos)
            return []

class PAroundcurve(PSharp):
    def __init__(self, pos, centre=False, radius=0, direction=False, transform=False):
        """Create a point which will head for point pos and then add an arc around the point centre with a radius=radius. Useful for adding ears around screw holes. if centre is not specified it is assumed it is the same as pos"""
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
        t.invert = self.invert
        return t

    def offset(self, side, distance, direction):
        self.setDirection()
        t=self.offsetSharp( side, distance, direction)
        ret = [self.copy()]
        if (self.direction=='cw' and side=='left' or self.direction=='ccw' and side=='right') !=self.reverse:
            ret[0].radius+=distance
# There is a case where for small angles offsetting can move the convergence point outside the radius
            if (t[0].pos - self.cp1).length()> ret[0].radius:
                ret= [PSharp(t[0].pos)]

        else:
            if ret[0].radius>distance:
                ret[0].radius-=distance
            else:
                ret= [PClear(ret[0].pos)]
        if ret[0].radius <=0:
            ret[0].radius = 0
            ret[0].point_type='sharp'
        ret[0].pos = t[0].pos
        return ret

    def setDirection(self):
        if self.direction is False:
            tempdir=(self.pos-self.lastorigin()).cross(self.nextorigin()-self.pos)
            if tempdir[2]>0:
                self.direction='cw'
            elif tempdir[2]<0:
                self.direction='ccw'
            else:
                self.direction='cw'

    def makeSegment(self, config):
        self.config=config
        self.dosetup=True
        # we need the last point to run _setup() later so set it up to
        self.last().dosetup=True
        self.last().config=config
        self._setup()
        self.setDirection()
        if self.last() != None and next(self) !=None:
            lastpoint=self.lastorigin()
            nextpoint=self.nextorigin()
            if self.radius ==0:
                return [Line(self.last().end(), self.pos)]
            if not self.cp1==self.pos:
                astart = self.lineArcIntersect(self.pos, lastpoint, self.cp1, self.radius)
                aend   = self.lineArcIntersect(self.pos, nextpoint, self.cp1, self.radius)
    #                       astart = self.pos + (lastpoint-self.pos).normalize()*self.radius
    #                       aend   = self.pos + (nextpoint-self.pos).normalize()*self.radius
            else:
                astart = self.pos + (lastpoint-self.pos).normalize()*self.radius
                aend   = self.pos + (nextpoint-self.pos).normalize()*self.radius
            if astart is False:
                return [Line(self.last().end(), self.pos)]
            if aend is False:
                return [Line(self.last().end(), self.pos)]
            if  self.reverse == self.invert:
                d=self.otherDir(self.direction)
            else:
                d=self.direction
       # d=self.direction
            return [Line(self.last().end(), astart),
                    Arc(astart, aend, self.cp1, d)]

    def start(self):
        lastpoint=self.lastorigin()
        if not self.setup:
            if self.next().pos==False:
                return self.pos
                print("ERROR: next().pos="+str(self.next().pos))
            print("NO setup start()")
            self._setup()
        if self.radius==0:
            return self.pos
        if not self.cp1==self.pos:
            return self.lineArcIntersect(self.pos, lastpoint, self.cp1, self.radius)
        else:
            return self.pos+(lastpoint-self.pos).normalize()*self.radius

    def end(self):
        nextpoint=self.nextorigin()
        if not self.setup:
            self._setup()
        if not self.setup:
            if self.next().pos is False:
                print("ERROR: next().pos="+str(self.next().pos))
            print("NO setup end()"+str(self))
            return self.next().pos
        if self.radius==0:
            return self.pos
        if not self.cp1==self.pos:
            a= self.lineArcIntersect(self.pos, nextpoint, self.cp1, self.radius)
            if a is False or a is None:
                print("ERROR:LAI nextpoint="+str(nextpoint)+" rad="+str(self.radius)+" self.pos"+str(self.pos))
                return self.pos
        else:
            a= self.pos+(nextpoint-self.pos).normalize()*self.radius
            if a is False or a is None:
                print("ERROR: nextpoint="+str(nextpoint)+" rad="+str(self.radius)+" self.pos"+str(self.pos))
                return self.pos
        return a
    def origin(self, forward=True):
        return self.pos
        if forward:
            op=self.last().pos
        else:
            op=self.next().pos
        vecin=(op-self.pos).normalize()
        if (self.direction=='cw' and self.reverse==False or self.direction=='ccw' and self.reverse==True)==forward:
            return op+rotate(vecin,-90)
        else:
            return op+rotate(vecin,90)


class PInsharp(PAroundcurve):
    def __init__(self, pos, transform=False):
        """Create a point which will head for point pos and then add an arc around the point centre with a radius=radius. Useful for adding ears around screw holes. if centre is not specified it is assumed it is the same as pos"""
        self.init()
        self.pos=Vec(pos)
        self.point_type='insharp'
       # self.radius=radius
        self.direction=False
        self.transform=transform
        self.obType="Point"
        self.config = {'cutterrad':0}
        self.radius = 0
        self.cp1=pos
        self.dosetup=False
    def copy(self):
        t= PInsharp( self.pos, self.transform)
        t.reverse=self.reverse
        t.lastpoint=self.lastpoint
        t.nextpoint=self.nextpoint
        t.forcelastpoint = self.lastpoint
        t.forcenextpoint = self.nextpoint
        t.invert = self.invert
        return t
    def _setup(self):
        if not self.setup:
            self.direction=False
            self.setDirection()
            # for some reason this needs reversing - probably because setDirection reverses the direction and it will happen again in Aroundcurve
            if not self.reverse:
                self.direction=self.otherDir(self.direction)
#                       self.direction=self.otherDir(self.direction)
            if self.dosetup and self.config is not False and  self.last() != None and next(self) !=None:
                self.setup=True
                lastpoint=self.lastorigin()
                if lastpoint==self.pos:
                    lastpoint=self.last().lastorigin()
                nextpoint=self.nextorigin()
                if nextpoint==self.pos:
                    nextpoint=self.next().nextorigin()
                angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
                if abs(angle-180)>0.00001 and abs(angle)>0.00001:
                    d=self.config['original_cutter']['cutterrad']*(1/math.sin((180-angle)/2/180*math.pi)-1- 1.0/math.sin(angle/2/180*math.pi))
                    self.cp1=self.pos-(((lastpoint-self.pos).normalize()+(nextpoint-self.pos).normalize())/2).normalize()*d
                else:
                    self.cp1 = self.pos
                if ( self.config['cutside']=='right' and self.direction=='cw' or self.config['cutside']=='left' and self.direction=='ccw') == self.reverse or abs(angle<0.01):
                    self.radius=0
                else:
                    self.radius = self.config['original_cutter']['cutterrad']
#                               print str(self.pos)+"self.cofig side="+self.config['cutside'] + " angle="+str(angle)+ " direction="+self.direction+ " reverse="+str(self.reverse)+" radius="+str(self.radius)

class PIncurve(PSharp):
    def __init__(self, pos, radius=0, direction=False, transform=False):
        """Create a point at position=pos which is then rounded off wot a rad=raidius, as if it were a piece of wood you have sanded off"""
        self.init()
        self.pos=Vec(pos)
        self.point_type='incurve'
        self.radius=radius
        self.direction=direction
        self.transform=transform
        self.obType="Point"
        self.sharp = False
    def copy(self):
        t= PIncurve( self.pos, self.radius, self.direction, self.transform)
        t.reverse=self.reverse
        t.lastpoint=self.lastpoint
        t.nextpoint=self.nextpoint
        t.forcelastpoint = self.lastpoint
        t.forcenextpoint = self.nextpoint
        t.invert = self.invert
        return t
    def origin(self, forward=True):
        self._setup()
        return self.pos
    def end(self):
        self._setup()
        lastpoint=self.lastorigin()
        nextpoint=self.nextorigin()
        angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
        dl=self.radius*math.tan((angle/180)/2*math.pi)
        if angle==180 or angle==0:
            print("STRAIGHT LINE")
            return self.pos
        return self.pos+(nextpoint-self.pos).normalize()*dl
    def start(self):
        lastpoint=self.lastorigin()
        nextpoint=self.nextorigin()
        angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
        dl=self.radius*math.tan((angle/180)/2*math.pi)
        if angle==180 or angle==0:
            print("STRAIGHT LINE")
            return self.pos
        return self.pos+(lastpoint-self.pos).normalize()*dl
    def offset(self, side, distance, direction):
        self._setup()
        self.setangle()
        t=copy.copy(self)
        if self.corner_side(side, direction)=='external':
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
        self._setup()
        if self.last() != None and next(self) !=None:
            lastpoint=self.lastorigin()
            nextpoint=self.nextorigin()
            angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
            dl=self.radius*math.tan((angle/180)/2*math.pi)
            startcurve=self.pos-(self.pos-lastpoint).normalize()*dl
            endcurve = self.pos+(nextpoint-self.pos).normalize()*dl
            # If these are straight there should be no curve or the maths blows up so just behave like a normal point
            if(((startcurve + endcurve)/2-self.pos).length()<0.001 or angle==0 or angle==180):
                return [Line(self.last().end(),self.pos)]
            else:
                d = math.sqrt(dl*dl+self.radius*self.radius)/((startcurve + endcurve)/2-self.pos).length()
                centre = self.pos + ((startcurve + endcurve)/2-self.pos)*d

# this may break insharps
#                                tempdir=(self.pos-self.last().end()).cross(nextpoint-self.pos)
                tempdir=(self.pos-lastpoint).cross(nextpoint-self.pos)
                if tempdir[2]>0:
                    tempd='cw'
                elif tempdir[2]<0:
                    tempd='ccw'
                else:
                    tempd='cw'
                if( endcurve-startcurve).length()>0.01:
                    return [
                         Line(self.last().end(),startcurve),
                         Arc(startcurve, endcurve, centre,tempd),
                 ]
                else:
                    return [Line(self.last().end(),startcurve),
                            Line(startcurve,endcurve)]
            frompoint=endcurve
        elif next(self)==None:
            return [Line(self.last().origin(), self.pos)]
        else:
            return []


class PSmoothArc(PIncurve):
    def __init__(self, pos=False, radius=0, direction=False, transform=False):
        """Create a point at position=pos which is then rounded off wot a rad=raidius, as if it were a piece of wood you have sanded off"""
        self.init()
#                self.pos=Vec(pos)
        self.point_type='incurve'
        self.pos=None
        self.direction=False
        self.transform = transform
#                self.radius=radius
#                self.direction=direction
#                self.transform=transform
        self.obType="Point"
    def copy(self):
        if self.setup:
            t= PIncurve( self.pos, self.radius, self.direction, self.transform)
        else:
            t= PSmoothArc(transform=self.transform)
        t.reverse=self.reverse
        t.lastpoint=self.lastpoint
        t.nextpoint=self.nextpoint
        t.forcelastpoint = self.lastpoint
        t.forcenextpoint = self.nextpoint
        t.invert = self.invert
        return t
    def _setup(self):
        if not self.setup:
            lastvec=self.last().pos-self.last().lastorigin()
#                        rlastvec=rotate(lastvec,90)
            nextvec=self.next().pos-self.next().nextorigin()
 #                       rnextvec=rotate(nextvec,90)
            self.pos = self.next().pos.intersect_lines(self.last().pos, self.last().lastorigin(), self.next().pos, self.next().nextorigin())
            dot=lastvec.normalize().dot(nextvec.normalize())
            if dot>=1:
                angle = 0
            elif dot<=-1:
                angle = math.pi
            else:
                angle = math.acos(dot)

            d = min((self.pos-self.next().pos).length(), (self.pos-self.last().pos).length())
            self.radius = d * math.tan(angle/2)
            self.setup=True

class PChamfer(Point):
    def __init__(self, pos, chamfer=0, radius=0, direction=False, transform=False):
        """Create a chamfered point at position=pos, with the end cut off straight to a radius radius"""
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
            print("Chamfer is larger than the distance to the previous point")
        if outvec.length()<self.radius:
            print("Chamfer is larger than the distance to the next point")
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
        pass
        self.pos+outvec.normalize()*self.radius
    def makeSegment(self, config):
        pass

class POutcurve(Point):
    def __init__(self, pos, radius=0, direction=False, transform=False):
        """Create an arc centred at position=pos with lines going towards and away from it at a tangent. """
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
        t.invert = self.invert
        return t
    def origin(self, forward=True):
        seg=self.makeSegment({'findOrigin':True})
        if forward == self.reverse:
            return seg[1].cutfrom
        else:
            return seg[1].cutto
    def end(self):
        if hasattr(self, 'endpos'):
            return self.endpos
        else:
            seg=self.makeSegment({'findOrigin':True})
            return seg[1].cutto
    def start(self):
        if hasattr(self, 'startpos'):
            return self.startpos
        lastpoint=self.lastorigin()
        nextpoint=self.nextorigin()
        angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
        dl=self.radius*math.tan((angle/180)/2*math.pi)
        return self.pos+(lastpoint-self.pos).normalize()*dl
    def offset(self, side, distance, direction):
        t=copy.copy(self)
        self.setangle()
        if self.direction in ['cw', 'ccw']:
            if (self.direction == 'cw') == (side=='left'):
                extint='external'
            else:
                extint='internal'
        else:
            extint= self.corner_side(side, direction)
        if extint =='external':
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
#                       t=d
#                       d=r
#                       r=t
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
    def getDirection(self):
        if self.direction:
            if self.reverse !=self.invert:
                if self.direction=='cw':
                    return 'ccw'
                else:
                    return 'cw'
            else:
                return self.direction
        else:
            return self.direction

    def makeSegment(self, config):
        segment_array=[]
        sd = self.direction
        if self.last().point_type=='outcurve':
            lr=self.last().radius
        else:
            lr=0
        if self.last() is not None and self.last().point_type not in ['sharp', 'outcurve', 'clear', 'doubleclear', 'incurve', 'insharp']:

            print("Outcurve must be preceeded by a sharp point or another outcurve not a "+str(self.last().point_type))
            return []
        if lr!=0:
            if type(self.last().last()) == None:
                print("OUtcurve must be preceeded by 2 points if previous point is outcurce")
            if(self.last().getDirection()):
                d1=self.last().getDirection()
            elif (self.last().pos-self.last().last().pos).cross(self.pos-self.last().pos)[2] <0:
                d1='cw'
            else:
                d1='ccw'
        else:
            # if lr=0 we don't care about the direction
            d1='cw'
        if self.getDirection():
            d2=self.getDirection()
        elif (self.pos-self.last().pos).cross(self.next().pos-self.pos)[2] <0:
            d2='cw'
        else:
            d2='ccw'
        p1=self.tangent_points( self.last().pos, lr, d1, self.pos, self.radius, d2)
    #        segment_array.append( Line(p1[0], p1[1]))
        if 'findOrigin' in config and config['findOrigin']:
            segment_array.append( Line(p1[0], p1[1]))
        else:
            #segment_array.append( Line(p1[0], p1[1]))
            segment_array.append( Line(self.last().origin(not self.reverse), p1[1]))
        d3=''
        if self.next().point_type=="outcurve":
#                        if (self.nextorigin()-self.pos).cross(self.next().nextorigin()-self.nextorigin())[2] <0:
            if self.next().getDirection():
                d3=self.next().getDirection()
            elif (self.next().pos-self.pos).cross(self.next().next().pos-self.next().pos)[2] <0:
                d3='cw'
            else:
                d3='ccw'
            p2=self.tangent_points( self.pos, self.radius, d2, self.next().pos, self.next().radius, d3)
            segment_array.append( Arc( p1[1],p2[0], self.pos, self.otherDir(d2)))
            self.endpos=p2[0]
        else:

            p2 = self.tangent_point(self.next().pos, self.pos, self.radius, self.otherDir(d2))
            segment_array.append( Arc( p1[1],p2, self.pos, self.otherDir(d2)))
            self.endpos=p2
        self.startpos = p1
        return segment_array

class PClear(PSharp):
    def __init__(self, pos, transform=False):
        """Create a sharp point at position=pos with an extra cut so that a sharp corner will fit inside it"""
        self.init()
        self.pos=Vec(pos)
        self.point_type='clear'
        self.transform=transform
        self.obType="Point"
        self.sharp = True
    def copy(self):
        t = PClear( self.pos, self.transform)
        t.lastpoint=self.lastpoint
        t.nextpoint=self.nextpoint
        t.reverse=self.reverse
        t.invert = self.invert
        return t
    def makeSegment(self, config):
        if self.last() != None and next(self) !=None:
            lastpoint=self.lastorigin()
            if lastpoint==self.pos:
                lastpoint=self.last().lastorigin()
            nextpoint=self.nextorigin()
            if nextpoint==self.pos:
                nextpoint=self.next().nextorigin()
            angle=(self.pos-lastpoint).angle(nextpoint-self.pos)
            if abs(angle-180)>0.00001:
                d=config['cutterrad']*(1/math.sin((180-angle)/2/180*math.pi)-1)

                extrapoint=self.pos-(((lastpoint-self.pos).normalize()+(nextpoint-self.pos).normalize())/2).normalize()*d
            else:
                return [Line(self.last().end(),self.pos)]

        return [
                Line(self.last().end(),self.pos),
                Line(self.pos,extrapoint),
                Line(extrapoint,self.pos),
        ]

class PDoubleClear(Point):
    def __init__(self, pos, transform=False):
        """Create a sharp point at position=pos with a cut on inside and out so it definitely clears all the material - useful for filling shapes"""
        self.init()
        self.pos=Vec(pos)
        self.point_type='doubleclear'
        self.transform=transform
        self.obType="Point"
        self.sharp = True
    def copy(self):
        t = PDoubleClear( self.pos, self.transform)
        t.lastpoint=self.lastpoint
        t.nextpoint=self.nextpoint
        t.forcelastpoint = self.lastpoint
        t.forcenextpoint = self.nextpoint
        t.reverse=self.reverse
        t.invert = self.invert
        return t
    def makeSegment(self, config):
        if self.last() != None and next(self) !=None:
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
        t.invert = self.invert
        return t
    def origin(self, forward=True):
        return self.pos
    def end(self):
        return self.next().pos
    def start(self):
        return self.last().pos
    def offset(self, direction, distance, pointlist):
        print("can't do bezier offset")

        return []

    def makeSegment(self, config):
        if self.last().point_type=='sharp' and self.next().point_type=='sharp':
            #quadratic
            return [Quad(self.last().pos, self.next().pos, self.pos)]
        elif self.last().last().point_type=='sharp' and self.last().point_type=='bcontrol' and self.next().point_type=='sharp':
            #cubic
            return [Cubic(self.last().last().end(), self.last().pos, self.pos, self.next().pos)]
        elif self.next().point_type=='bcontrol':
            return []
        else:
            print("Beiziers should be one or two bcontrol points flanked by sharp points")
            return []

class PArc(Point):
    def __init__(self, pos=None, radius=None, direction=None, length=False, transform=False):
        """Create a sharp point at position=pos
radius - arc radius, direction - direction of arc, length - [short, long]
Will try to guess the type of arc you have specified if insufficiently specified
Must have sharp points either side of it
If it can't reach either point with the arc, it will join up to them perpendicularly to the arc with straight lines
"""
        self.init()
        self.pos=pos
        self.radius=radius
        self.direction=direction
        self.length=length
        self.transform=transform
        self.point_type='arc'
        self.control = False#True
        self.dirpoint = False
        self.obType='Point'
    def copy(self):
        t = PArc( self.pos, self.radius, self.direction,self.length, self.transform)
        t.lastpoint=self.lastpoint
        t.nextpoint=self.nextpoint
        t.forcelastpoint = self.lastpoint
        t.forcenextpoint = self.nextpoint
        t.reverse=self.reverse
        t.invert = self.invert
        return t

    def checkArc(self):
        if self.pos is not None and self.radius is not False:
            if(self.direction is None):
                self.setangle()
                if self.angle>0:
                    self.direction='ccw'
                else:
                    self.direction='cw'
            if (self.pos-self.last().pos).length()-self.radius>000.1 or (self.next().pos-self.pos).length()-self.radius>0.001:
                pass
               #      print "Arc's radius should be <= distance to the centre"+str(self.next().pos)+"->"+str(self.pos)+"->"+str(self.last().pos)+" radius="+str(self.radius)+" AC-radius="+str((self.pos-self.last().pos).length()-self.radius)+" BC-raiuds="+str((self.next().pos-self.pos).length()-self.radius)
        elif self.radius is not False and self.length is not False and self.pos is None:

            l=self.nextorigin() - self.lastorigin()
            b=math.sqrt(self.radius**2-l.length()**2/4)

            if l.length()>2*self.radius:
                print("Can't make an arc longer than twice its radius")
            if (self.direction=='cw' and self.reverse or self.direction=='ccw' and not self.reverse) !=self.invert:
                perp=rotate(l.normalize(),-90)
            else:
                perp=rotate(l.normalize(),90)
            self.pos = self.last().pos + l/2 + perp * b
#                       self.pos = self.last().pos + l/2 - perp * b
        elif self.pos is not None:
            self.radius=min((self.next().pos-self.pos).length(), (self.pos- self.last().pos).length())
    def makeSegment(self, config):
        self.checkArc()
        if self.last().point_type not in ['sharp', 'clear', 'doubleclear', 'insharp'] or self.next().point_type not in ['sharp', 'clear', 'doubleclear', 'insharp']:
            print("points either side of an Arc should be sharp"+str(self.next().point_type)+" "+str(self.last().point_type))
            return []
        else:
            l=self.next().pos - self.last().pos
            perp=rotate(l.normalize(),-90)
            centre=self.pos.intersect_lines(self.last().pos, self.next().pos, self.pos, self.pos+perp)
            if self.radius**2 - (self.pos-centre).length()**2 >0:
                c=math.sqrt(self.radius**2 - (self.pos-centre).length()**2)
                a = l.normalize()*c
                if  self.reverse != self.invert:
                    d=self.direction
                else:
                    d=self.otherDir(self.direction)
                return [ Line(self.last().pos, centre-a), Arc(centre-a, centre+a, self.pos, d), Line(centre+a, self.next().pos)]
            else:
                return [ Line(self.last().pos, centre), Line(centre, self.next().pos)]

    def origin(self, forward=True):
        self.checkArc()
        if forward:
            op=self.last().pos
            r=-self.pos+self.last().pos
        else:
            op=self.next().pos
            r=-self.pos+self.next().pos
        if abs(r.length()-self.radius)<0.001:
            vecin=r.normalize()*20
            if (self.direction=='cw' and self.reverse==self.invert or self.direction=='ccw' and self.reverse!=self.invert)==forward:
                return op+rotate(vecin,90)
            else:
                return op+rotate(vecin,-90)
        else:
            if forward:
                return self.next().pos
            else:
                return self.last().pos

    def end(self):
        self.checkArc()
        l=self.next().pos - self.last().pos
        perp=rotate(l.normalize(),-90)
        centre=self.pos.intersect_lines(self.last().pos, self.next().pos, self.pos, self.pos+perp)
        if self.radius**2 - (self.pos-centre).length()**2 > 0:
            c=math.sqrt(self.radius**2 - (self.pos-centre).length()**2)
            a = l.normalize()*c
            return centre+a
        else:
            return centre
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
        if (side=='left' and self.direction=='cw' or side=='right' and self.direction=='ccw')!=self.invert:
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
        self.radius=float(radius)
        self.transform=transform
        self.point_type='circle'
        self.obType='Point'
    def copy(self):
        t= PCircle( self.pos, self.radius,  self.transform)
        t.lastpoint=self.lastpoint
        t.nextpoint=self.nextpoint
        t.reverse=self.reverse
        t.invert = self.invert
        return t
    def makeSegment(self, config):
        r1 = V(self.radius, 0)
        r2 = V(0, self.radius)
        if self.reverse:
            return [
            Arc(self.pos-r1, self.pos-r2, self.pos, 'cw'),
            Arc(self.pos-r2, self.pos+r1, self.pos, 'cw'),
            Arc(self.pos+r1, self.pos+r2, self.pos, 'cw'),
            Arc(self.pos+r2, self.pos-r1, self.pos, 'cw') ]
        else:
            ret = [
            Arc(self.pos-r1, self.pos+r2, self.pos, 'ccw'),
            Arc(self.pos+r2, self.pos+r1, self.pos, 'ccw'),
            Arc(self.pos+r1, self.pos-r2, self.pos, 'ccw'),
            Arc(self.pos-r2, self.pos-r1, self.pos, 'ccw') ]
            return ret
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
