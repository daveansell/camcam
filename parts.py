from path import *
from shapes import *

class Switch(Part):
	def __init__(self,pos, **config):
		self.init(config)
		if 'layer_config' not in config or type(config['layer_config']) is not dict:
			config['layer_config']={'base':'clearance', 'perspex':'doubleflat'}
		if 'switch_type' not in config:
			config['swtich_type'] = 'IWS_small'
		
		if config['switch_type'] == 'IWS_small':
			for l in config['layer_config'].keys():
				task =  config['layer_config'][l]
				if task=='clearance':
					self.add_path(Hole(pos, rad=19/2), layers=l)
				if task=='doubleflat':
					self.add_path(DoubleFlat(pos,rad=13.6/2, flat_rad=12.9/2))
				if task=='minimal':
					self.add_path(Hole(pos, rad=18/2, z1=-2 ), layers=l)
					self.add_path(Hole(pos, rad=14/2 ), layers=l)

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
					self.add_path(Stepper(pos, 'NEMA1.4', mode='stepper'),l)
				if task=='shaft':
					self.add_path(Stepper(pos, 'NEMA1.4', mode='justshaft'),l)

class Stepper(Pathgroup):
	def __init__(self,pos, stepper_type, **config):
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
		d=dat[stepper_type]
		if 'mode' in config and config['mode']=='justshaft':
			self.add_path(Hole(pos, rad=d['shaft_diam']/2+1))
		else:	
			self.add_path(Hole(pos+V(d['bolt_sep']/2,d['bolt_sep']/2), rad=milling.bolts[d['bolt_size']]['clearance']/2))
			self.add_path(Hole(pos+V(d['bolt_sep']/2,-d['bolt_sep']/2), rad=milling.bolts[d['bolt_size']]['clearance']/2))
			self.add_path(Hole(pos+V(-d['bolt_sep']/2,-d['bolt_sep']/2), rad=milling.bolts[d['bolt_size']]['clearance']/2))
			self.add_path(Hole(pos+V(-d['bolt_sep']/2,d['bolt_sep']/2), rad=milling.bolts[d['bolt_size']]['clearance']/2))
		
			self.add_path(Hole(pos, rad=d['shaft_diam']/2+1))
			self.add_path(Hole(pos, rad=d['pilot_diam']/2+0.1, z1=-d['pilot_depth']-0.5, partial_fill=d['pilot_diam']/2, fill_direction='in'))



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
		print d
		self.dims =d
		if mode=='clearance':
			self.add_path(Hole(pos+V(0,d['B']/2), rad = milling.bolts[d['bolt']]['clearance']/2))
			self.add_path(Hole(pos+V(0,-d['B']/2), rad = milling.bolts[d['bolt']]['clearance']/2))
		if mode=='insert':
			self.add_path(Hole(pos+V(0,d['B']/2), rad = milling.inserts[d['bolt']]['diams'], z1= milling.inserts[d['bolt']]['depths']))
			self.add_path(Hole(pos+V(0,-d['B']/2), rad = milling.inserts[d['bolt']]['diams'], z1= milling.inserts[d['bolt']]['depths']))
		if mode=='counterbore':
			self.add_path(Hole(pos+V(0,d['B']/2), rad = milling.bolts[d['bolt']]['clearance']/2))
			self.add_path(Hole(pos+V(0,-d['B']/2), rad = milling.bolts[d['bolt']]['clearance']/2))
			self.add_path(ClearRect(pos, centred=True, width=d['L']+0.4, height=d['W']+0.4, partial_fill=(d['L']+0.4)/2, fill_direction='in'))
	
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
				self.add_path(Hole(pos+V(-d['K']/2, -d['J']/2), milling.bolts[d['s1']]['clearance']/2))
				self.add_path(Hole(pos+V(d['K']/2, -d['J']/2), milling.bolts[d['s1']]['clearance']/2))
				self.add_path(Hole(pos+V(-d['K']/2, d['J']/2), milling.bolts[d['s1']]['clearance']/2))
				self.add_path(Hole(pos+V(d['K']/2, d['J']/2), milling.bolts[d['s1']]['clearance']/2))
	
class Insert(Pathgroup):
	def __init__(self, pos, insert_size, **config):
		"""Standard wood insert at pos"""
		self.init(config)
		if insert_size in milling.inserts:
			if 'insert_type' in config and config['insert_type'] in milling.inserts[insert_size]:
				insert=milling.inserts[insert_size][config['insert_type']]
			else:
				insert=milling.inserts[insert_size]
			self.add_path(Hole(pos, rad=insert['diams'], z1 = insert['depths'], **config))	

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
		for l in modes.keys():
			mode=modes[l]	
			d=dat[cell_type]
			e=(d['l']-d['s'])/2
			print "LOAD CELL"+str(mode)+str(pos)
			if mode=='bottom':
				self.add_path(Hole(pos+V(0,0), rad=milling.bolts[d['h']]['clearance']/2), l)
				if 's2' in d:
					self.add_path(Hole(pos+V((d['s']-d['s2'])/2,0), rad=milling.bolts[d['h']]['clearance'])/2, l)
			if mode=='bottom_counterbore':
				if 'counterbore' in config:
					counterbore = config['counterbore']
					self.add_path(ClearRect(pos+V(d['l']/4-e, d['w']/2), tr=pos+V(-e, -d['w']/2), partial_fill=d['w']/2-1 ),l)
				else:
					counterbore = 0
				self.add_path(Hole(pos+V(0,0), rad=milling.bolts[d['h']]['clearance']/2), l)
				self.add_path(ClearRect(pos+V(d['l']/4-e, d['w']/2+1), tr=pos+V(d['l']-e, -d['w']/2-1)),l)
				if 's2' in d:
					self.add_path(Hole(pos+V((d['s']-d['s2'])/2,0), rad=milling.bolts[d['h']]['clearance']/2), l)
			if mode=='bottom_clear':
				self.add_path(Hole(pos+V(0,0), rad=milling.bolts[d['h']]['clearance']/2), l)
				self.add_path(ClearRect(pos+V(d['l']/4-e, d['w']/2+1), tr=pos+V(d['l']-e, -d['w']/2-1), z1=d['z']),l)
				if 's2' in d:
					self.add_path(Hole(pos+V((d['s']-d['s2'])/2,0), rad=milling.bolts[d['h']]['clearance']/2), l)
			if mode=='top':
				self.add_path(Hole(pos+V(d['s'],0), rad=milling.bolts[d['h']]['clearance']/2), l)
				if 's2' in d:
					self.add_path(Hole(pos+V(d['s']-(d['s']-d['s2'])/2,0), rad=milling.bolts[d['h']]['clearance']/2), l)
				

