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
from camcamconfig import *
from path import *
from shapes import *
from parts import *
#print ("********has3D"+str(__camcam3d__))
#try:
#    __camcam3d__
#    from cc3d import *
#    has3D = True
#except NameError:
#    has3D = False
if has3D:
    from cc3d import *
#has3D = True
class RoundedBoxEnd(Part):
    def __init__(self,pos, layer, name, width, centre_height, centre_rad, centre_holerad, side_height, bend_rad=0,  sidemodes=False, thickness=6, tab_length=False,  fudge=0, **config):
        self.init(config)
        self.translate(pos)
        if sidemodes==False:
            sidemodes={'right':'off', 'bottom':'off', 'left':'off'}
        if tab_length==False:
            tab_length=20
        self.name=name
        self.layer=layer
        self.add_border(Path(closed=True, side='out'))
        self.centrepos=V(0,0)
        self.border.add_point(self.centrepos+V(-width/2-thickness, side_height-centre_height))
#               self.border.add_point(self.centrepos+V(-width/2-thickness, side_height-centre_height+0.01), radius=bend_rad)
        self.border.add_point(POutcurve(self.centrepos, direction='cw', radius=centre_rad))
#               self.border.add_point(self.centrepos+V(width/2+thickness, side_height-centre_height+0.01), radius=bend_rad)
        self.border.add_point(self.centrepos+V(width/2+thickness, side_height-centre_height))
#               self.border.add_point(self.centrepos+V(width/2+thicknes, side_height-centre_height))
        self.border.add_points(FingerJoint(self.centrepos+V(width/2, side_height-centre_height),
                                        self.centrepos+V(width/2,-centre_height),
                                        'left',
                                        'external',
                                        sidemodes['right'],
                                        sidemodes['right'],
                                        tab_length,
                                        thickness,
                                        0,
                                        fudge))
        self.border.add_points_intersect(FingerJoint(self.centrepos+V(width/2, -centre_height),
                                        self.centrepos+V(-width/2,-centre_height),
                                        'left',
                                        'external',
                                        sidemodes['bottom'],
                                        sidemodes['bottom'],
                                        tab_length,
                                        thickness,
                                        0,
                                        fudge))
        self.border.add_points_intersect(FingerJoint(self.centrepos+V(-width/2, -centre_height),
                                        self.centrepos+V(-width/2,side_height-centre_height),
                                        'left',
                                        'external',
                                        sidemodes['right'],
                                        sidemodes['right'],
                                        tab_length,
                                        thickness,
                                        0,
                                        fudge))
        if centre_holerad>0:
            self.add(Hole(V(0,0), rad=centre_holerad))

class RoundedBox(Part):
    def __init__(self,pos, layers, name, length, width, centre_height, centre_rad, centre_holerad, side_height, bend_rad=0, thickness=6, tab_length=False,  fudge=0, **config):
        self.init(config)
        cutter=False
        self.translate(pos)
        self.end=self.add(RoundedBoxEnd(V(0,0), layers['end'], name+'_end', width, centre_height, centre_rad, centre_holerad, side_height, bend_rad,  {'right':'off', 'bottom':'off', 'left':'off'}, thickness, tab_length,  fudge))
        if 'blank_end' in config:
            self.end2=self.add(RoundedBoxEnd(V(0,0), layers['end2'], name+'_end2', width, centre_height, centre_rad, config['centre_holerad2'], side_height, bend_rad,  {'right':'off', 'bottom':'off', 'left':'off'}, thickness, centre_height+20,  fudge))
            side_modes = {'top':'straight', 'left':'straight'}
            bottom_modes = {'bottom':'straight'}
        elif 'centre_holerad2' in config:
            self.end2=self.add(RoundedBoxEnd(V(0,0), layers['end2'], name+'_end2', width, centre_height, centre_rad, config['centre_holerad2'], side_height, bend_rad,  {'right':'off', 'bottom':'off', 'left':'off'}, thickness, tab_length,  fudge))
            side_modes={'top':'straight'}
            bottom_modes={}
        else:
            self.end.number=2
            side_modes={'top':'straight'}
            bottom_modes={}
        self.side=self.add(Part(name=name+'_side', layer=layers['side'], border=FingerJointBoxSide( V(0,0), length, side_height, 'out', {'left':'on', 'bottom':'off', 'right':'on', 'top':'on'}, side_modes, tab_length, thickness, cutter, auto=True)))
        self.side.number=2
        self.bottom=self.add(Part(name=name+'_bottom', layer=layers['bottom'], border=FingerJointBoxSide( V(0,0), width, length, 'out', {'left':'on', 'bottom':'on', 'right':'on','top':'on'}, bottom_modes, tab_length, thickness, cutter, auto=True,centred=True)))



class Turret(Part):
    def __init__(self, pos, plane, name, turret_type, thickness, fudge, **config):
        self.init(config)
        self.init_turret(pos, plane, name, turret_type, thickness, fudge, config)

    def init_turret(self, pos, plane, name, turret_type, thickness, fudge, config):
        p_layers={'side':'_side', 'end':'end', 'end2':'_end2', 'bottom':'_bottom', 'bearing_ring':'_bearing_ring', 'tube_insert':'_tube_insert', 'tube_insert_in':'_tube_insert_in', 'base':'_base',  'base_protector':'_base_protector'}
        layers = {}

        for i, l in p_layers.items():
            plane.add_layer(name+l, material='pvc', thickness=thickness, z0=0)
            layers[i] = name+l
        self.translate(pos)
        plane.add_layer(name+'_under_base', material='pvc', thickness = 10, z0=0)
        plane.add_layer(name+'_end_plate', material='pvc', thickness = 12.3, z0=0)
        data={
                'camera':{'length':85, 'edge_width':10, 'centre_height':60, 'centre_rad':56/2, 'centre_inner_rad':51.3/2, 'centre_holerad':10.2/2, 'side_height':50, 'bend_rad':5, 'tab_length':10, 'piviot_hole_rad':25/2, 'square_hole_side':10},
                'thermal':{'length':85, 'edge_width':10, 'centre_height':60, 'centre_rad':56/2, 'centre_inner_rad':51.3/2, 'centre_holerad':10.2/2, 'side_height':50, 'bend_rad':5, 'tab_length':10, 'piviot_hole_rad':20/2, 'square_hole_side':10},
                'lamp':{'length':50, 'edge_width':10, 'centre_height':35, 'centre_rad':56/2, 'centre_inner_rad':51.3/2, 'centre_holerad':10.2/2, 'side_height':50, 'bend_rad':5, 'tab_length':10, 'piviot_hole_rad':20/2, 'square_hole_side':10},
        }
        assert turret_type in data
        d=data[turret_type]
        self.d = d
        width = math.sqrt(d['centre_rad']**2-(d['centre_height']-d['side_height'])**2)*2
        base_protector_rad=40
        base_rad = math.sqrt((d['length']/2+thickness)**2 + (width/2+thickness)**2)+5
        box=self.add(RoundedBox(V(0,0), layers, name, d['length'], width, d['centre_height'], d['centre_rad'], 0, d['side_height'], d['bend_rad'], thickness, d['tab_length'], fudge, blank_end =True, centre_holerad2=0))
        self.bottom=box.bottom
        self.end=box.end
        # holes for cable clamps inside base
        self.bottom.add(Hole(V(0, -d['length']/2+20), rad=3.3/2))
        self.bottom.add(Hole(V(width/3, -d['length']/2+26), rad=3.3/2))
        self.bottom.add(Hole(V(-width/5, -d['length']/2+20), rad=3.3/2))
        self.bottom.add(Hole(V(-width/4, -width/4), rad=3.3/2))


        # Square for coach bolt
        self.end.add(Rect(V(0,0), centred=True, width=d['square_hole_side'], height=d['square_hole_side'], side='in'))
        self.side=box.side

        self.side.add(Hole(V(6, 8), 4.3/2))
        self.side.add(Hole(V(6, d['side_height']-10), 4.3/2))

        # piviot hole through middle
        self.bottom.add(Hole(V(0,0), rad=d['piviot_hole_rad']), [name+'_bottom', name+'_base', name+'_under_base'])
        self.bottom.add(Hole(V(0,0), rad=base_protector_rad+2), ['base', 'perspex', 'paper'])
        self.base_protector_rad=base_protector_rad
        # bearing ring sits inside open end of tube
        self.bearing_ring = self.add(Part(name = name+'_bearing_ring', layer = name+'_bearing_ring', border = Circle(V(0,0), rad=d['centre_inner_rad']-0.2, side='out')))
        for i in range(0,4):
            t=self.bearing_ring.add(Bolt(V(d['centre_inner_rad']*2/3, 0), 'M4', insert_layer=[], clearance_layers=name+'_end2', thread_layer=name+'_bearing_ring'))
            t.rotate(V(0,0), i*90)
        # end plate sits inside the opening end to allow it to be attached
        end_plate_border = Path(side='out', closed=True)
        end_plate_border.add_point(V(-width/2, -d['centre_height'] + d['side_height']-4))
        end_plate_border.add_point(V(-width/2, -d['centre_height']))
        end_plate_border.add_point(V(width/2, -d['centre_height']))
        end_plate_border.add_point(V(width/2, -d['centre_height'] + d['side_height']-4))
        end_plate_border.add_point(PIncurve(V(width/2-d['edge_width'], -d['centre_height'] + d['side_height']-d['edge_width']-4), radius=d['edge_width']))
        end_plate_border.add_point(PIncurve(V(width/2-d['edge_width'], -d['centre_height']+d['edge_width'] ), radius=d['edge_width']))
        end_plate_border.add_point(PIncurve(V(-width/2+d['edge_width'], -d['centre_height']+d['edge_width'] ), radius=d['edge_width']))
        end_plate_border.add_point(PIncurve(V(-width/2+d['edge_width'], -d['centre_height'] + d['side_height']-d['edge_width']-4), radius=d['edge_width']))
        self.end_plate = self.add(Part(name = name+'_end_plate', layer =  name+'_end_plate', border = end_plate_border))
        # Holes to hold end_plate while gluing
        self.end_plate.add(Bolt(V(width/2-d['edge_width']/2, -d['centre_height'] + d['side_height']-d['edge_width']-16), 'M4', insert_layer=[], clearance_layers=name+'_end_plate', thread_layer=name+'_end2', thread_depth=4))
        self.end_plate.add(Bolt(V(-width/2+d['edge_width']/2, -d['centre_height'] + d['side_height']-d['edge_width']-16), 'M4', insert_layer=[], clearance_layers=name+'_end_plate', thread_layer=name+'_end2', thread_depth=4))

        self.end_plate.add(Bolt(V(width/2-d['edge_width']/2, -d['centre_height'] +d['edge_width']/2), 'M4', insert_layer=[], clearance_layers=name+'_end_plate', thread_layer=name+'_end2', thread_depth=4))
        self.end_plate.add(Bolt(V(-width/2+d['edge_width']/2, -d['centre_height'] +d['edge_width']/2), 'M4', insert_layer=[], clearance_layers=name+'_end_plate', thread_layer=name+'_end2', thread_depth=4))

        # Tube insert is a double layer circle that glues into closed end of tube
        self.tube_insert = self.add(Part(name = name+'_tube_insert', layer= name+'_tube_insert', border = Circle(V(0,0), rad=d['centre_rad']+0.5)))
        self.tube_insert_in = self.add(Part(name = name+'_tube_insert_in', layer= name+'_tube_insert_in', border = Circle(V(0,0), rad=d['centre_inner_rad'])))
        self.tube_insert.add(Hole(V(0,0), rad=d['centre_holerad']), [ name+'_tube_insert',  name+'_tube_insert_in'])

        # under base is a ring under the board to act as bearing on piviot
        self.under_base = self.add(Part(name=name+'_under_base', layer = name+'_under_base', border = Circle(V(0,0), rad=base_protector_rad, side='out')))
        self.under_base.number = 2

        # magnet slots
        t=self.under_base.add(Rect(V((base_protector_rad+d['piviot_hole_rad'])/2,0), centred = True, width = base_protector_rad-d['piviot_hole_rad']-10, height = 6, z1 = -6, side='in'), name+'_under_base')
        t.rotate(V(0,0),15)
        t=self.under_base.add(Rect(V(-(base_protector_rad+d['piviot_hole_rad'])/2,0), centred = True, width = base_protector_rad-d['piviot_hole_rad']-10, height = 6, z1 = -6, side='in'), name+'_under_base')
        t.rotate(V(0,0),15)

        # base sits above board to act as bearing and constrain rotation
        self.base = self.add(Part(name=name+'_base', layer = name+'_base', border = Circle(V(0,0), rad=base_rad, side='out', cutter='1/8_endmill')))
        self.base.add(AngleConstraint(V(0,0), width/2-4, 320, 'M4', name+'_base', name+'_bottom', side='on'))

        # base protector sits on standoffs and has cable cable-tied to it protecting and holding the cable
        self.base_protector = self.add(Part(name=name+'_base_protector', layer = name+'_base_protector', border = Circle(V(0,0), rad=base_protector_rad, side='out')))
        self.base_protector.add(Lines([V(-5, base_protector_rad-12), V(-5, base_protector_rad-8)]))
        self.base_protector.add(Lines([V(5, base_protector_rad-12), V(5, base_protector_rad-8)]))
        self.base_protector.add(Lines([V(-5, base_protector_rad-20), V(-5, base_protector_rad-24)]))
        self.base_protector.add(Lines([V(5, base_protector_rad-20), V(5, base_protector_rad-24)]))
        self.holdDownHoleRad=base_rad-8
        for i in range(0,6):
            t=self.base.add(Bolt(V(0, base_rad-8), 'M4', clearance_layers=['perspex', 'paper', name+'_base']))
            t.rotate(V(0,0), i*60)
            t=self.under_base.add(Bolt(V(0, base_protector_rad-7), 'M4', clearance_layers=[ name+'_under_base'], thread_layer=[], insert_layer=[]))
            t.rotate(V(0,0), i*60)
            t=self.base_protector.add(Bolt(V(0, base_protector_rad-7), 'M4', clearance_layers=name+'_base_protector', thread_layer=name+'_under_base', insert_layer=[]))
            self.add_bom('standoff',1, 'M4 standooff MF 30mm', description='30mm standoff')
            t.rotate(V(0,0), 30+i*60)
        self.add_bom('M20 hollow',1,'M20_hollow', description='M20 hollow bolt')
        self.add_bom('M20 wavy washer',1, 'M20_wavy_washer', description='M20 wavy washer')
        self.add_bom('M20 washer',3, 'M20_washer', description='M20 washer')
        self.add_bom('M20 conduit locknut',3,'M20_conduit_locknut', description='M20 condut locknut')
        self.add_bom('20mm thrust bearing',1, '20mm_thrust_bearing', description='20mm thrust bearing')
        self.add_bom(BOM_rod('tube', 'black pvc', 'round tube', d['centre_rad']*2, d['length']-thickness-1, 1, 'Tube to make up-down part of turret should have holes drilled to take camera holder, sometimes camera and cable'))

class PiCamTurret(Turret):
    def __init__(self, pos, plane, name, thickness, fudge, **config):
        self.init(config)
        self.init_turret(pos, plane, name, 'camera', thickness, fudge, config)
        rod_rad = 51.5/2
        cam_yoff = 5.0
        cam_width=25.0
        cam_height=28.0
        cam_hole_from_side=2.0
        cam_hole_from_bottom=9.5
        cam_ribbon_width = 16.0
        cable_slot_depth = 40.0
        cable_slot_height = cam_yoff*2
        cable_slot_width=cam_ribbon_width+8.0
        mount_hole_from_edge = (rod_rad-(cam_height+cam_yoff*2)/2)/2
        window_rad = rod_rad-mount_hole_from_edge-2
        view_rad = window_rad -2
        accel_width = 22
        accel_depth = 17.5
        if 'window_thickness' in config:
            window_thickness = config['window_thickness']
        else:
            window_thickness = 3
        if 'face_thickness' in config:
            face_thickness = config['face_thckness']
        else:
            face_thickness = 6.5

        plane.add_layer(name+'_camera_holder', material='pvc', thickness=thickness, z0=0)
        plane.add_layer(name+'_camera_face', material='pvc', thickness=face_thickness, z0=0)
        plane.add_layer(name+'_camera_window', material='perspex', thickness=window_thickness, z0=0)
        self.camera_face = self.add(Part(name=name+'_camera_face', layer= name+'_camera_face', border = Circle(V(0,0), rad=rod_rad+1)))
        self.camera_face.add(Hole(V(0,0), rad=view_rad))
        self.camera_face.add(Hole(V(0,0), rad=window_rad, z1=-window_thickness))
        self.camera_window = self.add(Part(name=name+'_camera_window', layer= name+'_camera_window', border = Circle(V(0,0), rad=window_rad)))

        self.camera_holder = self.add(Part(name=name+'_camera_holder', layer= name+'_camera_holder', ignore_border=True))
        if 'cam_depth' in config:
            cam_depth = config['cam_depth']
        else:
            cam_depth = 26.0


        cam_centre= V(0, cam_yoff)
        self.camera_holder.add(Circle(V(0,0), rad=rod_rad), 'paper')
        self.camera_holder.add(Rect(cam_centre, centred=True, width = cam_width+2, height=cam_height+1, z1=-cam_depth-1, partial_fill=cam_width/2-4, cutter='6mm_endmill', side='in'))
        self.camera_holder.add(Rect(cam_centre+V(0,-cam_height/2-cable_slot_height/2), centred=True, width= cable_slot_width, height=cable_slot_height, z1=-cable_slot_depth, cutter='6mm_endmill', rad=3.1, partial_fill=cable_slot_height/2-7, side='in'))

        self.camera_holder.add(Drill(cam_centre+V(cam_width/2-cam_hole_from_side, cam_height/2-cam_hole_from_side), z0= -cam_depth-1, z1=-cam_depth-1, rad=1.5/2))
        self.camera_holder.add(Drill(cam_centre+V(-cam_width/2+cam_hole_from_side, cam_height/2-cam_hole_from_side), z0= -cam_depth-1, z1=-cam_depth-1, rad=1.5/2))
        self.camera_holder.add(Drill(cam_centre+V(cam_width/2-cam_hole_from_side, -cam_height/2+cam_hole_from_bottom), z0= -cam_depth-1, z1=-cam_depth-1, rad=1.5/2))
        self.camera_holder.add(Drill(cam_centre+V(-cam_width/2+cam_hole_from_side, -cam_height/2+cam_hole_from_bottom), z0= -cam_depth-1, z1=-cam_depth-1, rad=1.5/2))
        for i in range(0,6):
            t=self.camera_holder.add(Drill(V(0,rod_rad-mount_hole_from_edge), z1=-1, rad=1.5/2))
            t.rotate(V(0,0), i*60)
            t=self.camera_holder.add(Hole(V(0,rod_rad-mount_hole_from_edge),  rad=3.3/2), name+'_camera_face')
            t.rotate(V(0,0), i*60)
        cone_rad = rod_rad - 2*mount_hole_from_edge
        cone_inner_rad = cam_width/2
        cone_depth = cam_depth/2
        rstep = 4
        steps = int(math.ceil((cone_rad-cone_inner_rad)/rstep))
        rstep = (cone_rad-cone_inner_rad)/steps
        dstep = cone_depth / steps
        for i in range(0, steps):
            self.camera_holder.add(Circle(V(0,0), rad = cone_rad-rstep*i, z1 = -dstep*(i+1), side='in', cutter='6mm_endmill'))
        #               accelerometer
        self.camera_holder.add(RoundedRect(cam_centre, rad=3.1, centred=True, height = accel_width, width=6.5, z0 = -cam_depth, z1=-cam_depth-accel_depth, cutter="6mm_endmill", side='in'))
        self.camera_holder.add(RoundedRect(cam_centre+V(6.5/2,0), tr=V(-6.5/2, -cam_height/2-cable_slot_height/2), z0 = -cam_depth, z1=-cam_depth-6, cutter="6mm_endmill", rad=3.1, side='in'))
        self.add_bom(BOM_rod('rod', 'black pvc', 'round', rod_rad*2, 58, 1, 'rod for camera, should have a bite takenout of the middle of one side of radius the tube, and depth 14mm'))

class ThermalTurret(Turret):
    def __init__(self, pos, plane, name, thickness, fudge, **config):
        self.init(config)
        self.init_turret(pos, plane, name, 'thermal', thickness, fudge, config)
        cam_rad=25.0/2
        cam_height=45.0
        cam_lens_depth = 20
        cam_depth=14
        cam_top_to_connector = 2
        cam_front_z = -8
        cam_back_z = cam_front_z - cam_lens_depth

        centre_rad=56/2
        centre_inner_rad=51.3/2
        tube_wall = centre_rad-centre_inner_rad

        rod_rad = 51.5/2
        rod_length = 57
        window_holder_thickness = 6.5
        window_holder_rad = rod_rad - 2

        window_rad=28/2
        window_hole_rad = 20/2

        accel_width = 22
        accel_depth = 17.5

        if 'window_thickness' in config:
            window_thickness = config['window_thckness']
        else:
            window_thickness = 2
        if 'face_thickness' in config:
            face_thickness = config['face_thckness']
        else:
            face_thickness = 6.5


        minimum_bite_depth = rod_rad - cam_top_to_connector + tube_wall
        self.comment("Minimum bite depth = "+str(minimum_bite_depth))
        camera_centre = V(0, 0)

        hole_y = math.sqrt((rod_rad-2)**2 - cam_rad**2)
        plane.add_layer(name+'_camera_holder', material='pvc', thickness=50, z0=0)
        plane.add_layer(name+'_window_holder', material='delrin', thickness=window_holder_thickness, z0=0)
        self.camera_holder = self.add(Part(name=name+'_camera_holder', layer= name+'_camera_holder', ignore_border=True))
        self.window_holder = self.add(Part(name=name+'_window_holder', layer= name+'_window_holder', border = Circle(V(0,0), rad=window_holder_rad)))

        plane.add_layer(name+'_camera_face', material='pvc', thickness=face_thickness, z0=0)
        self.camera_face = self.add(Part(name=name+'_camera_face', layer= name+'_camera_face', border = Circle(V(0,0), rad=rod_rad+1)))
        self.camera_face.add(Hole(V(0,0), rad=window_hole_rad))

        camera_cutout = Path(closed=True, side='in', partial_fill= cam_rad-4, cutter='6mm_endmill', z1=cam_back_z, )
        camera_cutout.add_point(PSharp(V(-cam_rad, -hole_y/2)))
        camera_cutout.add_point(POutcurve(V(0,0), radius = cam_rad))
        camera_cutout.add_point(PSharp(V(cam_rad, -hole_y/2)))
        camera_cutout.add_point(PIncurve(V(cam_rad, -hole_y), radius=3.5))
        camera_cutout.add_point(PIncurve(V(-cam_rad, -hole_y), radius=3.5))
        self.camera_holder.add(camera_cutout)
        self.camera_holder.add(FilledCircle(V(0,0), rad=window_holder_rad + 0.5, z1 = -window_holder_thickness, cutter="6mm_endmill"))

#               accelerometer
        self.camera_holder.add(RoundedRect(V(0,0), rad=3.1, centred=True, width = accel_width, height=6.5, z0 = cam_back_z, z1=cam_back_z-accel_depth, cutter="6mm_endmill", side='in'))
        self.camera_holder.add(RoundedRect(V(6.5/2,0), tr=V(-6.5/2, -hole_y), z0 = cam_back_z, z1=cam_back_z-6, cutter="6mm_endmill", rad=3.1, side='in'))

        for i in range(-2,3):
            t=self.camera_holder.add(Hole(V(0, window_holder_rad -3), rad=3.3/2, z1=-12))
            t.rotate(V(0,0),i*60)
            t=self.window_holder.add(Hole(V(0, window_holder_rad -3), rad=4.3/2), name+'_camera_face')
            t.rotate(V(0,0), i*60)
            t=self.window_holder.add(Hole(V(0, window_holder_rad -3), rad=4.3/2),  name+'_window_holder')
            t.rotate(V(0,0), i*60)
# hole in window_holder as small as possible to keep out fingers and stepped to reflect unwanted light
        angle = 40.0/2
        startz = 4.0
        startr = 2.5
        steps = 6.0
        stepz = window_holder_thickness/steps
        stepr = math.tan(angle/180*math.pi)*stepz
        for i in range(0,6):
            self.window_holder.add(Hole(V(0,0), rad=startr+stepr*i, z1=-window_holder_thickness+stepz*i))
#                self.window_holder.add(Hole(V(0,0), rad=window_rad+0.5, z1=-window_thickness))
 #               self.window_holder.add(Hole(V(0,0), rad= window_rad-1))
        self.add_bom(BOM_rod('rod', 'black pvc', 'round', rod_rad*2, 58, 1, 'rod for camera, should have a bite takenout of the middle of one side of radius the tube, and depth '+str(minimum_bite_depth)+'mm'))


class PlainBox(Part):
    """pos       - position
       name      - part base name - the subparts will be called name_back etc
       layers    - layers if a string everything will be in one layer if a dict of 'top':'top_layer_name' etc they can be different layers
       width     - width in x
       height    - height in y
       depth     - depth in z
                 - all internal dimensions
       thickness - of material

       cornermodes - dict of ('left', 'top'):'on' (on the 'left part' whree it meets the 'top' part this sets the ends to on the line defining it. the 'top' part where it meets the 'left' part will be set to be the opposite
"""
    def __init__(self, pos, name, layers, width, height, depth, thickness, tab_length, **config):
        self.init(config)
        sides = ['top', 'bottom', 'left', 'right', 'front', 'back']
        conns = {
                'front':['left', 'top', 'right', 'bottom'],
                'back':['left', 'top', 'right', 'bottom'],
                'top':['left', 'front', 'right', 'back'],
                'bottom':['left', 'front', 'right', 'back'],
                'left':['front', 'bottom', 'back', 'top'],
                'right':['front', 'bottom', 'back', 'top'],
        }
        dims = {
                'front':[width, height],
                'back':[width, height],
                'top':[width, depth],
                'bottom':[width, depth],
                'left':[ depth, height],
                'right':[depth, height],
        }
        if 'cornermodes' in config:
            cornermodes = config['cornermodes']
        else:
            cornermodes = {}
        if 'facemodes' in config:
            facemodes = config['facemodes']
        else:
            facemodes = {}
        for f in sides:
            if f not in facemodes:
                facemodes[f]='normal'
        for s1 in sides:
            for s2 in conns[s1]:
                if (s1,s2) in cornermodes:
                    if (s2,s1) not in cornermodes:
                        if(cornermodes[(s1,s2)]=='on'):
                            cornermodes[(s2,s1)]='off'
                        else:
                            cornermodes[(s2,s1)]='on'
                elif (s2,s1) in cornermodes:
                    if cornermodes[(s2,s1)]=='on':
                        cornermodes[(s1, s2)]='off'
                    else:
                        cornermodes[(s1, s2)]='on'
                else:
                    cornermodes[(s1,s2)] = 'on'
                    cornermodes[(s2,s1)] = 'off'
        if type(thickness) is dict:
            side_thickness = thickness
        else:
            side_thickness = {}
            for s in sides:
                side_thickness[s]=thickness
        c=V(0,0)#-width/2, -height/2)
        offsets = {
                        'front':V(0,0),
                         'back':V(0,0),
                        'top':V(0, height/2+depth/2+side_thickness['top']+side_thickness['front']+10),
                        'bottom':V(0, -height/2-depth/2- (side_thickness['bottom']+side_thickness['front']+10)),
                        'left':V(-width/2-depth/2-(side_thickness['top']+side_thickness['left']+10),0),
                        'right':V(width/2+depth/2+(side_thickness['top']+side_thickness['left']+10),0),
        }
        for s in sides:
            if side_thickness[s]!=0:
                temp=['left', 'top', 'right', 'bottom']
                i=0
                sm={}
                corners={}
                th={}
                for con in conns[s]:
                    corners[temp[i]]=cornermodes[(s, con)]
                    if side_thickness[con]==0:
                        sm[temp[i]]='straight'
                    th[temp[i]]=side_thickness[con]
                    i+=1
                if type(layers) is dict:
                    l= layers[s]
                else:
                    l=layers
                if facemodes[s]=='normal':
                    t= self.add(Part(layer=l, name=name+'_'+s,
                            border = FingerJointBoxSide(
                                    c,
                                    dims[s][0],
                                    dims[s][1],
                                    'in',
                                    corners,
                                    sm,
                                    tab_length,
                                    th ,
                                     '1/8_endmill', auto=True , centred=True )))
                    t.translate(offsets[s])
                elif facemodes[s]=='mid':
                    t = self.add( FingerJointBoxMidSide(
                                    c,
                                    dims[s][0],
                                    dims[s][1],

                                    corners,
                                    True,
                                    tab_length,
                                    th ,
                                    '1/8_endmill', auto=True , centred=True
                            ),
                            l
                    )

                setattr(self, s, t)
        self.translate(pos)

class ArbitraryBox(Part):
    """
            faces - dict of 'side name' : {'points':[3d point, 3d point, 3d point],
                                            'thickness':thickness
                                            'x': 3d vector setting x direction in this face
                                            'origin': 3d point setting origin of face
                                            'layer': layer part should be in
                                            'corners': { side_no: 'on' or 'off' } side_no is defined as point 0->1 is side 0 etc.
                                                    - if undefined will just be made up.
                                            'tab_length': value or dict of values for each side side_no is defined as point 0->1 is side 0 etc.  default is global tab_length below
                                            'wood_direction': vector - only defined on one face will set which side of the polyhedron the wood is
                                            'good_direction': vector - direction that is going to be finished well
                                            'internal' : True/False - is a hole cut into another part should be added to that part
            'tab_length' - defaule tab length
            'fudge' - fudge for finger joints

            }
    """
    def __init__(self, faces, tab_length, fudge, **config):
        self.init(config)
        self.make_box(faces, tab_length, fudge, **config)
    def make_box(self, faces, tab_length, fudge, **config):
        if 'pos' in config:
            self.pos = config['pos']
        else:
            self.pos = V(0,0)
        self.translate(self.pos)
        self.tab_length = tab_length
        self.fudge = fudge
        self.faces = faces
        self.auto_properties = ['tab_length', 'joint_mode', 'butt_depression', 'butt_holerad', 'butt_numholes', 'hole_spacing', 'hole_offset', 'butt_outline']
        for prop in self.auto_properties:
            if prop in config:
                setattr(self, prop, config[prop])
        self.sides={}
        self.normals = {}
        self.side_angles={}
        self.config = config
        wood_direction_face = None
        wood_direction_faces = []
        good_direction_faces = []
        good_direction_face = None
        self.new_layers = []
        if 'name' in config:
            self.name=config['name']
        else:
            self.name='box'
        for f, face in faces.items():
            if 'rotate' in face:
                #print face['layer']+" x="+str( face['x'])+" dx="+str(face['x']-face['rotate'][0])
                for p in range(0, len(face['points'])):
                    if type(face['points'][p]) is Vec:
                        face['points'][p]=rotate(face['points'][p]-face['rotate'][0], face['rotate'][1])+ face['rotate'][0]
                    else:
                        face['points'][p].pos = rotate(face['points'][p].pos-face['rotate'][0], face['rotate'][1])+ face['rotate'][0]
                face['origin'] = rotate(face['origin']-face['rotate'][0], face['rotate'][1])+ face['rotate'][0]
                face['x'] = rotate(face['x'], face['rotate'][1])
                if 'good_direction' in face:
                    face['good_direction'] = rotate(face['good_direction'], face['rotate'][1])
                if 'wood_direction' in face:
                    face['wood_direction'] = rotate(face['wood_direction'], face['rotate'][1])
                if 'alt_good_direction' in face:
                    face['alt_good_direction'] = rotate(face['alt_good_direction'], face['rotate'][1])
                if 'alt_wood_direction' in face:
                    face['alt_wood_direction'] = rotate(face['alt_wood_direction'], face['rotate'][1])
            if 'layer' not in face:
                face['layer']='layer_'+f
                self.new_layers.append(f)
            self.preparsePoints(face)
            self.make_sides(f,face['points'])
            self.make_normal(f, face['points'])
            face['internal_joints'] = []
            if 'zoffset' not in face:
                face['zoffset'] = 0
#                       self.check_layer(face)
            if 'tab_length' not in face:
                face['tab_length'] = {}
            if 'joint_mode' not in face:
                face['joint_mode'] = {}
            if 'hole_offset' not in face:
                face['hole_offset'] = {}
            if 'butt_depression' not in face:
                face['butt_depression'] = {}
            if 'butt_holerad' not in face:
                face['butt_holerad'] = {}
            if 'butt_outline' not in face:
                face['butt_outline'] = {}
            if 'butt_numholes' not in face:
                face['butt_numholes'] = {}
            if 'hole_spacing' not in face:
                face['hole_spacing'] = {}
            if 'corners' not in face:
                face['corners'] = {}
            if 'hole_depth' not in face:
                face['hole_depth']=False
            if 'point_type' not in face:
                face['point_type'] = {}
            if 'wood_direction' in face:
  #                              if wood_direction_face is not None or wood_direction_face !=None:
 #                                       raise ValueError('wood direction defined more than once')
#                                wood_direction_face = f
                wood_direction_faces.append(f)
            if 'good_direction' in face:
                   # if good_direction_face is not None or good_direction_face !=None:
                #        raise ValueError('good direction defined more than once')
                   # good_direction_face = f
                good_direction_faces.append(f)
        if len(wood_direction_faces) == 0:
            raise ValueError("No face with wood_direction set")
        if len(good_direction_faces) == 0:
            raise ValueError("No face with good_direction set")

        scount=0
        for s, side in self.sides.items():
            self.find_angle(s, side)
            scount+=1
        # on internal faces you define the good direction the wrong way
        for good_direction_face in good_direction_faces:
            if 'internal' in self.faces[good_direction_face] and self.faces[good_direction_face]['internal']:
                self.faces[good_direction_face]['good_direction'] *= -1
            self.propagate_direction('good_direction', good_direction_face,0)

        for wood_direction_face in wood_direction_faces:
            self.propagate_direction('wood_direction', wood_direction_face,0)
        for s, side in self.sides.items():
            self.set_joint_type(s, side)


        for f, face in faces.items():
            self.get_cut_side(f, face)
#                       face['good_direction'] *= face['cut_from']
            if face['cut_from']<0:
                pass
                face['isback']=True
                face['good_direction'] *= face['cut_from']
        #               face['zoffset'] += face['thickness']
            if 'x' in face:
                if abs(face['x'].dot(face['normal'])) > 0.0000001 :
                    raise ValueError('face[x] direction in face "'+str(f)+'" not in plane of the rest of the face'+str(face['normal']))
                face['x'] = face['x'].normalize()
            else:
                face['x'] = (self.tuple_to_vec(face['sides'][0][1])- self.tuple_to_vec(face['sides'][0][0])).normalize()
            if 'y' in face:
                if abs(face['y'].dot(face['x'])) > 0.0000001 :
                    raise ValueError('face[y] in face '+str(f)+' not perpendicular to x')
                if abs(face['y'].dot(face['normal'])) > 0.0000001 :
                    raise ValueError('face[y] in face '+str(f)+' not in plane of the rest of the face')
            else:
                face['y'] = face['x'].cross(face['normal']).normalize()
            assert face['wood_direction'] in [-1,1]
            assert face['good_direction'] in [-1,1]
            if face['wood_direction'] == face['good_direction']:
                face['x'] *=-1
#                       face['y'] = face['x'].cross(face['normal']).normalize()
            # if we are cutting from the back flip x
#                       if 'isback' in face and face['isback']:
#                               face['y'] *=-1

#                       if face['good_direction'] == -1:
#                                face['x'] = - face['x']


            if 'origin' not in face:
                face['origin'] = face['points'][0]
            face['ppoints'] = []
            for p in face['points']:
                p2 = p-face['origin']
                face['ppoints'].append(V(p2.dot(face['x']), p2.dot(face['y'])))
            face['wdir']=self.find_direction(face['ppoints'])

        # go through unconnected sides and see if they are in the middle of any faces
        for s,side in self.sides.items():
            if len(side)==1:
                self.find_in_face(s,side)


        for f, face in faces.items():
            scount = 0
            for s in face['sides']:
                self.set_corners(self.sides[s], f, scount)
#                               self.set_tab_length(self.sides[s], f, scount)
                self.set_property(self.sides[s], f, scount, 'joint_mode')
                self.set_property(self.sides[s], f, scount, 'tab_length')
                self.set_property(self.sides[s], f, scount, 'butt_depression')
                self.set_property(self.sides[s], f, scount, 'butt_holrad')
                self.set_property(self.sides[s], f, scount, 'butt_numholes')
                self.set_property(self.sides[s], f, scount, 'butt_holerad')
                self.set_property(self.sides[s], f, scount, 'butt_outline')
                self.set_property(self.sides[s], f, scount, 'hole_spacing')
                self.set_property(self.sides[s], f, scount, 'hole_offset')
                scount+=1
            if 'internal' in face and face['internal']:
                face['intfact']=-1
            else:
                face['intfact']=1
            if face['wood_direction'] * face['good_direction']*face['intfact']>0:
                face['lineside']='front'
            else:
                face['lineside']= 'back'


        for f, face in faces.items():

        # if we are cutting an internal hole then don't make it the part border
            if "layer" not in face:
                raise ValueError( "Face "+f+" does not have a layer")
            if 'internal' in face and face['internal']:
                border = Path(closed=True, side='in')

            # add points here

                p = Part(name = self.name+'_'+f, layer = face['layer'], zoffset=face['zoffset'])
                self.get_border(p,  f, face, 'internal')
            else:
                p = Part(name = self.name+'_'+f, layer = face['layer'], zoffset=face['zoffset'])
                self.get_border(p,  f, face, 'external')
#                       if face['y'] == -face['x'].cross(face['normal']).normalize():
#                       if face['good_direction'] == -1:
            # DECIDE WHICH SISDE WE ARE CUttng FROM
            # CHECK THE DIRECTION OF THR LOOP
            t =  self.add(p)
            setattr(self, 'face_' + f, t)
#               def _pre_render(self):
            self.align3d_face(t, f, face)

# find any edges in the middle of other faces
    def find_in_face(self,s,side):
        face1 = self.faces[side[0][0]]
        p1 = face1['points'][ (side[0][1]-1)%len(face1['points']) ]
        p2 = face1['points'][side[0][1]]
        for f, face in self.faces.items():
            if f!= side[0][0]:
                p1a = p1-face['origin']
                p2a = p2-face['origin']
                p1p = V(p1a.dot(face['x']), p1a.dot(face['y']), p1a.dot(face['normal']))
                p2p = V(p2a.dot(face['x']), p2a.dot(face['y']), p2a.dot(face['normal']))
                if abs(p1p[2])<0.05 and abs(p2p[2])<0.05:
                    # we are in plane are we in the face
                    p=Path(closed=True)
                    c=0
                    for point in face['ppoints']:
                        if c in face['point_type']:
                            t=face['point_type'][c]
                            t.pos = point
                        else:
                            t=PSharp(point)
                        p.add_point(t)
                        c+=1
                    poly=p.polygonise(5)

                    if p.contains_point(p1p,poly) and p.contains_point(p2p, poly) and abs(p1p[2])<0.05 and abs(p2p[2])<0.05:
                        self.faces[f]['internal_joints'].append( { 'side':s, 'otherside':side[0], 'from':p1p, 'to':p2p, 'otherface':face1, 'otherf':side[0][0], 'sidedat':side, 'from3D':p1, 'to3D':p2 } )
                        side.append( [ '_internal', f, len(self.faces[f]['internal_joints'])-1 ])
                        self.find_angle(s, side)
        # The edge cross the normal gives you a vector that is in the plane and perpendicular to the edge
        svec1 = (face1['points'][ (side[0][1]-1)%len(face1['points']) ] - face1['points'][side[0][1]]).cross( face1['normal'] ).normalize()



    def align3d_face(self, p, f, face):
#               config = p.get_config()
        if face['wood_direction'] == face['good_direction']:
            flip=1#-face['wood_direction']
        else:
            flip = -1
        z = (face['normal'] * flip).normalize()

        x =  face['x'].normalize()
   #     if face['wdir']=='cw':
    #            flip *=-1
        flip=1
        flipped = 1
        if 'y' in face:
            y=face['y'].normalize()
            if (y-x.cross(z*-1)).length()>0.0001:
                flipped=-1
        else:
            y = x.cross(z*-1)
        #if y has been defined the other way around it all gets a little confused so unconfuse it:
   #     flipxy = y.dot(x.cross(z))
    #    x*=flipxy
 #   y*=flipxy

#               if 'isback' in face:
    #               z *= -1
    #               y *= -1
    #               x *= -1
    #               p.rotate3D([0,0,180])
    #               pass
#               xs = [x[0],x[1],x[2],0]
#               ys = [y[0],y[1],y[2],0]
#               zs = [z[0],z[1],z[2],0]
        xs = [x[0]*flip,y[0]*flip,z[0]*flip,0]
        ys = [x[1],y[1],z[1],0]
        zs = [x[2]*flip,y[2]*flip,z[2]*flip,0]
        qs = [0,0,0,1]
        if face['good_direction']==face['wood_direction'] and face['wood_direction']==1 or p.isback==True:
#                if face['good_direction']==face['wood_direction'] and face['wood_direction']==1:
#               if not ((face['wdir']=='cw')==face['good_direction']==face['wood_direction'] and flipped==-1):
      #          p.isback=True
            if has3D:
                p.border.translate3D([0,0,face['thickness']])
        #        p.rotate3D([0, 180, 0], self.pos)
      #  elif (hasattr(p, 'isback') and p.isback is True):
   #         p.rotate3D([0, 180, 0],self.pos)
        #        p.translate3D([0,0,-face['thickness']])
        if has3D:
            p.matrix3D([xs,ys,zs,qs],self.pos)
            p.translate3D(face['origin'])

    def tuple_to_vec(self, t):
        return V(t[0], t[1], t[2])

    def get_border(self, part, f, face, mode):
        if mode == 'internal':
            path = Path(closed=True, side='in')
        else:
            path = Path(closed=True, side='out')
        simplepath = Path(closed=True, side='on')

        p=0
        first = True
        lastpoly = False
        simplepoints = []
        if self.find_direction(face['ppoints'])=='cw':
            cutside0='left'
        else:
            cutside0='right'
        firstnointersect=False
        for point in face['ppoints']:
            nointersect = False
            lastpoint = face['ppoints'][(p-1)%len(face['sides'])]
            lastlastpoint = face['ppoints'][(p-2)%len(face['sides'])]
            nextpoint = face['ppoints'][(p+1)%len(face['sides'])]
            scount = (p)%len(face['sides'])
            s = face['sides'][scount]
            side = self.sides[s]
            if len(side[0])>2:
                obtuse = side[0][7]
            else:
                obtuse = 0
            lasts = face['sides'][(scount-1)%len(face['sides'])]
            nexts = face['sides'][(scount+1)%len(face['sides'])]
            lastsi = self.sides[lasts]
            nextsi = self.sides[nexts]
            (thisside, otherside) = self.get_side_parts(side, f)
            (nextside, nextotherside) = self.get_side_parts(nextsi, f)
            (lastside, lastotherside) = self.get_side_parts(lastsi, f)
            if otherside!=None and otherside[0]!='_internal':
                otherface = self.faces[otherside[0]]
                otherf = otherside[0]
            elif  otherside!=None and otherside[0]=='_internal':
                otherface = self.faces[otherside[1]]
                otherf = otherside[1]
            else:
                otherface = None
            simplepoints.append(PSharp(point))
            #clear newpoints
            newpoints=[]
            # need to add 2 points here so intersect_points works
            if len(side)==1 or scount in face['point_type'] and face['point_type'][scount].point_type not in  ['sharp', 'insharp', 'clear', 'doubleclear'] :
                newpoints=[]
                if ((p-1)%len(face['sides'])) in face['point_type']:
                    newpoints.append(face['point_type'][(p-1)%len(face['sides'])])
                    newpoints[-1].setPos(lastpoint)
                    if face['point_type'] not in ['sharp', 'insharp', 'clear', 'doubleclear']:
                        nointersect=True
                else:
                    newpoints.append(PInsharp(lastpoint))
                if scount in face['point_type']:
                    newpoints.append(face['point_type'][scount])
                    newpoints[-1].setPos(point)
                else:
                    newpoints.append(PInsharp(point))
#                               newpoints = [PInsharp(lastpoint),PInsharp(point)]
            else:
#                               if mode=='internal':
 #                                      newpoints = [PSharp(point)]

  #                             else:
                angle = thisside[4]
                altside = thisside[5]
                joint_type = thisside[6]
#                                       angle = 15
                if mode == 'internal':
                    corner = self.other_side_mode(face['corners'][scount])
                else:
                    corner = face['corners'][scount]
                lastcorner = face['corners'][(scount-1)%len(face['corners'])]
                nextcorner = face['corners'][(scount+1)%len(face['corners'])]
                if 'fudge' in face:
                    if type(face['fudge']) is dict and scount in face['fudge']:
                        fudge = face['fudge'][scount]
                    elif type(face['fudge']) in [int, float]:
                        fudge = face['fudge']
                    else:
                        fudge = self.fudge
                else:
                    fudge = self.fudge
                if face['joint_mode'][scount]=='straight':
                    newpoints = [PInsharp(lastpoint),PInsharp(point)]
                elif face['joint_mode'][scount]=='mitre':
                    if cutside0=='left' and joint_type=='concave':
                        cutside='right'
                    elif cutside0=='right' and joint_type=='concave':
                        cutside='left'
                    else:
                        cutside=cutside0
                    if nextotherside is None or nextotherside[0]=='_internal':
                        next_offset = 0
                    else:
                        if nextside[6]=='concave' and nextcorner=='off':
                            next_offset = self.faces[nextotherside[0]]['thickness']
                        else:
                            next_offset = 0
                    if lastotherside is None or lastotherside[0]=='_internal':
                        last_offset = 0
                    else:
                        if lastside[6]=='concave' and lastcorner=='off':
                            last_offset = self.faces[lastotherside[0]]['thickness']
                        else:
                            last_offset = 0
                    newpoints = MitreJoint(lastpoint, point, cutside, 'external', corner, corner, face['hole_spacing'][scount], otherface['thickness'], 0,angle, fudge = fudge, joint_type=joint_type, nextcorner=nextcorner, lastcorner=lastcorner, last_offset=last_offset, next_offset=next_offset, lastparallel = self.parallel(lastlastpoint, lastpoint, lastpoint, point), nextparallel = self.parallel(lastpoint, point, point, nextpoint))
#                                                        if corner=='off':
 #                                                               newpoints.insert(0, PInsharp(lastpoint))
                    if corner=='off' and otherside[0]=='_internal':
                        newpoints.append( PInsharp(point))
                elif face['joint_mode'][scount]=='butt':
                    if angle<0.0001:
                        if cutside0=='left' and joint_type=='concave':
                            cutside='right'
                        elif cutside0=='right' and joint_type=='concave':
                            cutside='left'
                        else:
                            cutside = cutside0

                        if nextotherside is None or nextotherside[0]=='_internal':
                            next_offset = 0
                        else:
                            if nextside[6]=='concave' and nextcorner=='off':
                                next_offset = self.faces[nextotherside[0]]['thickness']
                            else:
                                next_offset = 0
                        if lastotherside is None or lastotherside[0]=='_internal':
                            last_offset = 0
                        else:
                            if lastside[6]=='concave' and lastcorner=='off':
                                last_offset = self.faces[lastotherside[0]]['thickness']
                            else:
                                last_offset = 0

                        newpoints = ButtJoint(lastpoint, point, cutside, 'external', corner, corner, face['hole_spacing'][scount], otherface['thickness'], 0, fudge = fudge, butt_depression=face['butt_depression'][scount], butt_holerad=face['butt_holerad'][scount], joint_type=joint_type, hole_offset=face['hole_offset'][scount], nextcorner=nextcorner, lastcorner=lastcorner, last_offset=last_offset, next_offset=next_offset, lastparallel = self.parallel(lastlastpoint, lastpoint, lastpoint, point), nextparallel = self.parallel(lastpoint, point, point, nextpoint))
#                                                        if corner=='off':
 #                                                               newpoints.insert(0, PInsharp(lastpoint))
                        if corner=='off' and otherside[0]=='_internal':
                            newpoints.append( PInsharp(point))
                        if face['cut_from']<0:
                            if  cutside0=='left':
                                cutside= 'right'
                            else:
                                cutside='left'
                        else:
                            cutside=cutside0
                        part.add(ButtJointMid(lastpoint, point, cutside, 'external', corner, corner, face['hole_spacing'][scount], otherface['thickness'], 0, 'on', 'on',  butt_depression=face['butt_depression'][scount], holerad=face['butt_holerad'][scount], butt_numholes=face['butt_numholes'][scount], joint_type=joint_type, fudge=fudge, hole_offset=face['hole_offset'][scount], butt_outline=face['butt_outline'][scount], hole_depth=face['hole_depth']))
                        if not(lastcorner == 'off' and corner=='off'):
                            nointersect==True
                    #               if p==0:
                        #               firstnointersect=True

                    else:
    #                    if face['cut_from']<0:
   #                         if  cutside0=='left':
  #                              cutside= 'right'
 #                           else:
#                                cutside='left'
                        if  self.find_direction(face['ppoints'])=='cw':
                                cutside='left'
                        else:
                                cutside= 'right'

                      #  else:
                       #     cutside=cutside0
                        if nextotherside is None or nextotherside[0]=='_internal':
                            next_offset = 0
                        else:
                            if nextside[6]=='concave' and nextcorner=='off':
                                next_offset = self.faces[nextotherside[0]]['thickness']
                            else:
                                next_offset = 0
                        if lastotherside is None or lastotherside[0]=='_internal':
                            last_offset = 0
                        else:
                            if lastside[6]=='concave' and lastcorner=='off':
                                last_offset = self.faces[lastotherside[0]]['thickness']
                            else:
                                last_offset = 0
                        lineside=face['lineside']
                        print(f+" -> "+otherf+" Angled Butt Joint angle="+str(angle)+" corner="+str(corner))
                        newpoints = AngledButtJoint(
                                lastpoint, 
                                point, 
                                cutside, 
                                'external', 
                                corner, 
                                corner, 
                                face['hole_spacing'][scount], 
                                otherface['thickness'], 
                                0, 
                                fudge = fudge, 
                                butt_depression=face['butt_depression'][scount], 
                                butt_holerad=face['butt_holerad'][scount], 
                                joint_type=joint_type, 
                                hole_offset=face['hole_offset'][scount], 
                                nextcorner=nextcorner, lastcorner=lastcorner, 
                                last_offset=last_offset, 
                                next_offset=next_offset, 
                                lastparallel = self.parallel(lastlastpoint, lastpoint, lastpoint, point), 
                                nextparallel = self.parallel(lastpoint, point, point, nextpoint), 
                                angle=angle, 
                                lineside=lineside,
                                obtuse=obtuse,
                        )
#                                                        if corner=='off':
 #                                                               newpoints.insert(0, PInsharp(lastpoint))
         #               if corner=='off' and otherside[0]=='_internal':
        #                    newpoints.append( PInsharp(point))
       #                 if face['cut_from']<0:
      #                      if  cutside0=='left':
     #                           cutside= 'right'
    #                        else:
   #                             cutside='left'
  #                      else:
 #                           cutside = cutside0
#
   #                     newpoints = AngledButtJoint(
  #                              lastpoint, 
                              ###  point, 
                             #   cutside, 
                            #    'external', 
                           #     corner, 
                          #      corner, 
                         #       face['hole_spacing'][scount], 
                        #        otherface['thickness'], 
                       #         0, 
                      #          fudge = fudge, 
                     #           butt_depression=face['butt_depression'][scount], 
                    #            butt_holerad=face['butt_holerad'][scount], 
                   #             joint_type=joint_type, 
                  #              hole_offset=face['hole_offset'][scount], 
                 #               nextcorner=nextcorner, lastcorner=lastcorner, 
                #                last_offset=last_offset, 
               #                 next_offset=next_offset, 
              #                  lastparallel = self.parallel(lastlastpoint, lastpoint, lastpoint, point), 
             #                   nextparallel = self.parallel(lastpoint, point, point, nextpoint), 
            #                    angle=angle, 
           #                     lineside=lineside
          #              )

                        part.add(AngledButtJointMid(
                                lastpoint, 
                                point, 
                                cutside, 
                                'external', 
                                corner, 
                                corner, 
                                face['hole_spacing'][scount], 
                                otherface['thickness'], 
                                0, 
                                'on', 
                                'on', 
                                angle, 
                                lineside,  
                                butt_depression=face['butt_depression'][scount], 
                                holerad=face['butt_holerad'][scount], 
                                butt_numholes=face['butt_numholes'][scount], 
                                joint_type=joint_type, 
                                fudge=fudge, 
                                hole_offset=face['hole_offset'][scount], 
                                hole_depth=face['hole_depth'],
                                obtuse=obtuse,
                            ))
                        if not(lastcorner == 'off' and corner=='off'):
                            nointersect==True

#                                                        print "WARNING: angled butt joint not handled properly - needs update angle="+str(angle)
 #                                                       newpoints = [PInsharp(lastpoint),PInsharp(point)]
                elif face['joint_mode'][scount]=='bracket':
                    if angle==0:
                        if cutside0=='left' and joint_type=='concave':
                            cutside='right'
                        elif cutside0=='right' and joint_type=='concave':
                            cutside='left'
                        else:
                            cutside=cutside0

                        if nextotherside is None or nextotherside[0]=='_internal':
                            next_offset = 0
                        else:
                            if nextside[6]=='concave' and nextcorner=='off':
                                next_offset = self.faces[nextotherside[0]]['thickness']
                            else:
                                next_offset = 0
                        if lastotherside is None or lastotherside[0]=='_internal':
                            last_offset = 0
                        else:
                            if lastside[6]=='concave' and lastcorner=='off':
                                last_offset = self.faces[lastotherside[0]]['thickness']
                            else:
                                last_offset = 0
                        newpoints = BracketJoint(lastpoint, point, cutside, 'external', corner, corner, face['hole_spacing'][scount], otherface['thickness'], 0, fudge = fudge, butt_depression=face['butt_depression'][scount], butt_holerad=face['butt_holerad'][scount], joint_type=joint_type, hole_offset=face['hole_offset'][scount], nextcorner=nextcorner, lastcorner=lastcorner, last_offset=last_offset, next_offset=next_offset, lastparallel = self.parallel(lastlastpoint, lastpoint, lastpoint, point), nextparallel = self.parallel(lastpoint, point, point, nextpoint))
                        if face['cut_from']<0:
                            if  cutside0=='left':
                                cutside= 'right'
                            else:
                                cutside='left'
                        else:
                            cutside = cutside0
                        part.add(BracketJointHoles(lastpoint, point, cutside, 'external', corner, corner, face['hole_spacing'][scount], otherface['thickness'], 0, 'on', 'on',  butt_depression=face['butt_depression'][scount], butt_holerad=face['butt_holerad'][scount], butt_numholes=face['butt_numholes'][scount], joint_type=joint_type, fudge=fudge, hole_offset=face['hole_offset'][scount], bracket=self.config['bracket'], args=self.config['bracket_args'], wood_direction=face['wood_direction']))
                        if not(lastcorner == 'off' and corner=='off'):
                            nointersect==True
                    #               if p==0:
                        #               firstnointersect=True

                    else:
                        print("WARNING: angled butt joint not handled properly - needs update")
                        newpoints = [PInsharp(lastpoint),PInsharp(point)]
                else:


                    if angle!=0:
                        # this is being cut from the side we are cutting:

                        lineside=face['lineside']
                        if cutside0=='left' and joint_type=='concave':
                            cutside='right'
                        elif cutside0=='right' and joint_type=='concave':
                            cutside='left'
                        else:
                            cutside=cutside0

                        if thisside[3]*face['good_direction']*face['intfact']<0:
# THIS PUTS THE SLOPE ON THE WRONG PART OF THE JOINT
# create a new mode in finger joints called int and have it behave properly
                            newpoints = AngledFingerJoint(lastpoint, point, cutside, mode, corner, corner, face['tab_length'][scount], otherface['thickness'], 0, angle, lineside, fudge, material_thickness=face['thickness'])
                            part.add( AngledFingerJointSlope(lastpoint, point, cutside, mode, corner, corner, face['tab_length'][scount], otherface['thickness'], 3.17/2, angle, lineside, fudge, material_thickness=face['thickness']))
                        else:
                            newpoints = AngledFingerJointNoSlope(lastpoint, point, cutside, mode, corner, corner, face['tab_length'][scount], otherface['thickness'], 0, angle, lineside, fudge, material_thickness=face['thickness'])
                    else:
                        if cutside0=='left' and joint_type=='concave':
                            cutside='right'
                        elif cutside0=='right' and joint_type=='concave':
                            cutside='left'
                        else:
                            cutside=cutside0
                        newpoints = FingerJoint(
                                lastpoint,
                                point,
                                cutside,
                                'internal' if joint_type=='concave' else 'external',
                                corner,
                                corner,
                                face['tab_length'][scount],
                                face['thickness'],
                                0, fudge,
                                nextcorner=nextcorner,
                                lastcorner=lastcorner)
            if first or len(newpoints)<2 or nointersect:
                first = False
                path.add_points(newpoints)
            else:
                path.add_points_intersect(newpoints)
            p += 1
        if len(newpoints) >1 and not firstnointersect:
            path.close_intersect()
        simplepath.add_points(simplepoints)
        path.simplify_points()

 #      part.add(simplepath)
        if mode=='internal':
            part.add(path)
        else:
            part.add_border(path)
        part.tag = self.name+"_"+f
    # iterate through the internal joints
        for joint in face['internal_joints']:
            if (joint['to3D']-joint['from3D']).cross( joint['otherface']['normal']*joint['otherface']['wood_direction']).dot(face['normal']) >0:
                cutside='right'
            else:
                cutside='left'
            if 'isback' in face and face['isback']:
                if  cutside=='left':
                    cutside= 'right'
                else:
                    cutside='left'
            if 'force_swap_internal' in face and face['force_swap_internal']:
                if  cutside=='left':
                    cutside= 'right'
                else:
                    cutside='left'
            if('fudge' in joint['otherface']):
                if type(joint['otherface']['fudge']) is dict and joint['sidedat'][0][1] in joint['otherface']['fudge']:
                    fudge = joint['otherface']['fudge'][joint['sidedat'][0][1]]
                elif type(joint['otherface']['fudge']) in [int, float]:
                    fudge = joint['otherface']['fudge']
                else:
                    fudge = self.fudge
            else:
                fudge = self.fudge

            prevmode = 'on'
            nextmode = 'on'
            if 'joint_mode' not in joint:
                joint['joint_mode']='straight'
            if joint['joint_mode']=='straight':
                pass
            elif joint['joint_mode']=='butt':
                pass
                part.add(ButtJointMid(joint['from'], joint['to'], cutside, 'external', joint['corners'], joint['corners'], joint['hole_spacing'],  joint['otherface']['thickness'], 0, 'on', 'on',  butt_depression=joint['butt_depression'], holerad=joint['butt_holerad'], butt_numholes=joint['butt_numholes'], joint_type='convex', fudge=fudge, butt_outline=joint['butt_outline'], hole_depth=face['hole_depth']))
            elif joint['joint_mode']=='bracket':
                part.add(BracketJointHoles(
                        joint['from'],
                        joint['to'],
                        cutside,
                        'external',
                        corner,
                        corner,
                        joint['hole_spacing'],
                        joint['otherface']['thickness'],
                        0, 'on', 'on',
                        butt_depression=joint['butt_depression'],
                        butt_holerad=joint['butt_holerad'],
                        butt_numholes=joint['butt_numholes'],
                        joint_type=joint_type,
                        fudge=fudge,
                        hole_offset=joint['hole_offset'],
                        bracket=self.config['bracket'],
                        args=self.config['bracket_args']))
            else:
                part.add(FingerJointMid( joint['from'], joint['to'], cutside,'internal',  joint['corners'], joint['corners'], joint['tab_length'], joint['otherface']['thickness'], 0, prevmode, nextmode, fudge=fudge))
    def set_wood_factor(self, face):
        if face['wood_direction'].dot(face['normal'])>0:
            face['wood_factor']=1
        else:
            face['wood_factor']=-1

    def parallel(self, p0,p1, p2,p3):
        if abs((p1-p0).normalize().dot((p3-p2).normalize())-1)<0.00001:
            return True
        else:
            return False


    def find_direction(self, points):
        total = 0
        for p,q in enumerate(points):
            total+=(points[p]-points[(p-1)%len(points)]).normalize().cross((points[(p+1)%len(points)]-points[p]).normalize())
        # if it is a circle
        if total[2] ==0:
            print("side doesn't have a direction")
        elif(total[2]>0):
            return 'ccw'
        else:
            return 'cw'


    def get_side_parts(self, side, f):
        if len(side)==1:
            return (side[0], None)
        if side[0][0]==f:
            thisside= side[0]
            otherside = side[1]
        else:
            thisside = side[1]
            otherside = side[0]
        return (thisside, otherside)

    def get_cut_side(self, f, face):
        if 'force_cut_direction' in face:
            assert face['force_cut_direction'].dot(face['normal'])!=0, "force_cut_direction for face "+f+" is parallel with face"
            if face['force_cut_direction'].dot(face['normal'])>0:
                face['cut_from'] = 1
            else:
                face['cut_from'] = -1
            return
        if 'wood_direction' not in face:
            raise ValueError("wood_direction not in face "+f)
        good_direction = face['wood_direction']
        need_cut_from={}
        pref_cut_from = False
        for s in face['sides']:
            side = self.sides[s]
            if side[0][0]==f:
                thisside= side[0]
            else:
                thisside = side[1]
            # make sure this side is a joint
            if len(thisside)>2:
                cutside = thisside[3]
                if cutside * good_direction>0.0001:
                    need_cut_from[self.sign(cutside)]=True
                elif cutside!=0:
                    pref_cut_from = self.sign(cutside)

                # this means we should be cutting from this side
        if len(need_cut_from)>1:
            raise ValueError(str(f) + " cannot be cut without cavities as slopes can only be cut from one side ")
        elif len(need_cut_from)>0:
            face['cut_from'] = need_cut_from[list(need_cut_from.keys())[0]]
        elif pref_cut_from is not False:
            face['cut_from'] = pref_cut_from
        else:
            face['cut_from'] = 1

    def sign(self, val):
        if val>0:
            return 1
        elif val<0:
            return -1
        else:
            return 0

# t - type of direction - face key
# f - face that has it to start with
    def propagate_direction(self, t, f, recursion):
        face = self.faces[f]
        if recursion==0:
            if face[t].dot(face['normal'])>0:
                face[t]=1
            elif face[t].dot(face['normal'])<0:
                face[t]=-1
            else:
                raise ValueError(t+" in "+f+"is perpendicular to the normal")
        recursion += 1
        print ("############ propogate face:"+str(f))
        for s in face['sides']:
            side = self.sides[s]
            print(str(s)+" -> "+str(side))
            if(len(side)>1):
                if side[0][0]==f:
                    newf = side[1][0]
                    d = side[0][2]
                else:
                    newf = side[0][0]
                    d = side[1][2]

                newface = self.faces[newf]
                if t not in newface:
                    self.faces[newf][t] = d * face[t]
                    self.propagate_direction(t, newf, recursion)
        for f in self.faces:
            if t not in self.faces[f] and 'alt_'+t in self.faces[f]:
                if self.faces[f]['alt_'+t].dot(self.faces[f]['normal'])>0:
                    self.faces[f][t]=1
                else:
                    self.faces[f][t]=-1

    def set_corners(self, side, f, scount):
        face = self.faces[f]
        if len(side)==0:
            raise ValueError( "Side "+str(side)+" has no values")
        elif len(side) ==1:
            face['corners'][scount] = 'straight'
        else:
            if side[1][0]=='_internal':
                otherf = side[1][1]
                otherIJ = side[1][2]
                intJoint = self.faces[otherf]['internal_joints'][otherIJ]
                if scount in face['corners']:
                    intJoint['corners'] = self.other_side_mode(face['corners'][scount])
                    pass
                else:
                    face['corners'][scount] = 'on'
                    intJoint['corners'] = 'off'
                return


            if side[0][0]==f:
                otherf = side[1][0]
                otherscount = side[1][1]
            else:
                otherf = side[0][0]
                otherscount = side[0][1]
            otherface = self.faces[otherf]
            if scount in face['corners'] and otherscount  in otherface['corners']:
                if face['corners'][scount]==otherface['corners'][otherscount] and face['corners'][scount]!='straight':
                    raise ValueError( "side "+str(scount)+" in face "+str(f)+" and side "+str(otherscount)+" in face "+str(otherf)+" have same corners setting, but are the same side"+str(face['corners'][scount])+" "+str(otherface['corners'][otherscount]))
            elif scount in face['corners']:
                otherface['corners'][otherscount] = self.other_side_mode(face['corners'][scount])
            elif otherscount in otherface['corners']:
                face['corners'][scount] = self.other_side_mode(otherface['corners'][otherscount])
            else:
                face['corners'][scount] = 'off'
                otherface['corners'][otherscount] = 'on'

    def set_property(self, side, f, scount, prop):
        face = self.faces[f]
        fprop = None
        if prop not in face:
            face[prop] = {}
        elif  type(face[prop]) is not dict:
            fprop = face[prop]
            face[prop] = {}
        if len(side)==0:
            raise ValueError( "Side "+str(side)+" has no values")
        elif len(side) ==1:
            if prop=="joint_mode":
                face[prop][scount] = 'straight'
        else:
            if prop not in face:
                face[prop]={}
            if side[1][0]=='_internal':
                otherf = side[1][1]
                otherIJ = side[1][2]
                intJoint = self.faces[otherf]['internal_joints'][otherIJ]
                if scount in face[prop]:
                    intJoint[prop] = face[prop][scount]
                elif fprop != None:
                    face[prop][scount]=fprop
                    intJoint[prop] = fprop
                elif hasattr(self, prop):
                    face[prop][scount]=getattr(self,prop)
                    intJoint[prop] = getattr(self,prop)
                else:
                    face[prop][scount]=None
                    intJoint[prop] = None
                return
            if side[0][0]==f:
                otherf = side[1][0]
                otherscount = side[1][1]
            else:
                otherf = side[0][0]
                otherscount = side[0][1]
            otherface = self.faces[otherf]
            if prop not in otherface:
                otherface[prop]={}
            if scount in face[prop] and otherscount in otherface[prop]:
                if face[prop][scount]!=otherface[prop][otherscount]:
                    raise ValueError("side "+str(scount)+" in face "+str(f)+" and side "+str(otherscount)+" in face "+str(otherf)+" have different "+prop+"s, but are the same side"+str(face[prop][scount])+" "+str(otherface[prop][otherscount]))
            elif scount in face[prop]:
                otherface[prop][otherscount]=face[prop][scount]
            elif type(otherface[prop]) is not dict:
                raise ValueError( str(prop)+" in face "+otherf+"must be of the form {0:[value_side_0], 1:[value_side1]}" +str(type(otherface[prop])) )
            elif otherscount in otherface[prop]:
                face[prop][scount]=otherface[prop][otherscount]
            elif fprop != None:
                face[prop][scount]=fprop
                otherface[prop][otherscount]=fprop
            elif hasattr(self, prop):
                face[prop][scount]=getattr(self,prop)
                otherface[prop][otherscount]=getattr(self, prop)
            else:
                face[prop][scount]=None
                otherface[prop][otherscount]=None

    def other_side_mode(self, mode):
        if mode=='on':
            return 'off'
        else:
            return 'on'

    def make_normal(self, f, points):
        normal = False
        p = 0
        normalsum = V(0,0,0)
        for point in points:
            nextpoint = points[(p+1)%len(points)]
            lastpoint = points[(p-1)%len(points)]
            normalsum+= (lastpoint-point).cross( nextpoint-point)
            new_normal = (lastpoint-point).normalize().cross( nextpoint-point).normalize()
            if type(normal) is bool and normal == False:
                normal = new_normal.normalize()
            elif abs(abs((normal.dot(new_normal.normalize()))))-1 > 0.00001: #and normal.normalize() != - new_normal.normalize():
                raise ValueError( "points in face "+f+" are not in a plane "+str(points) )
            p += 1
        normal=normalsum.normalize()
        if 'origin' in self.faces[f]:
            o = self.faces[f]['origin']
            p = points[0]
            p2 = points[1]
            new_normal = (p-o).normalize().cross( (p2-o).normalize() ).normalize()
            #if new_normal.length()>0.00001:# and
            if (abs(new_normal.dot(normal)) < 0.99999) and (new_normal.length()>0.00001):
                raise ValueError( "origin of face "+f+" are not in a plane origin="+str(o)+ "  points="+str(points) +" normal="+str(normal) + " new_normal="+str(new_normal) )
        self.faces[f]['normal']=normal

    def get_sid(self, p1, p2):
        # if the points are the same to n dp they treat them as the same
        ndp = 3
        r1 = V(round(p1[0],ndp), round(p1[1],ndp), round(p1[2],ndp))
        r2 = V(round(p2[0],ndp), round(p2[1],ndp), round(p2[2],ndp))

        # have an arbitrary but repeatable way of ordering the two edges to produce a name which is the same in either direction
        if str(r1)>str(r2):
            return str((r1, r2))
        else:
            return str((r2, r1))

    def make_sides(self, f, points):
        self.faces[f]['sides'] = []
        p =0
        for point in points:
            sval = [f, p]
            sid = self.get_sid(point, points[(p-1)%len(points)])
            if sid in self.sides:
                self.sides[sid].append(sval)
            else:
                self.sides[sid] = [sval]
            self.faces[f]['sides'].append(sid)
            p+=1

        if len(self.sides[sid]) > 2:
            print(self.sides[sid])
            raise ValueError("more than 2 faces with the same side "+str(self.sides[sid]))

    def set_joint_type(self, s, side):
        face1 = self.faces[side[0][0]]
        if len(side)==1:
            return False
        elif side[1][0]=='_internal':
            joint_type='convex'
        else:
            face2 = self.faces[side[1][0]]
            edge1 = face1['points'][ (side[0][1]-1)%len(face1['points']) ] - face1['points'][side[0][1]]
            edge2 = face2['points'][ (side[1][1]-1)%len(face2['points']) ] - face2['points'][side[1][1]]
            svec1 = edge1.cross( face1['normal'] ).normalize()
            svec2 = edge2.cross( face2['normal'] ).normalize()
            if (svec1+svec2).length()*5 >   (svec1 * 5 + face1['normal']*face1['wood_direction'] + svec2 * 5 + face2['normal']*face2['wood_direction']).length():
                joint_type='concave'
            else:
                joint_type='convex'
        side[0][6] = joint_type
        if len(side)>1:
            side[1][6] = joint_type


    def find_angle(self, s,side):
        if len(side)!=2:
#                       print "side with only one face"
            return False
        face1 = self.faces[side[0][0]]
        internal=False

        if side[1][0]=='_internal':
            face2 = self.faces[side[1][1]]
            internal=True
        #       intJoint = self.faces['internal_joints'][side[1][2]]
            svec2 = (face1['points'][ (side[0][1]-1)%len(face1['points']) ] - face1['points'][side[0][1]]).cross( face2['normal']).normalize()
            scount2 = None #side[1][2]
        else:
            face2 = self.faces[side[1][0]]
        # The edge cross the normal gives you a vector that is in the plane and perpendicular to the edge
            svec2 = (face2['points'][ (side[1][1]-1)%len(face2['points']) ] - face2['points'][side[1][1]]).cross( face2['normal'] ).normalize()
            scount2 = side[1][1]

        svec1 = (face1['points'][ (side[0][1]-1)%len(face1['points']) ] - face1['points'][side[0][1]]).cross( face1['normal'] ).normalize()
        scount1 = side[0][1]

        # base angle is angle between the two svecs
        ac = min(1,max(-1,svec1.normalize().dot(svec2.normalize())))
        baseAngle = math.acos(ac) / math.pi *180#svec1.normalize().dot(svec2.normalize())) / math.pi *180
        if baseAngle < 45:
            cutsign = -1
            altside = -1
            angle = 90-abs(baseAngle)
        elif baseAngle < 90:
            altside = -1
            cutsign = -1
            angle = abs(90-baseAngle)
        elif baseAngle==90:
            altside = 1
            cutsign = 0
            angle =0
        elif baseAngle <135:
            altside = 1
            cutsign = 1
            angle = abs(baseAngle-90)
        else:
            altside = 1
            cutsign = 1
            angle = abs(180-baseAngle)
        # if this is +ve cut on same side as positive normal otherwse opposite direction to normal
        avSvec = (svec1 + svec2).normalize()

        # if you start a distance away from the joint and follow the normal, if they are coming together the going is internal, otherwise it is external
        # Is the normal of both faces in the same directions vs inside and outside
        # will only break with zero if  if planes are parallel
        t = face1['normal'].dot(avSvec) * avSvec.dot(face2['normal'] )
        if t>0:
            sideSign = 1
        elif t<0:
            sideSign = -1
        else:
#                        print ValueError( " Two adjoinig faces are parallel "+str(side[0][0])+" "+str(side[0][1])+" and "+ str(side[1][0])+" "+str(side[1][1])+" avSvec="+str(avSvec)+str(face1['normal'])+" == "+str(face2['normal']))
            face1['corners'][scount1] = 'straight'
            if scount2 is not None:
                face2['corners'][scount2] = 'straight'
            sideSign = 0

        # is the joint acute or obtuse
        if(svec1.dot(svec2)<0):
            obtuse=1
        elif( svec1.dot(svec2)>0):
            obtuse=-1
        else:
            obtuse=0
        print ("svec dot svec"+str(svec1.dot(svec2))+" obtuse="+str(obtuse))
        side[0].append(sideSign)
        side[0].append( avSvec.dot ( face1['normal'] ) * cutsign)
        side[0].append( angle )
        side[0].append(altside)
        side[0].append('convex')
        side[0].append(obtuse)

        side[1].append(sideSign)
        side[1].append( avSvec.dot ( face2['normal'] ) * cutsign)
        side[1].append( angle )
        side[1].append(altside)
        side[1].append('convex')
        side[1].append(obtuse)

    def preparsePoints(self, face):
        p=0
        if 'point_type' not in face:
            face['point_type']={}
        for pnt in face['points']:
            if type(pnt) is not Vec:
                try:
                    pnt.pos
                except ValueError:
                    raise ValueError("Point "+str(pnt)+" in face "+str(face)+" must be either a Vec or a Point type")
                face['point_type'][p]=pnt
                face['points'][p]=pnt.pos
            p+=1
    def _pre_render(self, config):
        for f in self.new_layers:
            self.get_plane().add_layer(self.faces[f]['layer'], material=self.get_layer_attrib('material',f), thickness=self.get_layer_attrib('thickness',f), colour=self.get_layer_attrib('colour',f))
    def get_layer_attrib(self, attrib, face):
        if attrib in self.faces[face]:
            return self.faces[face][attrib]
        elif hasattr( self, attrib):
            return getattr(self, attrib)
        else:
            return False

# functions for finding plane intersections
    def plane_intersection_line(self, o1, n1, o2,n2):
        intersection_normal = n1.cross(n2)
        det = intersection_normal.length()**2
        if det < 0.001:
            return False, False
        intersection_origin = (intersection_normal.cross(n2)*o1.length() + n1.cross(intersection_normal)*o2.length())/det
        return intersection_origin, intersection_normal

    def face_intersection_line(self, face1, face2):
        return plane_intersection_line(face1.origin, face1.normal, face2, face2.normal )

# need to find the projection of the intersection line from face f1 on f2 and vice versa
# if these aren't contained then return false
# if not we need to find out entry and leaving points of the intersection in both faces
# return these points and which face they cross

    def face_intersection(self, f1, f2):
        face1 = self.faces[f1]
        face2 = self.faces[f2]
        intersection_origin, intersection_normal = self.face_intersection_line(face1, face2)
        if intersection_origin is False:
            return False
        # resolve intersection onto 2 faces
        intersection_origin_f1 = V((intersection_origin-face1.origin).dot(face1.x), (intersection_origin-face1.origin).dot(face1.y))
        intersection_line_f1 = V(intersection_normal.dot(face1.x), intersection_normal.dot(face1.y))
        t1 = Path()
        t1.add_points(intersection_origin_f1-1000*intersection_line_f1, intersection_origin_f1+1000*intersection_line_f1)
        if(face1.border.contains(t1)>-1):

            intersection_origin_f2 = V((intersection_origin-face1.origin).dot(face2.x), (intersection_origin-face1.origin)).dot(face2.y)
            intersection_line_f2 = V(intersection_normal.dot(face2.x), intersection_normal.dot(face2.y))
            t2 = Path()
            t2.add_points(intersection_origin_f2-1000*intersection_line_f2, intersection_origin_f2+1000*intersection_line_f2)
            if(face2.border.contains(t2)>-1):
                return True

    def line_intersect_face(self, face, line):
        # project line onto face
        line2D = [ V(line[0].dot(face['x']), line[0].dot(face['y'])), 
                V(line[1].dot(face['x']), line[1].dot(face['y'])) ]
        intersections=[]
        for p in range(0, len(face['ppoints'])):
            intersections.append([p, Path.intersects(False, line2D, [face['ppoints'][(p-1)%len(face['ppoints'])],face['ppoints'][p]])])
        return intersections



class PlainBox2(ArbitraryBox):
    def __init__(self, pos, name, layers, width, height, depth, thickness, tab_length, **config):
        self.init(config)
        all_layers = ['top', 'bottom', 'left', 'right', 'front', 'back']
        self.new_layers = []
        self.thickness = thickness
        if 'material' in config:
            self.material = config['material']
        else:
            self.material = 'plywood'
        if 'fudge' in config:
            fudge = config['fudge']
        else:
            fudge = 0
        for l in all_layers:
            if l not in layers:
                self.new_layers.append(name+'_'+l)
                layers[l]=name+'_'+l
        n = name+"_"
        faces={
                'front':{
                        'points':[V(-width/2, -height/2, depth), V(width/2, -height/2, depth), V( width/2, height/2, depth), V(-width/2, height/2, depth)],
                        'face2num':{'left':0, 'bottom':1,'right':2, 'top':3, },
                        'x':V(1,0,0),
                        'origin':V(0,0,depth),
                        'layer':layers['front'],
                        'thickness':thickness,
                        'internal':False,
                        'corners':{0:'off', 1:'off',2:'off', 3:'off'},
                        'good_direction':V(0,0,1),
                        'wood_direction':V(0,0,1),
                },
                'back':{
                        'points':[V(-width/2, -height/2, 0), V(width/2, -height/2, 0), V( width/2, height/2, 0), V(-width/2, height/2, 0)],
                        'face2num':{'left':0, 'bottom':1,'right':2, 'top':3, },
                        'x':V(1,0,0),
                        'origin':V(0,0,0),
                        'layer':layers['back'],
                        'thickness':thickness,
                        'internal':False,
                        'corners':{0:'off', 1:'off',2:'off', 3:'off'},
                },
                'bottom':{
                        'points':[V(-width/2, -height/2, 0), V(-width/2, -height/2, depth), V( width/2, -height/2, depth), V(width/2, -height/2, 0)],
                        'face2num':{'left':0, 'front':1,'right':2, 'back':3, },
                        'x':V(1,0,0),
                        'origin':V(0,-height/2,0),
                        'layer':layers['bottom'],
                        'thickness':thickness,
                        'internal':False,
                },
                'top':{
                        'points':[V(-width/2, height/2, 0), V(-width/2, height/2, depth), V( width/2, height/2, depth), V(width/2, height/2, 0)],
                        'face2num':{'left':0, 'front':1,'right':2, 'back':3, },
                        'x':V(1,0,0),
                        'origin':V(0,height/2,0),
                        'layer':layers['top'],
                        'thickness':thickness,
                        'internal':False,
                },
                'left':{
                        'points':[V(-width/2, -height/2, 0), V(-width/2, -height/2, depth), V( -width/2, height/2, depth), V(-width/2, height/2, 0)],
                        'face2num':{'bottom':3, 'front':0,'top':1, 'back':2, },
                        'x':V(0,1,0),
                        'origin':V(-width/2,0,0),
                        'layer':layers['left'],
                        'thickness':thickness,
                        'internal':False,
                        'corners':{0:'on', 1:'on',2:'on', 3:'on'},
                },
                'right':{
                        'points':[V( width/2, -height/2, 0), V( width/2, -height/2, depth), V(  width/2, height/2, depth), V(width/2, height/2, 0)],
                        'face2num':{'bottom':3, 'front':0,'top':1, 'back':2, },
                        'x':V(0,1,0),
                        'origin':V( width/2,0,0),
                        'layer':layers['right'],
                        'thickness':thickness,
                        'internal':False,
                        'corners':{0:'on', 1:'on',2:'on', 3:'on'},
                },
        }
        if 'cornermodes' in config:
            assert type(config['cornermodes']) is dict
            for m in config['cornermodes']:
                if 'corners' not in faces[m[0]]:
                    faces[m[0]]['corners']={}
                if 'corners' not in faces[m[1]]:
                    faces[m[1]]['corners']={}
                faces[m[0]]['corners'][faces[m[0]]['face2num'][m[1]]] = config['cornermodes'][m]
                faces[m[1]]['corners'][faces[m[1]]['face2num'][m[0]]] = self.other_side_mode(config['cornermodes'][m])
        else:
            cornermodes = {}
        if 'facemodes' in config:
            facemodes = config['facemodes']
        else:
            facemodes = {}
        config['pos'] = pos
        config['name'] = name
        self.make_box(faces, tab_length, fudge, **config)
