#!/usr/bin/python

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



from minivec import *
from path import *
from shapes import *
from parts import *
from boxes import *
from font import *
from dxf import *
#import importlib
from optparse import OptionParser
import sys
import Milling
import pickle


class CamCam:
	def __init__(self):
		self.planes=[]
	def add_plane(self,plane):
	#	print plane.obType
		if hasattr(plane,'obType') and plane.obType=='Plane':#type(plane) is Plane:
			self.planes.append(plane)
			return plane
		else:
			print "Tring to add a non-plane to camcam"

	def render(self, mode,config):
		modeconfig=milling.mode_config[mode]
		if modeconfig['overview']:
			out=''
			for plane in self.planes:
				plane.render_all(mode,config)
				out+=plane.out
		 	f=open("Overview_"+mode+".svg",'w')
			f.write(modeconfig['prefix'] + out + modeconfig['postfix'])
			f.close()

		else:
			for plane in self.planes:
				plane.render_all(mode,config)
	def render_layout( self, mode, layout_file, config):
		modeconfig=milling.mode_config[mode]
		parts={}
		out = []
		config['layout'] = True
		for plane in self.planes:
			for part in plane.getParts():
				parts[part.name] = [plane, part]
		l = open(layout_file, 'r')
		sheets = pickle.load(l)
		print sheets
		for sheet in sheets['sheets']:
			out = {}
			for p in sheets['sheets'][sheet]:
				(plane, part) = parts[p['name']]
				tconfig = config
				tconfig['transformations'] = [{'rotate':[ V(p['startcentre'][0],p['startcentre'][1]), p['rotate']], 'translate':V(p['translate'][0], p['translate'][1] ) }]
				plane.render_part(part, mode, tconfig)
				if type(plane.lay_out) is dict:
					for i in plane.lay_out:
						if i not in out:
							out[i]=''
						out[i] += plane.lay_out[i]
				else:
					print "plane.lay_out is not a dict"
			if 'suffix' not in modeconfig:
				modeconfig['suffix'] = ''
			for i in out:
				f=open(self.sanitise_filename(sheet+ i + modeconfig['file_suffix']), 'w')
				f.write(modeconfig['prefix'] + out[i] + modeconfig['postfix'])
		


	def sanitise_filename(self,filename):
                return "".join(x for x in filename if x.isalnum() or x in '-._')

	def listparts(self):
		 for plane in self.planes:
                                plane.list_all()
	def get_bom(self):
		ret=[]
		for plane in self.planes:
			ret.extend(plane.get_bom())
		lookup={}
		ret2=[]
		c=0
		for l in ret:
			if type(l) is BOM_part:
				if str(l.part_number)+str(l.length) in lookup:
					ret2[lookup[str(l.part_number)+str(l.length)]].number+=l.number
				else:
					ret2.append(l)
					lookup[str(l.part_number)+str(l.length)]=c
					c+=1
			else:
				ret2.append(l)
				c+=1
		for l in ret2:
			print l
camcam = CamCam()
milling = Milling.Milling()
parser = OptionParser()
modes = ','.join(milling.mode_config.keys())

parser.add_option("-m", "--mode", dest="mode",
                  help="mode the output should be in. Can be one of "+modes, metavar="MODE")
parser.add_option("-l", "--list",
                  action="store_true", dest="listparts", default=False,
                  help="list all parts")
parser.add_option("-b", "--sep-border",
                  action="store_true", dest="sep_border", default=False,
                  help="Create a separate file for the border")
parser.add_option("-B", "--bom",
                  action="store_true", dest="bom", default=False,
                  help="Print Bill of Materials")
parser.add_option("-x", "--xreps", dest="repeatx",
                  help="number of times should be repeated in x direction")
parser.add_option("-y", "--yreps", dest="repeaty",
                  help="number of times should be repeated in y direction")
parser.add_option("-X", "--xspacing", dest="xspacing",
                  help="spacing in x direction")
parser.add_option("-Y", "--yspacing", dest="yspacing",
                  help="spacing in x direction")
parser.add_option("-r", "--repeatmode", dest="repeatmode",
                  help="Repeat mode - can be origin - move the origin, regexp - replace all the X and Y coordinates")
parser.add_option('-o', '--options', dest='options',
		  help='options for the code - format var=value;var=value')
parser.add_option('-R', '--rotate', dest='rotate',
		  help='Rotate by angle')
parser.add_option('-M', '--mirror', dest='mirror',
		  action='store_true', help='Mirror in x')
parser.add_option('-Z', '--zbase', dest='zbase',
		  action='store_true', help='set z=0 to bottom of material')
parser.add_option('-z', '--nozbase', dest='zbase',
		  action='store_false', help='set z=0 to top of material (default)')
parser.add_option("-L", "--layout-file", dest="layout_file",
                  help="file for layout")
(options, args) = parser.parse_args()
config={}

camcam.command_args={}
if options.options:
	for pair in options.options.split(';'):
		a=pair.split('=')
		if len(a)>1:
			camcam.command_args[a[0]]=a[1]
config['command_args']=camcam.command_args
if options.xspacing and options.repeatx and options.yspacing and options.repeaty:
	config['xspacing']=options.xspacing
	config['repeatx']=options.repeatx
	config['yspacing']=options.yspacing
	config['repeaty']=options.repeaty
elif options.xspacing and options.repeatx:
	config['xspacing']=options.xspacing
	config['repeatx']=options.repeatx
	config['yspacing']=1
	config['repeaty']=0
elif options.yspacing and options.repeaty:
	config['yspacing']=options.yspacing
	config['repeaty']=options.repeaty
	config['xspacing']=1
	config['repeatx']=1
if options.repeatmode:
	config['repeatmode']=options.repeatmode	
if options.sep_border:
	config['sep_border']=True
else:
	config['sep_border']=False
config['transformations']=[{}]
if options.rotate:
	config['transformations'][0]['rotate'] = [V(0,0), float(options.rotate)]
if options.mirror:
	config['transformations'][0]['mirror'] = [V(0,0),'x']

if options.zbase:
	config['zbase'] = True
# load all the requested files	
for arg in args:
	execfile(arg)

if options.listparts:
	camcam.listparts()
if options.bom:
	camcam.get_bom()
elif options.layout_file:
	camcam.render_layout(options.mode, options.layout_file, config)
else:
	camcam.render(options.mode,config)

