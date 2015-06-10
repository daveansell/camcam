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
					self.add(Hole(V(0,0), rad=19/2), layers=l)
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
		if 'name' in config:
			self.name = config['name']
		else:
			self.name = 'PiBarn'
		bolt_conf={'clearance_layers':[config['layer']], 'length':50, 'insert_layer':[], 'underinsert_layer':'base'}

		self.add(RepeatLine(pos+V(-x_units/2*spacing, -y_units/2*spacing), pos+V(x_units/2*spacing, -y_units/2*spacing), x_units+1, Bolt, bolt_conf)).paths
		self.add(RepeatLine(pos+V(x_units/2*spacing, (-y_units/2+1)*spacing), pos+V(x_units/2*spacing, (y_units/2-1)*spacing), y_units-1, Bolt, bolt_conf))
		self.add(RepeatLine(pos+V(x_units/2*spacing, y_units/2*spacing), pos+V(-x_units/2*spacing, y_units/2*spacing), x_units+1, Bolt, bolt_conf))
		self.add(RepeatLine(pos+V(-x_units/2*spacing, (y_units/2-1)*spacing), pos+V(-x_units/2*spacing, (-y_units/2+1)*spacing), y_units-1, Bolt, bolt_conf))
		self.add_border(RoundedRect(pos, centred=True, width=x_units*spacing+15, height=y_units*spacing+15, side='out', rad=8))
		self.add_bom('standoff',4, description='30mm standoff')

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

class LinearRail(Part):
	def __init__(self, start, end, rail_type, **config):
		self.init(config)
		if 'transform' in config:
			del(config['transform'])
		dat={
			'LFS-12-10':{'width':36, 'centre_height':16, 'centre_width':24, 'holespacing_x':50, 'holespacing_y':0, 'bolt_type':'M6'},
			'LFS-12-3':{'width':90, 'centre_height':25, 'centre_width':49, 'holespacing_x':100, 'holespacing_y':75, 'bolt_type':'M6'},
			'LFS-12-2':{'width':62, 'centre_height':25, 'centre_width':12, 'holespacing_x':100, 'holespacing_y':50, 'bolt_type':'M6'},
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
			
			for i in range(0, hole_gaps+1):
				if d['holespacing_y'] ==0:
					self.add(Bolt(start+ parallel *(offsetx+ d['holespacing_x']*i), d['bolt_type'], **config))
				else:
					self.add(Bolt(start+parallel*(offsetx+ d['holespacing_x']*i) + perp * d['holespacing_y'] , d['bolt_type'], **config))
					self.add(Bolt(start+parallel*(offsetx+ d['holespacing_x']*i) - perp * d['holespacing_y'] , d['bolt_type'], **config))
			self.add(Lines([start+perp*d['width']/2, start-perp*d['width']/2, end-perp*d['width']/2, end+perp*d['width']/2], closed=True), 'paper')

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
			'40mm':{'centrerad':38/2,  'hole_off':31.6/2, 'holeRad':4.5/2, 'threadRad':3.3/2},			
			'60mm':{'centrerad':58/2,  'hole_off':50/2, 'holeRad':4.5/2, 'threadRad':3.3/2},
			'80mm':{'centrerad':92/2, 'centre_limit':78/2, 'hole_off':71.5/2, 'holeRad':4.5/2, 'threadRad':3.3/2 },
			'92mm':{'centrerad':104/2, 'centre_limit':90/2, 'hole_off':82.5/2, 'holeRad':4.5/2, 'threadRad':3.3/2 },
			'120mm':{'centrerad':132/2, 'centre_limit':118/2, 'hole_off':105/2, 'holeRad':4.5/2, 'threadRad':3.3/2 },
			'140mm':{'centrerad':150/2, 'centre_limit':138/2, 'hole_off':124.5/2, 'holeRad':4.5/2, 'threadRad':3.3/2 },
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
			if 'base' in layer_config:
				self.add(Hole(V(0,0), rad=centreRad+2), [layer_config['base']])
			if 'clearance' in layer_config:
				self.add(Hole(V(0,0), rad=centreRad+2), layer_config['clearance'])

class RoundPlate(Plate):
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
                        'B101UAN02'  :{'ext_width':230.0, 'ext_height':149.7, 'screen_width':217.0,  'screen_height':135.5 },
                        'B140HAN01.2':{'ext_width':320.4, 'ext_height':188, 'screen_width':309.14, 'screen_height':173.89, 'lug_width':13, 'lug_depth':1, 'lug_height':7, 'toplug_fe':20, 'botlug_fe':35, 'elec_width':223, 'elec_height':12, 'conn_width':30, 'conn_x':115, 'conn_y0':-87, 'conn_y1':-117},
			'B156HAN01.2':{'ext_width':359.5, 'ext_height':223.8, 'screen_width':344.16, 'screen_height':193.59},
                }
		assert monitorType in data
		d = data[monitorType]
		self.d = d
		if 'toplug_fe' in d:
			self.add(Rect(V(d['ext_width']/2- d['toplug_fe'], d['ext_height']/2+d['lug_height']/2), centred=True, width=d['lug_width'], height=d['lug_height'], z1=-d['lug_depth']),base)
			self.add(Rect(V(-d['ext_width']/2+ d['toplug_fe'], d['ext_height']/2+d['lug_height']/2), centred=True, width=d['lug_width'], height=d['lug_height'], z1=-d['lug_depth']), base)
		if 'botlug_fe' in d:
			self.add(Rect(V(d['ext_width']/2- d['botlug_fe'], -d['ext_height']/2 - d['lug_height']/2), centred=True, width=d['lug_width'], height=d['lug_height'], z1=-d['lug_depth']), 'base')
			self.add(Rect(V(-d['ext_width']/2+ d['botlug_fe'], -d['ext_height']/2 - d['lug_height']/2), centred=True, width=d['lug_width'], height=d['lug_height'], z1=-d['lug_depth']), 'base')
		cutout=self.add(Path(closed=True, side='in'), base)
		cutout.add_point(V(d['ext_width']/2, d['ext_height']/2))
		cutout.add_point(V(-d['ext_width']/2, d['ext_height']/2))
		cutout.add_point(V(-d['ext_width']/2, -d['ext_height']/2))
		cutout.add_point(V(-d['elec_width']/2, -d['ext_height']/2))
		cutout.add_point(V(-d['elec_width']/2, -d['ext_height']/2-d['elec_height']))
		cutout.add_point(V(-d['ext_width']/2+d['conn_x']-d['conn_width']/2, -d['ext_height']/2-d['elec_height']))
		cutout.add_point(V(-d['ext_width']/2+d['conn_x']-d['conn_width']/2, d['conn_y1']))
		cutout.add_point(V(-d['ext_width']/2+d['conn_x']+d['conn_width']/2, d['conn_y1']))
		cutout.add_point(V(-d['ext_width']/2+d['conn_x']+d['conn_width']/2, -d['ext_height']/2-d['elec_height']))
		cutout.add_point(V(d['elec_width']/2, -d['ext_height']/2-d['elec_height']))
		cutout.add_point(V(d['elec_width']/2, -d['ext_height']/2))
		cutout.add_point(V(d['ext_width']/2, -d['ext_height']/2))

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
		self.add(RoundedArc(V(0,0), rad, 
			bolt['allen']['head_d']+1.5, 
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
	
