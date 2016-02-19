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
			font='/home/usr/share/fonts/truetype/ubuntu-font-family/UbuntuMono-B.ttf'
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
			print ch+" "+str(advance.x)+" "+str(kern)

			slot = face.glyph
			outline = slot.outline
#			print  outline.points
			#char.outline = char.add(self.import_outline(outline, side))
			lastc=-1
			for c in outline.contours:
#				print str(c)+"-"+str(len(outline.points))
				if lastc==-1:
					s=side
				else:
					s=notside
				char.add(self.import_outline(outline,lastc+1, c, s))
				lastc=c
			#	char.add(self.import_outline(c, notside))
			x+=advance.x/2+kern
			prev_glyph = glyph_index
			self.chars.append(char)
	def import_outline(self, outline, start, end, side):
		out=Path(closed=True, side=side)
		print "start"+str(start)+" ebd="+str(end)+" len"+str(len(outline.points))
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
			print "p="+str(p)+" pnt="+str(point)
			if (outline.tags[p] & 1) ==1:
#				print "sharp "+str(point)
				out.add_point(PSharp(V(point[0], point[1])))
			else:
				if point!=outline.points[lp]:
					if( (outline.tags[lp]&1)!=1):
#						print "esharp "+str((V(point[0], point[1])+V(outline.points[lp][0], outline.points[lp][1]))/2)
						out.add_point(PSharp((V(point[0], point[1])+V(outline.points[lp][0], outline.points[lp][1]))/2))
#					print "bc "+str(point)
					out.add_point(PBezierControl(V(point[0], point[1])))
#					out.add_point(PSharp(V(point[0], point[1])))
		out2=Path(closed=True, side=side)
		for p in out.polygonise(0.2):
			out2.add_point(p)
		return out2
			


"""
if __name__ == '__main__':
    import numpy
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as patches

    face = Face('./Vera.ttf')
    face.set_char_size( 48*64 )
    face.load_char('S')
    slot = face.glyph

    outline = slot.outline
    points = numpy.array(outline.points, dtype=[('x',float), ('y',float)])
    x, y = points['x'], points['y']

    figure = plt.figure(figsize=(8,10))
    axis = figure.add_subplot(111)
    #axis.scatter(points['x'], points['y'], alpha=.25)
    start, end = 0, 0

    VERTS, CODES = [], []
    # Iterate over each contour
    for i in range(len(outline.contours)):
        end    = outline.contours[i]
        points = outline.points[start:end+1]
        points.append(points[0])
        tags   = outline.tags[start:end+1]
        tags.append(tags[0])

        segments = [ [points[0],], ]
        for j in range(1, len(points) ):
            segments[-1].append(points[j])
            if tags[j] & (1 << 0) and j < (len(points)-1):
                segments.append( [points[j],] )
        verts = [points[0], ]
        codes = [Path.MOVETO,]
        for segment in segments:
            if len(segment) == 2:
                verts.extend(segment[1:])
                codes.extend([Path.LINETO])
            elif len(segment) == 3:
                verts.extend(segment[1:])
                codes.extend([Path.CURVE3, Path.CURVE3])
            else:
                verts.append(segment[1])
                codes.append(Path.CURVE3)
                for i in range(1,len(segment)-2):
                    A,B = segment[i], segment[i+1]
                    C = ((A[0]+B[0])/2.0, (A[1]+B[1])/2.0)
                    verts.extend([ C, B ])
                    codes.extend([ Path.CURVE3, Path.CURVE3])
                verts.append(segment[-1])
                codes.append(Path.CURVE3)
        VERTS.extend(verts)
        CODES.extend(codes)
        start = end+1


    # Draw glyph lines
    path = Path(VERTS, CODES)
    glyph = patches.PathPatch(path, facecolor='.75', lw=1)

    # Draw "control" lines
    for i, code in enumerate(CODES):
        if code == Path.CURVE3:
            CODES[i] = Path.LINETO
    path = Path(VERTS, CODES)
    patch = patches.PathPatch(path, ec='.5', fill=False, ls='dashed', lw=1 )

    axis.add_patch(patch)
    axis.add_patch(glyph)

    axis.set_xlim(x.min()-100, x.max()+100)
    plt.xticks([])
    axis.set_ylim(y.min()-100, y.max()+100)
    plt.yticks([])
    plt.show()
"""
