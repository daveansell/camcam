plane = camcam.add_plane(Plane('xy', cutter='1/8_endmill'))
plane.add_layer('test', material = 'pvc', thickness = 6)

ratchet=plane.add(Part(name = 'ratchet0', layer='test', border=SubCircle(V(50,0), rad = 50, yoff=10)))
ratchet=plane.add(Part(name = 'ratchet1', layer='test', border=Circle(V(0,0), rad = 80, yoff=20)))
