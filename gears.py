import math

from path import *
from  shapes import *
# =================================================================================
# =================================================================================
# Spur-gear generation script
# (c) James Gregson, 2012
# Free for all use, including commercial, but do not redistribute. 
# Use at your own risk.
#
# Notes:
#  - seems to work well for pressure angles up to about 30 degrees
# =================================================================================
# =================================================================================


class InvoluteGearBorder(Path):
        # compute the root diameter of a gear with a given pressure-angle (pa)
        # number of teeth (N), and pitch (P)
        def gears_root_diameter( self, pa, N, P ):
            return (N-2.5)/P

        # compute the base diameter of a gear with a given pressure-angle (pa)
        # number of teeth (N), and pitch (P)
        def gears_base_diameter( self, pa, N, P ):
            return self.gears_pitch_diameter( pa, N, P )*math.cos( pa*math.pi/180.0 )

        # compute the outer diameter of a gear with a given pressure-angle (pa)
        # number of teeth (N), and pitch (P)
        def gears_outer_diameter( self, pa, N, P ):
            return self.gears_pitch_diameter( pa, N, P ) + 2.0*self.gears_addendum( pa, N, P )

        # compute the outer diameter of a gear with a given pressure-angle (pa)
        # number of teeth (N), and pitch (P)
        def gears_pitch_diameter( self, pa, N, P ):
            return float(N)/float(P)

        # compute the outer diameter of a gear with a given pressure-angle (pa)
        # number of teeth (N) and pitch (P)
        def gears_circular_pitch( self, pa, N, P ):
            return math.pi/float(P)

        # compute the circular tooth thickness of a gear with a given 
        # pressure-angle (pa), number of teeth (N) and pitch (P)
        def gears_circular_tooth_thickness( self, pa, N, P, backlash=0.05 ):
            return self.gears_circular_pitch( pa, N, P )/(2.0+backlash)

        # compute the circular tooth angle of a gear with a given
        # pressure-angle (pa), number of teeth (N) and pitch (P)
        def gears_circular_tooth_angle( self, pa, N, P ):
            return self.gears_circular_tooth_thickness( pa, N, P )*2.0/self.gears_pitch_diameter( pa, N, P )

        # compute the addendum height for a gear with a given
        # pressure-angle (pa), number of teeth (N) and pitch (P)
        def gears_addendum( self, pa, N, P ):
            return 1.0/float(P)

        # compute the dedendum depth for a gear with a given 
        # pressur-angle (pa), number of teeth (N) and pitch (P)
        def gears_dedendum( self, pa, N, P ):
            return 1.25/float(P)

        # generates an involute curve from a circle of radius r up to theta_max radians
        # with a specified number of steps
        def gears_generate_involute( self, r, r_max, theta_max, steps=30 ):
            dtheta = theta_max / float(steps)
            x = []
            y = []
            theta = []
            rlast = r;
            for i in range( 0, steps+1 ):
                c = math.cos( i*dtheta )
                s = math.sin( i*dtheta )
                tx = r*( c + i*dtheta*s )
                ty = r*( s - i*dtheta*c )
                d = math.sqrt(tx*tx+ty*ty)
                if d > r_max:
                    a = (r_max-rlast)/(d-rlast)
                    tx = x[-1]*(1.0-a) + tx*a
                    ty = y[-1]*(1.0-a) + ty*a
                    ttheta = theta[-1]*(1.0-a) + math.atan2( ty, tx )*a
                    x.append( tx )
                    y.append( ty )
                    theta.append( ttheta )
                    break
                else:
                    x.append( tx ) 
                    y.append( ty )
                    theta.append( math.atan2( ty, tx) )
            return x, y, theta
        
        # returns the angle where an involute curve crosses a circle with a given radius
        # or -1 on failure
        def gears_locate_involute_cross_angle_for_radius( self, r, ix, iy, itheta ):
            for i in range( 0, len(ix)-1 ):
                r2 = ix[i+1]*ix[i+1] + iy[i+1]*iy[i+1]
                if r2 > r*r:
                    r1 = math.sqrt( ix[i]*ix[i] + iy[i]*iy[i] )
                    r2 = math.sqrt( r2 )
                    a = (r-r1)/(r2-r1)
                    return itheta[i]*(1.0-a) + itheta[i+1]*a
            return -1.0
        
        # rotates the involute curve around the gear center in order to have the involute
        # cross the x-axis at the pitch diameter
        def gears_align_involute( self, Dp, ix, iy, itheta ):
            theta = -self.gears_locate_involute_cross_angle_for_radius( Dp/2.0, ix, iy, itheta )
            c = math.cos(theta)
            s = math.sin(theta)
            for i in range( 0, len(ix) ):
                tx = c*ix[i] - s*iy[i]
                ty = s*ix[i] + c*iy[i]
                ix[i] = tx
                iy[i] = ty
            return ix, iy
        
        # reflects the input curve about the x-axis to generate the opposing face of 
        # a tooth
        def gears_mirror_involute( self, ix, iy ):
            tx = []
            ty = []
            for i in range( 0, len(iy) ):
                tx.append( ix[len(iy)-1-i] )
                ty.append( -iy[len(iy)-1-i] )
            return tx, ty
        
        # rotates the input curve by a given angle (in radians)
        def gears_rotate( self, theta, ix, iy ):
            c = math.cos(theta)
            s = math.sin(theta)
            x = []
            y = []
            for i in range( 0, len(ix) ):
                tx = c*ix[i] - s*iy[i]
                ty = s*ix[i] + c*iy[i]
                x.append( tx )
                y.append( ty )
            return x, y
        
        # translates the input curve by [dx, dy]
        def gears_translate(self,  dx, dy, ix, iy ):
            x = []
            y = []
            for i in range( 0, len(ix) ):
                x.append( ix[i]+dx )
                y.append( iy[i]+dy )
            return x, y
            
        # generates a single tooth profile of a spur gear
        def gears_make_tooth( self, pa, N, P ):
            ix, iy, itheta = self.gears_generate_involute( self.gears_base_diameter( pa, N, P )/2.0, self.gears_outer_diameter( pa, N, P )/2.0, math.pi/2.1 )
            ix.insert( 0, min( self.gears_base_diameter( pa, N, P )/2.0, self.gears_root_diameter( pa, N, P )/2.0 ) )
            iy.insert( 0, 0.0 )
            itheta.insert( 0, 0.0 )
            if self.round_corners:
                cx=ix[-1]
                cy=iy[-1]
                for i in range(2,5):
                        iy.append(cy+(1.0-math.cos(float(i)*math.pi/8))*self.round_corners/P)	
                        ix.append(cx+(math.sin(float(i)*math.pi/8))*self.round_corners/P)
                        itheta.append(math.atan2(iy[-1], ix[-1]))
                cx=ix[0]
                cy=iy[0]
#		for i in range(1,5):
#			iy.insert(0,cy-(1-math.cos(i*math.pi/8))*self.round_corners/P*2)	
#			ix.insert(0,cx-(math.sin(i*math.pi/8))*self.round_corners/P*2)
#			itheta.insert(0,math.atan2(iy[0], ix[0]))
                iy.insert(0,cy-self.round_corners/P*2)
                ix.insert(0,cx-self.round_corners/P*2)
                itheta.insert(0,math.atan2(iy[0], ix[0]))
            ix, iy = self.gears_align_involute( self.gears_pitch_diameter(pa, N, P), ix, iy, itheta )
            mx, my = self.gears_mirror_involute( ix, iy )
            mx, my = self.gears_rotate( self.gears_circular_tooth_angle( pa, N, P ), mx, my )
            ix.extend( mx )
            iy.extend( my )
        
            return ix, iy
        
        # generates a spur gear with a given pressure angle (pa),
        # number of teeth (N) and pitch (P)
        def gears_make_gear(self, pa, N, P, ignore_teeth=False ):
            tx, ty = self.gears_make_tooth( pa, N, P )
            x = []
            y = []
            for i in range( self.first_tooth, self.first_tooth+N ):
                rx=[]
                ry=[]
                if ignore_teeth and N-i<=ignore_teeth-self.first_tooth:
                        if not self.just_teeth:
                                rx=[self.gears_root_diameter( pa, N, P)/2*math.cos( float(i)*2.0*math.pi/float(N))]
                                ry=[self.gears_root_diameter( pa, N, P)/2*math.sin( float(i)*2.0*math.pi/float(N))]
                else:
                        rx, ry = self.gears_rotate( float(i)*2.0*math.pi/float(N), tx, ty )
                x.extend( rx )
                y.extend( ry )
#	    x.append( x[0] )
#	    y.append( y[0] )
            return x, y

        def gears_camcam( self, px, py):
                lastp=V(100000,100000)
                if px[0]==px[len(px)-1] and py[0]==py[len(px)-1]:
                        l=len(px)-1
                else:
                        l=len(px)
                for i in range(0, l):
                        p = V(px[i], py[i])
                        if p != lastp:
                                self.add_point(p)
                        lastp = p
        def __init__(self, pos, pressure_angle, number_teeth, **config):
                self.init(config)
                self.closed=True
                if 'pitch' in config:
                        Pd=math.pi/float(config['pitch'])
                elif 'rad' in config:
                        Pd=float(number_teeth)/(float(config['rad']*2))
                if 'ignore_teeth' in config:
                        ignore_teeth = config['ignore_teeth']
                else:
                        ignore_teeth = False
                if 'first_tooth' in config:
                        self.first_tooth=config['first_tooth']
                else:
                        self.first_tooth=0
                if 'round_corners' in config:
                        self.round_corners=config['round_corners']
                else:
                        self.round_corners=False
                if 'just_teeth' in config:
                        self.just_teeth=config['just_teeth']
                else:
                        self.just_teeth=False
                if 'no_gear' not in config:
                        x, y = self.gears_make_gear(pressure_angle, number_teeth, Pd, ignore_teeth)
                if 'rotate_gear' in config:
                        x,y = self.gears_rotate(-float(config['rotate_gear'])*math.pi/180, x, y)
                if 'no_gear' not in config:
                        self.gears_camcam(x,y)
                        self.translate(pos)
                        self.base_diameter=self.gears_base_diameter(pressure_angle, number_teeth, Pd)
                        self.outer_diameter=self.gears_outer_diameter(pressure_angle, number_teeth, Pd)
                        self.root_diameter=self.gears_root_diameter(pressure_angle, number_teeth, Pd)

class GearPoints(list):
        def __init__(self, pos, pressure_angle, number_teeth, **config):
                if 'pitch' in config:
                        Pd=math.pi/float(config['pitch'])
                elif 'rad' in config:
                        Pd=float(number_teeth)/(float(config['rad']*2))
                if 'ignore_teeth' in config:
                        ignore_teeth = config['ignore_teeth']
                else:
                        ignore_teeth = False
                if 'round_corners' in config:
                        self.round_corners=config['round_corners']
                else:
                        self.round_corners=False
                config['just_teeth']=True
                self.gear = InvoluteGearBorder(V(0,0), pressure_angle, number_teeth, **config)
                self.extend(self.gear.points)
                self.base_diameter=self.gear.base_diameter
                self.outer_diameter=self.gear.outer_diameter
                self.root_diameter=self.gear.root_diameter

class GearRack(list):
        def __init__(self, start, end, pressure_angle, **config):
                c={}
                number_teeth = 1000
                if 'layer' in config:
                        self.layer= config['layer']
                if 'name' in config:
                        self.layer=config['layer']
                if 'pitch' in config:
                        c['pitch'] = config['pitch']
                elif 'rad' in config:
                        c['rad'] = config['rad']
                if 'ignore_teeth' in config:
                        c['ignore_teeth'] = config['ignore_teeth']
                if 'round_corners' in config:
                        c['round_corners']= config['round_corners']
                c['no_gear']=True
                length = (end-start).length()
                para = (end-start).normalize()
                if 'tooth_side' in config and config['tooth_side']=='left':
                        perp = rotate(para, -90)
                else:
                        perp = rotate(para, 90)
                rnumber_teeth = int(math.floor(length/config['pitch']))
                dstart = (length -(rnumber_teeth-1) * config['pitch'])/2
                self.gear = InvoluteGearBorder(V(0,0), pressure_angle, number_teeth, **c)
                x,y = self.rack_make_tooth( pressure_angle, number_teeth, config['pitch'])
                ox=[]
                oy=[]
                for i in range(0,rnumber_teeth):
                        ix, iy = self.gear.gears_translate(0,i*c['pitch'], x, y )
                        ox.extend( ix)
                        oy.extend( iy)
#		ox,oy = self.gear.gears_translate(pos[0], pos[1], ox, oy)
                if 'align' in config:
                    if config['align']=='root':
                        dx=-self.rootx
                    elif config['align']=='outer':
                        dx=-self.outerx
                    elif config['align']=='Pd':
                        dx=0
                else:
                    dx =0
                for i in range(0, len(ox)):
                        self.append( PSharp(start+para*dstart+para*oy[i] + perp* ox[i] + perp*dx))
        def rack_make_tooth( self, pa, N, pitch):
            # make tooth for very large diameter
            N=50
            P=math.pi/float(pitch)
            ix, iy, itheta = self.gear.gears_generate_involute( self.gear.gears_base_diameter( pa, N, P )/2.0, self.gear.gears_outer_diameter( pa, N, P )/2.0, math.pi/2.1 )
            ix.insert( 0, min( self.gear.gears_base_diameter( pa, N, P )/2.0, self.gear.gears_root_diameter( pa, N, P )/2.0 ) )
            iy.insert( 0, 0.0 )
            itheta.insert( 0, 0.0 )
            if self.gear.round_corners:
                cx=ix[-1]
                cy=iy[-1]
                for i in range(2,5):
#                        print "QQ"+str(P) + " "+str(V(cx,cy))
#                        print "QQ"+str( V( (math.sin(i*math.pi/8)*self.gear.round_corners/P) , (1-math.cos(i*math.pi/8)*self.gear.round_corners/P)))
			print "QQ"+str(V((1.0+math.sin(math.pi/8*i))*self.gear.round_corners/P, (1.0-math.cos(math.pi/8*i))*self.gear.round_corners/P))+str(math.pi/8*i)
                        ix.append(cx+(math.sin(math.pi/8*i))*self.gear.round_corners/P)
                        iy.append(cy+(1.0-math.cos(math.pi/8*i))*self.gear.round_corners/P)
                        itheta.append(math.atan2(iy[-1], ix[-1]))
                cx=ix[0]
                cy=iy[0]
#                for i in range(1,5):
 #                       ix.insert(0,float(cx)-(1.0+math.sin(math.pi/8*i))*self.gear.round_corners/P*2)
  #                      iy.insert(0,float(cy)-(1.0-math.cos(math.pi/8*i))*self.gear.round_corners/P*2)
   #                     itheta.insert(0,math.atan2(iy[0], ix[0]))
	    ix.insert(0,float(cx)-(self.gear.round_corners/P*2))
            iy.insert(0,float(cy)-(self.gear.round_corners/P*2))
   	    itheta.insert(0,math.atan2(iy[0], ix[0]))

            ix, iy = self.rack_align_involute( self.gear.gears_pitch_diameter(pa, N, P), ix, iy, itheta )
            ix, iy = self.gear.gears_translate(0, -pitch/4, ix, iy )
            mx, my = self.gear.gears_mirror_involute( ix, iy )
#            mx, my = self.gears_rotate( self.gears_circular_tooth_angle( pa, N, P ), mx, my )
            ix.extend( mx )
            iy.extend( my )
            ix, iy = self.gear.gears_translate(-self.gear.gears_pitch_diameter(pa, N, P)/2, 0, ix, iy )
            self.rootx=(self.gear.gears_root_diameter(pa, N, P)-self.gear.gears_pitch_diameter(pa, N, P))/2
            self.outerx=(self.gear.gears_outer_diameter(pa, N, P)-self.gear.gears_pitch_diameter(pa, N, P))/2

            return ix, iy
# returns the angle where an involute curve crosses a circle with a given radius
        # or -1 on failure
        def rack_locate_involute_cross_y_for_radius( self, r, ix, iy, itheta ):
            for i in range( 0, len(ix)-1 ):
                r2 = ix[i+1]*ix[i+1] + iy[i+1]*iy[i+1]
                if r2 > r*r:
                    r1 = math.sqrt( ix[i]*ix[i] + iy[i]*iy[i] )
                    r2 = math.sqrt( r2 )
                    if r1==r2:
                        return iy[i]
                    a = (r-r1)/(r2-r1)
                    return iy[i]*(1.0-a) + iy[i+1]*a
            return -1.0
        def rack_align_involute( self, Dp, ix, iy, itheta ):
            y = -self.rack_locate_involute_cross_y_for_radius( Dp/2.0, ix, iy, itheta )
            ix, iy = self.gear.gears_translate(y, 0, ix, iy )
            return ix, iy

class InvoluteGear(Part):
        def __init__(self, pos, pressure_angle, number_teeth, **config):
                self.init(config)
                c={}
                if 'layer' in config:
                        self.layer= config['layer']
                if 'name' in config:
                        self.layer=config['layer']
                if 'pitch' in config:
                        c['pitch'] = config['pitch']
                elif 'rad' in config:
                        c['rad'] = config['rad']
                if 'ignore_teeth' in config:
                        c['ignore_teeth'] = config['ignore_teeth']
                if 'round_corners' in config:
                        c['round_corners']= config['round_corners']
                self.add_border(InvoluteGearBorder(V(0,0), pressure_angle, number_teeth, **c))
                if 'holerad' in config:
                        self.add(Hole(V(0,0), rad=config['holerad']))
                self.translate(pos)

class SprocketBorder(Path):
        def __init__(self, pos, number_teeth, roller_rad, roller_spacing, **config):
                self.init(config)
                self.closed=True
                gap = float(roller_spacing)-2*roller_rad
                step_angle = 360/float(number_teeth)
                radius = roller_spacing/2/math.tan(float(step_angle)/2/180*math.pi)
                self.effective_rad = roller_spacing/2/math.sin(step_angle/2/180*math.pi)
                radius2 = radius #math.sqrt(radius**2-roller_rad**2)
#		point_length=math.sqrt(gap*roller_rad+3*gap*gap/4)
                point_length=math.sqrt((gap+roller_rad)**2-(roller_rad+gap/2)**2)
                point_length2=math.sqrt((gap+roller_rad)**2-(roller_rad+gap/2*1.7)**2)
                for i in range(0, number_teeth):
                        theta = step_angle * i
#			self.add_point(V(-gap/2,radius),'sharp',1,transform={'rotate':[V(0,0),i*step_angle]})
                        self.add_point(PIncurve(V(0,radius2+point_length*0.7), transform={'rotate':[V(0,0),-theta]}, radius=(roller_spacing-2*roller_rad)/6))
                        self.add_point(PSharp(V(-gap/2*0.7,radius2+point_length2), transform={'rotate':[V(0,0),-theta]}))
                        self.add_point(PArc(length='short', radius=roller_spacing, direction='cw', transform={'rotate':[V(0,0),-theta]}))
                        self.add_point(PSharp(V(-gap/2,radius2),  transform={'rotate':[V(0,0),-theta]}))
                        self.add_point(PArc( length='short', radius=roller_rad, direction='cw', transform={'rotate':[V(0,0),-theta]}))
                        self.add_point(PSharp(V(gap/2,radius2),transform={'rotate':[V(0,0),-theta-step_angle]}))
                        self.add_point(PArc(length='short', radius=roller_spacing, direction='cw', transform={'rotate':[V(0,0),-theta]}))
                        self.add_point(PSharp(V(gap/2*0.7,radius2+point_length2), transform={'rotate':[V(0,0),-theta-step_angle]}))
