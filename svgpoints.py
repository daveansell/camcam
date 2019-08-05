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
		if 'item_type' in config and config['item_type'] is not False:
			item_type = config['item_type']
		else:
			item_type = 'path'		
		if 'match_type' in config:
			match_type = config['match_type']
		else:
			match_type = 'exact'
		with open( filename, 'r') as infile: 
			tree = etree.parse(infile) 
			root = tree.getroot()
		if 'paths' in config:
			paths = config['paths']
		else:
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

		if item_type == 'circle' and paths=='all':
			outpaths= tree.xpath('.//svg:circle',namespaces=nsmap)
		elif paths=='all':
			outpaths= tree.xpath('.//svg:path',namespaces=nsmap)
		elif type(paths) is list:
			outpaths = []
			for path in paths:
				#print path
				if item_type == 'circle':
					if match_type == 'exact':
					 	outpaths += tree.xpath('.//svg:circle[@id="'+path+'"]', namespaces=nsmap)
					else:
						outpaths += tree.xpath('.//svg:circle[starts-with(@id, "'+path+'")]', namespaces=nsmap)#@id="'+path+'"]', namespaces=nsmap)
				else:
					if match_type == 'exact':
						outpaths += tree.xpath('.//svg:path[@id="'+path+'"]', namespaces=nsmap)
					else:
						outpaths += tree.xpath('.//svg:path[starts-with(@id, "'+path+'")]', namespaces=nsmap)#@id="'+path+'"]', namespaces=nsmap)
		elif type(paths) is dict:
			for p in paths.keys():
				outpaths= tree.xpath(".//n:path[@"+path[p]['attrib']+"='"+path[p]['value']+"']", namespaces={'n': "http://www.w3.org/2000/svg"})
		for p in outpaths:
			if 'transform' in p.attrib:
				m = re.search('translate\(([-\d\.]*),([-\d\.]*)\)', p.attrib['transform'])
				if m:
					off = V(float(m.group(1)), float(m.group(2)))
				else:
					off = V(0,0)
			else:
				off=V(0,0)
			cal = V(cal_centrex, cal_centrey)
			pos = False
			if('{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx' in p.attrib):
				pos = V(float(p.attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cx']), float(p.attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}cy']))
			elif('cx' in p.attrib):
				pos = V(float(p.attrib['cx']), float(p.attrib['cy']))
			if pos is not False:
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
