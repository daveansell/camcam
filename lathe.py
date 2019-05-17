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
	def __init__(self, pos, **config):
		self.init(config)

	def init(self, config):
		if('materialEnd' in config):
			self.materialEnd = config['materialEnd']
		else:
			self.materialEnd = 3
		if('materialRad' in config):
			self.materialRad = config['materialRad']
		super().init(self, config)
			
			

class LathePath(Path):
	def __init__(self, **config):
		self.init(config)
		
	def init(self, config):
		self.shapelyPolygon=False
		super().init(self, config)
		self.cuts=[]

	def _pre_render(self, pconfig):
		out=[]
		config=self.generate_config(pconfig)
		self.maxValues()
		if side=='in':
			stepDir=1
		else:
			stepDir=-1
		if 'roughClearance' not in config or not config['roughClearance']==0:
			config['roughClearance'] = config['step']/2
		self.generateRouging(config)
		for cut in self.cuts.reversed():
			self.add_points(cut, 'start')
		

	def generateRouging(self,  **config):
		if config['latheMode']=='face':
			stepDir = V(-1,0)
			cutDir = V(0,-1)
			startRad = config['matRad']
			startZ = config['matEnd']	
			endZ = self.minY+config['roughClearance']
			self.cuts.append(self.findRoughingCuts(self, stepDir, cutDir, startZ, endZ, startRad, config))
		elif config['latheMode']=='bore':
			stepDir = V(0,1)
			cutDir = V(0,1)
			startRad = 0
			endRad = self.maxX - config['roughClearance']	
			startZ = config['matEnd']	
			self.cuts.append(self.findRoughingCuts(self, stepDir, cutDir, startRad, endRad, startZ, config))
		elif config['latheMode']=='turn':
			stepDir=V(0,-1)
			cutDir = V(-1,0)
			startRad = config['matRad']
			endRad = self.minX + config['roughClearance']
			startZ = config['matEnd']	
			self.cuts.append(self.findRoughingCuts(self, stepDir, cutDir, startRad, endRad, startZ, config))
		elif config['latheMode']=='backTurn':
			stepDir=V(0,-1)
			cutDir = V(1,0)
			startRad = config['matRad']	
			endRad = self.minX + config['roughClearance']
			startZ = config['matEnd']	
			self.cuts.append(self.findRoughingCuts(self, stepDir, cutDir, startRad, endRad, startZ, config))
	
	def maxValues(self):
		maxX = -100000
		maxY = -100000
		minX = 100000
		minY = 100000
		for p in self.polygon:
			if p[0]>maxX:
				maxX=p[0]
			if p[1]>maxY:
				maxy=p[1]
			if p[0]<minX:
				minX=p[0]
			if p[1]<minY:
				minY=p[1]
		self.min=V(minX, minY)
		self.max=V(maxX, maxY)

	def findRoughingCuts(self, stepDir, cutDir, startStep, endStep, startCut, config):
		cuts=[]
		numSteps = math.ceil((endStep - startStep)/config['step'])
		step = (endStep - startStep)/numSteps
		for i in range(1, numSteps+1):
			cuts+=findRoughingCut(startStep+i*step, cutDir, stepDir, config)
		return cuts

	def findRoughingCut(self, val, direction, stepDir, config):
		if( not self.shapelyPolygon):
			polygonised = self.polygonise(self, 1)
			points = []
			for p in polygonised:
				points.append(p.pos)
			self.shapelyPolygon = shapely.geometry.LineString(points)
		zstart = config['z0']
		xstart = config['x0']
		xend = config['xEnd']
		
		if abs(stepDir.dot(V(0,1))>0.0001):	
			off = val*stepDir.dot(V(0,1))	
			line = shapely.geometry.LineString([ [xstart, zstart+off], [ xstart+direction*10000, zstart+off] ])
			intersection = self.shapelyPolygon.intersection(line)
			return [V(xstart, zstart+off), intersection, V(xstart, zstart+off)]
		else:
			off = val*stepDir.dot(V(1,0))
			line = shapely.geometry.LineString([ [xstart+off, zstart], [ xstart+off, zstart*10000] ])
			intersection = self.shapelyPolygon.intersection(line)
			return [PSharp(V(xstart+off, zstart)), PSharp(intersection), PSharp(intersection - stepDir*config['cutClear']), PSharp(V(xstart+off, zstart) - stepDir*config['cutClear'])]			
		

#class LatheFace(Path):
#	def __init__(self, pos):
		

		
