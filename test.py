

top_thickness=12
mid_thickness=12
bottom_thickness=4
perspex_thickness=3
perspex_z=-2
corner_rad=10

width=110
height=110
lip=3

magnet_offset=10
magnet_rad=8.2/2
magnet_screw_rad=2.5/2

window_width=70
window_height=40

#side border is the slide left either side of the void in the middle
side_border=15

box = camcam.add_plane(Plane('box', cutter='1/8_endmill'))

Ltop=box.add_layer('top', material='pvc', thickness=top_thickness, z0=0, zoffset=0, isback=True)
Lmid=box.add_layer('mid', material='pvc', thickness=mid_thickness, z0=0, zoffset=-top_thickness, isback=False)
Lbot=box.add_layer('bottom', material='pvc', thickness=bottom_thickness, z0=0, zoffset=-top_thickness-mid_thickness, isback=False)
Lperspex=box.add_layer('top', material='perspex', thickness=perspex_thickness, z0=0, zoffset=perspex_z)



top=box.add_path(Part(name='top', border=RoundedRect(V(0,0), width=width+2*lip, height=height+2*lip, rad=corner_rad+lip, side='out', centred=True), layer='top'))
top.add_path(ClearRect(V(0,0), width=width-20, height=height-20, rad=corner_rad+lip, side='in', centred=True),'top')


