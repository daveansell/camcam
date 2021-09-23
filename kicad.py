#!/usr/bin/env python

import sys
import math
from kicad_pcb import *
from  path import *
from point import *
from shapes import *
import re

class Kicad:
    def __init__(self, filename):
        self.pcb = KicadPCB.load(filename)
# check for error
        for e in self.pcb.getError():
            print('Error: {}'.format(e))

    def getModules(self, modulePrefix=None, moduleName=None, output='simple'):
        positions=[]
        for module in self.pcb.module:
            prefix, name = module[0].split(':')
            if (prefix==modulePrefix or modulePrefix==None) and (name==moduleName or moduleName==None):
                if output=='simple':
                    positions.append(self.toV(module['at']))
                elif output=='dict':
                    positions.append({'pos':self.toV(module['at']), 'name':name, 'prefix':prefix})
        return positions 

    def toTuple(self, a):
        return (float(a[0]), float(a[1]))

    def getPart(self, name, layer):
        self.makeBorders('Edge.Cuts')
        part=Part(name=name, layer=layer, border=self.border)
        for path in self.paths:
            part.add(path)
        p=re.compile('(\d+)mm')
        for hole in self.getModules('MountingHole', None, 'dict'):
            m=p.search(hole['name'])
            if m and m.group(1):
                part.add(Hole(hole['pos'], rad=float(m.group(1))/2))
        return part


    def makeBorders(self, layer):
        segments=[]
        # collect all the sections
        for section in self.pcb.gr_line:
            if section['layer'] == layer:
                section['type']='line'
                newsect={'start':self.toTuple(section['start']), 'end':self.toTuple(section['end']), 'width':section['width'], 'type':'line'}
                segments.append(newsect)
        for section in self.pcb.gr_arc:
            if section['layer'] == layer:
                newsect={'start':self.toTuple(section['end']), 'centre':self.toTuple(section['start']), 'angle':section['angle'], 'width':section['width']}
                r = [newsect['start'][0]-newsect['centre'][0], newsect['start'][1]-newsect['centre'][1]]
                a = section['angle']*math.pi/180
                end = [newsect['centre'][0]+round(r[0]*math.cos(a) - r[1]*math.sin(a),4), newsect['centre'][1]+round(r[0]*math.sin(a)+r[1]*math.cos(a),4)]
                newsect['end']=self.toTuple(end)
                newsect['type']='arc'
                segments.append(newsect)
        count=0
        ends={}
        # create a hash of all the end positions
        for c in segments:
            start= c['start']
            end = c['end']
            c['id']=count
            if start in ends:
                ends[start].append([count,'start'])
            else:
                ends[start]=[[count,'start']]
            if end in ends:
                ends[end].append([count,'end'])
            else:
                ends[end]=[[count,'end']]
            count+=1
        loops=[]
        for s in range(0, len(segments)):
            if 'reversed' not in segments[s]:
                loops.append(self.getLoop(ends, segments, s,s, 'start', 'start'))
        paths=[]
        for loop in loops:
            paths.append(self.makePath(loop))

        for section in self.pcb.gr_circle:
            if section['layer'] == layer:
                section['type']='arc'
                paths.append(Circle(
                    self.toV(section['start']),
                    rad=(self.toV(section['start'])-self.toV(section['end'])).length()
                    )
                )
        if layer == 'Edge.Cuts':
            for i in range(0,len(paths)):
                fail=False
                for j in range(0, len(paths)):
                    if i!=j:
                        if paths[i].contains(paths[j])!=1:
                            fail=True
                            break
                        else:
                            paths[j].side='in'
                if not fail:
                    self.border=paths[i]
                    paths.remove(paths[i])
                    self.paths=paths
                    self.border.side='out'
        else:
            return paths

    def toV(self, t):
        return V(t[0], t[1])

    def makePath(self, loop):
        path = Path(closed=True)
        for l in loop:
            if l['reversed']:
                end='start'
                direction='cw'
            else:
                end='end'
                direction='ccw'

            if l['type']=='line':
                path.add_point(PSharp(self.toV(l[end])))
            if l['type']=='arc':
                rad=(self.toV(l['start'])-self.toV(l['centre'])).length()
                path.add_point(PArc(self.toV(l['centre']), radius=rad, direction=direction))
                path.add_point(PSharp(self.toV(l[end])))
        return path
    def getLoop(self, ends, segments, p, start, i, istart, depth=0):
        # we have gone all the way around the loop
        if(p==start and depth!=0):
            return []
        segment=segments[p]
        pos = segment[i]
        end = ends[pos]
        if end[0][0]==p:
            a=1
            na=0
        else:
            a=0
            na=1
        if end[a][1]=='start':
            newi='end'
        else:
            newi='start'

        loop=self.getLoop(ends,segments, end[a][0], start, newi, istart, depth+1 )
        if(end[na][1]=='start'):
            segment['reversed']=False
        else:
            segment['reversed']=True
        loop.insert(0,segment) 
        return loop



