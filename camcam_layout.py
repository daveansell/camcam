#!/usr/bin/python
from path import *
from shapes import *
from parts import *
from boxes import *
#import importlib
from optparse import OptionParser
import sys
import Milling
import kivy
kivy.require('1.0.6')
import pickle

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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from functools import partial
from kivy.properties import NumericProperty

class KvPart(Scatter):
	deleted = False
	def draw(self, part):
		self.part = part
		self.startcentre = (0,0)
		if part.border:
			config= part.border.generate_config({})
			ccpoints = part.border.polygonise()
			self.back_colour = Color(1,0,0,0.05)
			self.canvas.add( self.back_colour)
			width = part.border.boundingBox['tr'][0]-part.border.boundingBox['bl'][0]
			height = part.border.boundingBox['tr'][1]-part.border.boundingBox['bl'][1]
			centrex = part.border.centre[0]
			centrey = part.border.centre[1]
			self.canvas.add(Rectangle(pos=(0,0), size=(width, height)))
			print part.name+" self.center"+str(self.center)+" pos="+str(self.pos)
			self.startcentre = (centrex, centrey)
			self.size = (part.border.boundingBox['tr'][0]-part.border.boundingBox['bl'][0],part.border.boundingBox['tr'][1]-part.border.boundingBox['bl'][1])
			kvpoints=[]
			for p in ccpoints:
				kvpoints.append(p[0] - centrex + width/2)
				kvpoints.append(p[1] - centrey + height/2)
			if part.border.closed:
				kvpoints.append(ccpoints[0][0] -centrex+width/2)
				kvpoints.append(ccpoints[0][1] -centrey+height/2)
			if 'cutterrad' in config:
				self.canvas.add(Color(1,0,0,0.5))
				self.canvas.add(kivy.graphics.Line(points=kvpoints, width=config['cutterrad']*2))
			self.linecolour = Color(1,1,0)
			self.canvas.add(self.linecolour)
			self.canvas.add(kivy.graphics.Line(points=kvpoints, width=1))
			self.canvas.add(Color(0,1,0,1))
			self.canvas.add(Ellipse(pos=(ccpoints[0][0] -centrex+width/2, ccpoints[0][1] -centrey+height/2), size=(3,3)))
			self.center = ( centrex , centrey)
#			kvpoints=[]
#			indices = []
#			for p in ccpoints:
#				kvpoints.append([p[0], p[1], 0,0])
#				indices.append(p)
#			print kvpoints
#			self.canvas.add(Mesh(verticies=kvpoints, indices=indices, mode='line_loop'))
			self.canvas.add(Color(0,0,0))
			self.add_widget(Label(text=part.name, x=0, y=0, halign='center'))
			print part.name+" sself.center"+str(self.center)+" pos="+str(self.pos)
		self.startpos = self.pos
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
		button = Button(text = 'Save')
		button.bind(on_press = self.save)
		layout.add_widget(button)
		for sheet in sheets:
			print sheet
			for part in sheets[sheet]:
				for i in range(0, part.number):
					picture = KvPart()#rotation=randint(-30,30))
					picture.draw(part)
					picture.camcam=self
					self.sheet_widgets[sheet].append(picture)
#				root.add_widget(picture)
    		root.add_widget(layout)
		
	def do_touch(self):
		for s in self.sheet_widgets:
			for p in self.sheet_widgets[s]:
				p.back_colour.g = 0

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
				print p.part.name+" self.center"+str(p.center)+" startcentre"+str(p.startcentre)+" pos="+str(p.pos)+" startpos="+str(p.startpos)
				rec = {}
				rec['name']=p.part.name
				rec['translate'] = (p.pos[0] - p.startpos[0], p.pos[1] - p.startpos[1])
				
			#	m= p.get_window_matrix(x = p.center[0], y = p.center[1])
		#		rec['rotate'] = math.atan2(m[4], m[0])/math.pi*180
				rec['rotate'] = 0
				rec['startcentre'] = p.startcentre
				rec['startpos'] = p.startpos
				if p.deleted ==0:
					data['sheets'][s].append(rec)
#				print p.get_window_matrix(0,0)
		h = open( 'layout_file', 'w') 
		pickle.dump(data, h)

	def set_sheet(self, sheet, *largs):
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

