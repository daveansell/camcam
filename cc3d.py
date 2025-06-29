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



import solid #import *
import solid.utils #import *
from path import *
from segments import *
import math
from types import MethodType

SEGMENTS = 120
RESOLUTION = 0.5
_delta = 0
SCALEUP = 1
PRECISION = 3


def rotations_to_3D(self):
    p=self
    while p and type(p) is not Plane:
        if hasattr(p, 'transform') and p.transform is not None and type(p.transform) is dict:
            if 'rotate' in p.transform:
                
                #if 'rotate3D' not in p.transform:
#                                       p.transform['rotate3D'] = [ p.transform['rotate'][0], [0,0, p.transform['rotate'][1]] ]
                p.transform.insert(0,{
                        'rotate3D': [ 
                            [p.transform['rotate'][0][0], p.transform['rotate'][0][1], p.transform['rotate'][0][2]],
                            [0,0, p.transform['rotate'][1]]
                            ]} )
                #    del(p.transform['rotate'])
                #else:
                 #   print("OVERWRITING rotate3D with rotate which is unstable"+str(p.transform['rotate3D']))
#                       if 'translate' in p.transform:
#                               if 'translate3D' not in p.transform:
#                                       p.transform['translate3D'] = [ p.transform['translate'][0],  p.transform['translate'][0], 0 ]
#                                       del(p.transform['translate'])
#                               else:
#                                       print "OVERWRITING rotate3D with rotate which is unstable"
        p = p.parent
#                               self.transform['rotate3D'] = [ self.transform['rotate3D'][0], [0,0, self.transform['rotate3D'][1]] ]
#                               del(self.transform['rotate'])
Path.rotations_to_3D = rotations_to_3D
Part.rotations_to_3D = rotations_to_3D
Pathgroup.rotations_to_3D = rotations_to_3D


def path_render3D(self, pconfig, border=False):
    global _delta, PRECISION, SCALEUP
    self.rotations_to_3D()
    config={}
    config=self.overwrite(config,pconfig)
    inherited = self.get_config()
#               if('transformations' in config):
    print("++COLOUR"+str(config['colour']))
    config=self.overwrite(config, inherited)
    if border==False and 'zoffset' in pconfig:
        zoffset= pconfig['zoffset']
    elif 'zoffset' in config and  config['zoffset']:
        zoffset= config['zoffset']
    else:
        zoffset = 0
    if 'thickness' not in config:
        config['thickness']=pconfig['thickness']
    if config['z0'] is None or config['z0'] is False:
        z0=0
    else:
        z0=config['z0']

    if  border==False:
        z0 += config['thickness'] +1

    if (config['z1'] is False or config['z1'] is None) and config['z0'] is not None and config['thickness'] is not None:
        if  border==False:
            z1 = - config['thickness']- 20
        else:
            z1 = - config['thickness']
    else:
        z1= config['z1']
    z0 *=config['zdir']
    z1*=config['zdir']
    #       z0 = - config['thickness'] - z0
    #       z1 = - config['thickness'] - z1
# try to avoid faces and points touching by offsetting them slightly
    z0+=_delta
    z1-=_delta
    _delta+=0.00001
    outline = []
    self.reset_points()
    points = self.polygonise(RESOLUTION)
    points = self.clean_simplepath(points)
    if len(points)==0:
        return []
#       extrude_path = [ Point3(0,0,zoffset + float(z0)), Point3(0,0, zoffset + float(z1)) ]
    lastpoint=False
    # don't output repeated points in case it confuses things later
    for p in points:
        newpoint = [round(p[0],PRECISION)*SCALEUP, round(p[1],PRECISION)*SCALEUP ]
        if newpoint != lastpoint:
            outline.append( newpoint)
        lastpoint = newpoint
    newpoint = [round(points[0][0],PRECISION)*SCALEUP, round(points[0][1],PRECISION)*SCALEUP]
    if newpoint != lastpoint:
        outline.append( newpoint)

    outline.append([round(points[0][0],PRECISION)*SCALEUP, round(points[0][1],PRECISION)*SCALEUP])
#               outline.append( Point3(p[0], p[1], p[2] ))
#       outline.append( Point3(points[0][0], points[0][1], points[0][2] ))
    h = round(abs(z1-z0),PRECISION)*SCALEUP
    bottom = round((min(z1,z0)+zoffset),PRECISION) *SCALEUP
# dodgy but working atm
    if not border and 'isback' in config and config['isback']:
        pass
        h = 2*h
#       extruded = extrude_along_path(shape_pts=outline, path_pts=extrude_path)

    if self.extrude_scale is not None:
        scale = self.extrude_scale
        print("scaling ="+str(scale))
        if self.extrude_centre is None:
            self.extrude_centre = V(0,0)
        centre = (PSharp(V(0,0)).point_transform(config['transformations']).pos+self.extrude_centre)
        centre = [centre[0], centre[1]]
        uncentre = [-centre[0], -centre[1]]
        extruded = solid.translate([0,0,bottom])(
                        solid.translate(centre)(
                                solid.linear_extrude(height=h, center=False, scale = scale)(
                                        solid.translate(uncentre)(solid.polygon(points=outline)))))
    else:
        scale = 1
        extruded = solid.translate([0,0,bottom])(solid.linear_extrude(height=h, center=False)(solid.polygon(points=outline)))
    #extruded = translate([0,0,bottom])(linear_extrude(height=h, center=False)(solid.polygon(points=outline)))
#       if not border and 'isback' in config and config['isback'] and border==False:
#               extruded = solid.mirror([1,0,0])(extruded )
    print("COLOUR"+str(config['colour']))
    if 'colour' in config and config['colour']:
        extruded = solid.color(self.scad_colour(config['colour']))(extruded)
    return self.transform3D(self, extruded)

def path_transform3D(self, ob, extruded):
    p=ob
    c=0
 #   while(p and type(p) is not Plane):# and (c==0 or not p.renderable() )):
    p.rotations_to_3D()
    if hasattr(p, 'transform') and p.transform is not None and p.transform is not False and type(p.transform) is list:
            for transform in p.transform:
                if 'matrix3D' in transform:
                    if type(transform['matrix3D'][0]) is list or type(transform['matrix3D'][0]) is Vec:
                        extruded=solid.translate([-transform['matrix3D'][0][0], -transform['matrix3D'][0][1],-transform['matrix3D'][0][2]])(extruded)
                        extruded=solid.multmatrix(m=transform['matrix3D'][1])(extruded)
                        extruded=solid.translate([transform['matrix3D'][0][0], transform['matrix3D'][0][1],transform['matrix3D'][0][2]])(extruded)
                    else:
                        extruded=solid.multmatrix(m=transform['matrix3D'])(extruded)

                if 'rotate3D' in transform:
                    if type(transform['rotate3D'][0]) is list or type(transform['rotate3D'][0]) is Vec:
                        extruded=solid.translate([-transform['rotate3D'][0][0], -transform['rotate3D'][0][1],-transform['rotate3D'][0][2]])(extruded)
                        extruded=solid.rotate([transform['rotate3D'][1][0], transform['rotate3D'][1][1],transform['rotate3D'][1][2] ])(extruded)
                        extruded=solid.translate([transform['rotate3D'][0][0], transform['rotate3D'][0][1],transform['rotate3D'][0][2]])(extruded)
                    else:
                        extruded=solid.rotate([transform['rotate3D'][0], transform['rotate3D'][1],transform['rotate3D'][2] ])(extruded)
                if 'translate3D' in transform:
                    extruded=solid.translate([transform['translate3D'][0], transform['translate3D'][1],transform['translate3D'][2] ])(extruded)
   #     c+=1
#        p=p.parent
    return [extruded]
#def path_transform3D(self, pconfig):
#       config=self.overwrite(config,pconfig)
#        inherited = self.get_config()
#               if('transformations' in config):
#        config=self.overwrite(config, inherited)
#       for transform in config['transfomations']


Path.render3D = path_render3D
Path.transform3D = path_transform3D

def path_scad_colour(self, svgcolour):
    a=1.0
    if svgcolour[0]=='#':
        if len(svgcolour)<7:
            r = float(int(svgcolour[1],16))/15
            g = float(int(svgcolour[2],16))/15
            b = float(int(svgcolour[3],16))/15
            if(len(svgcolour)==5):
                a = float(int(svgcolour[4],16))/15
        else:
            r = float(int(svgcolour[1:3],16))/255
            g = float(int(svgcolour[3:5],16))/255
            b = float(int(svgcolour[5:7],16))/255
            if(len(svgcolour)>=9):
                a = float(int(svgcolour[7:9],16))/255
        return [r, g, b,a]
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
        self.transform=[]
    self.transform.append({'translate3D':vec})

Part.translate3D = part_translate3D
Path.translate3D = part_translate3D
Pathgroup.translate3D = part_translate3D

def part_rotate3D(self, vec, pos=False):
    if self.transform is False or self.transform is None:
        self.transform=[]
    if pos is False:
        self.transform.append({'rotate3D':vec})
    else:
        self.transform.append({'rotate3D':[pos, vec]})
Part.rotate3D = part_rotate3D
Path.rotate3D = part_rotate3D
Pathgroup.rotate3D = part_rotate3D

def part_matrix3D(self, vec, pos=False):
    if self.transform is False or self.transform is None:
        self.transform={}
    if pos is False:
        self.transform.append({'matrix3D':vec})
    else:
        self.transform.append({'matrix3D':[pos,vec]})
Part.matrix3D = part_matrix3D


def plane_generate_part3D(self, thepart, pconfig):
    self.mode='3D'
    self.callmode='3D'
    layers = self.get_layers(False)
    config=pconfig
    config['layer'] = thepart.layer
#       thepart.renderable = False
    if thepart.layer in layers and thepart.layer is not False and thepart.layer is not None:
#               if(thepart.border is not False and thepart.border is not None  and thepart.border.obType == "Path"):
#                       thepart.renderable = True
        paths=layers[thepart.layer]
        config.update(self.get_layer_config(thepart.layer))
    elif thepart.layer is not False and thepart.layer is not None:
        paths=[]
        config.update(self.get_layer_config(thepart.layer))
    else:
        paths=[]
    if thepart.layer in thepart.paths :
        paths.extend(thepart.paths[thepart.layer].paths)
    if 'all' in layers:
        paths.extend(layers['all'])
    config = thepart.overwrite(config,thepart.get_config())
    if(thepart.border is not False and thepart.border is not None):
        print("--COLOUR"+str(config['colour']))
        thepart.border3D = thepart.border.render3D(config, True)[0]
#       else:
#               thepart.renderable=False
    thepart.cutouts3D = []
    thepart.layercutouts3D = []
    thepart.intersections3D = []
    thepart.layerintersections3D = []
    for path in paths:
        thepart.cutouts3D.extend(path.render3D(config))

def plane_make_part3D(self, thepart, layers, pconfig, root=True):
    self.generate_part3D(thepart, pconfig)
#       for cutout in thepart.cutouts3D:
#               for c in cutout:
#                       thepart.border3D = thepart.border3D - c
    subparts = []
            
    for sp in thepart.parts:
        if hasattr(sp, 'subpart') and sp.subpart and sp!=thepart:
            #print('subpart='+str(sp))
            self.make_part3D(sp, layers, pconfig, False)
            if hasattr(sp, 'border3D'):
                if(sp.subpart=='subtract'):
                    thepart.cutouts3D.append([sp.border3D])
                elif(sp.subpart=='intersect'):
                    thepart.intersections3D.append(sp.border3D)
                else:    
                    subparts.append(sp.border3D)
    if len(subparts):
        if hasattr(thepart,'compose') and thepart.compose=='hull':
            #print("DO hull")
            if hasattr(thepart, 'border3D'):
                thepart.border3D=solid.hull()(thepart.border3D,*subparts)
            else:
                thepart.border3D=solid.hull()(*subparts)
        else:
            if hasattr(thepart, 'border3D'):
                thepart.border3D=solid.union()(thepart.border3D,*subparts)
            else:
                thepart.border3D=solid.union()(*subparts)
    if not hasattr(thepart, 'border3D'):
        return False
    cutouts = [thepart.border3D]
    for cutout in thepart.cutouts3D:
        if type(cutout) is list:
            for c in cutout:
                cutouts.append(c)
        else:
            cutouts.append(cutout)

    thepart.border3D = solid.difference()(*cutouts)
    if len(thepart.intersections3D):
        thepart.border3D = solid.intersection()(thepart.border3D, *thepart.intersections3D)

    # 3D transformations can only be applied to parts, so we can just go up the tree
    p = thepart

    c=0
    while(p and type(p) is not Plane):# and (c==0 or not p.renderable() ):
        p.rotations_to_3D()
        if hasattr(p, 'transform') and p.transform is not None and p.transform is not False and type(p.transform) is list and (c==0 or p.name is None):
            print(p.transform)
            for transform in p.transform:
                if 'matrix3D' in transform:
                    if type(transform['matrix3D'][0]) is list or type(transform['matrix3D'][0]) is Vec:
                        thepart.border3D=solid.translate([-transform['matrix3D'][0][0], -transform['matrix3D'][0][1],-transform['matrix3D'][0][2]])(thepart.border3D)
                        thepart.border3D=solid.multmatrix(m=transform['matrix3D'][1])(thepart.border3D)
                        thepart.border3D=solid.translate([transform['matrix3D'][0][0], transform['matrix3D'][0][1],transform['matrix3D'][0][2]])(thepart.border3D)
                    else:
                        thepart.border3D=solid.multmatrix(m=transform['matrix3D'])(thepart.border3D)

                if 'rotate3D' in transform:
                    if type(transform['rotate3D'][0]) is list or type(transform['rotate3D'][0]) is Vec:
                        thepart.border3D=solid.translate([-transform['rotate3D'][0][0], -transform['rotate3D'][0][1],-transform['rotate3D'][0][2]])(thepart.border3D)
                        thepart.border3D=solid.rotate([transform['rotate3D'][1][0], transform['rotate3D'][1][1],transform['rotate3D'][1][2] ])(thepart.border3D)
                        thepart.border3D=solid.translate([transform['rotate3D'][0][0], transform['rotate3D'][0][1],transform['rotate3D'][0][2]])(thepart.border3D)
                    else:
                        thepart.border3D=solid.rotate([transform['rotate3D'][0], transform['rotate3D'][1],transform['rotate3D'][2] ])(thepart.border3D)
                if 'translate3D' in transform:
                    thepart.border3D=solid.translate([transform['translate3D'][0], transform['translate3D'][1],transform['translate3D'][2] ])(thepart.border3D)
        c+=1
        if not hasattr(p, 'subpart') and not p.subpart or hasattr(p,'layer') and hasattr(p.parent, 'layer') and p.layer != p.parent.layer: # if this is a root part add parent's transforms, or if it has come in via layers 
            p=p.parent
        else:
            p=False
    layersubparts = []
    if hasattr(thepart, 'layer') and thepart.layer in layers and root:
        # has issue that these get wrapped with root part transforms
        pass
        for sp in layers[thepart.layer]:
            if hasattr(sp, 'subpart') and sp.subpart and sp!=thepart:
                #print('subpart='+str(sp))
                self.make_part3D(sp, layers, pconfig, False)
                if hasattr(sp, 'border3D'):
                    if(sp.subpart=='subtract'):
                        thepart.layercutouts3D.append([sp.border3D])
                    elif(sp.subpart=='intersect'):
                        thepart.layerintersections3D.append(sp.border3D)
                    else:    
                        layersubparts.append(sp.border3D)
    if len(layersubparts):
            if hasattr(thepart, 'border3D'):
                thepart.border3D=solid.union()(thepart.border3D,*layersubparts)
            else:
                thepart.border3D=solid.union()(*layersubparts)
    if len(thepart.layercutouts3D):
        cutouts = [thepart.border3D]
        for cutout in thepart.layercutouts3D:
            for c in cutout:
                cutouts.append(c)
        thepart.border3D = solid.difference()(*cutouts)
    if len(thepart.layerintersections3D):
        thepart.border3D = solid.intersection()(thepart.border3D, *thepart.intersections3D)


def plane_render_part3D(self, thepart, pconfig, layers={}, filename=False):
    self.make_part3D(thepart, layers, pconfig)
    if filename==False:
        if thepart.name is None:
            return
        filename = thepart.name+'.scad'
    else:
        filename = filename +',scad'
    if hasattr(thepart, 'border3D'):
        solid.scad_render_to_file(thepart.border3D, filename,file_header = '$fa = 0.5;\n$fs = 0.5;', include_orig_code=False)
import inspect
def part_get_layers3D(self):
    """collect subparts with a different layer to parent"""
    layers={}
    for part in self.parts:
        ls = part.get_layers3D()
        for l,ly in ls.items():
            if l not in layers.keys():
                layers[l]=ly
            else:
                layers[l]=layers[l]+ls[l]
        if hasattr(part,'subpart') and part.subpart and hasattr(self, 'layer') and part.layer!=self.layer:
            if part.layer not in layers:
                layers[part.layer]=[]
            layers[part.layer].append(part)
    return layers

def plane_render_all3D(self,callmode,cmdconfig):
    """Render all parts in the Plane"""
    self.modeconfig=milling.mode_config[callmode]
    self.make_copies()
    layers = self.get_layers3D()
   # print(layers)
    config=copy.copy(self.modeconfig)
    if(self.modeconfig['overview']==False):
        for thepart in self.getParts(False):
            if not (hasattr(thepart, 'subpart') and thepart.subpart):
                self.render_part3D(thepart,config, layers)
    else:
        scene = False
        for thepart in self.getParts(True):
            print(config)
            if not (hasattr(thepart, 'subpart') and thepart.subpart) and ('parts' not in cmdconfig or len(cmdconfig['parts'])==0 or thepart.name in cmdconfig['parts']):

                self.make_part3D(thepart, layers, config)
                if hasattr(thepart,"border3D"):
                    if scene==False:
                        scene = solid.part()(thepart.border3D)
                    else:
                        scene += solid.part()(thepart.border3D)
        solid.scad_render_to_file(scene, 'Overview.scad',file_header = '$fa = 2.5;\n$fs = 2.5;', include_orig_code=False)

Part.get_layers3D = part_get_layers3D
Plane.get_layers3D = part_get_layers3D
Plane.generate_part3D = plane_generate_part3D# MethodType(plane_generate_part3D, Plane)
Plane.make_part3D = plane_make_part3D#MethodType(plane_render_part3D, Plane)
Plane.render_part3D = plane_render_part3D#MethodType(plane_render_part3D, Plane)
Plane.render_all3D = plane_render_all3D #MethodType(plane_render_all3D, Plane)
