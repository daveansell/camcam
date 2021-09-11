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

import os
import math
import shapely.geometry
import shapely.ops

from minivec import Vec, Mat
import Milling
import pprint
import copy
import collections
import traceback
import re
from point import *
from segments import *
spindleDir = False
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
                'forcecutter':'force the cutter - normally for laser cutting around once',
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
                'input_direction':'force the direction it thinks you inputted the points in',
                'extrude_scale': ' If shape is not same size at bottom as top this is the scaling factor',
                'extrude_centre':'centre of extrusion',
                'zoffset':'offset z=0 in 3D modes',
                'isback':'is a back',
                'no_mirror':'don\'t mirror',
                'part_thickness':'thickness of part',
                'use_point_z':'use point z  for 3D cuts',
                'clear_height':'how far up the cutter should go to clear things',
                'finishdepth':'last cut thickness',
                'sidefeed':'sidefeed',
}
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


# Interpolate between p1 and p2
# x - return point on line where x=x
# y - retruen point on line where y=y
# dist - return point xy dist along line from p1
# prop - return point xy which is a proportion of the way from p1 to p2
def interpolate(p1, p2, **config):
    i=0;
    j=1;
    
    if 'i' in config:
        i=config['i']
    if 'j' in config:
        j=config['j']
    if 'x' in config:
        d=p2-p1
        t=[0,0,0]
        t[j]=d[j]/d[i]
        a=Vec(t)
        t=[0,0,0]
        t[i]=1
        xdir = Vec(t)
        return p1 + a*(config['x']-p1[i]) + (config['x']-p1[i])*xdir

    elif 'y' in config:
        d=p2-p1
        t=[0,0,0]
        t[i]=d[i]/d[j]
        a=Vec(t)
        t=[0,0,0]
        t[j]=1
        ydir = Vec(t)
        return p1 + a*(config['y']-p1[j]) + (config['y']-p1[j])*ydir

    elif 'dist' in config:
        a = (p2-p1).normalize()
        return p1+a*config['dist']

    elif 'prop' in config:
        return config['prop']*p2+ (1-config['prop'])*p1

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
        self.transform=[]
        self.otherargs=''
        varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter', 'partial_fill','fill_direction','finishing', 'input_direction', 'extrude_scale', 'extrude_centre', 'zoffset', 'isback', 'no_mirror','use_point_z','clear_height', 'finishdepth', 'sidefeed', 'blendTolerance', 'vertfeed', 'downmode', 'blendTolerance','finalpass']
        if hasattr(self, 'varlist') and type(self.varlist) is list:
            self.varlist+=varlist
        else:
            self.varlist=varlist
        for v in self.varlist:
            if v in config:
                setattr(self,v, config[v])
            else:
                setattr(self,v, None)
#                        self.otherargs+=':param v: '+arg_meanings[v]+"\n"
        self.start=False
        self.extents= {}
        self.output=[]
        self.boundingBox={}
        self.centre=V(0,0)
        self.polygon={}
        self.changed={}
        self.input_direction=False
        self.parent=False
        self.blendTolerance=0
        self.comment("start:"+str(type(self)))

    def __deepcopy__(self,memo):
        obj_copy = object.__new__(type(self))
    #       obj_copy.__dict__ = self.__dict__.copy()
        for v in self.__dict__:
            if v=='parent':# or v=='points':
                obj_copy.__dict__[v]=copy.copy(self.__dict__[v])
            elif v=='points':
                obj_copy.__dict__[v]=[]
                for k in self.__dict__[v]:
                    obj_copy.__dict__[v].append(copy.copy(k))
            else:
                obj_copy.__dict__[v]=copy.deepcopy(self.__dict__[v],memo)

        return obj_copy


    def comment(self, comment):
        comment = "".join(x for x in comment if x.isalnum() or x in '-._ ')
        self.add_out([{'_comment':str(comment)}])

    def overwrite(self,ain,b):
        a=copy.copy(ain)
        for i in list(b.keys()):
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
        #       if type(b['transform']) is list:
            a['transformations'].append(b['transform'])
        return a
#               for i in b.keys():
#                       if b[i] is not False and b[i] is not None:
#                               a[i] = b[i]
#                       if (b[i] is False or b[i] is None ) and i not in a:
#                               a[i] = None

    def blendTolerance(self, tolerance):
        self.blendTolerance=tolerance

    def rotate(self,pos, angle):
        if self.transform==False or self.transform==None:
            self.transform=[]
        self.transform.append({'rotate':[pos, angle]})

    def mirror(self, pos, dirvec):
        if self.transform==False or self.transform==None:
            self.transform=[]
        self.transform.append({'mirror':[pos,dirvec]})

    def translate(self,vec):
        if self.transform is False or self.transform is None:
            self.transform=[]
        self.transform.append({'translate':vec})

    def set_cutter(self, config):
        if 'forcecutter' in config and config['forcecutter'] is not None:
            cutter = config['forcecutter']
        elif 'partcutter' in config and config['partcutter'] is not None:
            print ("Partcutter="+str(config['partcutter']))
            cutter = config['partcutter']
        else:
            cutter=config['cutter']
        if cutter in milling.tools:
            tool=milling.tools[cutter]
            config['cutterrad']=float(tool['diameter'])/2
            config['endcut']=tool['endcut']
            config['sidecut']=tool['sidecut']
            if tool['sidecut']==0:
                config['downmode']='cutdown'
            elif 'downmode' not in config:
                config['downmode']='ramp'
            if 'forcestepdown' in tool:
                config['forcestepdown'] = tool['forcestepdown']
            if 'handedness' in tool:
                config['handedness'] = tool['handedness']
        if config['cutter'] in milling.tools:
            tool=milling.tools[config['cutter']]
            c={}
            c['cutterrad']=float(tool['diameter'])/2
            c['endcut']=tool['endcut']
            c['sidecut']=tool['sidecut']
            if tool['sidecut']==0:
                c['downmode']='cutdown'
            elif 'downmode' in config:
                c['downmode']=config['downmode']
            else:
                c['downmode']='ramp'
            config['original_cutter']=c
        if 'vertfeed' in config and config['vertfeed']:
            config['vertfeed'] *= tool['diameter']/4.0
        if 'stepdown' in config and config['stepdown']:
            config['stepdown'] *= tool['diameter']/4.0
        if 'sidefeed' in config and config['sidefeed']:
            config['sidefeed'] *= tool['diameter']/4.0

    def set_material(self, config):
        if config['material'] in milling.materials:
            mat=milling.materials[config['material']]
            config['vertfeed']=mat['vertfeed']
            if 'sidefeed' not in config or config['sidefeed'] is None:
                config['sidefeed']=mat['sidefeed']
            if 'stepdown' not in config or type(config['stepdown']) is not int and type(config['stepdown']) is not float:
                config['stepdown']=mat['stepdown']
            config['kress_setting']=mat['kress_setting']
            if 'mill_dir' in mat:
                config['mill_dir']=mat['mill_dir']
            else:
                config['mill_dir']='up'
            if 'spring' in mat:
                config['spring']=mat['spring']
            else:
                config['spring']=0
        else:
            if config['material'] is not None:
                raise ValueError("Unknown Material "+str(config['material'])+"\n"+str(self.trace))
            else:
                config['mill_dir']='up'
    def add_point(self,pos, point_type='sharp', radius=0, cp1=False, cp2=False, direction=False, transform=False):
        if hasattr(pos,'obType') and pos.obType=='Point':
            self.points.append(pos)
        else:
            self.points.append(self.make_point(pos, point_type, radius,cp1, cp2, direction, transform))
        self.has_changed()
        self.points[-1].path=self
        l = len(self.points)
        if self.closed:
            self.points[0].lastpoint = self.points[-1]
            self.points[-1].nextpoint = self.points[0]
            self.points[-2%l].nextpoint = self.points[-1]
            self.points[-1].lastpoint = self.points[-2%l]
        else:
            self.points[-1].lastpoint = self.points[-2%l]
            self.points[-1].nextpoint = self.points[-2%l]
            self.points[-1].nextpoint = self.points[-2%l]
            self.points[-2%l].nextpoint = self.points[-1]
            self.points[-2%l].lastpoint = self.points[-3%l]
    def insert_point(self,  pos, point):
        self.points.insert(pos, point)
        self.reset_points()
    def reset_points(self, pointlist=False):
        if pointlist==False:
            pointlist=self.points
        for p in range(0, len(pointlist)):
            l = len(self.points)
            pointlist[p].path=self
            pointlist[p].i = p
            if self.closed==True:
                pointlist[p].nextpoint = pointlist[(p+1)%l]
                pointlist[p].lastpoint = pointlist[(p-1)%l]
            else:
                if p==0:
                    if l>1:
                        pointlist[p].lastpoint = pointlist[1]
                    else:
                        pointlist[p].lastpoint = pointlist[0]
                else:
                    pointlist[p].lastpoint = pointlist[p-1]
                if p==l-1:
                    if l>1:
                        pointlist[p].nextpoint = pointlist[l-2]
                    else:
                        pointlist[p].nextpoint = pointlist[0]
                else:
                    pointlist[p].nextpoint = pointlist[p+1]

    def make_point(self,pos, point_type='sharp', radius=0, cp1=False, cp2=False, direction=False, transform=False):
        if point_type=='sharp':
            return PSharp(pos, transform=transform)
        elif point_type=='incurve':
            return PIncurve(pos, radius, direction, transform=transform)
        elif point_type=='chamfer':
            return PChamfer( pos, chamfer=cp1, radius=radius,  transform=transform)
        elif point_type=='outcurve':
            return POutcurve( pos, radius, direction, transform=transform)
        elif point_type=='clear':
            return PClear( pos, transform)
        elif point_type=='doubleclear':
            return PDoubleClear( pos, transform)
        elif point_type=='bcontrol':
            return PBezierControl( pos, transform)
        elif point_type=='arc':
            return PArc( pos, radius, direction, length=cp1)
        elif point_type=='circle':
            return PCircle(pos, radius)
        elif point_type=='arcend':
            return PSharp(pos, transform=transform)
        elif point_type=='aroundcurve':
            return PAroundcurve(pos, centre=pos, radius=radius, direction=direction, transform=transform)

    def prepend_point(self,pos, point_type='sharp', radius=0, cp1=False, cp2=False, direction=False, transform=False):
        self.has_changed()
        l = len(self.points)
        if hasattr(pos,'obType') and pos.obType=='Point':
            self.points.insert(0,pos)
        else:
            self.points.insert(0,self.make_point(pos, point_type, radius,cp1, cp2, direction, transform))
        self.has_changed()
        if self.closed:
            self.points[0].lastpoint = self.points[-1]
            self.points[-1].nextpoint = self.points[0]
            self.points[0].nextpoint = self.points[1%l]
            self.points[0].lastpoint = self.points[-1]
        else:
            self.points[0].lastpoint = self.points[1%l]
            self.points[0].nextpoint = self.points[1%l]
            self.points[1%l].lastpoint = self.points[0]


    def add_points(self,points, end='end', transform={}):
        c=0
        for p in points:
            if type(p) is Vec:
                p = PSharp(p)
            if hasattr(p,'obType') and p.obType=='Point':
                q = copy.deepcopy(p)
                q.transform=transform

                if end=='end':
                    self.points.append(q)
                elif end=='prepend':
                    self.points.insert(c,q)
                    c+=1
                else:
                    self.points.insert(0,q)
            else:
                raise TypeError( "add_points - adding a non-point "+str(type(p)))
        self.has_changed()
        self.reset_points()

    def get_bounding_box(self):
        self.polygonise()
        return self.boundingBox


    def get_last_vec(self,points=False):
        if points==False:
            points=self.points
        end=points[len(points)-1]
        start=False
        for p in range( len(points)-1, -1, -1):
            if type(points[p].pos) is Vec and type(end.pos) is Vec and points[p].pos !=end.pos:
                start=points[p]
                break
        return [start, end]
    def get_first_vec(self,points=False):
        if points==False:
            points=self.points
        start=points[0]
        end=False
        for p in range( 1, len(points)):
            if type(points[p].pos) is Vec and type(start.pos) is Vec and points[p] !=end:
                end=points[p]
                break
        return [start, end]

    def add_points_intersect(self, points):
        thisvec=self.get_last_vec()
        thatvec=self.get_first_vec(points)
        if thisvec[1].pos!=thatvec[0].pos and (thisvec[1].pos-thisvec[0].pos).dot(thatvec[1].pos-thatvec[0].pos) !=1:
            joint=self.intersect_lines(thisvec[0].pos,thisvec[1].pos, thatvec[0].pos, thatvec[1].pos)
            if joint is not False:
#               joint=self.intersect_lines(self.points[len(self.points)-2].pos, self.points[len(self.points)-1].pos, points[0].pos, points[1].pos)
                del(self.points[len(self.points)-1])
                self.points.append(PInsharp(joint))
#                       del(self.points[len(self.points)-1])
        for i in range(1, len(points)):
            self.points.append(points[i])
        self.reset_points()

    def close_intersect(self):
        joint=self.intersect_lines(self.points[len(self.points)-2].pos, self.points[len(self.points)-1].pos, self.points[0].pos, self.points[1].pos)
        if joint is not False:
            del(self.points[len(self.points)-1])

            self.points[0].pos=joint
            self.reset_points()

    def ccw(self, a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]);

    def intersects(self, ap, aq, bp, bq):
        if (self.ccw(ap, aq, bp) * self.ccw(ap, aq, bq) > 0):
            return False
        if (self.ccw(bp, bq, ap) * self.ccw(bp, bq, aq) > 0):
            return False
        return True;

    def self_intersects(self, points):
        ret=[]
        l=len(self.points)
        for i in range(0, len(points)):
            for j in range(i+1, len(points)):
                if self.intersects(points[i], points[(i-1)%l], points[j], points[(j-1)%l]):
                    intersection = self.intersect_lines(points[i], points[(i-1)%l], points[j], points[(j-1)%l])
                    if (intersection-points[i]).length()>0.01 and (intersection-points[(i-1)%l]).length()>0.01:
                        ret.append( [i,j, intersection])
        return ret


    def intersect_lines(self,a, b, c, d):
        # if the things we are trying to intersect are parallel we don't have to do any work
#               if abs((d-c).normalize().dot((b-a).normalize())) -1 <0.0001:
#                       return False
        if abs(a[0]-b[0])<0.001 and abs(a[1]-b[1])<0.001:
            return b
        if abs(c[1]-d[1])<0.001 and abs(c[0]-d[0])<0.001:
            return c
        # if the join point is in the same place
        if (b-c).length()<0.01:
            return b
        # if the denominator is zero the rest of this will explode because they don't intersect, so return false
        if ((a[0]-b[0])*(c[1]-d[1]) - (a[1]-b[1])*(c[0]-d[0]))==0:
            return False
        x= ((a[0]*b[1]-a[1]*b[0])*(c[0]-d[0]) - (a[0]-b[0])*(c[0]*d[1]-c[1]*d[0]) ) / ((a[0]-b[0])*(c[1]-d[1]) - (a[1]-b[1])*(c[0]-d[0]))
        y= ((a[0]*b[1]-a[1]*b[0])*(c[1]-d[1]) - (a[1]-b[1])*(c[0]*d[1]-c[1]*d[0]) ) / ((a[0]-b[0])*(c[1]-d[1]) - (a[1]-b[1])*(c[0]-d[0]))
        return V(x,y)

    def convertIntersection(self, intersection, default):
        if not intersection:
            intersection = default#V( endCut,val)
        elif type(intersection) is shapely.geometry.collection.GeometryCollection:
            intersection = V(intersection[0].x, intersection[0].y)
        elif type(intersection) is shapely.geometry.linestring.LineString:
            intersection = V(list(intersection.coords)[0][0],list(intersection.coords)[0][1] )
        elif type(intersection) is shapely.geometry.multipoint.MultiPoint:
            intersection = V(intersection[0].x, intersection[0].y)
        elif type(intersection) is Vec:
            intersection = intersection
        else:
            intersection = V(intersection.x, intersection.y)
        return intersection

    def convertToShapely(self,path):
        points = []
        if type(path) is list:
            for p in path:
                if type(p) is Vec:
                    points.append([p[0], p[1]])
                elif type(p) is list:
                    points.append(p)
                elif type(p) is Point:
                    points.append([p[0], p[1]])
            return shapely.geometry.LineString(points)
        else:
            path.makeShapely()
            return path.shapelyPolygon



    def findIntersection(self, path):
        self.convertToShapely(self)
        intersection = self.shapelyPolygon.intersection(self.convertToShapely(path))
        intersection = self.convertIntersection(intersection, False)
        return intersection


    def has_changed(self):
        for c in list(self.changed.keys()):
            self.changed[c]=True
    def transform_pointlist(self, pointlist,transformations):
        pout=[]

        for p in pointlist:
            # reset the pointlist
            p.invert=False

            pout.append(p.point_transform(transformations))
        self.reset_points(pout)
        return pout

    def make_segments(self, direction,segment_array,config):
        self.reset_points()
        self.simplify_points()
        pointlist = self.transform_pointlist(self.points,config['transformations'])
        self.reset_points(pointlist)
        if direction is None:
            self.isreversed=0
        elif direction!=self.find_direction(config):
            pointlist.reverse()
            # this is in the wrong sense as it will be run second in the reversed sense
            self.isreversed=1
        else:
            self.isreversed=0
        if self.side in ['left', 'right']:
            config['side'] = self.side
#               elif (((direction=='cw') == (self.mirrored>0))==(direction=='cw'))==(self.side=='in'):
        elif (((direction=='cw'))==(self.mirrored))==(self.side=='in'):
            config['cutside']='right'
        else:
            config['cutside']='left'
        numpoints=len(pointlist)
#                self.reset_points(pointlist)
        #if(self.closed):
    #               numpoints=len(pointlist)
    #       else:
    #               numpoints=len(pointlist)*2-2
#               for p,point in enumerate(pointlist):
        for p in range(0,numpoints):
            newsegments = pointlist[p].generateSegment(self.isreversed, config,p)
            segment_array.extend(newsegments)
        for s in segment_array:
            s.config=config
            s.parent=self
    #       else:
    #               for p in range(1, numpoints):
    #                       segment_array.extend(pointlist[p].generateSegment(self.isreversed, config))
#                       thispoint = pointlist[p]

    def otherDir(self,direction):
        if direction=='cw':
            return 'ccw'
        else:
            return 'cw'
# Find 2 points joined by a line from r1 from point1 and r2 from point2

    def delete_point(self,p):
        if p==0:
            if self.closed:
                self.points[p+1].lastpoint = self.points[len(self.points)-1]
                self.points[len(self.points)-1].nextpoint = self.points[p+1]
            else:
                self.points[1].lastpoint = self.points[2]
        elif p==len(self.points)-1:
            if self.closed:
                self.points[0].lastpoint = self.points[p-1]
                self.points[p-1].nextpoint = self.points[0]
            else:
                self.points[p-1].nextpoint = self.points[p-2]
        else:
            self.points[p-1].nextpoint = self.points[p+1]
            self.points[p+1].lastpoint = self.points[p-1]
        self.points.pop(p)

    def remove_backtracks(self):
        if len(self.points)>3:
            for p,point in enumerate(self.points):
                if (point.point_type in ['sharp', 'clear', 'doubleclear', 'insharp'] ):
                    point.setangle()
                    if point.dot==-1 and (self.closed or p!=0 and p!=len(self.points)-1):
                        print( "deleting point as pos="+str(point.pos))
                        self.delete_point(p)

    def simplify_points(self):
        if len(self.points)>2:
            for p,point in enumerate(self.points):
                if (point.point_type in ['sharp', 'clear', 'doubleclear', 'insharp'] and
                        point.next().point_type in ['sharp', 'clear', 'doubleclear', 'insharp'] and
                        point.last().point_type in ['sharp', 'clear', 'doubleclear', 'insharp'] ):
#                                 or (point.point_type == 'insharp' and
#                                       point.next().point_type=='insharp' and
#                                       point.last().point_type=='insharp') ):# and p!=0 and p!=len(self.points)-1:
                # delete if the two points are in the same place
                    if (point.point_transform({}).pos-point.lastpoint.point_transform({}).pos).length()<0.0001:
                        self.delete_point(p)
                # delete if they are in a straight line
                    elif point.point_transform({}).pos!= point.next().point_transform({}).pos and abs((point.point_transform({}).pos-point.last().point_transform({}).pos).normalize().dot((point.next().point_transform({}).pos-point.point_transform({}).pos).normalize())-1)<0.001:
                        self.delete_point(p)
                # delete if they are are in the same place and the same point type
                elif point.point_type == point.lastpoint.point_type and (point.point_transform({}).pos-point.lastpoint.point_transform({}).pos).length()<0.001:
                    self.delete_point(p)
        self.remove_backtracks()

    def offset_path(self,side,distance, config):
        self.simplify_points()
        newpath=copy.deepcopy(self)
        newpath.points=[]
        thisdir=self.find_direction(config)
        pointlist=self.transform_pointlist(self.points,{})#config['transformations'])
        if len(pointlist)==1:
            if pointlist[0].point_type=='circle':
                p = copy.copy(pointlist[0])
                p.transform=None
                if side=='left':
                    if ((thisdir=='cw') == (self.mirrored>0)):#==((thisdir=='cw')):
                        side='in'
                    else:
                        side='out'
                elif side=='right':
                    if ((thisdir=='cw')  == (self.mirrored>0)):#==((thisdir=='cw')):
                        side='out'
                    else:
                        side='in'
                if side=='in':
                    p.radius-=distance
                elif side=='out':
                    p.radius+=distance

                newpath.points.append(p)
                return newpath
    #       mirrored=1
        if side=='in':
            #if thisdir=='cw' and self.mirrored>0 or thisdir=='ccw' and not self.mirrored>0:
#                       if thisdir=='cw':# and self.mirrored>0 or thisdir=='ccw' and not self.mirrored>0:
#                       if config['direction']=='cw' and self.mirrored>0 or config['direction']=='ccw' and not self.mirrored>0:
            if ((thisdir=='cw') == (self.mirrored>0)):#==((thisdir=='cw')):
                side='right'
            else:
                side='left'
        elif side=='out':
            #if thisdir=='cw' and self.mirrored>0 or thisdir=='ccw' and not self.mirrored>0:
#                       if thisdir=='cw' and self.mirrored>0 or thisdir=='cw' and not self.mirrored>0:
#                       if config['direction']=='cw' and self.mirrored>0 or config['direction']=='ccw' and not self.mirrored>0:
            if ((thisdir=='cw')  == (self.mirrored>0)):#==((thisdir=='cw')):
                side='left'
            else:
                side='right'
        lookup=[]
        for p,point in enumerate(pointlist):
# Offsetting a point at the end of an open path is a special case. If there is the special case for the point type use that, otherwise move it perpendicularly to the vector from neighbouring point
            if not self.closed and (p==0 or p==len(pointlist)-1):
                if hasattr(pointlist[p], 'offset_end'):
                    t=point.offset_end(side, distance, thisdir)
                else:
                    if p==0:
                        para = (pointlist[1].pos-pointlist[0].pos).normalize()
                    else:
                        para = (pointlist[-1].pos-pointlist[-2].pos).normalize()
                    if side=='right':
                        perp = rotate(para,90)
                    else:
                        perp = rotate(para,-90)
                    t=[]
                    tp = copy.deepcopy(point)
                    tp.pos+=perp*distance
                    t.append(copy.deepcopy(tp))
            else:
                t=point.offset(side, distance, thisdir)
            if t:
                newpath.points.extend(t)
            lookup.append(len(newpath.points))
        newpath.reset_points()
        return newpath



# find whether the path is setup clockwise or anticlockwise
    def find_direction(self,config):
        if self.input_direction in ['cw','ccw']:
            return self.input_direction
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
# create a list of points ignoring the ones we should ignore
        pointlist=[]
        for p in self.points:
            if p.pos is not None and p.dirpoint:
                pointlist.append(p)
        self.mirrored=reverse
        if len(self.points)==1 and hasattr(self.points[0],'direction') and self.points[0].direction in ['cw','ccw']:
            if reverse:
                return self.otherDir(self.points[0].direction)
            else:
                return self.points[0].direction
        for p,q in enumerate(pointlist):
            if pointlist[p].pos is not None and pointlist[(p-1)%len(pointlist)].pos is not None and pointlist[(p+1)%len(pointlist)].pos is not None and pointlist[p].dirpoint:
                total+=(pointlist[p].pos-pointlist[(p-1)%len(pointlist)].pos).normalize().cross((pointlist[(p+1)%len(pointlist)].pos-pointlist[p].pos).normalize())
        #for p,q in enumerate(self.points):
        #       if self.points[p].pos is not None and self.points[(p-1)%len(self.points)].pos is not None and self.points[(p+1)%len(self.points)].pos is not None and self.points[p].dirpoint:
        #               print "findDir pnt="+str(self.points[p].pos)+" reverse="+str(reverse)
        #               total+=(self.points[p].pos-self.points[(p-1)%len(self.points)].pos).normalize().cross((self.points[(p+1)%len(self.points)].pos-self.points[p].pos).normalize())
        # if it is a circle
        if total[2]==0:
            for p in self.points:
                if hasattr(p,'direction') and p.direction in ['cw','ccw']:
                    return p.direction
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
    def polygonise(self,resolution=5, direction='cw'):
        ret=[]
        self.Fsegments=[]
        if resolution in self.polygon and (resolution not in self.changed or self.changed[resolution]==False):
            return self.polygon[resolution]
        else:
            config=self.generate_config({'cutterrad':0})
            self.make_segments(direction,self.Fsegments,config)
            for s in self.Fsegments:
                ret.extend(s.polygon(resolution))
            for p in ret:
                if 'bl' not in self.boundingBox:
                    self.boundingBox={'bl':[1000000000,1000000000],'tr':[-1000000000,-1000000000]}
                self.boundingBox['bl'] = [min(self.boundingBox['bl'][0],p[0]), min(self.boundingBox['bl'][1],p[1])]
                self.boundingBox['tr'] = [max(self.boundingBox['tr'][0],p[0]), max(self.boundingBox['tr'][1],p[1])]
            if('tr' in self.boundingBox):
                self.boundingBox['tr']=V(self.boundingBox['tr'][0],self.boundingBox['tr'][1])
                self.boundingBox['bl']=V(self.boundingBox['bl'][0],self.boundingBox['bl'][1])
                self.centre=(self.boundingBox['bl']+self.boundingBox['tr'])/2
                self.polygon[resolution]=ret
                self.changed[resolution]=False

            return ret

    def in_bounding_box(self,point):
        return point[0]>=self.boundingBox['bl'][0] and point[1]>=self.boundingBox['bl'][1] and point[0]<=self.boundingBox['tr'][0] and point[1]<=self.boundingBox['tr'][1]
    def intersect_bounding_box(self,bbox):
        if 'tr' not in bbox or 'bl' not in bbox:
            return False
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
            if len(otherpolygon)==1:
                if self.contains_point(otherpolygon[0], thispolygon):
                    return 1
                else:
                    return 0
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
        points = []
        for p in poly:
            points.append((p[0],p[1]))

        sPoly = shapely.geometry.Polygon(points)
        sPoint = shapely.geometry.Point(point[0],point[1])
        ret = sPoly.contains(sPoint)
        if ret:
            return ret
        points.append((poly[0][0], poly[0][1]))
        sLine = shapely.geometry.LineString(points)
        if(sPoint.distance(sLine)<0.01):
            return True
        else:
            return False

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


    def get_plane(self):
        if self.parent:
            return self.parent.get_plane()
        else:
            return False


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
            if type(self.transform) is list :
                config['transformations']+=self.transform
            else:
                config['transformations'].append(self.transform)
        #       self.transform=None
    #       self.varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode', 'stepdown','finishdepth','forcestepdown', 'forcecutter', 'mode','partial_fill','finishing','fill_direction','precut_z', 'layer', 'no_mirror', 'part_thickness','use_point_z','clear_height', 'sidefeed']
        for v in self.varlist:
            # we want to be able to know if we are on the front or the back
            if v !='transform' and v !='transformations':
                if hasattr(self,v) and getattr(self,v) is not None:
                    config[v]=getattr(self,v)
                elif pconfig is not False and v in pconfig and pconfig[v] is not None:
                    config[v]=pconfig[v]
                else:
                    config[v]=None
        if pconfig is not False and 'zdir' in pconfig and pconfig['zdir'] is not None:
            config['zdir']= pconfig['zdir']
        else:
            config['zdir']=1
        if hasattr(self, 'layer') and self.layer is not None:
            l=copy.copy(self.get_plane().get_layer_config(self.layer))
            if 'thickness' in l and l['thickness'] is not None:
                config['thickness'] = l['thickness']
            if 'isback' not in l:
                l['isback']=False
        else:
            l={'thickness':0, 'zoffset':0, 'isback':False}
        if hasattr(self, 'thickness') and self.thickness is not None:
            config['thickness'] = self.thickness
        if  hasattr(self,'isback') and getattr(self,'isback') or l['isback']:
            config['zdir']*=-1

        if config['zdir']==-1 and config['no_mirror']:
            self.mirror(V(0,0), V(0,1,0))

        if hasattr(self,'zoffset') and getattr(self,'zoffset') is not None:
            zoffset=self.zoffset
        elif 'zoffset' in l and l['zoffset'] is not None:
            zoffset = l['zoffset']
        else:
            zoffset = 0
        if pconfig is not False and 'zoffset' in pconfig and pconfig['zoffset'] is not None:
            config['zoffset'] = pconfig['zoffset'] + zoffset * config['zdir']
        else:
            config['zoffset'] = zoffset * config['zdir']


        if  hasattr(self,'isback') and getattr(self,'isback') or l['isback']:
            config['zoffset'] += l['thickness'] * config['zdir']


        return config
    def pre_render(self, config):

        if getattr(self, "_pre_render", None) and callable(self._pre_render):
            self._pre_render(config)

    def makeShapely(self):
        if( not hasattr(self, 'shapelyPolygon') or not self.shapelyPolygon):
            polygonised = self.polygonise( 1.0)
            points = []
            for p in polygonised:
                points.append([p[0], p[1]])
            self.shapelyPolygon = shapely.geometry.LineString(points)
            self.rawPolygon = polygonised


    def generate_config(self, pconfig):
        config={}
        config=self.overwrite(config,pconfig)
        inherited = self.get_config()
#               if('transformations' in config):
        config=self.overwrite(config, inherited)
#                if getattr(self, "_pre_render", None) and callable(self._pre_render):
 #                       self._pre_render(config)
#               if('transformations' in config):
#               for k in inherited.keys():
 #                       if (config[k] is None or config[k] is False) and k in pconfig:
  #                              config[k]=pconfig[k]
        self.set_material(config)
        self.set_cutter(config)
        thisdir=self.find_direction(config)

        if 'direction' not in config or config['direction'] is False:

            if hasattr(self,'direction') and  self.direction=='this':
                config['direction'] = thisdir
            elif hasattr(self,'direction') and  self.direction!=False:
                config['direction']=self.direction
            elif(config['side'] =='in' and  config['mill_dir']=='up' or config['side'] =='out' and  config['mill_dir']=='down' ):
                config['direction']='cw'
            elif(config['side'] =='out' and  config['mill_dir']=='up' or config['side'] =='in' and  config['mill_dir']=='down'):
                config['direction']='ccw'
            else:
                config['direction']=thisdir
#               if self.mirrored==-1:
#                       config['direction']=self.otherDir(config['direction'])
        if config['side'] is None or config['side'] is False:
            config['side']='on'
        if config['z0'] is None or config['z0'] is False:
            config['z0']=0
        if (config['z1'] is False or config['z1'] is None) and config['z0'] is not None and config['thickness'] is not None:
            if hasattr(self, 'isborder') and self.isborder or not 'thickness' in pconfig:
                thickness = config['thickness']
            else:
                thickness = pconfig['thickness']

            if 'z_overshoot' in config:
                config['z1'] = - thickness - config['z_overshoot']
            else:
                config['z1'] = - thickness
        return config

    def fill_path(self, side, cutterrad, distance=False, step=False, cutDirection=None):
        print ("FIll pTh")
        if step==False:
            step = cutterrad*0.5
        ret=[self]
        spath=self.offset_path('in', cutterrad)
        spath.makeShapely()
        poly = shapely.geometry.LineString(spath.shapelyPolygon.coords[:] + spath.shapelyPolygon.coords[0:1])
        thisdir=self.find_direction({})
        if (thisdir=='ccw') == (side=='in'):
            cutside='right'
        else:
            cutside='left'
        if distance is not False:
            steps = int(distance/step)+1
            step = distance/steps
        else:
            steps = 100
        polTree = self.fill_path_step( side, step, poly, steps)
        polPaths = self.make_fill_path(polTree, cutDirection)
        fillPath = Pathgroup()
        for p in polPaths:
            path = Path(closed=True, side='on', z1=self.z1)
            path.add_points(p)
            fillPath.add(path)
        return fillPath

    def make_fill_path(self, polTree, cutDirection, depth=0):
        ret=[]
        for section in polTree[1]:
#            print("SECTION£");
            ret+=self.make_fill_path(section, cutDirection, depth+1)
        if len(ret)==0:
            ret.append([])
        elif ret[0] is None:
            ret[0]=[]
        if type(polTree[0]) is shapely.geometry.LineString:
            newPoints = []
            print("num="+str(depth)+" sections="+str(len(polTree[1]))+" "+str(polTree[0].coords[0])+"lenret="+str(len(ret)))
            for p in polTree[0].coords:
                newPoints.append(PSharp(V(p[0], p[1])))
            if (self.signed_area(polTree[0])>0) != (cutDirection=='ccw'):
                newPoints.reverse()
            if(depth==0):
                ret.append(newPoints)
            else:
                ret[0]+=newPoints
        return ret

    def signed_area(self,pr):
        """Return the signed area enclosed by a ring using the linear time
        algorithm at http://www.cgafaq.info/wiki/Polygon_Area. A value >= 0
        indicates a counter-clockwise oriented ring."""
        xs, ys = map(list, zip(*pr.coords))
        xs.append(xs[1])
        ys.append(ys[1])
        return sum(xs[i]*(ys[i+1]-ys[i-1]) for i in range(1, len(pr.coords)))/2.0
    def fill_path_step(self, cutside, step, polygon, stepcount):
        stepcount-=1;
        if polygon.is_empty:
            return [[],[]]
        if (cutside=='in') == (self.signed_area(polygon)>0):
                side='left'
        else:
                side='right'
        new=polygon.parallel_offset(step, side, join_style=2)
        ret=[]

        if stepcount==0:
            pass
        elif type(new) is shapely.geometry.LineString:
            ret.append(self.fill_path_step( cutside, step, new, stepcount))
        elif type(new) is shapely.geometry.MultiLineString:
            for p in new:
                ret.append(self.fill_path_step( cutside, step, p, stepcount))
        return [polygon, ret]
    def _key_cross(self, a):
        return a[0]
    # If a simplepath crosses itself split it into many paths
    def clean_simplepath(self, points):
#        self.makeShapely(dd)
        ls = shapely.geometry.LineString(points)
        lr = shapely.geometry.LineString(ls.coords[:] + ls.coords[0:1])
        if lr.is_simple:
            return points
        mls = shapely.ops.unary_union(lr)
        print (lr.is_simple)
        print (mls.geom_type)
       # print(shapely.ops.polygonize(mls))
        ret = False
        maxarea=0
        for polygon in shapely.ops.polygonize(mls):
            if polygon.area>maxarea:
                ret=polygon
                maxarea=polygon.area
        return list(zip(*ret.exterior.coords.xy))
#        points = copy.copy(self.polygon[resolution])
#        intersections = self.self_intersects(points)
#        crosses = []
#        print (intersections)
#        for i  in range(0,len(intersections)):
#            print (i)
#            intersection=intersections[i]
#            crosses.append([intersection[0],intersection[1],i,0,intersection[2],0])
#            crosses.append([intersection[1],intersection[0],i,1,intersection[2],0])
#        sorted(crosses, key=self._key_cross)
#        print( crosses)
#       # points = self.points
#        if len(crosses)==0:
#            return [points]

 #       paths = [[]]
        # keep going while we have points in the bank
        #traverse_loop(0, paths[0], crosses, paths, points):


    def traverse_loop(self, c, path, crosses, direction, paths, points):
        path.append(crosses[c][4])
        p = crosses[c][0]
        while crosses[(c+1)%len(crosses)][0]!=p:
            path.append(points[p])
            p+=direction
            


#  output the path
    def render(self,pconfig):
        global spindleDir
        out=[]
# Do something about offsets manually so as not to rely on linuxcnc
        config=self.generate_config(pconfig)
        if config['mode']=='gcode' and hasattr(self, 'spindleDir') and self.spindleDir and spindleDir != self.spindleDir:
            if spindleDir is None:
                time = "5"
            else:
                time = "10"
            if self.spindleDir=='ccw':
                out.append('M03\nG04p'+time+'\n')
            elif self.spindleDir=='cw':
                out.append('M04\nG04p'+time+'\n')
            spindleDir = self.spindleDir
        finalpass=False
        outpaths=[]
        if config['side']=='in' or config['side']=='out':
            side = config['side']
            c =copy.copy(config)
            c['opacity']=0.5
            thepath=self.offset_path(side,c['cutterrad'],c)
            c['side']='on'
            if config['hide_cuts']:
                self.output_path(config)
                return [config['cutter'],self.render_path(self,config)]
            elif config['overview']:
                self.output_path(config)
                out.append( self.render_path(self,config) )
        else:
            thepath=self
            c=config
        if 'finishing' in config and config['finishing'] is not None and config['finishing']>0:
            if 'partial_fill' not in config or config['partial_fill']==None or config['partial_fill']==False:
                config['partial_fill']=config['finishing']
                if config['side']=='out':
                    config['fill_direction']='out'
                else:
                    config['fill_direction']='in'
                c['z1']=c['z1']+1
                if 'finalpass' in config:
                    finalpass=config['finalpass']
                else:
                    finalpass=True
                finishing=config['finishing']
            else:
                finishing=0
        else:
            finishing=0

        if not config['hide_cuts']  and 'partial_fill' in config and config['partial_fill'] and config['partial_fill']>0:
            dist=max(config['partial_fill']-config['cutterrad'], finishing)
            if dist<=0:
                numpasses=0
                step=1
            else:
                numpasses = int(math.ceil(abs(float(dist)/ float(config['cutterrad'])/1.4)))
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
                fillpath.add_point(p.pos-V(p.radius,0), point_type='sharp')
                fillpath.add_point(PArc(p.pos,  radius=p.radius, direction='cw'))
                fillpath.add_point(p.pos+V(0,p.radius), point_type='sharp')
                fillpath.add_point(PArc(p.pos,  radius=p.radius, direction='cw'))
                fillpath.add_point(p.pos+V(p.radius,0), point_type='sharp')
                fillpath.add_point(PArc(p.pos,  radius=p.radius, direction='cw'))
                #fillpath.add_point(p.pos-V(p.radius,0.001), point_type='sharp')
# there seems to be a problem with arcs and reversing...
            if fillpath.find_direction(c)!=config['direction']:
                reverse=True

            else:
                reverse=False

            if numpasses>0:
            # if it is a circle we need to split it into 2 arcs to be able to fill properly
                fillpath.output_path(config)
                frompos = fillpath.points[-1].end()
                if frompos!=fillpath.points[-1].pos:
                    fillpath.add_point(frompos,'sharp')
                else:
                    print("pass")
                    pass
                fillpath.prepend_point(frompos,'sharp')


            tpath=thepath
    #               outpaths.append(tpath)
          #  tpath=fillpath
            for d in range(0,int(numpasses+1)):
        #               temppath.output_path(config)
                temppath=copy.deepcopy(tpath)
                tpath=temppath.offset_path(ns, step, c)

                frompos = temppath.points[-1].end()
                if frompos!=temppath.points[-1].pos:
                    temppath.add_point(frompos,'sharp')
                else:
                    temppath.points[-1].point_type='sharp'
                temppath.prepend_point(frompos,'sharp')

                outpaths.insert(0,temppath)

                if reverse:
                    fillpath.add_points(temppath.points,'start')
                else:
                    fillpath.add_points(temppath.points[::-1],'start')

            offpath=thepath
            thepath=fillpath
        tempout = thepath.output
        thepath.output=[]
        if len(outpaths)>1:
            pass
            thepath.output_paths(c,outpaths)
            thepath.add_out(tempout)
        else:
            thepath.output_path(c)
        out.append( thepath.render_path(thepath,c))
        if finalpass:
            c['z0']=c['z1']
            c['z1']=config['z1']
            c['partial_fill']=None
            offpath.output_path(c)
            out.append( offpath.render_path(offpath,c))
        if 'partcutter' in config and config['partcutter'] is not None:
            key = config['partcutter']
        else:
            key = config['cutter']
        return [key,out]


  #  def fill_path(self, path,  direction='in', distance=0, inner_paths=False, **config):
  #      done = False
  #      tpath=[path]
  #      i=0
  #      paths = [[path]]
  #      paths.extend(copy.copy(inner_paths))
  #      startdir=path.find_direction()
  #      segments=[]
        # we start with a list of paths and then offset them and check wiheter they intersect with themselves or any of the newly made paths

        # if they do intersect then we slice them up into smaller sections and check they still have the same sense as before and drop the onces which didn't

   #     while done==False:
   #         # iterate t
   #         for j in range(len(paths)-1,-1):
   #             paths[j].append(tpath.offset_path(ns, step, c))
   #             n = len(paths[j])-1
   #             paths[j][n].output_path(config)
   #             intersections = paths[j][n].self_intersects()
    #            if len(intersections)>0:
#
#                    pass
#                else:
#                    if self.find_direction()!=startdir:
 #                       done=True


    def other_intersects(self, paths, j, n):
        pass
# need some way of going back from segments to points for the offsetting
    def split_path(self, path, intersections):
        for seg1 in range(0,len(path.Fsegments)):
            for seg2 in range(seg1+1, len(path.Fsegments)):
                intersects=seg1.intesects(seg)
                if intersects != False:
                    for intersect in intersects:
                        pass

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
        else:
            return self.output
#               elif config['mode']=='simplegcode':
#                       ret+=self.render_path_gcode(self.output,config)+'G0Z%0.4f\n'%config['clear_height']
        return ret

    def render_path_svg(self,path,config):
        ret=""
        comments=""
        for point in path:
            if 'cmd' in point:
                ret+=" "+point['cmd']
            if 'rx' in point:
                ret+=" %0.4f"%point['rx']
            if 'ry' in point:
                ret+=",%0.4f"%point['ry']
            if '_rot' in point:
                ret+=" %0.0f"%point['_rot']
            if '_lf' in point:
                ret+=" %s"%point['_lf']
            if '_dir' in point:
                ret+=" %s"%point['_dir']
            if 'x' in point:
                ret+=" %0.4f"%point['x']
            if 'y' in point:
                ret+=",%0.4f"%point['y']
            if 'x2' in point:
                ret+=" %0.4f"%point['x2']
            if 'y2' in point:
                ret+=",%0.4f"%point['y2']
            if 'x3' in point:
                ret+=" %0.4f"%point['x3']
            if 'y3' in point:
                ret+=",%0.4f"%point['y3']
            if '_comment' in point :
                comments+="<!--"+point['_comment']+"-->\n"
            if '_colour' in point and point['_colour'] is not None:
                if type(point['_colour']) is str:
                    colour=point['_colour']
                else:
                    print("colour is not a string"+str(point["_colour"]))
            else:
                colour='black'
            if '_fill' in point and point['_fill'] is not None:
                fill = point['_fill']
            else:
                fill = 'none'
            if '_opacity' in point:
                opacity = "opacity:"+str(point['_opacity'])
            else:
                opacity = "opacity:1"
            if '_closed' in point and point['_closed']:
                z=' Z'
            else:
                z=''
        ret+=z
        return comments+"<path d=\""+ret+"\"  style='stroke-width:0.1px;"+opacity+"' fill='"+fill+"' stroke='"+colour+"'/>\n"

    def render_path_gcode(self,path,config):
        ret=""
        if config['mode']=='gcode':
            if 'blendTolerance' in config:
                if config['blendTolerance']>0:
                    ret+="G64P"+str(config['blendTolerance'])+"\n"
                else:
                    if 'blendTolerance' in config:
                        ret+="G64\n"
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
                ret+="F%0.2f"%point['F']
            ret+="\n"
        if config['mode']=='gcode':
            ret+="G64\n"
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
            raise ValueError( "ERROR trying to cut sideways with a cutter "+str(self.cutter)+"with no sidefeed")
        if dz>0 and 'vertfeed' not in config or config['vertfeed']==0:
            raise ValueError( "ERROR trying to cut down with a cutter "+str(self.cutter)+" with no vertfeed")
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
        colour = self.get_colour(config)
        if 'fill_colour' in config:
            fill = config['fill_colour']
        else:
            fill = 'none'
        for cut in self.output:
            cut['_colour']=colour
            cut['_fill']=fill
            if 'opacity' in config:
                cut['_opacity'] = config['opacity']
            if self.closed:
                cut['_closed'] = self.closed
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

            if 'colour' in config and config['colour'] is not False and config['colour'] is not None and type(config['colour']) is not str:
                print("config['colour'] is not string="+str(config['colour']))
                print(type(config['colour']))
                print(self)
                print(self.parent)
                print(self.parent.parent)
                return "black"
            if 'colour' in config and config['colour'] is not False:
                return config['colour']
            else:
                return 'black'
    # Runs output_path for an array of paths all of which will be cut before dropping a stepdown.
    def output_paths(self, pconfig, paths):
        output=[]
        config=pconfig #self.generate_config(pconfig)
        self.config=config
        mode=pconfig['mode']
        if self.use_point_z:
            downmode='cutdown'
            config['stepdown']=1000
        else:
            downmode=config['downmode']
        if downmode==None:
            downmode='ramp'
        if 'forcestepdown' in pconfig and pconfig['forcestepdown'] is not None:
            stepdown = pconfig['forcestepdown']
        else:
            stepdown = config['stepdown']

        direction=config['direction']
        self.mode=mode
        segments=[]
        start=True
        for path in paths:
            path.make_path_segments(config)
            if not start:
                segments.append(Line(segments[-1].cutto, path.Fsegments[0].cutfrom))
            segments.extend(path.Fsegments)
            start=False
        segments.insert(0,Line(segments[-1].cutto, segments[0].cutfrom))

# Runin/ ramp
        if 'finishdepth' in config and config['finishdepth'] and config['finishdepth']>0:
            z1=config['z1']+config['finishdepth']
        else:
            z1=config['z1']
        step,depths=self.get_depths(config['mode'], config['z0'], z1, stepdown)
        if 'finishdepth' in config and config['finishdepth'] and config['finishdepth']>0:
            depths.append(config['z1'])
# dodgy fudge to stop things crashing
        if step == None:
            step=1
        if len(depths)==0:
            return False
# if closed go around and around, if open go back and forth
        firstdepth=1
        if self.closed:
            self.runin(config['cutterrad'],config['direction'],config['downmode'],config['side'])
#                       if downmode=='ramp'
#                               self.add_out(self.Fsegments[-1].out(self.mode, depths[0]))
           # if downmode=='down':
            self.add_out(self.quickdown(depths[0]-step+config['precut_z']))
            for depth in depths:
                if downmode=='down' or downmode=='cutdown':
                    self.add_out(self.cutdown(depth))
                first=1
                for segment in segments:
                    segment.parent = path
                    if first==1 and downmode=='ramp' and (mode=='gcode' or mode=='simplegcode'):
                        if firstdepth and (mode=='gcode' or mode=='simplegcode'):
                            self.add_out(self.quickdown(depth-step+config['precut_z']))
                            firstdepth=0
                        self.add_out(segment.out(True,mode,depth-step,depth, config['use_point_z']))
                    else:
                        self.add_out(segment.out(True,mode, depth, depth, config['use_point_z']))
                    first=0
            # if we are in ramp mode, redo the first segment
#                       if downmode=='ramp' and (mode=='gcode' or mode=='simplegcode'):
            if  (mode=='gcode' or mode=='simplegcode'):
                self.add_out(self.Fsegments[0].out(direction,mode, depth, depth, config['use_point_z']))
            self.add_out(self.runout(config['cutterrad'],config['direction'],config['downmode'],config['side']))

        if self.mode=='gcode':
            self.add_out( [{"cmd":'G40'}])
        if self.mode=='gcode' or self.mode=='simplegcode':
            self.add_out([{'cmd':'G0','Z':config['clear_height']}])
            self.add_feedrates(config)
            self.comment("test")
        elif self.mode=='svg' or self.mode=='scr':
            self.add_colour(config)

# extract the bits of output_path to produce a series of segments with no Z
# this is called by output_path and output_paths
    def make_path_segments(self, pconfig):
        config=pconfig #self.generate_config(pconfig)
        self.config=config
        direction=config['direction']
        self.Fsegments=[]
        self.Bsegments=[]
        self.make_segments(direction,self.Fsegments,config)
        self.make_segments(self.otherDir(direction),self.Bsegments,config)
    def output_path(self, pconfig):#z0=False,z1=False,side='on',direction=False, stepdown=False, downmode='down', transformations=False):
        """ output a path in whatever the config tells it - pconfig will be inherited from """
        # we want a new list for each call, to make it properly recusive
        self.output=[]
        config=pconfig #self.generate_config(pconfig)
        self.config=config
        mode=pconfig['mode']
        if self.use_point_z:
            downmode='down'
            config['stepdown']=1000
        else:
            downmode=config['downmode']
        if downmode==None:
            downmode='ramp'
        direction=config['direction']
        self.mode=mode
        self.Fsegments=[]
        self.Bsegments=[]
        self.make_segments(direction,self.Fsegments,config)
        self.make_segments(self.otherDir(direction),self.Bsegments,config)
# Runin/ ramp
        if hasattr(self,'finishdepth') and self.finishdepth is not None:
            finishdepth = self.finishdepth
        else:
            finishdepth = config['finishdepth']
        if finishdepth and finishdepth>0:
            z1=config['z1']+finishdepth
        else:
            z1=config['z1']
        if 'forcestepdown' in config and config['forcestepdown'] is not None:
            stepdown = config['forcestepdown']
        else:
            stepdown = config['stepdown']
        step,depths=self.get_depths(config['mode'], config['z0'], z1, stepdown)
        if 'finishdepth' in config and config['finishdepth'] and config['finishdepth']>0:
            depths.append(config['z1'])
# dodgy fudge to stop things crashing
        if step == None:
            step=1
        if len(depths)==0:
            return False
# if closed go around and around, if open go back and forth
        firstdepth=1
        if self.closed:
            self.runin(config['cutterrad'],config['direction'],config['downmode'],config['side'])
            segments=self.Fsegments
#                       if downmode=='ramp'
#                               self.add_out(self.Fsegments[-1].out(self.mode, depths[0]))
            if downmode=='down' or downmode=='cutdown':
                self.add_out(self.quickdown(depths[0]-step+config['precut_z']))
            for depth in depths:
                if downmode=='down' or downmode=='cutdown':
                    self.add_out(self.cutdown(depth))
                first=1
                for segment in segments:
                    if first==1 and downmode=='ramp' and (mode=='gcode' or mode=='simplegcode'):
                        if firstdepth and (mode=='gcode' or mode=='simplegcode'):
                            self.add_out(self.quickdown(depth-step+config['precut_z']))
                            firstdepth=0
                        self.add_out(segment.out(True,mode,depth-step,depth, config['use_point_z']))
                    else:
                        self.add_out(segment.out(True,mode, depth, depth, config['use_point_z']))
                    first=0
            # if we are in ramp mode, redo the first segment
#                       if downmode=='ramp' and (mode=='gcode' or mode=='simplegcode'):
            if  (mode=='gcode' or mode=='simplegcode'):
                self.add_out(self.Fsegments[0].out(direction,mode, depth, depth, config['use_point_z']))
            self.add_out(self.runout(config['cutterrad'],config['direction'],config['downmode'],config['side']))

    # Deal with open lines
        else:
            self.runin(downmode,self.side)
            d=True
            # add the final depth one more time so it comes back and cuts the ramp
            for depth in depths+[depths[-1]]:
                if d:
                    segments=self.Fsegments
                else:
                    segments=self.Bsegments
                if downmode=='down':
                    self.add_out(self.cutdown(depth))
                first=1
                s=len(segments)
                for s in range(1,s):
                    segment=segments[s]
                    if first==1 and downmode=='ramp':
                        if firstdepth and (mode=='gcode' or mode=='simplegcode'):
                            self.add_out(self.quickdown(depth-step+config['precut_z']))
                            firstdepth=0
                        self.add_out(segment.out(True,mode,depth-step,depth, config['use_point_z']))
                    else:
                        self.add_out(segment.out(True,mode, depth, depth, config['use_point_z']))
                    first=0
                d= not d
#                       if downmode='ramp':
            if d:
                self.add_out(self.Fsegments[0].out(True,mode, depth, depth, config['use_point_z']))
            else:
                self.add_out(self.Bsegments[0].out(True,mode, depth, depth, config['use_point_z']))
            self.add_out(self.runout(config['cutterrad'],config['direction'],config['downmode'],config['side']))
        # If we are in a gcode mode, go through all the cuts and add feed rates to them
        if self.mode=='gcode':
            self.add_out( [{"cmd":'G40'}])
        if self.mode=='gcode' or self.mode=='simplegcode':
            self.add_out([{'cmd':'G0','Z':config['clear_height']}])
            self.add_feedrates(config)
            self.comment("test")
        elif self.mode=='svg' or self.mode=='scr':
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
            raise TypeError("moveto must be a Vec not a "+str(type(moveto))+" Created:"+str(self.trace))
        else:
            if self.mode=='gcode' or self.mode=='simplegcode':
                return [{"cmd":"G0","X":moveto[0],"Y":moveto[1]}]
            elif self.mode=='svg':
                return [{"cmd":"M","x":moveto[0],"y":moveto[1]}]
    def setside(self,side, direction):
        if self.mode=='gcode':
            if side=='on':
                return [{"cmd":"G40"}]
#                       if side=='in':
#                               if direction=='cw':
#                                       return [{"cmd":"G42"}]
#                               else:
#                                       return [{"cmd":"G41"}]
#                       else:
#                               if direction=='cw':
#                                       return [{"cmd":"G41"}]
#                               else:
#                                       return [{"cmd":"G42"}]
    def cut_filled(self,z0=False,z1=False,side='on',dir=False):
        print("cut filled\n")
# find a tangent to the first segment of the path to allow the cutter to work
    def runin(self, cutterrad, direction, mode='down', side='on', ):
        #if self.isreversed:
        #       seg=0
    #               segments=self.Bsegments
    #               cutfrom=segments[seg].cutto
    #               cutto=segments[seg].cutfrom
    #       else:
        seg=0
        segments=self.Fsegments
        #if len(self.Bsegments)==0:
        cutto=segments[seg].cutto
        cutfrom=segments[seg].cutfrom
        if side=='on':
            if mode=='down':
                self.comment("runin0")
                self.start=cutto
                self.add_out(self.move(cutto))
            else:
                self.comment("runin1")
                self.start=cutfrom
                self.add_out(self.move(cutfrom))
        else:
            if(segments[seg].seg_type=='line'):
                diff = (cutto-cutfrom).normalize()

            if(segments[seg].seg_type=='arc'):
                centre=segments[seg].centre
                # find a normalized tangent to the line from the centre to the start point
                p=PSharp(V(0,0))
                if direction=='cw' :
                    angle=90
                else:
                    angle=-90
                diff= p.rotate((-centre+cutfrom), [V(0,0),angle])
                # we now need to find out if this is in the right direction
            #       sense = diff.cross(segments[seg].centre-segments[seg].cutfrom).z
            #       if sense[2]>0 and segments[seg].direction=='ccw' or sense[2]<0 and segments[seg].direction=='cw':
            #               diff=-diff

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
        varlist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth','forcestepdown', 'forcecutter',  'stepdown','finishdepth', 'forcecolour', 'rendermode','partial_fill','finishing','fill_direction','cutter','precut_z', 'zoffset','layer','no_mirror', 'part_thickness','use_point_z','clear_height', 'blendTolerance', 'roughClearance', 'matEnd', 'latheMode', 'matRad', 'step', 'cutClear', 'handedness', 'cutFromBack', 'chipBreak', 'justRoughing', 'vertfeed', 'blendTolerance','finalpass']
        if hasattr(self, 'varlist') and type(self.varlist) is list:
            self.varlist+=varlist
        else:
            self.varlist=varlist
        self.otherargs=''
        for v in self.varlist:
            if v in args:
                setattr(self,v, args[v])
            else:
                setattr(self,v,None)
            #self.otherargs+=':param v: '+arg_meanings[v]+"\n"
        self.output=[]
        self.parent=False
        self.comments=[]
        self.transform=[]#{}

    def get_plane(self):
        if self.parent:
            return self.parent.get_plane()
        else:
            return False

    def pre_render(self, config):
        if hasattr(self, '_pre_render'):
            self._pre_render(config)
        for p in self.paths:
            p.pre_render(config)
    def __deepcopy__(self,memo):
        conf={}
        ret=copy.copy(self)#type(self)( **conf)
        for v in self.varlist:
            if v !='parent':
                setattr(ret, v, copy.deepcopy(getattr(self,v),memo))
#                       conf[v]=copy.deepcopy(getattr(self,v),memo)
#               ret.parent=copy.copy(self.parent)
        ret.paths=copy.deepcopy(self.paths)
        for p in ret.paths:
            p.parent=ret
        return ret

    def _pre_render(self, config):
        for path in self.paths:
          #  print points
            #       path.shapelyPolygon = shapely.geometry.LineString(points)
            #       path.rawPolygon = polygonised

            #if getattr(path, "_pre_render", None) and callable(path._pre_render):
            path.pre_render(config)

    def get_config(self):
        if self.parent is not False:
            pconfig = self.parent.get_config()
        else:
            #raise Warning( "PATHGROUP has no parent Created:"+str(self.trace))
            pconfig = False
        config = {}
#               varslist = ['order','transform','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth', 'forcestepdown','forcecutter', 'stepdown','finishdepth', 'forcecolour','rendermode','partial_fill','finishing','fill_direction','cutter','precut_z', 'layer', 'no_mirror', 'part_thickness','use_point_z','clear_height']
        if pconfig is False or  'transformations' not in pconfig or pconfig['transformations'] is False or pconfig['transformations'] is None:
            config['transformations']=[]
        else:
            config['transformations']=pconfig['transformations'][:]
        if type(self.transform) is list:
            config['transformations']+=self.transform
        elif self.transform!=None:
            config['transformations'].append(self.transform)
        #       self.transform=None
        for v in self.varlist:
            if v !='transform' and v !='transformations':
                if getattr(self,v) is not None:
                    config[v]=getattr(self,v)
                elif pconfig!=False and v in pconfig and pconfig[v] is not None:
                    config[v]=pconfig[v]
                else:
                    config[v]=None
        if pconfig is not False and 'zdir' in pconfig and pconfig['zdir'] is not None:
            config['zdir']= pconfig['zdir']
        else:
            config['zdir']=1
        if hasattr(self, 'layer') and self.layer is not None:
            l=copy.copy(self.get_plane().get_layer_config(self.layer))
            if 'thickness' in l and l['thickness'] is not None:
                config['thickness'] = l['thickness']
            if 'isback' not in l:
                l['isback']=False
        else:
            l={'thickness':0, 'zoffset':0, 'isback':False}
        if hasattr(self, 'thickness') and self.thickness is not None:
            config['thickness'] = self.thickness


        if  hasattr(self,'isback') and getattr(self,'isback') or l['isback']:
            config['zdir']*=-1

        if hasattr(self,'zoffset') and getattr(self,'zoffset') is not None:
            zoffset=self.zoffset
        elif 'zoffset' in l and l['zoffset'] is not None:
            zoffset = l['zoffset']
        else:
            zoffset = 0
        if pconfig is not False and 'zoffset' in pconfig and pconfig['zoffset'] is not None:
            config['zoffset'] = pconfig['zoffset'] + zoffset * config['zdir']
        else:
            config['zoffset'] = zoffset * config['zdir']

        if  hasattr(self,'isback') and getattr(self,'isback') or l['isback']:
            config['zoffset'] += l['thickness'] * config['zdir']
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
    def add(self,path, prepend=False):
        return self.add_path(path, prepend)
    def add_path(self,path, prepend=False):
        try:
            path.obType
        except NameError:
            raise TypeError("adding incorrect object to pathgroup, the object should have a Path or Pathgroup so should have an obtype, your class may not have run init()")
        else:
            if (path.obType=='Path' or path.obType=="Pathgroup"):
                path.parent=self
                if prepend:
                    self.paths.insert(0, path)
                else:
                    self.paths.append(path)
            else:
                raise TypeError("Attempting to add "+str(path.obType)+" to Pathgroup. Should be Path or Pathgroup")
        return path
# return a list of all the path gcode grouped by the ordering parameter
    def output_path(self, pconfig=False):
        # we want a new list for each call, to make it properly recusive
        gcode=[]
        for path in self.paths:
            try:
                path.obType
            except NameError:
                raise TypeError("One Path "+str(path)+" in the Pathgroup does not have an obType")
            else:
                if  (path.obType=='Path'):
                    path.output_path(pconfig)
                    gcode.append(path.output)
                elif path.obType=='Pathgroup':
                    paths = path.output_path(pconfig)
                    gcode.extend(paths)
                else:
                    raise TypeError("One Path "+str(path)+" in the Pathgroup is not a Path or Pathgroup")
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

    def rotate(self,pos, angle):
        if self.transform==False:
            self.transform=[]
        self.transform.append({'rotate':[pos, angle]})

    def translate(self,vec):
        if self.transform is False or self.transform is None:
            self.transform=[]
        self.transform.append({'translate':vec})

    def mirror(self, pos, dirvec):
        if self.transform==False or self.transform==None:
            self.transform={}
        self.transform.append({'mirror':[pos,dirvec]})



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
    def __init__(self, name, material, xsection,  diameter, length, number=1, description=False):
        self.name=name
        self.material=material
        self.diameter=diameter
        self.length=length
        self.number=1
        self.description=description
        self.xsection=xsection
        self.init()
    def __str__(self):
        return str(self.number)+'x '+str(self.length)+'mm of '+str(self.name)+' in '+str(self.diameter)+"mm diameter "+str(self.material)+" "+str(self.xsection)+". "+str(self.material)+" "+str(self.description)

class BOM_software(BOM):
    def __init__(self, name, number, folder, language, target, description):
        self.name=name
        self.folder=folder
        self.description=description
        self.language=language
        self.target=target
        self.number=number
        self.init()
    def __str__(self):
        return "Software"+str(name)+" in "+str(folder)+" written in "+str(language)+" on a "+str(target)+" "+str(description)

class BOM_pcb(BOM):
    def __init__(self, name, number, folder, description):
        self.name=name
        self.number=number
        self.description=description
        self.folder=folder
        self.part_number="PCB"+str(name)+"_"+str(folder)
    def __str__(self):
        return "PCB "+str(number)+" of "+str(name)+" in "+str(folder)+" "+str(description)

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
        self.copied = False
        self.isCopy = False
        self.layer = False
        self.comments = []
        self.parent=False
        self.internal_borders=[]
        self.ignore_border=False
        self.transform=[]
        varlist = ['order','side','z0', 'z1', 'thickness', 'material', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth', 'forcestepdown','forcecutter', 'stepdown','finishdepth', 'forcecolour', 'border', 'layer', 'name','partial_fill','finishing','fill_direction','precut_z','ignore_border', 'material_shape', 'material_length', 'material_diameter', 'zoffset', 'no_mirror','subpart', 'isback','use_point_z','clear_height', 'offset', 'blendTolerance', 'vertfeed', 'blendTolerance','finalpass']
        self.otherargs=''
        if hasattr(self, 'varlist') and type(self.varlist) is list:
            self.varlist+=varlist
        else:
            self.varlist=varlist
        for v in self.varlist:
            if v in config:
                setattr(self,v, config[v])
            else:
                setattr(self,v,None)
    #               self.otherargs+=':param v: '+arg_meanings[v]+"\n"
        self.output=[]
        self.number=1
        if 'transform' in config:
            self.transform=copy.copy(config['transform'])
        if 'border' in config:
            self.add_border(config['border'])
        if not hasattr(self, 'cutoutside'):
            self.cutoutside = 'front'
        self.bom=[]
        if 'layers' in config:
            self.layers = config['layers']
        else:
            self.layers = {}
        if  hasattr(self, 'layer_config') and  'plane' in config and config['plane'].obType=='Plane':
            for l, ldat in self.layer_config.items():
                if l in self.layers:
                    lname = self.layers[l]
                else:
                    lname = ldat
                if type(lname) is dict:
                    for k, val in lname.items():
                        ldat[k] = val

                if  (type(lname) is list or type(lname) is str and  lname[0] != '_' or l in self.layers):
                    if l not in self.layers:
                        if type(lname) is dict:
                            self.layers[l] = lname['name']
                        else:
                            self.layers[l] = lname
                elif l not in self.layers and type(ldat) is dict:
                    assert 'material' in ldat # creating new layer should have material in dict
                    assert 'name' in ldat # creating new layer should have name in dict
                    assert 'thickness' in ldat # creating new layer should have thickness in dict
                    ltemp = ldat
                    ltemp['name'] = config['name'] + ltemp['name']
                    config['plane'].add_layer(**ltemp)
                    self.layers[l] = ltemp['name']
                elif l not in self.layers:
                    raise ValueError('Creating new layer "'+str(l)+'". config not sent as dict with name, thickness and material elements so can not create it.')
    def __deepcopy__(self,memo):
        conf={}
        for v in self.varlist:
        #       pass
            conf[v]=copy.deepcopy(getattr(self,v),memo)
#               ret=type(self)( **conf)
        ret=copy.copy(self)
        ret.parent=copy.copy(self.parent)
        # paths and parts need explicitly including
        ret.paths=copy.deepcopy(self.paths)
        ret.parts=copy.deepcopy(self.parts)
        ret.border=copy.deepcopy(self.border)
        ret.transform=copy.deepcopy(self.transform)
        if ret.border is not None:
            ret.border.parent=ret
        # change parent
        for l in ret.paths:
            for p in ret.paths[l].paths:
                p.parent=ret
        for p in ret.parts:
            p.parent=ret
        return ret

    def rotate(self,pos, angle):
        if self.transform==False or self.transform==None:
            self.transform=[]
        self.transform.append({'rotate':[pos, angle]})

    def mirror(self, pos, dirvec):
        if self.transform==False or self.transform==None:
            self.transform=[]
        self.transform.append({'mirror':[pos,dirvec]})

    def translate(self,vec):
        if self.transform is False or self.transform is None:
            self.transform=[]
        self.transform.append({'translate':vec})
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

    def get_plane(self):
        if self.parent:
            return self.parent.get_plane()
        else:
            return False
    def get_config(self):
        if self.parent is not False:
            pconfig = self.parent.get_config()
        else:
            pconfig = False

        config = {}
        if pconfig is None or pconfig is False or 'transformations' not in pconfig or  pconfig['transformations'] is None:
            config['transformations']=[]
        else:
            config['transformations']=pconfig['transformations'][:]
        if type(self.transform ) is list:
            config['transformations']+=self.transform
        elif self.transform is not None:
            config['transformations'].append(self.transform)
        #       self.transform=None
        for v in self.varlist:
            if v !='transform' and v !='transformations':
                if hasattr(self,v) and getattr(self,v) is not None and getattr(self,v) is not False:
                    config[v] = getattr(self,v)
                elif pconfig is not None and pconfig is not False and v in pconfig and pconfig[v] is not None and pconfig[v] is not False:
                    config[v] = pconfig[v]
                else:
                    config[v] = None
        if pconfig is not False and 'zdir' in pconfig and pconfig['zdir'] is not None:
            config['zdir']= pconfig['zdir']
        else:
            config['zdir']=1
        if hasattr(self, 'layer') and self.layer is not None:
            l=copy.copy(self.get_plane().get_layer_config(self.layer))
            if 'thickness' in l and l['thickness'] is not None:
                config['thickness'] = l['thickness']
            if 'isback' not in l:
                l['isback']=False
        else:
            l={'thickness':0, 'zoffset':0, 'isback':False}
        if hasattr(self, 'thickness') and self.thickness is not None:
            config['thickness'] = self.thickness

# when drilling holes through a part we want to know the part thickness not the thickness of thie hole
        if hasattr(self, 'border') and self.border is not None and self.border is not False and hasattr(self.border, 'thickness') and self.border.thickness is not None:
            config['part_thickness'] = self.border.thickness
        else:
            config['part_thickness'] = config['thickness']

        if  (hasattr(self,'isback') and getattr(self,'isback') or l['isback']) and not (hasattr(self,'isback') and getattr(self,'isback') and l['isback']):
            config['zdir']*=-1
        if hasattr(self,'zoffset') and getattr(self,'zoffset') is not None:
            zoffset=self.zoffset
        elif 'zoffset' in l and l['zoffset'] is not None:
            zoffset = l['zoffset']
        else:
            zoffset = 0
        if pconfig is not False and 'zoffset' in pconfig and pconfig['zoffset'] is not None:
            config['zoffset'] = pconfig['zoffset'] + zoffset * config['zdir']
        else:
            config['zoffset'] = zoffset * config['zdir']

        if   (hasattr(self,'isback') and getattr(self,'isback') or l['isback']) and not (hasattr(self,'isback') and getattr(self,'isback') and l['isback']):
            config['zoffset'] += l['thickness'] * config['zdir']
        return config

    # is this a part we can render or just a multilayer pathgroup
    def renderable(self):
#               if (not hasattr(self, 'border') or self.border is False or self.layer is False or self.border is None) and not (hasattr(self,'ignore_border') and not (self.ignore_border==True) and (hasattr(self,'subpart') and self.subpart==True and self.layer is False)):
#                       return False
#               else:
#                       return True
        if  hasattr(self, 'border') and self.border is not False and self.layer is not False and self.border is not None:
            return True
        if hasattr(self,'ignore_border') and self.ignore_border==True and self.layer is not False:
            return True
        if hasattr(self,'subpart') and self.subpart==True and self.layer is False:
            return False
        return False


    def getParts(self, overview=True, first=True, config={}):
        ret=[]
        if self.isCopy and not overview:
            return []
        if first and  getattr(self, "_pre_render", None) and callable(self._pre_render):
            self._pre_render(config)
        for part in self.parts:
            if getattr(part, "_pre_render", None) and callable(part._pre_render):
                part._pre_render(config)
            ret.extend(part.getParts(overview,False, config))
        for path in self.paths:
            if getattr(self.paths[path], "_pre_render", None) and callable(self.paths[path]._pre_render):
                self.paths[path]._pre_render(config)
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
            raise TypeError( "Part border should have and obType and it should be a Path")
        else:
            #self.add_path(path,self.layer)
            if path.obType!="Path":
                raise TypeError("Part border should be a Path not a"+str(path.obType))
            self.border=copy.deepcopy(path)
            if self.border.side==None:
                self.border.side='out'
            self.border.parent=self
            self.border.is_border=True


    def add_internal_border(self,path):
        if hasattr(path,'obType') and path.obType=='Path':
            p=copy.deepcopy(path)
            p.is_border=True
            if p.side==None:
                p.side='in'
            p.parent=self
            self.internal_borders.append(p)
            return path
        else:
            raise TypeError("ERROR an internal border must be a Path not "+type(path))
    def add_copy(self,copy_transformations):
        # would
#               for t in copy_transformations:
            # TODO check this is a real transform
        self.number+=1;
        self.copies.append(copy_transformations)
    def add(self, path, layers=False):
        return self.add_path( path, layers)

    def add_path(self,path,layers = False, prepend=False):
        try:
            path.obType
        except NameError:
            raise TypeError( "Added object should be a Path, Pathgroup or Part and should have an obType, it may not have had init() run properly")
        else:
            if path.obType=='Part':
                path.parent = self
                if prepend:
                    self.parts.insert(0,path)
                else:
                    self.parts.append(path)
                return path
            elif (path.obType=='Path' or path.obType=="Pathgroup"):
                if layers is False:
                    layers = [self.layer]
                if type(layers) is not list:
                    layers = [layers]
                if layers == []:
#                                       print "add path with no layers to add it to "+str(path.trace)
                    return False
                for layer in layers:
                    # if layer is not used yet add a pathgroup and ant config
                    if layer not in list(self.paths.keys()):
                        self.paths[layer] = Pathgroup()
                        self.paths[layer].parent=self
#                                               self.paths[layer].parent=self
#                                               for v in self.varlist:
#                                                       if hasattr(self,v):
#                                                               setattr(self.paths[layer],v,getattr(self,v))

# deepcopy problem:
                    p=copy.deepcopy(path)
                    p.parent=self.paths[layer]
                    path.parent=self.paths[layer]
                    self.paths[layer].add_path(p, prepend)
                return p

            else:
                raise TypeError( "Added Object should be a Path, Pathgroup or Part not a "+str(path.obType))



    def make_copies(self):
        """Create multiple versions of any parts that should be copied"""
        if self.isCopy or self.copied:
            return False

        for part in self.parts:
            part.make_copies()
        for copytrans in self.copies:
            t = copy.deepcopy(self)
            t.isCopy = True
            t.transform = copytrans
            self.parent.add(t)

        self.copied = True

    # flatten the parts tree
    def get_layers(self):
        """Get all the Path/Pathgroupd in a part grouped by layer. Used when rendering"""
        layers={}


        for part in self.parts:
            # find all the contents of layers
            part.mode=self.mode
            part.callmode=self.callmode
# this may be dangerous as pre_render will be called more than oncee
            ls=part.get_layers()
            p=""
            if(ls is not False and ls is not None):
                for l in list(ls.keys()):
                    # if the part had no layer of its own we will inherit it from self
                    if l is None and hasattr(self, 'layer') and self.layer is not False:
                        tl=self.layer
                    else:
                        tl=l
                    if not part.isCopy:
                        if tl not in layers:
                            layers[tl]=[]
                        layers[tl].extend(ls[l])
                    # if the part should be copied, copy its parts which aren't in its core layer
                    # This means you can add an object in lots of places and mounting holes will be drilled
                    # or we are in an overview mode
                    elif not hasattr(part,'layer') or part.layer==False or l!=part.layer or hasattr(self, 'callmode') and milling.mode_config[self.callmode]['overview']:
                        if l not in layers:
                            layers[l]=[]
                        layers[l].extend(ls[l])
                    else:
                        pass
#                                               for copytrans in part.copies:
#                                                       for p in ls[l]:
#                                                               t = copy.deepcopy(p)
#                                                               t.is_copy = True
#                                                               t.transform = copytrans
#                                                               layers[l].append(t)
                    #if not hasattr(part,'layer') or part.layer==False or l!=part.layer:# or milling.mode_config[self.mode]['overview']:
        for l in list(self.paths.keys()):
#                       if not hasattr(self,'layer') or self.layer==False or l != self.layer:
            if (l==None or l==False):# and self.layer!=False and self.layer!=None:
                l=self.layer
            if 1==1:#l!=None and l!=False:
                self.paths[l].parent=self
                if l not in layers:
                    layers[l]=[]
                layers[l].append(self.paths[l])
    #       if hasattr(self, 'callmode') and milling.mode_config[self.callmode]['overview'] and self.layer!=None and self.layer!=False and self.border!=None and self.border!=False and hasattr(self,'layer'):
    #               if self.layer not in layers:
    #                       layers[self.layer]=[]
    #               layers[self.layer].append(self.border)
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
        """Is path contained by this part"""
        if self.border.contains(path) >-1:
            if len(self.internal_borders):
                for ib in self.internal_borders:
                    if ib.contains(path)!=-1:
                        return -1
            return 1
        return -1

    def overwrite(self,ain,b):
        a=copy.copy(ain)

        for i in list(b.keys()):
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
        #       if type(b['transform']) is list:
            a['transformations'].append(b['transform'])
        return a

# stores a series of parts which can overlap in layers
class Plane(Part):
    output_modes={}
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
        self.varlist = ['order','transform','side', 'colour', 'cutter','downmode','mode','prefix','postfix','settool_prefix','settool_postfix','rendermode','mode', 'sort', 'toolchange', 'linewidth', 'forcestepdown', 'forcecutter', 'stepdown','finishdepth', 'forcecolour', 'border', 'layer','partial_fill','finishing','fill_direction','precut_z', 'cutter', 'offset', 'blendTolerance']
        self.out=''
        self.isCopy=False
        self.copied=False
        self.copies=[]
        self.bom=[]
        self.number=1
    #       self.output_modes={}
        self.ignore_border=False
        for v in self.varlist:
            if v in config:
                self.config[v]=config[v]
            else:
                self.config[v]=None
    def get_plane(self):
        return self
    def get_config(self):
        return self.config
    def add_part_layer(self, part, material, thickness, z0=0,zoffset=0, add_back=False, isback=False, colour=False):
        self.add_layer(part.name, material, thickness, z0, zoffset, add_back, isback, colour)
        part.layer=part.name
        self.add(part)
    # A plane can have several layers
    def add_layer(self,name, material, thickness, z0=0,zoffset=0, add_back=False, isback=False, colour=False):
        if add_back:
            self.layers[name+'#back'] = Layer(name,material, thickness, z0, zoffset, isback=True, back=name, colour=colour)
            self.layers[name] = Layer(name,material, thickness, z0, zoffset, isback=False, back=name+'#back', colour=colour)
        else:
            self.layers[name] = Layer(name,material, thickness, z0, zoffset, isback=isback, colour=colour)
        return self.layers[name]
    def render_layer(self,layer):
        """Render all the parts in a layer"""

    def render_all(self,mode,config):
        """Render all parts in the Plane"""
        config['mode']=milling.mode_config[mode]['mode']
        self.make_copies()
        for part in self.getParts(milling.mode_config[mode]['overview'],config=config):
            if('parts' in config and type(config['parts']) is list and len(config['parts'])):
                if(part.name in config['parts']):
                    self.render_part(part, mode,config)
            else:
                self.render_part(part, mode,config)
    def list_all(self):
        """List all tha parts in this Plane"""
        for part in self.getParts():
            if hasattr(part, 'name'):
                print(str(part.name))

    def get_layer_config(self,layer):
        if layer in self.layers:
            return self.layers[layer].config
        else:
            raise Warning(str(layer)+" is referenced but doesn't exist.")

    def render_part(self, part, callmode, pconfig=False):
        global spindleDir
        spindleDir = None
        self.callmode = callmode
        self.modeconfig=milling.mode_config[callmode]
        self.mode=self.modeconfig['mode']
        self.modeconfig['callmode']=callmode
        self.callmode=callmode
        self.lay_out = {}
        layers = self.get_layers()
        output= collections.OrderedDict()
        c=0
        lastcutter=False
        config=copy.copy(self.modeconfig)
        if pconfig is not False:
            config=self.overwrite(config,pconfig)
        config=self.overwrite(config,self.config)
        if part.layer in layers and part.layer is not False and part.layer is not None:
            paths=layers[part.layer]
            config.update(self.get_layer_config(part.layer))
            if hasattr(part, 'cutter'):
                config['partcutter']=part.cutter
            else:
                config['partcutter']=None
        elif part.layer is not False and part.layer is not None:
            paths=[]
            config.update(self.get_layer_config(part.layer))
        else:
            paths=[]
        # if we are looking at a back layer and we are in a cutting mode then mirror the image
        if (part.layer in self.layers and self.layers[part.layer].config['isback'] is True or part.isback is True) and 'mirror_backs' in config and config['mirror_backs'] is True:
            if 'transformations' in config and type(config['transformations']) is list:
                config['transformations'].append({'mirror':[V(0,0),'x']})
#                               config['transformations'].insert(0,{'mirror':[V(0,0),'x']})
            else:
                config['transformations']=[{'mirror':[V(0,0),'x']}]
        part_config = copy.deepcopy(config)
        part_config=self.overwrite(part_config, part.get_config())
        if 'part_thickness' in part_config:
            config['thickness'] = part_config['thickness']

        # if it has been set to layer 'all' it should be in here
        if 'all' in layers:
            paths.extend(layers['all'])
# probably don't need this any more as it is now done in get_layers automatically
        #paths.extend(part.get_own_paths(config))

        # iterate through all the paths in the part's layer
        for path in paths:
            if getattr(path, "_pre_render", None) and callable(path._pre_render):
                path._pre_render(config)
        # if the path is within the bounds of the part then render it
            if path.obType=="Path" or path.obType=="Part":
                if not hasattr(part, 'border') or part.border is None or part.ignore_border or  part.contains(path)>-1 or hasattr(path,'is_border') and path.is_border:
                    (k,pa)=path.render(config)
                    if self.modeconfig['group'] is False:
                        k=c
                        c=c+1
                    #else:
                    #       k=getattr(path,self.modeconfig['group'])
                    #       if (k==False or k==None) and self.modeconfig['group']=='cutter':
                    #               k=config['cutter']
                    if 'render_string' not in self.modeconfig or self.modeconfig['render_string']:
                        if k not in list(output.keys()):
                            output[k]=''
                        output[k]+=''.join(pa)
                    else:
                        if k not in list(output.keys()):
                            output[k]=[]
                        output[k].append(pa)

                    lastcutter=k
            if path.obType=="Pathgroup":
                for p in path.get_paths(config):
                    if not hasattr(part, 'border') or part.ignore_border or part.contains(p)>-1:
                        (k,pa)=p.render(config)
                        if self.modeconfig['group'] is False:
                            k=c
                            c=c+1
                        #else:
                        #       k=config[self.modeconfig['group']]#getattr(p,self.modeconfig['group'])
                        if 'render_string' not in self.modeconfig or self.modeconfig['render_string']:
                            if k not in list(output.keys()):
                                output[k]=''
                            output[k] += ''.join(pa)
                        else:
                            if k not in list(output.keys()):
                                output[k]=[]
                            output[k].append(pa)

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
                    if 'render_string' not in self.modeconfig or self.modeconfig['render_string']:
                        if not k in output:
                            output[k]=''
                        output[k]+= ''.join(b)
                    else:
                        if k not in list(output.keys()):
                            output[k]=[]
                        output[k].append(pa)
                else:
                    if self.modeconfig['mode'] == 'scr':
                        output[k] += "LAYER " + str(self.modeconfig['border_layer'])+"\n"
                    output['__border']=b
            else:
                if 'render_string' not in self.modeconfig or self.modeconfig['render_string']:
                    if self.modeconfig['mode'] == 'scr':
                        output['__border'] = "LAYER " + str(self.modeconfig['border_layer'])+"\n"
                    else:
                        output['__border'] = ''
                    if type(b) is list:
                        output['__border']+=b[0]
                    else:
                        output['__border']+=b
                else:

                    output['__border']=[b]
        for key in sorted(output.keys(), key=str):
            if self.modeconfig['mode']=='gcode' or self.modeconfig['mode']=="simplegcode":
                self.writeGcodeFile(part.name,key, output[key], part.border, part_config)
            elif self.modeconfig['mode']=='svg':
                out+="<!-- "+str(part.name)+" - "+str(key)+" -->\n"+output[key]
            elif self.modeconfig['mode']=='scr':
                out+='\n\n'+output[key]
            elif self.modeconfig['mode'] in self.output_modes and self.modeconfig['group']!=False:
                self.output_modes[self.modeconfig['mode']](self, part.name,key, output[key], part.border, config)
        key = ''
        if self.modeconfig['mode']=='svg' or self.modeconfig['mode']=='scr':
        #       f=open(parent.name+"_"+self.name+"_"+part.name)
            if part.border != None:
                centre=part.border.centre
            else:
                centre=V(0,0)
            if self.modeconfig['label'] and  self.modeconfig['mode'] == 'svg':
                out+="<text transform='scale(1,-1)' text-anchor='middle' x='"+str(int(centre[0]))+"' y='"+str(-int(centre[1]))+"'>"+str(part.name)+"</text>"
            if 'layout' in pconfig and pconfig['layout']:
                self.lay_out['svg'] = '<g>'+out+'</g>'
                return True
            if self.modeconfig['overview']:
                self.out+='<g>'+out+'</g>'
            elif part.name is not None:
                filename=self.name+"_"+part.name+config['file_suffix']
                f=open(filename,'w')
                f.write( self.modeconfig['prefix'] + out + self.modeconfig['postfix'] )
                f.close()
        elif self.modeconfig['mode'] in self.output_modes and self.modeconfig['group'] == False:
            self.output_modes[self.modeconfig['mode']](self, part.name,key, output, part.border, config)

    def repeatGcode(self, output, config):
        if 'repeatmode' in config:
            repeatmode=config['repeatmode']
        else:
            repeatmode='regexp'
        if 'repeatpattern' in config:
            repeatpattern=config['repeatpattern']
        else:
            repeatpattern='rect'
        if 'repeatoffset' in config:
            repeatoffset=config['repeatoffset']
        else:
            repeatoffset=None
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
#                               xreg=re.compile('X[\d\.-]+')
#                               yreg=re.compile('Y[\d\.-]+')
            outputs=[]
            for y in range(0,int(config['repeaty'])):
                for x in range(0,int(config['repeatx'])):
                    docut=True
                    if repeatpattern=='cp_int2':
                        xp=x+1
                    else:
                        xp=x
                    if repeatpattern=='cp_ext' or repeatpattern=='cp_int' or repeatpattern=='cp_int2':
                        xoff=float(x)*float(config['xspacing'])*math.sin(math.pi/3)
                        print(type(repeatoffset))
                        if xp%2:
                            yoff=float(y)*float(config['yspacing'])
                        else:
                            if repeatoffset:
                                yoff = 1.0*float(repeatoffset) + float(y)*float(config['yspacing'])
                            else:
                                yoff=(0.5+float(y))*float(config['yspacing'])
                        print("yoff = "+str(yoff))
                        if repeatpattern in ['cp_int', 'cp_int2'] and y==int(config['repeaty'])-1 and not xp%2:
                            docut=False
                    else:
                        xoff=x*float(config['xspacing'])
                        yoff=y*float(config['yspacing'])
                    if docut:
                        outputs.append( "(copy x="+str(xoff)+" y="+str(yoff)+")\n"+self.offset_gcode(output, V(xoff, yoff)))
            output2="\n".join(outputs)
        return output2

    def writeGcodeFile(self,partName, key, output, border, config):
        if 'shortFilename' in config and config['shortFilename']:
            filename = str(partName)+str(key)
        else:
            filename=str(partName)+"_"+str(self.name)+"_"+str(key)
            if len(config['command_args']):
                for k in list(config['command_args'].keys()):
                    filename=k+"_"+filename+"-"+config['command_args'][k]
            if 'material' in config:
                filename+='_'+str(config['material'])
            if 'thickness' in config:
                filename+="_thickness-"+str(config['thickness'])
            if 'cutter' in config:
                filename+="_cutter-"+str(config['cutter'])
        if 'zero' in config and config['zero']=='bottom_left' and border!=None:
            if 'layout' in config and config['layout']:
                offset = V(0,0)
                if 'offset' in config:
                    offset = config['offset']
            elif not hasattr(border,'boundingBox') or 'bl' not in list(border.boundingBox.keys()):
                border.polygonise()
            offset=-border.boundingBox['bl']
            output = self.offset_gcode( output, offset)
        else:
            offset = V(0,0)
        if 'repeatx' in config and 'repeaty' in config and 'xspacing' in config and 'yspacing' in config and ('layout' not in config or not config['layout']):
        #       output2+='\nG10 L2 P1 X0 Y0\n'
            output = self.repeatGcode(output, config)
            filename+='_'+str(config['repeatx'])+'x_'+str(config['repeaty'])+'y'
            #output=output2
        output=self.offset_gcode(output, config['offset'])
        config['prefix']=config['prefix'].replace("%zclear%", str(config['clear_height']))
        # if we are making gcode we we should have tool changes in there
        if config['mode']=='gcode':
            toolid=str(milling.tools[config['cutter']]['id'])
            output = "\n"+config['settool_prefix']+toolid+config['settool_postfix']+"\n"+output
        if 'zbase' in config and config['zbase']:
            zoff = config['thickness']
            output = self.offset_gcode( output, V(0,0,zoff))
        if 'layout' in config and config['layout']:
            if key not in self.lay_out:
                self.lay_out[key]=''
            self.lay_out[key]+=output
        else:
            output = config['prefix']+"\n"+output+"\n"+config['postfix']
            if 'noblank' in config and config['noblank']:
                print("removing blank lines")
                lines = output.split("\n")

                lines2 = [line for line in lines if line.strip() != ""]
                output = ''
                for line in lines2:
                    output += line + "\n"
            output += "\n"
            f=open(self.sanitise_filename(filename+config['file_suffix']),'w')
            f.write(output)
            f.close()
            if 'dosfile' in config and config['dosfile']:
                os.system("/usr/bin/unix2dos "+self.sanitise_filename(filename+config['file_suffix']))

    def offset_gcode(self, output, offset):
        def reg_add_offset(m):
            if len(m.group(1)) and len(m.group(2)):
                axismap={'X':0, 'Y':1, 'Z':2}
                val=float(m.group(2))
                val += offset[axismap[m.group(1)]]
                return m.group(1)+str(round(val,3))
            else:
                return m.group(0)

        reg = re.compile('([XYZ])([\d\.-]+)')
        tempoutput=output
        return reg.sub(reg_add_offset, tempoutput)

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
