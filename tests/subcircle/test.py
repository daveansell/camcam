plane = camcam.add_plane(Plane('xy', cutter='1/8_endmill'))
plane.add_layer('test', material = 'pvc', thickness = 6)
ratchet=plane.add(Part(name = 'ratchet', layer='test', border=SubCircle(V(0,0), rad = 25, yoff=1)))
ratchet.add(SubCircle(V(0,0), rad = 18, yoff=6, side='in'))

