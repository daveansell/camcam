from solid import *
from path import *
from shapes import *
import solid
import sys
sys.path.append("../../../camcam/")
import kicad

class ProjectBox(Part):
    def __init__(self,width, height, depth, thickness, outerrad, innerWidth, innerHeight, innerRad, cutz, screwFromEdge, pcbScrewLength,pcbScrewCylinderRad, pcbScrewThreadRad, screwPoses,  screwCylinderRad, screwThreadRad, screwRad,screwHeadRad,overlap, mountingEars, earThickness, edge, holePoses, pcbs, extraSolids=[], extraHoles=[], **config):
        if 'slope' in config:
            slope = config['slope']
        else:
            slope = 0
        print(width)
        print("Hello")

        Sf=(height-2*thickness)*math.sin(float(slope)/180*math.pi)
        faces = {
                'front' :[ {'rotate3D':[[0,180,0], V(0,0,0)]},   {'translate3D':V(0,0,depth/2-1)}],
                'back'  :[ {'rotate3D':[[0,0,0], V(0,0,0)]},  {'rotate3D':[[slope,0,0],V(0,0,0)]}, {'translate3D':V(0,0,-depth/2+1-Sf/2)}],
                'left'  :[ {'rotate3D':[[90,0,90], V(0,0,0)]}, {'translate3D':V(-width/2+1,0,0)}],
                'right' :[ {'rotate3D':[[90,0,-90], V(0,0,0)]},{'translate3D':V( width/2-1,0,0)}],
                'top'   :[ {'rotate3D':[[0,90,90], V(0,0,0)]}, {'rotate3D':[[0,90,0], V(0,0,0)]},{'translate3D':V( 0,height/2+1,0)}],
                'bottom':[ {'rotate3D':[[0,90,-90], V(0,0,0)]},{'rotate3D':[[0,90,0], V(0,0,0)]},{'translate3D':V( 0,-height/2-1,0)}],
                }
        earEdges = ['left', 'right', 'top', 'bottom']
        defaultEar = {'length':12, 'holeEarProp':0.5, 'holeFromEndsProp':0.5, 'numHoles':2, 'holeRad':4.5/2}
        innerRad = max(innerRad,0.5)

        outerbox = self.box(width, height, depth, outerrad,slope)
        innerbox = self.box(width-2*thickness, height-2*thickness, depth=depth -2*thickness, rad=max(outerrad-thickness,0.5),slope=slope)
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
        er = earThickness/4*math.cos(float(slope)/180*math.pi)

        S=(height-2*er)*math.sin(float(slope)/180*math.pi)
        earHole=self.doTransform(union()(*earHoles), [{'rotate3D':[[slope,0,0],V(0,0,-depth/2)]}, {'translate3D':V(0,0,-S/2)}
            ])
        print("S+"+str(S))
        earbox = difference()(
                        self.rbox(earShape['xmax']-er, earShape['xmin']+er, earShape['ymax']-er, earShape['ymin']+er, -depth/2+earThickness-er , -depth/2+er, er, S, S )
                    ,earHole)
#                    [{'rotate3D':[[slope,0,0],V(0,-height/2,-depth/2)]}])

        outer = union()(outerbox, earbox)


        fullbox = difference()(outer, innerbox)
        screws = []
        screwCylinders = []
        for s in screwPoses:
            screwCylinders.append( intersection()(outerbox,translate([s[0],s[1],-500])(cylinder(r=screwCylinderRad, h=1000))))
            screws.append( translate([s[0],s[1],depth/2])(
                self.screw(screwRad, screwHeadRad, screwThreadRad, depth-4*thickness, depth/2-cutz)
                )
            )
        #for s in pcbScrewPoses:
        #    screwCylinders.append( intersection()(outerbox,translate([s[0],s[1],-1000+pcbScrewLength-depth/2])(cylinder(r=pcbScrewCylinderRad, h=1000))))
        #    screws.append(translate([s[0],s[1],-depth/2+thickness])(cylinder(r=pcbScrewThreadRad, h=depth-2*thickness)))


        trimmedScrews = union()(*screwCylinders)
        wholebox = difference()(
            union()(fullbox, 
                translate([0,0,cutz-overlap])(self.RoundedRectPrism(innerWidth, innerHeight, innerRad, depth/2-cutz+overlap)),
                ),
                translate([0,0,cutz-overlap-1])(self.RoundedRectPrism(innerWidth-2*edge-2, innerHeight-2*edge-2, innerRad, depth/2-thickness-cutz+1+overlap)),
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
                      translate([0,0,cutz-overlap])(self.RoundedRectPrism(innerWidth, innerHeight, innerRad, overlap+2)),
                    )
        temp=translate([0,0,cutz-overlap-1.01])(self.RoundedRectPrism(innerWidth, innerHeight, innerRad, overlap+1))
        try:
            pillars
        except:
            pillars=[]


        holes=[]
        rods=[]
        for face in faces.keys():
            print(face)
            print(pcbs[face])
            for pcb in pcbs[face]:
                p=importpcb(pcb, depth)
                pillars+=p.getPillars()
                # apply transforms
            for hole in holePoses[face]:
                print (hole)
                if hole['shape']=='rect':
                    holes.append(self.doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness-2])(self.RoundedRectPrism(hole['width'], hole['height'], hole['rad'], thickness+4)), faces[face]))
                elif hole['shape']=='circle':
                    holes.append(self.doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness/2-1])(cylinder(r=hole['rad'], h=thickness+5, center=True)), faces[face]))
                elif hole['shape']=='pillar':
                    if hole['from']=='out':
                        holes.append(self.doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness/2-1])(cylinder(r=hole['rad'], h=hole['length']+1)), faces[face]))
                        rods.append(self.doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness/2])(cylinder(r=hole['pillarRad'], h=hole['length']+1)), faces[face]))
                    else:
                        holes.append(self.doTransform(translate([hole['pos'][0], hole['pos'][1], 1])(cylinder(r=hole['rad'], h=hole['length']+1)), faces[face]))
                        rods.append(self.doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness/2+0.1])(cylinder(r=hole['pillarRad'], h=hole['length']-0.1)), faces[face]))
                elif hole['shape']=='slot':
                    holes.append(self.doTransform(translate([hole['pos'][0], hole['pos'][1], -thickness/2+1])(self.SlotPrism(hole['width'], hole['height'], thickness+1)), faces[face]))

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


    def doTransform(self, ob, transforms):
        ret = ob
        for tr in transforms:
            for t in tr.keys():
                if t=='rotate3D':
                    if len(tr[t])>=2:
                        ret = solid.translate(tr[t][1])(
                                solid.rotate(tr[t][0])(
                                    solid.translate(-tr[t][1])(ret)
                                ))
                    else:
                        ret = solid.rotate(tr[t][0])(ret)

                elif t=='translate3D':
                    ret = translate(tr[t])(ret)
        return ret
                
    def screw(self, rad, headRad, threadRad, length, clearanceLength):
        return solid.rotate([180,0,0])(union()( cylinder(r=threadRad, h=length),
                cylinder(r=rad, h=clearanceLength),
                translate([0,0,-headRad])(cylinder(r1=headRad*2, r2=0, h=headRad*2)),
                ))

    def roundedRect(self, width, height, rad):
            W=width/2-rad
            H=height/2-rad
            return hull()(
                translate([-W,H])(circle(r=rad)),
                translate([-W,-H])(circle(r=rad)),
                translate([W,-H])(circle(r=rad)),
                translate([W,H])(circle(r=rad)),
            )
    def RoundedRectPrism(self,width, height, rad,depth):
        return linear_extrude(height=depth)(self.roundedRect(width, height, rad))

    def PointyRect(self,width, height):
        W=width/2
        H=height/2-W
        return polygon(points=[[0,H+W],[W,H],[W,-H],[W,-H],[0,-H-W], [-W,-H], [-W,H]])

    def SlotPrism(self,width, height,depth):
        return linear_extrude(height=depth, center=True)(self.PointyRect(width, height))


    def box(self,width, height, depth, rad,slope):
            W=width/2-rad
            H=height/2-rad
            D=depth/2-rad
            S=(height-2*rad)*math.sin(float(slope)/180*math.pi)
            if rad<0:
                R=0
            else:
                R=rad
            print ("sleop= "+str(slope)+" S="+str(S))
            return self.rbox(W, -W, H, -H, D, -D, R, S)

    def rbox(self,Wa, Wi, Ha, Hi, Da, Di, R, S=0, ST=0):
            print([Wa, Wi, Ha, Hi, Da, Di, R, S])
            return  hull()(
            translate([Wa,Ha,Da])(sphere(r=R)),
            translate([Wi,Ha,Da])(sphere(r=R)),
            translate([Wi,Hi,Da-ST])(sphere(r=R)),
            translate([Wa,Hi,Da-ST])(sphere(r=R)),

            translate([Wa,Ha,Di])(sphere(r=R)),
            translate([Wi,Ha,Di])(sphere(r=R)),
            translate([Wi,Hi,Di-S])(sphere(r=R)),
            translate([Wa,Hi,Di-S])(sphere(r=R)),
            )


class importpcb:
    def __init__(self,  conf, depth):
        print("importpcb");
        pcb = kicad.Kicad(conf['filename'])
        pcb.makeBorders('')
        part=pcb.getPart('','')
        border = part.border
        bb=pcb.border.get_bounding_box()
        if 'pos' in conf:
            pos=conf['pos']
        else:
            pos=V(0,0)
        self.offset = -(bb['bl']+bb['tr'])/2+pos
        self.conf=conf
        self.pcb =pcb
        self.depth = depth
    def getPCBmodel(self):
        part = self.pcb.getPart()
        return translate(self.conf['pos'])(translate([self.offset[0],self.offset[1]])(self.part.render3D()))
    def getPillars(self):
        pillars=[]
        print(self.conf['pillars'])
        for p in self.conf['pillars']:
            print ("p="+str(p))
            pattern=re.compile('(\d+\.*\d*)mm')    
            args={}
            for a in ['modulePrefix','moduleName']:
                if a in p:
                    args[a]=p[a]
            args['output']='dict'
            print ("kicad args="+str(args))
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
