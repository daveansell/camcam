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



from path import *
from shapes import *
from parts import *
from boxes import *
#import importlib
from optparse import OptionParser
import sys
import Milling
import pygame
import planes
import kivy
kivy.require('1.0.6')

from glob import glob
from random import randint
from os.path import join, dirname
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty
# FIXME this shouldn't be necessary
from kivy.core.window import Window
from kivy.graphics import *# Color, Rectangle, Canvas
from  kivy.uix.label import *

class KvPart(Scatter):
	def draw(self, part):
		print "drawp pwart "+str(part.name)
		if part.border:
			ccpoints = part.border.polygonise()
			self.canvas.add(Color(1,0,0,0.05))
			print part.border.centre
			print (part.border.boundingBox['tr'][0]-part.border.boundingBox['bl'][0],part.border.boundingBox['tr'][1]-part.border.boundingBox['bl'][1])
			width = part.border.boundingBox['tr'][0]-part.border.boundingBox['bl'][0]
			height = part.border.boundingBox['tr'][1]-part.border.boundingBox['bl'][1]
			centrex = part.border.centre[0]
			centrey = part.border.centre[1]
			self.canvas.add(Rectangle(pos=(0,0), size=(width, height)))
			self.canvas.add(Color(1,0,0))
			self.center = ( centrex , centrey)
			self.size = (part.border.boundingBox['tr'][0]-part.border.boundingBox['bl'][0],part.border.boundingBox['tr'][1]-part.border.boundingBox['bl'][1])
			kvpoints=[]
			for p in ccpoints:
				kvpoints.append(p[0] - centrex + width/2)
				kvpoints.append(p[1] - centrey + height/2)
			if part.border.closed:
				kvpoints.append(ccpoints[0][0] -centrex+width/2)
				kvpoints.append(ccpoints[0][1] -centrey+height/2)
			self.canvas.add(Line(points=kvpoints, width=1))
#			kvpoints=[]
#			indices = []
#			for p in ccpoints:
#				kvpoints.append([p[0], p[1], 0,0])
#				indices.append(p)
#			print kvpoints
#			self.canvas.add(Mesh(verticies=kvpoints, indices=indices, mode='line_loop'))
			self.canvas.add(Color(0,0,0))
#			self.canvas.add(Label(text=part.name, x=self.center_x, y=self.center_y, halign='center'))
		self.do_rotation = True
		self.do_scale = False
		self.do_translation = True

class RenderPart:
	def __init__(self):
		self.offset=V(0,0)
		self.rotate=0
		self.borders=[]
		self.resolution = 2

	def set_part(self,part):
		part.border
	

class CamCam(App):
	planes=[]
	def add_plane(self,plane):
	#	print plane.obType
		if hasattr(plane,'obType') and plane.obType=='Plane':#type(plane) is Plane:
			self.planes.append(plane)
			return plane
		else:
			print "Tring to add a non-plane to camcam"
    	def build(self): 
		print "BUILD"
        # the root is created in pictures.kv
        	root = self.root

        # get any files into images directory
		print self
		print root
		for plane in self.planes:
			print "plane="+str(plane)
			for part in plane.getParts():
				for i in range(0, part.number):
					picture = KvPart()#rotation=randint(-30,30))
					picture.draw(part)
					root.add_widget(picture)
    
   	def on_pause(self):
        	return True


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
(options, args) = parser.parse_args()
config={}

camcam.command_args={}
if options.options:
	for pair in options.options.split(';'):
		a=pair.split('=')
		if len(a)>1:
			camcam.command_args[a[0]]=a[1]
config['command_args']=camcam.command_args
# load all the requested files	
for arg in args:
	execfile(arg)


if __name__ == '__main__':
  camcam.run()
#camcam.build()

