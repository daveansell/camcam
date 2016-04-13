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



from solid import *
from solid.utils import *
from path import *
from segments import *
import math
from types import MethodType


SEGMENTS = 120
RESOLUTION = 0.3
_delta = 0
SCALEUP = 1
PRECISION = 3

def path_render3D(self, pconfig, border=False):
	global _delta, PRECISION, SCALEUP
	config={}
	config=self.overwrite(config,pconfig)
      	inherited = self.get_config()
#               if('transformations' in config):
      	config=self.overwrite(config, inherited)

	if 'zoffset' in pconfig and  pconfig['zoffset']:
		zoffset= pconfig['zoffset']
	else:
		zoffset = 0
	if config['z0'] is None or config['z0'] is False:
		z0=0
	else:
		z0=config['z0']
	
	if  border==False:
                        z0 += 1

	if (config['z1'] is False or config['z1'] is None) and config['z0'] is not None and config['thickness'] is not None:
        	if  border==False:
                 	z1 = - config['thickness']- 1
           	else:
                   	z1 = - config['thickness']
	else:
		z1= config['z1']
	if 'isback' in config and config['isback'] and border==False:
		z0 = - config['thickness'] - z0
		z1 = - config['thickness'] - z1
# try to avoid faces and points touching by offsetting them slightly
	z0+=_delta
	z1-=_delta
	_delta+=0.001
	outline = []
	points = self.polygonise(RESOLUTION)
	extrude_path = [ Point3(0,0,zoffset + float(z0)), Point3(0,0, zoffset + float(z1)) ]
	for p in points:
		outline.append( [round(p[0],PRECISION)*SCALEUP, round(p[1],PRECISION)*SCALEUP ])
	outline.append([round(points[0][0],PRECISION)*SCALEUP, round(points[0][1],PRECISION)*SCALEUP])
#		outline.append( Point3(p[0], p[1], p[2] ))
#	outline.append( Point3(points[0][0], points[0][1], points[0][2] ))
	h = round(abs(z1-z0),PRECISION)*SCALEUP
	bottom = round((min(z1,z0)+zoffset),PRECISION) *SCALEUP
#	extruded = extrude_along_path(shape_pts=outline, path_pts=extrude_path)
	extruded = translate([0,0,bottom])(linear_extrude(height=h, center=False)(polygon(points=outline)))
#	if 'isback' in config and config['isback'] and border==False:
#		extruded = mirror([1,0,0])(extruded )
	if 'colour' in config and config['colour']:
		extruded = color(self.scad_colour(config['colour']))(extruded)
	return [extruded]
#def path_transform3D(self, pconfig):
#	config=self.overwrite(config,pconfig)
#        inherited = self.get_config()
#               if('transformations' in config):
#        config=self.overwrite(config, inherited)
#	for transform in config['transfomations']


Path.render3D = path_render3D

def path_scad_colour(self, svgcolour):
	if svgcolour[0]=='#':
		r = float(int(svgcolour[1:3],16))/255
		g = float(int(svgcolour[3:5],16))/255
		b = float(int(svgcolour[5:7],16))/255
		return [r, g, b]
	else:
		lookup={'green':[0,1.0,0], 'red':[1.0, 0, 0], 'yellow':[1.0,1.0,0], 'blue':[0,0,1.0]}
		return 
Path.scad_colour = path_scad_colour


def pathgroup_render3D(self, pconfig):
	ret=[]
	for path in self.paths:
		ret.append(path.render3D(pconfig))
	return ret
	
Pathgroup.render3D = pathgroup_render3D

def part_translate3D(self, vec):
	if self.transform is False or self.transform is None:
            	self.transform={}
      	self.transform['translate3D']=vec

Part.translate3D = part_translate3D

def part_rotate3D(self, vec):
	if self.transform is False or self.transform is None:
            	self.transform={}
      	self.transform['rotate3D']=vec

Part.rotate3D = part_rotate3D

def plane_generate_part3D(self, thepart, pconfig):
	self.mode='3D'
	self.callmode='3D'
	layers = self.get_layers()
	config=pconfig
	config['layer'] = thepart.layer
     	if thepart.layer in layers and thepart.layer is not False and thepart.layer is not None:
      		paths=layers[thepart.layer]
           	config.update(self.get_layer_config(thepart.layer))
      	elif thepart.layer is not False and thepart.layer is not None:
           	paths=[]
             	config.update(self.get_layer_config(thepart.layer))
     	else:
             	paths=[]
	if 'all' in layers:
        	paths.extend(layers['all'])
	config = thepart.overwrite(config,thepart.get_config())
	if(thepart.border is not False and thepart.border is not None):
		thepart.border3D = thepart.border.render3D(config, True)[0]
	thepart.cutouts3D = []
	for path in paths:
		thepart.cutouts3D.extend(path.render3D(config))
	
def plane_make_part3D(self, thepart, pconfig):
	self.generate_part3D(thepart, pconfig)
#	for cutout in thepart.cutouts3D:
#		for c in cutout:
#			thepart.border3D = thepart.border3D - c
	cutouts = [thepart.border3D]
	for cutout in thepart.cutouts3D:
		for c in cutout:
			cutouts.append(c)

	thepart.border3D = difference()(*cutouts)
	# 3D transformations can only be applied to parts, so we can just go up the tree
	p = thepart
	while(p and type(p) is not Plane):
		if 'rotate3D' in p.transform:
			thepart.border3D=solidpython.rotate([p.transform['rotate3D'][0], p.transform['rotate3D'][1],p.transform['rotate3D'][2] ])(thepart.border3D)
		if 'translate3D' in p.transform:
			thepart.border3D=solidpython.translate([p.transform['translate3D'][0], p.transform['translate3D'][1],p.transform['translate3D'][2] ])(thepart.border3D)
		p=p.parent
def plane_render_part3D(self, thepart, pconfig, filename=False):
	self.make_part3D(thepart, pconfig)
	if filename==False:
		filename = thepart.name+'.scad'
	else:
		filename = filename +',scad'
	scad_render_to_file(thepart.border3D, filename, include_orig_code=False)

def plane_render_all3D(self,callmode,config):
     	"""Render all parts in the Plane"""
	self.modeconfig=milling.mode_config[callmode]
       	self.make_copies()
	config=copy.copy(self.modeconfig)
	if(self.modeconfig['overview']==False):
	     	for thepart in self.getParts(False):
        	 	self.render_part3D(thepart,config)
	else:
		scene = False
		for thepart in self.getParts(True):
			self.make_part3D(thepart, config)
			if scene==False:
				scene = part()(thepart.border3D)
			else:
				scene += part()(thepart.border3D)
		scad_render_to_file(scene, 'Overview.scad', include_orig_code=False)

Plane.generate_part3D = plane_generate_part3D# MethodType(plane_generate_part3D, Plane)
Plane.make_part3D = plane_make_part3D#MethodType(plane_render_part3D, Plane)
Plane.render_part3D = plane_render_part3D#MethodType(plane_render_part3D, Plane)
Plane.render_all3D = plane_render_all3D #MethodType(plane_render_all3D, Plane)

