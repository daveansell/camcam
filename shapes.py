

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
from minivec import *
from segments import *
from dxfwrite import DXFEngine as dxf

# create a rectangular path
class Rect(Path):
    def __init__(self, bl,  **config):
        self.init( config)
        self.cut_square(bl, config)
        """Cut a rectanngle
        """+self.otherargs

    def cut_square(self, bl, config):
        self.otherargs+="""
        :param bl: bottom left or centre if centred
        :param tr: top right if not centred
        :param centred: true if you want the rectangle to be centred
        :param cornertype: type of corner points sharp, incurve, outcurve
        :param rad: radius of cornwer curves if you have them"""
        if 'width' in config and 'height' in config and 'centred' not in config:
            config['centred']=True
        if 'centred' in config and config['centred']:
            if 'width' in config and 'height' in config:
                pos=bl
                bl=pos-V(config['width']/2, config['height']/2)
                tr=pos+V(config['width']/2, config['height']/2)
            else:
                print("Rounded square is centred but no width or height")
        else:
            if 'tr' in config:
                tr=config['tr']
            else:
                print("Rounded square is not centred but no tr value")
        if 'cornertype' in config:
            ct=config['cornertype']
        else:
            ct='sharp'
        args={}
        if ct=='aroundcurve':
            if 'direction' in config:
                args['direction']=config['direction']
            else:
                args['direction'] = 'ccw'
        if ct=='chamfer':
            if 'chamfer' in config:
                args['chamfer'] = config['chamfer']
            else:
                args['chamfer'] = config['rad']
        self.closed=True
        if 'rad' not in config or config['rad'] is False:
            rad = 0.01
        else:
            rad = config['rad']
        self.closed=True
        if rad is False:
            rad = self.cutterrad
        if bl[0]-tr[0] ==0 or bl[1]-tr[1] ==0:
            raise ValueError("Rectangle has no area")
        self.comment("Rounded Square")
# attempt to start cut on longest side to reduce loosing small parts
        if(abs(bl[0]-tr[0]) < abs(bl[1]-tr[1])):
            points=[bl, V(tr[0],bl[1],0), tr, V(bl[0],tr[1],0)]
        else:
            points=[bl, V(bl[0],tr[1],0), tr, V(tr[0],bl[1],0)]
        if type(ct) is str:
            for p in points:
                self.add_point(p,ct, radius=rad, **args)
        elif type(ct) is list:
            args['radius']=rad
            if type(args['radius']) is list:
                for i in range(0,4):
                    args['radius']=rad[i]
                    self.add_point(ct[i](points[i], **args))
            else:
                args['radius']=rad
                for i in range(0,4):

                    self.add_point(ct[i](points[i], **args))
        else:
            for p in points:
                self.add_point(ct(p, **args))

class DottedCircle(Pathgroup):
    def __init__(self, pos, rad, dotLength, prop=0.5,**config):
        self.init(config)
        numDots = round(2*math.pi/dotLength*rad)
        angle = math.pi*2/numDots/math.pi*180
        for i in range(0, numDots):
            p=Path(closed=False, side='on')
            p.add_point(PSharp(pos+rotate(V(0,rad), angle*i)))
            p.add_point(PArc(pos, radius=rad, direction='cw'))
            p.add_point(PSharp(pos+rotate(V(0,rad), angle*(i+prop))))
            self.add(p)


class RoundedRect(Rect):
    def __init__(self, bl,  **config):
        self.init(config)
        config['cornertype']='incurve'
        self.cut_square(bl,config)
        """Cut a rectangle with incurve corners
        """+self.otherargs

class CurvedRect(Path):
    def __init__(self, pos, **config):
        self.init(config)
        self.closed=True
        if 'centred' in config and config['centred']:
            if 'width' in config:
                width = config['width']
            else:
                raise ValueError('centred CurveRec with no width')
            if 'height' in config:
                height = config['height']
            else:
                raise ValueError('centred CurveRec with no height')
        else:
            if 'tr' in config:
                tr=config['tr']
            else:
                raise ValueError('non-centred CurveRec with no tr')
        if 'siderad' in config:

            siderad = config['siderad']
        elif 'from_centre' in config:
            pass
        else:
            raise ValueError('so siderad in curvedRect')
        self.add_point(pos+V(-width/2, -height/2))
        self.add_point(PArc(None, radius=siderad, direction='cw', length='short'))
        self.add_point(pos+V(-width/2, height/2))
        self.add_point(PArc(None, radius=siderad, direction='cw', length='short'))
        self.add_point(pos+V(width/2, height/2))
        self.add_point(PArc(None, radius=siderad, direction='cw', length='short'))
        self.add_point(pos+V(width/2, -height/2))
        self.add_point(PArc(None, radius=siderad, direction='cw', length='short'))

class RectFromTo(Path):
    def __init__(self, cutFrom, to, width, **config):
        self.init(config)
        self.closed=True
        along=(to-cutFrom).normalize()
        perp = rotate(along, 90)
        if 'fromends' in config and config['fromends'] is not None:
            cutFrom -= along*config['fromends']
            to += along*config['fromends']
        self.add_point(cutFrom + perp * width/2)
        self.add_point(cutFrom - perp * width/2)
        self.add_point(to - perp * width/2)
        self.add_point(to + perp * width/2)


# Two circles joined with straight lines
class Egg(Path):
    def __init__(self, pos1, rad1, pos2, rad2, **config):
        """Two circles joined with straight line with rad1, and rad2, centred at pos1, pos2"""
        self.init(config)
        self.closed=True
        self.add_point(POutcurve(pos1, radius=rad1))
        self.add_point(POutcurve(pos2, radius=rad2))

class Ellipse(Path):
    def __init__(self, pos, **config):
        self.init(config)
        self.closed=True
        self.translate(pos)
        if 'width' in config:
            width = config['width']
        else:
            print('width not defined in Ellipse')
        if 'height' in config:
            height = config['height']
        else:
            print('Height not defined in Ellipse')
        if 'resolution' in config:
            points = config['resolution']
        else:
            points = 32
        if 'extra_height' in config:
            extra_height=config['extra_height']
        else:
            extra_height=0
        a = 2.0 * math.pi / points
        for i in range(0, points):
            if(math.sin( a * float(i)) * extra_height>0 ):
                self.add_point(V( width/2 * math.cos( a * float(i)), height/2 * math.sin( a * float(i)) +extra_height))
            else:
                self.add_point(V( width/2 * math.cos( a * float(i)), height/2 * math.sin( a * float(i)) ))

class SemiCircle(Path):
    def __init__(self, pos, rad, **config):
        self.init(config)
        self.closed=True
        self.translate(pos)
        self.add_point(V(-rad,0))
        self.add_point(PIncurve(V(-rad,rad), radius=rad))
        self.add_point(PIncurve(V(rad,rad), radius=rad))
        self.add_point(V(rad,0))

class SubCircle(Path):
    def __init__(self, centre, rad, yoff, **config):
        self.init(config)
        self.closed=True
        xoff = math.sqrt(rad*rad - yoff*yoff)
        self.add_point(PSharp(centre + V( xoff, yoff)))
        self.add_point(PArc(centre, radius=rad, direction='ccw'))
        self.add_point(PSharp(centre + V( 0, rad)))
        self.add_point(PArc(centre, radius=rad, direction='ccw'))
        self.add_point(PSharp(centre + V(-xoff, yoff)))
        if 'extraSquare' in config and config['extraSquare']>0:
            self.add_point(PSharp(centre + V(-xoff, yoff-config['extraSquare'])))
            self.add_point(PSharp(centre + V( xoff, yoff-config['extraSquare'])))


class RepeatEllipse(Part):
    def __init__(self, pos, ob, **config):
        self.init(config)
        self.closed=True
        if 'width' in config:
            width = config['width']
        else:
            print('width not defined in Ellipse')
        if 'height' in config:
            height = config['height']
        else:
            print('Height not defined in Ellipse')
        if 'number' in config:
            points = config['number']
        else:
            points = 32
        a = 2.0 * math.pi / points
        for i in range(0, points):
            t=copy.deepcopy(ob)
            t.transform['translate'] = V( width/2 * math.cos( a * float(i)), height/2 * math.sin( a * float(i)) )
            self.add(t)

class Spiral(Path):
    def __init__(self, pos, r1, r2, **config):
        self.init(config)
        self.length=0
        self.r1=r1
        self.r2=r2
        self.pos = pos
        if 'closed' in config:
            self.closed=config['closed']
        else:
            self.closed=True
        if "turns" in config:
            self.turns=config["turns"]
        elif 'spacing' in config:
            self.turns = (r2-r1)/config['spacing']
            turns= self.turns
        else:
            self.turns = 1.0
        if "steps" in config:
            steps = config["steps"]
        else:
            steps = int(50 * turns)
        if 'startTurns' in config:
            startTurns = config['startTurns']
        else:
            startTurns = 0
        if 'endTurns' in config:
            endTurns = config['endTurns']
        else:
            endTurns = self.turns
        if 'rad' in config:
            rad = config['rad']
        else:
            rad = False
        self.startTurns = startTurns
        self.endTurns = endTurns
        astep = 360.0
        rstep = float(r2-r1)/self.turns
        tstep = float(self.turns)/steps
        self.length=0
        if 'fromStart' in config:
            startTurns+=float(config['fromStart'])/(r1+startTurns*rstep)/2/math.pi

        if 'fromEnd' in config:
            endTurns-=float(config['fromEnd'])/(r1+endTurns*rstep)/2/math.pi
        t = startTurns + (2*rad)/(r1+startTurns*rstep)/2/math.pi
        if rad:
#                       self.add_point(PIncurve(pos+rotate(V(r1+rstep*endTurns, 0), astep*t), radius=rad))
            self.add_point(PIncurve(self.alongSpiral(startTurns), radius=rad))
        else:
#                       self.add_point(PSharp(pos+rotate(V(r1+rstep*endTurns, 0), astep*t)))
            self.add_point(PSharp(self.alongSpiral(startTurns)))
        while t<endTurns-(rad*2)/(r1+endTurns*rstep)/2/math.pi:
#                       self.add_point(PSharp(pos+rotate(V(r1+rstep*t, 0), astep*t)))
            self.add_point(PSharp(self.alongSpiral(t)))
            if t>startTurns+rad and t<endTurns-rad:
                self.length += (self.alongSpiral( t)-self.alongSpiral(t-tstep)).length()
#                            self.length += (V(r1+rstep*t,0) - rotate(V(r1+rstep*(t-tstep),0), astep*tstep)).length()
        #self.add_point(PSharp(pos+rotate(V(r1+rstep*endTurns,0), endTurns*astep)))
            t+=tstep
        if rad:
#                       self.add_point(PIncurve(pos+rotate(V(r1+rstep*endTurns, 0), astep*t), radius=rad))
            self.add_point(PIncurve(self.alongSpiral(endTurns), radius=rad))
        else:
#                       self.add_point(PSharp(pos+rotate(V(r1+rstep*endTurns, 0), astep*t)))
            self.add_point(PSharp(self.alongSpiral(endTurns)))
#                for i in range(int(start/, int(steps)+1):
 #                       self.add_point(PSharp(pos+V(r1+rstep*i,0), transform={'rotate':[pos, astep*i]}))
   # astep = 360.0*self.turns/steps
   # rstep = float(r2-r1)/steps
   # for i in range(0, int(steps)+1):
   #         self.add_point(PSharp(pos+V(r1+rstep*i,0), transform={'rotate':[pos, astep*i]}))
    def alongSpiral(self, turns):
        return self.pos + rotate(V(self.r1+float(self.r2-self.r1)*turns/self.turns,0), 360*turns)

class SpiralLoop(Path):
    def __init__(self, pos, r1, r2, width, **config):
        self.init(config)
        self.closed=True

        spiral1 = Spiral( pos, r1-width/2, r2-width/2, **config)
        spiral2 = Spiral( pos, r1+width/2, r2+width/2, **config)
        self.add_points(spiral1.points)
        for point in spiral2.points[::-1]:
            self.add_point(point)
#               self.add_points(spiral2.points, end='prepend')

class LineLoop(Path):
    def __init__(self, points, width, **config):
#               assert type(points) is list
        self.init(config)
        if 'cornertype' in config:
            cornertype=config['cornertype']
        else:
            cornertype=PSharp
        self.closed = True

        if 'rad' in config:
            rad = config['rad']
        else:
            rad = 0
        out = Path()
        back = Path()
        for p in range(0,len(points)):
            out.add_point(cornertype(points[p]))
            back.add_point(cornertype(points[len(points)-1-p]))
        out=out.offset_path('left', width/2, {})
        back=back.offset_path('left', width/2, {})
        for p in out.points:
            self.add_point(p)
        for p in back.points:
            self.add_point(p)

class Lines(Path):
    def __init__(self, points, **config):
#               assert type(points) is list
        self.init(config)
        if 'cornertype' in config:
            cornertype=config['cornertype']
        else:
            cornertype='sharp'
        if 'closed' in config:
            self.closed = config['closed']
        else:
            self.closed = False

        if 'rad' in config:
            rad = config['rad']
        else:
            rad = 0
        for p in points:
            if(type(p) != 'Vec' and hasattr(p, 'obType')):
                self.add_point(p)
            elif(type(cornertype) is str):
                self.add_point(p, cornertype, radius=rad)
            else:
                self.add_point(cornertype(p))

class ClearRect(Rect):
    def __init__(self, bl,  **config):
        self.init(config)
        if 'side' in config and config['side'] in ['in', 'out']:
            if config['side']=='out':
                config['cornertype']='sharp'
            else:
                config['cornertype']=PInsharp#'clear'
        self.cut_square(bl,config)
        """Cut a rectangle with sharp or clear corners depending on the side you are cutting
        """+self.otherargs
    def pre_render(config):
        if 'side' in config and config['side']=='in':
            config['cornertype']=PInsharp
        self.points=[]

class Polygon(Path):
    def __init__(self, pos, rad, sides, cornertype='sharp', cornerrad=False, **config):
        self.init( config)
        """Cut a regular polygon with radius to the points :param rad: centred at :param pos:, with :param sides: sides with corners of type :param cornertype:\n"""+self.otherargs
        self.closed=True
        step=360.0/float(sides)
        if 'cornerdir' in config:
            cornerdir=config['cornerdir']
        else:
            cornerdir=False
        if 'radMode' in config and config['radMode']=='flat':
            rad/=math.cos(math.pi/sides)
        elif 'radMode' in config and config['radMode']=='side':
            a = math.pi * 2 / sides
            rad = rad/ 2 / math.sin(a/2)
        if 'startAngle' in config:
            startAngle= config['startAngle']
        else:
            startAngle=0
        for i in range(0,int(sides)):
            self.add_point(
                    pos+rotate(V(rad,0), 
                    i*step+startAngle),
                    cornertype,
                    cornerrad,
                    direction=cornerdir)
        self.comment("Polygon")
        self.comment("pos="+str(pos)+" rad="+str(rad)+" sides="+str(sides)+" cornertype="+cornertype)

class ScallopedCircle(Path):
    def __init__(self, pos, rad, num, scallopRad, width, **config):
        self.init(config)
        if width/2 >= scallopRad:
            print("scallopRad must be less than half of width (ScallopedCircle)")
        scallopDist = math.sqrt(rad*rad-width*width/4)+ math.sqrt( scallopRad*scallopRad-width*width/4)
        scallopAngle = math.asin(width/2 / rad) / math.pi * 180
        angleStep = 360.0/num
        self.closed=True
        for i in range(0,num):
            a0 = angleStep * i
            self.add_point( PSharp(rotate(V(rad,0), a0-scallopAngle)))
            self.add_point( 
				PArc(
					rotate(V(scallopDist, 0), a0), 
					radius = scallopRad, 
					direction='ccw'
				)
			)
            self.add_point( PSharp(rotate(V(rad,0), a0+scallopAngle)))
            self.add_point( PArc(V(0,0), radius = rad, direction='cw'))
		

class Star(Path):
    def __init__(self, pos, outerRad, innerRad, sides, **config):
        self.init( config)
        """Cut a regular polygon with radius to the points :param rad: centred at :param pos:, with :param sides: sides with corners of type :param cornertype:\n"""+self.otherargs
        self.closed=True
        step=360.0/float(sides)
        if 'cornerPoint' in config:
            cornerPoint=config['cornerPoint']
        else:
            cornerPoint=PSharp(V(0,0))
        print("ISES="+str(sides))
        for i in range(0,int(sides)):
            t = copy.deepcopy(cornerPoint)
            t.pos = pos+rotate(V(innerRad,0), i*step)
            self.add_point(t)
            t = copy.deepcopy(cornerPoint)
            t.pos = pos+rotate(V(outerRad,0), (0.5+i)*step)
            self.add_point(t)

class CountersinkHole(Pathgroup):
    def __init__(pos, holerad, countersinkrad,  **config):
        if 'cutter' in config:
            cutter=config['cutter']
        else:
            cutter='countersink'
            config['cutter']='countersink'
        self.init(config)
        """Countersink an existing hole of radius :param holeRad: at :param pos: to a radius of :param countersinkrad:
if :param cutter: is not explicitly specified it will use the countersink cutter\n"""+self.otherargs
        if cutter in milling.tools:
            cutterconfig=milling.tools[self.cutter]
            if 'min_diameter' in cutterconfig:
                if holerad<=cutterconfig['min_diameter']/2:
                    self.add(Drill(pos,  z1=countersinkrad))
                # if the requesed countersink is too big, we will have to chop it into chunks
                elif countersinkrad-holerad>(cutterconfig['diameter']/2-cutter_config['min_rad'])*0.7:
                    steps = math.ceil(float(countersinkrad-holerad)/((cutterconfig['diameter']/2-cutter_config['min_rad'])*0.7))
                    step  = (countersinkrad-holerad)/steps
                    for i in reversed(list(range(0,steps))):
                        self.add(Circle(pos, rad=countersinkrad-(cutterconfig['diameter']/2-cutter_config['min_rad'])*0.7-step*i, z1=-(cutterconfig['diameter']/2-cutter_config['min_rad'])*0.7-step*i,cutter=cutter))
                else:
                    self.add(Circle(pos, rad=holerad-cutter_config['min_rad'], z1=countersinkrad-holerad+cutter_config['min_rad'])),

        self.comment("CountersinkHole")
        self.comment("pos="+str(pos)+" holerad="+str(holerad)+" countersinkrad="+str(countersinkrad))



# create a circular path
class Circle(Path):
    def __init__(self, pos, rad, **config):
        self.init( config)
        self.rad = rad
        self.pos = pos
        """Cut a circle centre at :param pos: with radius :param rad:"""+self.otherargs
        if rad==0:
            raise ValueError("circle of zero radius")
        else:
            if rad<3.17/2:
                self.cutter='2mm_endmill'
            self.closed=True
            self.add_point(pos,'circle',rad)
            self.comment("Circle")
            self.comment("pos="+str(pos)+" rad="+str(rad))
    def render_path_dxf(self,output, config):
        p=self.points[0].point_transform(config['transformations'])
        return [dxf.circle(radius = self.rad, center=p.pos)]

class Raster(Path):
    def __init__(self, pos, filename, width, height, **config):
        self.init(config)
        self.pos=pos
        self.width=width
        self.height=height
        self.filename=filename
        self.closed=False
        self.add_point(pos)
        self.add_point(pos+V(0,1))

    def transform2svg(self, transforms):
        ret=''
        if not transforms or not type(transforms) == list:
            return ""
        for t in transforms:
            if t:
                if 'translate' in t:
                    ret+="translate("+str(t['rotate'][0][0])+" "+str(t['rotate'][0][1])+") "
                if 'rotate' in t:
                    ret+="rotate("+str(t['rotate'][1])+" "+str(t['rotate'][0][0])+" "+str(t['rotate'][0][1])+") "
                if 'mirror' in t:
                    if t['mirror']=='x':
                        ret+='scale ( -1 1) '
                    elif t['mirror']=='y':
                        ret+='scale ( 1 -1) '
        return ret

    def render(self, pconfig):
        config=self.generate_config(pconfig)
        print(config['transformations'])
        if config['mode']=='svg':
            preTrans = "translate("+str(-self.width/2+self.pos[0])+" "+str(-self.height/2+self.pos[1])+") "
            return [config['cutter'],"<image width=\""+str(self.width)+"\" height=\""+str(self.height)+"\" xlink:href=\""+str(self.filename)+"\" transform=\""+self.transform2svg(config['transformations'])+preTrans+"\" />"]
        else:
            return [config['cutter'],""]

class Drill(Circle):
    def __init__(self, pos, **config):
        self.init(config)
        self.pos=pos
        if 'chipbreak' in config and config['chipbreak']:
            self.chipbreak = config['chipbreak']
        else:
            self.chipbreak = False
        if 'peck' in config and config['peck']:
            self.peck = config['peck']
        else:
            self.peck = False
        if 'rad' in config and config['rad']:
            if self.cutter is False or self.cutter is None:
                self.drillrad=config['rad']
                for m in milling.tools:
                    if milling.tools[m]['diameter']/2==self.drillrad:
                        self.cutter=m
            else:
                self.drillrad=milling.tools[self.cutter]['diameter']/2

            if self.cutter is False or self.cutter is None:
                pass
                #print("drill of "+str(self.drillrad)+"mm not found in tools")
        self.closed=True
        self.add_point(pos,'circle',self.drillrad)
        if 'vertfeed' in config:
            self.vertfeed = config['vertfeed']
        else:
            self.vertfeed = None
#               self.add_point(PSharp(self.pos))

    def render(self, pconfig):
        config=self.generate_config(pconfig)
        p=PSharp(self.pos).point_transform(config['transformations'])
        if not self.vertfeed:
            self.vertfeed=config['vertfeed']
    #       print "Drill render"+str(config['mode'])
        if config['mode']=='svg':
    #               print '<circle cx="%0.2f" cy="%0.2f" r="%0.2f"/>\n'%(p.pos[0], p.pos[1], self.drillrad)
            return [config['cutter'], '<circle cx="%0.2f" cy="%0.2f" r="%0.2f"/>\n'%(p.pos[0], p.pos[1], self.drillrad)]
        elif config['mode']=='gcode':
            if hasattr(self, 'clear_height') and self.clear_height is not None:
                clearanceHeight = self.clear_height
            else:
                clearanceHeight = config['clear_height']
            if self.peck:
                return [config['cutter'], 'G0X%0.2fY%0.2f\nG0Z1\n'%(p.pos[0], p.pos[1])+'G83X%0.2fY%0.2fZ%0.2fR%0.2fQ%0.2fF%0.2f\nG0Z%0.2f\n'%(p.pos[0], p.pos[1], config['z1'], config['z0']+3, self.peck, self.vertfeed,clearanceHeight)]
            elif self.chipbreak:
                return [config['cutter'], 'G73X%0.2fY%0.2fZ%0.2fR%0.2fQ%0.2fF%0.2f\nG0Z%0.2f\n'%(p.pos[0], p.pos[1], config['z1'], config['z0']+3, self.chipbreak, self.vertfeed,clearanceHeight)]
            else:
                return [config['cutter'], 'G81X%0.2fY%0.2fZ%0.2fR%0.2fF%0.2f\nG0Z%0.2f\n'%(p.pos[0], p.pos[1], config['z1'], config['z0']+clearanceHeight,self.vertfeed,clearanceHeight)]
        elif config['mode']=='simplegcode':
            dist= config['z1']-config['z0']
            if self.peck:
                steps = math.floor(dist/self.peck)
            else:
                steps = 1
            step = dist / steps
            ret = 'G0X%0.2fY%0.2f\n'%[p.pos[0], p.pos[1]]
            for i in range(1,steps+1):
                ret+='G0Z%0.2f\n'% i-1*step+0.5
                ret+='G1Z%0.2f\n'% i*step
                ret+='G0Z%0.2f\n'% config['z0']+0.5
            ret += 'G0Z%0.2f\n'%config['clear_height']
            return [config['cutter'], ret]

#       def polygonise(self, resolution=0):
#               config=self.generate_config({'cutterrad':0})
#               p=PSharp(self.pos).point_transform(config['transformations'])
#               self.boundingBox={'bl':p.pos, 'tr':p.pos}
#               self.centre=p.pos
#               return [self.pos]

class ParametricPath3D(Pathgroup):
    def __init__(self, pos, callback, pmin, pmax, pstep, **config):
        self.init(config)
        self.translate(pos)
        self.use_point_z = True
        self.callback = callback
        self.pmin = float(pmin)
        self.pmax = float(pmax)
        self.stepdown = 1000
        if "closed" in config:
            self.closed =config['closed']
        else:
            self.closed = False
        if "do_cutdown" in config:
            self.cutdown = config['do_cutdown']
        else:
            self.cutdown = False
        wholecut = False
        zoff = 0
        while not wholecut:
            zmin = 1000
            wholecut = True
            p= self.pmin
            pa = Path(closed = self.closed, prepend=True)
            pa.use_point_z = True

            while p<pmax:
                pnt = callback(p)
                pnt = V(pnt[0], pnt[1], pnt[2]+zoff)
                zmin = min(pnt[2], zmin)
                if pnt[2] <0:
                    pa.add_point(pnt)
                p+=pstep
            p=pmax
            pnt = callback(p)
            pnt = V(pnt[0], pnt[1], pnt[2]+zoff)
            if pnt[2] <0:
                pa.add_point(pnt)
            if len(pa.points)>0 and self.cutdown!=False:
                self.add(pa,  True)
                wholecut=False
                zoff+=self.cutdown
#               for p in self.points:
#                       print p.pos

class CutSlope3D(Pathgroup):
    def __init__(self, path, direction, **config):
        self.init(config)
        self.use_point_z = True
        self.downmode='down'
        self.stepdown =1000
        if 'angle' in config:
            self.angle = config['angle']
        else:
            self.angle = None
        if 'step' in config:
            self.step = config['step']
        else:
            self.step = None
        if 'side' in config:
            self.side = config['side']
        else:
            self.side = None
        self.direction = direction
        self.distance = direction.length()
        self.path = path
        self.flatpath = self.flatten_path(path)

    def flatten_path(self, path):
        ret = copy.deepcopy(path)
        for i in range(0,len(path.points)):

            ret.points[i].pos=V(path.points[i].pos[0], path.points[i].pos[1])
        return ret

    def unflatten_path(self, path, sourcepath, zoffset):
        ret = copy.deepcopy(path)
        for i in range(0,len(path.points)):
            ret.points[i].pos=V(path.points[i].pos[0], path.points[i].pos[1], sourcepath.points[i].pos[2]+zoffset)
        return ret
    def reverse(self, path):
        path.points.reverse()
        path.reset_points()

    def _pre_render(self, config):
        #assert 'side' in config
        pconfig=self.get_config()
        cutter = milling.tools[pconfig['cutter']]
        if self.step is None:
            if 'min_diameter' in cutter:
                self.step = (cutter['diameter'] - cutter['min_diameter'])/2 *0.8
            else:
                self.step = cutter['diameter']/2 *0.8
        if self.angle is None:
            if 'angle' in cutter:
                self.angle = cutter['angle']
            else:
                self.angle = 45
        dist = self.distance - cutter['diameter']/2
        num_steps = int(math.ceil(dist / self.step))
        thestep = dist/num_steps
        ystep = math.tan(float(self.angle)/180*math.pi)*thestep
        # use a flattened path in case any of the point stuff get confused if the path is not in a plane
        opath = copy.deepcopy(self.flatpath)
        opath2 = copy.deepcopy(self.flatpath)
        if self.side:
            side=self.side
        elif config['side']:
            side=config['side']
        perp = self.direction.normalize()
        for i in reversed(list(range(1, num_steps))):
            if side == 'on':
                npath = copy.deepcopy(opath)
                npath2 = copy.deepcopy(opath)
                for p in range(0,len(npath.points)):
                    npath.points[p].pos +=  i*perp*thestep
                    npath2.points[p].pos += - i*perp*thestep
                self.add(self.unflatten_path(npath, self.path, i*ystep))
                t=self.add(self.unflatten_path(npath2, self.path, i*ystep))
                self.reverse(t)
            else:
                npath = copy.deepcopy(opath)
                for p in range(0,len(npath.points)):
                    npath.points[p].pos +=  i*perp*thestep
                self.add(self.unflatten_path(npath, self.path, i*ystep))
        self.add(self.path)


class RoundSpeakerGrill(Pathgroup):
    def __init__(self,pos, rad, holerad, spacing, **config):
        self.init(config)
        """Cut a circular grid with radius :param rad: of holes with radius :param holerad: and :param spacing:"""+self.otherargs
        if 'pattern' not in config or  not config['pattern'] or config['pattern'] == 'tri':
                yspacing=spacing*math.cos(math.pi/6)
                offset = 0.5
        elif config['pattern']=='square':
                yspacing = spacing
                offset = 0
        numholesx = int(math.ceil(rad/spacing)+1)
        numholesy = int(math.ceil(rad/yspacing))
        for x in range(-numholesx,numholesx):
            for y in range(-numholesy,numholesy):
                if y%2:
                    p=V(x*spacing, y*yspacing)
                else:
                    p=V((x+offset)*spacing, y*yspacing)
                if p.length()<rad-holerad:
                    if 'shape' in config and config['shape']=='hexagon':
                        p=self.add(Polygon(pos+p, sides=6, rad=holerad, startAngle=30))
                    elif 'shape' in config and config['shape']=='drill':
                        p=self.add(Drill(pos+p, rad=holerad))
                    else:
                        self.add(Hole(pos+p, rad=holerad))
class RoundSlitGrill(Pathgroup):
    def __init__(self,pos, rad, slotWidth, spacing, **config):
        self.init(config)
        """Cut a circular grid with radius :param rad: of holes with radius :param holerad: and :param spacing:"""+self.otherargs
        numSlits = int(rad*2/spacing)
        o = float(numSlits)*spacing/2
        for i in range(0,numSlits+1):
            y = -o + i*spacing
            w = math.sqrt(float(rad)**2-y**2)
            if w:
                self.add(RoundedRect(pos+V(0, y), centred=True, width=2*w, height=slotWidth, rad=slotWidth/2, side='in'))

class RoundSlotsGrill(Pathgroup):
    def __init__(self,pos, rad, slotWidth, slotHeight, slotRad, spacingx, spacingy, **config):
        self.init(config)
        """Cut a circular grid with radius :param rad: of slots with width :param slotWidth:, height :param slotHeight: radius :param slotRad: and :param spacing:"""+self.otherargs
        if 'pattern' in config:
            pattern = config['pattern']
        else:
            pattern = 'offset'
        if 'crop' in config:
            crop = config['crop']
        else:
            crop = True
        numRows = int(rad*2/spacingy)
        o = float(numRows)*spacingy/2
        for i in range(0,numRows+1):
            y = -o + i*spacingy
            w = math.sqrt(float(rad)**2-y**2)
            if pattern=='square':
                numCols = int(w/spacingx)*2
            elif pattern=='offset':
                numCols = int(w/spacingx) 
                if numCols%1 != i%1:
                    numCols-=1
            elif pattern=='best_fit':
                print( "i="+str(i)+"fCols = "+str(w*2/spacingx)+" iCol="+str(int(w*2/spacingx)))
                numCols = int(w*2/spacingx)
            if crop:
                numCols+=2
            ox = (float(numCols-1)*spacingx)/2
            print( ox)
            if w:
                for j in range(-1, numCols+1):
                    x = -ox + j*spacingx
                    if type(slotWidth) is list:
                        s = (float(spacingx) - sum(slotWidth))
                        l = len(slotWidth)
                        ds = s/(l)
                        tot=0.5*ds-spacingx/2
                        for k in range(0, l):
                            dx=tot+slotWidth[k]/2
                            self.add(RoundedRect(pos+V(x+dx, y), centred=True, width=slotWidth[k], height=slotHeight, rad=slotRad, side='in'))
                            tot+=slotWidth[k]+ds
                    else:
                        if crop and abs(x)+slotWidth/2>w:
                            if abs(x)+slotWidth/2>w:
                                width = (w - abs(x))*2
                  #              print ("Width="+str(width))
#                               x2 = x/abs(x)*(w-width/2)
                                x2 = x/abs(x)*(abs(x)-slotWidth/2+width/2)
                                if width >slotRad*2:
                                    self.add(RoundedRect(pos+V(x2, y), centred=True, width=width, height=slotHeight, rad=slotRad, side='in'))

                        else:
                            self.add(RoundedRect(pos+V(x, y), centred=True, width=slotWidth, height=slotHeight, rad=slotRad, side='in'))

class RectSlitGrill(Pathgroup):
    def __init__(self,pos, width, height, slitWidth, spacing, **config):
        self.init(config)
        numSlits = int((width - slitWidth)/(slitWidth+spacing))
        x0 = (slitWidth+spacing)*numSlits /2
        for i in range(0,numSlits+1):
                self.add(RoundedRect(pos+V(-x0+i*(slitWidth+spacing), 0), width = slitWidth, height=height, rad=slitWidth/2-0.01, side='in'))

class RectSpeakerGrill(Pathgroup):
    def __init__(self,pos, width, height, holerad, spacing, **config):
        self.init(config)
        """Cut a rectangular grid with width :param width: and height :param height: of holes with radius :param holerad: and :param spacing:"""+self.otherargs
        yspacing=spacing*math.cos(math.pi/6)
        numholesx = int(math.ceil(width/spacing)+1)
        numholesy = float(math.ceil(height/yspacing)+2)
        if numholesy % 2:
            yoff=1.0
        else:
            yoff=0.0
        print("yoff="+str(yoff))
        self.miny=100000
        self.maxy=-100000
        self.minx=100000
        self.maxx=-100000
        for x in range(-numholesx,numholesx):
            count =0;
            for y0 in range(-int(2*numholesy),int(2*numholesy),2):
                y0 = yoff+ y0
                holes=[]
                y=float(y0)/2
                if count%2:
                    p=V(x*spacing, y*yspacing)
                else:
                    p=V((x+0.5)*spacing, y*yspacing)
                if abs(p[0])<=width/2-holerad and abs(p[1])<=height/2-holerad:
                    print(str(x)+","+str(y)+" "+str(p)+" "+str(width/2)+" "+str(height/2))
                    if 'shape' in config and config['shape']=='hexagon':
                        holes.append(Polygon(pos+p, sides=6, rad=holerad, startAngle=30))
                    elif 'shape' in config and config['shape']=='drill':
                        holes.append(Drill(pos+p, rad=holerad))
                    else:
                        print("Rectpeakergrill"+str(pos)+" p="+str(p)+" holerad="+str(holerad))
                        holes.append(Hole(pos+p, rad=holerad))
                    #holes.append(Hole(pos+p, rad=holerad))
                    self.maxx=max(self.maxx, (pos+p)[0])
                    self.maxy=max(self.maxy, (pos+p)[1])
                    self.minx=min(self.minx, (pos+p)[0])
                    self.miny=min(self.miny, (pos+p)[1])
                count+=1
                if x%2:
                   # print("NORMAL")
                    for h in holes:
                        self.add(h)
                else:
                    #print("REVERWSED")
                    for h in reversed(holes):
                        self.add(h)

class LobedCircle(Path):
    def __init__(self,pos, rad, lobe_angle, loberad, num_lobes, lobe_length, **config):
        self.init(config)
        self.closed=True
        if 'angle_offset' in config:
            o = config['angle_offset']
        else:
            o = 0
        step = 360/num_lobes
        for i in range(0,num_lobes):
            self.add_point(PSharp(pos + V(rad,0), transform={'rotate':[pos,o+i*step-lobe_angle]}))
            self.add_point(PIncurve(pos + V(rad+lobe_length,0), radius=loberad, transform={'rotate':[pos,o+i*step]}))
            self.add_point(PSharp(pos + V(rad,0), transform={'rotate':[pos,o+i*step+lobe_angle]}))
            self.add_point(PArc(pos, radius=rad, direction='cw'))



class FilledCircle(Pathgroup):

    def __init__(self, pos, rad, **config):
        self.init(config)
        self.rad=rad
        self.pos=pos
#               sides=int(max(8, rad))

#               self.add(Polygon(pos, rad, sides, partial_fill=rad-0.5, fill_direction='in', side='in'))
        self.circle=self.add(Circle(pos, rad, side='in'))
    def __render__(self,config):
        c=self.circle.generate_config(config)
        self.paths=[]
        if 'partial_fill' in c and c['partial_fill'] and c['partial_fill']>0:
            steps = math.ceil((c['partial_fill'] - c['cutterrad']) /c['cutterrad']/1.2)
            if 'overview' in config and config['overview'] or c['cutterrad']<0.1:
                steps=1
            step = (c['partial_fill'] - c['cutterrad'])/steps
        else:
            r=self.rad-c['cutterrad']
            if c['cutterrad']==0:
                steps=1
            else:
                steps=math.ceil(r/c['cutterrad']/1.2)
            if 'overview' in config and config['overview'] or c['cutterrad']<0.1:
                steps=1
            if steps==0:
                steps=1
            step=r/steps
        for i in range(0,int(steps)+1):
            if(self.rad-(steps-i)*step!=0):
                t=self.add(Circle(self.pos, self.rad-(steps-i)*step, side='in'))
class FilledRect(Pathgroup):

    def __init__(self, bl,  **config):
        self.init(config)
        if 'centred' in config and config['centred'] or ('width' in config and 'height' in config):
            self.width = float(config['width'])
            self.height = float(config['height'])
            self.pos=bl
        elif 'tr' in config:
            tr=config['tr']
            d = bl-tr
            self.width = float(abs(bl[0]-tr[0]))
            self.height = float(abs(bl[1]-tr[1]))
            self.pos=(bl+tr)/2
        self.maxdist = min(self.width, self.height)/2
        if 'rad' in config:
            self.rad=config['rad']
        else:
            self.rad=0
        if 'cornertype' in config:
            self.cornertype=config['cornertype']
        else:
            self.cornertype=PSharp
        if 'noFinal' in config:
            self.noFinal=config['noFinal']
        else:
            self.noFinal=False
#               sides=int(max(8, rad))

#               self.add(Polygon(pos, rad, sides, partial_fill=rad-0.5, fill_direction='in', side='in'))
        if 'cutterrad' in config:
                cutterrad = config['cutterrad']
        else:
                cutterrad = 0
        filldist= min(self.width,self.height)/2 -cutterrad
        self.add(RoundedRect(self.pos, rad=self.rad, width=self.width, height=self.height, centred=True, side='in', fill_direction='in', partial_fill=filldist, noFinal=self.noFinal))
        #self.rect=RoundedRect(self.pos, rad=self.rad, width=self.width, height=self.height, centred=True, side='in')
#       def __render__(self,config):
#               c=self.rect.generate_config(config)
#               self.paths=[]
#               d=self.maxdist-c['cutterrad']
#               if c['cutterrad']>0:
#                       steps=math.ceil(d/c['cutterrad']/1.2)
#                       step=(self.maxdist+c['cutterrad']/2)/steps
#                       for i in range(1,int(steps)):
#                                rad=self.rad-step*i
#                                if rad<0:
#                                        rad=0
#                                diff = step*i
#                                self.add(RoundedRect(self.pos, rad=rad, width=self.width-diff*2, height=self.height-diff*2, centred=True, side='in', z1=self.z1))
#               if not self.noFinal:
#                       self.add(Rect(self.pos, rad=self.rad, width=self.width, height=self.height, centred=True, side='in', cornertype=self.cornertype, z1=self.z1))



class Chamfer(Pathgroup):
    def __init__(self, path, chamfer_side, **config):
        if 'chamfer_depth' not in config:
            self.chamfer_depth=False
        else:
            self.chamfer_depth=config['chamfer_depth']
        if 'chamfer_angle' not in config:
            self.chamfer_angle=None
        else:
            self.chamfer_depth=config['chamfer_angle']
        if 'chamfer_ref' not in config:
            self.chamfer_ref='top'
        elif config['chamfer_ref'] in ['top', 'bottom']:
            self.chamfer_ref=config['chamfer_ref']
        else:
            raise('Chamfer: chamfer_ref should be top or bottom')
        if 'chamfer_offset' in config:
            self.chamfer_offset=config['chamfer_offset']
        else:
            self.chamfer_offset=0

        self.chamfer_side=chamfer_side
        self.init(config)
        self.chamfer_path=path
#               self.add(path)

    def __render__(self,config):
        c=self.chamfer_path.generate_config(config)
        self.paths=[]
        if hasattr(self, 'cutter') and self.cutter is not None:
            cutter=self.cutter
        elif 'cutter' in c and c['cutter'] is not None:
            cutter=c.cutter
        else:
            print("No cutter")
            cutter=None
        if self.chamfer_angle==None:
            if c['cutter'] and 'angle' in milling.tools[c['cutter']]:
                self.chamfer_angle= milling.tools[c['cutter']]['angle']
        if 'cutterrad' in c and c['cutterrad']:
            cutterrad=c['cutterrad']
        elif cutter is not None:
            cutterrad=milling.tools[cutter]['diameter']/2
        if 'z0' not in c or c['z0']==None:
            z0=0
        else:
            z0=c['z0']
        if 'z1' not in c or c['z1']==None:
            if 'thickness' in c:
                z1=-c['thickness']-0.5
            else:
                print("CHamfer: z1 not definined and no thickness")
                z1=z0
        else:
            z1=c['z1']
        if self.chamfer_angle==None:
            if 'angle' in milling.tools[cutter]:
                self.chamfer_angle=milling.tools[cutter]['angle']
            else:
                self.chamfer_angle=45
                print("Chamfer angel is not set so assuming 45")

        if self.chamfer_depth==False or self.chamfer_depth==None:
            zdiff= z1-z0
        else:
            zdiff=-self.chamfer_depth-z0
        xdiff= zdiff*math.tan(float(self.chamfer_angle)/180*math.pi)
        if c['stepdown'] is not None:
            stepdown=c['stepdown']
        elif 'material' in c and milling.materials[c['material']]:
            stepdown = milling.materials[c['material']]['stepdown']
        steps=max( math.ceil(abs(float(zdiff)/stepdown)), math.ceil(abs(float(xdiff)/cutterrad*0.8)) )
        zstep=zdiff/steps
        xstep=xdiff/steps
        xoffset=self.chamfer_offset/zdiff*xdiff
        if self.chamfer_ref=='bottom':
            startpath=copy.copy(self.chamfer_path.offset_path(side=self.chamfer_side, distance=xdiff, config=c))
        else:
            startpath=copy.copy(self.chamfer_path)
        for i in range(1, int(steps+1)):
            tc=copy.copy(c)
            startpath.z0=0#(i-1)*-zstep
            startpath.z1=i*zstep
#                       tc['partial_fill']=xstep*(steps-i)-0.1
#                       tc['fill_direction']=self.chamfer_path.otherDir(self.chamfer_side)
            temp=startpath.offset_path(side=self.chamfer_side, distance=abs(xstep*(i))+abs(xoffset), config=tc)
#                       print temp
#                       print callable(self.add)
            self.add(temp)

class CircleChord(Path):
    """ Creates part of a circle as if it were filled with water from bottom rad - radius of circle height depth of water. pos is centre of circle"""
    def __init__(self, pos, rad, height, **config):
        self.init(config)
        if height>=2*rad:
            raise ValueError("height must be less than diam")
        self.closed=True

        # horrible fudge!!!
        if height<rad:
            if self.side=='in':
                self.side='out'
            elif self.side=='out':
                self.side='in'

        self.direction='cw'
        if height <=rad:
            end_x = math.sqrt(rad**2-height**2)
        else:
            end_x = math.sqrt(rad**2-(height-rad)**2)
        h = rad -height
        self.add_point(V(-end_x, h)+pos)
        self.add_point(PArc(V(0, 0)+pos, radius=rad, direction='cw'))
        self.add_point(V(end_x, h)+pos)




class DoubleFlat(Path):
    def __init__(self, pos, rad, flat_rad, **config):
        """Cut a circle with two flats, centred at :param pos: with radius :param rad: and :param flat_rad: is half the distance between the flats"""
        self.init(config)
        self.closed=True
        y=math.sqrt(rad**2 - flat_rad**2)
        self.add_point(pos+V(-flat_rad,0))
        self.add_point(pos+V(-flat_rad,-y), point_type='clear')
#               self.add_point(pos, radius=rad, direction='cw', point_type='arc')
#               self.add_point(pos, radius=rad, direction='cw', point_type='aroundcurve')
        self.add_point(pos, direction='ccw', radius=rad, point_type='arc')
        self.add_point(pos+V(flat_rad, -y), point_type='clear')
        self.add_point(pos+V(flat_rad, 0), point_type='sharp')
        self.add_point(pos+V(flat_rad, y),  point_type='clear')
#               self.add_point(pos, radius=rad, point_type='arc', direction='cw')
#               self.add_point(pos, radius=rad, point_type='aroundcurve', direction='cw')
        self.add_point(pos,  point_type='arc', radius=rad, direction='ccw')
        self.add_point(pos+V(-flat_rad,y), point_type='clear')

class Cross(Pathgroup):
    def __init__(self, pos, rad, **config):
        self.init(config)
        """Cut a cross with radius :param rad: at :param pos: oriented NS EW"""+self.otherargs
        a=Path(closed=False)
        b=Path(closed=False)
        a.add_point(V(pos[0]+rad, pos[1]))
        a.add_point(V(pos[0]-rad, pos[1]))
        b.add_point(V(pos[0], pos[1]+rad))
        b.add_point(V(pos[0], pos[1]-rad))
        self.add(a)
        self.add(b)
        print("cross os="+str(pos)+" rad="+str(rad))
        self.comment("Cross")
        self.comment("pos="+str(pos)+" rad="+str(rad))

class KeyHole(Path):
    def __init__(self, pos, rad, smallrad, h, **config):
        self.init(config)
        self.closed = True
        kw = smallrad
        kh = h
        kr = rad
        ky = math.sqrt(rad**2 - kw**2)+0.01
        if 'double' in config and config['double']:
            self.add_point(PIncurve(pos+V(kw, kh), radius = kw))
            self.add_point(PIncurve(pos+V(-kw, kh), radius = kw))
            self.add_point(pos+V(-kw, ky))
            self.add_point(PAroundcurve(pos+V(0, 0), radius = kr, direction='ccw'))
            self.add_point(pos+V(-kw, -ky))
            self.add_point(PIncurve(pos+V(-kw, -kh), radius = kw))
            self.add_point(PIncurve(pos+V(kw, -kh), radius = kw))
            self.add_point(pos+V(kw, -ky))
            self.add_point(PAroundcurve(pos+V(0, 0), radius = kr, direction='ccw'))
            self.add_point(pos+V(kw, ky))
        else:
            self.add_point(PIncurve(pos+V(kw, kh), radius = kw))
            self.add_point(PIncurve(pos+V(-kw, kh), radius = kw))
            self.add_point(pos+V(-kw, ky))
            self.add_point(POutcurve(pos+V(0, 0), radius = kr))
            self.add_point(pos+V(kw, ky))


class RepeatLine(Part):
    def __init__(self, start, end, number, ob, args, **config):
        self.init(config)
        """Repeat :param number: objects of type :param ob: in a line from :param start: to :param end:"""+self.otherargs
        if 'layers' in config:
            layers=config['layers']
        else:
            layers=False
        step=(end-start)/(number-1)
        if type(ob)==type:
            for i in range(0,number):
                t=self.add(ob(start+step*i, **args),layers).paths
            self.comment("RepeatLine")
            self.comment("start="+str(start)+" end="+str(end)+" number="+str(number))
        elif hasattr(ob, 'obType') and (ob.obType=='Part' or ob.obType=='Path' or ob.obType=='Pathgroup'):
            for i in range(0,number):
                t=copy.deepcopy(ob)
                t.transform['translate']=start+step*i
                self.add(t)
class RepeatSpacedGrid(Part):
    def __init__(self, start, dx, dy, numberx, numbery, ob, args,layers, **config):
        self.init(config)
        """Repeat objects of type :param ob: in a grid this can be rectangular if :param dx: and :param dy: are perpendicular or skewed if the are not
:param start: - position grid is started at
:param dx: - the step between objects in one direction
:param dy: - the step in the other direction
:param numberx: - the number of objects in x direction
:param numbery: - the number of objects in y direction
:param ob: - the object type
:param args: - arguments to initialise ob (dict)
:param centred: - the grid is centred rather than starting at a corner
"""+self.otherargs
        numberx = int(numberx)
        numbery = int(numbery)
        if 'centred' in config and config['centred'] is True:
            start= start -((dx*(numberx-1))/2+dy*(numbery-1)/2)
        for i in range(0,numberx):
            for j in range(0,numbery):
                self.add(ob(start+dx*i+dy*j, **args),layers)
        self.comment("RepeatSpacedGrid")
        self.comment("start="+str(start)+" dx="+str(dx)+" dy="+str(dy)+" numberx"+str(numberx)+" numbery"+str(numbery))

class Hole(Pathgroup):
    def __init__(self, pos, rad, **config):
        self.init(config)
        """Cut a hole at :param pos: with radius :param rad:
:param rad: can be a list as can :param z1:"""+self.otherargs
        if 'side' not in config:
            config['side']='in'
        if type(rad) is list:
            for i,r in enumerate(rad):
                if 'z1' in list(config.keys()) and type(config['z1']) is list:
                    c=copy.copy(config)
                    if i <= len(config['z1']):
                        c['z1']=config['z1'][i]
                        self.add(Circle(pos, rad[i],  **c))
                    else:
                        c['z1']=config['z1'][len(config['z1'])]
                        self.add(Circle(pos, rad[i],  **c))
                else:
                    self.add(Circle(pos, rad[i], **config))
        else:
            if 'z1' in config and type(config['z1']) is list:
                print("z1 should only be a list if rad is also  a list "+str(config['z1']))
            self.add(Circle(pos, rad, **config))
        self.comment("Hole")
        self.comment("pos="+str(pos)+" rad="+str(rad))

class HoleLine(Pathgroup):
    def __init__(self, start, end, number, rad, **config):
        self.init(config)
        if 'hole_depth' in config and config['hole_depth'] is not False:
            z1=-config['hole_depth']
        else:
            z1=False

        step=(end-start)/(number-1)
        for i in range(0,number):
            self.add(Hole(start+step*i, rad=rad, z1=z1)) #self.add(Hole(start+step*i, rad, 'in'))
        self.comment("HoleLine")
        self.comment("start="+str(start)+" end="+str(end)+" number="+str(number)+" rad="+str(rad))

class Screw(Part):
    def __init__(self,pos, **config):
        self.init(config)
        if 'layer_config' in config:
            layer_conf=config['layer_config']
            for c in list(layer_conf.keys()):
                print("c"+str(c)+" pos="+str(pos))
                conf = copy.deepcopy(layer_conf[c])
                if 'drill' in conf and conf['drill']:
                    self.add(Drill(pos, **conf), c)
                else:
                    self.add(Hole(pos, **conf), c)
class FourScrews(Part):
    def __init__(self, bl, layer_conf, **config):
        self.init(config)
        self.add(FourObjects(bl,  Screw(V(0,0), layer_config=layer_conf,**config), **config))
#               d=tr-bl
#               self.add(Screw(bl, layer_config=layer_conf, **config))
#               self.add(Screw(bl+V(d[0], 0), layer_config=layer_conf, **config))
#               self.add(Screw(bl+V(0, d[1]), layer_config=layer_conf, **config))
#               self.add(Screw(tr, layer_config=layer_conf, **config))

class CopyObject(Part):
    """Copy object :param ob: centred on each of the list :param points:"""
    def __init__(self, ob, points, **config):
        self.init(config)
        if type(points) is not list:
            raise TypeError("points should be a list of vecs")
        for p in points:
            t=copy.deepcopy(ob)
            t.translate(p)
            if 'layers' in config and config['layers'] is not None:
                self.add(t, config['layers'])
            else:
                self.add(t)
class FourObjects(Part):
    """Copy object :param ob: onto four corners of a rectangle defined form :param bl: and :param tr: or :param bl: :param width: :param height: when :param centrend: is true"""
    def __init__(self, bl, ob, **config):
        self.init(config)
        if 'centred' in config or 'tr' not in config:
            if 'width' in config and 'height' in config:
                w=config['width']/2
                h=config['height']/2
                points=[bl+V(w,h), bl+V(-w,h), bl+V(-w,-h), bl+V(w, -h)]
            else:
                raise ValueError('If using centred mode you need a width and height defined')
        else:
            if 'tr' in config:
                d=config['tr']-bl
                points=[bl, bl+V(d[0], 0), bl+d, bl+V(0,d[1])]
        if ob.obType=='Part':
            self.add(CopyObject(ob, points))
        else:
            self.add(CopyObject(ob, points, layers=config['layers']))
class LineObjects(Part):
    """Copy object :param ob:, :param num: times, between :param a: and :param b:"""
    def __init__(self, a, b, fromends, num, ob, **config):
        self.init(config)
        if 'doends' in config and not config['doends']:
            starti = 1
            endi = num -1
        else:
            starti = 0
            endi = num
        totlength=(b-a).length()
        length=totlength-2*fromends
        # if we just have one hole put it in the middle
        if num==1:
            self.add(CopyObject(ob, [(a+b)/2]))
        else:
            if('stepLength' in config):
                step=(b-a).normalize() * config['stepLength']
                if num is None or num is False:
                    num = int((b-a).length() / config['stepLength'])
            else:
                step=(b-a)/(num-1)
                step=length/(num-1)*(b-a).normalize()
            start=a+fromends*(b-a).normalize()
            points=[]
            for i in range(0, num):
                points.append(start+step*i)
            if ob.obType=='Part':
                self.add(CopyObject(ob, points))
            else:
                self.add(CopyObject(ob, points, layers=config['layers']))

class SquareObjects(Part):
    """Copy objects around the edge of a square defined with bl&tr or bl, centred, width and height. starting :param fromends: from the ends. numx and numy on sides"""
    def __init__(self, bl, numx, numy, ob, **config):
        self.init(config)
        if 'centred' in config and config['centred']:
            centre=bl
            w=config['width']/2
            h=config['height']/2
        else:
            centre=(bl+config['tr'])/2
            w=(config['tr']-bl)[0]/2
            h=(config['tr']-bl)[1]/2
        if 'fromends' in config:
            fe=config['fromends']
        else:
            fe=0
        if 'layers' in config:
            l=config['layers']
        else:
            l=None
        # if there is no fromends then don't cut the corner objects twice
        if fe==0:
            if numx>3:
                stepx = 2*w/(numx-1)
                self.add(LineObjects(centre+V(-w,-h+fe), centre+V(-w,h-fe), 0, numy, ob, layers=l))
                self.add(LineObjects(centre+V(-w+fe+stepx,h), centre+V(w-fe-stepx,h), 0, numx-2, ob, layers=l))
                self.add(LineObjects(centre+V(w,h-fe), centre+V(w,-h+fe), 0, numy, ob, layers=l))
                self.add(LineObjects(centre+V(w-fe-stepx,-h), centre+V(-w+fe+stepx,h), 0, numx-2,  ob, layers=l))
            elif numx==3:
                self.add(LineObjects(centre+V(-w,-h+fe), centre+V(-w,h-fe),0, numy, ob, layers=l))
                self.add(CopyObject(ob,[centre+V(0,-h)], layers=l))
                self.add(LineObjects(centre+V(w,h-fe), centre+V(w,-h+fe), 0, numy, ob, layers=l))
                self.add(CopyObject(ob,[centre+V(0,h)], layers=l))
            else:
                self.add(LineObjects(centre+V(-w,-h+fe), centre+V(-w,h-fe), 0, numy, ob, layers=l))
                self.add(LineObjects(centre+V(w,h-fe), centre+V(w,-h+fe), 0, numy, ob, layers=l))
        else:
            self.add(LineObjects(centre+V(-w,-h+fe), centre+V(-w,h-fe), 0, numy, ob, layers=l))
            self.add(LineObjects(centre+V(-w+fe,h), centre+V(w-fe,h), 0, numx, ob, layers=l))
            self.add(LineObjects(centre+V(w,h-fe), centre+V(w,-h+fe), 0, numy, ob, layers=l))
            self.add(LineObjects(centre+V(w-fe,-h), centre+V(-w+fe,-h), 0, numx, ob, layers=l))

class Bolt(Part):
    def __init__(self,pos,thread='M4',head='button', length=10, **config):
        """ thread - thread type, head - head type, length - bolt length, insert_layer - the layer or layers inserts should be added to , clearance layers - the layers that should have a clearance hole, head_layer - layer for bolt head"""
        self.init(config)
        self.add_bom("Machine screw", 1, str(length)+"mm "+str(thread)+" "+str(head),'')
        if 'clearance_layers' in config:
            clearance_layers = config['clearance_layers']
        else:
            clearance_layers = []#['perspex', 'paper']
        if 'insert_layer' in config:
            insert_layer = config['insert_layer']
        else:
            insert_layer = []#'base'
        if 'head_layer' in config:
            head_layer = config['head_layer']
        else:
            head_layer = []#'top'
        if 'thread_layer' in config:
            thread_layer = config['thread_layer']
        else:
            thread_layer = []#['back']
        if 'thread_depth' in config:
            thread_depth = config['thread_depth']
        else:
            thread_depth = False
        if 'underinsert_layer' in config:
            underinsert_layer = config['underinsert_layer']
        else:
            underinsert_layer = False#['underbase']
        if 'underinsert_depth' in config:
            underinsert_depth = config['underinsert_depth']
        else:
            underinsert_depth = False

        if thread in milling.bolts:
            if insert_layer is not False:
                if 'insert_type' in config and config['insert_type'] in milling.inserts[thread]:
                    insert=milling.inserts[thread][config['insert_type']]
                elif thread in milling.inserts:
                    insert=milling.inserts[thread]
                else:
                    print(thread+" is not in milling.inserts")
                    insert=False
                if insert:
                    self.add_bom("Wood insert", 1, str(thread)+"insert",'')
                    for i,diam in enumerate(insert['diams']):
    #                                       self.add(Insert(pos, config['insert_type'], **config))
                        if 'z1' in config and insert['depths'][i] is False:
                            print("z1="+str(config['z1']))
                            depth=config['z1']
                        else:
                            depth = insert['depths'][i]
                        self.add(Hole(pos, insert['diams'][i],  side='in' , z1 = depth ),insert_layer)
            if underinsert_layer is not False:
                if 'insert_type' in config and config['insert_type'] in milling.inserts[thread]:
                    insert=milling.inserts[thread][config['insert_type']]
                else:
                    insert=milling.inserts[thread]
                i = insert['depths'].index(False)
                if underinsert_depth:
                    self.add(FilledCircle(pos, rad=insert['diams'][i], z1=-underinsert_depth), underinsert_layer)
                else:
                    self.add(Hole(pos, insert['diams'][i],  side='in' , z1=insert['depths'][i]),underinsert_layer)

            self.add(Hole(pos, (milling.bolts[thread]['clearance'])/2, side='in'),clearance_layers)
            if(head=='countersunk'):
                self.add(Countersink(pos, milling.bolts[thread]['clearance'], milling.bolts[thread]['countersunk']['diam']/2, config),head_layer)
            elif head=='cap':
                self.add(Hole(pos, rad=milling.bolts[thread]['allen']['head_d']/2, z1=-milling.bolts[thread]['allen']['head_l']), head_layer)
                self.add(Hole(pos, milling.bolts[thread]['clearance']/2, side='in'),head_layer)
            else:
                self.add(Hole(pos, milling.bolts[thread]['clearance']/2, side='in'),head_layer)
            if thread_layer:
                if thread_depth:
                    self.add(Hole(pos, milling.bolts[thread]['tap']/2, side='in', z1=-thread_depth),thread_layer)
                else:
                    self.add(Hole(pos, milling.bolts[thread]['tap']/2, side='in'),thread_layer)

#class AngledButtJoint(list):
#    def __init__(self, start, end, side, linemode, startmode, endmode, hole_spacing, thickness, cutterrad,  angle, lineside='back', **config):
#        newThickness = abs(thickness / math.sin(float(angle)/math.pi*180))

#        for p in ButtJoint(start, end, side, linemode, startmode, endmode, hole_spacing, newThickness, cutterrad,**config):
#            self.append(p)
class ButtJoint(list):
    def __init__(self, start, end, side, linemode, startmode, endmode, hole_spacing, thickness, cutterrad, **config):
        assert startmode==endmode, "ButtJoint - startmode and endmode should be the same"
        parallel=(end-start).normalize( )
        if side=='left':
            perp = rotate(parallel,-90)
        else:
            perp = rotate(parallel,90)
#               if we set this to zero bad things happen. probably to do with points being on top of each other for intersections
        depth=0.0
        if 'joint_type' in config:
            joint_type=config['joint_type']
        else:
            joint_type='convex'
        if 'butt_depression' in config:
            if config['butt_depression'] is not None and config['butt_depression']>0:
                depression=True
                depth = config['butt_depression']
            else:
                depression=False
        if 'last_offset' in config and config['last_offset']!=0:
            last_offset = parallel*config['last_offset']
        else:
            last_offset = parallel*0
        if 'next_offset' in config and config['next_offset']!=0:
            next_offset = parallel*config['next_offset']
        else:
            next_offset = parallel*0
        if 'nextparallel' in config:
            nextparallel = config['nextparallel']
        else:
            nextparallel = False
        if 'lastparallel' in config:
            lastparallel = config['lastparallel']
        else:
            lastparallel = False

        if (startmode == 'off') and (joint_type=='convex') :
            extra=thickness
        elif (startmode == 'on') and (joint_type=='convex') :
            extra=depth
        elif (startmode == 'off') and (joint_type=='concave') :
            extra=thickness-depth
        elif (startmode == 'on') and (joint_type=='concave') :
            extra=0
        if startmode == 'straight':
            extra=0
        lastcorner = config['lastcorner']
        nextcorner = config['nextcorner']
        if cutterrad==0:
            pointtype=PInsharp
        else:
            pointtype=PSharp
#               if abs(extra)>0 and startmode == 'on' and lastcorner != 'off':
        if abs(extra)>0 and  (startmode == 'off') and (joint_type=='concave' or lastcorner!=startmode):
            self.append(pointtype(start+last_offset+perp*thickness))
        elif abs(extra)>0 and not  (startmode == 'off' and lastcorner == 'off') and not lastparallel:
            self.append(pointtype(start+last_offset))
        self.append(pointtype(start+last_offset+extra*perp))
#               self.append(PSharp((start+end)/2+extra*perp))
        self.append(pointtype(end-next_offset+extra*perp))

#               if startmode == 'on' and nextcorner!='off' and  abs(extra)>0:
        if  abs(extra)>0 and (startmode == 'off') and (joint_type=='concave' or nextcorner!=endmode):
            self.append(pointtype(end-next_offset+perp*thickness))
        elif  abs(extra)>0 and not (endmode == 'off' and nextcorner == 'off') and not nextparallel:
            self.append(pointtype(end-next_offset))

class AngledButtJoint(ButtJoint):
    def __init__(self, start, end, side, linemode, startmode, endmode, hole_spacing, thickness, cutterrad,  angle, lineside='back', **config):
        newThickness = abs(thickness / math.cos(float(angle)*math.pi/180))
        super(AngledButtJoint, self).__init__(start, end, side, linemode, startmode, endmode, hole_spacing, newThickness, cutterrad,**config)

class MitreJoint(ButtJoint):
    def __init__(self, start, end, side, linemode, startmode, endmode, hole_spacing, thickness, cutterrad,  angle, lineside='back', **config):
        if 'joint_type' in config:
            joint_type = config['joint_type']
        else:
            joint_type = 'convex'
        if joint_type=='convex':
            startmode='off'
        else:
            startmode='on'
        newThickness = thickness * ( math.tan(float(angle)/2/180*math.pi))
        super(MitreJoint, self).__init__(start, end, side, linemode, startmode, startmode, hole_spacing, newThickness, cutterrad,**config)

class ButtJointMid(Pathgroup):
    def __init__(self, start, end, side,linemode, startmode, endmode, hole_spacing, thickness, cutterrad, prevmode, nextmode, **config):
        self.init(config)
        assert startmode==endmode, "ButtJoint - startmode and endmode should be the same"
        if 'fudge' in config:
            fudge = config['fudge']
        else:
            fudge = 0
        if 'joint_type' in config:
            joint_type=config['joint_type']
        else:
            joint_type='convex'
        if side=='left':
            perp = rotate((end-start).normalize(),-90)
        else:
            perp = rotate((end-start).normalize(),90)
        if 'butt_num_holes' in config and type(config['butt_num_holes']) is not None:
            num_holes = config['butt_num_holes']
        else:
            num_holes = int(math.ceil((end-start).length()/hole_spacing))
        if 'hole_offset' in config and config['hole_offset'] is not None:
            hole_offset = config['hole_offset']
        else:
            hole_offset = 0
        if num_holes>0:
            hole_length = (end-start).length()/num_holes
        else:
            hole_length = 1
        parallel=(end-start).normalize( )
        holes=True
        depression=False
        if (startmode == 'off') == (joint_type=='convex'):
            if 'butt_depression' in config and config['butt_depression']!=None:
                if config['butt_depression']>0:
                    depression=True
                    depth = config['butt_depression']
                else:
                    depression=False
            if 'butt_outline' in config and config['butt_outline']!=None:
                outline=config['butt_outline']
            else:
                outline=False
            if 'butt_holerad' in config and config['butt_holerad']!=None:
                holerad = config['holerad']
            else:
                holerad = 4.2/2
            if joint_type=='convex':
                holepos = thickness/2-hole_offset
                deppos = 0
            else:
                holepos = thickness/2+hole_offset
                deppos = 0
            if holes:
                if 'hole_depth' in config:
                    hole_depth = config['hole_depth']
                else:
                    hole_depth = False
                self.add(HoleLine(start+parallel*hole_length/2 + perp*(holepos), end - parallel*hole_length/2 + perp*(holepos), num_holes,  holerad, hole_depth=hole_depth))

            if depression:
                self.add(FilledRect(
                                bl = start-parallel*fudge - perp*(-deppos+fudge),
                                tr = end+perp*(thickness+fudge+deppos)+parallel*fudge,
                                z1 = -depth, side='in',
                                cornertype = PInsharp,
                                ))
            if outline:
#                print(outline)
#                               self.add(Rect(
#                                       bl = start-parallel*fudge - perp*(-deppos+fudge),
 #                                               tr = end+perp*(thickness+fudge+deppos)+parallel*fudge,
  #                                              z1 = -outline, side='out',
   #                                             cornertype = PInsharp))
                self.add(Lines([ start - parallel*fudge - perp*(-deppos+fudge),
                                start - parallel*fudge + perp*(thickness+fudge+deppos),
                                end + perp*(thickness+fudge+deppos) + parallel*fudge,
                                end - perp*(-deppos+fudge) + parallel*fudge,
                        ],
                        closed=True,
                        z1 = -outline, side='out', cornertype = PInsharp))

class AngledButtJointMid(ButtJointMid):
    def __init__(self, start, end, side,linemode, startmode, endmode, hole_spacing, thickness, cutterrad, prevmode, nextmode,  angle, lineside='back', **config):
        config['hole_depth']=2
#        print ("lineside="+str(lineside)+" angle="+str(angle)+" obtuse="+str(config['obtuse']))
        newThickness = thickness / math.cos(float(angle)*math.pi/180)
       # newThickness = thickness / math.sin(float(angle)/math.pi*180)
        if 'hole_offset' in config and config['hole_offset'] is not None:
            config['hole_offset']/=math.cos(float(angle)/math.pi*180)
        else:
            config['hole_offset']=0
        if lineside=='back' == ('obtuse' in config and config['obtuse']==1):
            config['hole_offset'] -= newThickness-thickness
       # else:
        #    config['hole_offset'] += newThickness-thickness

            #config['hole_offset']+=newThickness-thickness
      #  else:
       #     config['hole_offset']=newThickness-thickness
      #  print("new Hole_offset="+str(config['hole_offset']))
        super(AngledButtJointMid, self).__init__(start, end, side,linemode, startmode, endmode, hole_spacing, newThickness, cutterrad, prevmode, nextmode, **config)

class FingerJointMid(Pathgroup):
    def __init__(self, start, end, side,linemode, startmode, endmode, tab_length, thickness, cutterrad, prevmode, nextmode, **config):
        """Produce points for a finger joint cut on :param side: of a line from :param start: to :param end:
The line defines the
:param linemode: 'internal' - for a joint that is in a hole in a piece of wood 'external' is a side of a box
:param start: Point to start reference line
:param end: Point to end reference line
:param side: side to cut into wood of the reference line
:param startmode: start 'on' or 'off' the reference line
:param endmode: end 'on' or 'off' the reference line
:param tab_length: approximate tab length
:param thickness: thickness of the material
:param cutterrad: radius of the cutter you are using
:param fudge: a fudge factor that increases the gap along the finger joint when negative - it should be 1/4 of the gap you want\n"""
        self.init( config)
        print("FingerJointMid "+str(start)+"->"+str(end)+" side="+str(side))
        if 'fudge' in config:
            fudge=config['fudge']
        else:
            fudge=0
        num_tab_pairs= math.floor((end-start).length()/tab_length/2)
        if startmode==endmode:
            num_tabs = num_tab_pairs*2+1
        else:
            num_tabs = num_tab_pairs*2
        tab_length = (end-start).length()/num_tabs
        if side=='left':
            perp = rotate((end-start).normalize(),-90)
        else:
            perp = rotate((end-start).normalize(),90)
        if 'depth' in config:
            depth = config['depth']
            print("depth="+str(depth))
        else:
            depth = False
        parallel=(end-start).normalize( )
        along=parallel*tab_length
        cra=(end-start).normalize()*-(cutterrad+fudge)
        crp=perp*-(cutterrad+fudge)
        cutin=perp*thickness
        if startmode=='on':
            # cut a bit extra on first tab if the previous tab was off as well
            if prevmode=='on':
                if depth:
                    print("doedepth")
                    self.add(Lines([start-parallel*thickness+cra+crp, start+cra-crp, start+along+cutin-cra-crp, start+along+cutin+cra-crp-parallel*thickness], closed=True, side='in', cornertype=PInsharp, z1=-depth).fill_path('in', 4.0/2, z1=-depth))

                #else:
                self.add(Lines([start-parallel*thickness+cra+crp, start+cra-crp, start+along+cutin-cra-crp, start+along+cutin+cra-crp-parallel*thickness], closed=True, side='in', cornertype=PInsharp))
#                               self.add(ClearRect(bl=start-parallel*thickness+cra+crp, tr=start+along+cutin-cra-crp, direction='cw', side='in'))
            else:
                pass
#                               self.add(ClearRect(bl=start-parallel+cra+crp, tr=start+along+cutin-cra-crp, direction='cw', side='in'))
            m='off'
        else:
            m='on'
        for i in range(1,int(num_tabs)):
            if m=='on':
                # cut a bit extra on last tab if the next tab was off as well
                if i==num_tabs and nextmode=='off':
                    p=Lines([start+along*i+-cra-crp, start+along*(i+1)+cra-crp, start+along*(i+1)+cutin+cra+crp+parallel*thickness, start+along*i+cutin-cra+crp+parallel*thickness], closed=True, side='in', cornertype=PInsharp)
#                                       self.add(ClearRect(bl=start+along*i+cra+crp, tr=start+along*(i+1)+cutin-cra-crp+parallel*thickness, direction='cw', side='in'))
                else:
                    p=Lines([start+along*i-cra-crp, start+along*(i+1)+cra-crp, start+along*(i+1)+cutin+cra+crp, start+along*i+cutin-cra+crp], closed=True, side='in', cornertype=PInsharp)
#                                       self.add(ClearRect(bl=start+along*i+cra+crp, tr=start+along*(i+1)+cutin-cra-crp, direction='cw', side='in'))

                if depth:
                    p.z1=-depth
                    self.add(p.fill_path('in', 4.0/2))
                #else:
                self.add(p)
                m='off'
            else:
                m='on'
        self.comment("FingerJointMid")

class FingerJointBoxMidSide(Pathgroup):
    def __init__(self, pos, width, height, corners, sidemodes, tab_length, thickness, cutter,**config):
        config['direction']='ccw'
        self.init(config)
        if 'centred' in config:
            pos=pos - V(width, height)/2
        self.closed=True
        s='left'
        if sidemodes==True:
            sidemodes={'left':True, 'top':True, 'right':True, 'bottom':True}
        linemode='internal'
        cutterrad = 0#milling.tools[cutter]['diameter']/2
        if 'fudge' in config:
            fudge=config['fudge']
        else:
            fudge=0
        if type(thickness) is dict:
            th = thickness
        else:
            th = {'left':thickness, 'right':thickness, 'top':thickness, 'bottom':thickness}
        if sidemodes['left']:
            self.add(FingerJointMid(start=pos+V(0,0), end=pos+V(0,height), side=s, linemode=linemode, startmode=corners['left'], endmode=corners['left'], tab_length=tab_length, thickness=th['left'], cutterrad=cutterrad, prevmode=corners['bottom'], nextmode=corners['top'], fudge=fudge))
        if sidemodes['top']:
            self.add(FingerJointMid(start=pos+V(0,height), end=pos+V(width,height), side=s, linemode=linemode, startmode=corners['top'], endmode=corners['top'], tab_length=tab_length, thickness=th['top'], cutterrad=cutterrad, prevmode=corners['left'], nextmode=corners['right'], fudge=fudge))
        if sidemodes['right']:
            self.add(FingerJointMid(start=pos+V(width, height), end=pos+V(width,0), side=s, linemode=linemode, startmode=corners['right'], endmode=corners['right'], tab_length=tab_length, thickness=th['right'], cutterrad=cutterrad, prevmode=corners['top'], nextmode=corners['bottom'], fudge=fudge))
        if sidemodes['bottom']:
            self.add(FingerJointMid(start=pos+V(width,0), end=pos+V(0,0), side=s, linemode=linemode, startmode=corners['bottom'], endmode=corners['bottom'], tab_length=tab_length, thickness=th['bottom'], cutterrad=cutterrad, prevmode=corners['right'], nextmode=corners['left'], fudge=fudge))
        self.comment("FingerJointBoxMidSide")


class AngledFingerJoint(list):
    """ like a normal finger joint but with longer toungues to take into account the angle"""
    def __init__(self, start, end, side,linemode, startmode, endmode, tab_length, thickness, cutterrad,  angle, lineside='back', fudge=0, material_thickness=False):
#               """  AngledFingerJoint
#start - point the funger joint should start
#end - point the finger joint should end
#side - side the fingers should be cut (left/right)
#linemode - is this an external or internal finger joint (internal is in a hole in a box)
#startmode - should start on or off the line
#endmode - should end on or off the line
#tab_length - a length of tab to aim for - will actually be an integer fraction of the length
#thickness - the thickness of the piece of wood you are slotting into
#cutterrad - radius of the cutter
#angle - angle from vertical that the finger joint is mounted at
#lineside - the side of the piece you are cutting that the line form start to end runs along (front/back)
#fudge - fudge factor which just affects the sides of the fingers not their length"""
    #       self.init({})
        chamfer_width = material_thickness*math.tan(float(angle)/180*math.pi)
    # If this is being cut from the Outside of the shape, the whole joint needs moving by the same amount as the length of the tabs
        if material_thickness is False:
            material_thickness=thickness
        if side=='left':
            perp = rotate((end-start).normalize(),-90)
        else:
            perp = rotate((end-start).normalize(),90)
        if lineside=='front':
            start+=perp*chamfer_width
            end+=perp*chamfer_width
#                       start+=perp*material_thickness*math.sin(float(angle)/180*math.pi)
#                       end+=perp*material_thickness*math.sin(float(angle)/180*math.pi)
    #       for p in FingerJoint(start, end, side,linemode, startmode, endmode, tab_length, thickness*math.tan(float(angle)/180*math.pi), cutterrad, fudge):
        for p in FingerJoint(start, end, side,linemode, startmode, endmode, tab_length, thickness/math.cos(float(angle)/180*math.pi), cutterrad, fudge):
            self.append(p)

class AngledFingerJointNoSlope(list):
    """ like a normal finger joint but with longer toungues to take into account the angle and cut back to the start of the slope"""
    def __init__(self, start, end, side,linemode, startmode, endmode, tab_length, thickness, cutterrad,  angle, lineside='back', fudge=0, material_thickness=False):
#               """  AngledFingerJoint
#start - point the funger joint should start
#end - point the finger joint should end
#side - side the fingers should be cut (left/right)
#linemode - is this an external or internal finger joint (internal is in a hole in a box)
#startmode - should start on or off the line
#endmode - should end on or off the line
#tab_length - a length of tab to aim for - will actually be an integer fraction of the length
#thickness - the thickness of the piece of wood you are slotting into
#cutterrad - radius of the cutter
#angle - angle from vertical that the finger joint is mounted at
#lineside - the side of the piece you are cutting that the line form start to end runs along (front/back)
#fudge - fudge factor which just affects the sides of the fingers not their length"""
    #       self.init({})
    # If this is being cut from the Outside of the shape, the whole joint needs moving by the same amount as the length of the tabs
        if material_thickness is False:
            material_thickness=thickness
        if side=='left':
            perp = rotate((end-start).normalize(),-90)
        else:
            perp = rotate((end-start).normalize(),90)
        chamfer_width = material_thickness*math.tan(float(angle)/180*math.pi)
        if lineside=='front':
# DODGY
            start += - perp * chamfer_width
            end   += - perp * chamfer_width
#               elif lineside =='back':
#                       start += - perp * chamfer_width
#                        end   += - perp * chamfer_width

        for p in FingerJoint(start, end, side,linemode, startmode, endmode, tab_length, chamfer_width + thickness/math.cos(float(angle)/180*math.pi), cutterrad, fudge):
            self.append(p)



class AngledFingerJointSlope(Pathgroup):
    """ This will cut a load of slopes away from an AngledFingerJoint, the both must be called"""
    def __init__(self, start, end, side,linemode, startmode, endmode, tab_length, thickness, cutterrad, angle, lineside='back', fudge=0, material_thickness=False):
        """  AngledFingerJointSlope
start - point the funger joint should start
end - point the finger joint should end
side - side the fingers should be cut (left/right)
linemode - is this an external or internal finger joint (internal is in a hole in a box)
startmode - should start on or off the line
endmode - should end on or off the line
tab_length - a length of tab to aim for - will actually be an integer fraction of the length
thickness - the thickness of the piece of wood you are slotting into
cutterrad - radius of the cutter
angle - angle from vertical that the finger joint is mounted at
lineside - the side of the piece you are cutting that the line form start to end runs along (front/back)
fudge - fudge factor which just affects the sides of the fingers not their length
"""
        self.init({})
        if material_thickness is False:
            material_thickness=thickness
        max_xstep=cutterrad
        chamfer_width = material_thickness*math.tan(float(angle)/180*math.pi)

        steps=int(math.ceil(chamfer_width/max_xstep))
        xstep=chamfer_width/steps
        zstep=material_thickness/steps

        num_tab_pairs= math.floor((end-start).length()/tab_length/2)
        if startmode==endmode:
            num_tabs = num_tab_pairs*2+1
        else:
            num_tabs = num_tab_pairs*2
        tab_length = (end-start).length()/num_tabs
        if side=='left':
            perp = rotate((end-start).normalize(),-90)
        else:
            perp = rotate((end-start).normalize(),90)
        if lineside=='front' and linemode=='external':
            start += perp * chamfer_width
            end += perp * chamfer_width
#                       start+=perp* (material_thickness*math.sin(float(angle)/180*math.pi))
#                       end+=perp* (material_thickness*math.sin(float(angle)/180*math.pi))
        along=tab_length*(end-start).normalize()
        cra=(end-start).normalize()*(cutterrad+fudge)
        crp=perp*cutterrad
        cutin=perp*thickness
        m = startmode
        if linemode=='external':
            onpointmode='clear'
            offpointmode='sharp'
            self.direction = 'ccw'
        elif linemode=='internal':
            onpointmode='sharp'
            offpointmode='clear'
            cra=-cra
            crp=-crp
            self.direction = 'cw'
            if m=='on':
                m='off'
            elif m=='off':
                m='on'
            start +=  perp * (thickness/math.cos(float(angle)/180*math.pi) + chamfer_width)
            end += perp * (thickness/math.cos(float(angle)/180*math.pi) + chamfer_width)
        for i in range(1,int(num_tabs+1)):
            if m=='on':
                m='off'
                for j in range(0, steps):
#                                       print "xoff="+str((j+1)*xstep)+" zoff="+str(material_thickness-zstep*j)
                    p=Path(closed=False, side='on', z1=-material_thickness+zstep*j)
                    if i==1:
                        p.add_point((start+along*(i-1)-cra-perp*(j+1)*xstep), 'sharp')
                    else:
                        p.add_point((start+along*(i-1)-perp*(j+1)*xstep), 'sharp')
                    if i==num_tabs:
                        p.add_point((start+along*i+cra-perp*(j+1)*xstep), 'sharp')
                    else:
                        p.add_point((start+along*i-perp*(j+1)*xstep), 'sharp')
                    self.add(p)
            else:
                m='on'

class FingerJoint(list):
    def __init__(self, start, end, side,linemode, startmode, endmode, tab_length, thickness, cutterrad, fudge=0, **config):
        """Produce points for a finger joint cut on :param side: of a line from :param start: to :param end:
The line defines the
:param linemode: 'internal' - for a joint that is in a hole in a piece of wood 'external' is a side of a box
:param start: Point to start reference line
:param end: Point to end reference line
:param side: side to cut into wood of the reference line
:param startmode: start 'on' or 'off' the reference line
:param endmode: end 'on' or 'off' the reference line
:param tab_length: approximate tab length
:param thickness: thickness of the material
:param cutterrad: radius of the cutter you are using
:param fudge: a fudge factor that increases the gap along the finger joint when negative - it should be 1/4 of the gap you want\n"""
        if 'lastcorner' in config:
            lastcorner = config['lastcorner']
        else:
            lastcorner = endmode
        if 'nextcorner' in config:
            nextcorner = config['nextcorner']
        else:
            nextcorner = endmode
        num_tab_pairs= math.floor((end-start).length()/tab_length/2)
        if startmode==endmode:
            num_tabs = num_tab_pairs*2+1
        else:
            num_tabs = num_tab_pairs*2
        tab_length = (end-start).length()/num_tabs
        if side=='left':
            perp = rotate((end-start).normalize(),-90)
        else:
            perp = rotate((end-start).normalize(),90)
        along=tab_length*(end-start).normalize()

        cra=(end-start).normalize()*(cutterrad+fudge)
        # don't apply fudge on the first and last points or it can overshoot
        craFirst=(end-start).normalize()*(cutterrad)
        crp=perp*cutterrad
        cutin=perp*thickness
        first=True
        if linemode=='external' or linemode==False:
            if cutterrad==0:
                offpointmode=PInsharp
                onpointmode=PInsharp
            else:
                onpointmode = PClear
                offpointmode = PSharp
        elif linemode=='internal':
            if cutterrad==0:
                offpointmode=PInsharp
                onpointmode=PInsharp
            else:
                onpointmode = PSharp
                offpointmode = PClear
            cra=-cra
            crp=-crp
        else:
            print("NO LINEMODE"+str(linemode))
        if startmode=='on':
            if lastcorner != "on":
                if first:
                    self.append(onpointmode(start+crp-craFirst))
                    first=False
                else:
                    self.append(onpointmode(start+crp-cra))
            self.append(onpointmode(start+crp))#onpointmode))
            m='on'
        elif startmode=='off':
            if lastcorner != "off":
                self.append(offpointmode(start+cutin+crp-cra))
            self.append(onpointmode(start+cutin+crp))#offpointmode))
            m='off'
        elif startmode =='straight':
            m='on'
        else:
            print("wrong start mode"+str(startmode))
        for i in range(1,int(num_tabs)):
            if m=='on':
                self.append(onpointmode(start+along*i-cra+crp))
            #       if(i!=num_tabs):
                self.append(offpointmode(start+along*i+crp-cra+cutin))
                m='off'
            else:
                self.append(offpointmode(start+along*i+crp+cra+cutin))
                self.append(onpointmode(start+along*i+crp+cra))
                m='on'
        if endmode=='on':
            if nextcorner != "on":
                self.append(onpointmode(end+crp+craFirst))
            self.append(onpointmode(end+crp))#onpointmode))
        elif endmode=='off':
            self.append(offpointmode(end+cutin+crp+craFirst))
            if nextcorner != "off":
                self.append(onpointmode(end+cutin+crp))#offpointmode))

class FingerJointBoxSide(Path):
    def __init__(self, pos, width, height, side, corners, sidemodes, tab_length, thickness, cutter,**config):
    #       config['side']='on'
        self.init(config)
        self.closed=True
        if 'fudge' in config:
            fudge=config['fudge']
        else:
            fudge=0
        if 'centred' in config and config['centred'] is True:
            pos-=V(width/2, height/2)
        if side=='in':
            s='left'
            linemode='external'
        else:
            s='left'
            linemode='internal'
        if type(thickness) is not dict:
            thickness={'left':thickness, 'top':thickness, 'right':thickness, 'bottom':thickness}

        c={}
        if 'auto' in config:
            self.side='out'
            cutterrad=0
        else:
            self.side='on'
            cutterrad = milling.tools[cutter]['diameter']/2
        if 'cornertypes' in config:
            cornertypes = config['cornertypes']
        else:
            cornertypes = {}
        cs = [('left','top'), ('top', 'right'), ('right', 'bottom'), ('bottom','left')]
        for cor in cs:
            if(cor in cornertypes):

                cornertypes[(cor[1],cor[0])] = cornertypes[cor]
            elif((cor[1],cor[0]) in cornertypes):
                cornertypes[cor] = cornertypes[(cor[1],cor[0])]
            else:
                cornertypes[cor] = 'sharp'
                cornertypes[(cor[1],cor[0])] ='sharp'


        for k in list(thickness.keys()):
            if k in corners and corners[k]=='on':
                if linemode=='external':
                    c[k] = cutterrad
                else:
                    c[k] = -cutterrad
            else:
                if linemode=='external':
                    c[k] = cutterrad+thickness[k]
                else:
                    c[k] = -cutterrad+thickness[k]

        if 'left' in sidemodes and sidemodes['left']=='straight':
            if cornertypes[('left','top')] == 'sharp':
                self.add_point(pos+V(-c['left'],height+c['top']))
            else:
                self.add_point(pos+V(-c['left'], height+c['top']), cornertypes[('left','top')]['type'], cornertypes[('left','top')]['rad'])
        else:
            #if corners['left']=='off' and corners['bottom']=='off':
#                               self.add_point(pos+V(-thickness['left']-cutterrad, -thickness['bottom']-cutterrad),'sharp')
            if cornertypes[('left','bottom')] == 'sharp':
                pass
#                               self.add_point(pos+V(-c['left'], -c['bottom']))
            else:
                self.add_point(pos+V(-c['left'], -c['bottom']), cornertypes[('left','bottom')]['type'], cornertypes[('left','bottom')]['rad'])
            self.add_points(FingerJoint(start=pos+V(0,0), end=pos+V(0,height), side=s, linemode=linemode, startmode=corners['left'], endmode=corners['left'], tab_length=tab_length, thickness=thickness['left'], cutterrad=cutterrad, fudge=fudge)

)
        if 'top' in sidemodes and sidemodes['top']=='straight':
            if cornertypes[('right','top')] == 'sharp':
                self.add_point(pos+V(width+c['right'],height+c['top']))
            else:
                self.add_point(pos+V(width+c['right'],height+c['top']), cornertypes[('right','top')]['type'], cornertypes[('right','top')]['rad'])
        else:
        #       if corners['left']=='off' and corners['top']=='off':
            if cornertypes[('left','top')] == 'sharp':
                pass
#                               self.add_point(pos+V(-c['left'], height+c['top']),'sharp')
            else:
                self.add_points_intersect(pos+V(-c['left'], height+c['top']), cornertypes[('left','bottom')]['top'], cornertypes[('left','top')]['rad'])
            self.add_points_intersect(FingerJoint(start=pos+V(0,height), end=pos+V(width,height), side=s, linemode=linemode,startmode=corners['top'], endmode=corners['top'], tab_length=tab_length, thickness=thickness['top'], cutterrad=cutterrad, fudge=fudge))


        if 'right' in sidemodes and sidemodes['right']=='straight':
            if cornertypes[('right','bottom')] == 'sharp':
                self.add_point(pos+V(width+c['right'],-c['bottom']))
            else:
                self.add_point(pos+V(width+c['right'],-c['bottom']), cornertypes[('right','bottom')]['type'], cornertypes[('right','bottom')]['rad'])
        else:
            if cornertypes[('right','top')] == 'sharp':
#                       self.add_point(pos+V(width+c['right'], height+c['top']),'sharp')
                pass
            else:
                self.add_point(pos+V(width+c['right'], height+c['top']), cornertypes[('right','top')]['type'], cornertypes[('left','bottom')]['rad'])
        #       if corners['top']=='off' and corners['right']=='off':
            self.add_points_intersect(FingerJoint(start=pos+V(width,height), end=pos+V(width,0), side=s, linemode=linemode, startmode=corners['right'], endmode=corners['right'], tab_length=tab_length, thickness=thickness['right'], cutterrad=cutterrad, fudge=fudge))


        if 'bottom' in sidemodes and sidemodes['bottom']=='straight':
            if cornertypes[('bottom','left')] == 'sharp':
                self.add_point(pos+V(-c['bottom'],-c['left']))
            else:
                self.add_point(pos+V(width+c['right'], height+c['top']), cornertypes[('left','bottom')]['type'], cornertypes[('left','bottom')]['rad'])
        else:
        #       if corners['right']=='off' and corners['bottom']=='off':
            if cornertypes[('bottom','right')] == 'sharp':
                pass
                #self.add_point(pos+V(width+c['right'], -c['bottom']),'sharp')
            else:
                self.add_point(pos+V(width+c['right'], -c['bottom']), cornertypes[('left','bottom')]['type'], cornertypes[('left','bottom')]['rad'])

            self.add_points_intersect(FingerJoint(start=pos+V(width,0), end=pos+V(0,0), side=s, linemode=linemode, startmode=corners['bottom'], endmode=corners['bottom'], tab_length=tab_length, thickness=thickness['bottom'], cutterrad=cutterrad, fudge=fudge))
        self.close_intersect()
        self.comment("FingerJointBoxSide")
#               self.simplify_points()



class BracketJoint(ButtJoint):
    def p(self):
        pass
# probably doesn't work with non-mirror symmetric hole patterns, am using rotation rather than mirror
class BracketJointHoles(Pathgroup):
    def __init__(self, start, end, side,linemode, startmode, endmode, hole_spacing, thickness, cutterrad, prevmode, nextmode, **config):
#(self, start, end, side,linemode, startmode, endmode, tab_length, thickness, cutterrad, **config):
        self.init(config)
        if 'bracket' in config:
            bracket = config['bracket']
        if 'args' in config:
            args = config['args']

        if 'joint_type' in config:
            joint_type=config['joint_type']
        else:
            joint_type='convex'
      #          if side=='left':
       #                 perp = rotate((end-start).normalize(),-90)
    #        else:
         #               perp = rotate((end-start).normalize(),90)
        if 'butt_num_holes' in config and type(config['butt_num_holes']) is not None:
            num_holes = config['butt_num_holes']
        else:
            num_holes = int(math.ceil((end-start).length()/hole_spacing))
        if 'hole_offset' in config and config['hole_offset'] is not None:
            hole_offset = config['hole_offset']
        else:
            hole_offset = 0
        if 'wood_direction' in config:
            wood_dir = config['wood_direction']
        else:
            wood_dir = 1
        if num_holes>0:
            hole_length = (end-start).length()/num_holes
        else:
            hole_length = 1
        parallel=(end-start).normalize( )
        holes=True
        l = end - start
        dl = l/(num_holes-1)
        angle = math.atan2(l[1], l[0])/math.pi*180.0
        if wood_dir<0 and side=="left":
            angle+=180
#                       angle=-angle
#               else:
        angle=-angle
        args['mode']=startmode
        args['side']=side
        if(side=='left'):
            perp = rotate(parallel, -90)
        else:
            perp = rotate(parallel, 90)
        for i in range(0, num_holes-1):
            t=self.add( bracket(start+dl*(0.5+i), along=parallel, perp=perp, **args))
    #                       t.transform={'mirror':[V(0,0),'x']}
            t.rotate(V(0,0), angle)


class KeyHoleArc(Path):
    def __init__(self, pos, rad, keyHoleRad, width, angle,  **config):
        """ An arc of length angle with width - width """
        self.init(config)
        if 'startangle' in config:
            startangle = config['startangle']
        else:
            startangle = 0

        self.closed=True
        a1 = -float(angle)/2+startangle
        a2 = float(angle)/2+startangle
        w = float(width)/2

        keyOff = math.sqrt(keyHoleRad**2 - w**2)

        self.add_point(PSharp(pos+V(0,rad+w), transform={'rotate':[pos, a1]}))
        self.add_point(PArc(pos+V(0,0), radius=rad+w, direction='cw'))
        self.add_point(PSharp(pos+V(0,rad+w), transform={'rotate':[pos, a2]}))
        self.add_point(PArc(pos+V(0,rad), radius=w, direction='cw', transform={'rotate':[pos, a2]}))
        self.add_point(PSharp(pos+V(0,rad-w), transform={'rotate':[pos, a2]}))
        self.add_point(PArc(pos+V(0,0), radius=rad-w, direction='ccw'))
        self.add_point(PSharp(pos+V(0,rad-w), transform={'rotate':[pos, a1]}))
        self.add_point(PArc(pos+V(-keyOff,rad), radius=keyHoleRad, direction='cw', transform={'rotate':[pos, a1]}))


class Arrow(Path):
    def __init__(self, pos, length, width, headwidth, headlength,  **config):
        """ An arc of length angle with width - width with arrow head on the end """
        self.init(config)
        self.closed=True
        self.add_point(PSharp(pos+V(0,length/2)))
        self.add_point(PSharp(pos+V( headwidth/2,length/2-headlength)))
        self.add_point(PSharp(pos+V( width/2,length/2-headlength)))
        self.add_point(PSharp(pos+V( width/2,-length/2)))
        self.add_point(PSharp(pos+V(-width/2,-length/2)))
        self.add_point(PSharp(pos+V(-width/2,length/2-headlength)))
        self.add_point(PSharp(pos+V(-headwidth/2,length/2-headlength)))

class RoundedArrow(Path):
    def __init__(self, pos, rad, width, headwidth, headlength, angle,  **config):
        """ An arc of length angle with width - width with arrow head on the end """
        self.init(config)
        if 'startangle' in config:
            startangle = config['startangle']
        else:
            startangle = 0
        
        self.closed=True
        a1 = -float(angle)/2+startangle
        a2 = float(angle)/2+startangle
        w = float(width)/2
        headw = headwidth/2
        ahead = headlength/(math.pi*2*rad)*360
        print("headlength="+str(headlength)+"ahead="+str(ahead))
        heads = [True, True]
        if 'heads' in config:
                if config['heads'] == 'cw':
                        heads[0]=False
                elif config['heads'] == 'ccw':
                        heads[1]=False
                elif config['heads'] =='none':
                        heads=[False, False]
        if width==0:
                self.closed=False
                self.side='on'
                if(heads[0]):
                        self.add_point(PSharp(pos+V(0,rad), transform={'rotate':[pos, a1]}))
                        self.add_point(PSharp(pos+V(0,rad)+rotate(V(headlength,-headw),ahead/2), transform={'rotate':[pos, a1]}))
                        self.add_point(PSharp(pos+V(0,rad), transform={'rotate':[pos, a1]}))
                        self.add_point(PSharp(pos+V(0,rad)+rotate(V(headlength,headw),ahead/2), transform={'rotate':[pos, a1]}))
                self.add_point(PSharp(pos+rotate(V(0,rad),a1)))
                self.add_point(PArc(pos+V(0,0), radius=rad+w, direction='cw'))
                self.add_point(PSharp(pos+rotate(V(0,rad), a2)))
                if(heads[1]):
                        #self.add_point(PSharp(pos+rotate(V(-headlength,rad-headw), a2)))
                        self.add_point(PSharp(pos+V(0,rad)+rotate(V(-headlength,-headw),-ahead/2), transform={'rotate':[pos, a2]}))
                        self.add_point(PSharp(pos+V(0,rad), transform={'rotate':[pos, a2]}))
                        self.add_point(PSharp(pos+V(0,rad)+rotate(V(-headlength,headw),-ahead/2), transform={'rotate':[pos, a2]}))
                        #self.add_point(PSharp(pos+rotate(V(-headlength,rad+headw), a2)))
                        self.add_point(PSharp(pos+V(0,rad), transform={'rotate':[pos, a2]}))
                for p in self.points:
                        print ("qqq"+str(p)+str(p.pos))
        else:
                self.add_point(PSharp(pos+V(0,rad+w), transform={'rotate':[pos, a1]}))
                self.add_point(PArc(pos+V(0,0), radius=rad+w, direction='cw'))
                self.add_point(PSharp(pos+V(0,rad+w), transform={'rotate':[pos, a2]}))
                if(heads[1]):
                        self.add_point(PSharp(pos+V(0,rad+headw), transform={'rotate':[pos, a2]}))
                        self.add_point(PSharp(pos+V(headlength,rad), transform={'rotate':[pos, a2]}))
                        self.add_point(PSharp(pos+V(0,rad-headw), transform={'rotate':[pos, a2]}))
             
                self.add_point(PSharp(pos+V(0,rad-w), transform={'rotate':[pos, a2]}))
                self.add_point(PArc(pos+V(0,0), radius=rad-w, direction='ccw'))
                self.add_point(PSharp(pos+V(0,rad-w), transform={'rotate':[pos, a1]}))
                if(heads[0]):
                        self.add_point(PSharp(pos+V(0,rad-headw), transform={'rotate':[pos, a1]}))
                        self.add_point(PSharp(pos+V(-headlength,rad), transform={'rotate':[pos, a1]}))
                        self.add_point(PSharp(pos+V(0,rad+headw), transform={'rotate':[pos, a1]}))
        
class RoundedArc(Path):
    def __init__(self, pos, rad, width, angle,  **config):
        """ An arc of length angle with width - width """
        self.init(config)
        if 'startangle' in config:
            startangle = config['startangle']
        else:
            startangle = 0

        self.closed=True
        a1 = -float(angle)/2+startangle
        a2 = float(angle)/2+startangle
        w = float(width)/2
        self.add_point(PSharp(pos+V(0,rad+w), transform={'rotate':[pos, a1]}))
        self.add_point(PArc(pos+V(0,0), radius=rad+w, direction='cw'))
        self.add_point(PSharp(pos+V(0,rad+w), transform={'rotate':[pos, a2]}))
        self.add_point(PArc(pos+V(0,rad), radius=w, direction='cw', transform={'rotate':[pos, a2]}))
        self.add_point(PSharp(pos+V(0,rad-w), transform={'rotate':[pos, a2]}))
        self.add_point(PArc(pos+V(0,0), radius=rad-w, direction='ccw'))
        self.add_point(PSharp(pos+V(0,rad-w), transform={'rotate':[pos, a1]}))
        self.add_point(PArc(pos+V(0,rad), radius=w, direction='cw', transform={'rotate':[pos, a1]}))

class ArcRect(Path):
    def __init__(self, pos, rad, width, minorrad, angle,  **config):
        """ A curved rounded rect with length angle around rad and a minorrad around the corners"""
        self.init(config)
        if 'startangle' in config:
            startangle = config['startangle']
        else:
            startangle = 0

        self.closed=True
        a1 = -float(angle)/2+startangle
        a2 = float(angle)/2+startangle
        w = float(width)/2
        print("minorrad "+str(minorrad))
        if not minorrad:
            pass
        if not type(minorrad) is list:
            minorrad=[minorrad, minorrad, minorrad, minorrad]
        elif len(minorrad)<4:
            print("if minorrad is a list it should have 4 values")
        self.add_point(PSharp(pos+V(0,rad+w), transform={'rotate':[pos, a1]}))
        self.add_point(PArc(pos+V(0,0), radius=rad+w, direction='cw'))
        self.add_point(PSharp(pos+V(0,rad+w), transform={'rotate':[pos, a2]}))
        if(minorrad and minorrad != [0, 0, 0, 0]):
            self.add_point(PIncurve(pos+V(minorrad[0], rad+w), radius=minorrad[0], transform={'rotate':[pos, a2]}))
            self.add_point(PSharp(pos+V(minorrad[0], rad+w-minorrad[0]), transform={'rotate':[pos, a2]}))
            self.add_point(PSharp(pos+V(minorrad[1], rad-w+minorrad[1]), transform={'rotate':[pos, a2]}))
            self.add_point(PIncurve(pos+V(minorrad[1], rad-w), radius=minorrad[1], transform={'rotate':[pos, a2]}))

        self.add_point(PSharp(pos+V(0,rad-w), transform={'rotate':[pos, a2]}))
        self.add_point(PArc(pos+V(0,0), radius=rad-w, direction='ccw'))
        self.add_point(PSharp(pos+V(0,rad-w), transform={'rotate':[pos, a1]}))
        if(minorrad):
            self.add_point(PIncurve(pos+V(-minorrad[2],rad-w), radius=minorrad[2], transform={'rotate':[pos, a1]}))
            self.add_point(PSharp(pos+V(-minorrad[2], rad-w+minorrad[2]), transform={'rotate':[pos, a1]}))
            self.add_point(PSharp(pos+V(-minorrad[3], rad+w-minorrad[3]), transform={'rotate':[pos, a1]}))
            self.add_point(PIncurve(pos+V(-minorrad[3], rad+w), radius=minorrad[3], transform={'rotate':[pos, a1]}))
     #   self.add_point(PSharp(pos+V(0, rad+w), transform={'rotate':[pos, a1]}))

# The bit you cut out to make a spoke
class AntiSpoke(Path):
    def __init__(self, pos, outerrad, innerrad, spokewidth, minorrad, angle,  **config):
        """ A curved rounded rect with length angle around rad and a minorrad around the corners"""
        self.init(config)
        if 'startangle' in config:
            startangle = config['startangle']
        else:
            startangle = 0
        if 'spokewidth2' in config:
            spokewidth2 = config['spokewidth2']
        else:
            spokewidth2 = spokewidth
        self.closed=True
        minorrad_in_angle = minorrad/(2*math.pi*innerrad)*360
        minorrad_out_angle = minorrad/(2*math.pi*outerrad)*360
        iedgeangle1 = (spokewidth/2+minorrad) /(math.pi *2 *innerrad) * 360
        oedgeangle1 = (spokewidth/2+minorrad) /(math.pi *2 *outerrad) * 360
        iedgeangle2 = (spokewidth2/2+minorrad) /(math.pi *2 *innerrad) * 360
        oedgeangle2 = (spokewidth2/2+minorrad) /(math.pi *2 *outerrad) * 360
        ia1 = -float(angle)/2+startangle+iedgeangle1
        ia2 = float(angle)/2+startangle-iedgeangle2
        oa1 = -float(angle)/2+startangle+oedgeangle1
        oa2 = float(angle)/2+startangle-oedgeangle2
        self.add_point(PSharp(pos+V(0,outerrad), transform={'rotate':[pos, oa1]}))
        self.add_point(PArc(pos+V(0,0), radius=outerrad, direction='cw'))
        self.add_point(PSharp(pos+V(0,outerrad), transform={'rotate':[pos, oa2]}))
        if(minorrad):
            self.add_point(PIncurve(pos+V(minorrad, outerrad), radius=minorrad, transform={'rotate':[pos, oa2]}))
      #                  self.add_point(PSharp(pos+V(minorrad, outerrad-minorrad), transform={'rotate':[pos, oa2]}))
       #                 self.add_point(PSharp(pos+V(minorrad, innerrad+minorrad), transform={'rotate':[pos, ia2]}))
            self.add_point(PIncurve(pos+V(minorrad, innerrad), radius=minorrad, transform={'rotate':[pos, ia2]}))

        self.add_point(PSharp(pos+V(0,innerrad), transform={'rotate':[pos, ia2]}))
        self.add_point(PArc(pos+V(0,0), radius=innerrad, direction='ccw'))
        self.add_point(PSharp(pos+V(0,innerrad), transform={'rotate':[pos, ia1]}))
        if(minorrad):
            self.add_point(PIncurve(pos+V(-minorrad,innerrad), radius=minorrad, transform={'rotate':[pos, ia1]}))
    #                self.add_point(PSharp(pos+V(-minorrad, innerrad+minorrad), transform={'rotate':[pos, ia1]}))
         #               self.add_point(PSharp(pos+V(-minorrad, outerrad-minorrad), transform={'rotate':[pos, oa1]}))
            self.add_point(PIncurve(pos+V(-minorrad, outerrad), radius=minorrad, transform={'rotate':[pos, oa1]}))
        self.add_point(PSharp(pos+V(0, outerrad), transform={'rotate':[pos, oa1]}))

class RoundedCorner(Path):
    def __init__(self, pos, dir1, len1, dir2, len2, endrad, **config):
        self.init(config)
        print("Rounded Corner")
        print(config)
        print(self.side)
        assert type(dir1) is Vec
        assert type(dir2) is Vec
        if 'innerrad' in config and 'outerrad' in config:
            width = config['outerrad'] - config['innerrad']
        elif 'width' in config:
            width = config['width']
            if 'innerrad' in config:
                outerrad = config['innerrad'] + width
            elif 'outerrad' in config:
                outerrad = config['outerrad']
        else:
            raise ValueError("Must have two of innerrad, outerrad and width defined")
        if 'from_inside' in config and config['from_inside']:
            pos += dir1*-width + dir2*-width
            len1+=width
            len2+=width
        dir1 = dir1.normalize()
        dir2 = dir2.normalize()
        self.closed=True
        self.add_point(PIncurve(pos+ dir2*len1, radius=endrad))
        self.add_point(PIncurve(pos+ dir2*len1 + dir1*width, radius=endrad))
        self.add_point(PIncurve(pos+ dir1*width + dir2*width, radius=outerrad - width))
        self.add_point(PIncurve(pos+ dir1*len1 + dir2*width, radius=endrad))
        self.add_point(PIncurve(pos+ dir1*len1, radius=endrad))
        self.add_point(PIncurve(pos, radius=outerrad))



class RectAlong(Path):
    def __init__(self, start, end, width, rad, **config):
        self.init(config)

        para = (end-start).normalize()
        perp = rotate(para, 90)
        w=width/2
        self.closed=True
        self.add_point(PIncurve(start+perp*w-para*rad, radius=rad))
        self.add_point(start+perp*w)
        self.add_point(end+perp*w)
        self.add_point(PIncurve(end+perp*w+para*rad, radius=rad))
        self.add_point(PIncurve(end-perp*w+para*rad, radius=rad))
        self.add_point(end-perp*w)
        self.add_point(start-perp*w)
        self.add_point(PIncurve(start-perp*w-para*rad, radius=rad))

class ParametricFunctionAlongPath(list):
    def __init__(self, pathFunc, paramFunc, pstart, pend, **config):
        if 'step' in config:
            step=config['step']
        else:
            step = (float(pend)-float(pstart))/100
        p = pstart
        while p<pend:
            along = (pathFunc(p+step/4)-pathFunc(p-step/4)).normalize()
            perp = rotate(along, 90)
            if pathFunc(p) is not None and paramFunc(p) is not None:
                self.append( PSharp(pathFunc(p) + perp * paramFunc(p) ))
            p+=step 
        p = pend
        along = (pathFunc(p+step/4)-pathFunc(p-step/4)).normalize()
        perp = rotate(along, 90)
        if pathFunc(p) is not None and paramFunc(p) is not None:
            self.append( PSharp(pathFunc(p) + perp * paramFunc(p) ))


class ParametricFunction(list):
    def __init__(self, pos, pstart, pend, func, **config):
        if 'step' in config:
            step=config['step']
        else:
            step = (float(pend)-float(pstart))/100
        p = pstart
        while p<pend:
            self.append(PSharp(pos+func(p)))
            p+=step
        self.append(PSharp(pos+func(pend)))
class RadialParametricFunction(list):
    def __init__(self, pos, func, **config):
        if 'pstart' in config:
            pstart= config['pstart']
        else:
            pstart=0
        if 'pend' in config:
            pend=config['pend']
        else:
            pend=360

        if 'step' in config:
            step=config['step']
        else:
            step = (float(pend)-float(pstart))/100
        p = pstart
        while p<pend:
            r=func(p)
            self.append(V(math.sin(float(p)/180*math.pi)*r, math.cos(float(p)/180*math.pi)*r))
            p+=step
        self.append(func(pend))


class CutFunction(list):
    def __init__(self, start, end, func, **config):
        return self.cut_function(start, end, func, config)

    def cut_function(self, start, end, func, config):
        length = (end-start).length()
        para = (end-start).normalize()
        perp = rotate(para, 90)

        if 'step' in config:
            step = config['step']
            del(config['step'])
        else:
            step = 4

        if 'skew' in config:
            skew = config['skew']
            del(config['skew'])
        else:
            skew = 0
        x=0
        while x<length:
            y = func(x, **config)
            self.append( PSharp(start+ (x+y*skew) *para + y*perp))
            x+=step
        y = func(length, **config)
        self.append(PSharp(start+ (length+y*skew) *para + y*perp))




class SineWave(CutFunction):
    def __init__(self, start, end, **config):
        args={}
        length = (end-start).length()
        para = (end-start).normalize()
        perp = rotate(para, 90)
        if 'amplitude' in config:
            args['amplitude'] = float(config['amplitude'])
        else:
            args['amplitude'] = 10.0
        if 'cycles' in config:
            args['k']= 2*math.pi*float(config['cycles'])/length
        elif 'wavelength' in config:
            args['k']= 2*math.pi/config['wavelength']
        elif 'k' in config:
            args['k'] = config['k']
        if 'phase' in config:
            args['phase'] = float(config['phase'])
        else:
            args['phase'] = 0
        if 'step' in config:
            args['step'] = float(config['step'])
        if 'skew' in config:
            args['skew'] = float(config['skew'])

        return self.cut_function(start, end, self.sine, args)

    def sine(self, x, amplitude, k, phase):
        return amplitude * math.sin(x*k+phase)

class RepeatWave(list):
    def __init__(self, start, end, points, **config):
        self.cut_wave(start, end, points, config)

    def cut_wave(self, start, end, points, config):
        length = (end-start).length()
        if 'wavelength' in config:
            wavelength = float(config['wavelength'])
            cycles = float(length) / wavelength
        elif 'cycles' in config:
            cycles = float(config['cycles'])
            wavelength = length/cycles
        if 'amplitude' in config:
            amplitude = float(config['amplitude'])
        else:
            amplitude = 10.0
        if 'skew' in config:
            skew = float(config['skew'])
        else:
            skew = 0.0
        if 'point_type' in config:
            point_type = config['point_type']
        else:
            point_type = PSharp
        if 'point_args' in config:
            point_args = config['point_args']
        else:
            point_args = {}
        if 'start_offset' in config:
            start_offset = float(config['start_offset'])
        else:
            start_offset = 0.0

        para = (end-start).normalize()
        perp = rotate(para, 90) * amplitude
        para *= wavelength
        print("start="+str(start)+" end="+str(end))
        for i in range(0,int(math.ceil(cycles))):
            print("cycles="+str(cycles-i)+" i"+str(i))
            for p in points:
                if (cycles-i>1 or p[0]-start_offset<cycles-i) and (start_offset-i<=0 or start_offset<p[0]):
                    print("p[0]="+str(p[0])+" offset="+str(cycles-i)+str(start + i * para + para* (float(p[0]-start_offset) + skew * float(p[1])) + perp * float(p[1])))
                #self.append( PSharp(  start + i * para + para* (float(p[0]) + skew * float(p[1])) + perp * float(p[1])))
                    self.append( point_type(  start + i * para + para* (float(p[0]-start_offset) + skew * float(p[1])) + perp * float(p[1]), **point_args))


class SquareWave(RepeatWave):
    def __init__(self, start, end, **config):
        args={}
        length = (end-start).length()
        if 'amplitude' in config:
            args['amplitude'] = float(config['amplitude'])
        else:
            args['amplitude'] = 10.0
        if 'offset' in config:
            args['offset']=config['offset']
        else:
            args['offset']=0
        if 'skew' in config:
            args['skew'] = config['skew']

        if 'cycles' in config:
            args['wavelength'] = length/config['cycles']
            args['cycles'] = config['cycles']
        else:
            args['wavelength'] = config['wavelength']
            args['cycles'] = int(length/config['wavelength'])
        return self.cut_wave(start, end, [V(0, 0), V(0, 1), V(0.5, 1), V(0.5, 0), V(0.5, -1), V(1, -1), V(1, 0)], args)


class TriangleWave(RepeatWave):
    def __init__(self, start, end, **config):
        args={}
        length = (end-start).length()
        if 'amplitude' in config:
            args['amplitude'] = float(config['amplitude'])
        else:
            args['amplitude'] = 10.0
        if 'offset' in config:
            args['offset']=config['offset']
        else:
            args['offset']=0
        if 'skew' in config:
            args['skew'] = config['skew']

        if 'cycles' in config:
            args['wavelength'] = length/config['cycles']
            args['cycles'] = config['cycles']
        else:
            args['wavelength'] = config['wavelength']
            args['cycles'] = int(length/config['wavelength'])
        return self.cut_wave(start, end, [V(0, 0), V(0.25, 1),  V(0.5, 0), V(0.75, -1), V(1, 0)], args)



class Clamp(Path):
    def __init__(self, pos, inner_rad, outer_rad, **config):
        self.init(config)
        self.translate(pos)
        if 'bolt_length' in config:
            bolt_length = config['bolt_length']
        else:
            bolt_length = outer_rad - inner_rad

        if 'bolt_width' in config:
            bolt_width = config['bolt_width']
        else:
            bolt_width = bolt_length

        if 'hold_length' in config:
            hold_length = config['hold_length']
        else:
            hold_length = inner_rad

        if 'hold_width' in config:
            hold_width = config['hold_width']
        else:
            hold_width = (outer_rad - inner_rad)*2
        gap=4


        bolt_out_x = math.sqrt(outer_rad*outer_rad-bolt_length*bolt_length)
        hold_out_x = -math.sqrt(outer_rad*outer_rad-hold_length*hold_length)
        self.closed=True
        self.side='out'
        self.add_point(V(-inner_rad-hold_width, hold_length))
        self.add_point(V(hold_out_x, hold_length))
        self.add_point(PArc(V(0,0), radius=outer_rad, direction='cw'))
        self.add_point(V(bolt_out_x, bolt_length))
        self.add_point(V(outer_rad+bolt_width, bolt_length))
        self.add_point(V(outer_rad+bolt_width, gap/2))
        self.add_point(V(inner_rad, gap/2))
        self.add_point(PArc(V(0,0), radius=inner_rad))
        self.add_point(V(-inner_rad, gap/2))
        self.add_point(PArc(V(0,0), radius=inner_rad))
        self.add_point(V(inner_rad, -gap/2))
        self.add_point(V(outer_rad+bolt_width, -gap/2))
        self.add_point(V(outer_rad+bolt_width, -bolt_length))
        self.add_point(V(bolt_out_x, -bolt_length))
        self.add_point(PArc(V(0,0), radius=outer_rad, direction='cw'))
        self.add_point(V(hold_out_x, -hold_length))
        self.add_point(V(-inner_rad-hold_width, -hold_length))

class ClockHand(Path):
    def __init__(self, pos, length, width, rad, **config):
        self.init(config)
        self.translate(pos)
        w=width/2
        if 'pointlen' in config:
            pointlen = config['pointlen']
        else:
            pointlen = 2*w
        if 'cornerrad' in config:
            cornerrad = config['cornerrad']
        else:
            cornerrad = 1.0
        self.closed=True
        self.add_point(PIncurve(V(-w,rad*1.2), radius=2*cornerrad))
        self.add_point(PIncurve(V(-w,length-pointlen), radius=cornerrad))
        self.add_point(PIncurve(V(0,length), radius=cornerrad))
        self.add_point(PIncurve(V(w,length-pointlen), radius=cornerrad))
        self.add_point(PIncurve(V(w,rad*1.2), radius=2*cornerrad))
        self.add_point(POutcurve(V(0,0), radius=rad))


class Module(Plane):
    def __init__(self, size,  **config):#holesX=False, holesY=False, fromedge=15, fromends=40):
        """Create a module
:param size: A1, A2, A3
:param fromedge: distance holdowns should be from edge of board
:param orientation: portrait, landscape
:param fromends: distance holdowns from ends
:param holesY: number of holes in Y direction
:param holesX: number of holes in X direction
:param base_thicknesss: thickenss of base layer
:param insert_type:  the type of insert - default screw in, or hammer
:param no_perspex: if rue don't create perspex layer
:param no_holdowns: if True no holdowns
"""
        self.init('module',V(0,0),V(0,0),config)
        self.bom=[]
        bolt_config={}
        if('fromends' in config):
            fromends=config['fromemds']
        else:
            fromends=40
        if('fromedge' in config):
            fromedge=config['fromedge']
        else:
            fromedge=16
        if('holesY' in config):
            holesY=config['holesY']
        else:
            holesY=False
        if('holesX' in config):
            holesX=config['holesX']
        else:
            holesX=False
        if 'base_thickness' in config:
            base_thickness=config['base_thickness']
        else:
            base_thickness=12
        if 'underbase_thickness' in config:
            underbase_thickness = config['underbase_thickness']
        else:
            underbase_thickness = base_thickness
        if 'perspex_thickness' in config:
            perspex_thickness=config['perspex_thickness']
            if perspex_thickness>3:
                bolt_config['length']=16
        else:
            perspex_thickness=3
        if 'insert_type' in config:
            bolt_config['insert_type']=config['insert_type']
        if 'cornerHoleLayers' in config:
            cornerHoleLayers = config['cornerHoleLayers']
        else:
            cornerHoleLayers = ['base', 'underbase','perspex','paper']

        #name, material, thickness, z0=0,zoffset=0
        self.perspex_layer=self.add_layer('perspex',material='perspex',thickness=perspex_thickness,z0=0,zoffset=3)
        self.base_layer=self.add_layer('base',material='plywood', thickness=base_thickness, z0=0,zoffset=0, add_back=True)
        self.underbase_layer=self.add_layer('underbase',material='plywood', thickness=underbase_thickness, z0=0,zoffset=-base_thickness, add_back=True)
        self.pibarn_layer=self.add_layer('pibarn',material='perspex', thickness=6, z0=0,zoffset=30, add_back=False)
        self.add_layer('paper',material='paper',thickness=0.05,z0=0,zoffset=0.05)
        radius=30
        if 'orientation' in config and config['orientation'] in ['landscape', 'portrait']:
            orientation=config['orientation']
        else:
            orientation='landscape'
        if size=='A4':
            width=297
            height=210
            if holesX==False:
                holesX=3
            if holesY==False:
                holesY=2
            self.backgap=0
        elif size=='A3':
            width=420
            height=297
            if holesX==False:
                holesX=4
            if holesY==False:
                holesY=3
            self.backgap=0
        elif size=='A2':
            width=594
            height=420
            if holesX==False:
                holesX=4
            if holesY==False:
                holesY=3
            self.backgap = 40
        elif size=='A1':
            width=841
            height=594
            if holesX==False:
                holesX=4
            if holesY==False:
                holesY=4
            self.backgap =0

        if orientation!='landscape':
            width,height = height,width
            holesX, holesY = holesY, holesX
        self.width = width
        self.height = height

        edge= RoundedRect(bl=V(0,0), tr=V(width, height), rad=radius, side='out')
        if not ('no_perspex' in config and not config['no_perspex']):
            self.perspex = self.add(Part(name='perspex', border=edge, layer='perspex',colour="red"))
        self.base = self.add(Part(name='base', border=edge, layer='base'))
        self.paper = self.add(Part(name='paper', border=edge, layer='paper'))
        if 'twolayer' in config and config['twolayer']:
            self.underbase = self.add(Part(name='underbase', border=edge, layer='underbase'))



        if size=='A1':
            if orientation=='landscape':
                self.add(Hole(V(width/2,radius),rad=13/2,side='in'),cornerHoleLayers)
                self.add(Hole(V(width/2,height-radius),rad=13/2,side='in'),cornerHoleLayers)
            else:
                self.add(Hole(V(radius,height/2),rad=13/2,side='in'),cornerHoleLayers)
                self.add(Hole(V(width-radius,height/2),rad=13/2,side='in'),cornerHoleLayers)

        self.add(Hole(V(radius,radius),rad=13/2,side='in'),cornerHoleLayers)
        if not ('no_holdown' in config and  config['no_holdown']):
            self.add(RepeatLine(V(fromends, fromedge), V(width-fromends,fromedge), holesX, Bolt, bolt_config,layers=['base', 'underbase','perspex','paper','top'])
)
        self.add(Hole(V(width-radius,radius),rad=13/2,side='in'),cornerHoleLayers)
        if not ('no_holdown' in config and  config['no_holdown']):
            self.add(RepeatLine(V(width-fromedge, fromends), V(width-fromedge,height-fromends), holesY, Bolt, bolt_config,layers=['base', 'underbase','perspex','paper','top']))

        self.add(Hole(V(width-radius,height-radius),rad=13/2,side='in'),cornerHoleLayers)
        if not ('no_holdown' in config and  config['no_holdown']):
            self.add(RepeatLine(V(width-fromends, height-fromedge), V(fromends,height-fromedge), holesX, Bolt, bolt_config,layers=['base', 'underbase','perspex','paper','top']))
        self.add(Hole(V(radius,height-radius),rad=13/2,side='in'),cornerHoleLayers)

        if not ('no_holdown' in config and  config['no_holdown']):
            self.add(RepeatLine(V(fromedge, height-fromends), V(fromedge,fromends), holesY, Bolt,bolt_config,layers=['base', 'underbase','perspex','paper','top']))


class ModuleClearBack(Part):
    def __init__(self, size, layer, **config):
        self.init(config)
        self.add_border(ModuleClearBackPath(size))
        b=self.border
        self.layer=layer
        if 'fromedge' in config:
            fromedge=b.side+config['fromedge']
        else:
            fromedge=b.side+15
        if 'fromends' in config:
            fromends=b.corner+config['fromends']
        else:
            fromends=b.corner+25
        fend=25
        if size=='A3':
            holesX=4
            holesY=3
        elif size=='A2':
            holesX=4
            holesY=3
        elif size=='A1':
            holesX=4
            holesY=4
        if 'screw_config' in config:
            screw_config=config['screw_config']
            self.add(RepeatLine(V(fromends, fromedge), V(b.width-fromends,fromedge), holesX, Screw, screw_config))
            self.add(RepeatLine(V(b.width-fromedge, fromends), V(b.width-fromedge,b.height-fromends), holesY, Screw, screw_config))
            self.add(RepeatLine(V(b.width-fromends, b.height-fromedge), V(fromends,b.height-fromedge), holesX, Screw, screw_config))
            self.add(RepeatLine(V(fromedge, b.height-fromends), V(fromedge,fromends), holesY, Screw,screw_config))
        if 'bolt_config' in config:
            bolt_config=config['bolt_config']
            self.add(RepeatLine(V(fromends, fromedge), V(b.width-fromends,fromedge), holesX, Bolt, bolt_config))
            self.add(RepeatLine(V(b.width-fromedge, fromends), V(b.width-fromedge,b.height-fromends), holesY, Bolt, bolt_config))
            self.add(RepeatLine(V(b.width-fromends, b.height-fromedge), V(fromends,b.height-fromedge), holesX, Bolt, bolt_config))
            self.add(RepeatLine(V(fromedge, b.height-fromends), V(fromedge,fromends), holesY, Bolt,bolt_config))

class ModuleClearBackPath(Path):
    def __init__(self,size,**config):

        self.init(config)
        if 'side' not in config:
            self.side='out'
        self.closed=True

        self.side=17
        self.corner=51+self.side
        self.mid_height=120/2
        self.mid_width=39+self.side
        self.mid_edge=9
        self.mid_mid=60/2
        if size=='A3':
            self.self.width=420
            self.height=297
        elif size=='A2':
            self.width=594
            self.height=420
        elif size=='A1':
            self.width=841
            self.height=594
        self.add_point(V(self.side,self.corner))
        self.add_point(V(self.corner,self.side))
        self.add_point(V(self.width-self.corner,self.side))
        self.add_point(V(self.width-self.side,self.corner))
        if(size=='A1'):
            self.add_point(V(self.width-self.side,self.height/2-self.mid_height))
            self.add_point(V(self.width-self.side-self.mid_edge,self.height/2-self.mid_height))
            self.add_point(V(self.width-mid_self.width,self.height/2-mid_mid))
            self.add_point(V(self.width-mid_self.width,self.height/2+mid_mid))
            self.add_point(V(self.width-self.side-self.mid_edge,self.height/2+self.mid_height))
            self.add_point(V(self.width-self.side,self.height/2+self.mid_height))
        self.add_point(V(self.width-self.side,self.height-self.corner))
        self.add_point(V(self.width-self.corner,self.height-self.side))
        self.add_point(V(self.corner,self.height-self.side))
        self.add_point(V(self.side,self.height-self.corner))
        if(size=='A1'):
            self.add_point(V(self.side,self.height/2+self.mid_height))
            self.add_point(V(self.side-self.mid_edge,self.height/2+self.mid_height))
            self.add_point(V(mid_self.width,self.height/2+mid_mid))
            self.add_point(V(mid_self.width,self.height/2-mid_mid))
            self.add_point(V(self.side-self.mid_edge,self.height/2-self.mid_height))
            self.add_point(V(self.side,self.height/2-self.mid_height))
