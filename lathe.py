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
                self.closed='raw'
                self.side='on'
                self.downmode='none'
        
        def init(self, config):
                self.varlist=['roughClearance', 'matEnd', 'latheMode', 'matRad', 'step', 'cutClear', 'handedness', 'cutFromBack', "spindleDir", "chipBreak", "justRouging", "cutHandedness", "doRoughing", 'donePreRender']
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
                print ("START PRE RENDER"+str(self))
#                for p in self.points:
 #                               print( p.pos)
                out=[]
                config=self.generate_config(pconfig)
                if self.donePreRender:
                    return
  #              for p in self.points:
   #                 print("p-"+str( p.pos))
                if not self.donePreRender and config['cutFromBack'] and (not 'mode' in config or config['mode']=='gcode'):
                        c=0
                        for p in self.points:
                                self.points[c].pos=V(p.pos[0],-p.pos[1])
                                if hasattr(p, 'direction') and p.direction in ['cw','ccw']:
                                        self.points[c].direction=p.otherDir(p.direction)
                                c+=1
                self.donePreRender=True
                if 'step' not in config or not config['step']:
                        config['step']=1.0
                        
                if 'roughClearance' not in config or not config['roughClearance']==0:
                        config['roughClearance'] = config['step']/2
                if( not self.shapelyPolygon):
                        self.makeShapely(0.1)
                      #  polygonised = self.polygonise( 1.0)
                       # points = []
                        #for p in polygonised:
                         #       points.append(p)
                        #self.shapelyPolygon = shapely.geometry.LineString(points)
                        #self.rawPolygon = polygonised
                self.maxValues()
                if not self.doneRoughing:
#               self.thePath = self.points
                        self.generateRouging(config)
                        if self.cutHandedness != config['handedness']:
                                for cut in self.points:
                                        cut.pos= V(-cut.pos[0], cut.pos[1])
                                        if hasattr(cut, 'direction'):
                                            cut.direction = cut.otherDir(cut.direction)
                                self.spindle('cw')
                                self.flipSide=-1        
                        else:
                                self.spindle('ccw')
                                self.flipSide=1 
                       # if self.flipSide==-1:
                        #    c=0
                         #   for p in self.points:
                          #      print("invert along x-"+str( p.pos))
                           #     self.points[c].pos=V(-p.pos[0],p.pos[1])
                            #    if hasattr(p, 'direction') and p.direction in ['cw','ccw']:
                             #           self.points[c].direction=p.otherDir(p.direction)
                              #  c+=1
        # if we are doing roughing add going to a safe position to the cut
                        if len(self.cuts) and len(self.cuts[0]) and self.doRoughing:
                                
                                fs = self.flipSide
                                if self.clearFirst == 'z':
                                       # print(len(self.cuts))
                                        self.cuts[0].insert(0, PSharp(V(self.cuts[0][0].pos[0] , self.clearZ), isRapid=True))
                                        self.cuts[0].insert(0, PSharp(V(self.clearX * fs, self.clearZ), isRapid=True))
                                        self.cuts[-1].append( PSharp(V(self.cuts[-1][-1].pos[-1] , self.clearZ), isRapid=True))
                                        self.cuts[-1].append( PSharp(V(self.clearX * fs, self.clearZ), isRapid=True))
                                elif self.clearFirst == 'x':
                                        self.cuts[0].insert(0, PSharp(V(self.clearX * fs, self.cuts[0][0].pos[1] ), isRapid=True))
                                        self.cuts[0].insert(0, PSharp(V(self.clearX * fs, self.clearZ ), isRapid=True))
                                        self.cuts[-1].append( PSharp(V(self.clearX * fs, self.cuts[-1][-1].pos[1] ), isRapid=True))
                                        self.cuts[-1].append( PSharp(V(self.clearX * fs, self.clearZ ), isRapid=True))

                        if not self.justRoughing:
                                if self.clearFirst == 'z':
                                        #print("clearZ")
                                        self.insert_point(0, PSharp(V(self.points[0].pos[0], self.clearZ), isRapid=True))
                                        self.insert_point(0, PSharp(V(self.clearX * self.flipSide, self.clearZ), isRapid=True))
                                        self.add_point( PSharp(V(self.points[-1].pos[0], self.clearZ), isRapid=True))
                                        self.add_point( PSharp(V(self.clearX * self.flipSide, self.clearZ), isRapid=True))
                                elif self.clearFirst == 'x':
                                        #print("clearX")
                                        self.insert_point(0, PSharp(V(self.clearX * self.flipSide, self.points[0].pos[1] ), isRapid=True))
                                        self.insert_point(0, PSharp(V(self.clearX * self.flipSide, self.clearZ), isRapid=True))
                                        self.add_point( PSharp(V(self.clearX * self.flipSide, self.points[-1].pos[1] ), isRapid=True))
                                        self.add_point( PSharp(V(self.clearX * self.flipSide, self.clearZ), isRapid=True))
                                        
                        if self.justRoughing:
                                self.points=[]
                        if self.doRoughing:
                                for cut in self.cuts:#[::-1]:
                                        self.add_points(cut, 'prepend')
                self.doneRoughing=True
                
        def spindle(self, direction):
                self.spindleDir = direction

        def generateRouging(self,  config):
                if config['latheMode']=='face':
                        stepDir = V(0,-1)
                        cutDir = V(-1,0)
                        endRad = 0
                        startRad = config['matRad']
                        self.cutHandedness = 1                  
                        self.clearFirst = "z"
                        self.clearZ = self.max[1] + config['matEnd']
                        self.clearX = config['matRad']+1.0
                        startZ = self.max[1] + config['matEnd'] 
                        endZ = self.min[1]+config['roughClearance']
                        roughing = self.findRoughingCuts2( stepDir, cutDir, startZ, endZ, startRad, endRad, config)

                elif config['latheMode']=='bore':
                        stepDir = V(1,0)
                        cutDir = V(0,-1)
                        startRad = self.min[0] + config['roughClearance']
                        self.cutHandedness = -1                 
                        self.clearFirst = "z"
                        self.clearZ = self.max[1] + config['matEnd']
                        self.clearX = 0.0
                        endRad = self.max[0]# - config['roughClearance']        
                        startZ = self.max[1] + config['matEnd']
                        endZ = self.min[1] + config['roughClearance']   
                        roughing = self.findRoughingCuts2( stepDir, cutDir, startRad, endRad, startZ, endZ, config)

                elif config['latheMode']=='boreface':
                        stepDir = V(0,-1)
                        cutDir = V(1,0)
                        startRad = self.min[0] + config['roughClearance'] 
                        endRad = self.max[0] 
                        self.cutHandedness = -1                 
                        self.clearFirst = "z"
                        self.clearZ = self.max[1] + config['matEnd']
                        self.clearX = 0.0
                        endRad = self.max[0]# - config['roughClearance']        
                        startZ = self.max[1] + config['matEnd']
                        endZ = self.min[1]# + config['roughClearance']  
                        roughing = self.findRoughingCuts2( stepDir, cutDir, startZ, endZ, startRad, endRad, config)

                elif config['latheMode']=='backBore':
                        stepDir = V(1,0)
                        cutDir = V(0,1)
                        self.cutHandedness = -1                 
                        self.clearFirst = "z"
                        self.clearZ = self.max[1] + config['matEnd']
                        self.clearX = 0.0
                        startRad = 0 #+ config['roughClearance']
                        endRad = self.max[0]# - config['roughClearance']        
                        startZ = self.min[1]# - config['matEnd']
                        endZ = self.max[1] #- config['roughClearance']
                        roughing = self.findRoughingCuts2( stepDir, cutDir, startZ, endZ, startRad, endRad, config)
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
                        self.clearZ = self.max[1]+config['matEnd']
                        roughing = self.findRoughingCuts2( stepDir, cutDir, startRad, endRad, startZ, endZ, config)
                elif config['latheMode']=='backTurn':
                        cutDir = V(1,0)
                        self.clearFirst = "x"
                        self.clearX = config['matRad'] + 2.0
                        self.clearZ = self.max[1]+config['matEnd']
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
                        roughing = self.findRoughingCuts2( stepDir, cutDir, startRad, endRad, startZ, endZ, config)
                if self.cutHandedness == config['handedness']:
                        self.cuts.append(roughing)
                        self.flipSide=1
                else:
                        for cut in roughing:
                                cut.pos= V(-cut.pos[0], cut.pos[1])
                                if hasattr(cut, 'direction') and cut.direction in ['cw','ccw']:
                                        #print("flip direction")
                                        cut.direction=cut.otherDir(cut.direction)
                        self.flipSide=-1        
                        self.cuts.append(roughing)

        def findRoughingCuts2(self, stepDir, cutDir, startStep, endStep, startCut, endCut, config):
                cuts=[]
                numSteps = int(math.ceil(abs((endStep - startStep)/config['step'])))
                if numSteps == 0:
                    step = 1
                else:
                    step = (endStep - startStep)/numSteps

                cuts+=self.findRoughingCut2(startStep, cutDir, stepDir, False, startCut, endCut, step, endStep, config)
                return cuts

        def sign(self, x):
                if x<0:
                        return -1
                if x>0:
                        return 1
                return 0

        def convertIntersection(self, intersection, default):
                        if not intersection:
                                intersection = default#V( endCut,val)
                        elif type(intersection) is shapely.geometry.collection.GeometryCollection:
                                intersection = V(intersection[0].x, intersection[0].y)
                        elif type(intersection) is shapely.geometry.linestring.LineString:
                                if intersection.is_empty:
                                    intersection = None
                                else:
                                    intersection = V(list(intersection.coords)[0][0],list(intersection.coords)[0][1] )
                        elif type(intersection) is shapely.geometry.multipoint.MultiPoint:
                                intersection2 = []
                                for i in range(0,len(intersection)):
                                    intersection2.append(V(intersection[i].x, intersection[i].y))
                                
                                intersection = intersection2
                        elif type(intersection) is Vec:
                                intersection = intersection
                        elif type(intersection) is shapely.geometry.multilinestring.MultiLineString:
                                intersection = V(list(intersection[0].coords)[0][0], list(intersection[0].coords)[0][1])

                        else:
                                intersection = V(intersection.x, intersection.y)
                        return intersection


        

        def findIntersection(self, line, endCut, val):
                intersection = self.shapelyPolygon.intersection(shapely.geometry.linestring.LineString(line))
                intersection = self.convertIntersection(intersection, V( endCut,val))
                return intersection

        def findRoughingCut2(self, val, direction, stepDir, intersected, startCut, endCut, step, endStep, config):
                if step<0:
                    if val<endStep:
                        return []
                else:
                    if val>endStep:
                        return []
                if abs(stepDir.dot(V(0,1)))>0.0001:
                        alongCut = V(1,0) * self.sign(endCut-startCut)
                        alongAxis = V(1,0)
                        stepAxis = V(0,1)
#                       intersection = self.findIntersection( [ [startCut, val], [ endCut, val] ], endCut, val)
                        line = shapely.geometry.LineString([ [ startCut, val], [ endCut, val] ])
                else:
                        alongCut = V(0,1) * self.sign(endCut-startCut)
                        alongAxis = V(0,1)
                        stepAxis = V(1,0)
                        off = val
                        line = shapely.geometry.LineString([ [val, startCut], [ val, endCut] ])
                intersection = self.shapelyPolygon.intersection(line)
                default = endCut*alongAxis + val * stepAxis
                intersection = self.convertIntersection(intersection, None)
# if we get no intersection we might have gone past line or have not got there yet
                if intersection is None:
                    if intersected:
                        return []
                    else:
                        intersection = default
                else:
                    intersected = True
                if not type(intersection) is list:
                    intersection = [intersection]

                if type(intersection) is list:
                            def keyfunc(a):
                                return a.dot(alongCut)
                            intersection.sort(key=keyfunc)
                            ret = []
                            p=0
                            if len(intersection)%2==1:
                                print ("ODD QQ"+self.clearFirst)
 #                               ret+=  [PSharp(startCut*alongAxis+ val*stepAxis) ]  
                                nextcuts=self.findRoughingCut2( val+step, direction, stepDir, intersected, startCut, intersection[p].dot(alongAxis), step, endStep,  config)
                                theCut=self.cutChipBreak(
                                        startCut*alongAxis+ val*stepAxis,
                                        intersection[p]+stepDir*config['cutClear'] - alongCut*config['roughClearance']
                                    )
                                if len(nextcuts):
                                     ret+= theCut+[
                                        PSharp(nextcuts[0].pos+stepDir*step*2, isRapid=True)
                                    ]+nextcuts +[PSharp(nextcuts[-1].pos+step*stepDir*2, isRapid=True)
                                    ] 
                                #ret.append(
                                 #   PSharp(val*stepAxis+ ret[-1].pos.dot(alongAxis) + stepAxis*(config['cutClear']), isRapid=True)
                                #)
                                
                                p+=1
                            while p<len(intersection):
                                print ("EVEN QQ"+self.clearFirst)
                                nextcuts=self.findRoughingCut2( val+step, direction, stepDir, True, intersection[p].dot(alongAxis), intersection[p+1].dot(alongAxis), step, endStep, config)
# move to one step outside the start position
#                                ret.append(PSharp(intersection[p] - stepDir*(step+config['cutClear']), isRapid=True))
# cut down to the start position
# cut along the cut we want to make
                                ret+= [ PSharp(intersection[p] - stepDir*config['cutClear'] + alongCut*config['roughClearance']) ] \
                                        + self.cutChipBreak(
                                            intersection[p] - stepDir*config['cutClear'] + alongCut*config['roughClearance'],
                                            intersection[p+1] - stepDir*config['cutClear'] - alongCut*config['roughClearance']
                                        )
# move out to clear part
                                if len(nextcuts):
                                        ret+= [PSharp(nextcuts[0].pos+step*stepDir*2, isRapid=True)
                                    ] + nextcuts + [PSharp(nextcuts[-1].pos+step*stepDir*2, isRapid=True)]
                                     
# make any more cuts in this section
# move one step out in case we need to move to another section
                                #ret.append(
                                #    PSharp(val*stepAxis+ ret[-1].pos.dot(alongAxis) - stepDir*(step+config['cutClear']), isRapid=True)
                                #)

                                p+=2
                return ret


        def cutChipBreak(self, cutFrom, cutTo):
                
                if hasattr(self, 'chipBreak') and self.chipBreak:
                        chipBreak = self.chipBreak
                else:
                        return [PSharp(cutFrom)]
                numCuts= int(math.ceil((cutTo-cutFrom).length() / chipBreak))
                if numCuts>0:
                    step = (cutTo-cutFrom).length() / numCuts
                else:
                    step = (cutTo-cutFrom).length()
                along = (cutTo-cutFrom).normalize()
                points=[]
                for i in range(1, numCuts+1):
                        points.append(PSharp(cutFrom + along * (i * step) ) )
                        points.append(PSharp(cutFrom + along * (i * step - 0.2) , isRapid=True) )
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

        def render(self,pconfig):
                global spindleDir

                out=[]
                config=self.generate_config(pconfig)
                if config['mode']=='gcode' and hasattr(self, 'spindleDir') and self.spindleDir and spindleDir != self.spindleDir:
                        if spindleDir is None:
                                time = "5"
                        else:
                                time = "10"
                        if self.spindleDir=='ccw':
                                out.append('M04S'+str(config['spindleRPM'])+'\n')#G04p'+time+'\n')
                        elif self.spindleDir=='cw':
                                out.append('M03S'+str(config['spindleRPM'])+'\n')#G04p'+time+'\n')
                        spindleDir = self.spindleDir

                self.output_path(config)
                out.append( self.render_path(self,config))
                if 'partcutter' in config and config['partcutter'] is not None:
                    key = config['partcutter']
                else:
                    key = config['cutter']
                return [key,out]

#class LatheFace(Path):
#       def __init__(self, pos):
                

                
