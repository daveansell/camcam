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

class Switch(Part):
        def __init__(self,pos, **config):
                self.init(config)
                self.transform['translate']=pos
                if 'layer_config' not in config or type(config['layer_config']) is not dict:
                        config['layer_config']={'base':'clearance', 'perspex':'doubleflat'}
                if 'switch_type' not in config:
                        config['switch_type'] = 'IWS_small'
                if config['switch_type'] == 'IWS_small':
                        self.add_bom('IWS small switch', 1, part_number='59-112', description='Red Round Ip67 Mom Switch Solder Term')
                if config['switch_type'] == 'IWS_small_LED':
                        self.add_bom('IWS small switch LED', 1, part_number='59-411R', description='Red Round Ip67 Mom Switch Solder Term red LED')
                
                if config['switch_type'] == 'IWS_small' or  config['switch_type'] == 'IWS_small_LED':
                        if not 'paper' in config['layer_config'].keys():
                                        config['layer_config']['paper']='doubleflat'
                        for l in config['layer_config'].keys():
                                task =  config['layer_config'][l]
                                if task=='clearance':
                                        self.add(Hole(V(0,0), rad=23/2), layers=l)
                                if task=='doubleflat':
                                        self.add(CircleChord(V(0,0), 13.6/2, 12.9, side='in'), layers=l)
#					self.add(DoubleFlat(V(0,0),13.6/2, 12.9/2, side='in'), layers=l)
                                if task=='minimal':
                                        self.add(Hole(V(0,0), rad=18/2, z1=-2 ), layers=l)
                                        self.add(Hole(V(0,0), rad=14/2 ), layers=l)
                                if task=='counterbore':
                                        self.add(Hole(V(0,0), rad=12/2, z1=-config['counterbore_depth']), layers=l)
                                        self.add(Hole(V(0,0), rad=16/2, z1=-config['counterbore_depth']), layers=l)
                                        self.add(Hole(V(0,0), rad=19/2, z1=-config['counterbore_depth']), layers=l)
                                        self.add(Hole(V(0,0), rad=21/2, z1=-config['counterbore_depth']), layers=l)
                                        self.add(Hole(V(0,0), rad=23/2, z1=-config['counterbore_depth']), layers=l)
                                        self.add(CircleChord(V(0,0), 13.6/2, 12.9, side='in'), layers=l)

                if config['switch_type']== 'rocker':
                        rocker_data={
                                'PRFDA1-16F-BB0BW':{'cutout_width':22, 'cutout_height':30.2, 'clearance_width':26, 'clearance_height':32.5},
                                'MC37920-001-1101':{'cutout_width':22.5, 'cutout_height':30.1, 'clearance_width':26, 'clearance_height':33},
                        }
                        if 'sub_type' not in config:
                                config['sub_type']='PRFDA1-16F-BB0BW'
                        data=rocker_data[config['sub_type']]
                        self.add_bom('rocker switch',1,part_number=config['sub_type'])
                        for l in config['layer_config'].keys():
                                task =  config['layer_config'][l]
                                if task=='cutout':
                                        self.add(ClearRect(V(0,0), width=data['cutout_width'], height=data['cutout_height'], centred=True),layers=l)
                                if task=='clearance':
                                        self.add(ClearRect(V(0,0), width=data['clearance_width'], height=data['clearance_height'], centred=True),layers=l)

class SevenSegmentDisplay(Part):
        def __init__(self, pos, **config):
                self.init(config)
                self.transform['translate']=pos
                data={
                        'HDSP-C1E3':{'width':24,'height':34, 'depth':10.5, 'pcb_width':55, 'pcb_height':60, 'pcb_xoff':13.5},
                        'HDSP-C1E3x2':{'width':48,'height':34, 'depth':10.5, 'pcb_width':55, 'pcb_height':60,'pcb_xoff':1.5},
                        'HDSP-C2E3':{'width':24,'height':34, 'depth':10.5, 'pcb_width':50, 'pcb_height':40,'pcb_xoff':0},
                }
                if 'part' in config and config['part'] in data and 'layer_config' in config:
                        d=data[config['part']]
                        for l in config['layer_config']:
                                task =  config['layer_config'][l]
                                if task=='cutout':
                                        self.add(Rect(V(0,0), width=d['width']+1, height=d['height']+1, centred=True),layers=l)
                                if task=='pcb':
                                        self.add(Rect(V(-d['pcb_xoff'],0), width=d['pcb_width']+1, height=d['pcb_height']+1, centred=True),layers=l)
                
class Knob(Part):
        def __init__(self,pos, **config):
                self.init(config)
                self.translate(pos)
                if 'layer_config' not in config or type(config['layer_config']) is not dict:
                        config['layer_config']={'base':'stepper_mount', 'perspex':'shaft'}
                if 'knob_type' not in config:
                        config['knob_type'] = 'stepper'

                if config['knob_type'] == 'stepper':
                        for l in config['layer_config'].keys():
                                task =  config['layer_config'][l]
                                if task=='stepper_mount':
                                        stepper = self.add(Stepper(V(0,0), 'NEMA1.7', mode='stepper', layer=l, length=43))
                                if task=='shaft':
                                        stepper = self.add(Stepper(V(0,0), 'NEMA1.7', mode='justshaft', layer=l, length=43))
                self.magnetometer_holder = self.add(Part(layer='_magnetometer_holder', name='_magnetometer_holder', border=RoundedRect(V(0,0), centred=True, width=stepper.d['width'], height=stepper.d['width'], rad=stepper.d['corner_rad']), cutter='2mm_endmill')) 
        #	bolt_spacing = 11
                bolt_spacing = 8.3
                bolt_y = 7.3-3.3/2
                solder_y = -8
                solder_width = 2.54*5
                self.magnetometer_holder.add(Hole(V(0,0), rad=8/2))
                self.magnetometer_holder.add(Hole(V(bolt_spacing/2, bolt_y), rad=2.5/2))
                self.magnetometer_holder.add(Hole(V(-bolt_spacing/2, bolt_y), rad=2.5/2))
#		self.magnetometer_holder.add(RoundedRect(V(0, solder_y), centred=True, width = solder_width, height=3, z1=-2))
                self.magnetometer_holder.add(FourObjects(V(0, 0), Hole(V(0,0), rad=3.3/2), centred=True, width=stepper.d['bolt_sep'], height=stepper.d['bolt_sep'], layers=['_magnetometer_holder']))
                self.magnetometer_holder.add(RoundedRect(V(0, solder_y), centred=True, width = solder_width, height=3.1, z1=-2, side='in', cutter='2mm_endmill'))
        def _pre_render(self, config):
                self.get_plane().add_layer('_magnetometer_holder', 'pvc', 6, colour='#80808080', zoffset=49)

class TightHole(Pathgroup):
        def __init__(self, pos, rad, **config):
                self.init(config)
                self.pos=pos
                self.rad = rad
                self.materials={
                        'plywood':0.97,
                        'delrin':0.98,
                        'pvc':0.99,
                        'perspex':0.99,
                }
        def _pre_render(self, config):
                self.add(Hole(self.pos, self.rad*self.materials[config['material']]))

class Dowel(Part):
        def __init__(self, pos, rad, dowel_type, layers, **config):
                self.init(config)
                offsets={
                        'steel':{'loose':1.05, 'tight':1.05},
                        'wood_ribbed':{'loose':1.05, 'tight':1.0},
                        'wood':{'loose':1.05, 'tight':1.0},
                }
                self.pos=pos
                self.layers=layers
                self.dowel_type = dowel_type
                self.rad = rad
                self.tightrad = rad*offsets[dowel_type]['tight']
                self.looserad = rad*offsets[dowel_type]['loose']
                if 'tight' in layers:
                        self.add(TightHole(self.pos, rad=self.tightrad), layers['tight'])
                if 'loose' in layers:
                        self.add(Hole(self.pos, rad=self.looserad), layers['loose'])
                        self.add(Hole(self.pos, rad=self.looserad), layers['loose'])


class Post(Part):
        def __init__(self, pos, **config):
                self.init(config)
                if 'spacing' in config:
                        spacing=config['spacing']
                else:
                        spacing=20

                if 'orientation' in config and config['orientation']=='x':
                        s=V(0,spacing/2)
                else:
                        s=V(spacing/2,0)
                if 'height' in config:
                        height=config['height']
                else:
                        height=75
                self.add_bom('wooden post 2x1"x'+str(height)+'mm',1,description='Wooden post for standing module on a table')
                self.add(Hole(pos+s, rad=5/2),'base')
                self.add(Hole(pos-s, rad=5/2), 'base')

class Bracket(Pathgroup):
        def __init__(self, pos, bracket_type, side, **config):
                self.init(config)
                self.translate(pos)
                dat = {
                        'bpc60x40':{
                                'holerad':3.3/2,
                                'holes':{
                                                'on':[V(25.0, 27.5), V(12.5,41.0), V(25,53.5), V( 0.0,53.5), V(-25.0,53.5), V(-12.5, 41.0), V(-25.0, 27.5)],
                                                'off':[V(12.5, 17.5), V(25,34), V(0,34), V(-25,34), V(-12.5,17.5)],
                                },
                        },
                        
                }
                if bracket_type in dat:
                        d=dat[bracket_type]
                        if side in d['holes']:
                                for p in d['holes'][side]:
                                        self.add(Hole(p, rad=d['holerad']))
                

class Barn(Part):
        def __init__(self, pos, width, height,**config):
                self.init(config)
                self.translate(pos)
                if('rad' in config):
                        rad = config['rad']
                else:
                        rad = 15
                if('insert_layer' in config):
                        insert_layer = config['insert_layer']
                else:
                        insert_layer = 'base'
                if('depth' in config):
                        depth = config['depth']
                else:
                        depth = 30
                if('name' in config):
                        self.name = config['name']
                if('layer' in config):
                        self.layer = config['layer']

                self.translate(pos)
                self.add_border(RoundedRect(V(0,0), width=width, height=height, centred=True, rad=rad))
                self.add(Bolt(V((width/2-rad),(height/2-rad)), insert_layer=insert_layer, clearance_layers=self.layer))
                self.add(Bolt(V(-(width/2-rad),(height/2-rad)), insert_layer=insert_layer, clearance_layers=self.layer))
                self.add(Bolt(V(-(width/2-rad),-(height/2-rad)), insert_layer=insert_layer, clearance_layers=self.layer))
                self.add(Bolt(V((width/2-rad),-(height/2-rad)), insert_layer=insert_layer, clearance_layers=self.layer))
                self.add_bom('standoff'+str(depth),4, description=str(depth)+'mm standoff')
                

class PiBarn(Part):
        def __init__(self, pos, **config):
                if('layer' not in config):
                        config['layer']='pibarn'
                self.init(config)
                if 'x_units' in config:
                        x_units=config['x_units']
                else:
                        x_units=4
                if 'y_units' in config:
                        y_units=config['y_units']
                else:
                        y_units=4
                if 'every_other' in config and config['every_other']:
                        spacing=50
                        x_units/=2
                        y_units/=2
                else:
                        spacing=25
                if 'name' in config:
                        self.name = config['name']
                else:
                        self.name = 'PiBarn'
                if('depth' in config):
                        depth = config['depth']
                else:
                        depth = 30
                self.depth=depth
                if('insert_layer' in config):
                        insert_layer = config['insert_layer']
                else:
                        insert_layer = 'base'
                bolt_conf={'clearance_layers':[config['layer']], 'length':50, 'insert_layer':[], 'underinsert_layer':insert_layer}

                self.add(RepeatLine(pos+V(-float(x_units)/2*spacing, -float(y_units)/2*spacing), pos+V(float(x_units)/2*spacing, -float(y_units)/2*spacing), x_units+1, Bolt, bolt_conf)).paths
                self.add(RepeatLine(pos+V(float(x_units)/2*spacing, (-float(y_units)/2+1)*spacing), pos+V(float(x_units)/2*spacing, (float(y_units)/2-1)*spacing), y_units-1, Bolt, bolt_conf))
                self.add(RepeatLine(pos+V(float(x_units)/2*spacing, float(y_units)/2*spacing), pos+V(-float(x_units)/2*spacing, float(y_units)/2*spacing), x_units+1, Bolt, bolt_conf))
                self.add(RepeatLine(pos+V(-float(x_units)/2*spacing, (float(y_units)/2-1)*spacing), pos+V(-float(x_units)/2*spacing, (-float(y_units)/2+1)*spacing), y_units-1, Bolt, bolt_conf))
                self.add_border(RoundedRect(pos, centred=True, width=x_units*spacing+15, height=y_units*spacing+15, side='out', rad=8))
                self.add_bom('standoff'+str(depth),4, description=str(depth)+'mm standoff')
                self.zoffset=depth+6
        def _pre_render(self,config):
                self.get_plane().add_layer('pibarn', 'perspex', 6, colour='#80808080')


class Pi(Part):
        def __init__(self, pos,**config):
                self.init(config)
                h=85
                w=56
                hw=49
                hl=58
                self.translate(pos)
                if 'layer_config' in config:
                        layer_config = config['layer_config']
                else:
                        layer_config = {'paper':'paper', 'clearance':'base'}
                self.add(RoundedRect(V(0,0), centred=True, width=w, height=h, rad=3),'paper')
                hole_bl=V(-w/2+3.5, -h/2+3.5)
                if 'insert' in layer_config.keys():
                        self.add(Insert(hole_bl,'M3', layer_config['insert']))
                        self.add(Insert(hole_bl+V(hw,0),'M3', layer_config['insert']))
                        self.add(Insert(hole_bl+V(hw, hl),'M3', layer_config['insert']))
                        self.add(Insert(hole_bl+V(0,hl),'M3', layer_config['insert']))
                if 'clearance' in layer_config.keys():
                        self.add(Hole(hole_bl,rad=3.3/2), layer_config['clearance'])
                        self.add(Hole(hole_bl+V(hw,0),rad=3.3/2), layer_config['clearance'])
                        self.add(Hole(hole_bl+V(hw, hl),rad=3.3/2), layer_config['clearance'])
                        self.add(Hole(hole_bl+V(0,hl),rad=3.3/2), layer_config['clearance'])

class Pi3(Part):
        def __init__(self, pos,**config):
                self.init(config)
                w=85
                h=56
                o=1.5
                self.layer='_pilayer'
                self.name='Pi3'
                self.translate(pos)
#		self.zoffset+=o
                self.no_mirror = True
                self.add_border(RoundedRect(V(0,0), width=w, height=h, centred=True, rad=3, thickness=1.5,  colour="#008030"))
                self.hdmi = self.add(Part(subpart=True, layer='_pilayer', border=Rect(V(-w/2+32, -h/2+6.1-2), centred=True, width=14, height=12.2, zoffset=6, thickness=6, colour='#808080')))	
                self.network = self.add(Part(subpart=True, layer='_pilayer', border=Rect(V(w/2-8.55, -h/2+10.25), centred=True, width=21.1, height=15.5, zoffset=13.6, thickness=13.6, colour='#808080'))	)
                self.USB1 = self.add(Part(subpart=True, layer='_pilayer', border=Rect(V(w/2-6.65, -h/2+29), centred=True, width=17.7, height=13.3, zoffset=15.0, thickness=15.0, colour='#808080')))	
                self.USB2 = self.add(Part(subpart=True, layer='_pilayer', border=Rect(V(w/2-6.65, -h/2+47), centred=True, width=17.7, height=13.3, zoffset=15.0, thickness=15.0, colour='#808080')))	
                self.GPIO = self.add(Part(subpart=True, layer='_pilayer', border=Rect(V(-w/2+29+3.5, 49/2), centred=True, width=50.5, height=5, zoffset=5, thickness=5, colour='#101010')))
                self.CPU = self.add(Part(subpart=True, layer='_pilayer', border=Rect(V(-15.6, -h/2+30.3), centred=True, width=13.8, height=13.8, zoffset=1, thickness=1, colour='#101010')))
                self.CSI = self.add(Part(subpart=True, layer='_pilayer', border=Rect(V(-2.6, -h/2+11.5), centred=True, width=4, height=22.2, zoffset=4, thickness=4, colour='#dddddd')))
                self.DSI = self.add(Part(subpart=True, layer='_pilayer', border=Rect(V(-39, -h/2+28), centred=True, width=4, height=22.2, zoffset=4, thickness=4, colour='#dddddd')))
                if 'clearance_layers' in config:
                        if type(config['clearance_layers']) is list:
                                config['clearance_layers'].append('_pilayer')
                        else:
                                config['clearance_layers']=[config['clearance_layers'], '_pilayer']
                else:
                        config['clearance_layers']='_pilayer'
                if 'thread_layer' not in config:
                        config['thread_layer'] = []
                if 'insert_layer' not in config:
                        config['insert_layer'] = []
#		self.add(Hole(V(0,0), rad=3))
                self.add(Bolt(V(-w/2+3.5, 49/2), 'M2.5', clearance_layers=config['clearance_layers'], insert_layer=config['insert_layer'], thread_layer=config['thread_layer']))
                self.add(Bolt(V(-w/2+3.5, -49/2), 'M2.5', clearance_layers=config['clearance_layers'], insert_layer=config['insert_layer'], thread_layer=config['thread_layer']))
                self.add(Bolt(V(-w/2+3.5+58, 49/2), 'M2.5', clearance_layers=config['clearance_layers'], insert_layer=config['insert_layer'], thread_layer=config['thread_layer']))
                self.add(Bolt(V(-w/2+3.5+58, -49/2), 'M2.5', clearance_layers=config['clearance_layers'], insert_layer=config['insert_layer'], thread_layer=config['thread_layer']))
        def _pre_render(self,config):
                self.get_plane().add_layer('_pilayer', 'pcb', 1, zoffset=0, colour='#808080')

class PiCompute(Part):
        def __init__(self, pos, **config):
                self.init(config)
                w=67
                h=28
                self.zoffset=4
                self.no_mirror = True
                if 'clearance_layers' in config:
                        if type(config['clearance_layers']) is list:
                                config['clearance_layers'].append('_piclayer')
                        else:
                                config['clearance_layers']=[config['clearance_layers'], '_piclayer']
                else:
                        config['clearance_layers']='_piclayer'
                if 'thread_layer' not in config:
                        config['thread_layer'] = []
                if 'insert_layer' not in config:
                        config['insert_layer'] = []
                self.layer = '_piclayer'
                self.add_border(RoundedRect(V(0,h/2), width=w, height=h, centred=True, rad=0, thickness=1.5,  colour="#008030"))	
                self.CPU = self.add(Part(subpart=True, layer='_piclayer', border=Rect(V(-w/2+44, -h/2+22), centred=True, width=13.8, height=13.8, zoffset=1, thickness=1, colour='#101010')))
                self.MEM = self.add(Part(subpart=True, layer='_piclayer', border=Rect(V(-w/2+18, -h/2+22), centred=True, width=13.8, height=13.8, zoffset=1, thickness=1, colour='#101010')))
        def _pre_render(self,config):
                self.get_plane().add_layer('_piclayer', 'pcb', 1, zoffset=0, colour='#808080')
class PiComputeIO(Part):
        def __init__(self, pos, **config):
                self.init(config)
                w=105
                h=85
                hsy=77
                hsx=92	

                o=1.5
                self.layer='_piciolayer'
                self.name='PiComputeIO'
                self.translate(pos)
#		self.zoffset+=o
                self.no_mirror = True
        
                if 'clearance_layers' in config:
                        if type(config['clearance_layers']) is list:
                                config['clearance_layers'].append('_piciolayer')
                        else:
                                config['clearance_layers']=[config['clearance_layers'], '_piciolayer']
                else:
                        config['clearance_layers']='_piciolayer'
                if 'thread_layer' not in config:
                        config['thread_layer'] = []
                if 'insert_layer' not in config:
                        config['insert_layer'] = []
                self.add_border(RoundedRect(V(0,0), width=w, height=h, centred=True, rad=3, thickness=1.5,  colour="#008030"))
                self.hdmi = self.add(Part(subpart=True, layer='_piciolayer', border=Rect(V(0, -h/2+6.1-2), centred=True, width=14, height=12.2, zoffset=6, thickness=6, colour='#808080')))
                self.add(Bolt(V(-hsx/2, -hsy/2), 'M3', clearance_layers=config['clearance_layers'], thread_layer=config['thread_layer'], insert_layer=config['insert_layer']))	
                self.add(Bolt(V(hsx/2, -hsy/2), 'M3', clearance_layers=config['clearance_layers'], thread_layer=config['thread_layer'], insert_layer=config['insert_layer']))	
                self.add(Bolt(V(hsx/2, hsy/2), 'M3', clearance_layers=config['clearance_layers'], thread_layer=config['thread_layer'], insert_layer=config['insert_layer']))	
                self.add(Bolt(V(-hsx/2, hsy/2), 'M3', clearance_layers=config['clearance_layers'], thread_layer=config['thread_layer'], insert_layer=config['insert_layer']))
#               self.add(Hole(V(0,0), rad=3))
                self.USB1 = self.add(Part(subpart=True, layer='_piciolayer', border=Rect(V(w/2-6.65, -h/2+29), centred=True, width=17.7, height=13.3, zoffset=7.0, thickness=7.0, colour='#808080')))	
                self.USBSL = self.add(Part(subpart=True, layer='_piciolayer', border=Rect(V(w/2-2, -h/2+14), centred=True, width=5, height=7, zoffset=3.0, thickness=3.0, colour='#808080')))
                self.USBPOW = self.add(Part(subpart=True, layer='_piciolayer', border=Rect(V(w/2-2, h/2-12), centred=True, width=5, height=7, zoffset=3.0, thickness=3.0, colour='#808080')))
                self.GPIO = self.add(Part(subpart=True, layer='_piciolayer', border=Rect(V(-3.5, h/2-5.5), centred=True, width=76, height=5, zoffset=5, thickness=5, colour='#101010')))
                self.GPIO2 = self.add(Part(subpart=True, layer='_piciolayer', border=Rect(V(-3.5, h/2-18), centred=True, width=76, height=5, zoffset=5, thickness=5, colour='#101010')))
                self.DSI = self.add(Part(subpart=True, layer='_piciolayer', border=Rect(V(-w/2+35, -h/2+2.5), centred=True, width=16, height=3, zoffset=2, thickness=2, colour='#dddddd')))
                self.DSI = self.add(Part(subpart=True, layer='_piciolayer', border=Rect(V(-w/2+17, -h/2+2.5), centred=True, width=16, height=3, zoffset=2, thickness=2, colour='#dddddd')))
                self.DSI = self.add(Part(subpart=True, layer='_piciolayer', border=Rect(V( w/2-35, -h/2+2.5), centred=True, width=16, height=3, zoffset=2, thickness=2, colour='#dddddd')))
                self.DSI = self.add(Part(subpart=True, layer='_piciolayer', border=Rect(V( w/2-17, -h/2+2.5), centred=True, width=16, height=3, zoffset=2, thickness=2, colour='#dddddd')))
                self.add(PiCompute(V(46-w/2, 20-w/2), clearance_layers='_piciolayer'))	
        def _pre_render(self, config):
                self.get_plane().add_layer('_piciolayer', 'pcb', 1, zoffset=0, colour='#808080')



class ArduinoUno(Part):
        def __init__(self, pos,**config):
                self.init(config)
                w=68
                h=53.3
                t=1.5
                fe=2.5
                self.layer='_ardlayer'
                self.name='ArduinoUno'
                self.translate(pos)
                self.no_mirror=True

                border=Path(closed=True, side='out', thickness=t,  colour="#001080")
                border.add_point(V(-w/2, h/2))
                border.add_point(V(-w/2, -h/2))
                border.add_point(V(w/2-fe, -h/2))
                border.add_point(V(w/2-fe, -h/2+2))
                border.add_point(V(w/2, -h/2+5))
                border.add_point(V(w/2, -h/2+37))
                border.add_point(V(w/2-fe, -h/2+40))
                border.add_point(V(w/2-fe, +h/2))
                self.add_border(border)
                if 'mode' in config and config['mode']=='shield':
                        self.zoffset=12
                        self.pins1 = self.add(Part(subpart=True, layer='_ardlayer', border=Rect(V(w/2-fe-1-10, -h/2+50.5), centred=True, width=20, height=2.5, zoffset=-t, thickness=2, colour='#202020')))
                        self.pins2 = self.add(Part(subpart=True, layer='_ardlayer', border=Rect(V(w/2-fe-1-10-22.5, -h/2+50.5), centred=True, width=20, height=2.5, zoffset=-t, thickness=2, colour='#202020')))
                        self.pinsA = self.add(Part(subpart=True, layer='_ardlayer', border=Rect(V(w/2-fe-1-7.5, h/2-50.5), centred=True, width=15, height=2.5, zoffset=-t, thickness=2, colour='#202020')))
                        self.pinsP = self.add(Part(subpart=True, layer='_ardlayer', border=Rect(V(w/2-fe-1-25, h/2-50.5), centred=True, width=15, height=2.5, zoffset=-t, thickness=2, colour='#202020')))

                else:
                        self.USB = self.add(Part(subpart=True, layer='_ardlayer', border=Rect(V(-w/2-6.2+9, h/2-9.6-6), centred=True, width=18, height=12, zoffset=10.9, thickness=10.9, colour='#808080')))
                        self.USB = self.add(Part(subpart=True, layer='_ardlayer', border=Rect(V(-w/2+5-1.8, -h/2+3.3+4.5), centred=True, width=10, height=9, zoffset=10, thickness=10, colour='#202020')))
                        self.pins1 = self.add(Part(subpart=True, layer='_ardlayer', border=Rect(V(w/2-fe-1-10, -h/2+50.5), centred=True, width=20, height=2.5, zoffset=8, thickness=10, colour='#202020')))
                        self.pins2 = self.add(Part(subpart=True, layer='_ardlayer', border=Rect(V(w/2-fe-1-10-22.5, -h/2+50.5), centred=True, width=20, height=2.5, zoffset=8, thickness=10, colour='#202020')))
                        self.pinsA = self.add(Part(subpart=True, layer='_ardlayer', border=Rect(V(w/2-fe-1-7.5, h/2-50.5), centred=True, width=15, height=2.5, zoffset=8, thickness=10, colour='#202020')))
                        self.pinsP = self.add(Part(subpart=True, layer='_ardlayer', border=Rect(V(w/2-fe-1-25, h/2-50.5), centred=True, width=15, height=2.5, zoffset=8, thickness=10, colour='#202020')))

                if 'clearance_layers' in config:
                        if type(config['clearance_layers']) is list:
                                config['clearance_layers'].append('_ardlayer')
                        else:
                                config['clearance_layers']=[config['clearance_layers'], '_ardlayer']
                else:
                        config['clearance_layers']='_ardlayer'
                print "CLEARA"+str( config['clearance_layers'])
                if 'thread_layer' not in config:
                        config['thread_layer'] = []
                if 'insert_layer' not in config:
                        config['insert_layer'] = []
#               self.add(Hole(V(0,0), rad=3))
		if 'pocket_layer' in config:
                        pocket_layer = config['pocket_layer']
                else:
                        pocket_layer = []
                if 'pocket_depth' in config:
                        pocket_depth = config['pocket_depth']
                else:
                        pocket_depth = 0

		print "pocket_layer="+str(pocket_layer)+" pocket_depth="+str(pocket_depth)
                self.add(FilledRect(V(0,0), centred=True, width=w, height = h, z1=-pocket_depth), pocket_layer)
		self.add(Hole(V(0,0), rad=10), pocket_layer)

                self.add(Bolt(V(-w/2+14, -h/2+2.5), 'M3', clearance_layers=config['clearance_layers'], insert_layer=config['insert_layer'], thread_layer=config['thread_layer']))
                self.add(Bolt(V(w/2-fe, -h/2+7.6), 'M3', clearance_layers=config['clearance_layers'], insert_layer=config['insert_layer'], thread_layer=config['thread_layer']))
                self.add(Bolt(V(w/2-fe, -h/2+35.5), 'M3', clearance_layers=config['clearance_layers'], insert_layer=config['insert_layer'], thread_layer=config['thread_layer']))
                self.add(Bolt(V(-w/2+14+1.3, -h/2+50.7), 'M3', clearance_layers=config['clearance_layers'], insert_layer=config['insert_layer'], thread_layer=config['thread_layer']))
        def _pre_render(self,config):
                self.get_plane().add_layer('_ardlayer', 'pcb', 1, zoffset=0, colour='#808080')

class WashingBowl(Part):
        def __init__(self, pos, bowl_type, **config):
                self.init(config)
                self.translate(pos)
                bowl_layers=['_washing_bowl', '_washing_bowl_support']
                if 'clearance_layers' in config:
                        clearance_layers=config['clearance_layers']
                else:
                        clearance_layers=['perspex', 'paper']
                if 'insert_layer' in config:
                        insert_layer=config['iinsert_layer']
                        if type(insert_layer) is not list:
                                insert_layer = [insert_layer]
                else:
                        insert_layer = ['base']
                if 'thread_layer' in config:
                        thread_layer=config['ithread_layer']
                        if type(thread_layer) is not list:
                                thread_layer = [thread_layer]
                else:
                        thread_layer = []


                data = {
                        'bline-27cm':{'outer_rad':270.0/2, 'top_outer_rad':260.0/2, 'bottom_rad':205.0/2, 'depth':90.0, 'lip_depth':8.0, 'top_rad':233.0/2, 'num_bolts':8, 'wall':1}
                }
                if bowl_type in data:
                        self.d=data[bowl_type]
                self.bowl = self.add(Part(subpart=True, layer='_washing_bowl', zoffset = 0, border = Circle(V(0,0), rad = self.d['top_rad'],)))# extrude_scale = self.d['bottom_rad']/self.d['top_rad'])))
                self.layer = '_washing_bowl'
                self.name = '_washing_bowl'
                self.zoffset = self.d['lip_depth']
                self.add_border( Circle(V(0,0), rad=self.d['top_outer_rad'],thickness = self.d['lip_depth']))#  extrude_scale = self.d['outer_rad']/self.d['top_outer_rad']))
                self.add(Hole(V(0,0), self.d['top_rad']-self.d['wall']))
                self.bowl.add(Circle(V(0,0), rad=self.d['top_rad']-self.d['wall'], z1=-self.d['lip_depth']-self.d['depth']+self.d['wall'], side='in',))#  extrude_scale = (self.d['top_rad']-self.d['wall'])/(self.d['bottom_rad']-self.d['wall']), extrude_centre=V(0,0)))
                self.add(Hole(V(0,0), rad=self.d['top_rad']+1), clearance_layers + insert_layer)
#		self.add(Hole(V(0,0), rad=self.d['top_rad']+1, thickness=None), 'base')
                for i in range(0, int(self.d['num_bolts'])):
                        t = self.add(Bolt(V(0, (self.d['top_outer_rad']+self.d['top_rad'])/2), 'M4', clearance_layers = clearance_layers+bowl_layers, insert_layer=insert_layer, thread_layer= thread_layer))
                        t.rotate(V(0,0), i * 360.0/self.d['num_bolts']-22.5)
                support = self.add(Part(name='washing_bowl_support', layer='_washing_bowl_support', border = RoundedArc(V(0,0), (self.d['top_outer_rad']+self.d['top_rad'])/2, 8, 360.0/self.d['num_bolts']*2-5, startangle=360.0/self.d['num_bolts']/2-22.5)))
                for i in range(0, int(self.d['num_bolts']/2)):
                        support.add_copy({'rotate':[V(0,0), i*360.0/self.d['num_bolts']*2]})
        def _pre_render(self,config):
                self.get_plane().add_layer('_washing_bowl', 'delrin', 1, colour='#80808040')
                self.get_plane().add_layer('_washing_bowl_support', 'pvc', self.d['lip_depth']-2, colour='#808080')



 
class PiCam(Pathgroup):
        def __init__(self, pos, **config):
                self.init(config)
                self.translate(pos)
                self.holder_width = 25.5
                self.holder_height = 24
                self.cam_pos=self.holder_height-14.5
                centre = V(0,self.holder_height-14.5)
                holder_depression_top = -1.5
                holder_depression_bottom = -14.2
                holder_depression_depth = 1.5
                holder_hole_h1=-2
                holder_hole_h2=-14.5
                holder_hole_sp=21
                holder_wire_top = -16
                holder_wire_width = 21
                self.wire_width = holder_wire_width
                holder_wire_length = 15
                holder_wire_length2 = 20
                holder_wire_depth = 2.5
                hw = self.holder_width/2
                self.cutter="2mm_endmill"
                depression = self.add(
                        Rect(
                                centre + V(-self.holder_width/2,holder_depression_bottom),
                                tr = centre + V(self.holder_width/2,holder_depression_top),
                                partial_fill=(holder_depression_top-holder_depression_bottom)/2,
                                z1=-holder_depression_depth
                        )
                )
                wire = self.add(
                        Rect(
                                centre + V(-holder_wire_width/2, holder_wire_top-holder_wire_length),
                                tr=centre + V(holder_wire_width/2, holder_wire_top),
                                partial_fill=holder_wire_width/2,
                                z1=-holder_wire_depth
                        )
                )
                self.add(
                        Rect(
                                centre + V(-holder_wire_width/2, holder_wire_top-holder_wire_length2),
                                tr=centre + V(holder_wire_width/2, holder_wire_top-holder_wire_length),
                                partial_fill=holder_wire_width/2,
                                z1=-holder_wire_depth/2
                        )
                )
                self.add(Hole(centre + V(-holder_hole_sp/2,holder_hole_h2), rad=1.1, z1=-3))
                self.add(Hole(centre + V(holder_hole_sp/2,holder_hole_h2), rad=1.1, z1=-3))
                self.add(Hole(centre + V(holder_hole_sp/2,holder_hole_h1), rad=1.1, z1=-3))
                self.add(Hole(centre + V(-holder_hole_sp/2,holder_hole_h1), rad=1.1, z1=-3))






class CableTie(Pathgroup):
        def __init__(self, pos, cable_width, tie_width,**config):
                self.init(config)
                self.translate(pos)
                cw=cable_width+3.3
                self.add(RoundedRect(V(0,cw/2), centred=True, width=tie_width, height=3.4, rad=3.3/2))
                self.add(RoundedRect(V(0,-cw/2), centred=True, width=tie_width, height=3.4, rad=3.3/2))

class CableClipR(Part):
        def __init__(self, pos, clip_type, direction, layer,  **config):
                """Add an R type cable clip. centred on the cable, mode set to inset will bury the cable"""
                self.init(config)
                self.translate(pos)
                data = {
                        '5mm':{'width':9.5, 'length':19.0, 'clamp_depth':7.5, 'body_depth':3, 'body_length':8, 'hole_from_end':4.5, 'cable_from_end':4, 'bolt_size':'M4'},
                        '6mm':{'width':9.5, 'length':20.0, 'clamp_depth':9.2, 'body_depth':3, 'body_length':9.8, 'hole_from_end':4.5, 'cable_from_end':4.9, 'bolt_size':'M4'},
                        '10mm':{'width':9.5, 'length':25.0, 'clamp_depth':12.5, 'body_depth':3, 'body_length':12.8, 'hole_from_end':6, 'cable_from_end':6.4, 'bolt_size':'M4'},
                }
                assert clip_type in data
                direction = direction.normalize()
                d = data[clip_type]
                if 'mode' in config:
                        mode = config['mode']
                else:
                        mode = 'hole'
                if 'thread_depth' in config:
                        thread_depth = config['thread_depth']
                else:
                        thread_depth = False
                if 'clearance_layers' in config:
                        clearance_layers=config['clearance_layers']
                else:
                        clearance_layers = []
                rect_centre = V(0, -d['length']/2 + d['cable_from_end'])
                if mode=='hole_thread' or mode =='inset' or mode=='flat':
                        self.add(Bolt(rect_centre + V(0, -d['length']/2 + d['hole_from_end']), d['bolt_size'], thread_layer=layer, insert_layer=[], clearance_layers=clearance_layers, thread_depth=thread_depth) )
                if mode=='hole_thread':
                        self.add(Bolt(rect_centre +V(0,-d['length']/2 + d['hole_from_end'] + d['cable_from_end']), d['bolt_size'],  insert_layer=thread, clearance_layers=clearance_layers, thread_depth=thread_depth)) 
                a = math.atan2(direction[1], direction[0])/math.pi*180
                self.rotate(V(0,0), -a-90)
                if mode=='inset':
                        self.add(FilledRect(V(0,0), width = d['width']+1, height = d['body_length']+1, z1=-d['body_depth'], centred=True, side='in'), layer)
                if mode=='flat':
                        self.add(FilledRect(V(0,0), width = d['width']+1, height = d['body_length']+1, z1=-d['clamp_depth'], centred=True, side='in'), layer)
                        self.add(FilledRect(rect_centre, width = d['width']+1, height = d['length']+1, z1=-d['body_depth'], centred=True, side='in'), layer)

class LedHolder(Pathgroup):
        def __init__(self, pos, size, holder_type, **config):
                self.init(config)
                data={
                        'chrome':{
                                3:6,
                                5:7,
                                10:13,
                        },
                        'snapIn':{
                                3:5,
                                5:6,
                        },
                        'prominent':{
                                3:6,
                                5:7,
                                10:13
                        }
                }
                self.add(Hole(pos, rad=data[holder_type][size]/2))
                        

class Stepper(Part):
        def __init__(self,pos, stepper_type,layer, **config):
                self.init(config)
                dat={
                        'NEMA0.8':{
                                'bolt_size':'M3',
                                'bolt_sep':16,
                                'shaft_diam':4,
                                'pilot_diam':15,
                                'pilot_depth':1.5,
                                'width':20.4,
                                'shaft_len':15,
                                'corner_rad':2,
                        },
                        'NEMA1.1':{
                                'bolt_size':'M4',
                                'bolt_sep':23,
                                'shaft_diam':5,
                                'pilot_diam':22,
                                'pilot_depth':2,
                                'width':28,
                                'shaft_len':20,
                                'corner_rad':3,
                        },
                        'NEMA1.4':{
                                'bolt_size':'M4',
                                'bolt_sep':26,
                                'shaft_diam':5,
                                'pilot_diam':22,
                                'pilot_depth':2,
                                'width':36,
                                'shaft_len':21,
                                'back_shaft_len':10,
                                'corner_rad':4,
                        },
                        'NEMA1.7':{
                                'bolt_size':'M4',
                                'bolt_sep':31,
                                'shaft_diam':5,
                                'pilot_diam':22,
                                'pilot_depth':2,
                                'width':44,
                                'shaft_len':24,
                                'back_shaft_len':10,
                                'corner_rad':5,
                        },
                        'NEMA2.3':{
                                'bolt_size':'M5',
                                'bolt_sep':47.14,
                                'shaft_diam':6.35,
                                'pilot_diam':38.1,
                                'pilot_depth':1.6,
                                'width':58.5,
                                'flange_thickness':5,
                                'shaft_len':20.6,
                                'back_shaft_len':15,
                                'corner_rad':4,
                        },
                        'NEMA3.4':{
                                'bolt_size':'M6',
                                'bolt_sep':69.7,
                                'shaft_diam':14.0,
                                'pilot_diam':73.2,
                                'pilot_depth':2.5,
                                'width':86.5,
                                'flange_thickness':9.3,
                                'shaft_len':30,
                                'back_shaft_len':28,
                                'corner_rad':4,
                        },
                }
                if 'length' in config:
                        self.length=config['length']
                else:
                        self.length=50
		if 'thread_corners' in config and config['thread_corners']:
			thread_layer=layer
			clearance_layers='_stepper_layer'
		else:
			thread_layer='_stepper_layer'
			clearance_layers=layer
		
        #	self.add(Hole(pos, rad=10))
                d=dat[stepper_type]
                self.d=d
                self.cutlayer=layer
                if 'shaft_length' in config:
                        self.shaft_length=config['shaft_len']
                else:
                        self.shaft_length=d['shaft_len']

                if 'mode' in config and config['mode']=='justshaft':
                        self.add(Hole(pos, rad=d['shaft_diam']/2+1),layer)
                else:	
                        self.add(Bolt(pos+V( d['bolt_sep']/2, d['bolt_sep']/2), d['bolt_size'], clearance_layers=clearance_layers, thread_layer=thread_layer, insert_layer=[]))
                        self.add(Bolt(pos+V(-d['bolt_sep']/2, d['bolt_sep']/2), d['bolt_size'], clearance_layers=clearance_layers, thread_layer=thread_layer, insert_layer=[]))
                        self.add(Bolt(pos+V(-d['bolt_sep']/2,-d['bolt_sep']/2), d['bolt_size'], clearance_layers=clearance_layers, thread_layer=thread_layer, insert_layer=[]))
                        self.add(Bolt(pos+V(d['bolt_sep']/2,-d['bolt_sep']/2), d['bolt_size'], clearance_layers=clearance_layers, thread_layer=thread_layer, insert_layer=[]))
                
			if 'throughPilot' in config and config['throughPilot']=='through':
				self.add(Hole(pos, rad=d['pilot_diam']/2+0.1), layer)
			else:
                        	self.add(FilledCircle(pos, rad=d['pilot_diam']/2+0.1, z1=-d['pilot_depth']-0.5),layer)
                        	self.add(Hole(pos, rad=d['shaft_diam']/2+1),layer)
                        #self.add(Hole(pos, rad=d['shaft_diam']/2+1),layer)
                self.layer = '_stepper_layer'
		if 'motorDir' in config:
			motorDir = config['motorDir']
		else:
			motorDir = 1;
		if 'motorOffset' in config:
			motorOffset = config['motorOffset']
		else:
			motorOffset = 0;
                self.add_border( RoundedRect(pos, centred=True, width=d['width'], height=d['width'], rad=d['corner_rad'], zoffset=self.length*motorDir+motorOffset, thickness=self.length*motorDir))
                
                self.shaft = self.add(Part(name='shaft', layer='_stepper_layer', border = Circle(pos, rad=d['shaft_diam']/2, thickness=self.shaft_length*motorDir, zoffset=motorOffset)))
                self.pilot = self.add(Part(name='pilot', layer='_stepper_layer', border = Circle(pos, rad=d['pilot_diam']/2), thickness=d['pilot_depth']*motorDir, zoffset=motorOffset)) 

        def _pre_render(self,config):
                self.stepper_layer = '_stepper_layer'
                l= self.get_plane().get_layer_config(self.cutlayer)
                zoffset=l['zoffset']
                self.get_plane().add_layer(self.stepper_layer, 'aluminium', 10, colour='#808080', zoffset=0)


class RoundShaftSupport(Pathgroup):
        def __init__(self,pos, shaft_type, mode,  **config):
                self.init(config)
                dat={
                        'SK3':{'h':20, 'E':21, 'W':42,'L':14, 'F':37.5, 'G':6, 'P':18, 'B':32, 'S':5.5, 'bolt':'M5'},
                        'SK4':{'h':20, 'E':21, 'W':42,'L':14, 'F':37.5, 'G':6, 'P':18, 'B':32, 'S':5.5, 'bolt':'M5'},
                        'SK5':{'h':20, 'E':21, 'W':42,'L':14, 'F':37.5, 'G':6, 'P':18, 'B':32, 'S':5.5, 'bolt':'M5'},
                        'SK6':{'h':20, 'E':21, 'W':42,'L':14, 'F':37.5, 'G':6, 'P':18, 'B':32, 'S':5.5, 'bolt':'M5'},
                        'SK7':{'h':20, 'E':21, 'W':42,'L':14, 'F':37.5, 'G':6, 'P':18, 'B':32, 'S':5.5, 'bolt':'M5'},
                        'SK8':{'h':20, 'E':21, 'W':42,'L':14, 'F':37.5, 'G':6, 'P':18, 'B':32, 'S':5.5, 'bolt':'M5'},
                        'SK10':{'h':20, 'E':21, 'W':42,'L':14, 'F':37.5, 'G':6, 'P':18, 'B':32, 'S':5.5, 'bolt':'M5'},
                        'SK12':{'h':23, 'E':21, 'W':42,'L':14, 'F':37.5, 'G':6, 'P':20, 'B':32, 'S':5.5, 'bolt':'M5'},
                        'SK13':{'h':23, 'E':21, 'W':42,'L':14, 'F':37.5, 'G':6, 'P':20, 'B':32, 'S':5.5, 'bolt':'M5'},
                        'SK16':{'h':27, 'E':24, 'W':48,'L':16, 'F':44, 'G':8, 'P':25, 'B':38, 'S':5.5, 'bolt':'M5'},
                        'SK20':{'h':31, 'E':30, 'W':60,'L':20, 'F':51, 'G':10, 'P':30, 'B':45, 'S':6.6, 'bolt':'M6'},
                        'SK25':{'h':35, 'E':35, 'W':70,'L':24, 'F':60, 'G':12, 'P':38, 'B':56, 'S':6.6, 'bolt':'M8'},
                        'SK30':{'h':42, 'E':42, 'W':84,'L':28, 'F':70, 'G':12, 'P':44, 'B':64, 'S':9, 'bolt':'M10'},
                }
                d=dat[shaft_type]
                self.dims =d
                if mode=='clearance':
                        self.add(Hole(pos+V(0,d['B']/2), rad = milling.bolts[d['bolt']]['clearance']/2))
                        self.add(Hole(pos+V(0,-d['B']/2), rad = milling.bolts[d['bolt']]['clearance']/2))
                if mode=='insert':
                        self.add(Hole(pos+V(0,d['B']/2), rad = milling.inserts[d['bolt']]['diams'], z1= milling.inserts[d['bolt']]['depths']))
                        self.add(Hole(pos+V(0,-d['B']/2), rad = milling.inserts[d['bolt']]['diams'], z1= milling.inserts[d['bolt']]['depths']))
                if mode=='counterbore':
                        self.add(Hole(pos+V(0,d['B']/2), rad = milling.bolts[d['bolt']]['clearance']/2))
                        self.add(Hole(pos+V(0,-d['B']/2), rad = milling.bolts[d['bolt']]['clearance']/2))
                        self.add(ClearRect(pos, centred=True, width=d['L']+0.4, height=d['W']+0.4, partial_fill=(d['L']+0.4)/2, fill_direction='in'))

class LinearBearing(Pathgroup):
        def __init__(self,pos, bearing_type, mode,  **config):
                self.init(config)
                dat={
                        'SMA12':{'d':12, 'h':15, 'D':21, 'W':42, 'H':28,'G':24, 'A':7.4, 'J':30.5, 'E':5.75, 's1':'M5', 's2':4.3, 'K':26, 'L':36}
                }
                if bearing_type in dat:
                        d=dat[bearing_type]
                        self.dims=d
                        if mode=='clearance':
                                self.add(Hole(pos+V(-d['K']/2, -d['J']/2), milling.bolts[d['s1']]['clearance']/2))
                                self.add(Hole(pos+V(d['K']/2, -d['J']/2), milling.bolts[d['s1']]['clearance']/2))
                                self.add(Hole(pos+V(-d['K']/2, d['J']/2), milling.bolts[d['s1']]['clearance']/2))
                                self.add(Hole(pos+V(d['K']/2, d['J']/2), milling.bolts[d['s1']]['clearance']/2))

class ProfileBearing(Part):
        def __init__(self,pos, bearing_type, mode,  **config):
                self.init(config)
                dat={
#http://dgjiayi88.en.alibaba.com/product/423259063-210484550/TAIWAN_original_MGN9C_HIWIN_linear_guide.html
                        'MGN9C':{'W':20, 'H':10, 'B':15, 'L':28.9,'C':10, 'thread':'M3', 'H1':2.4, }
                }
                self.bearing_type=bearing_type
                self.d=dat[bearing_type]
                self.create_layer=True
                self.translate(pos)
                if 'layers' in config:
                        layers = config['layers']
                        if 'carriage' in layers:
                                self.carriage_layer=layers['carriage']
                                self.create_layer=False
                        else:
                                self.carriage_layer = 'carriage_layer'
                        if 'clearance' not in layers:
                                layers['clearance'] = []
                        if 'head' not in layers:
                                layers['head'] =[]
                        if 'head' in config:
                                head=config['head']
                        else:
                                head= 'cap'

                        self.add(Bolt(V(self.d['B']/2, self.d['C']/2), self.d['thread'], clearance_layers=layers['clearance'], insert_layer=[], thread_layer=self.carriage_layer, head_layer=layers['head'], head='cap'))
                        self.add(Bolt(V(-self.d['B']/2, self.d['C']/2), self.d['thread'], clearance_layers=layers['clearance'], insert_layer=[], thread_layer=self.carriage_layer, head_layer=layers['head'], head='cap'))
                        self.add(Bolt(V(-self.d['B']/2, -self.d['C']/2), self.d['thread'], clearance_layers=layers['clearance'], insert_layer=[], thread_layer=self.carriage_layer, head_layer=layers['head'], head='cap'))
                        self.add(Bolt(V(self.d['B']/2, -self.d['C']/2), self.d['thread'], clearance_layers=layers['clearance'], insert_layer=[], thread_layer=self.carriage_layer, head_layer=layers['head'], head='cap'))
                self.layer=self.carriage_layer
                self.add_border(Rect(V(0,0), centred=True, width = self.d['W'], height=self.d['L']))
                self.name=self.bearing_type+"_carriage"
                self.zoffset=self.d['H']
        def _pre_render(self,config):
                if self.create_layer:
                        self.carriage_layer = 'carriage_layer'
                        self.get_plane().add_layer(self.carriage_layer, 'aluminium', self.d['H']-self.d['H1'],  colour='#808080')
class Bearing(Pathgroup):
        def __init__(self, pos, outer_rad, inner_rad, depth, **config):
                outer_rad=float(outer_rad)
                inner_rad=float(inner_rad)
                self.init(config)
                self.add(FilledCircle(pos, rad=outer_rad, z1=-depth))
                overlap = max(1, (outer_rad-inner_rad)/5)
                self.add(Hole(pos, rad=outer_rad-overlap))
#		self.add_bom('Bearing', 1, part_number='Bearing_ID_'+str(inner_rad*2)+"_OD_"+str(outer_rad*2)+"_D_"+str(depth), description='Ball Bearing ID='+str(innerrad*2)+" OD="+str(outerrad*2)+" depth="+str(depth))		
#		self.add_bom("Ball_bearing_"+str(outer_rad*2)+'x'+str(inner_rad*2)+'x'+str(depth), 1, 'OD='+str(outer_rad*2)+"mm ID="+str(inner_rad*2)+" Depth="+str(depth),'')

class LinearRail(Part):
        def __init__(self, start, end, rail_type, **config):
                self.init(config)
                if 'transform' in config:
                        del(config['transform'])
                dat={
                        'LFS-12-10':{'width':36, 'centre_height':16, 'centre_width':24, 'holespacing_x':50, 'holespacing_y':0, 'bolt_type':'M6'},
                        'LFS-12-3':{'width':90, 'centre_height':25, 'centre_width':49, 'holespacing_x':100, 'holespacing_y':75, 'bolt_type':'M6'},
                        'LFS-12-2':{'width':62, 'centre_height':25, 'centre_width':12, 'holespacing_x':100, 'holespacing_y':50, 'bolt_type':'M6'},
                        'MGN-9C':{'width':9, 'holespacing_y':0, 'bolt_type':'M3', 'holespacing_x':20, 'height':6.5}, 
                        'MGN-12C':{'width':12, 'holespacing_y':0, 'bolt_type':'M3', 'holespacing_x':25, 'height':8}, 
                        'MGN-15C':{'width':12, 'holespacing_y':0, 'bolt_type':'M3', 'holespacing_x':40, 'height':10}, 
                }
                if rail_type in dat:
                        d=dat[rail_type]
                        self.d=d
                        tot_len = (end-start).length()
                        parallel = (end-start).normalize()
                        perp = rotate(parallel, 90)
                        hole_gaps = int(math.floor(tot_len/d['holespacing_x']))
                        if 'offsetx' not in config:
                                offsetx = (tot_len - hole_gaps*d['holespacing_x'])/2
                        else:
                                offsetx = config['offsetx']
                        border=Path(side='out', closed=True)
                        border.add_point(perp*-d['width']/2+parallel*tot_len/2) 
                        border.add_point(perp*d['width']/2+parallel*tot_len/2) 
                        border.add_point(perp*d['width']/2-parallel*tot_len/2) 
                        border.add_point(perp*-d['width']/2-parallel*tot_len/2) 
                        self.add_border(border)
                        self.zoffset=self.d['height']
                        self.layer = '_rail_layer'
                        if 'head_layer' in config:
                                if type(config['head_layer']) is list:
                                        config['head_layer'].append('_rail_layer')
                                else:
                                        config['head_layer'] = [ config['head_layer'], '_rail_layer' ]
                        else:
                                config['head_layer'] = '_rail_layer'
                        config['head']='cap'
                        for i in range(0, hole_gaps+1):
                                if d['holespacing_y'] ==0:
                                        self.add(Bolt(start+ parallel *(offsetx+ d['holespacing_x']*i), d['bolt_type'], **config))
                                else:
                                        self.add(Bolt(start+parallel*(offsetx+ d['holespacing_x']*i) + perp * d['holespacing_y'] , d['bolt_type'], **config))
                                        self.add(Bolt(start+parallel*(offsetx+ d['holespacing_x']*i) - perp * d['holespacing_y'] , d['bolt_type'], **config))
                        self.add(Lines([start+perp*d['width']/2, start-perp*d['width']/2, end-perp*d['width']/2, end+perp*d['width']/2], closed=True), 'paper')
        def _pre_render(self,config):
                self.carriage_layer = '_rail_layer'
                self.get_plane().add_layer(self.carriage_layer, 'aluminium', self.d['height'], colour='#808080')

class Insert(Part):
        def __init__(self, pos, insert_size,layer, **config):
                """Standard wood insert at pos"""
                self.init(config)
                self.add_bom("Wood insert", 1, str(insert_size)+"insert",'')

                if insert_size in milling.inserts:
                        if 'insert_type' in config and config['insert_type'] in milling.inserts[insert_size]:
                                insert=milling.inserts[insert_size][config['insert_type']]
                        else:
                                insert=milling.inserts[insert_size]
                        if 'z1' in config:
                                depths=[]
                                for d in insert['depths']:
                                        if d is False:
                                                depths.append(config['z1'])
                                        else:
                                                depths.append(d)
                                del(config['z1'])
                        else:
                                depths = insert['depths']
                        self.add(Hole(pos, rad=insert['diams'], z1 = depths, **config), layer)	

class LoadCell(Part):
        def __init__(self, pos, cell_type, modes,**config):
                """Load cell, centred around bolt through bottom - if there are two bolts on each end the outer one is the centre"""	
                self.init(config)
                dat={
                        'phidget780g':{'w':9.32, 'l':45.16, 'h':5.99, 's':29.48, 's2':22.18, 'h':'M3', 'z':-2},
                        'phidget5kg':{'w':12.7, 'l':55.25, 'h':12.7, 's':40, 'h':'M5', 'z':-2},
                        'phidget10kg':{'w':12.7, 'l':55.25, 'h':12.7, 's':40, 'h':'M5', 'z':-2},
                        'phidget20kg':{'w':12.7, 'l':55.25, 'h':12.7, 's':40, 'h':'M5', 'z':-2},
                        'phidget50kg':{'w':12.7, 'l':55.25, 'h':12.7, 's':40, 'h':'M5', 'z':-2},
                }
                d=dat[cell_type]
                self.dims=d
                self.add_bom('Load cell', 1, cell_type, '')
                for l in modes.keys():
                        mode=modes[l]	
                        e=(d['l']-d['s'])/2
                        if mode=='bottom':
                                self.add(Hole(pos+V(0,0), rad=milling.bolts[d['h']]['clearance']/2), l)
                                if 's2' in d:
                                        self.add(Hole(pos+V((d['s']-d['s2'])/2,0), rad=milling.bolts[d['h']]['clearance']/2, side='in'), l)
                        if mode=='bottom_counterbore':
                                if 'counterbore' in config:
                                        counterbore = config['counterbore']
                                        self.add(ClearRect(pos+V(d['l']/4-e+1, d['w']/2), tr=pos+V(-e, -d['w']/2-1), partial_fill=d['w']/2-1, z1=counterbore, side='in'),l)
                                else:
                                        counterbore = 0
                                self.add(Hole(pos+V(0,0), rad=milling.bolts[d['h']]['clearance']/2), l)
                                self.add(ClearRect(pos+V(d['l']/4-e, d['w']/2+2), tr=pos+V(d['l']-e, -d['w']/2-2), side='in'),l)
                                if 's2' in d:
                                        self.add(Hole(pos+V((d['s']-d['s2'])/2,0), rad=milling.bolts[d['h']]['clearance']/2, side='in'), l)
                        if mode=='bottom_clear':
                                self.add(Hole(pos+V(0,0), rad=milling.bolts[d['h']]['clearance']/2), l)
                                self.add(ClearRect(pos+V(d['l']/4-e, d['w']/2+1), tr=pos+V(d['l']-e, -d['w']/2-1), z1=d['z'], side='in'),l)
                                if 's2' in d:
                                        self.add(Hole(pos+V((d['s']-d['s2'])/2,0), rad=milling.bolts[d['h']]['clearance']/2), l)
                        if mode=='top':
                                self.add(Hole(pos+V(d['s'],0), rad=milling.bolts[d['h']]['clearance']/2), l)
                                if 's2' in d:
                                        self.add(Hole(pos+V(d['s']-(d['s']-d['s2'])/2,0), rad=milling.bolts[d['h']]['clearance']/2), l)
                        if mode=='whole_counterbore':
                                if('whole_counterbore' in config and config['whole_counterbore']):	
                                        self.add(ClearRect(pos+V(d['l']/2-e,0), width=d['l']+4, height=d['w']+4, z1=config['whole_counterbore'], partial_fill=d['w']/2-1, fill_direction='in', centred=True, side='in'),l)
                                else:
                                        self.add(ClearRect(pos+V(d['l']/2-e,0), width=d['l']+4, height=d['w']+4, centred=True, side='in'),l)

class DrilledBall(Part):
        def __init__(self,pos, diameter='12.7', thread='M4', head='flanged', length=16, layer='base',**config):
                self.init(config)
                self.add(Hole(pos, rad=[milling.bolts[thread]['clearance'], milling.bolts[thread]['clearance']*1.5], z1=[False, -1], centred=True),layer)
                self.add_bom("Machine screw", 1, str(length)+"mm "+str(thread)+" "+str(head),'')
                self.add_bom("Tapped Mild Steel ball", 1, str(diameter)+"mm "+str(thread)+" tapped",'')

class ScrewBOM(BOM_part):
        def __init__(self, thread, head, length, number):
                self.init()
                self.name="Machine screw"
                self.number=number
                self.part_number=str(length)+"mm "+str(thread)+" "+str(head)
                self.description=''
                self.length=length
                self.head = head
                self.thread = thread

class Fan(Pathgroup):
        def __init__(self, pos,  **config):
                """Add a fan of fan_tpe at pos"""
                self.init(config)
                self.translate(pos)
                data={
                        '40mm':{'centrerad':38/2,  'hole_off':31.6/2, 'holeRad':4.5/2, 'threadRad':3.3/2},			
                        '60mm':{'centrerad':58/2,  'hole_off':50/2, 'holeRad':4.5/2, 'threadRad':3.3/2},
                        '80mm':{'centrerad':92/2, 'centre_limit':78/2, 'hole_off':71.5/2, 'holeRad':4.5/2, 'threadRad':3.3/2 },
                        '92mm':{'centrerad':104/2, 'centre_limit':90/2, 'hole_off':82.5/2, 'holeRad':4.5/2, 'threadRad':3.3/2 },
                        '120mm':{'centrerad':132/2, 'centre_limit':118/2, 'hole_off':105/2, 'holeRad':4.5/2, 'threadRad':3.3/2 },
                        '140mm':{'centrerad':150/2, 'centre_limit':138/2, 'hole_off':124.5/2, 'holeRad':4.5/2, 'threadRad':3.3/2 },
                        '217mm':{'centrerad':217.0/2, 'hole_off':169.0/2, 'holeRad':4.5/2, 'threadRad':3.3/2 },
                        }
                if 'fan_type' in config:
                        d=data[config['fan_type']]
                else:
                        d=data['120mm']
                if 'grill' in config and config['grill']:
                        if config['grill'] == True:
                                holerad = 6/2
                        else:
                                holerad = config['grill']
                
                        spacing = holerad * 2.5

                        self.add(RoundSpeakerGrill(V(0,0), d['centrerad'], holerad, spacing))

                elif 'no_hole' not in config or not config['no_hole']:
                        print "FAN HOLE"
                        if 'centre_limit' in d:
                                print "CENTRE LIMIT"
                                o = math.sqrt(d['centrerad']**2 - d['centre_limit']**2)
                                cutout=self.add(Path(side='in', closed=True))
                                cutout.add_point(V(o,d['centre_limit']), 'sharp')
#				cutout.add_point(V(0,0), 'aroundcurve', radius=d['centrerad'], direction='ccw')
                                cutout.add_point(V(d['centre_limit'],o), 'sharp')
                                
                                cutout.add_point(V(d['centre_limit'],-o), 'sharp')
#				cutout.add_point(V(0,0), 'aroundcurve', radius=d['centrerad'], direction='ccw')
                                cutout.add_point(V(o,-d['centre_limit']), 'sharp')
        
                                cutout.add_point(V(-o,-d['centre_limit']), 'sharp')
#				cutout.add_point(V(0,0), 'aroundcurve', radius=d['centrerad'], direction='ccw')
                                cutout.add_point(V(-d['centre_limit'],-o), 'sharp')
        
                                cutout.add_point(V(-d['centre_limit'],o), 'sharp')
#				cutout.add_point(V(0,0), 'aroundcurve', radius=d['centrerad'], direction='ccw')
                                cutout.add_point(V(-o,d['centre_limit']), 'sharp')
                        else:
                                self.add(Hole(V(0,0), rad=d['centrerad']))
                        print self.paths
                if 'tapped_holes' in config and config['tapped_holes']:
                        self.add(Hole(V(d['hole_off'],d['hole_off']), d['threadRad']))
                        self.add(Hole(-V(d['hole_off'],d['hole_off']), d['threadRad']))
                        self.add(Hole(-V(d['hole_off'],-d['hole_off']), d['threadRad']))
                        self.add(Hole(V(d['hole_off'],-d['hole_off']), d['threadRad']))
                elif 'inserts' in config and config['inserts']:
                        insert_size='M4'
                        if 'inserts' in config and config['inserts'] in milling.inserts[insert_size]:
                                insert=milling.inserts[insert_size][config['inserts']]
                        else:
                                insert=milling.inserts[insert_size]
                        self.add(Hole(V(d['hole_off'],d['hole_off']), rad=insert['diams'], z1 = insert['depths'], **config))			
                        self.add(Hole(V(d['hole_off'],-d['hole_off']), rad=insert['diams'], z1 = insert['depths'], **config))			
                        self.add(Hole(V(-d['hole_off'],-d['hole_off']), rad=insert['diams'], z1 = insert['depths'], **config))			
                        self.add(Hole(V(-d['hole_off'],d['hole_off']), rad=insert['diams'], z1 = insert['depths'], **config))		
                elif 'noholes' in config and config['noholes']:
                        pass	
                else:
                        self.add(Hole(V(d['hole_off'],d['hole_off']), d['holeRad']))
                        self.add(Hole(-V(d['hole_off'],d['hole_off']), d['holeRad']))
                        self.add(Hole(-V(d['hole_off'],-d['hole_off']), d['holeRad']))
                        self.add(Hole(V(d['hole_off'],-d['hole_off']), d['holeRad']))

class StepperDriver(Pathgroup):
        def __init__(self, pos, **config):
                self.init(config)
                self.translate(pos)
                data={
                        'DM422':{'l':86, 'w':55, 'hs_b':79, 'hoff_b':27.5,'hs_s':79, 'hoff_s':11.75}
                }
                if 'type' in config:
                                d=data[config['type']]
                else:
                        d=data['DM422']
                if 'orientation' in config and config['orientation']=='back':
                        self.add(Hole(V(d['hs_b']/2, 0), rad=4.5/2))
                        self.add(Hole(V(-d['hs_b']/2, 0), rad=4.5/2))
                else:
                        self.add(Hole(V(d['hs_b']/2, 0), rad=4.5/2))
                        self.add(Hole(V(-d['hs_b']/2, 0), rad=4.5/2))

class RFID_holder(Part):
        def __init__(self, pos, name, **config):
                self.init(config)
                self.translate(pos)
                self.name=name
                width=71
                length=107
                socket_slot_l=40
                socket_extra=14
                socket_slot_w=11
                if 'layer_config' not in config:
                        layer_config={'base':'base', 'part':'back'}
                else:
                        layer_config=config['layer_config']
                self.layer=layer_config['part']
                cutout=self.add(Path(side='in', closed=True), layer_config['base'])
                cutout.add_point(V(length/2, width/2))
                cutout.add_point(V(length/2, -width/2))
                cutout.add_point(V(-length/2, -width/2))
                cutout.add_point(V(-length/2, -socket_slot_w/2))
                cutout.add_point(V(-length/2-socket_slot_l, -socket_slot_w/2))
                cutout.add_point(V(-length/2-socket_slot_l, socket_slot_w/2))
                cutout.add_point(V(-length/2, socket_slot_w/2))
                cutout.add_point(V(-length/2, width/2))
                self.add_border(Path(side='out', closed=True))
                self.border.add_point(PIncurve(V(length/2+5, width/2+12), radius=5))
                self.border.add_point(PIncurve(V(length/2+5, -width/2-12), radius=5))
                self.border.add_point(PIncurve(V(-length/2-5-socket_slot_l, -width/2-12), radius=5))
                self.border.add_point(PIncurve(V(-length/2-5-socket_slot_l, -socket_slot_w/2), radius=20))
                self.border.add_point(PIncurve(V(-length/2-5, -socket_slot_w/2), radius=5))
                self.border.add_point(PIncurve(V(-length/2-5, socket_slot_w/2), radius=5))
                self.border.add_point(PIncurve(V(-length/2-5-socket_slot_l, socket_slot_w/2), radius=20))
                self.border.add_point(PIncurve(V(-length/2-5-socket_slot_l, width/2+12), radius=5))
        #	self.border.translate(pos)
#		self.add(RoundedRect(V(-length/2-socket_slot_l/2-7, 0), centred=True, width=14, height=socket_slot_w, z1=-6, partial_fill=socket_slot_w/2), layer_config['base'])

                #RoundedRect(V(length/2+5, width/2+12), tr=V(-length/2-socket_slot_l-5, -width/2-12), side='out', rad=5)
                
                self.add(Bolt(V(length/2,width/2+6), clearance_layers=layer_config['part']))
                self.add(Bolt(V(length/2,-width/2-6), clearance_layers=layer_config['part']))
                self.add(Bolt(V(-length/2-socket_slot_l,width/2+6), clearance_layers=layer_config['part']))
                self.add(Bolt(V(-length/2-socket_slot_l,-width/2-6), clearance_layers=layer_config['part']))

class Plate(Part):
        """
                Create a circle with holes around the edge
                pos - pos
                name - part name
                rad - external rad or circle
                centreRad - rad of hole in centre (can be 0)
                holes - number of holes
                holeRad - radius from centre holes should appear
                holeSize - rad of holes
                [layer_config] - dict that defaults to {'base':'base', 'part':'stringplate', 'thread':[], 'clearance':['paper','perspex']} defining layer config
        """
        def __init__(self, pos, name, rad, centreRad, holes, holeRad, holeSize, **config):
                self.init(config)
                self.initPlate(pos, name, rad, centreRad, holes, holeRad, holeSize, config)

        def initPlate(self, pos, name, rad, centreRad, holes, holeRad, holeSize, config):
                self.name=name
                self.transform={'translate':pos}
                if 'layer_config' not in config:
                        layer_config={'base':'base', 'part':'stringplate', 'thread':[], 'clearance':['paper','perspex']}
                else:
                        layer_config=config['layer_config']

                self.add_border(Circle(V(0,0), rad=rad, side='out'))
                self.layer=layer_config['part']
                if not 'base' in layer_config:
                        layer_config['base']=[]
                if not  'clearance' in layer_config:
                        layer_config['clearance']=[]
                if not 'part' in layer_config:
                        layer_config['part']=[]
                if 'clearance' in layer_config and type(layer_config['clearance']) is list and 'part' in layer_config and  type(layer_config['part']) is list:
                        clearance=layer_config['part']+layer_config['clearance']
                elif type(layer_config['clearance']) is list:
                        clearance=copy.copy(layer_config['clearance'])
                        clearance.append(layer_config['part'])
                else:
                        clearance=[layer_config['clearance'], layer_config['part']]
                if 'thread' not in layer_config:
                        layer_config['thread']=[]
                if 'thread_depth' in config:
                        thread_depth = config['thread_depth']
                else:
                        thread_depth = False
#		screwConf={layer_config['part']:{'rad':milling.bolts[holeSize]['clearance']/2+0.5}, layer_config['base']:{'rad':milling.bolts[holeSize]['clearance']/2}}
                if holes >0:
                        for i in range(0, holes):
                                self.add(Bolt(V(holeRad,0), 'M4', 'button', 16, clearance_layers=clearance, insert_layer=layer_config['base'], thread_layer=layer_config['thread'], thread_depth = thread_depth, transform={'rotate':[V(0,0), i*360/holes]}))
#				self.add(Screw(V(d['holeRad'],0), layer_config=screwConf, transform={'rotate':[V(0,0), i*360/d['holes']]}))
                if centreRad >0:
                        self.add(Hole(V(0,0), rad=centreRad))
                        if 'base' in layer_config:
                                self.add(Hole(V(0,0), rad=centreRad+2), layer_config['base'])
                        if 'clearance' in layer_config:
                                self.add(Hole(V(0,0), rad=centreRad+2), layer_config['clearance'])

class RoundPlate(Plate):
        """
                Attempt at standardising some plates
                pos - pos
                plateType - one of the types in the array below
                [layer_config] - dict that defaults to {'base':'base', 'part':'stringplate', 'thread':[], 'clearance':['paper','perspex']} defining layer config
"""
        def __init__(self, pos, plateType, **config):
                self.init(config)
                data={
                        'stringplate6':{'rad':28, 'centreRad':4/2, 'holes':6, 'holeRad':19, 'holeSize':'M4'},
                        'stringplate3':{'rad':28, 'centreRad':4/2, 'holes':3, 'holeRad':19, 'holeSize':'M4'},
                }
                d=data[plateType]
                self.initPlate(pos, plateType, d['rad'], d['centreRad'], d['holes'], d['holeRad'], d['holeSize'], config)

class FlatMonitor(Part):
        def __init__(self, pos, monitorType, **config):
                self.init(config)
                self.translate(pos)
                if 'layers' in config and 'base' in  config['layers']:
                        base = config['layers']['base']
                else:
                        base = 'base'
                if 'layers' in config and 'underbase' in  config['layers']:
                        underbase = config['layers']['underbase']
                else:
                        underbase='underbase'
                        pass
                        #raise ValueError('Need underbase in layers')
                if 'layers' in config and 'paper' in  config['layers']:
                        paper = config['layers']['paper']
                else:
                        paper = 'paper'

                data={
                        'B101UAN02'  :{'ext_width':230.0, 'ext_height':149.7, 'screen_width':217.0,  'screen_height':135.5, 'depth':4, 'border':5 },
                        'B140HAN01.2':{'ext_width':321, 'ext_height':188, 'screen_width':309.14, 'screen_height':173.89, 'lug_width':15, 'lug_depth':1, 'lug_height':7, 'toplug_fe':20, 'botlug_fe':36, 'elec_width':223, 'elec_height':12, 'conn_width':30, 'conn_x':115, 'conn_y0':-87, 'conn_y1':-117},
                        'B156HAN01.2':{'ext_width':359.5, 'ext_height':223.8, 'screen_width':344.16, 'screen_height':193.59},
                        '27inch':{'ext_width':359.5*27/21, 'ext_height':223.8*27/21, 'screen_width':344.16, 'screen_height':193.59},
                        '32inch':{'ext_width':359.5*32/21, 'ext_height':223.8*32/21, 'screen_width':344.16, 'screen_height':193.59},
                }
                assert monitorType in data
                d = data[monitorType]
                if 'border' in d:
                        border = d['border']
                else:
                        border = 5
                if 'cover_offset' in config:
                        cover_offset = config['cover_offset']
                else:
                        cover_offset = V((d['ext_width'] - d['ext_height'])/2, (d['ext_width'] - d['ext_height'])/2-35)
                self.d = d
                if 'toplug_fe' in d:
                        self.add(Rect(V(d['ext_width']/2- d['toplug_fe'] - d['lug_width']/2, d['ext_height']/2+d['lug_height']/2), centred=True, width=d['lug_width'], height=d['lug_height'], z1=-d['lug_depth'], side='in'),base)
                        self.add(Rect(V(-d['ext_width']/2+ d['toplug_fe'] + d['lug_width']/2, d['ext_height']/2+d['lug_height']/2), centred=True, width=d['lug_width'], height=d['lug_height'], z1=-d['lug_depth'], side='in'), base)
                if 'botlug_fe' in d:
                        self.add(Rect(V(d['ext_width']/2- d['botlug_fe'], -d['ext_height']/2 - d['lug_height']/2), centred=True, width=d['lug_width'], height=d['lug_height'], z1=-d['lug_depth'], side='in'), base)
                        self.add(Rect(V(-d['ext_width']/2+ d['botlug_fe'], -d['ext_height']/2 - d['lug_height']/2), centred=True, width=d['lug_width'], height=d['lug_height'], z1=-d['lug_depth'], side='in'), base)
                
#		self.add(FourObjects(V(0,0), Hole(V(0,0), rad=4.5/2),centred=True, width=d['ext_width']+20, height = d['ext_height']+20, layers=base))
#		self.add(FourObjects(V(0,0), Insert(cover_offset, 'M4', [underbase,base]),centred=True, height=d['ext_width']-20, width = d['ext_height']-20))
                self.add(Rect(V(0,0), centred=True, width=d['ext_width']-2*border, height = d['ext_height']-2*border), base)
                if 'depth' in d and 'border' in d:
                        self.add(Rect(V(0,0), centred=True, width=d['ext_width'], height = d['ext_height'], z1=-d['depth'], partial_fill=border), base)
                
                cutout=self.add(Path(closed=True, side='in'), base)
                cutout.add_point(V(d['ext_width']/2, d['ext_height']/2))
                cutout.add_point(V(-d['ext_width']/2, d['ext_height']/2))
                cutout.add_point(V(-d['ext_width']/2, -d['ext_height']/2))
                if 'elec_width' in d:
                        cutout.add_point(V(-d['elec_width']/2, -d['ext_height']/2))
                        cutout.add_point(V(-d['elec_width']/2, -d['ext_height']/2-d['elec_height']))
                if 'conn_x' in d:
                        cutout.add_point(V(-d['ext_width']/2+d['conn_x']-d['conn_width']/2, -d['ext_height']/2-d['elec_height']))
                        cutout.add_point(V(-d['ext_width']/2+d['conn_x']-d['conn_width']/2, d['conn_y1']))
                        cutout.add_point(V(-d['ext_width']/2+d['conn_x']+d['conn_width']/2, d['conn_y1']))
                        cutout.add_point(V(-d['ext_width']/2+d['conn_x']+d['conn_width']/2, -d['ext_height']/2-d['elec_height']))
                if 'elec_width' in d:
                        cutout.add_point(V(d['elec_width']/2, -d['ext_height']/2-d['elec_height']))
                        cutout.add_point(V(d['elec_width']/2, -d['ext_height']/2))
                cutout.add_point(V(d['ext_width']/2, -d['ext_height']/2))

                if 'conn_y' in d:
                        self.add(Rect(V(-d['ext_width']/2+d['conn_x'], (d['conn_y0']+d['conn_y1'])/2), centred=True, width = d['conn_width'], height = d['conn_y0'] - d['conn_y1']), underbase)

#		self.add(Rect(V(0,0), centred=True, width = d['ext_width'], height = d['ext_height']), base)
                self.add(Rect(V(0,0), centred=True, width = d['screen_width'], height = d['screen_height']), paper)

class Monitor(Part):
        def __init__(self, pos, monitorType, **config):
                self.init(config)
                self.translate(pos)

                if monitorType =='LG23':
                        mountPlateCentre=-V(0,-5)
                        monitorMountHeight=120
                        monitorMountWidth=300

                        monitorMountHoleSpacing=75
                        monitorMountBoltDiameter=4
                        perspexPlatewidth=30
                        holeOffset=20
                        offset=V(0,15)
                        monitorWidth = 533
                        monitorHeight = 326
                elif monitorType =='LG22':
                        mountPlateCentre=-V(0,-5)
                        monitorMountHeight=120
                        monitorMountWidth=300
                        monitorMountHoleSpacing=75
                        monitorMountBoltDiameter=4
                        perspexPlatewidth=30
                        holeOffset=20
                        offset=V(0,8)
                        monitorWidth = 509
                        monitorHeight = 316
                else:
                        raise ValueError('Invalid Monitor Type')


                dcDcConverterWidth=58 
                dcDcConverterHeight=26.5 
                dcDcConverterCentre=V(monitorMountHeight/2+30+dcDcConverterWidth/2,-monitorHeight/2+50)

                #Monitor mount holes - assume square
                self.add(SquareObjects(mountPlateCentre-offset, 2,2, Rect(V(0,0), centred=True, height=monitorMountBoltDiameter, width=5*monitorMountBoltDiameter, side='in'), centred=True, width=monitorMountHoleSpacing, height=monitorMountHoleSpacing), 'perspex')
                
                #Mount plate mounting holes
#		self.add(SquareObjects(mountPlateCentre-offset, 2,2, Hole(V(0,0), rad=5/2), centred=True, width=monitorMountHeight-holeOffset, height=monitorMountWidth-holeOffset), ['base', 'perspex'])
                self.add(FourObjects(mountPlateCentre-offset, Hole(V(0,0), rad=4.5/2),  centred=True, width = monitorMountHoleSpacing, height = monitorMountHoleSpacing, layers= ['base', 'perspex']))

                #Perspex spacer to sit under the mount plate
                self.add(RoundedRect(mountPlateCentre-offset-V(0,((monitorMountWidth/2)-(perspexPlatewidth/2))), centred=True, width=monitorMountHeight, height=perspexPlatewidth, side='out', rad=10), 'perspex')
                self.add(RoundedRect(mountPlateCentre-offset+V(0,((monitorMountWidth/2)-(perspexPlatewidth/2))), centred=True, width=monitorMountHeight, height=perspexPlatewidth, side='out', rad=10), 'perspex')
                #Holes to hold module to monitor mount plate
                self.add(SquareObjects(mountPlateCentre, 2,2, Bolt(V(0,0), 'M4'), centred=True, width=monitorMountWidth-holeOffset, height=monitorMountHeight-holeOffset))
                self.add(FourObjects(mountPlateCentre-offset, Hole(V(0,0), rad=4.5/2), centred=True, height=monitorMountWidth-holeOffset, width=monitorMountHeight-holeOffset, layers= ['base', 'perspex']))

                

                # Hole through board for cables - also used to make mounting board
                self.add(RoundedRect(mountPlateCentre-offset, centred=True, width=monitorMountHeight, height=monitorMountWidth, side='out', rad=10), ['base', 'paper', 'perspex'])


                # Holes for mounting 12v-19v DC-DC converter
                self.add(SquareObjects(dcDcConverterCentre, 2 ,2, Bolt(V(0,0), 'M3', clearance_layers=[]), centred=True, width=dcDcConverterWidth, height=dcDcConverterHeight))

# Perspex stand off for power 
                self.add(SquareObjects(mountPlateCentre, 2,6, Hole(V(0,0), rad=3.5/2), centred=True, width=10, height=50), 'perspex')
                self.add(SquareObjects(mountPlateCentre, 2,6, Hole(V(0,0), rad=5.5/2), centred=True, width=10, height=50), 'perspex')
                self.add(Rect(V(0,0), centred=True, width = monitorWidth, height = monitorHeight), 'paper')

# creates a means of constraining angles by cutting a curved slot around pos in slot_layer, and a hole for an allen bolt in bolt_layer
class AngleConstraint(Part):
        def __init__(self, pos, rad, angle, head, slot_layer, bolt_layer, **config):
                self.init(config)
                assert head in milling.bolts
                bolt = milling.bolts[head]
                if 'start_angle' in config:
                        startangle = config['startangle']
                else:
                        startangle = 0
                self.translate(pos)
                
                d=(bolt['allen']['head_d']+0.7)
                e = d-3
                n = math.floor(float(e)/2.2)
                step = float(d)/n
                for i in range(0,int(n)):
                        self.add(RoundedArc(V(0,0), rad, 
                                d-i*step, 
                                angle, startangle=startangle, 
                                z1=-bolt['allen']['head_l']-0.8, side='in'
                        ), slot_layer)
                self.add(Hole(V(0,rad), rad=bolt['tap']/2), bolt_layer)

class AngleBracket(Part):
        def __init__(self, pos, bracket_type, mode, **config):
                self.init(config)
                self.translate(pos)
                data={
                        'B&Q_100mm_bracket':{'thickness':6, 'width':20.7, 'inner_length':94, 'outer_length':100, 'hole_from_inside':20.5, 'hole_spacing':30, 'num_holes':3},
                }
                assert bracket_type in data
                d = data[bracket_type]
                fe = 0
                if 'clearance_layers' in config:
                        clearance_layers = config['clearance_layers']
                else:
                        clearance_layers = []
                if 'recess_layer' in config:
                        recess_layers = config['recess_layer']
                else:
                        recess_layers = []
                if 'insert_layer' in config:
                        insert_layer = config['insert_layer']
                else:
                        insert_layer = []
                if 'bolt' in config:
                        bolt = config['bolt']
                else:
                        bolt = 'M4'
                
                top_thickness = d['outer_length'] - d['inner_length']
                # centre is top side of centre
                if mode=='through':
                        self.add(Rect(V(0, -top_thickness/2), centred = True, width = d['width'] + 1, height = d['thickness'] +1, side='in'), clearance_layers)
                        # add a recess for the inside of the bend
                        self.add(Rect(V(0, -2-top_thickness), centred = True, width = d['width'] + 1, height = 4, side='in', z1=-4), clearance_layers) 
                if mode=='through' or mode=='top':
                        self.add(LineObjects(V(0, -top_thickness - d['hole_from_inside']), V(0, -top_thickness - d['hole_from_inside'] - d['hole_spacing'] * (d['num_holes']-1)), 0, d['num_holes'], Bolt(V(0,0), bolt, clearance_layers = clearance_layers, insert_layer = insert_layer )))
                if mode == 'recess_through':
                        if 'through_thickness' in config:
                                if config['through_thickness']=='full':
                                        fe = d['thickness']
                                else:
                                        fe = config['through_thickness']
                        else:
                                raise ValueError('Angle bracket needs through_thickness to be set in recess_through mode')
                                
                        if 'recess_depth' in config:
                                recess_depth =  -config['recess_depth']
                        else:
                                recess_depth = False
                        self.add(LineObjects(V(0, -top_thickness - d['hole_from_inside']+fe), V(0, -top_thickness - d['hole_from_inside'] - d['hole_spacing'] * (d['num_holes']-1)+fe), 0,  d['num_holes'], Bolt(V(0,0), bolt, clearance_layers = clearance_layers, insert_layer=[])))
                        self.add(Rect(V(-d['width']/2-0.5, 0), tr = V(d['width']/2+0.5, -d['outer_length']+fe), partial_fill = d['width']/2-1, z1= recess_depth, side='in'), recess_layers)
        
class PipeClamp(Part):
        def __init__(self,pos, clamp_type, **config):
                self.init(config)
                self.translate(pos)
                data = {
                        'stauff763.5PP':{'D1':63.5, 'L1':121, 'L2':94, 'H':93, 'S':0.8, 'W':30, 'bolt':'M6'}, 
                        'stauff650.8PP':{'D1':50.8, 'L1':86, 'L2':66, 'H':66, 'S':0.8, 'W':30, 'bolt':'M6'}, 
                        'stauff538PP':{'D1':38, 'L1':71, 'L2':52, 'H':58, 'S':0.8, 'W':30, 'bolt':'M6'}, 
                        'stauff325PP':{'D1':25, 'L1':50, 'L2':33, 'H':36, 'S':0.6, 'W':30, 'bolt':'M6'}, 
                        'stauff319PP':{'D1':19, 'L1':50, 'L2':33, 'H':36, 'S':0.6, 'W':30, 'bolt':'M6'}, 
                        'stauff216PP':{'D1':16, 'L1':42, 'L2':26, 'H':33, 'S':0.6, 'W':30, 'bolt':'M6'}, 
                        'stauff212.7PP':{'D1':12.7, 'L1':42, 'L2':26, 'H':33, 'S':0.6, 'W':30, 'bolt':'M6'}, 
                        'stauff109.5APP':{'D1':9.5, 'L1':37, 'L2':20, 'H':27, 'S':0.4, 'W':30, 'bolt':'M6'}, 
                }
                assert clamp_type in data
                if 'insert_layer' in config:
                        insert_layer = config['insert_layer']
                else:
                        insert_layer = []
                if 'thread_layer' in config:
                        thread_layer = config['thread_layer']
                else:
                        thread_layer = []
                if 'clearance_layers' in config:
                        clearance_layers = config['clearance_layers']
                else:
                        clearance_layers = []
                head_layer = '_pipeclamp'

                d = data[clamp_type]
                self.add_border(RoundedRect(V(0,0), centred=True, width=d['L1'], height=d['W'], rad=d['W']/2))
                self.thickness = d['H']
                self.zoffset = d['H']
                self.layer = '_pipeclamp'
                self.name = '_pipeclamp_'+clamp_type
                #hole=self.add(Circle(V(0,0), rad=20, z0=0, z1=-d['W']))
                hole=self.add(Circle(V(0,0), rad=d['D1']/2, z0=d['W'], z1=-d['W']))
                hole.rotate3D(V(0,0,0), [90,0,0]) 
                hole.translate3D(V(0,0,-d['H']/2))
                self.add(Bolt(V(d['L2']/2,0), d['bolt'], clearance_layers=clearance_layers, head_layer=head_layer, insert_layer=insert_layer, thread_layer=thread_layer))
                self.add(Bolt(V(-d['L2']/2,0), d['bolt'], clearance_layers=clearance_layers, head_layer=head_layer, insert_layer=insert_layer, thread_layer=thread_layer))
        def _pre_render(self,config):
                self.get_plane().add_layer('_pipeclamp', 'polyethene', 6, colour='#80ff80')
                
        
class ScreenHolderFixed(Part):
        def __init__(self,pos, plane, name, **config):
                self.init(config)
                self.translate(pos)
                l_types = {'top':'_top', 'mid':'_mid', 'bottom':'_bottom', 'clearance_layers':['perspex', 'paper'], 'insert_layer':'base'}
                if 'layers' in config:
                        layers = config['layers']
                else:
                        layers = {}
                if 'thickness' in config:
                        thickness = config['thickness']
                else:
                        thickness = 6
                if 'material' in config:
                        material = config['materal']
                else:
                        material = 'pvc'
                if 'height' in config:
                        height = config['height']
                else:
                        height = 200
                if 'width' in config:
                        width = config['width']
                else:
                        width = 200
                if 'edge' in config:
                        edge = config['edge']
                else:
                        edge = 40
                if 'bracket' in config:
                        bracket = config['bracket']
                else:
                        bracket = 'B&Q_100mm_bracket'
                rad = edge
                inrad = 6
                edgefrac = 0.8
                for l, lname in l_types.iteritems():
                        if type(lname) is list or lname[0] != '_':
                                if l not in layers:
                                        layers[l] = lname
                        elif l not in layers:
                                plane.add_layer(name = name + lname, material = material, thickness = thickness)
                                layers[l] = name + lname

                plane.add_layer(name = name + '_window', material = 'perspex', thickness = thickness)
                back_border = Path(closed = True, side ='out')
                back_border.add_point(V(-width/2, 0))
                back_border.add_point(PIncurve(V(-width/2, height), radius=rad))
                back_border.add_point(PIncurve(V(width/2, height), radius=rad))
                back_border.add_point(V(width/2, 0))
                self.back = self.add(Part(name = name + '_bottom', layer = name+'_bottom', border = back_border))
                self.front = self.add(Part(name = name + '_top', layer = name+'_top', border = back_border))
                self.mid = self.add(Part(name = name + '_mid', layer = name+'_mid', border = back_border))
                self.window = self.add(Part(name = name + '_window', layer = name+'_window', border =
                        RoundedRect(V(-width/2+edge*edgefrac+0.5, edge*edgefrac+0.5), tr = V(width/2-edge*edgefrac-0.5, height-edge*edgefrac-0.5), rad = inrad)
                ))
                self.front.add(RoundedRect(V(-width/2+edge, edge), tr = V(width/2-edge, height-edge), rad = inrad), layers = [ layers['top'], layers['bottom']])
                self.front.add(RoundedRect(V(-width/2+edge*edgefrac, edge*edgefrac), tr = V(width/2-edge*edgefrac, height-edge*edgefrac), rad = inrad), layers = [ layers['mid']])
                b=self.add(AngleBracket(V(-width/2+edge*edgefrac/2, 0), bracket, 'recess_through', recess_layer = layers['mid'], through_thickness=15, recess_thickness = 'full', clearance_layers=[name+'_top', name+'_bottom'], bolt='M8'))
                b.rotate(V(0,0), 180)
                b=self.add(AngleBracket(V(width/2-edge*edgefrac/2, 0), bracket, 'recess_through', recess_layer = layers['mid'], through_thickness=15, recess_thickness = 'full',  clearance_layers=[name+'_top', name+'_bottom'], bolt='M8'))
                b.rotate(V(0,0), 180)
                self.add(AngleBracket(V(-width/2+edge*edgefrac/2, 0), bracket, 'through', clearance_layers = layers['clearance_layers'], insert_layer=layers['insert_layer'], bolt='M6'))
                self.add(AngleBracket(V(width/2-edge*edgefrac/2, 0), bracket, 'through', clearance_layers = layers['clearance_layers'], insert_layer=layers['insert_layer'], bolt='M6'))

                b  = Bolt( V(0,0), clearance_layers = layers['top'], thread_layer = layers['mid'], insert_layer = [] )
                b2 = Bolt( V(0,0), clearance_layers = layers['bottom'], thread_layer = layers['mid'], insert_layer =[]  )

                self.add( LineObjects( V(-width/2+edge, height - edge/2), V(width/2-edge, height - edge/2), 0, 3, b) )
                self.add( LineObjects( V(-width/2+edge,  edge/2), V(width/2-edge,  edge/2), 0, 3, b) )
                self.add( LineObjects( V(-width/2+edge, height - edge/2), V(width/2-edge, height - edge/2), 10, 2, b2) )
                self.add( LineObjects( V(-width/2+edge,  edge/2), V(width/2-edge,  edge/2), 10, 2, b2) )
                self.add(Bolt( V(-width/2+edge/2,height-3*edge/2), clearance_layers=layers['top'], thread_layer = layers['mid'], insert_layer = []))
                self.add(Bolt( V( width/2-edge/2,height-3*edge/2), clearance_layers=layers['top'], thread_layer = layers['mid'], insert_layer = []))
                self.add(Bolt( V(-width/2+edge/2,height-3*edge/2-10), clearance_layers=layers['top'], thread_layer = layers['mid'], insert_layer = []))
                self.add(Bolt( V( width/2-edge/2,height-3*edge/2-10), clearance_layers=layers['top'], thread_layer = layers['mid'], insert_layer = []))

class ScreenHolderRemovable(Part):
        def __init__(self,pos, plane, name, **config):
                self.init(config)
                self.translate(pos)
                l_types = {'top':'_top', 'mid':'_mid', 'bottom':'_bottom', 'clearance_layers':['perspex', 'paper'], 'insert_layer':'base'}
                if 'layers' in config:
                        layers = config['layers']
                else:
                        layers = {}
                if 'thickness' in config:
                        thickness = config['thickness']
                else:
                        thickness =6
                if 'material' in config:
                        material = config['materal']
                else:
                        material = 'pvc'
                if 'height' in config:
                        height = config['height']
                else:
                        height = 200
                if 'width' in config:
                        width = config['width']
                else:
                        width = 200
                if 'edge' in config:
                        edge = config['edge']
                else:
                        edge = 40
                if 'bracket' in config:
                        bracket = config['bracket']
                else:
                        bracket = 'B&Q_100mm_bracket'
                rad = edge
                inrad = 6
                edgefrac = 0.8
                for l, lname in l_types.iteritems():
                        if type(lname) is list or lname[0] != '_':
                                if l not in layers:
                                        layers[l] = lname
                        elif l not in layers:
                                plane.add_layer(name = name + lname, material = material, thickness = thickness)
                                layers[l] = name + lname
                back_border = Path(closed = True, side ='out')
                back_border.add_point(V(-width/2, 0))
                back_border.add_point(PIncurve(V(-width/2, height), radius=rad))
                back_border.add_point(PIncurve(V(width/2, height), radius=rad))
                back_border.add_point(V(width/2, 0))
                self.back = self.add(Part(name = name + '_bottom', layer = name+'_bottom', border = back_border))


                front_border = Path(closed = True, side ='out')
                front_border.add_point(V(-width/2, 0))
                front_border.add_point(V(-width/2, height-edge-inrad))
                front_border.add_point(V(-width/2+edge, height-edge-inrad))
                front_border.add_point(PIncurve(V(-width/2+edge, edge), radius = inrad))
                front_border.add_point(PIncurve(V( width/2-edge, edge), radius = inrad))
                front_border.add_point(V( width/2-edge, height-edge-inrad))
                front_border.add_point(V( width/2, height-edge-inrad))
                front_border.add_point(V(width/2, 0))
                self.front = self.add(Part(name = name + '_top', layer = name+'_top', border = front_border))

                front_top_border = Path(closed = True, side ='out')
                front_top_border.add_point(V(-width/2, height-edge-inrad))
                front_top_border.add_point(V(-width/2+edge, height-edge-inrad))
                front_top_border.add_point(PIncurve(V(-width/2+edge, height-edge), radius = inrad))
                front_top_border.add_point(PIncurve(V(width/2-edge, height-edge), radius = inrad))
                front_top_border.add_point(V(width/2-edge, height-edge-inrad))
                front_top_border.add_point(V(width/2, height-edge-inrad))
                front_top_border.add_point(PIncurve(V(width/2, height), radius = rad))
                front_top_border.add_point(PIncurve(V(-width/2, height), radius = rad))
                self.front_top = self.add(Part(name = name + '_top_top', layer = name+'_top', border = front_top_border))


                mid_border = Path(closed = True, side ='out')
                mid_border.add_point(V(-width/2, 0))
                mid_border.add_point(V(-width/2, height-edge-inrad))
                mid_border.add_point(V(-width/2+edge*edgefrac, height-edge-inrad))
                mid_border.add_point(PSharp(V(-width/2+edge*edgefrac, edge*edgefrac), radius = inrad))
                mid_border.add_point(PSharp(V( width/2-edge*edgefrac, edge*edgefrac), radius = inrad))
                mid_border.add_point(V( width/2-edge*edgefrac, height-edge-inrad))
                mid_border.add_point(V( width/2, height-edge-inrad))
                mid_border.add_point(V(width/2, 0))
                self.mid = self.add(Part(name = name + '_mid', layer = name+'_mid', border = mid_border))


                mid_inner_border = Path(closed = True, side ='out')
                mid_inner_border.add_point(V(-width/2, height-edge-inrad))
                mid_inner_border.add_point(V(-width/2+edge*edgefrac+1, height-edge-inrad))
                mid_inner_border.add_point(PIncurve(V(-width/2+edge*edgefrac+1, edge*edgefrac+1), radius = inrad))
                mid_inner_border.add_point(PIncurve(V( width/2-edge*edgefrac-1, edge*edgefrac+1), radius = inrad))
                mid_inner_border.add_point(V(width/2-edge*edgefrac-1, height-edge-inrad))
                mid_inner_border.add_point(V(width/2, height-edge-inrad))
                mid_inner_border.add_point(PIncurve(V(width/2, height), radius = rad))
                mid_inner_border.add_point(PIncurve(V(-width/2, height), radius = rad))
                self.mid_inner = self.add(Part(name = name + '_mid_inner', layer = name+'_mid', border = mid_inner_border))

                self.front.add(RoundedRect(V(-width/2+edge, edge), tr = V(width/2-edge, height-edge), rad = inrad), layers = [ layers['mid'], layers['bottom']])

                b=self.add(AngleBracket(V(-width/2+edge*edgefrac/2, 0), bracket, 'recess_through', recess_layer = layers['mid'], through_thickness=15, recess_thickness = 'full', clearance_layers=[name+'_top', name+'_bottom'], bolt='M8'))
                b.rotate(V(0,0), 180)
                b=self.add(AngleBracket(V(width/2-edge*edgefrac/2, 0), bracket, 'recess_through', recess_layer = layers['mid'], through_thickness=15, recess_thickness = 'full',  clearance_layers=[name+'_top', name+'_bottom'], bolt='M8'))
                b.rotate(V(0,0), 180)
                self.add(AngleBracket(V(-width/2+edge*edgefrac/2, 0), bracket, 'through', clearance_layers = layers['clearance_layers'], insert_layer=layers['insert_layer'], bolt='M6'))
                self.add(AngleBracket(V(width/2-edge*edgefrac/2, 0), bracket, 'through', clearance_layers = layers['clearance_layers'], insert_layer=layers['insert_layer'], bolt='M6'))

                b = Bolt(V(0,0), clearance_layers=layers['top'], thread_layer = layers['mid'], insert_layer = [])
                b2 = Bolt(V(0,0), clearance_layers=layers['bottom'], thread_layer = layers['mid'], insert_layer = [])

                self.add(LineObjects( V(-width/2+edge, height - edge/2), V(width/2-edge, height - edge/2), 0, 3, b))
                self.add(LineObjects( V(-width/2+edge,  edge/2), V(width/2-edge,  edge/4), 0, 3, b))

                self.add(LineObjects( V(-width/2+edge,  edge/2), V(width/2-edge,  edge/4), 10, 2, b2))
                self.add(Bolt( V(-width/2+edge/2,height-3*edge/2), clearance_layers=layers['top'], thread_layer = layers['mid'], insert_layer = []))
                self.add(Bolt( V( width/2-edge/2,height-3*edge/2), clearance_layers=layers['top'], thread_layer = layers['mid'], insert_layer = []))
                self.add(Bolt( V(-width/2+edge/2,height-3*edge/2-10), clearance_layers=layers['top'], thread_layer = layers['mid'], insert_layer = []))
                self.add(Bolt( V( width/2-edge/2,height-3*edge/2-10), clearance_layers=layers['top'], thread_layer = layers['mid'], insert_layer = []))

class LightSwitch(Part):
        def __init__(self, pos, switch_type, layers, **config):
                self.init(config)
                self.translate(pos)
                data={
                        'single':{'box_width':79, 'box_height': 79, 'screw_sep':60.3, 'toungue_edge':6, 'width':86, "height":86},
                        'double':{'box_width':140, 'box_height': 79, 'screw_sep':120.6, 'toungue_edge':6, 'width':146, "height":86},
                }
                assert( switch_type in data)
                d=data[switch_type]
                
                if('cutout' in layers):
                        cutout=Path(closed=True, side='in')
                        cutout.add_point(PIncurve(V(-d['box_width']/2, d['box_height']/2), radius = 2))
                        cutout.add_point(PIncurve(V( d['box_width']/2, d['box_height']/2), radius = 2))
                        cutout.add_point(PIncurve(V( d['box_width']/2, d['toungue_edge']), radius = 2))
                        cutout.add_point(POutcurve(V( d['screw_sep']/2, 0), radius = d['toungue_edge']))
                        cutout.add_point(PIncurve(V( d['box_width']/2, -d['toungue_edge']), radius = 2))
                        
                        cutout.add_point(PIncurve(V( d['box_width']/2, -d['box_height']/2), radius = 2))
                        cutout.add_point(PIncurve(V(-d['box_width']/2, -d['box_height']/2), radius = 2))

                        cutout.add_point(PIncurve(V( -d['box_width']/2, -d['toungue_edge']), radius = 2))
                        cutout.add_point(POutcurve(V( -d['screw_sep']/2, 0), radius = d['toungue_edge']))
                        cutout.add_point(PIncurve(V( -d['box_width']/2, d['toungue_edge']), radius = 2))
                        self.add(cutout, layers['cutout'])
                        self.add(Insert(V(-d['screw_sep']/2,0), 'M3.5', layers['cutout']))
                        self.add(Insert(V(d['screw_sep']/2,0), 'M3.5', layers['cutout']))
                if('clearance' in layers):
                        self.add(Rect(V(0,0), width = d['box_width'], height = d['box_height'], centred=True), layers['clearance'])
                if('part' in layers):
                        self.switch=self.add(Part(name="switch", layer=layers['part'], border=Rect(V(0,0), width=d['width'], height=d['height'], centred=True)))
                        self.switch.add(Hole(V(-d['screw_sep']/2,0),rad=4/2))
                        self.switch.add(Hole(V( d['screw_sep']/2,0),rad=4/2))
                        if('num_switches' in config):
                                num_switches = config['num_switches']
                        else:
                                num_switches = 1
                        switch_spacing = d['screw_sep']/(num_switches+1)
                        but_width = 18
                        but_height = 36
                        for i in range(0,num_switches):
                                self.add(Part(subpart=True, layer=layers['part'], border=Rect(V(switch_spacing*(-float(num_switches)/2+i),0), width=but_width, height = but_height, centred=True), zoffset=3, colour="#808080"))

class LED5050(Pathgroup):
        def __init__(self, pos, thickness, **config):
                self.init(config)
                self.translate(pos)
		self.add(Hole(V(0,0), rad=11.0/2, z1=-thickness+6.4))
                self.add(Hole(V(0,0), rad=10.2/2))
#                self.add(Hole(V(0,0), rad=15.0/2, z1=-thickness+6.4))
 #               self.add(Hole(V(0,0), rad=21.0/2, z1=-thickness+6.4))
  #              self.add(Hole(V(0,0), rad=25.0/2, z1=-thickness+6.4))

class Magnetometer(Part):
	def __init__(self, pos, mag_type, layer, **config):
		self.init(config)
		self.translate(pos)
		data={
			'HMC5883L':{
				'bolt_spacing':8.3,
                		'bolt_y':7.3-3.3/2,
                		'solder_y': -8,
                		'solder_width' :2.54*5,
				'width':14.5,
				'height':20,
				'cutoutCentre':V(0,-1.5),
				'countersink_depth':3,
			}
		}
		assert( mag_type in data)
		d= data[mag_type]
		if 'countersink_depth' in config:
			if config['countersink_depth'] is True:
				countersink_depth = d['countersink_depth']
			else:
				countersink_depth = config['countersink_depth']
		else:
			countersink_depth = False
		if 'hole_depth' in config:
			hole_depth=-config['hole_depth'] - countersink_depth
		else:
			hole_depth=False
                self.add(Hole(V(d['bolt_spacing']/2, d['bolt_y']), rad=2.5/2, z1=hole_depth), layer)
                self.add(Hole(V(-d['bolt_spacing']/2, d['bolt_y']), rad=2.5/2, z1=hole_depth), layer)
                self.add(RoundedRect(V(0, d['solder_y']), centred=True, width = d['solder_width'], height=3.3, z1=- countersink_depth-2, side='in'), layer)
		if countersink_depth:
			self.add(Rect(d['cutoutCentre'], centred=True, width = d['width'], height=d['height'], z1=-countersink_depth, partial_fill = min(d['width'], d['height'])/2)) 
