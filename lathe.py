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
                self.varlist=['roughClearance', 'matEnd', 'latheMode', 'matRad', 'step', 'cutClear', 'handedness', 'cutFromBack', "spindleDir", "chipBreak", "justRouging", "cutHandedness", "doRoughing"]
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
                for p in self.points:
                                print( p.pos)

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
                print ("START PRE RENDER")
                for p in self.points:
                                print( p.pos)
                out=[]
                config=self.generate_config(pconfig)
                if not self.donePreRender and config['cutFromBack'] and (not 'mode' in config or config['mode']=='gcode'):
                        self.donePreRender=True
                        c=0
                        for p in self.points:
                                print("invert along z-"+str( p.pos))
                                self.points[c].pos=V(p.pos[0],-p.pos[1])
                                if hasattr(p, 'direction') and p.direction in ['cw','ccw']:
                                        self.points[c].direction=p.otherDir(p.direction)
                                c+=1
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
                        if self.doRoughing:
                                fs = self.flipSide
                                if self.clearFirst == 'z':
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
                                        self.insert_point(0, PSharp(V(self.points[0].pos[0], self.clearZ), isRapid=True))
                                        self.insert_point(0, PSharp(V(self.clearX * self.flipSide, self.clearZ), isRapid=True))
                                        self.add_point( PSharp(V(self.points[-1].pos[0], self.clearZ), isRapid=True))
                                        self.add_point( PSharp(V(self.clearX * self.flipSide, self.clearZ), isRapid=True))
                                elif self.clearFirst == 'x':
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
                        print("Wrong handedness")
                        for cut in roughing:
                                cut.pos= V(-cut.pos[0], cut.pos[1])
                                print (cut)
                                if hasattr(cut, 'direction') and cut.direction in ['cw','ccw']:
                                        print("flip direction")
                                        cut.direction=cut.otherDir(cut.direction)
                        self.flipSide=-1        
                        self.cuts.append(roughing)
#                       print self.cuts
                                
#        def findRoughingCuts(self, stepDir, cutDir, startStep, endStep, startCut, endCut, config):
#                cuts=[]
#                numSteps = int(math.ceil(abs((endStep - startStep)/config['step'])))
#                step = (endStep - startStep)/numSteps
##               print "stepDir="+str(stepDir)+" cutDir="+str(cutDir)+" numSteps"+str(numSteps)
#                for i in range(1, numSteps+1):
#                        #print str(startStep+i*step)+"  startCut="+str(startCut)+" endCut="+str(endCut) +" cutDir="+str(cutDir)+" stepDir="+str(stepDir)
#                        cuts+=self.findRoughingCut(startStep+i*step, cutDir, stepDir,startStep, startCut, endCut, config)
##               for p in  cuts:
##                       print p.pos
#                return cuts
        def findRoughingCuts2(self, stepDir, cutDir, startStep, endStep, startCut, endCut, config):
                cuts=[]
                numSteps = int(math.ceil(abs((endStep - startStep)/config['step'])))
                step = (endStep - startStep)/numSteps

#               print "stepDir="+str(stepDir)+" cutDir="+str(cutDir)+" numSteps"+str(numSteps)
        #        for i in range(1, numSteps+1):
                        #print str(startStep+i*step)+"  startCut="+str(startCut)+" endCut="+str(endCut) +" cutDir="+str(cutDir)+" stepDir="+str(stepDir)
                cuts+=self.findRoughingCut2(startStep, cutDir, stepDir, False, startCut, endCut, step, endStep, config)
 #               for p in  cuts:
#                       print( p.pos)
                return cuts
        def sign(self, x):
                if x<0:
                        return -1
                if x>0:
                        return 1
                return 0
        def convertIntersection(self, intersection, default):
                        #print type(intersection)
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
                       #         print (len(intersection))
                                for i in range(0,len(intersection)):
                        #            print (intersection[i])
                                    intersection2.append(V(intersection[i].x, intersection[i].y))
                                
                                intersection = intersection2
                        #        intersection = V(intersection[0].x, intersection[0].y)
                      #          print("multipoint="+str(intersection))
                        elif type(intersection) is Vec:
                                intersection = intersection
                        elif type(intersection) is shapely.geometry.multilinestring.MultiLineString:
                                intersection = V(list(intersection[0].coords)[0][0], list(intersection[0].coords)[0][1])

                        else:
                                #print intersection
                                intersection = V(intersection.x, intersection.y)
                        return intersection


        

        def findIntersection(self, line, endCut, val):
                intersection = self.shapelyPolygon.intersection(shapely.geometry.linestring.LineString(line))
                intersection = self.convertIntersection(intersection, V( endCut,val))
                return intersection

        def findRoughingCut2(self, val, direction, stepDir, intersected, startCut, endCut, step, endStep, config):
              #  print ("find RoughingCuts"+str([val, direction, stepDir, intersected, startCut, endCut, endStep, step]))
                if step<0:
                    if val<endStep:
                        return []
                else:
                    if val>endStep:
                        return []
                if abs(stepDir.dot(V(0,1)))>0.0001:
                        #print "FACE"
                        #print [val, direction, stepDir, intersected, startCut, endCut]
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
                    print ("bleep")
                    if intersected:
                        return []
                    else:
                        intersection = default
                else:
                    intersected = True
                if not type(intersection) is list:
                    intersection = [intersection]

                print ("final intersection="+str(intersection))
                if type(intersection) is list:
                            def keyfunc(a):
                                return a.dot(alongCut)
                            intersection.sort(key=keyfunc)
                            ret = []
                            p=0
                            if len(intersection)%2==1:
                                #ret+=  [PSharp(startCut*alongAxis+ val*stepAxis) ]+ 
                                nextcuts=self.findRoughingCut2( val+step, direction, stepDir, intersected, startCut, intersection[p].dot(alongAxis), step, endStep,  config)
                                ret+=self.cutChipBreak(
                                        startCut*alongAxis+ val*stepAxis,
                                        intersection[p]+stepDir*config['cutClear'] - alongCut*config['roughClearance']
                                    )
                                if len(nextcuts):
                                     ret+=[
                                        PSharp(nextcuts[0].pos+stepDir*step, isRapid=True)
                                    ]+nextcuts
                                #ret.append(
                                 #   PSharp(val*stepAxis+ ret[-1].pos.dot(alongAxis) - stepDir*(step+config['cutClear']), isRapid=True)
                                #)
                                
                                p+=1
                            while p<len(intersection):
                                nextcuts=self.findRoughingCut2( val+step, direction, stepDir, True, intersection[p].dot(alongAxis), intersection[p+1].dot(alongAxis), step, endStep, config)
# move to one step outside the start position
                                #ret.append(PSharp(intersection[p] - stepDir*(step+config['cutClear']), isRapid=True))
# cut down to the start position
                                ret+= [ PSharp(intersection[p] - stepDir*config['cutClear'] + alongCut*config['roughClearance']) ] \
                                    + [PSharp(intersection[p+1] - stepDir*config['cutClear'] - alongCut*config['roughClearance'])]
# cut along the cut we want to make
                                   #     +self.cutChipBreak(
                                    #        intersection[p] - stepDir*config['cutClear'] + alongCut*config['roughClearance'],
                                     #       intersection[p+1] - stepDir*config['cutClear'] - alongCut*config['roughClearance']
                                      #  )+[
# move out to clear part
                                if len(nextcuts):
                                        ret+= [PSharp(nextcuts[0].pos+step*stepDir, isRapid=True)
                                    ] + nextcuts
# make any more cuts in this section
# move one step out in case we need to move to another section
                                #ret.append(
                                #    PSharp(val*stepAxis+ ret[-1].pos.dot(alongAxis) - stepDir*(step+config['cutClear']), isRapid=True)
                                #)

                                p+=2
                return ret


#        def findRoughingCut(self, val, direction, stepDir, startStep, startCut, endCut, config):
#                if abs(stepDir.dot(V(0,1)))>0.0001:
#                        #print "FACE"
#                        #print [val, direction, stepDir, startStep, startCut, endCut]
#                        alongCut = V(1,0) * self.sign(endCut-startCut)
##                       intersection = self.findIntersection( [ [startCut, val], [ endCut, val] ], endCut, val)
#                        line = shapely.geometry.LineString([ [ startCut, val], [ endCut, val] ])
#                        intersection = self.shapelyPolygon.intersection(line)
#                        #print line
#                        #print self.shapelyPolygon
#                        print (intersection)
#                        intersection = self.convertIntersection(intersection, V( endCut, val))
#
#                        if type(intersection) is list:
#                            intersection = intersection[0]
#
#                        #print "intesection="+str(intersection)
#                        #print " chibpra=" +str(self.cutChipBreak( V(startCut, val), intersection - alongCut*config['roughClearance'])[0].pos)
#                            #print ([intersection, stepDir,config['cutClear'] ,alongCut,config['roughClearance']])
#                        return [ PSharp(V(startCut, val)) 
#                                ] + self.cutChipBreak( V(startCut, val), intersection - alongCut*config['roughClearance']) + [
##                               PSharp(intersection - alongCut*config['roughClearance']),]  
#                                
#                                PSharp(intersection-stepDir*config['cutClear'] - alongCut*config['roughClearance'], isRapid=True), 
#                                PSharp(V(startCut, val)-stepDir*config['cutClear'], isRapid=True)
#                                ]
#                else:
#                        alongCut = V(0,1) * self.sign(endCut-startCut)
#                        off = val
#                        line = shapely.geometry.LineString([ [val, startCut], [ val, endCut] ])
#                        intersection = self.shapelyPolygon.intersection(line)
#                        print(intersection)
 #                       intersection = self.convertIntersection(intersection, V( val, endCut))
 #                       if type(intersection) is list:
 #                           intersection = intersection[0]
##                       if not intersection:
##                               intersection = V(val, endCut)
##                       else:
##                               intersection = V(intersection.x, intersection.y)
 #                       return [
 #                               PSharp(V(val, startCut))
 #                               ] + self.cutChipBreak ( V(val, startCut), intersection - alongCut*config['roughClearance'] ) + [ 
##                               PSharp(intersection - alongCut*config['roughClearance']), 
 #                               PSharp(intersection - stepDir*config['cutClear'] - alongCut*config['roughClearance'], isRapid=True), 
 #                               PSharp(V(val, startCut) - stepDir*config['cutClear'], isRapid=True)
 #                       ]                       
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


#class LatheFace(Path):
#       def __init__(self, pos):
                

                
