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
import shapely.geometry


class LathePart(Part):
	def __init__(self, **config):
		self.init(config)
		self.ignore_border=True

	def init(self, config):
		self.varlist=['roughClearance', 'matEnd', 'latheMode', 'matRad', 'step', 'cutClear', 'handedness', 'cutFromBack', 'chipBreak', 'justRoughing']
		super(LathePart, self).init(config)
		self.ignore_border = True

	def _pre_render(self, config):
		if('matEnd' not in config):
			self.materialEnd = 3
			
			

class LathePath(Path):
	def __init__(self, **config):
		self.init(config)
		self.closed=False
		self.side='on'
	
	def init(self, config):
		self.varlist=['roughClearance', 'matEnd', 'latheMode', 'matRad', 'step', 'cutClear', 'handedness', 'cutFromBack', "spindleDir", "chipBreak", "justRouging"]
		self.shapelyPolygon=False
		self.stepdown = 1000
		self.direction= 'this'	
		self.spindleDir = 'ccw'
		super(LathePath, self).init(config)
		self.cuts=[]
		if 'doRoughing' in config and config['doRoughing'] is not None:
			self.doRoughing= config['doRoughing']
		else:
			self.doRoughing=True
		if 'chipBreak' in config:
			self.chipBreak = config['chipBreak']
			print "initCHipbreak"
		if 'justRoughing' in config and config['justRoughing'] is not None:
			self.justRoughing= config['justRoughing']
		else:
			self.justRoughing=False
		self.doneRoughing = False
		self.donePreRender = False

	def render_path_gcode(self,path,config):
                ret=""
                if config['mode']=='gcode':
                        if 'blendTolerance' in config:
                                if config['blendTolerance']>0:
                                        ret+="G64P"+str(config['blendTolerance'])+"\n"
                                else:
                                        ret+="G64\n"
                for point in path:
			if 'cmd' in point:
				if point['cmd']=="G2":
					point['cmd']="G3"
				elif point['cmd']=="G3":
					point['cmd']="G2"
                        if '_comment' in point and config['comments']:
                                ret+="("+point['_comment']+")"
                        if 'cmd' in point:
                                ret+=point['cmd']
                        if 'X' in point:
                                ret+="X%0.4f"%point['X']
                        if 'Y' in point:
                                ret+="Z%0.4f"%point['Y']
#                        if 'Z' in point:
#                                ret+="Z%0.4f"%point['Z']
                        if 'I' in point:
                                ret+="I%0.4f"%point['I']
                        if 'J' in point:
                                ret+="K%0.4f"%point['J']
#                        if 'K' in point:
#                                ret+="K%0.4f"%point['K']
                        if 'L' in point:
                                ret+="L%0.4f"%point['L']
                        # the x, y, and z are not accurate as it could be an arc, or bezier, but will probably be conservative
                        if 'F' in point:
                                ret+="F%0.4f"%point['F']
                        ret+="\n"
                if config['mode']=='gcode':
                        ret+="G64\n"
                return ret


	def _pre_render(self, pconfig):
		out=[]
		config=self.generate_config(pconfig)
		if not self.donePreRender and config['cutFromBack'] and (not 'mode' in config or config['mode']=='gcode'):
#			print "MODE="+str(config['mode'])
			self.donePreRender=True
			c=0	
			for p in self.points:
		#		print p.pos
				self.points[c].pos=V(p.pos[0],-p.pos[1])
				if hasattr(p, 'direction') and p.direction in ['cw','ccw']:
					self.points[c].direction=p.otherDir(p.direction)
				c+=1
		if 'step' not in config or not config['step']:
			config['step']=1.0
			
		if 'roughClearance' not in config or not config['roughClearance']==0:
			config['roughClearance'] = config['step']/2
		if( not self.shapelyPolygon):
			polygonised = self.polygonise( 1.0)
			points = []
			for p in polygonised:
				points.append(p)
			print points
			self.shapelyPolygon = shapely.geometry.LineString(points)
			self.rawPolygon = polygonised
		self.maxValues()
#		self.thePath = self.points
		if self.doRoughing and not self.doneRoughing:
			self.generateRouging(config)
			if self.clearFirst == 'z':
				self.insert_point(0, PSharp(V(self.points[0].pos[0] * self.flipSide, self.clearZ), isRapid=True))
				self.insert_point(0, PSharp(V(self.cuts[-1][0].pos[0] * self.flipSide, self.clearZ), isRapid=True))
			elif self.clearFirst == 'x':
				self.insert_point(0, PSharp(V(self.clearX * self.flipSide, self.points[0].pos[1] ), isRapid=True))
				self.insert_point(0, PSharp(V(self.clearX * self.flipSide, self.cuts[-1][0].pos[1] ), isRapid=True))
			if self.justRoughing:
				self.points=[]
			for cut in self.cuts:#[::-1]:
				self.add_points(cut, 'prepend')
			
			self.doneRoughing=True
		
	def spindle(self, direction):
		self.spindleDir = direction

	def generateRouging(self,  config):
		if config['latheMode']=='face':
			stepDir = V(-1,0)
			cutDir = V(0,-1)
			endRad = 0
			startRad = config['matRad']
			self.cutHandedness = 1			
			self.clearFirst = "z"
			self.clearZ = self.max[1] + config['matEnd']
			startZ = self.max[1] + config['matEnd']	
			endZ = self.minY#+config['roughClearance']
			roughing = self.findRoughingCuts( stepDir, cutDir, startZ, endZ, startRad, endRad, config)
		elif config['latheMode']=='bore':
			stepDir = V(1,0)
			cutDir = V(0,-1)
			startRad = self.min[0] + config['roughClearance']
			self.cutHandedness = -1			
			self.clearFirst = "z"
			self.clearZ = self.max[1] + config['matEnd']
			endRad = self.max[0]# - config['roughClearance']	
			startZ = self.max[1] + config['matEnd']

			endZ = self.min[1]# + config['roughClearance']	
			roughing = self.findRoughingCuts( stepDir, cutDir, startZ, endZ, startRad, endRad, config)
		elif config['latheMode']=='backBore':
			stepDir = V(1,0)
			cutDir = V(0,1)
			self.cutHandedness = -1			
			self.clearFirst = "z"
			self.clearZ = self.max[1] + config['matEnd']
			startRad = 0 #+ config['roughClearance']
			endRad = self.max[0]# - config['roughClearance']	
			startZ = self.min[1]# - config['matEnd']
			endZ = self.max[1] #- config['roughClearance']
			roughing = self.findRoughingCuts( stepDir, cutDir, startZ, endZ, startRad, endRad, config)
		elif config['latheMode']=='turn':
			cutDir=V(0,-1)
			stepDir = V(-1,0)
			startRad = config['matRad']
			endRad = self.min[0]# + config['roughClearance']
			startZ = self.max[1] + config['matEnd']	
			endZ = self.min[1]# + config['roughClearance']	
			self.cutHandedness = 1			
			self.clearFirst = "x"
			self.clearX = config['matRad'] + 2.0
			roughing = self.findRoughingCuts( stepDir, cutDir, startRad, endRad, startZ, endZ, config)
		elif config['latheMode']=='innerTurn':
			cutDir = V(0,-1)
			stepDir = V(1,0)
			startRad = self.min[0]
			endRad = self.max[0]# + config['roughClearance']
			startZ = self.max[1] + config['matEnd']	
			endZ = self.min[1]# + config['roughClearance']	
			self.cutHandedness = -1			
			self.clearFirst = "z"
			self.clearZ = self.max[1] + config['matEnd']
			roughing = self.findRoughingCuts( stepDir, cutDir, startRad, endRad, startZ, endZ, config)
		elif config['latheMode']=='backTurn':
			cutDir = V(1,0)
			self.clearFirst = "x"
			self.clearX = config['matRad'] + 2.0
			if(self.min[0]<0 and self.max[0]<0):
				startRad = -config['matRad']	
				stepDir=V(0,1)
				endRad = self.max[0]# - config['roughClearance']
			else:
				startRad = config['matRad']	
				stepDir=V(0,-1)
				endRad = self.min[0]# + config['roughClearance']
			self.cutHandedness = 1			

			endZ = self.max[1]# + config['roughClearance']
			startZ = self.min[1] 
			roughing = self.findRoughingCuts( stepDir, cutDir, startRad, endRad, startZ, endZ, config)
		if self.cutHandedness == config['handedness']:
			self.spindle('ccw')
			self.cuts.append(roughing)
			self.flipSide=1
		else:
			self.spindle('cw')
			for cut in roughing:
				cut.pos= V(-cut.pos[0], cut.pos[1])
			for cut in self.points:
				cut.pos= V(-cut.pos[0], cut.pos[1])
			self.flipSide=-1	
			self.cuts.append(roughing)
				
	def findRoughingCuts(self, stepDir, cutDir, startStep, endStep, startCut, endCut, config):
		cuts=[]
		numSteps = int(math.ceil(abs((endStep - startStep)/config['step'])))
		step = (endStep - startStep)/numSteps
		for i in range(1, numSteps+1):
			print str(startStep+i*step)+"  startCut="+str(startCut)+" endCut="+str(endCut) +" cutDir="+str(cutDir)+" stepDir="+str(stepDir)
			cuts+=self.findRoughingCut(startStep+i*step, cutDir, stepDir,startStep, startCut, endCut, config)
		return cuts
	def sign(self, x):
		if x<0:
			return -1
		if x>0:
			return 1
		return 0

	def findRoughingCut(self, val, direction, stepDir, startStep, startCut, endCut, config):
		if abs(stepDir.dot(V(1,0))>0.0001):
			print "stepX"+str(stepDir)
			alongCut = V(1,0) * self.sign(endCut-startCut)
			line = shapely.geometry.LineString([ [startCut, val], [ endCut, val] ])
			intersection = self.shapelyPolygon.intersection(line)
			if not intersection:
				intersection = V( endCut,val)
			elif type(intersection) is shapely.geometry.collection.GeometryCollection:
				intersection = V(intersection[0].x, intersection[0].y)
			elif type(intersection) is shapely.geometry.linestring.LineString:
				intersection = V(list(intersection.coords)[0][0],list(intersection.coords)[0][1] )
			elif type(intersection) is shapely.geometry.multipoint.MultiPoint:
				intersection = V(intersection[0].x, intersection[0].y)
			elif type(intersection) is Vec:
				intersection = intersection
			else:
				
				intersection = V(intersection.x, intersection.y)
			print "firstpoint"+str(V(startCut, val))+"->"+str(intersection - alongCut*config['roughClearance'])
			return [ PSharp(V(startCut, val)) 
				] + self.cutChipBreak( V(startCut, val), intersection - alongCut*config['roughClearance']) + [
#				PSharp(intersection - alongCut*config['roughClearance']),]  
				
				PSharp(intersection-stepDir*config['cutClear'] - alongCut*config['roughClearance'], isRapid=True), 
				PSharp(V(startCut, val)-stepDir*config['cutClear'], isRapid=True)
				]
		else:
			alongCut = V(0,1) * self.sign(endCut-startCut)
			off = val
			line = shapely.geometry.LineString([ [val, startCut], [ val, endCut] ])
			intersection = self.shapelyPolygon.intersection(line)
			if not intersection:
				intersection = V(val, endCut)
			else:
				intersection = V(intersection.x, intersection.y)
			return [
				PSharp(V(val, startCut))
				] + self.cutChipBreak ( V(val, startCut), intersection - alongCut*config['roughClearance'] ) + [ 
#				PSharp(intersection - alongCut*config['roughClearance']), 
				PSharp(intersection - stepDir*config['cutClear'] - alongCut*config['roughClearance'], isRapid=True), 
				PSharp(V(val, startCut) - stepDir*config['cutClear'], isRapid=True)
			]			
	def cutChipBreak(self, cutFrom, cutTo):
		print "chipbrea="+str(self.chipBreak)
		
		if hasattr(self, 'chipBreak') and self.chipBreak:
			chipBreak = self.chipBreak
		else:
			return [PSharp(cutFrom)]
		numCuts= int(math.ceil((cutTo-cutFrom).length() / chipBreak))
		step = (cutTo-cutFrom).length() / numCuts
		along = (cutTo-cutFrom).normalize()
		points=[]
		for i in range(1, numCuts+1):
			points.append(PSharp(cutFrom + along * (i * step) ) )
			points.append(PSharp(cutFrom + along * (i * step - 0.1) , isRapid=True) )
		return points
	def maxValues(self):
		maxX = -100000
		maxY = -100000
		minX = 100000
		minY = 100000
		for p in self.rawPolygon:
			if p[0]>maxX:
				maxX=p[0]
			if p[1]>maxY:
				maxY=p[1]
			if p[0]<minX:
				minX=p[0]
			if p[1]<minY:
				minY=p[1]
		self.min=V(minX, minY)
		self.max=V(maxX, maxY)


#class LatheFace(Path):
#	def __init__(self, pos):
		

		
