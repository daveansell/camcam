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



import math
from minivec import *

def V(x=False,y=False,z=False):
        if x==False:
                x=0
        if y==False:
                y=False
        if z==False:
                z=False
        return Vec(x,y,z)

def rotate(pos, a, *config):
	if len(config):
		axis = config[0]
	else:
		axis = V(0,0,-1)

        if type(pos) is Vec:
                M=Mat(1).rotateAxis(a, axis)
                pos=pos.transform(M)
                return pos
        else:
                return False

class Segment(object):
	seg_types = {}
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
		else:
			return getattr(self, self.seg_types[mode])(direction)
#                if mode=='gcode':
 #                       temp=self.gcode(direction)
  #                      if len(temp)>0 and zfrom!=zto:
   #                             temp[0]['Z']=zto
    #                    return temp
     #           elif mode=='simplegcode' or mode=='scr':
      #                  temp=self.simplegcode(zfrom, zto, direction)
       #                 return temp
        #        else:
         #               return self.seg_types[mode](direction) 
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
                        return [{"cmd":"G1","X":self.cutto[0],"Y":self.cutto[1], "Z":self.cutto[2]}]
                else:
                        return [{"cmd":"G1","X":self.cutfrom[0],"Y":self.cutfrom[1],"Z":self.cutfrom[2]}]
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
                        print Warning( "Arc of zero length")
                        return []
                if( not  direction):
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
                tempcross=(self.centre-self.cutfrom).cross(self.cutto-self.centre)
                t=tempcross[2]
                #if (t>0 and direction=='cw' or t<0 and direction=='ccw')!=(self.direction=='cw'):
                if (t>0 and self.direction=='ccw' or t<0 and self.direction=='cw'):#!=(self.direction=='cw'):
#		if (t<0):
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
#                       return [{'cmd':'L',"x":self.centre[0],"y":self.centre[1]},{'cmd':'L',"x":self.cutfrom[0],"y":self.cutfrom[1]},{"cmd":"A","rx":r,"ry":r,"x":self.cutto[0],"y":self.cutto[1], '_lf':longflag,'_rot':0,'_dir':dirflag}] 
                else:
                        return [{"cmd":"A","rx":r,"ry":r,"x":self.cutfrom[0],"y":self.cutfrom[1], '_lf':longflag,'_rot':0,'_dir':dirflag}]
#                       return [{'cmd':'L',"x":self.centre[0],"y":self.centre[1]},{'cmd':'L',"x":self.cutto[0],"y":self.cutto[1]},{"cmd":"A","rx":r,"ry":r,"x":self.cutfrom[0],"y":self.cutfrom[1], '_lf':longflag,'_rot':0,'_dir':dirflag}] 
        def polygon(self,resolution=1, direction=1):
                if direction:
                        cutfrom=self.cutfrom
                        cutto=self.cutto
                else:
                        cutfrom=self.cutto
                        cutto=self.cutfrom
                r1 = cutfrom-self.centre
                r2 = cutto-self.centre
		if r1.length()==0 or r2.length()==0:
			return []
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
                              #  points.append(cutto)
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
        def gcode(self,direction=True):
                if(direction):
                        offset = self.cp - self.cutfrom
                        return [{"cmd":"G5.1", "X":self.cutto[0], "Y":self.cutto[1], "I":offset[0], "J":offset[1]}]
                else:
                        offset = self.cp - self.cutto
                        return [{"cmd":"G5.1", "X":self.cutfrom[0], "Y":self.cutfrom[1], "I":offset[0], "J":offset[1]}]
        def svg(self,direction = True):
                if(direction):
                        offset = self.cp - self.cutfrom
                        return [{"cmd":"Q", "x1":self.cutto[0], "y1":self.cutto[1], "x":offset[0], "y":offset[1]}]
                else:
                        offset = self.cp - self.cutto
                        return [{"cmd":"Q", "x1":self.cutfrom[0], "y1":self.cutfrom[1], "x":offset[0], "y":offset[1]}]

        def polygon(self,resolution=1, direction=1):
                p0=self.cutfrom
                p1=self.cp
                p2=self.cutto
                ret=[]
#		print str(p0)+"->"+str(p1)+"->"+str(p2)
#		print (p2-p1).length()
#		print (p1-p0).length()
                numsteps = int(((p2-p1).length()+(p1-p0).length())/float(resolution))
#		print ((p2-p1).length()+(p1-p0).length())
		if numsteps<3:
			numsteps=3
                step = 1.0/float(numsteps)
                for i in range(1,numsteps-1):
                        t=float(i)*step
                        ret.append((1-t)*(1-t)*p0 + 2*(1-t)*t*p1 + t*t*p2 )
                return ret

class Cubic(Segment):
        def __init__(self, cutfrom, cutto, cp1, cp2):
                self.seg_type='cubic'
                self.cutto=cutto
                self.cutfrom=cutfrom
                self.cp1=cp1
                self.cp2=cp2

        def gcode(self,direction=True):
                if(direction):
                        offset1 = cp1 - self.cutfrom
                        offset2 = cp2 - self.cutfrom
                        return [{"cmd":"G5", "X":self.cutto[0], "Y":self.cutto[1], "I":offset1[0], "J":offset1[1], "P":offset2[0], "Q":offset2[1]}]
                else:
                        offset1 = cp2 - self.cutto
                        offset2 = cp1 - self.cutto
                        return [{"cmd":"G5", "X":self.cutfrom[0], "Y":self.cutfrom[1], "I":offset1[0], "J":offset1[1], "P":offset2[0], "Q":offset2[1]}]
        def svg(self,direction = True):
                if(direction):
                        return [{"cmd":"Q", "x2":self.cutto[0], "y2":self.cutto[1], "x1":self.cp1[0], "y1":self.cp1[1], "x":self.cp2[0], "y":self.cp2[1]}]
                else:
                        return [{"cmd":"Q", "x2":self.cutfrom[0], "y2":self.cutfrom[1], "x1":self.cp2[0], "y1":self.cp2[1], "x":self.cp1[0], "y":self.cp1[1]}]

        def polygon(self,resolution=1, direction=1):
                p0=self.cutfrom
                p1=self.cp1
                p2=self.cp2
                p3=self.cutto
                ret=[]
                numsteps = int(((p3-p2).length()+(p2-p1).length()+(p1-p0).length())/resolution)
                step = 1.0/float(numsteps)
                for i in range(1,numsteps-1):
                        t=i*step
                        ret.append((1-t)*(1-t)*(1-t)*p0 + 3*(1-t)*(1-t)*t*p1 + 3*(1-t)*t*t +  t*t*t*p3 )
                return ret



