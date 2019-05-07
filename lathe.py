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
			
	def render(self, pconfig):
		nop

class LathePath(Path):
	def __init__(self, **config):
		self.init(config)
		
	def init(self, config):
		self.shapelyPolygon=False
		super().init(self, config)

	def render(self, pconfig):
		out=[]
		config=self.generate_config(pconfig)
		if side=='in':
			stepDir=1
		else:
			stepDir=-1

	
	def generateRouging(self,  **config):
		if config['latheMode']=='face':
			stepDir=V(-1,0)
		else:
			if self.side=='in':
				stepDir=V(0,1)
			else:
				stepDir=V(0,-1)
		

	def findRoughingCut(self, val, direction, step, config):
		if(!self.shapelyPolygon):
			polygonised = self.polygonise(self, 1)
			points = []
			for p in polygonised:
				points.append(p.pos)
			self.shapelyPolygon = shapely.geometry.LineString(points)
		zstart = config['z0']
		xstart = config['x0']
		xend = config['xEnd']
		
		if abs(stepDir.dot(V(0,1)):	
			off = val*stepDir.dot(V(0,1))	
			line = shapely.geometry.LineString([ [xstart, zstart+off], [ xstart+direction*10000, zstart+off] ])
			intersection = self.shapelyPolygon.intersection(line)
			return [V(xstart, zstart+off), intersection, V(xstart, zstart+off)]
		else:
			off = val*stepDir.dot(V(1,0))
			line = shapely.geometry.LineString([ [xstart+off), zstart], [ xstart+off), zstart*10000] ])
			intersection = self.shapelyPolygon.intersection(line)
			return [V(xstart+off), zstart), intersection, V(xstart+off, zstart)]			
		

class LatheFace(Path):
	def __init__(self, pos):
		

		
