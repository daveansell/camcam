#!/usr/bin/python
from path import *
from shapes import *
#import importlib
from optparse import OptionParser
import sys
import Milling

class CamCam:
	def __init__(self):
		self.planes=[]
	def add_plane(self,plane):
		print plane.obType
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
	def listparts(self):
		 for plane in self.planes:
                                plane.list_all()
camcam = CamCam()
milling = Milling.Milling()
parser = OptionParser()
modes = ','.join(milling.mode_config.keys())

parser.add_option("-m", "--mode", dest="mode",
                  help="mode the output should be in. Can be one of "+modes, metavar="MODE")
parser.add_option("-l", "--list",
                  action="store_true", dest="listparts", default=False,
                  help="list all parts")
parser.add_option("-x", "--xreps", dest="repeatx",
                  help="number of times should be repeated in x direction")
parser.add_option("-y", "--yreps", dest="repeaty",
                  help="number of times should be repeated in y direction")
parser.add_option("-X", "--xspacing", dest="xspacing",
                  help="spacing in x direction")
parser.add_option("-Y", "--yspacing", dest="yspacing",
                  help="spacing in x direction")
(options, args) = parser.parse_args()
config={}

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
	
# load all the requested files	
for arg in args:
	execfile(arg)

if options.listparts:
	camcam.listparts()
else:
	camcam.render(options.mode,config)

