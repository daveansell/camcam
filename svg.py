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



from lxml import etree
from path import *
import re

class SVGimport(Pathgroup):
    def __init__(self,pos, filename, paths, **config):
        nsmap = {
            'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
            'cc': 'http://web.resource.org/cc/',
            'svg': 'http://www.w3.org/2000/svg',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'xlink': 'http://www.w3.org/1999/xlink',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
        }

        self.init(config)
        #self.translate(pos)
        config['pos']=pos

        if 'match_type' in config:
            match_type = config['match_type']
        else:
            match_type = 'exact'
        with open( filename, 'r') as infile:
            tree = etree.parse(infile)
            root = tree.getroot()
        outpaths=[]
        if paths=='all':
            outpaths= tree.xpath('.//svg:path',namespaces=nsmap)
        elif type(paths) is list:
            for path in paths:
                if match_type == 'exact':
                    outpaths += tree.xpath('.//svg:path[@id="'+path+'"]', namespaces=nsmap)
                else:
                    outpaths += tree.xpath('.//svg:path[starts-with(@id, "'+path+'")]', namespaces=nsmap)
#                                outpaths= tree.xpath('.//svg:path[@id="'+path+'"]', namespaces=nsmap)
        elif type(paths) is dict:
            for p in list(paths.keys()):
                outpaths= tree.xpath(".//n:path[@"+path[p]['attrib']+"='"+path[p]['value']+"']", namespaces={'n': "http://www.w3.org/2000/svg"})
        for p in outpaths:
            transform = p.get('transform')
            self.parse_d(p.get('d'),transform, config)

    def svgtransform(self, pos, transform):
        if transform is None:
            return pos
        commands=transform.split(';')
        for command in commands:
            print(command)
            m= re.search('(.*?)\((.*?),(.*?)\)', command)
#                       m = re.search('(.*?)\(([-,\d]+),\s*([-,\d]+)\)', command)
            if m.groups(1)[0] == 'scale':
                pos=V(pos[0]*float(m.groups(1)[1]), pos[1]*float(m.groups(1)[2]))
            if m.groups(1)[0] == 'transform':
                pos+=V(m.groups(1)[1],m.groups(1)[2])
            if m.groups(1)[0] == 'matrix':
                ma = m.groups(1)[2].split(',')
                ma.insert(0, m.groups(1)[1])
                ma = [float(i) for i in ma]
                pos = V(
                        ma[0]*pos[0] + ma[2]*pos[1] + ma[4],
                        ma[1]*pos[0] + ma[3]*pos[1] + ma[3],
                )
        return pos
# at the moment this just treats everything as a line so add lots of points
    def parse_d(self,d,transform, config):
        outpaths=[]
        outpath=False
        items = re.split('[, ]+', d)
        pos = config['pos']#V(0,0)
        firstpath=True
        i=0
        while i<len(items):
            if items[i]=='M':
                i+=1
                if outpath!=False and len(outpath.points)>1:
                    if (startpos-pos).length()<0.04:
                        outpath.closed=True
                        outpath.points.pop()
                    outpaths.append(outpath)

                outpath = Path()#transform={'translate':config['pos']})
                pos=V(float(items[i]), -float(items[i+1]))
                startpos = pos
                outpath.add_point(self.svgtransform(pos, transform))
                i+=2
                while i<len(items) and self.is_number(items[i]):
                    pos=config['pos']+V(float(items[i]), -float(items[i+1]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=2
            elif items[i]=='L':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos=config['pos'] + V(float(items[i]), -float(items[i+1]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=2
            elif items[i]=='A':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos=config['pos'] + V(float(items[i+5]), -float(items[i+6]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=7
            elif items[i]=='C':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos = config['pos'] + V(float(items[i+4]), -float(items[i+5]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=6
            elif items[i]=='S':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos = config['pos'] + V(float(items[i+2]), -float(items[i+3]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=4
            elif items[i]=='Q':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos = config['pos'] + V(float(items[i+2]), -float(items[i+3]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=4
            elif items[i]=='T':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos = config['pos'] + V(float(items[i]), -float(items[i+1]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=2
            elif items[i]=='H':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos = config['pos'] + V(float(items[i]), pos[1])
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=1
            elif items[i]=='V':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos = config['pos'] + V(pos[0],float(items[i]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=1
            elif items[i]=='m':
                if outpath!=False and len(outpath.points)>1:
                    if (startpos-pos).length()<0.04:
                        outpath.closed=True
                        outpath.points.pop()
                    outpaths.append(outpath)
                outpath = Path()#transform={'translate':config['pos']})
                i+=1
                pos+=V(float(items[i]), -float(items[i+1]))
                startpos = pos
                outpath.add_point(self.svgtransform(pos, transform))
                i+=2
                while i<len(items) and self.is_number(items[i]):
                    pos+=V(float(items[i]), -float(items[i+1]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=2
            elif items[i]=='l':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos+=V(float(items[i]), -float(items[i+1]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=2
            elif items[i]=='a':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos+=V(float(items[i+5]), -float(items[i+6]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=7
            elif items[i]=='c':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos+=V(float(items[i+4]), -float(items[i+5]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=6
            elif items[i]=='s':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos=V(float(items[i+2]), -float(items[i+3]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=4
            elif items[i]=='q':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos=V(float(items[i+2]), -float(items[i+3]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=4
            elif items[i]=='t':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos=V(float(items[i]), -float(items[i+1]))
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=2
            elif items[i]=='h':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    pos+=V(float(items[i]), 0)
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=1
            elif items[i]=='v':
                i+=1
                while i<len(items) and self.is_number(items[i]):
                    try:
                        pos+=V(0, -float(items[i]))
                    except ValueError:
                        print (d)
                    
                        raise( ValueError);
                    outpath.add_point(self.svgtransform(pos, transform))
                    i+=1
            elif items[i]=='z' or items[i]=='Z':
                i+=1
                outpath.closed=True
                pos=outpath.points[0].pos
            else:
                i+=1
        if outpath!=False and len(outpath.points)>0:
            if (startpos-pos).length()<0.04:
                outpath.closed=True
               # outpath.points.pop()
            outpaths.append(outpath)
        for i in range(0, len(outpaths)):
            if len(outpaths[i].points):
                self.add(outpaths[i])
        if len(outpaths)>1 and 'side' in list(config.keys()) and config['side']!='on':
            outermost=0
            for i in range(1, len(outpaths)):
                if outpaths[outermost].contains(outpaths[i]):
                    outermost=i
            outerdir=outpaths[outermost].find_direction(config)
            for i in range(0, len(outpaths)):
                if i==outermost or outpaths[i].find_direction(config)==outerdir:
                    outpaths[i].side=config['side']
                else:
                    if config['side']=='in':
                        outpaths[i].side='out'
                    elif config['side']=='out':
                        outpaths[i].side='in'
                    elif config['side']=='left':
                        outpaths[i].side='right'
                    elif config['side']=='right':
                        outpaths[i].side='left'
    def is_number(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False

#s=SVGimport(1, '/home/dave/cnc/modules/davecad1/beam_bridge/beam-bridge-river.svg','all')
