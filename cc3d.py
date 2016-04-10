
from solid import *
from solid.utils import *
from path import *
from segments import *
import math
from types import MethodType


SEGMENTS = 120
RESOLUTION = 0.2

def path_render3D(self, pconfig, border=False):
	config={}
	config=self.overwrite(config,pconfig)
      	inherited = self.get_config()
#               if('transformations' in config):
      	config=self.overwrite(config, inherited)

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
		print "isback"
		z0 = - config['thickness'] - z0
		z1 = - config['thickness'] - z1

	outline = []
	points = self.polygonise(RESOLUTION)
	extrude_path = [ Point3(0,0,float(z0)), Point3(0,0, float(z1)) ]
	print extrude_path
	for p in points:
		outline.append(Point3(p[0], p[1], 0))
	extruded = extrude_along_path(shape_pts=outline, path_pts=extrude_path)
	if 'isback' in config and config['isback'] and border==False:
		extruded = mirror([1,0,0])(extruded )
	return [extruded]
#def path_transform3D(self, pconfig):
#	config=self.overwrite(config,pconfig)
#        inherited = self.get_config()
#               if('transformations' in config):
#        config=self.overwrite(config, inherited)
#	for transform in config['transfomations']


Path.render3D = path_render3D

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

def plane_generate_part3D(self, thepart, pconfig):
	self.mode='3D'
	self.callmode='3D'
	layers = self.get_layers()
	config=pconfig
	print thepart
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
	if(thepart.border is not False and thepart.border is not None):
		thepart.border3D = thepart.border.render3D(pconfig, True)[0]
	
	thepart.cutouts3D = []
	for path in paths:
		thepart.cutouts3D.extend(path.render3D(pconfig))
	
def plane_make_part3D(self, thepart, pconfig):
	print pconfig
	self.generate_part3D(thepart, pconfig)
	for cutout in thepart.cutouts3D:
		for c in cutout:
			thepart.border3D = thepart.border3D + hole()(c)
	if 'translate3D' in thepart.transform:
		thepart.border3D=translate([thepart.transform['translate3D'][0], thepart.transform['translate3D'][1],thepart.transform['translate3D'][2] ])(thepart.border3D)
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

