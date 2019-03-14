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
from font import *
#import importlib
from optparse import OptionParser
import sys
import Milling
import kivy
kivy.require('1.0.6')
import json
import transformations
import numpy
import copy

from glob import glob
from random import randint
from os.path import join, dirname
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty
# FIXME this shouldn't be necessary
from kivy.core.window import Window
#from kivy.graphics import *# Color, Rectangle, Canvas
import kivy.graphics
from  kivy.uix.label import *
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from functools import partial
from kivy.properties import NumericProperty


class KvSheet(Scatter):
	deleted = False
	def draw(self, bl, tr):
		self.bl = bl
		self.tr = tr
		self.part = None
		self.linecolour = kivy.graphics.Color(0,0,1)
		self.back_colour = kivy.graphics.Color(0,0,1,0.05)
		self.canvas.add(self.linecolour)
		self.canvas.add(kivy.graphics.Line(rectangle=(bl[0], bl[1], tr[0], tr[1]), width=2))
                self.canvas.add( self.back_colour)
		self.canvas.add(kivy.graphics.Rectangle(pos=(bl[0], bl[1]), size=( (tr[0]- bl[0]),  (tr[1]- bl[1])) ))
		self.startpos = self.pos
                self.do_rotation = False
                self.do_scale = True
                self.do_translation = True
        def on_touch_down(self, touch):
                print "shhet"

                self.camcam.do_touch()
                self.back_colour.g = 1
                self.camcam.selected = self


class KvPart(Scatter):
	deleted = False
	back_colour = kivy.graphics.Color(0,0,0)
	def draw(self, part):
		xoffset = 200
		mirror = 1
		self.part = part
		self.startcentre = (0,0)
		if part.border:
			config= part.border.generate_config({})
			if(hasattr(part, 'isback') and part.isback):
				print "part "+part.name+" is mirrored %%"
				mirror=-1
			else:
				mirror = 1
			ccpoints = part.border.polygonise()
			self.back_colour = kivy.graphics.Color(1,0,0,0.05)
			self.canvas.add( self.back_colour)
			width = part.border.boundingBox['tr'][0]-part.border.boundingBox['bl'][0]
			height = part.border.boundingBox['tr'][1]-part.border.boundingBox['bl'][1]
			if mirror>0:
				centrex = part.border.centre[0]
				centrey = part.border.centre[1]
			else:
				centrex = -part.border.centre[0]
				centrey = part.border.centre[1]
			if(mirror==-1):
				
				self.canvas.add(kivy.graphics.Rectangle(pos=(0,0), size=(width, height)))
			else:
				self.canvas.add(kivy.graphics.Rectangle(pos=(0,0), size=(width, height)))
			
			self.startcentre = (centrex, centrey)
			self.size = (part.border.boundingBox['tr'][0]-part.border.boundingBox['bl'][0],part.border.boundingBox['tr'][1]-part.border.boundingBox['bl'][1])
			kvpoints=[]
			for p in ccpoints:
				if mirror==-1:
					kvpoints.append((p[0] - centrex + width/2)*mirror+xoffset)
				else:
					kvpoints.append((p[0] - centrex + width/2)*mirror)
				kvpoints.append(p[1] - centrey + height/2)
			if part.border.closed:
				if mirror==-1:
	                                kvpoints.append((ccpoints[0][0] -centrex+width/2)*mirror+xoffset)
				else:
					kvpoints.append((ccpoints[0][0] -centrex+width/2)*mirror)
				kvpoints.append(ccpoints[0][1] -centrey+height/2)
			if 'cutterrad' in config:
				self.canvas.add(kivy.graphics.Color(1,0,0,0.5))
				self.canvas.add(kivy.graphics.Line(points=kvpoints, width=config['cutterrad']*2))
			self.linecolour = kivy.graphics.Color(1,1,0)
			self.canvas.add(self.linecolour)
			self.canvas.add(kivy.graphics.Line(points=kvpoints, width=1))
			self.canvas.add(kivy.graphics.Color(0,1,0,1))
#			self.canvas.add(Label(pos=((ccpoints[0][0] -centrex+width/2*mirror), ccpoints[0][1] -centrey+height/2), size=(3,3)))
			if mirror==-1:
				self.center = ( centrex+xoffset, centrey)
			else:
				self.center = ( centrex+xoffset, centrey)
#			kvpoints=[]
#			indices = []
#			for p in ccpoints:
#				kvpoints.append([p[0], p[1], 0,0])
#				indices.append(p)
#			print kvpoints
#			self.canvas.add(Mesh(verticies=kvpoints, indices=indices, mode='line_loop'))
			self.canvas.add(kivy.graphics.Color(0,0,0))
			self.add_widget(Label(text=str(part.name), x=0, y=0, halign='center'))
			print str(part.name)+" sself.center"+str(self.center)+" pos="+str(self.pos)
		self.startpos = self.pos
#		if mirror==-1:
#			self.startpos=(self.pos[0]-400, self.pos[1])
		self.do_rotation = True
		self.do_scale = False
		self.do_translation = True

	def on_bring_to_front(self, touch):
		print self.parent

		self.camcam.do_touch()
		self.back_colour.g = 1
		self.camcam.selected = self
		print self
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
	selected = False
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
		print App
		print dir(self)
		sheets = {}
		self.sheet_widgets = {}
		buttons = []
		layout = BoxLayout(size_hint=(1, None), height=50)
		for plane in self.planes:
			for part in plane.getParts():
				layer = plane.layers[part.layer].config
				sheetid = layer['material']+' '+str(layer['thickness'])
				if sheetid not in sheets:
					sheets[sheetid]=[]
					self.sheet_widgets[sheetid] = []
				sheets[sheetid].append( part)
		for sheet in sheets:
			button = Button(text = sheet)
			button.bind(on_press = partial(self.set_sheet, sheet))
			layout.add_widget(button)
		button = Button(text = 'Delete')
		button.bind(on_press = self.delete)
		layout.add_widget(button)
		button = Button(text = 'Duplicate')
		button.bind(on_press = self.duplicate)
		layout.add_widget(button)
		button = Button(text = 'Save')
		button.bind(on_press = self.save)
		layout.add_widget(button)
		for sheet in sheets:
			print sheet
			material = KvSheet()
			material.draw([0,50], [1200,650])
			material.camcam = self
			self.sheet_widgets[sheet].append(material)
			for part in sheets[sheet]:
				for i in range(0, part.number):
					picture = KvPart()#rotation=randint(-30,30))
					picture.draw(part)
					picture.camcam=self
					picture.part = part
					self.sheet_widgets[sheet].append(picture)
#				root.add_widget(picture)
		
    		root.add_widget(layout)
		
	def do_touch(self):
		for s in self.sheet_widgets:
			for p in self.sheet_widgets[s]:
				p.back_colour.g = 0

	def duplicate(self, *largs):
		print "DUPLICATE"
		if not self.selected:
			return
		picture = KvPart()#rotation=randint(-30,30))
                picture.draw(self.selected.part)
                picture.camcam=self
                picture.part = self.selected.part
                self.sheet_widgets[self.current_sheet].append(picture)

#		new = copy.copy(self.selected)
#		new.name+='_'
#		self.sheet_widgets[self.current_sheet].append(new)

	def delete(self, *largs):
		print "DELETE"
		print self.selected
		if self.selected:
			if self.selected.back_colour.b ==1:
				self.selected.back_colour.b = 0
				self.selected.deleted = 0
				self.selected.linecolour.a = 1
			else:
				self.selected.back_colour.b = 1
				self.selected.deleted = 1
				self.selected.linecolour.a = 0.1
	def save(self, *largs):
		global args
		data = {}
		data['args']=args
		data['sheets']={}
		for s in self.sheet_widgets:
			data['sheets'][s]=[]
			for p in self.sheet_widgets[s]:
				print p
				if p.part is not None:
					print p.part.name+" self.center"+str(p.center)+" startcentre"+str(p.startcentre)+" pos="+str(p.pos)+" startpos="+str(p.startpos)
					rec = {}
					rec['name']=p.part.name
					rec['translate'] = (p.pos[0] - p.startpos[0], p.pos[1] - p.startpos[1])
				
					m= p.get_window_matrix(x = p.center[0], y = p.center[1])
		#		print m
					m2 = numpy.matrix(m.tolist())
		#		print m2
					d = transformations.decompose_matrix(m2)
#				print "rotate="+str(d[2][2]/math.pi*180)
#				print "translate="+str(d[3])
#				print "perspective="+str(d[4])
#				print "position="+ str( [d[4][0]/d[4][3], d[4][1]/d[4][3] ])
#				print "kivy_translate="+str(rec['translate'])
		#		rec['rotate'] = math.atan2(m[4], m[0])/math.pi*180
					rec['rotate'] = d[2][2]/math.pi*180
					rec['startcentre'] = [0,0]
				#rec['startpos'] = p.startpos
					rec['startpos'] = [d[4][0]/d[4][3], d[4][1]/d[4][3]]
					if p.deleted ==0:
						data['sheets'][s].append(rec)
#				print p.get_window_matrix(0,0)
		h = open( 'layout_file', 'w')
		json.dump(data,h) 
#		pickle.dump(data, h)

	def set_sheet(self, sheet, *largs):
		print sheet
		self.current_sheet = sheet
		for s in self.sheet_widgets:
			for p in self.sheet_widgets[s]:
				if s==sheet:
					if not p.parent:
						self.root.add_widget(p)
				else:
					if p.parent:
						self.root.remove_widget(p)

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
parser.add_option("-L", "--layout-file", dest="layout_file",
                  help="output file for layout")
(options, args) = parser.parse_args()
config={}

camcam.command_args={}
if options.options:
	for pair in options.options.split(';'):
		a=pair.split('=')
		if len(a)>1:
			camcam.command_args[a[0]]=a[1]
print camcam.command_args
config['command_args']=camcam.command_args
# load all the requested files	
files = {}
lastfile = False
for arg in args:
	execfile(arg)
	#if arg[-1: -3] == '.py':
	#	execfile(arg)
#		lastfile = arg
#		files[arg]={}
#	elif unicode(arg).isnumeric():
#		files[lastfile]['number'] = int(arg)

if __name__ == '__main__':
  camcam.run()
#camcam.build()

