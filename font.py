from freetype import *
from path import *
from point import *

class Text(Pathgroup):
	def __init__(self, pos, text, **config): 
		self.init(config)
		self.translate(pos)
		if 'font' in config:
			font=config['font']
		else:
			font='/home/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf'
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
				if lastc==-1:
					s=side
				else:
					s=notside
				char.add(self.import_outline(outline,lastc+1, c, s))
				lastc=c

			x+= float(face.glyph.linearHoriAdvance)/1000 + kern
			prev_glyph = glyph_index
			self.chars.append(char)

	def import_outline(self, outline, start, end, side):
		out=Path(closed=True, side=side)
		l = end-start
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
				out.add_point(PSharp(V(point[0], point[1])*self.scale))
			else:
				if point!=outline.points[lp]:
					if( (outline.tags[lp]&1)!=1):
						out.add_point(PSharp((V(point[0], point[1])+V(outline.points[lp][0], outline.points[lp][1]))/2*self.scale))
# lets just move to straight lines as beziers don't offset yet
		out2=Path(closed=True, side=side)
		for p in out.polygonise(0.2):
			out2.add_point(p)
		return out2

class CurvedText(Text):
        def __init__(self, pos, rad, text, **config):
                self.init(config)
                self.translate(pos)
                if 'font' in config:
                        font=config['font']
                else:
                        font='/home/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf'
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
				print "CurvedText direction "+str(config['dir'])+" should be 'cw' or 'ccw'"
		else:
			direction = 1
		if 'startangle' in config:
			startangle = config['startangle']
		else:
			startangle = 0

		spacing_angle = 360.0 / math.pi * 2.0 * rad 
                prev_glyph = None
                x=0
                face = Face(font)
                face.set_char_size(charwidth, charheight)
                self.chars=[]
                for ch in text :
                        char = self.add(Pathgroup())
                        char.translate( V(0,rad) )
			char.rotate( V(0,0), x * spacing_angle + start_angle)
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
                                if lastc==-1:
                                        s=side
                                else:
                                        s=notside
                                char.add(self.import_outline(outline,lastc+1, c, s))
                                lastc=c

                        x+= float(face.glyph.linearHoriAdvance)/1000 + kern
                        prev_glyph = glyph_index
                        self.chars.append(char)
        
			

