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



from dxfwrite import DXFEngine as dxf
from segments import *
from path import *

Segment.seg_types['dxf']='dxf'
colours = {None:1, False:1}
colourcount = 2
def colour_from_z(z):
	global colourcount, colours
	if z not in colours:
		colours[z]=colourcount
		print "z="+str(z)+" to colour="+str(colours[z])
		colourcount+=1
	return colours[z]


def line_dxf(self, direction=True):
	c=self.parent.get_config()
	if 'z1' in c and c['z1'] is not None and c['z1'] is not False:
		colour = colour_from_z(c['z1'])
	elif hasattr(self, 'z1'):
		colour = colour_from_z(self.z1)
	elif(hasattr(self, "parent") and hasattr(self.parent, 'z1')):
		colour = colour_from_z(self.parent.z1)
	else:
		colour = 1
	
	if(direction):
		return [dxf.line((self.cutfrom[0], self.cutfrom[1]), (self.cutto[0], self.cutto[1]), color=colour)]
	else:
		return [dxf.line( (self.cutto[0], self.cutto[1]), (self.cutfrom[0], self.cutfrom[1]), color=colour)]

setattr(Line, 'dxf', line_dxf)

def arc_dxf(self, direction=True):
	if(hasattr(self, "parent") and hasattr(self.parent, 'z1')):
		colour = colour_from_z(self.parent.z1)
	else:
		colour = 1
	radius = (self.centre - self.cutto).length()
	a = self.centre - self.cutto
	b = self.centre - self.cutfrom
	angle0 = math.atan2(a[1], a[0])/math.pi *180+180
	angle1 = math.atan2(b[1], b[0])/math.pi *180+180
        if(self.direction=='ccw'):
                return [dxf.arc(radius, self.centre, angle0, angle1, color=colour)]
        else:
                return [dxf.arc(radius, self.centre, angle1, angle0, color=colour)]

setattr(Arc, 'dxf', arc_dxf)

def write_dxf(self,partName, key, output, border, config):
	drawing = dxf.drawing(self.sanitise_filename(str(partName)+"-"+str(config['thickness'])+"_"+str(key)+config['file_suffix']))
	drawing.header['$LUNITS']=1
	drawing.header['$AUNITS']=0
	drawing.header['$ANGBASE']=0

	drawing.header['$ACADVER']='AC1009'
	drawing.add_layer('LINES')
	if type(output) is not list:
	        for k,o in output.iteritems():
	                if type(o) is list:
	                        for p in o:
	                                if type(p) is list:
	                                        for q in p:
							if type(q) is list:
								for r in q:
									if type(r) is not dict:
		                                                        	drawing.add(r)
							else:
								if type(q) is not dict:
	                                                		drawing.add(q)
	                                else:
						if type(p) is not dict:
	                                        	drawing.add(p)
	                else:
				drawing.add(0)
	else:	
		for o in output:
			if type(o) is list:
				for p in o:
					if type(p) is list:
						for q in p:
							drawing.add(q)
					else:
						drawing.add(p)
			else:
				drawing.add(o)
	drawing.save()

Plane.output_modes['dxf']=write_dxf
