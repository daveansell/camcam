from path import *
from cc3d import *
class Sphere(Path):
    def __init__(self, pos, rad, **config):

        self.init(config)
        self.pos=pos
        self.rad=rad

    def render3D(self, pconfig, border=False):
        self.translate3D(self.pos)
        extruded = solid.sphere(r=self.rad)
        print (self.transform)
        print( self.transform3D(self, extruded))
        return self.transform3D(self, extruded)

