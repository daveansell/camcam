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
	    ix, iy = self.gears_align_involute( self.gears_pitch_diameter(pa, N, P), ix, iy, itheta )
	    mx, my = self.gears_mirror_involute( ix, iy )
	    mx, my = self.gears_rotate( self.gears_circular_tooth_angle( pa, N, P ), mx, my )
	    ix.extend( mx )
	    iy.extend( my )
	    return ix, iy
	
	# generates a spur gear with a given pressure angle (pa),
	# number of teeth (N) and pitch (P)
	def gears_make_gear(self, pa, N, P ):
	    tx, ty = self.gears_make_tooth( pa, N, P )
	    x = []
	    y = []
	    for i in range( 0, N ):
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
			Pd=1/2*float(config['rad'])/number_teeth
		x, y = self.gears_make_gear(pressure_angle, number_teeth, Pd)
		self.gears_camcam(x,y)
		self.translate(pos)
		self.base_diameter=self.gears_base_diameter(pressure_angle, number_teeth, Pd)
		self.outer_diameter=self.gears_outer_diameter(pressure_angle, number_teeth, Pd)
		self.root_diameter=self.gears_root_diameter(pressure_angle, number_teeth, Pd)


class InvoluteGear(Part):
	def __init__(self, pos, pressure_angle, number_teeth, pitch, **config):
		self.init(config)
		c=[]
		if 'pitch' in config:
			c['pitch'] = config['pitch']
		elif 'rad' in config:
			c['rad'] = config['rad']
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
		radius2 = radius #math.sqrt(radius**2-roller_rad**2)
#		point_length=math.sqrt(gap*roller_rad+3*gap*gap/4)
		point_length=math.sqrt((gap+roller_rad)**2-(roller_rad+gap/2)**2)
		point_length2=math.sqrt((gap+roller_rad)**2-(roller_rad+gap/2*1.7)**2)
		for i in range(0, number_teeth):
			theta = step_angle * i
#			self.add_point(V(-gap/2,radius),'sharp',1,transform={'rotate':[V(0,0),i*step_angle]})
			self.add_point(V(0,radius2+point_length*0.7),'sharp',1, transform={'rotate':[V(0,0),-theta]})
			self.add_point(V(-gap/2*0.7,radius2+point_length2),'arcend',1, transform={'rotate':[V(0,0),-theta]})
			self.add_point(V(0,radius2), 'arc',roller_spacing, direction='cw', transform={'rotate':[V(0,0),-theta]})
			self.add_point(V(-gap/2,radius2), 'arcend', 0,  transform={'rotate':[V(0,0),-theta]})
			self.add_point(V(0,radius2), 'arc',roller_rad, direction='ccw', transform={'rotate':[V(0,0),-theta]})
			self.add_point(V(gap/2,radius2), 'arcend',0, transform={'rotate':[V(0,0),-theta-step_angle]})
			self.add_point(V(0,radius), 'arc',roller_spacing, direction='cw', transform={'rotate':[V(0,0),-theta]})
			self.add_point(V(gap/2*0.7,radius2+point_length2),'arcend',1, transform={'rotate':[V(0,0),-theta-step_angle]})
