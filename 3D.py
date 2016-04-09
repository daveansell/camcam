from solid import *
from solid.utils import *
from path import *
from segments import *
import math
from types import MethodType


SEGMENTS = 120
RESOLUTION = 0.2

def path_render3D(self, pconfig, border=True):
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


	outline = []
	points = self.polygonise(RESOLUTION)
	extrude_path = [ Point3(0,0,z0), Point3(0,0, z1) ]

	for p in points:
		outline.append(Point3(p[0], p[1], 0))
	extruded = extrude_along_path(shape_pts=outline, path_pts=path)

	return [extruded]
#def path_transform3D(self, pconfig):
#	config=self.overwrite(config,pconfig)
#        inherited = self.get_config()
#               if('transformations' in config):
#        config=self.overwrite(config, inherited)
#	for transform in config['transfomations']


Path.render3D = MethodType(path_render3D, Path)

def pathgroup_render3D(self, pconfig):
	ret=[]
	for path in self.paths:
		ret.append(path.render3D(pconfig))
	return ret
	
Pathgroup.render3D = MethodType(pathgroup_render3D, Pathgroup)

def plane_generate_part3D(self, part, pconfig):
	layers = self.get_layers()
        output = []
     	if part.layer in layers and part.layer is not False and part.layer is not None:
      		paths=layers[part.layer]
           	config.update(self.get_layer_config(part.layer))
      	elif part.layer is not False and part.layer is not None:
           	paths=[]
             	config.update(self.get_layer_config(part.layer))
     	else:
             	paths=[]
	if 'all' in layers:
        	paths.extend(layers['all'])
	if(part.border is not False and part.border is not None):
		self.border3D = part.border.render3D(pconfig, True)
	
	self.cutouts3D = []
	for path in paths:
		self.cutouts3D.extend(path.render3D(pconfig))
	
def plane_render_part3D(self, part, pconfig):
	self.generate_part3D(part, pconfig)
	for cutout in self.cutouts3D:
		self.border3D += hole()(cutout)
	
	scad_render_to_file(self.border3D, 'test.scad', include_orig_code=False)



Plane.generate_part3D = MethodType(plane_generate_part3D, Plane)
Plane.render_part3D = MethodType(plane_render_part3D, Plane)

