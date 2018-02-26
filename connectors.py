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
class Dconnector(Part):
        def __init__(self, pos, **config):
                self.init(config)
                self.translate(pos)
                data={
                        9:{'A':20.5, 'B':10.25, 'C':25, 'D':12.5},
                        15:{'A':28.8, 'B':14.4, 'C':33.3, 'D':16.65},
                        25:{'A':42.5, 'B':21.25, 'C':47, 'D':23.5},
                        37:{'A':59.1, 'B':29.55, 'C':63.5, 'D':31.75},
                }
                hole_rad=3.3/2
                top=5.9
                h=11.4
                r=4
                ex=0.4
                dw=h*math.tan(10/180*math.pi)
                self.init(config)
                if 'pins' in config:
                        if config['pins'] in [9,15,25,37]:
                                pins=config['pins']
                        else:
                                print "D connectors should have 9,15,25, or 37 pins not "+str(config['pins'])
                else:
                        pins=9
                cutout = self.add(Path(side='in', closed=True))
                d=data[pins]
                cutout.add_point(V(-d['B']-ex,top),'incurve',r)
                cutout.add_point(V(d['B']+ex,top),'incurve',r)
                cutout.add_point(V(d['B']+ex-dw,top-h),'incurve',r)
                cutout.add_point(V(-d['B']-ex+dw,top-h),'incurve',r)
                self.add(Hole(V(d['D'],0),hole_rad))
                self.add(Hole(V(-d['D'],0),hole_rad))
                self.add_bom('D connector -'+str(config['pins'])+' pin',1,'D-'+str(config['pins']))
class XLR(Part):
        def __init__(self, pos, **config):
                self.init(config)
                self.translate(pos)
                data={
                        'male':{'h':V(0,27/2), 'r':20/2},
                        'female':{'h':V((26.3-9.6)/2, -25.6/2), 'r':24/2},
                        'female5way':{'h':V(-19/2, 24/2), 'r':24/2},
                }
                if 'type' in config:
                        d=data[config['type']]
                        self.add(Hole(V(0,0), d['r']))
                        self.add(Hole(d['h'],3.3/2))
                        self.add(Hole(-d['h'],3.3/2))
                self.add_bom('XLR-'+str(config['type']),1,'XLR-'+str(config['type']))
                #position, type="male/female"
