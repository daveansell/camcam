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
from boxes import *
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
