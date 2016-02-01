from dxfwrite import DXFEngine as dxf
from segments import *
from path import *

Segment.seg_types['dxf']='dxf'
def line_dxf(self, direction=True):
	if(direction):
		return [dxf.line((self.cutfrom[0], self.cutfrom[1]), (self.cutto[0], self.cutto[1]))]
	else:
		return [dxf.line( (self.cutto[0], self.cutto[1]), (self.cutfrom[0], self.cutfrom[1]))]

setattr(Line, 'dxf', line_dxf)

def arc_dxf(self, direction=True):
	radius = (self.centre - self.cutto).length()
	a = self.centre - self.cutto
	b = self.centre - self.cutfrom
	angle0 = math.atan2(a[1], a[0])/math.pi *180+180
	angle1 = math.atan2(b[1], b[0])/math.pi *180+180
        if(self.direction=='ccw'):
                return [dxf.arc(radius, self.centre, angle0, angle1)]
        else:
                return [dxf.arc(radius, self.centre, angle1, angle0)]

setattr(Arc, 'dxf', arc_dxf)

def write_dxf(self,partName, key, output, border, config):
	drawing = dxf.drawing(self.sanitise_filename(str(partName)+"_"+str(key)+config['file_suffix']))
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
	                                                        	drawing.add(r)
							else:
	                                                	drawing.add(q)
	                                else:
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
