from lxml import etree
from path import *
import re


class SVGpoints(list):
	""" This takes an inkscape svg file and looks for circles (inkscape produces paths with circle attributes), and returns the centre of all those circles as a list of poitns.
You can calibrate these with a rectangle or a named circle of known width and height or radius"""
	def __init__(self,pos, filename, **config):
		nsmap = {
		    'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
		    'cc': 'http://web.resource.org/cc/',
		    'svg': 'http://www.w3.org/2000/svg',
		    'dc': 'http://purl.org/dc/elements/1.1/',
		    'xlink': 'http://www.w3.org/1999/xlink',
		    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
		    'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
		}
		if 'cal_path' in config:
			self.cal_path = config['cal_path']
		else:
			self.cal_path = False

		if 'cal_rad' in config:
			self.cal_rad = config['cal_rad']
			self.cal_circ = True
		else:
			self.cal_circ = False

		if 'cal_width' in config and 'cal_height' in config:
			self.cal_rect = True
			self.cal_width = config['cal_width']
			self.cal_height = config['cal_height']
		else:
			self.cal_rect = False

		if 'p_mm' in config:
			self.scalex = config['ppm']
			self.scaley = config['ppm']

		with open( filename, 'r') as infile: 
			tree = etree.parse(infile) 
			root = tree.getroot()
		paths='all'
		outpaths=[]
		calpaths = False
		scalex = 1
		scaley = 1
		cal_centrex = 0
		cal_centrey = 0			
	
		if self.cal_circ:
			if self.cal_path:
				calpaths= tree.xpath('.//svg:path[@id="'+path+'"]', namespaces=nsmap)
				if len(calpaths):
					assert calpaths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}rx'] == calpaths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}ry']
					scalex = float(self.cal_width) / float(calpaths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}rx'])
					scaley = float(self.cal_height) / float(calpaths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}ry'])
					cal_centrex = float(calpaths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx'])
					cal_centrey = float(calpaths[0].attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cy'])
		elif self.cal_rect:
			if self.cal_path:
				calpaths = tree.xpath('.//svg:rect[@id="'+self.cal_path+'"]', namespaces=nsmap)
			else:
				calpaths = tree.xpath('.//svg:rect',namespaces=nsmap)
			if len(calpaths):
				scalex = float(self.cal_width) / float(calpaths[0].attrib['width'])
				scaley = float(self.cal_height) / float(calpaths[0].attrib['height'])
				cal_centrex = float(calpaths[0].attrib['x'])+float(calpaths[0].attrib['width'])/2
				cal_centrey = float(calpaths[0].attrib['y'])+ float(calpaths[0].attrib['height'])/2


		if paths=='all':
			outpaths= tree.xpath('.//svg:path',namespaces=nsmap)
		elif type(paths) is list:
			for path in paths:
				outpaths= tree.xpath('.//svg:path[@id="'+path+'"]', namespaces=nsmap)
		elif type(paths) is dict:
			for p in paths.keys():
				outpaths= tree.xpath(".//n:path[@"+path[p]['attrib']+"='"+path[p]['value']+"']", namespaces={'n': "http://www.w3.org/2000/svg"})
		for p in outpaths:
			if 'transform' in p.attrib:
				m = re.search('translate\(([-\d\.]*),([-\d\.]*)\)', p.attrib['transform'])
				off = V(float(m.group(1)), float(m.group(2)))
			else:
				off=V(0,0)
			cal = V(cal_centrex, cal_centrey)
			pos = V(float(p.attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx']), float(p.attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cy']))
			pos+=off
			pos -=cal

			pos = V(pos[0]*scalex, -pos[1]*scaley)			

			self.append(pos)
#V( (float(p.attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx'])+off[0]-cal_centrex)*scalex, 
#					(float(p.attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cy'])+off[1]-cal_centrex)*scaley))
# at the moment this just treats everything as a line so add lots of points
	def is_number(self,s):
	    try:
	        float(s)
	        return True
	    except ValueError:
	        return False

#s=SVGimport(1, '/home/dave/cnc/modules/davecad1/beam_bridge/beam-bridge-river.svg','all')
