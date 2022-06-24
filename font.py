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



from freetype import *
from path import *
from point import *
from HersheyFonts import HersheyFonts

class HersheyText(Pathgroup):
    def __init__(self, pos, text, **config):
        self.init(config)
        thefont = HersheyFonts()
        if 'font' in config:
            thefont.load_default_font(config['font'])
        else:
            thefont.load_default_font('rowmans')
        if 'scale' in config:
            self.scale =float(config['scale'])
        else:
            self.scale=1.0
        lastx=None
        lasty=None
        minx = 100000
        miny = 100000
        maxx = -100000
        maxy = -100000
        for (x1, y1), (x2, y2) in thefont.lines_for_text(text):
            if lastx!=x1 or lasty!=y1:
                thepath = self.add(Path(closed=False))
                thepath.add_point(pos+V(x1,-y1)*self.scale)
            thepath.add_point(pos+V(x2,-y2)*self.scale)
            lastx=x2
            lasty=y2
            maxx = max(maxx, x1, x2)
            maxy = max(maxy, y1, y2)
            minx = min(minx, x1, x2)
            miny = min(miny, y1, y2)
        if 'centred' in config and config['centred']:
            self.translate(-V((maxx+minx)/2, (maxy+miny)/2)*self.scale)

class Text(Pathgroup):
    def __init__(self, pos, text, **config):
        self.init(config)
        if 'font' in config:
            font=config['font']
        else:
            font='/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf'
            try:
                f=open("filename.txt")
            except FileNotFoundError:
                font='/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf'
        if 'scale' in config:
            self.scale =config['scale']
        else:
            self.scale=1.0
        if 'charwidth' in config:
            charwidth =config['charwidth']
        else:
            charwidth=10
        if 'charheight' in config:
            charheight =config['charheight']
        else:
            charheight=10
        if 'side' in config:
            if config['side'] =='in':
                side='in'
                notside='out'
            elif config['side'] =='out':
                side='out'
                notside='in'
            elif config['side'] == 'on':
                side='on'
                notside='on'
        else:
            side='on'
            notside='on'
        prev_glyph = None
        x=0
        face = Face(font)
        face.set_char_size(charwidth, charheight)
        self.chars=[]

        if 'centred' in config and config['centred']:
            offset = self.get_length(text, face)/2 *self.scale
            if 'YcentreMode' in config and config['YcentreMode']:
                offsety = float(self.getVoffset(face, config['YcentreMode'])) *self.scale
            else:
                offsety = float(self.getVoffset(face, 'aCentre')) *self.scale
        else:
            offset = 0
            offsety = 0
        self.translate(pos-V(offset,offsety))
        for ch in text :
            char = self.add(Pathgroup())
            char.translate(V(x,0))
            glyph_index = face.get_char_index(ord(ch))
            face.load_glyph(glyph_index, FT_LOAD_DEFAULT)
            if prev_glyph != None :
                kern = face.get_kerning(prev_glyph, glyph_index, FT_KERNING_DEFAULT).x
            else :
                kern = 0
            advance = face.glyph.advance

            slot = face.glyph
            outline = slot.outline
            lastc=-1
            for c in outline.contours:
                o = self.import_outline(outline,lastc+1, c, side)
                if o.orig_direction=='cw':
                    o.side = side
                else:
                    o.side = notside
                char.add(o)
                lastc=c

            x+= self.scale*float(face.glyph.linearHoriAdvance)/1000 + kern
            prev_glyph = glyph_index
            self.chars.append(char)
    def get_length(self, text, face):
        x=0
        prev_glyph = None
        for ch in text :
            glyph_index = face.get_char_index(ord(ch))
            face.load_glyph(glyph_index, FT_LOAD_DEFAULT)
            if prev_glyph != None :
                kern = face.get_kerning(prev_glyph, glyph_index, FT_KERNING_DEFAULT).x
            else :
                kern = 0
            prev_glyph = glyph_index
            x+= float(face.glyph.linearHoriAdvance)/1000 + kern

        return x
    def getVoffset(self, face, alignOn):
        if alignOn=='line':
            return 0
        elif alignOn=='ACentre':
            face.load_char('A')
            bbox = self.getBBox(face.glyph)
            return (float(bbox['maxy']) + float(bbox['miny']))/2
        elif alignOn=='aCentre':
            face.load_char('a')
            bbox = self.getBBox(face.glyph)
            return (float(bbox['maxy']) + float(bbox['miny']))/2

    def getBBox(self, slot):
        outline = slot.outline
        minx = 1000000
        maxx = -1000000
        miny = 1000000
        maxy = -1000000

        for p in outline.points:
            minx = min(minx, p[0])
            maxx = max(maxx, p[0])
            miny = min(miny, p[1])
            maxy = max(maxy, p[1])
        return {'minx':minx, 'maxx':maxx, 'miny':miny, 'maxy':maxy}

    def import_outline(self, outline, start, end, side, offset=False):
        out=Path(closed=True, side=side)
        l = end-start
        if type(offset) is False:
            offset=V(0,0)
        for p in range(start, end+1):
            if p==start:
                lp=end-1
            else:
                lp=p-1
            if p==end-1:
                np=start
            else:
                np=p+1
            point=outline.points[p]
            if (outline.tags[p] & 1) ==1:
                out.add_point(PSharp(offset + V(point[0], point[1])*self.scale, sharp=False))
            else:
                if point!=outline.points[lp]:
                    if( (outline.tags[lp]&1)!=1):
                        out.add_point( PSharp(offset+(V(point[0], point[1])+V(outline.points[lp][0], outline.points[lp][1]))/2*self.scale, sharp=False))
# lets just move to straight lines as beziers don't offset yet
        out2=Path(closed=True, side=side)
        for p in out.polygonise(0.2):
            out2.add_point(PSharp(p, sharp=False))
        out2.simplify_points()
# we will need to know what the original direction was to work out if this is internal or not
        out2.orig_direction = out.find_direction({})
        return out2

class CurvedText(Text):
    def __init__(self, pos, rad, text, **config):
        self.init(config)
        self.translate(pos)
        if 'font' in config:
            font=config['font']
        else:
            font='/home/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf'
            try:
                f=open(font)
            except FileNotFoundError:
                font='/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf'
        print (font)
        if 'scale' in config:
            self.scale =config['scale']
        else:
            self.scale=1.0
        if 'charwidth' in config:
            charwidth =config['charwidth']
        else:
            charwidth=10
        if 'charheight' in config:
            charheight =config['charheight']
        else:
            charheight=10
        if 'side' in config:
            if config['side'] =='in':
                side='in'
                notside='out'
            elif config['side'] =='out':
                side='out'
                notside='in'
            elif config['side'] == 'on':
                side='on'
                notside='on'
        else:
            side='on'
            notside='on'
        if 'dir' in config:
            if config['dir'] == 'cw':
                direction = 1
            elif config['dir'] == 'ccw':
                direction = -1
            else:
                print("CurvedText direction "+str(config['dir'])+" should be 'cw' or 'ccw'")
        else:
            direction = 1
        if 'startangle' in config:
            start_angle = config['startangle']
        else:
            start_angle = 0
# the line you are defining by rad - can be top, middle, bottom
        if 'line' in config:
            line = config['line']
        else:
            line = 'bottom'
        prev_glyph = None
        x=0
        face = Face(font)
        face.set_char_size(charwidth, charheight)

        self.chars=[]
        glyph_index = face.get_char_index(ord("H"))
        face.load_glyph(glyph_index, FT_LOAD_DEFAULT)
#               slot = face.glyph
        Hheight = 44.1/63*face.glyph.linearVertAdvance * self.scale/1000
        glyph_index = face.get_char_index(ord("a"))
        face.load_glyph(glyph_index, FT_LOAD_DEFAULT)
        aheight = 44.1/63*face.glyph.linearVertAdvance * self.scale/1000
        if line == 'bottom':
            spacing_angle = 360.0 / (math.pi * 2.0 * (abs(rad+Hheight/2) )) * direction
        elif line == 'middle':
            rad-=aheight
            spacing_angle = 360.0 / (math.pi * 2.0 * (abs(rad+Hheight/2) )) * direction
        elif line == 'top':
            rad-=Hheight
            spacing_angle = 360.0 / (math.pi * 2.0 * (abs(rad+Hheight/2) )) * direction
        if 'centred' in config and config['centred']:
            start_angle -= self.get_length(text, face)/2 * spacing_angle *self.scale

        lastmove=0
        for ch in text :
            char = self.add(Pathgroup())
            char.translate( V(0,0) )
            glyph_index = face.get_char_index(ord(ch))
            face.load_glyph(glyph_index, FT_LOAD_DEFAULT)
            if prev_glyph != None :
                kern = face.get_kerning(prev_glyph, glyph_index, FT_KERNING_DEFAULT).x
            else :
                kern = 0
            advance = face.glyph.advance

            slot = face.glyph
            outline = slot.outline
            lastc=-1
            for c in outline.contours:
                o = self.import_outline(outline,lastc+1, c, side, V(-float(face.glyph.linearHoriAdvance)/1000/2*self.scale, direction*rad))
                if o.orig_direction=='cw':
                    o.side = side
                else:
                    o.side = notside
                char.add(o)
#                               lastc=c
    #                            if lastc==-1:
   #                                     s=side
  #                              else:
 #                                       s=notside
#                                char.add(self.import_outline(outline,lastc+1, c, s, V(-float(face.glyph.linearHoriAdvance)/1000/2*self.scale, rad)))
                lastc=c

            move = float(face.glyph.linearHoriAdvance)/1000+kern
            x+= move/2 + lastmove/2
            if(direction>0):
                char.rotate( V(0,0), x * spacing_angle * self.scale + start_angle)
            else:
                char.rotate( V(0,0), x * spacing_angle * self.scale + start_angle+180)
            lastmove = move
            prev_glyph = glyph_index
            self.chars.append(char)
