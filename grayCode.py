import math

from path import *
from  shapes import *

class Gray(Pathgroup):
    def generateCode(self, bits):
        code = [[0], [1]]
        for i in range(0,bits-1):
            newcode=[]
            for c in code:
                t = copy.deepcopy(c)
                t.insert(0,0)
                newcode.append(t)
                t = copy.deepcopy(c)
                t.insert(0,1)
                newcode.insert(0, t)
            code = newcode
        return code

class GrayStraight(Gray):
    def __init__(self, pos, width, length, bits, **config):
        self.init(config)
        self.transform['translate']=pos
        self.code = self.generateCode(bits)
        bitWidth = float(width)/bits
        bitLength = float(length)/2**bits
        x = 0
        if 'offsets' in config:
            self.offsets = config['offsets']
        else:
            self.offsets = [0] * bits
        for line in self.code:
            p = -width/2
            for bit in line:
                if bit:
                    self.add(Rect(V(x+bitLength/2+self.offsets[bit], p+bitWidth/2), centred=True, width=bitLength, height = bitWidth))
                p+=bitWidth
            x+=bitLength



class GrayArc(Gray):
    def __init__(self, pos, innerRad, outerRad, bits, **config):
        self.init(config)
        self.transform['translate']=pos
        self.code = self.generateCode(bits)
        bitWidth = (outerRad-innerRad)/bits
        bitAngle = 360.0/2**bits
        angle = 0
        if 'offsets' in config:
            self.offsets = config['offsets']
        else:
            self.offsets = [0] * bits
        for line in self.code:
            p = innerRad
            for bit in line:
                if bit:
                    black = Path(closed=True)
                    black.add_point(rotate(V(p,0), angle+self.offsets[bit]))
                    black.add_point(rotate(V(p+bitWidth,0), angle+self.offsets[bit]))
                    black.add_point(PArc(V(0,0), radius=p+bitWidth, direction='cw'))
                    black.add_point(rotate(V(p+bitWidth,0), angle+self.offsets[bit]+bitAngle))
                    black.add_point(rotate(V(p,0), angle+self.offsets[bit]+bitAngle))
                    black.add_point(PArc(V(0,0), radius=p, direction='ccw'))
                    self.add(black)
                p+=bitWidth
            angle+=bitAngle
