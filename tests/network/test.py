from network import *

plane = camcam.add_plane(Plane('xy', cutter='1/8_endmill'))

#net=Network(13.0, intRadius=0)
net=Network(13.0, intRadius=3)
n0 = net.add(Node(V(0,0), radius=12.0))
n1 = net.add(Node(V(100,0), radius=12.0))
n1.add_conn(n0, noCutout='left')
n2 = net.add(Node(V(0,100), radius=12.0))
n2.add_conn(n0)
n2.add_conn(n1)
n3 = net.add(Node(V(-100,0), radius=12.0))
n3.add_conn(n0)
n3.add_conn(n2)
n4 = net.add(Node(V(0,-100), radius=12.0))
n4.add_conn(n0)
n4.add_conn(n3)
n4.add_conn(n1)

net.make_paths()

plane.add_layer('test', material = 'plywood', thickness = 6)
plane.add(NetworkPart(net, name='test', layer='test'))
