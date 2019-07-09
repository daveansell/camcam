
# rectangle with 4 holes

# variables we might want to edit later
width=300
height=200
from_edge=10
centre=V(0,0)
side_rad=50
# add plane - xy is standard
# main class = camcam
# This is adding to camcam
# camcam understands planes - longer term is to add multiple planes - at the moment is has the xy plane - this contains the parts and layers
# layer has: thickness, material, and a z-offset from plane at z-zero (ignored at moment)
# part exists in it's own layer, and can modify other layers (ie part through top of baseboard will cut perspex). Multiple parts can exsist in the same layer. If you don't need to print it, it doesn't need to have its own layer e.g. a stepper motor is not something we can cut (yet), so it just needs to make holes in the layers it's mounted to or going through.
#
# camcam/path.py defines: planes, parts, path groups & paths & points, layers [core concepts]
# camcam/shapes.py defines: shapes (e.g. circles, holes, screws, bolts, polygons & modules
# camcam/parts.py defines: stepper  motors, inserts
# camcam/Milling.py defines: cutting modes (e.g. diagram, makespacerouter, laser...), bolt sizes, insert sizes, tools & materials [essentially a config files]


# add plane

plane = camcam.add_plane(Plane('xy', cutter='1/8_endmill'))

# add layer

plane.add_layer('layer_name', 'plywood', 9)



plate_border = RoundedRect(V(0,0), width=width, height=height, rad=10, centred=True)

plate = plane.add(Part(name='ring', layer= 'layer_name', border = plate_border))


plate.add(Hole(V(width/4, height/4), rad=4))
plate.rotate(V(0,0), 45)
