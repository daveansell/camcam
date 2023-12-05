import solid
from  path import *
from cc3d import *

class SolidPath(Path):
    def __init__(self, **config):
        self.init(config)

    def getSolid(self):
        return(solid.cube())

    def render3D(self, pconfig, border=False):
        global _delta, PRECISION, SCALEUP
        extruded=self.getSolid()
        p=self
        p.rotations_to_3D()
        while(p and type(p) is not Plane and not ( hasattr(p,'renderable') and p.renderable())):# and (c==0 or not p.renderable() )):
                if hasattr(p, 'transform') and p.transform is not None and p.transform is not False and 'matrix3D' in p.transform:
                        if type(p.transform['matrix3D'][0]) is list or type(p.transform['matrix3D'][0]) is Vec:
                                extruded=solid.translate([-p.transform['matrix3D'][0][0], -p.transform['matrix3D'][0][1],-p.transform['matrix3D'][0][2]])(extruded)
                                extruded=solid.multmatrix(m=p.transform['matrix3D'][1])(extruded)
                                extruded=solid.translate([p.transform['matrix3D'][0][0], p.transform['matrix3D'][0][1],p.transform['matrix3D'][0][2]])(extruded)
                        else:
                                extruded=solid.multmatrix(m=p.transform['matrix3D'])(extruded)

                if hasattr(p, 'transform') and p.transform is not None and p.transform is not False and 'rotate3D' in p.transform:
                        if type(p.transform['rotate3D'][0]) is list or type(p.transform['rotate3D'][0]) is Vec:
                                if p.transform['rotate3D'][0]!=[0,0,0]:
                                        extruded=solid.translate([-p.transform['rotate3D'][0][0], -p.transform['rotate3D'][0][1],-p.transform['rotate3D'][0][2]])(extruded)
                                extruded=solid.rotate([p.transform['rotate3D'][1][0], p.transform['rotate3D'][1][1],p.transform['rotate3D'][1][2] ])(extruded)
                                if p.transform['rotate3D'][0]!=[0,0,0]:
                                        extruded=solid.translate([p.transform['rotate3D'][0][0], p.transform['rotate3D'][0][1],p.transform['rotate3D'][0][2]])(extruded)
                        else:
                                extruded=solid.rotate([p.transform['rotate3D'][0], p.transform['rotate3D'][1],p.transform['rotate3D'][2] ])(extruded)
                if hasattr(p, 'transform') and p.transform is not None and p.transform is not False and 'translate3D' in p.transform:
                        extruded=solid.translate([p.transform['translate3D'][0], p.transform['translate3D'][1],p.transform['translate3D'][2] ])(extruded)
                p=p.parent
        return [extruded]

class Sphere(SolidPath):
    def __init__(self, pos, rad, **config):
        self.init(config)
        self.pos=pos
        self.rad=rad
        self.closed=True
        self.add_point(pos,'circle',rad)

    def getSolid(self):
        return solid.translate(self.pos)(solid.sphere(r=self.rad))

class Cuboid(SolidPath):
    def __init__(self, pos, width, height, depth, **config):
        self.init(config)
        if 'centre' in config:
            self.centre= config['centre']
        else:
            self.centre= False
        self.pos=pos
        self.width=width
        self.height=height
        self.depth=depth
        self.closed=True
        self.add_point(pos,'circle',width/2)

    def getSolid(self):
        print(solid.translate(self.pos)(solid.cube([self.width, self.height, self.depth], center=self.centre)))
        return solid.translate(self.pos)(solid.cube([self.width, self.height, self.depth], center=self.centre))


class Cylinder(SolidPath):
    def __init__(self, pos, rad1=None, rad2=None, height=1, rad=None, **config):
        self.init(config)
        if 'centre' in config:
            self.centre= config['centre']
        else:
            self.centre= False
        if rad is not None:
            rad1=rad
            rad2=rad
        self.pos=pos
        self.rad1=rad1
        self.rad2=rad2
        self.height=height
        self.closed=True
        self.add_point(pos,'circle',rad2)
        self.translate3D(pos)
      #  self.centre=pos
        #self.centre=pos

    def getSolid(self):
        return solid.translate(self.pos)(solid.cylinder(r1=self.rad1, r2=self.rad2, h=self.height, center=self.centre))

class CSScrew(SolidPath):
    def __init__(self, pos, size, length, mode,**config):
        self.init(config)
        self.closed=True
        self.pos=pos
        self.size=size
        self.length=length
        self.mode=mode
        if mode=='clearance':
            self.add_point(PCircle(pos,radius=milling.bolts[self.size]['clearance']/2))
        else:
            self.add_point(PCircle(pos,radius=milling.bolts[self.size]['tap']/2))
        if 'rotate' in config:
            self.rotate=config['rotate']
        else:
            self.rotate=[0,0,0]
    def getSolid(self):
        ret = []
        if self.mode=='clearance':
            ret.append(solid.cylinder(r=milling.bolts[self.size]['clearance']/2, h=self.length)) 
            ret.append(
                solid.translate(V(0,0,-0.1))(
                    solid.cylinder(
                        r1=milling.bolts[self.size]['cs']['head_d']/2*(milling.bolts[self.size]['cs']['head_l']+0.1)/milling.bolts[self.size]['cs']['head_l'], 
                        r2=milling.bolts[self.size]['tap']/2, 
                        h=milling.bolts[self.size]['cs']['head_l']+0.1
                    )
                )
            )
            ret.append(
                solid.translate(V(0,0,-milling.bolts[self.size]['cs']['head_l']-10.1))(
                    solid.cylinder(
                        r1=milling.bolts[self.size]['cs']['head_d']/2*(milling.bolts[self.size]['cs']['head_l']+0.1)/milling.bolts[self.size]['cs']['head_l'], 
                        r2=milling.bolts[self.size]['cs']['head_d']/2*(milling.bolts[self.size]['cs']['head_l']+0.1)/milling.bolts[self.size]['cs']['head_l'], 
                        h=milling.bolts[self.size]['cs']['head_l']+10
                    )
                )   
            )
                
        elif self.mode=='thread':
            ret.append(solid.cylinder(r=milling.bolts[self.size]['tap']/2, h=self.length)) 


        return solid.translate(self.pos)(solid.rotate(self.rotate)(solid.union()(*ret)))

class CapScrew(SolidPath):
    def __init__(self, pos, size, length, mode,**config):
        self.init(config)
        self.closed=True
        self.pos=pos
        self.size=size
        self.length=length
        self.mode=mode
        if mode=='clearance':
            self.add_point(PCircle(pos,radius=milling.bolts[self.size]['clearance']/2))
        else:
            self.add_point(PCircle(pos,radius=milling.bolts[self.size]['tap']/2))
        if 'rotate' in config:
            self.rotate=config['rotate']
        else:
            self.rotate=[0,0,0]
    def getSolid(self):
        ret = []
        if self.mode=='clearance':
            ret.append(solid.cylinder(r=milling.bolts[self.size]['clearance']/2, h=self.length)) 
            ret.append(
                solid.translate(V(0,0,-10))(
                    solid.cylinder(
                        r1=milling.bolts[self.size]['allen']['head_d']/2+0.3,
                        r2=milling.bolts[self.size]['allen']['head_d']/2+0.3, 
                        h=milling.bolts[self.size]['cs']['head_l']+10
                    )
                )
            )
                
        elif self.mode=='thread':
            ret.append(solid.cylinder(r=milling.bolts[self.size]['tap']/2, h=self.length)) 


        return solid.translate(self.pos)(solid.rotate(self.rotate)(solid.union()(*ret)))

class HullSpheres(SolidPath):
    def __init__(self, pos, corners, **config):
        self.init(config)
        self.closed=True
        self.pos=pos
        if 'rad' in config:
            self.rad=config['rad']
        else:
            self.rad=0.01
        self.corners = corners
    def getSolid(self):
        spheres=[]
        for c in self.corners: 
            spheres.append(solid.translate(c)( solid.sphere(r=self.rad)))
        return solid.translate(self.pos)(
                solid.hull()(*spheres)
                )
class RoundedCuboid(SolidPath):
    def __init__(self, pos, width, height, depth, rad, **config):
        self.init(config)
        self.closed=True
        self.W = width/2-rad
        self.H = height/2 - rad
        self.D = depth/2 -rad
        self.rad = rad
        self.pos = pos
        self.add_point(pos,'circle',rad)
    def getSolid(self):
        W=self.W
        H=self.H
        D=self.D
        rad=self.rad
        return solid.translate(self.pos)(
                solid.hull()(
                    solid.translate([-W,H,D])( solid.sphere(r=rad)),
                    solid.translate([-W,-H,D])( solid.sphere(r=rad)),
                    solid.translate([W,H,D])( solid.sphere(r=rad)),
                    solid.translate([W, -H,D])( solid.sphere(r=rad)),

                    solid.translate([W, H,-D])( solid.sphere(r=rad)),
                    solid.translate([-W, H,-D])( solid.sphere(r=rad)),
                    solid.translate([ W,-H,-D])( solid.sphere(r=rad)),
                    solid.translate([-W,-H,-D])( solid.sphere(r=rad))
                )
                )
class Text3D(SolidPath):
    def __init__(self, pos, text, height, **config):
        self.init(config)
        self.pos=pos
        self.text=text
        self.args = {}
        self.height = height
        argNames = ['valign', 'size', 'halign', 'font']
        for n in argNames:
            if n in config:
                self.args[n]=config[n]
        self.args['text']=text
        self.closed=True
        self.add_point(pos,'circle',1)

    def getSolid(self):
        self.translate3D(self.pos)
        return solid.linear_extrude(height=self.height)(solid.text(**self.args))

class SolidExtrude(SolidPath):
    def __init__(self, pos, shape,height, **config):
        self.init(config)
        self.shape=shape
        self.pos = pos
        self.closed=True
        self.translate3D(pos)
        self.height=height
        if 'twist' in config:
                self.twist = config['twist']
        else:
                self.twist = 0
        if 'centre' in config:
                self.centre=config['centre']
        else:
                self.centre=False
        if 'convexity' in config:
                self.convexity=config['convexity']
        else:
                self.convexity=10
        if 'scale' in config:
                self.scale=config['scale']
        else:
                self.scale=1

    def getSolid(self):
        global RESOLUTION
        outline=[]
        points = self.shape.polygonise(RESOLUTION)
        for p in points:
            outline.append( [round(p[0],PRECISION)*SCALEUP, round(p[1],PRECISION)*SCALEUP ])
        outline.append([round(points[0][0],PRECISION)*SCALEUP, round(points[0][1],PRECISION)*SCALEUP])
        polygon = solid.polygon(outline)
        print("scale="+str(self.scale))
        return self.transform3D(self, solid.linear_extrude(height=self.height, convexity=self.convexity, scale=self.scale,  center=self.centre, twist=self.twist)(polygon))




class SolidOfRotation(SolidPath):
    def __init__(self, pos, shape, **config):
        self.init(config)
        self.shape=shape
        self.pos = pos
        self.closed=True
        self.translate3D(pos)
        if 'convexity' in config:
            self.convexity = config['convexity']
        else:
            self.convexity = 10
        if 'angle' in config:
            self.angle = config['angle']
        self.add_points(shape.points)
    def getSolid(self):
        global RESOLUTION
        outline=[]
        points = self.shape.polygonise(RESOLUTION)
        for p in points:
            outline.append( [round(p[0],PRECISION)*SCALEUP, round(p[1],PRECISION)*SCALEUP ])
        outline.append([round(points[0][0],PRECISION)*SCALEUP, round(points[0][1],PRECISION)*SCALEUP])
        polygon = solid.polygon(outline)
        if hasattr(self,"angle"):
            return solid.rotate_extrude(convexity=self.convexity, angle = self.angle)(polygon)
        else:
            return solid.rotate_extrude(convexity=self.convexity)(polygon)

class ExtrudeU(SolidPath):
    def __init__(self, pos, shape, straightLen, **config):
        self.init(config)
        self.shape=shape
        self.closed=True
        self.straightLen=straightLen
        self.pos=pos
        self.translate3D(pos)
        if 'convexity' in config:
            self.convexity = config['convexity']
        else:
            self.convexity = 10
        #print("ExtrudeU __init_-")
    def getSolid(self):
        global RESOLUTION
        #print("ExtrudeU getSolid")
        outline=[]
        points = self.shape.polygonise(RESOLUTION)
        for p in points:
            outline.append( [round(p[0],PRECISION)*SCALEUP, round(p[1],PRECISION)*SCALEUP ])
        outline.append([round(points[0][0],PRECISION)*SCALEUP, round(points[0][1],PRECISION)*SCALEUP])

        outline2 = copy.deepcopy(outline)
        for p in points:
            outline2.append( [-round(p[0],PRECISION)*SCALEUP, round(p[1],PRECISION)*SCALEUP ])
        polygon = solid.polygon(outline)
        polygon2 = solid.polygon(outline2)

        return self.transform3D(self, 
                solid.hull()(
                    solid.rotate_extrude(convexity=self.convexity)(polygon),
                    solid.rotate([90,0,0])(
                        solid.linear_extrude(height=self.straightLen)(solid.hull()(polygon2))
                    )
                )
            )
class SlopedDisc(SolidOfRotation): 
    def __init__(self, pos, innerRad, outerRad, height, **config):
        self.init(config)
        if 'holeRad' in config:
            holeRad=config['innerRad']
        else:
            holeRad=0.01
        self.shape=Path(closed=True)
        self.shape.add_point(V(outerRad,0))
        self.shape.add_point(V(innerRad,height/2))
        self.shape.add_point(V(holeRad,height/2))
        self.shape.add_point(V(holeRad,-height/2))
        self.shape.add_point(V(innerRad,-height/2))
        self.pos = pos
        self.closed=True
        self.translate3D(pos)
        if 'convexity' in config:
            self.convexity = config['convexity']
        else:
            self.convexity = 10
        self.add_points(self.shape.points)

class Torus(SolidOfRotation):
    def __init__(self, pos, bigRad, smallRad, **config):
        self.init(config)
        self.translate3D(pos)
        self.smallRad = smallRad
        self.bigRad = bigRad
        if 'convexity' in config:
            self.convexity = config['convexity']
        else:
            self.convexity = 10
        if 'angle' in config:
            self.angle=config['angle']
        else:
            self.angle=360.0
        self.closed=True
        self.add_point(PCircle(pos, radius=smallRad))

    def getSolid(self):
        return solid.rotate_extrude(convexity = self.convexity, angle=self.angle)(solid.translate([self.bigRad,0,0])(solid.circle(r=self.smallRad)))


class RoundedTube(SolidOfRotation):
    def __init__(self, pos, rad, length, **config):
        self.init(config)
        self.shape=Path(closed=True)
        self.shape.add_point(V(0.01, length/2))
        self.shape.add_point(PIncurve(V(rad, length/2), radius=rad-0.1))
        self.shape.add_point(PIncurve(V(rad, -length/2), radius=rad-0.1))
        self.shape.add_point(V(0.01, -length/2))
        self.length=length
        self.rad=rad
        self.convexity=10
        self.add_points(shape.points)
    def getSolid(self):
        return solid.union()(super().getSolid(), Cylinder(V(0,0), 0.11, .11, height=self.length, centre=True).getSolid())

class PointyTube(RoundedTube):
    def __init__(self, pos, rad, length, **config):
        self.init(config)
        self.shape=Path(closed=True)
        self.shape.add_point(V(0.01, length/2,0))
        self.shape.add_point(V(rad, length/2-rad,0))
        self.shape.add_point(V(rad, -length/2+rad,0))
        self.shape.add_point(V(0.01, -length/2,0))
        self.length=length
        self.rad=rad
        self.convexity=10
        self.closed=True
        self.add_points(self.shape.points)

class PointyTopCuboid(SolidExtrude):
    def __init__(self, pos, width, height, depth, **config):
        self.init(config)
        if 'convexity' in config:
            self.convexity=config['convexity']
        else:
            self.convexity=10
        if 'double' in config:
            double=True
        else:
            double=False

        self.twist=0
        self.init(config)
        self.shape=Path(closed=True)
        self.shape.add_point(V(-depth/2,-width/2))
        self.shape.add_point(V(-depth/2, width/2))
        self.shape.add_point(V( depth/2, width/2))
        if double:
            self.shape.add_point(V( depth/2+width/2, 0))
            self.shape.add_point(V( depth/2, -width/2))
        else:
            self.shape.add_point(V( depth/2+width, -width/2))
        self.height=height
        self.translate3D(V(0,0,-height/2))
        self.rotate3D([0,-90,90])
        self.scale =1
        self.translate3D(pos)

class Polyhedron(SolidPath):
    def __init__(self, points, faces, **config):
        self.init(config)
        self.closed=True
        if 'convexity' in config:
            self.convexity=config['convexity']
        else:
            self.convexity=10
        self.init(config)
        self.inPoints = points
        self.faces = faces
        self.add_point(PCircle(V(0,0), rad=1))
    def getSolid(self):
        return solid.polyhedron(points=self.inPoints, faces=self.faces, convexity=self.convexity)

class CylindricalPolyhedron(Polyhedron):
    def __init__(self, rFunc, height, **config):
        self.init(config)
        self.closed=True
        if 'convexity' in config:
            self.convexity=config['convexity']
        else:
            self.convexity=10
        if 'zStep' in config:
            zStep = config['zStep']
        else:
            zStep = 1.0
        if 'z0' in config:
            self.z0=float(config['z0'])
        else:
            self.z0=0.0
        if 'gradient' in config:
            gradient = config['gradient']
        else:
            gradient = V(0,0)
        height = float(height)
        nz = (height-self.z0)/zStep +1
        self.facetLength = nz
        if 'facets' in config:
            self.facets = config['facets']
        else:
            self.facets = 30
        tStep = 360.0/self.facets
        self.inPoints = [V(0,0,self.z0), V(0,0,height)]
        self.faces = []
        self.first=2
        z=float(self.z0)
        
        t=0.0
        f=0
        while t<360.0:
            c=0
            z=self.z0
            while z<height:

                self.inPoints.append(gradient*z+rotate(V(rFunc(z,t),0,z), t))
                if(z==self.z0):
                    self.faces.append([ self.pn(f,c), 0,  self.pn(f+1,c)])
                else:
                    self.faces.append([
                        self.pn(f+1,c-1),
                        self.pn(f+1,c), 
                        self.pn(f,c), 
                        self.pn(f, c-1), 
                        ])
                z+=zStep
                c+=1
            self.inPoints.append(gradient*height+rotate(V(rFunc(height,t),0,height), t))
        #    c+=1
            self.faces.append([
                self.pn(f+1,c-1),
                self.pn(f+1,c), 
                self.pn(f,c), 
                self.pn(f,c-1), 
                ])
            self.faces.append([
                self.pn(f,c), 
                self.pn(f+1,c), 
                    1
                ])
            t+=tStep
            f+=1
            c+=1
        self.add_point(PCircle(V(0,0), radius=1))
        self.closed=True
    def pn(self, facet, c):
        return int(self.first+(facet%self.facets) * self.facetLength + c) 

#class Hull(SolidPath):
#    def __init__(self, ):
class PathPolyhedron(Polyhedron):
    def __init__(self, xsection, path, **config):
        self.init(config)
        self.closed=True
        if 'convexity' in config:
            self.convexity=config['convexity']
        else:
            self.convexity=10
        if 'zStep' in config:
            zStep = config['zStep']
        else:
            zStep = 1.0
        if 'x0' in config:
            lastx=config['x0'].normalize()
        else:
            lastx = V(1,0,0)
        # preserve x direction
        if 'samex' in config:
            samex=config['samex']
        else:
            samex=False

        if 'gradient' in config:
            gradient = config['gradient']
        else:
            gradient = V(0,0)
        if xsection.find_direction({})=='cw':
            xsection.points.reverse()
        pxsection = xsection.polygonise()
        ppath = path.polygonise()
        self.faces = []
        self.rings=[]
        self.inPoints=[]
        pc=0
        s="path="
        for p in path.points:
            s+=str(p.pos)+" "
        
        for p in range(0,len(ppath)):
            if p==0:
                along = (ppath[1]-ppath[0]).normalize()
            elif p==len(ppath)-1:
                along = (ppath[len(ppath)-1]-ppath[len(ppath)-2]).normalize()
            else:
                along = ((ppath[p]-ppath[p-1]).normalize()+(ppath[p+1]-ppath[p]).normalize())/2
            if samex:
                x = lastx
                y = -along.cross(lastx).normalize()
            elif p==0: # if x hasn't been specified pick an arbitrary x
                y=along.cross(V(1,0,0))
                if y.length()<0.001:
                    y=along.cross(V(0,1,0)).normalize()
                else:
                    y=y.normalize()
                x=along.cross(y).normalize()
                lastx=x
                samex=True
            else:
                y = along.cross(lastx).normalize()
                x = along.cross(y).normalize()
            if(x.dot(lastx)<0):
                x*=-1
            self.rings.append([])
            for o in range(0,len(pxsection)):
                #print("faces ppath="+str(ppath[p])+" pxsection[][0]="+str(pxsection[o][0]*x)+" [1]"+str(pxsection[o][1]*y))
                self.inPoints.append(ppath[p]+x*pxsection[o][0]+y*pxsection[o][1])
                self.rings[-1].append(pc)
                if p>0 and o>0:
                    self.faces.append([ self.rings[-1][o], self.rings[-1][o-1], self.rings[-2][o-1], self.rings[-2][o]])
                pc+=1
            if p>0:
                self.faces.append([ self.rings[-1][0], self.rings[-1][-1], self.rings[-2][-1], self.rings[-2][0]])
            lastx = x
        self.faces.append(reversed(self.rings[0]))
#        self.faces[-1].reverse()
        self.faces.append(self.rings[-1])
        self.add_point(PCircle(V(0,0), radius=1))
        self.closed=True
#        print("faces Points="+str(self.inPoints))
 #       print("faces="+str(self.faces))
#class Hull(SolidPath):
#    def __init__(self, ):
class SurfacePolyhedron(Polyhedron):
    def __init__(self, vFunc, bFunc, xmin, xmax, ymin, ymax, **config):

        self.init(config)
        self.closed=True
        if 'convexity' in config:
            self.convexity=config['convexity']
        else:
            self.convexity=10
        if 'step' in config:
            self.step = config['step']
        else:
            self.step = 1.0
        if 'sFunc' in config:
            sFunc = config['sFunc']
        else:
            sFunc = False
        if 'sbFunc' in config:
            sbFunc = config['sbFunc']
        else:
            sbFunc = False
        cols = math.floor((xmax-xmin)/self.step)+1
        rows = math.floor((ymax-ymin)/self.step)+1
    #    self.basePoints = []
   #     self.leftSide = []
  #      self.rightSide = []
 #       self.topSide = []
#        self.bottomSide = []
        self.faces = []
        self.inPoints = []
        self.first=0
        self.faces=[]
        self.pArray= [[0 for k in range(0,rows+1)] for j in range(0,cols+1)]#[[0]*cols]*rows
        self.bArray= [[0 for k in range(0,rows+1)] for j in range(0,cols+1)]#[[0]*cols]*rows
        self.sArray= [[0 for k in range(0,rows+1)] for j in range(0,cols+1)]#[[0]*cols]*rows
        self.sbArray= [[0 for k in range(0,rows+1)] for j in range(0,cols+1)]#[[0]*cols]*rows
        x = xmin
        p=0
        X=0
        Y=0
        while x<xmax:
            y = ymin
            Y = 0
            while y<ymax:
                self.inPoints.append(vFunc(x,y))
                self.pArray[X][Y]=p
                p+=1
                self.inPoints.append(bFunc(x,y))
                self.bArray[X][Y]=p
                p+=1
                Y+=1
                y+=self.step
            if(X>0 and Y>0):
                self.inPoints.append(vFunc(x,ymax))
                self.pArray[X][Y]=p
                p+=1
                self.inPoints.append(bFunc(x,ymax))
                self.bArray[X][Y]=p
                p+=1
   #             Y+=1
   #             self.faces.append([self.pArray[X][Y], self.pArray[X-1][Y], self.pArray[X-1][Y-1], self.pArray[X][Y-1]])

            x+=self.step
            X+=1
        Y=0
        y=ymin
        x=xmax
        while y<ymax:
            self.inPoints.append(vFunc(x,y))
            self.pArray[X][Y]=p
            p+=1
            self.inPoints.append(bFunc(x,y))
            self.bArray[X][Y]=p
            p+=1
            Y+=1
            y+=self.step
        self.inPoints.append(vFunc(xmax,ymax))
        self.pArray[X][Y]=p
        p+=1
        self.inPoints.append(bFunc(xmax,ymax))
        self.bArray[X][Y]=p
        p+=1


        # apply a second function perpendicular to the surface
        if sFunc:
            for X in range(0, cols-1):
                for Y in range(0,rows-1):
                    if X==0:
                        xvec1 = (self.inPoints[self.pArray[X+1][Y]]-self.inPoints[self.pArray[X][Y]]).normalize()
                    else:
                        xvec1 = (self.inPoints[self.pArray[X][Y]]-self.inPoints[self.pArray[X-1][Y]]).normalize()
                    if X==cols-2:
                        xvec2 = (self.inPoints[self.pArray[X][Y]]-self.inPoints[self.pArray[X-1][Y]]).normalize()
                    else:
                        xvec2 = (self.inPoints[self.pArray[X+1][Y]]-self.inPoints[self.pArray[X][Y]]).normalize()
                    xvec = (xvec1+xvec2)/2
                    if Y==0:
                        yvec1 = (self.inPoints[self.pArray[X][Y+1]]-self.inPoints[self.pArray[X][Y]]).normalize()
                    else:
                        yvec1 = (self.inPoints[self.pArray[X][Y]]-self.inPoints[self.pArray[X][Y-1]]).normalize()
                    if Y==rows-2:
                        yvec2 = (self.inPoints[self.pArray[X][Y]]-self.inPoints[self.pArray[X][Y-1]]).normalize()
                    else:
                        yvec2 = (self.inPoints[self.pArray[X][Y+1]]-self.inPoints[self.pArray[X][Y]]).normalize()
                    yvec = (yvec1+yvec2)/2
                    normal = -xvec.cross(yvec)
                    point = self.inPoints[self.pArray[X][Y]]
                    self.sArray[X][Y] = normal*sFunc(point[0], point[1])
            for X in range(0, cols-1):
                for Y in range(0,rows-1):
                    self.inPoints[self.pArray[X][Y]]+=self.sArray[X][Y]

        if sbFunc:
            for X in range(0, cols-1):
                for Y in range(0,rows-1):
                    if X==0:
                        xvec1 = (self.inPoints[self.bArray[X+1][Y]]-self.inPoints[self.bArray[X][Y]]).normalize()
                    else:
                        xvec1 = (self.inPoints[self.bArray[X][Y]]-self.inPoints[self.bArray[X-1][Y]]).normalize()
                    if X==cols-2:
                        xvec2 = (self.inPoints[self.bArray[X][Y]]-self.inPoints[self.bArray[X-1][Y]]).normalize()
                    else:
                        xvec2 = (self.inPoints[self.bArray[X+1][Y]]-self.inPoints[self.bArray[X][Y]]).normalize()
                    xvec = (xvec1+xvec2)/2
                    if Y==0:
                        yvec1 = (self.inPoints[self.bArray[X][Y+1]]-self.inPoints[self.bArray[X][Y]]).normalize()
                    else:
                        yvec1 = (self.inPoints[self.bArray[X][Y]]-self.inPoints[self.bArray[X][Y-1]]).normalize()
                    if Y==rows-2:
                        yvec2 = (self.inPoints[self.bArray[X][Y]]-self.inPoints[self.bArray[X][Y-1]]).normalize()
                    else:
                        yvec2 = (self.inPoints[self.bArray[X][Y+1]]-self.inPoints[self.bArray[X][Y]]).normalize()
                    yvec = (yvec1+yvec2)/2
                    normal = -xvec.cross(yvec)
                    point = self.inPoints[self.bArray[X][Y]]
                    self.sbArray[X][Y] = normal*sbFunc(point[0], point[1])
            for X in range(0, cols-1):
                for Y in range(0,rows-1):
                    self.inPoints[self.bArray[X][Y]]+=self.sbArray[X][Y]

        for X in range(0, cols-1):
            for Y in range(0,rows-1):
                if(X>0 and Y>0):
                    self.faces+=self.quad([self.pArray[X][Y], self.pArray[X-1][Y], self.pArray[X-1][Y-1], self.pArray[X][Y-1]])
                    self.faces+=self.quad([self.bArray[X-1][Y], self.bArray[X][Y], self.bArray[X][Y-1], self.bArray[X-1][Y-1]])

       #     for j in range(0,rows):
      #          s+=" "+str(self.bArray[i][j])
     #       print (s)
        # work around the edges
        for X in range(1, cols-1):
            pass
            self.faces+=self.quad([self.pArray[X][0], self.pArray[X-1][0], self.bArray[X-1][0], self.bArray[X][0]])
            self.faces+=self.quad([self.pArray[X-1][rows-2], self.pArray[X][rows-2], self.bArray[X][rows-2], self.bArray[X-1][rows-2]])
        for Y in range(1, rows-1):
            pass
            self.faces+=self.quad([self.pArray[0][Y], self.pArray[0][Y-1], self.bArray[0][Y-1], self.bArray[0][Y]])
            self.faces+=self.quad([self.pArray[cols-2][Y-1], self.pArray[cols-2][Y], self.bArray[cols-2][Y], self.bArray[cols-2][Y-1]])

        self.add_point(PCircle(V(0,0), radius=1))
        self.closed=True
    def quad(self,p):
        return [ [p[2], p[1], p[0]], [p[3],p[2],p[0]] ]
#class Hull(SolidPath):
#    def __init__(self, ):

class RoundedSolid(SolidPath):
    def __init__(self, pos, spheres, **config):
        self.init(config)
        self.pos=pos
        self.spheres=spheres
    def getSolid(self):
        spheres = []
        for r,sl in self.spheres.items():
            for s in sl:
                spheres.append(solid.translate(s+self.pos)(solid.sphere(r=r)))
        return solid.hull()(*spheres)


class RoundedBox(SolidPath):
    def __init__(self,pos, width, height, depth, rad,**config):
        self.init(config)
        if rad<0:
            self.rad=0
        else:
            self.rad=rad
        self.width=width
        self.height=height
        self.depth=depth
        self.pos=pos

    def getSolid(self):
        w=self.width/2-self.rad
        h=self.height/2-self.rad
        d=self.depth/2-self.rad
        return self.rbox([
		V(w,h,d),
		V(w,h,-d),
		V(w,-h,d),
		V(w,-h,-d),
		V(-w,h,d),
		V(-w,h,-d),
		V(-w,-h,d),
		V(-w,-h,-d),
		],self.rad)

    def rbox(self,corners, R):
        spheres = []
        for c in corners:
            spheres.append(solid.translate(c+self.pos)(solid.sphere(r=R)))
        return solid.hull()(*spheres)

class Thread(SolidExtrude):
    def __init__(self, pos, rad, height, pitch, **config):
        global RESOLUTION
        self.init(config)
        self.shape=Path(closed=True)
        for a in range(0,180,5):
            self.shape.add_point(PSharp(rotate(V(rad-pitch/2+pitch/2/180*a,0), a)))
            self.shape.insert_point(0,PSharp(rotate(V(rad-pitch/2+pitch/2/180*a,0), -a)))
        self.pos = pos
        self.closed=True
        self.translate3D(pos)
        self.height=height
        self.twist = -360.0*height/pitch
        pitch=abs(pitch)
        if 'centre' in config:
                self.centre=config['centre']
        else:
                self.centre=False
        if 'convexity' in config:
                self.convexity=config['convexity']
        else:
                self.convexity=10
        self.scale=1
        if 'resolution' in config:
            self.resolution=config['resolution']
        else:
            self.resolution = RESOLUTION
        print (self.shape)
#        screwP.insert_point(0,PSharp(rotate(V(domeRad+-pitch+pitch*math.sqrt(3)/3/180*a,0),-a)))
 #       SolidExtrude(V(0,0), shape=screwP, height=domeRad, twist=360.0*domeRad/pitch))
    def getSolid(self):
        global RESOLUTION
        outline=[]
        points = self.shape.polygonise(self.resolution)
        for p in points:
            outline.append( [round(p[0],PRECISION)*SCALEUP, round(p[1],PRECISION)*SCALEUP ])
        outline.append([round(points[0][0],PRECISION)*SCALEUP, round(points[0][1],PRECISION)*SCALEUP])
        polygon = solid.polygon(outline)
        print("scale="+str(self.scale))
        return self.transform3D(self, solid.linear_extrude(height=self.height, convexity=self.convexity, scale=self.scale,  center=self.centre, twist=self.twist)(polygon))
