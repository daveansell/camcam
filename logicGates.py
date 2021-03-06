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


from path import *
from shapes import *
from math import *

class LogicGate(Part):
    def __init__(self,pos, **config):
        self.conn_len=8
        self.conn_wid=7
        self.init(config)
        self.transform['translate']=pos
        self.init2()
        if 'layer_config' in config:
            for l in list(config['layer_config'].keys()):
                if config['layer_config'][l]=='diagram':
                    self.diagram(l,config)
                if config['layer_config'][l]=='holes':
                    self.holes(l,config)
    def init2(self):
        pass
    def diagram(self,layer, config):
        pass
    def holes(self,layer, config):
        pass


class NOTgate(LogicGate):
    def init2(self):
        self.l=14
        self.w1=10
        self.w2=16
        self.h=20
        self.r=3/2
        self.add_bom('NOT gate',1,'Sparkfun NOT LogicBlock','')

    def diagram(self,layer,config):
        l=self.l
        w1=self.w1
        w2=self.w2
        h=self.h
        r=self.r
        l1=l*math.sqrt(3)/2
        l2=l-l1

        tri=Path(closed=True, side='out')
        tri.add_point(V(-l2,-l/2))
        tri.add_point(V(-l2,l/2))
        tri.add_point(V(l1,0))
        self.add(tri,layer)

        self.add(Circle(V(l1+r,0),rad=r))

        outline=Path(closed=True, side='out')
        outline.add_point(V(-h/2,-w2/2))
        outline.add_point(V(-h/2,w2/2))
        outline.add_point(V(h/2,w1/2))
        outline.add_point(V(h/2,-w1/2))
        self.add(outline, layer)

    def holes(self,layer,config):
        l=self.l
        w1=self.w1
        w2=self.w2
        h=self.h
        self.add(Hole(V(-h/2-self.conn_len,0),3.3/2),layer)
        self.add(Hole(V(h/2+self.conn_len,0),3.3/2),layer)


class ANDgate(LogicGate):
    def init2(self):
        self.l=5
        self.w=27
        self.h=20
        self.s=5
        self.add_bom('AND gate',1,'Sparkfun AND LogicBlock','')
    def diagram(self,layer,config):
        l=self.l
        w=self.w
        h=self.h
        s=self.s

        symbol=Path(closed=True, side='out')
        symbol.add_point(V(-l,-l))
        symbol.add_point(V(-l,l))
        symbol.add_point(V(l,l), 'incurve', radius=l-0.1)
        symbol.add_point(V(l,-l), 'incurve', radius=l-0.1)

        self.add(symbol,layer)
        outline=Path(closed=True, side='out')
        outline.add_point(V(-h/2,w/2))
        outline.add_point(V(-h/2,-w/2))
        outline.add_point(V(-h/2+s,-w/2))
        outline.add_point(V(h/2,-s))
        outline.add_point(V(h/2,s))
        outline.add_point(V(-h/2+s,w/2))
        self.add(outline,layer)
    def holes(self,layer,config):
        l=self.l
        w=self.w
        h=self.h
        s=self.s
        self.add(Hole(V(-h/2+self.conn_wid/2, w/2+self.conn_len),3.3/2),layer)
        self.add(Hole(V(-h/2+self.conn_wid/2, -w/2-self.conn_len),3.3/2),layer)
        self.add(Hole(V(h/2+self.conn_len, 0),3.3/2),layer)


class ORgate(LogicGate):
    def init2(self):
        self.l=5
        self.w=27
        self.h=20
        self.s=5
        self.add_bom('OR gate',1,'Sparkfun OR LogicBlock','')
    def diagram(self,layer,config):
        self.diagram2(layer,config)

    def diagram2(self,layer,config):
        l=self.l
        w=self.w
        h=self.h
        s=self.s

        symbol=Path(closed=True, side='out')
        symbol.add_point(V(-l,-l))
        symbol.add_point(V(-0.7*l,0), 'incurve', radius=l*1.8-0.1)
        symbol.add_point(V(-l,l))
        symbol.add_point(V(0,l), 'incurve', radius=l*1.3)
        symbol.add_point(V(l,0))
        symbol.add_point(V(0,-l), 'incurve', radius=l*1.3)

        self.add(symbol,layer)
        outline=Path(closed=True, side='out')
        outline.add_point(V(-h/2,w/2))
        outline.add_point(V(-h/2,-w/2))
        outline.add_point(V(-h/2+s,-w/2))
        outline.add_point(V(h/2,-s))
        outline.add_point(V(h/2,s))
        outline.add_point(V(-h/2+s,w/2))
        self.add(outline,layer)

    def holes(self,layer,config):
        l=self.l
        w=self.w
        h=self.h
        s=self.s
        self.add(Hole(V(-h/2+self.conn_wid/2, w/2+self.conn_len), rad=3.3/2),layer)
        self.add(Hole(V(-h/2+self.conn_wid/2, -w/2-self.conn_len),3.3/2),layer)
        self.add(Hole(V(h/2+self.conn_len, 0),3.3/2),layer)

class XORgate(ORgate):
    def init2(self):
        self.l=5
        self.w=27
        self.h=20
        self.s=5
        self.add_bom('XOR gate',1,'Sparkfun XOR LogicBlock','Will have to be made from an OR gate and changing the gate')
    def diagram(self,layer,config):
        l=self.l
        w=self.w
        h=self.h
        s=self.s
        self.diagram2(layer,config)

        symbol=Path(closed=False, side='on')
        symbol.add_point(V(-l*1.2,-l))
        symbol.add_point(V(-0.9*l,0), 'incurve', radius=l*1.7)
        symbol.add_point(V(-l*1.2,l))
        self.add(symbol,layer)
