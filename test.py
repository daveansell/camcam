

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



top=box.add_path(Part(name='top', layer='top'))
top.add_path(Circle(V(0,0), cornertype="outcurve", rad=50, side='out', centred=True),'top')
#top.add_path(Polygon(V(0,0), 40, 3, 'outcurve', 10))

#bottom_border=Path(closed=True, side='out')
#bottom_border.add_point(V(0,0), radius=50, point_type='outcurve')
#bottom_border.add_point(V(60,1), radius=5, point_type='outcurve')
#bottom_border.add_point(V(60,-1), radius=5, point_type='outcurve')


#top.add_path(bottom_border)

#b2= copy.deepcopy(bottom_border)
#b2.rotate(V(50,0),180)
#top.add_path(b2,'top')
