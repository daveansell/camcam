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
			for l in config['layer_config'].keys():
				task =  config['layer_config'][l]
				if task=='clearance':
					self.add(Hole(V(0,0), rad=19/2), layers=l)
				if task=='doubleflat':
					self.add(DoubleFlat(V(0,0),13.6/2, 12.9/2, side='in'), layers=l)
				if task=='minimal':
					self.add(Hole(V(0,0), rad=18/2, z1=-2 ), layers=l)
					self.add(Hole(V(0,0), rad=14/2 ), layers=l)
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
		if 'layer_config' not in config or type(config['layer_config']) is not dict:
			config['layer_config']={'base':'stepper_mount', 'perspex':'shaft'}
		if 'knob_type' not in config:
			config['knob_type'] = 'stepper'

		if config['knob_type'] == 'stepper':
			for l in config['layer_config'].keys():
				task =  config['layer_config'][l]
				if task=='stepper_mount':
					print self.add(Stepper(pos, 'NEMA1.7', mode='stepper', layer=l))
				if task=='shaft':
					print self.add(Stepper(pos, 'NEMA1.7', mode='justshaft', layer=l))

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
		bolt_conf={'clearance_layers':['pibarn'], 'length':50}
		print self.add(RepeatLine(pos+V(-x_units/2*spacing, -y_units/2*spacing), pos+V(x_units/2*spacing, -y_units/2*spacing), x_units+1, Bolt, bolt_conf)).paths
		self.add(RepeatLine(pos+V(x_units/2*spacing, (-y_units/2+1)*spacing), pos+V(x_units/2*spacing, (y_units/2-1)*spacing), y_units-1, Bolt, bolt_conf))
		self.add(RepeatLine(pos+V(x_units/2*spacing, y_units/2*spacing), pos+V(-x_units/2*spacing, y_units/2*spacing), x_units+1, Bolt, bolt_conf))
		self.add(RepeatLine(pos+V(-x_units/2*spacing, (y_units/2-1)*spacing), pos+V(-x_units/2*spacing, (-y_units/2+1)*spacing), y_units-1, Bolt, bolt_conf))
		self.add_border(RoundedRect(pos, centred=True, width=x_units*spacing+15, height=x_units*spacing+15, side='out', rad=8))
		self.add_bom('standoff',4, description='30mm standoff')
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
			},
			'NEMA1.1':{
				'bolt_size':'M4',
				'bolt_sep':23,
				'shaft_diam':5,
				'pilot_diam':22,
				'pilot_depth':2,
			},
			'NEMA1.4':{
				'bolt_size':'M4',
				'bolt_sep':26,
				'shaft_diam':5,
				'pilot_diam':22,
				'pilot_depth':2,
			},
			'NEMA1.7':{
				'bolt_size':'M4',
				'bolt_sep':31,
				'shaft_diam':5,
				'pilot_diam':22,
				'pilot_depth':2,
			},
			'NEMA2.3':{
				'bolt_size':'M5',
				'bolt_sep':47.14,
				'shaft_diam':6.35,
				'pilot_diam':38.1,
				'pilot_depth':1.6,
			},
			'NEMA3.4':{
				'bolt_size':'M5',
				'bolt_sep':69.7,
				'shaft_diam':9,
				'pilot_diam':22,
				'pilot_depth':2,
			},
		}
		self.add(Hole(pos, rad=10))
		d=dat[stepper_type]
		if 'mode' in config and config['mode']=='justshaft':
			self.add(Hole(pos, rad=d['shaft_diam']/2+1),layer)
		else:	
			self.add(Hole(pos+V(d['bolt_sep']/2,d['bolt_sep']/2), rad=milling.bolts[d['bolt_size']]['clearance']/2),layer)
			self.add(Hole(pos+V(d['bolt_sep']/2,-d['bolt_sep']/2), rad=milling.bolts[d['bolt_size']]['clearance']/2),layer)
			self.add(Hole(pos+V(-d['bolt_sep']/2,-d['bolt_sep']/2), rad=milling.bolts[d['bolt_size']]['clearance']/2),layer)
			self.add(Hole(pos+V(-d['bolt_sep']/2,d['bolt_sep']/2), rad=milling.bolts[d['bolt_size']]['clearance']/2),layer)
		
			self.add(Hole(pos, rad=d['shaft_diam']/2+1),layer)
#			self.add(Hole(pos, rad=d['pilot_diam']/2+0.1, z1=-d['pilot_depth']-0.5, partial_fill=d['pilot_diam']/2-1, fill_direction='in'),layer)
#			self.add(Hole(pos, rad=d['pilot_diam']/2+0.1, z1=-d['pilot_depth']-0.5),layer)
			self.add(FilledCircle(pos, rad=d['pilot_diam']/2+0.1, z1=-d['pilot_depth']-0.5),layer)


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
			self.add(Hole(pos, rad=insert['diams'], z1 = insert['depths'], **config), layer)	

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
			'60mm':{'centrerad':58/2,  'hole_off':50/2, 'holeRad':4.5/2},
			'80mm':{'centrerad':92/2, 'centre_limit':78/2, 'hole_off':71.5/2, 'holeRad':4.5/2 },
			'92mm':{'centrerad':104/2, 'centre_limit':90/2, 'hole_off':82.5/2, 'holeRad':4.5/2 },
			'120mm':{'centrerad':132/2, 'centre_limit':118/2, 'hole_off':105/2, 'holeRad':4.5/2 },
			'140mm':{'centrerad':150/2, 'centre_limit':138/2, 'hole_off':124.5/2, 'holeRad':4.5/2 },
			}
		if 'fan_type' in config:
			d=data[config['fan_type']]
		else:
			d=data['120mm']
		if 'centre_limit' in d:
			o = math.sqrt(d['centrerad']**2 - d['centre_limit']**2)
			cutout=self.add(Path(side='in', closed=True))
			cutout.add_point(V(o,d['centre_limit']), 'sharp')
			cutout.add_point(V(0,0), 'aroundcurve', radius=d['centrerad'], direction='ccw')
			cutout.add_point(V(d['centre_limit'],o), 'sharp')
			
			cutout.add_point(V(d['centre_limit'],-o), 'sharp')
			cutout.add_point(V(0,0), 'aroundcurve', radius=d['centrerad'], direction='ccw')
			cutout.add_point(V(o,-d['centre_limit']), 'sharp')

			cutout.add_point(V(-o,-d['centre_limit']), 'sharp')
			cutout.add_point(V(0,0), 'aroundcurve', radius=d['centrerad'], direction='ccw')
			cutout.add_point(V(-d['centre_limit'],-o), 'sharp')

			cutout.add_point(V(-d['centre_limit'],o), 'sharp')
			cutout.add_point(V(0,0), 'aroundcurve', radius=d['centrerad'], direction='ccw')
			cutout.add_point(V(-o,d['centre_limit']), 'sharp')
		else:
			self.add(Hole(V(0,0), rad=d['centrerad']))

		self.add(Hole(V(d['hole_off'],d['hole_off']), d['holeRad']))
		self.add(Hole(-V(d['hole_off'],d['hole_off']), d['holeRad']))
		self.add(Hole(-V(d['hole_off'],-d['hole_off']), d['holeRad']))
		self.add(Hole(V(d['hole_off'],-d['hole_off']), d['holeRad']))

class StepperDriver(Pathgroup):
	def __init__(self, pos, **config):
		self.init(config)
		self.translate(pos)
		print pos
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



class Plate(Part):
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
#		screwConf={layer_config['part']:{'rad':milling.bolts[holeSize]['clearance']/2+0.5}, layer_config['base']:{'rad':milling.bolts[holeSize]['clearance']/2}}
		if holes >0:
			for i in range(0, holes):
				self.add(Bolt(V(holeRad,0), 'M4', 'button', 16, clearance_layers=clearance, insert_layer=layer_config['base'], thread_layer=layer_config['thread'], transform={'rotate':[V(0,0), i*360/holes]}))
#				self.add(Screw(V(d['holeRad'],0), layer_config=screwConf, transform={'rotate':[V(0,0), i*360/d['holes']]}))
		if centreRad >0:
			self.add(Hole(V(0,0), rad=centreRad))
			self.add(Hole(V(0,0), rad=centreRad+2), [layer_config['base']])
			self.add(Hole(V(0,0), rad=centreRad+2), clearance)

class RoundPlate(Plate):
	def __init__(self, pos, plateType, **config):
		self.init(config)
		data={
			'stringplate6':{'rad':28, 'centreRad':4/2, 'holes':6, 'holeRad':19, 'holeSize':'M4'},
			'stringplate3':{'rad':28, 'centreRad':4/2, 'holes':3, 'holeRad':19, 'holeSize':'M4'},
		}
		d=data[plateType]
		self.initPlate(pos, plateType, d['rad'], d['centreRad'], d['holes'], d['holeRad'], d['holeSize'], config)

