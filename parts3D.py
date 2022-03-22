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
        print ("custom render3D")
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
        print ("hello")
        print (extruded)
        return [extruded]

class Sphere(SolidPath):
    def __init__(self, pos, rad, **config):
        self.init(config)
        self.pos=pos
        self.rad=rad
        self.closed=True
        self.add_point(pos,'circle',rad)

    def getSolid(self):
        self.translate3D(self.pos)
        return solid.sphere(r=self.rad)

class Cylinder(SolidPath):
    def __init__(self, pos, rad1, rad2, height, **config):
        self.init(config)
        if 'centre' in config:
            self.centre= config['centre']
        else:
            self.centre= False
        self.pos=pos
        self.rad1=rad1
        self.rad2=rad2
        self.height=height
        self.closed=True
        self.add_point(pos,'circle',rad2)

    def getSolid(self):
        return solid.translate(self.pos)(solid.cylinder(r1=self.rad1, r2=self.rad2, h=self.height, center=self.centre))

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
                    solid.translate([W,H,D])( solid.sphere(r=rad)),
                    solid.translate([-W,H,D])( solid.sphere(r=rad)),
                    solid.translate([-W,-H,D])( solid.sphere(r=rad)),
                    solid.translate([W,-H,D])( solid.sphere(r=rad)),
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
print (Sphere.render3D)

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
        return solid.linear_extrude(height=self.height, convexity=self.convexity, scale=self.scale,  center=self.centre, twist=self.twist)(polygon)




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
        self.add_points(shape.points)
    def getSolid(self):
        global RESOLUTION
        outline=[]
        points = self.shape.polygonise(RESOLUTION)
        for p in points:
            outline.append( [round(p[0],PRECISION)*SCALEUP, round(p[1],PRECISION)*SCALEUP ])
        outline.append([round(points[0][0],PRECISION)*SCALEUP, round(points[0][1],PRECISION)*SCALEUP])
        polygon = solid.polygon(outline)
        return solid.rotate_extrude(convexity=self.convexity)(polygon)

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
        self.add_points(PCircle(pos, radius=smallRad))

    def getSolid(self):
        return solid.rotate_extrude(convexity = self.convexity)(solid.translate([self.bigRad,0,0])(solid.circle(r=self.smallRad)))


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
        self.add_points(shape.points)

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
class SurfacePolyhedron(Polyhedron):
    def __init__(self, vFunc, xmin, xmax, ymin, ymax, floorz, **config):

        self.init(config)
        self.closed=True
        if 'step' in config:
            self.step = config['step']
        else:
            self.step = 1.0
        self.basePoints = []
        self.leftSide = []
        self.rightSide = []
        self.topSide = []
        self.bottomSide = []
        self.faces = []
        self.inPoints = []
        self.first=0
        x = xmin
        while x<xmax:
            p


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
