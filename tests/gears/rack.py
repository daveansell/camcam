from gears import *

plane = camcam.add_plane(Plane('xy', cutter='4mm_endmill'))
plane.add_layer('rack', 'delrin', 12)

r=GearRack(V(0,0), V(0,250), 10,  pitch=15, round_corners=0.01)
rack = Path(closed=True, side='out')
rack.add_points(r)
rack.add_point(V(r.rootx,300))
rack.add_point(V(-30,300))
rack.add_points(GearRack(V(-30,250), V(-30,0), 10,  pitch=15, round_corners=0.01, align='root', tooth_side='left'))
rack.add_point(V(-30,-20))
rack.add_point(V(r.rootx,-20))
plane.add(Part(name='rack', layer='rack', border=rack))
plane.add(InvoluteGear(V(0,0),10,20, pitch=15))
