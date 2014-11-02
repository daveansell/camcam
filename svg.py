from lxml import etree
from path import *
import re

class SVGimport(Pathgroup):
	def __init__(self,pos, filename, paths, **config):
		print paths	
		nsmap = {
		    'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
		    'cc': 'http://web.resource.org/cc/',
		    'svg': 'http://www.w3.org/2000/svg',
		    'dc': 'http://purl.org/dc/elements/1.1/',
		    'xlink': 'http://www.w3.org/1999/xlink',
		    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
		    'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
		}

		self.init(config)
		self.translate(pos)
		with open( filename, 'r') as infile: 
			tree = etree.parse(infile) 
			root = tree.getroot()
		outpaths=[]
		if paths=='all':
			outpaths= tree.xpath('.//svg:path',namespaces=nsmap)
		elif type(paths) is list:
			for path in paths:
				print './/n:path[@id="'+path+'"]'
				outpaths= tree.xpath('.//svg:path[@id="'+path+'"]', namespaces=nsmap)
		elif type(paths) is dict:
			for p in paths.keys():
				outpaths= tree.xpath(".//n:path[@"+path[p]['attrib']+"='"+path[p]['value']+"']", namespaces={'n': "http://www.w3.org/2000/svg"})
		for p in outpaths:
			self.parse_d(p.get('d'))
# at the moment this just treats everything as a line so add lots of points
	def parse_d(self,d):
		outpath=False
		items = re.split('[, ]+', d)
		pos=V(0,0)
		i=0
		while i<len(items):
			if items[i]=='M':
				i+=1
				if outpath!=False and len(outpath.points)>1:
					self.add(outpath)
				outpath = Path()
				while i<len(items) and self.is_number(items[i]):
					pos=V(float(items[i]), -float(items[i+1]))
					outpath.add_point(pos)
					i+=2
			elif items[i]=='L':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos=V(float(items[i]), -float(items[i+1]))
					outpath.add_point(pos)
					i+=2
			elif items[i]=='A':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos=V(float(items[i+5]), -float(items[i+6]))
					outpath.add_point(pos)
					i+=7
			elif items[i]=='C':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos=V(float(items[i+4]), -float(items[i+5]))
					outpath.add_point(pos)
					i+=6	
			elif items[i]=='S':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos=V(float(items[i+2]), -float(items[i+3]))
					outpath.add_point(pos)
					i+=4	
			elif items[i]=='Q':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos=V(float(items[i+2]), -float(items[i+3]))
					outpath.add_point(pos)
					i+=4	
			elif items[i]=='T':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos=V(float(items[i]), -float(items[i+1]))
					outpath.add_point(pos)
					i+=2	
			elif items[i]=='H':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos=V(float(items[i]), pos[1])
					outpath.add_point(pos)
					i+=1
			elif items[i]=='V':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos=V(pos[0],float(items[i]))
					outpath.add_point(pos)
					i+=1
			if items[i]=='m':
				if outpath!=False and len(outpath.points)>1:
					self.add(outpath)
				outpath = Path()
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos+=V(float(items[i]), -float(items[i+1]))
					outpath.add_point(pos)
					i+=2
			elif items[i]=='l':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos+=V(float(items[i]), -float(items[i+1]))
					outpath.add_point(pos)
					i+=2
			elif items[i]=='a':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos+=V(float(items[i+5]), -float(items[i+6]))
					outpath.add_point(pos)
					i+=7
			elif items[i]=='c':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos+=V(float(items[i+4]), -float(items[i+5]))
					outpath.add_point(pos)
					i+=6
			elif items[i]=='s':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos=V(float(items[i+2]), -float(items[i+3]))
					outpath.add_point(pos)
					i+=4	
			elif items[i]=='q':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos=V(float(items[i+2]), -float(items[i+3]))
					outpath.add_point(pos)
					i+=4
			elif items[i]=='t':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos=V(float(items[i]), -float(items[i+1]))
					outpath.add_point(pos)
					i+=2
			elif items[i]=='h':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos+=V(float(items[i]), 0)
					outpath.add_point(pos)
					i+=1
			elif items[i]=='v':
				i+=1
				while i<len(items) and self.is_number(items[i]):
					pos+=V(0, -float(items[0]))
					outpath.add_point(pos)
					i+=1
			elif items[i]=='z' or items[i]=='Z':
				i+=1
				outpath.closed=True
				pos=outpath.points[0].pos
			else:
				i+=1
		if outpath!=False and len(outpath.points)>0:
			self.add(outpath)
	def is_number(self,s):
	    try:
	        float(s)
	        return True
	    except ValueError:
	        return False

#s=SVGimport(1, '/home/dave/cnc/modules/davecad1/beam_bridge/beam-bridge-river.svg','all')
