from solid import *
import sys
sys.path.append("../../../camcam/")
import kicad
"""
width = 90
height = 60
depth = 55

thickness =1.5

outerrad =2

innerWidth = width -thickness*2
innerHeight = height -thickness*2
innerRad =outerrad -thickness 
#cutz=depth/2-outerrad
cutz=-depth/2+26+10

screwFromEdge = 6

pcbScrewLength = 8
pcbScrewCylinderRad = 5.0/2
pcbScrewThreadRad = 3.3/2
     
screwPoses = [
        
        [-width/2+screwFromEdge,-height/2+screwFromEdge],
        [ width/2-screwFromEdge,-height/2+screwFromEdge],
        [ width/2-screwFromEdge, height/2-screwFromEdge],
        [-width/2+screwFromEdge, height/2-screwFromEdge],
        ]
        
screwCylinderRad = 5.0
screwThreadRad = 3.3/2
screwRad = 4.5/2
screwHeadRad = 8.4/2
overlap = 3
mountingEars = { 'left':{'length':10}, 'right':{'length':10}}

earThickness = 3.0#thickness*1.5
edge=2.5

holePoses = {
        'front':[], 
        'back':[
            {'pos':V(0,0), 'shape':'rect', 'rad':3.5, 'width':20.0, 'height':27.7 },
            {'pos':V(0,20.0), 'shape':'pillar', 'from':'out', 'rad':2.5/2, 'pillarRad':6.0/2, 'length':10},
            {'pos':V(0,-20.0), 'shape':'pillar', 'from':'out', 'rad':2.5/2, 'pillarRad':6.0/2, 'length':10},
            ], 
        'left':[
            {'pos':V(0,-depth/2+17+earThickness,0), 'shape':'circle', 'rad':20.0/2},
            ], 
        'right':[
            {'pos':V(0,-depth/2+17+earThickness,0), 'shape':'circle', 'rad':20.0/2},
            ], 
        'top':[], 
        'bottom':[]
        }
pcbs = {'top':[], 'bottom':[], 'left':[], 'right':[], 'front':[], 'back':[]}
"""
try:
    extraSolids
except:
    extraSolids = []

try:
    extraHoles
except:
    extraHoles = []



faces = {
        'front' :[{'rotate3D':[[0,0,0], V(0,0,0)]},{'translate3D':V(0,0,depth/2+1)}],
        'back'  :[{'rotate3D':[[0,0,0], V(0,0,0)]},{'translate3D':V(0,0,-depth/2+1)}],
        'left'  :[{'rotate3D':[[90,0,90], V(0,0,0)]},{'translate3D':V(-width/2+1,0,0)}],
        'right' :[{'rotate3D':[[90,0,-90], V(0,0,0)]},{'translate3D':V( width/2-1,0,0)}],
        'top'   :[{'rotate3D':[[0,90,90], V(0,0,0)]},{'rotate3D':[[0,90,0], V(0,0,0)]},{'translate3D':V( 0,height/2+1,0)}],
        'bottom':[{'rotate3D':[[0,90,-90], V(0,0,0)]},{'rotate3D':[[0,90,0], V(0,0,0)]},{'translate3D':V( 0,-height/2-1,0)}],
        }
earEdges = ['left', 'right', 'top', 'bottom']
defaultEar = {'length':12, 'holeEarProp':0.5, 'holeFromEndsProp':0.5, 'numHoles':2, 'holeRad':4.5/2}
innerRad = max(innerRad,0.5)

def doTransform(ob, transforms):
    ret = ob
    for tr in transforms:
        for t in tr.keys():
            if t=='rotate3D':
                ret = rotate(tr[t][0])(ret)
            elif t=='translate3D':
                ret = translate(tr[t])(ret)
    return ret

class importpcb:
    def __init__(self,  conf, depth):
        pcb = kicad.Kicad(conf['filename'])
        pcb.makeBorders('')
        part=pcb.getPart('','')
        border = part.border
        bb=pcb.border.get_bounding_box()
        self.offset = -(bb['bl']+bb['tr'])/2
        self.conf=conf
        self.pcb =pcb
        self.depth = depth
    def getPCBmodel(self):
        part = self.pcb.getPart()
        return translate(self.conf['pos'])(translate([self.offset[0],self.offset[1]])(self.part.render3D()))
    def getPillars(self):
        pillars=[]
        for p in self.conf['pillars']:
            print (p)
            pattern=re.compile('(\d+\.*\d*)mm')    
            args={}
            for a in ['modulePrefix','moduleName']:
                if a in p:
                    args[a]=p[a]
            args['output']='dict'
            print (args)
            for mod in self.pcb.getModules(**args):
                print (mod)
                if 'diameter' in p: 
                    m=pattern.search(mod['name'])
                    rad=float(m.group(1))/2
                    print('rad='+str(rad*2))
                    if p['diameter']==rad*2:
                        print('append')
                        pillars.append(
                                translate([mod['pos'][0]+self.offset[0], mod['pos'][1]+self.offset[1],-self.depth/2+self.conf['fromBottom']-0.1])(
                                difference()(
                                cylinder(r=p['cylinderRad'], h=self.conf['fromBottom']+0.1),
                                translate([0,0,-1])(cylinder(r=p['holeRad'], h=self.conf['fromBottom']+2))
                                )
                                )
                        )
                        print(pillars)
        print (pillars)
        return pillars
            
def screw(rad, headRad, threadRad, length, clearanceLength):
    return rotate([180,0,0])(union()( cylinder(r=threadRad, h=length),
            cylinder(r=rad, h=clearanceLength),
            translate([0,0,-headRad])(cylinder(r1=headRad*2, r2=0, h=headRad*2)),
            ))

def roundedRect(width, height, rad):
        W=width/2-rad
        H=height/2-rad
        return hull()(
            translate([-W,H])(circle(r=rad)),
            translate([-W,-H])(circle(r=rad)),
            translate([W,-H])(circle(r=rad)),
            translate([W,H])(circle(r=rad)),
        )
def RoundedRectPrism(width, height, rad,depth):
    return linear_extrude(height=depth)(roundedRect(width, height, rad))

def PointyRect(width, height):
    W=width/2
    H=height/2-W
    return polygon(points=[[0,H+W],[W,H],[W,-H],[W,-H],[0,-H-W], [-W,-H], [-W,H]])

def SlotPrism(width, height,depth):
    return linear_extrude(height=depth, center=True)(PointyRect(width, height))


def box(width, height, depth, rad):
        W=width/2-rad
        H=height/2-rad
        D=depth/2-rad
        if rad<0:
            R=0
        else:
            R=rad
        return rbox(W, -W, H, -H, D, -D, R)

def rbox(Wa, Wi, Ha, Hi, Da, Di, R):
        print([Wa, Wi, Ha, Hi, Da, Di, R])
        return  hull()(
        translate([Wa,Ha,Da])(sphere(r=R)),
        translate([Wi,Ha,Da])(sphere(r=R)),
        translate([Wi,Hi,Da])(sphere(r=R)),
        translate([Wa,Hi,Da])(sphere(r=R)),

        translate([Wa,Ha,Di])(sphere(r=R)),
        translate([Wi,Ha,Di])(sphere(r=R)),
        translate([Wi,Hi,Di])(sphere(r=R)),
        translate([Wa,Hi,Di])(sphere(r=R)),
        )

outerbox = box(width, height, depth, outerrad)
innerbox = box(width-2*thickness, height-2*thickness, depth=depth -2*thickness, rad=max(outerrad-thickness,0.5))
earShape={'xmin':-width/2, 'xmax':width/2, 'ymin':-height/2, 'ymax':height/2}
doEars = False
earHoles = []

# mounting ears
for e in earEdges:
    if e in mountingEars:
        doEars = True
        config = copy.copy(defaultEar)
        config = {**config, **mountingEars[e]}
        if e=='left':
            earShape['xmin']-=config['length']
            start = [ earShape['xmin']+config['length']*config['holeEarProp'], height/2 - config['holeFromEndsProp']*config['length']]
            end   = [ earShape['xmin']+config['length']*config['holeEarProp'], -height/2 + config['holeFromEndsProp']*config['length']]
        elif e=='right':
            earShape['xmax']+=config['length']
            start = [  earShape['xmax']-config['length']*config['holeEarProp'], height/2 - config['holeFromEndsProp']*config['length']]
            end   = [  earShape['xmax']-config['length']*config['holeEarProp'], -height/2 + config['holeFromEndsProp']*config['length']]
        elif e=='top':
            earShape['ymax']+=config['length']
            start = [ -width/2 + config['holeFromEndsProp']*config['length'], earShape['ymax']-config['length']*config['holeEarProp']]
            end   = [  width/2 - config['holeFromEndsProp']*config['length'], earShape['ymax']-config['length']*config['holeEarProp']]
        elif e=='bottom':
            earShape['ymin']-=config['length']
            start = [ -width/2 + config['holeFromEndsProp']*config['length'], earShape['ymin']+config['length']*config['holeEarProp']]
            end   = [  width/2 - config['holeFromEndsProp']*config['length'], earShape['ymin']+config['length']*config['holeEarProp']]
        # add holes
        for i in range(0, config['numHoles']):
            hp = [start[0] + (end[0]-start[0])/(config['numHoles']-1)*i, start[1] + (end[1]-start[1])/(config['numHoles']-1)*i]
            print("hp"+str(hp)+e+" start="+str(start)+" end="+str(end))
            earHoles.append(translate([hp[0], hp[1], -depth/2])(cylinder(r=config['holeRad'], h=earThickness+10, center=True)))
earHole=union()(*earHoles)
er = earThickness/4
earbox = difference()(
        rbox(earShape['xmax']-er, earShape['xmin']+er, earShape['ymax']-er, earShape['ymin']+er, -depth/2+earThickness-er , -depth/2+er, er )
        ,earHole)
outer = union()(outerbox, earbox)


fullbox = difference()(outer, innerbox)
screws = []
screwCylinders = []
for s in screwPoses:
    screwCylinders.append( intersection()(outerbox,translate([s[0],s[1],-500])(cylinder(r=screwCylinderRad, h=1000))))
    screws.append( translate([s[0],s[1],depth/2])(
        screw(screwRad, screwHeadRad, screwThreadRad, depth-4*thickness, depth/2-cutz)
        )
    )
#for s in pcbScrewPoses:
#    screwCylinders.append( intersection()(outerbox,translate([s[0],s[1],-1000+pcbScrewLength-depth/2])(cylinder(r=pcbScrewCylinderRad, h=1000))))
#    screws.append(translate([s[0],s[1],-depth/2+thickness])(cylinder(r=pcbScrewThreadRad, h=depth-2*thickness)))


trimmedScrews = union()(*screwCylinders)
wholebox = difference()(
    union()(fullbox, 
        translate([0,0,cutz-overlap])(RoundedRectPrism(innerWidth, innerHeight, innerRad, depth/2-cutz+overlap)),
        ),
        translate([0,0,cutz-overlap-1])(RoundedRectPrism(innerWidth-2*edge-2, innerHeight-2*edge-2, innerRad, depth/2-thickness-cutz+1+overlap)),
    )

wholebox = difference()(
        union()(
            wholebox,
            trimmedScrews
            ),
        union()(*screws),
        )

wbox = wholebox
cut = union()(translate([-200,-200,cutz])(
                cube(size=[400,400, 250])
            ),
              translate([0,0,cutz-overlap])(RoundedRectPrism(innerWidth, innerHeight, innerRad, overlap+2)),
            )
temp=translate([0,0,cutz-overlap-1.01])(RoundedRectPrism(innerWidth, innerHeight, innerRad, overlap+1))
try:
    pillars
except:
    pillars=[]


holes=[]
rods=[]
for face in faces.keys():
    print(face)
    for pcb in pcbs[face]:
        p=importpcb(pcb, depth)
        pillars+=p.getPillars()
        # apply transforms
    for hole in holePoses[face]:
        print (hole)
        if hole['shape']=='rect':
            holes.append(doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness-2])(RoundedRectPrism(hole['width'], hole['height'], hole['rad'], thickness+4)), faces[face]))
        elif hole['shape']=='circle':
            holes.append(doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness/2-1])(cylinder(r=hole['rad'], h=thickness+5, center=True)), faces[face]))
        elif hole['shape']=='pillar':
            if hole['from']=='out':
                holes.append(doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness/2-1])(cylinder(r=hole['rad'], h=hole['length']+1)), faces[face]))
                rods.append(doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness/2])(cylinder(r=hole['pillarRad'], h=hole['length']+1)), faces[face]))
            else:
                holes.append(doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness/2+hole['length']+1])(cylinder(r=hole['rad'], h=hole['length']+1)), faces[face]))
                rods.append(doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness/2+0.1])(cylinder(r=hole['pillarRad'], h=hole['length']-0.1)), faces[face]))
        elif hole['shape']=='slot':
            holes.append(doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness/2+1])(SlotPrism(hole['width'], hole['height'], thickness+1)), faces[face]))

#if len(rods):
wholebox = union()(wholebox,*rods, *extraSolids)



allHoles = union()(*holes, *extraHoles)

#if len(allHoles):
    
wholebox=difference()(wholebox,allHoles)

bottom = union()(
        difference()(wholebox,cut),
        *pillars
        )
ttop = intersection()(wbox,cut)

scad_render_to_file(temp, 'fullbox.scad' , file_header = '$fa = 0.5;\n$fs = 0.5;', include_orig_code=True)
top = intersection()(wholebox, cut)
top2 = union ()(top,innerbox)
scad_render_to_file(top, 'top.scad' , file_header = '$fa = 0.5;\n$fs = 0.5;', include_orig_code=True)
scad_render_to_file(bottom, 'bottom.scad' , file_header = '$fa = 0.5;\n$fs = 0.5;', include_orig_code=True)

