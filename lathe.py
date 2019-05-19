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
	def _pre_render(self, config):
		if('matEnd' not in config):
			self.materialEnd = 3
			
			

class LathePath(Path):
	def __init__(self, **config):
		self.varlist=['roughClearance', 'matEnd', 'latheMode', 'matRad', 'step', 'cutClear']
		self.init(config)
		self.closed=False
		self.side='on'
		
	def init(self, config):
		self.shapelyPolygon=False
		super(LathePath, self).init(config)
		self.cuts=[]
		if 'doRoughing' in config and config['doRoughing'] is not None:
			self.doRoughing= config['doRoughing']
		else:
			self.doRoughing=True
	def _pre_render(self, pconfig):
		out=[]
		config=self.generate_config(pconfig)
		if 'step' not in config or not config['step']:
			config['step']=1.0
			
		if 'roughClearance' not in config or not config['roughClearance']==0:
			config['roughClearance'] = config['step']/2
		if( not self.shapelyPolygon):
			polygonised = self.polygonise( 1.0)
			points = []
			for p in polygonised:
				points.append(p)
			self.shapelyPolygon = shapely.geometry.LineString(points)
			self.rawPolygon = polygonised
		self.maxValues()
		print "min="+str(self.min)
		print "max="+str(self.max)
		if self.doRoughing:
			self.generateRouging(config)
			for cut in self.cuts[::-1]:
				self.add_points(cut, 'start')
		

	def generateRouging(self,  config):
		if config['latheMode']=='face':
			stepDir = V(-1,0)
			cutDir = V(0,-1)
			endRad = 0
			startRad = config['matRad']
			
			startZ = config['matEnd']	
			endZ = self.minY+config['roughClearance']
			self.cuts.append(self.findRoughingCuts( stepDir, cutDir, startZ, endZ, startRad, endRad, config))
		elif config['latheMode']=='bore':
			stepDir = V(0,1)
			cutDir = V(0,1)
			startRad = 0
			endRad = self.max[0] - config['roughClearance']	
			startZ = self.max[1] + config['matEnd']
			endZ = self.min[1] + config['roughClearance']	
			self.cuts.append(self.findRoughingCuts( stepDir, cutDir, startRad, endRad, startZ, endZ, config))
		elif config['latheMode']=='turn':
			stepDir=V(0,-1)
			cutDir = V(-1,0)
			startRad = config['matRad']
			endRad = self.min[0] + config['roughClearance']
			startZ = self.max[1] + config['matEnd']	
			endZ = self.min[1] + config['roughClearance']	
			self.cuts.append(self.findRoughingCuts( stepDir, cutDir, startRad, endRad, startZ, endZ, config))
		elif config['latheMode']=='backTurn':
			stepDir=V(0,-1)
			cutDir = V(1,0)
			startRad = config['matRad']	
			endRad = self.min[0] + config['roughClearance']
			endZ = config['matEnd']	- config['roughClearance']
			startZ = self.min[1] 
			self.cuts.append(self.findRoughingCuts( stepDir, cutDir, startRad, endRad, startZ, endZ, config))

	def findRoughingCuts(self, stepDir, cutDir, startStep, endStep, startCut, endCut, config):
		cuts=[]
		print "find ROUGHING CUTS"
		print startCut
		print endCut
		numSteps = int(math.ceil(abs((endStep - startStep)/config['step'])))
		step = (endStep - startStep)/numSteps
		for i in range(1, numSteps+1):
		#	print startStep+i*step
			cuts+=self.findRoughingCut(startStep+i*step, cutDir, stepDir,startStep, startCut, endCut, config)
		return cuts
	def sign(self, x):
		if x<0:
			return -1
		if x>0:
			return 1
		return 0

	def findRoughingCut(self, val, direction, stepDir, startStep, startCut, endCut, config):
		if abs(stepDir.dot(V(0,1))>0.0001):	
			alongCut = V(1,0) * self.sign(endCut-startCut)
			line = shapely.geometry.LineString([ [startCut, val], [ endCut, val] ])
			intersection = self.shapelyPolygon.intersection(line)
			
			if not intersection:
				intersection = V( endCut,val)
			else:
				intersection = V(intersection.x, intersection.y)
			return [
				PSharp(V(startCut, val)),
				PSharp(intersection - alongCut*config['cutClear']), 
				PSharp(intersection-stepDir*config['cutClear'] - alongCut*config['cutClear']), 
				PSharp(V(startCut, val)-stepDir*config['cutClear'])
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
				print "Intersection = "+str(intersection)
			return [
				PSharp(V(val, startCut)), 
				PSharp(intersection - alongCut*config['cutClear']), 
				PSharp(intersection - stepDir*config['cutClear'] - alongCut*config['cutClear']), 
				PSharp(V(val, startCut) - stepDir*config['cutClear'])
			]			
		
	def maxValues(self):
		maxX = -100000
		maxY = -100000
		minX = 100000
		minY = 100000
		for p in self.rawPolygon:
			print p
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
		

		
