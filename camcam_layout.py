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
from kivy.uix.scatter import ScatterPlane
from kivy.properties import StringProperty
# FIXME this shouldn't be necessary
from kivy.core.window import Window
#from kivy.graphics import *# Color, Rectangle, Canvas
import kivy.graphics
from  kivy.uix.label import *
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from functools import partial
from kivy.properties import NumericProperty
from kivy.lang import Builder 
from kivy.uix.slider import Slider


Builder.load_file('/home/dave/cnc/camcam/camcam.kv')
class KvSheet(ScatterPlane):
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

                self.camcam.do_touch()
                self.back_colour.g = 1
                #self.camcam.selected = self


class KvPart(Scatter):
	deleted = False
	back_colour = kivy.graphics.Color(0,0,0)
	def draw(self, part):
		xoffset = 200
		mirror = 1
		self.part = part
		self.startcentre = (0,0)
		if part.border:
			#part.transform={}
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
			
			self.origin = (width/2,height/2)
			self.canvas.add(kivy.graphics.Ellipse(pos=(self.origin[0]-1.5, self.origin[1]-1.5), size=(3, 3)))

#			kvpoints=[]
#			indices = []
#			for p in ccpoints:
#				kvpoints.append([p[0], p[1], 0,0])
#				indices.append(p)
#			print kvpoints
#			self.canvas.add(Mesh(verticies=kvpoints, indices=indices, mode='line_loop'))
			self.canvas.add(kivy.graphics.Color(0,0,0))
			self.add_widget(Label(text=str(part.name), x=0, y=0, halign='center'))
		self.startpos = self.pos
#		if mirror==-1:
#			self.startpos=(self.pos[0]-400, self.pos[1])
		self.do_rotation = False
		self.do_scale = False
		self.do_translation = True

	def on_bring_to_front(self, touch):

		self.camcam.do_touch()
		self.back_colour.g = 1
		self.camcam.selected = self
		self.camcam.slider.value = self.rotation
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
        	root = BoxLayout(size_hint=(1,1), orientation='vertical')
		self.floatlayout = ScatterPlane()
		root.add_widget(self.floatlayout)
        # get any files into images directory
		sheets = {}
		self.sheet_widgets = {}
		buttons = []
		layout = BoxLayout(size_hint=(1, None), height=30)
		layout2 = BoxLayout(size_hint=(1, None), height=30)
		print "command_args="+str(camcam.command_args)
		mode='normal'
		if camcam.command_args.layout_file:
			mode='layout'
			partlist={}
                	for plane in self.planes:
                        	for part in plane.getParts(config={}):
                        	        part.make_copies()
                        	        partlist[part.name] = [plane, part]
					

			with open(camcam.command_args.layout_file, "r") as read_file:
    				shts = json.load(read_file)['sheets']
			for sheetid in shts:
				sheetname = re.sub('_\d+-\d+$','',sheetid)
				if sheetname not in sheets:
					sheets[sheetname]=[]
	                                self.sheet_widgets[sheetname] = []
				for p in shts[sheetid]:
					if p and p['name']!='None':
						part=copy.copy(partlist[str(p['name'])][1])
						part.kivy_translate=p['translate']
						part.kivy_rotate=p['rotate']
						part.sheet = sheetname
						sheets[sheetname].append( part)
		else:
			for plane in self.planes:
				for part in plane.getParts():
					layer = plane.layers[part.layer].config
					sheetid = layer['material']+' '+str(layer['thickness'])
					if sheetid not in sheets:
						sheets[sheetid]=[]
						self.sheet_widgets[sheetid] = []
					part.sheet = sheetid
					sheets[sheetid].append( part)
		if hasattr( self.command_args, "sheets") and self.command_args.sheets:
			sheetlist = self.command_args.sheets.split(',')
		else:
			sheetlist = sheets.keys()
		for sheet in sheetlist:
			button = Button(text = sheet)
			button.bind(on_press = partial(self.set_sheet, sheet))
			layout.add_widget(button)
		button = Button(text = 'Delete')
		button.bind(on_press = self.delete)
		layout2.add_widget(button)
		button = Button(text = 'Duplicate')
		button.bind(on_press = self.duplicate)
		layout2.add_widget(button)
		button = Button(text = 'Save')
		button.bind(on_press = self.save)
		layout2.add_widget(button)
		button = Button(text = '+')
		button.bind(on_press = self.zoomin)
		layout2.add_widget(button)
		button = Button(text = '-')
		button.bind(on_press = self.zoomout)
		layout2.add_widget(button)
		self.slider = Slider(min=0, max=360, on_touch_move=self.doSlider) 
		layout2.add_widget(self.slider)
		if not self.command_args.boardWidth:
			self.command_args.boardWidth=1200
		if not self.command_args.boardHeight:
                        self.command_args.boardHeight=600
		if not self.command_args.repeatx:
			self.command_args.repeatx=1
		if not self.command_args.repeaty:
			self.command_args.repeaty=1
		for sheet in sheets:
			material = KvSheet()
			for i in range(0,int(self.command_args.repeatx)):
				for j in range(0,int(self.command_args.repeaty)):
					material.draw(
						[i*int(self.command_args.boardWidth),
						j*int(self.command_args.boardHeight)], 
						[(i+1)*int(self.command_args.boardWidth),
						(j+1)*int(self.command_args.boardHeight)])
			material.camcam = self
			self.sheet_widgets[sheet].append(material)
			for part in sheets[sheet]:
				if mode=='layout':
					num=1
				else:
					num=part.number
				for i in range(0, num):
					picture = KvPart()#rotation=randint(-30,30))
					picture.draw(part)
					picture.camcam=self
					picture.part = part
					if hasattr(part, "kivy_translate"):
						picture.pos =[picture.pos[0]+part.kivy_translate[0], picture.pos[1]+part.kivy_translate[1]]
					if hasattr(part, "kivy_rotate"):
						picture.rotation=part.kivy_rotate
					self.sheet_widgets[sheet].append(picture)
#				root.add_widget(picture)
    		root.add_widget(layout)
    		root.add_widget(layout2)
		return root

	def doSlider(self, touch, b):
		if self.selected:
			self.selected.rotation=touch.value
		
	def do_touch(self):
		for s in self.sheet_widgets:
			for p in self.sheet_widgets[s]:
				p.back_colour.g = 0
	def zoomin(self, *args):
		self.floatlayout.scale*=1.5
	def zoomout(self, *args):
		self.floatlayout.scale/=1.5
	def duplicate(self, *largs):
		print "DUPLICATE"
		if not self.selected:
			return
		picture = KvPart()#copy.copy(self.selected)#rotation=randint(-30,30))
		part = copy.copy(self.selected.part)
                picture.draw(self.selected.part)
                picture.camcam=self
                picture.part = part
                self.sheet_widgets[self.current_sheet].append(picture)
		self.floatlayout.add_widget(picture)
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
		data['command_args']=camcam.command_args.__dict__
		data['files']=camcam.files
		for s in self.sheet_widgets:
			for i in range(0,int(self.command_args.repeatx)):
				for j in range(0,int(self.command_args.repeaty)):
					data['sheets'][s+"_"+str(i)+"-"+str(j)]=[]
			
			for p in self.sheet_widgets[s]:
				if p.part is not None:
					rec = {}
					rec['name']=str(p.part.name)
					tempr=p.rotation
					p.rotation=0
					rec['translate'] = (p.pos[0] - p.startpos[0], p.pos[1] - p.startpos[1])
					p.rotation=tempr
					m= p.get_window_matrix(x = p.center[0], y = p.center[1])
					m2 = numpy.matrix(m.tolist())
					d = transformations.decompose_matrix(m2)
					rec['origin'] = p.origin
					rec['center'] = p.center
					rec['rotate'] = p.rotation
					rec['startcentre'] = p.startcentre
				#rec['startpos'] = p.startpos
					rec['startpos'] = [d[4][0]/d[4][3], d[4][1]/d[4][3]]
#					print str(p.part.name)+" self.center"+str(p.center)+" startcentre"+str(p.startcentre)+" pos="+str(p.pos)+" startpos="+str(p.startpos)+" translate="+str(rec['translate'])+" origin="+str(rec['origin']) 
					if p.deleted ==0:
						for i in range(0,int(self.command_args.repeatx)):
			                                for j in range(0,int(self.command_args.repeaty)):
								if	p.center[0]>i*int(self.command_args.boardWidth)\
									and p.center[0]<(i+1)*int(self.command_args.boardWidth)\
									and p.center[1]>j*int(self.command_args.boardHeight)\
                                                                        and p.center[1]<(j+1)*int(self.command_args.boardHeight):
										data['sheets'][s+"_"+str(i)+"-"+str(j)].append(rec)
										print "*>>>>* "+str(p.part.name)+" "+str(p.pos)+" "+s+"_"+str(i)+"-"+str(j)+" center"+str(p.center)
									

#				print p.get_window_matrix(0,0)
		h = open( 'layout_file', 'w')
		json.dump(data,h, indent=4) 
#		pickle.dump(data, h)

	def set_sheet(self, sheet, *largs):
		print sheet
		self.current_sheet = sheet
		for s in self.sheet_widgets:
			for p in self.sheet_widgets[s]:
				if s==sheet:
					if not p.parent:
						self.floatlayout.add_widget(p)
				else:
					if p.parent:
						self.floatlayout.remove_widget(p)

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
parser.add_option("-W", "--boardWidth", dest="boardWidth",
                  help="board Width")
parser.add_option("-H", "--boardHeight", dest="boardHeight",
                  help="boardHeight")
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
parser.add_option("-L", "--layout-file", dest="layout_file",
                  help="output file for layout")
parser.add_option("-s", "--sheets", dest="sheets",
                  help="just output these sheets (comma separated)")
parser.add_option("-O", "--repeatoffset", dest="repeatoffset",
                  help="Repeat Offset for cp_int etc")
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
parser.add_option('-e', '--reposition', dest='zero',
                  help='reposition the origin to bottom_left, top_right or centre')
parser.add_option("-q", "--offsetx", dest="offsetx",
                  help="offset x")
parser.add_option("-Q", "--offsety", dest="offsety",
                  help="offset y")

(options, args) = parser.parse_args()
config={}
print "****options"+str(options)
camcam.command_args=options
camcam.files=args
if camcam.command_args.layout_file:
	def byteify(input):
    		if isinstance(input, dict):
        		return {byteify(key): byteify(value)
           		     	for key, value in input.iteritems()}
    		elif isinstance(input, list):
        		return [byteify(element) for element in input]
    		elif isinstance(input, unicode):
        		return input.encode('utf-8')
    		else:
        		return input

	with open(camcam.command_args.layout_file, "r") as read_file:
		layoutData = byteify(json.load(read_file))
	print layoutData.keys()
	if len(args)==0:
		args = layoutData['args']
	print "******ARGS="+str(args)
	if 'command_args' in layoutData:
		for v in camcam.command_args.__dict__:
			if camcam.command_args.__dict__[v] is not None:
				layoutData['command_args'][v] = camcam.command_args.__dict__[v]
		print "****"+str(layoutData['command_args'])
		camcam.command_args.__dict__ = layoutData['command_args']
	

print camcam.command_args
config['command_args']=camcam.command_args
# load all the requested files	
files = {}
lastfile = False
for arg in args:
	execfile(os.getcwd()+'/'+arg)
	#if arg[-1: -3] == '.py':
	#	execfile(arg)
#		lastfile = arg
#		files[arg]={}
#	elif unicode(arg).isnumeric():
#		files[lastfile]['number'] = int(arg)

if __name__ == '__main__':
  camcam.run()
#camcam.build()

