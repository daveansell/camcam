#!/usr/bin/python
from path import *
from shapes import *
import importlib
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

	def render(self, mode):
		modeconfig=milling.mode_config[mode]
		if modeconfig['overview']:
			out=''
			for plane in self.planes:
				plane.render_all(mode)
				out+=plane.out
		 	f=open("Overview_"+mode+".svg",'w')
			f.write(modeconfig['prefix'] + out + modeconfig['postfix'])
			f.close()

		else:
			for plane in self.planes:
				plane.render_all(mode)
camcam = CamCam()
milling = Milling.Milling()
parser = OptionParser()
modes = ','.join(milling.mode_config.keys())

parser.add_option("-m", "--mode", dest="mode",
                  help="mode the output should be in. Can be one of "+modes, metavar="MODE")
(options, args) = parser.parse_args()
print options.mode
print args
for arg in args:
	print arg
	execfile(arg)

camcam.render(options.mode)

