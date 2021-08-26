import solid
from  path import *

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
    def getSolid(self):
        self.translate3D(self.pos)
        return solid.sphere(r=self.rad)
print (Sphere.render3D)
