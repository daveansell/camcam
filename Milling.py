#This file is part of CamCam.

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


class Milling:
        def __init__(self):

                self.mode_config={
                        "dave-emc":{
                                'prefix':'M03\nG21\nG0Z%zclear%\nG64 p.001 q.001\nG17\n',
                                'postfix':'M05\nM02\n',
                                'settool_prefix':'T',
                                'settool_postfix':' M6\nS100\nM03',
                                'mode':'gcode',
                                'group':'cutter',
                                'toolchange':'newfile',
                                'transform':[],
                                'mirror_backs':True,
                                'overview':False,
                                'clear_height':10,
                                'precut_z':1,
                                'hide_cuts':False,
                                'file_suffix':'.ngc',
                                'comments':True,
                                'z_overshoot':0.4,
                                'label':False,
                                'zero':False,
				'blendTolerance':True,
                                'cuttingMode':True,   
                        },
                        "dave-lathe":{
                                'prefix':'G21\nG64 p.001 q.001\nG18\n',
                                'postfix':'M05\nM02\n',
                                'settool_prefix':'T',
                                'settool_postfix':' M6\nS2000\n',
                                'mode':'gcode',
                                'group':'cutter',
                                'toolchange':'newfile',
                                'transform':[],
                                'mirror_backs':True,
                                'overview':False,
                                'clear_height':10,
                                'precut_z':1,
                                'hide_cuts':False,
                                'file_suffix':'.ngc',
                                'comments':True,
                                'z_overshoot':0.4,
                                'label':False,
                                'zero':False,
                                'cuttingMode':True,   
                        },
                        'eagle':{
                                'prefix':'GRID MM\nLAYER 21\n',
                                'normal_layer':21, #tPlace
                                'border_layer':20, #dimension
                                'postfix':'',
                                'mode':'scr',
                                'toolchange':'none',
                                'group':False,
                                'mirror_backs':False,
                                'overview':False,
                                'clear_height':10,
                                'precut_z':1,
                                'hide_cuts':True,
                                'file_suffix':'.scr',
                                'comments':False,
                                'dosfile':True,
                                'label':False,
                                'zero':False,
                                'cuttingMode':True,   
                        },
                        '3D':{
                                'overview':False,
                                'mirror_backs':False,
                                'cuttingMode':False,   

                        },
                        '3Dall':{
                                'overview':True,
                                'mirror_backs':True,
                                'cuttingMode':False,   

                        },
                        'makespacerouter2':{
                                'prefix':'T1M6\nG17\nG0Z30\n',
                                'postfix':'M30\n',
                                'settool_prefix':'T',
                                'settool_postfix':' M6\nS100\nM03',
                                'mode':'gcode',
                                'group':'cutter',
                                'toolchange':'newfile',
                                'transform':[],
                                'mirror_backs':True,
                                'overview':False,
                                'clear_height':10,
                                'precut_z':1,
                                'file_suffix':'.tap',
                                'comments':False,
                                'dosfile':True,
                                'z_overshoot':0.2,
                                'label':False,
                                'zero':'bottom_left',
				'downmode':'cutdown',
				'hide_cuts':False,
                                'cuttingMode':True,   
                        },
                        'makespacerouter':{
#                                'prefix':'T1M6\nG17\nG0Z10S11000M3\n',
                                'prefix':'T1M6\nG17\nG0Z30\n',
                                'postfix':'M30\n',
                                'mode':'simplegcode',
                                'group':'cutter',
                                'toolchange':'newfile',
                                'mirror_backs':True,
                                'overview':False,
                                'clear_height':10,
                                'precut_z':1,
                                'hide_cuts':False,
                                'file_suffix':'.tap',
                                'comments':False,
                                'dosfile':True,
                                'z_overshoot':0.2,
                                'label':False,
				'noblank':True,
				'shortFilename':True,
                	#	'downmode':'down',
                		#'zero':'bottom_left',
                                'cuttingMode':True,   
                        },
                        'laser':{
                              #  'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n<svg width="594mm" height="420mm"\n     xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 594 420">\n<g transform="scale(1, -1) translate(0,-420)">',
                                'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n <svg width="594mm" height="420mm"\n   xmlns:dc="http://purl.org/dc/elements/1.1/" \n   xmlns:cc="http://creativecommons.org/ns#"\n   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n   xmlns:svg="http://www.w3.org/2000/svg"\n   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"\n   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"\n   xmlns="http://www.w3.org/2000/svg"\n version="1.1" viewBox="0 0 594 420">\n<sodipodi:namedview      id="base"      pagecolor="#ffffff"      bordercolor="#666666"      borderopacity="1.0"      inkscape:pageopacity="0.0"      inkscape:pageshadow="2"     inkscape:zoom="0.35"     inkscape:cx="375"     inkscape:cy="520"     inkscape:document-units="mm"     inkscape:current-layer="layer1"     showgrid="false"     units="mm"     inkscape:window-width="504"     inkscape:window-height="441"     inkscape:window-x="320"     inkscape:window-y="25"     inkscape:window-maximized="0" />\n<g transform="scale(1, -1) translate(0,-420)">',
                                'postfix':'</g>\n</svg>\n',
                                'mode':'svg',
                                'forcestepdown':1000,
                                'forcecutter':'laser',
                                'linewidth':0.5,
                                'group':False,
                                'toolchange':'none',
                                'mirror_backs':True,
                                'overview':False,
                                'hide_cuts':False,
                                'z_overshoot':0,
                                'label':False,
                                'zero':False,
                                'file_suffix':'.svg',
                                'cuttingMode':True,   
                        },
                        'cutdxf':{
                                'forcestepdown':1000,
                                'toolchange':'none',
                                'mirror_backs':True,
                                'z_overshoot':0,
                                'group':False,
                                'overview':False,
                                'hide_cuts':False,
                                'label':False,
                                'zero':False,
                                'file_suffix':'.dxf',
                                'mode':'dxf',
                                'render_string':False,
                                'cuttingMode':True,   
                        },
                        'laserdxf':{
                                'forcestepdown':1000,
                                'forcecutter':'laser',
                                'toolchange':'none',
                                'mirror_backs':True,
                                'z_overshoot':0,
                                'group':False,
                                'overview':False,
                                'hide_cuts':False,
                                'label':False,
                                'zero':False,
                                'file_suffix':'.dxf',
                                'mode':'dxf',
                                'render_string':False,
                                'precut_z':0,
                                'cuttingMode':True,   
                        },
                        'exportdxf':{
                                'forcestepdown':1000,
                                'forcecutter':'on',
                                'toolchange':'none',
                                'group':False,
                                'overview':False,
                                'hide_cuts':True,
                                'label':False,
                                'zero':False,
                                'mirror_backs':True,
                                'file_suffix':'.dxf',
                                'mode':'dxf',
                                'render_string':False,
                                'cuttingMode':True,   
                        },
                        'dxf':{
                                'forcestepdown':1000,
                                'forcecutter':'on',
                                'toolchange':'none',
                                'group':False,
                                'overview':False,
                                'hide_cuts':True,
                                'label':False,
                                'zero':False,
                                'file_suffix':'.dxf',
                                'mode':'dxf',
                                'render_string':False,
                                'cuttingMode':False,   
                        },
                        'pcbsvg':{
                                'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n<svg width="594mm" height="420mm"\n     xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 594 420">\n<g transform="scale(1, -1) translate(0,-420)">',
                                'postfix':'</g>\n</svg>\n',
                                'mode':'svg',
                                'forcestepdown':1000,
                                'linewidth':0.5,
                                'group':False,
                                'toolchange':'none',
                                'mirror_backs':True,
                                'overview':False,
                                'hide_cuts':False,
                                'z_overshoot':0,
#				'transformations':[{'scale':1/2.54}]
                                'label':False,
                                'zero':False,
				'file_suffix':'.svg',
                                'cuttingMode':False,   
                        },
                        'paper':{
                                'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n<svg width="594mm" height="420mm"\n     xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 594 420">\n<g transform="scale(1, -1) translate(0,-420)">',
                                'postfix':'</g>\n</svg>\n',
                                'mode':'svg',
                                'forcestepdown':1000,
                                'linewidth':0.1,
                                'group':False,
                                'toolchange':'none',
                                'mirror_backs':False,
                                'overview':False,
                                'hide_cuts':True,
                                'z_overshoot':0.01,
                                'label':False,
                                'zero':False,
                                'cuttingMode':True,   
                        },
                        'millsvg':{
                                'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n<svg width="594mm" height="420mm"\n     xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 594 420">\n<g transform="scale(1, -1) translate(0,-420)">',
                                'postfix':'</g>\n</svg>\n',
                                'mode':'svg',
                                'forcestepdown':1000,
                                'group':'cutter',
                                'forcecolour':True,
                                'mirror_backs':True,
                                'overview':False,
                                'hide_cuts':False,
                                'z_overshoot':0,
                                'label':False,
                                'zero':False,
                                'file_suffix':'.svg',
                                'cuttingMode':True,   
                        },
                        'svg':{
                                'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n<svg width="594mm" height="420mm"\n     xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 594 420">\n<g transform="scale(1, -1) translate(0,-420)">',
                                'postfix':'</g>\n</svg>\n',
                                'mode':'svg',
                                'group':False,
                                'forcestepdown':1000,
                                'mirror_backs':False,
                                'overview':False,
                                'hide_cuts':False,
                                'z_overshoot':0,
                                'label':False,
                                'zero':False,
				'file_suffix':'.svg',
                                'cuttingMode':False,   
                        },
                        'diagram':{
                                'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n <svg width="594mm" height="420mm"\n   xmlns:dc="http://purl.org/dc/elements/1.1/" \n   xmlns:cc="http://creativecommons.org/ns#"\n   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n   xmlns:svg="http://www.w3.org/2000/svg"\n   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"\n   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"\n   xmlns="http://www.w3.org/2000/svg"\n version="1.1" viewBox="0 0 594 420">\n<sodipodi:namedview      id="base"      pagecolor="#ffffff"      bordercolor="#666666"      borderopacity="1.0"      inkscape:pageopacity="0.0"      inkscape:pageshadow="2"     inkscape:zoom="0.35"     inkscape:cx="375"     inkscape:cy="520"     inkscape:document-units="mm"     inkscape:current-layer="layer1"     showgrid="false"     units="mm"     inkscape:window-width="504"     inkscape:window-height="441"     inkscape:window-x="320"     inkscape:window-y="25"     inkscape:window-maximized="0" />\n<g transform="scale(1, -1) translate(0,-420)">',
                                #'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n<svg width="594mm" height="420mm"\n     xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 594 420">\n<g transform="scale(1, -1) translate(0,-420)">',
                                'postfix':'</g>\n</svg>\n',
                                'mode':'svg',
                                'group':False,
                                'forcestepdown':1000,
                                'mirror_backs':False,
                                'overview':True,
                                'hide_cuts':True,
                                'z_overshoot':0,
                                'label':True,
                                'zero':False,
                                'cuttingMode':True,   
                                'forcecutter':'laser',
                        },
                        'visualise':{
                                'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n <svg width="594mm" height="420mm"\n   xmlns:dc="http://purl.org/dc/elements/1.1/" \n   xmlns:cc="http://creativecommons.org/ns#"\n   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n   xmlns:svg="http://www.w3.org/2000/svg"\n   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"\n   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"\n   xmlns="http://www.w3.org/2000/svg"\n version="1.1" viewBox="0 0 594 420">\n<sodipodi:namedview      id="base"      pagecolor="#ffffff"      bordercolor="#666666"      borderopacity="1.0"      inkscape:pageopacity="0.0"      inkscape:pageshadow="2"     inkscape:zoom="0.35"     inkscape:cx="375"     inkscape:cy="520"     inkscape:document-units="mm"     inkscape:current-layer="layer1"     showgrid="false"     units="mm"     inkscape:window-width="504"     inkscape:window-height="441"     inkscape:window-x="320"     inkscape:window-y="25"     inkscape:window-maximized="0" />\n<g transform="scale(1, -1) translate(0,-420)">',
                                #'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n<svg width="594mm" height="420mm"\n     xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 594 420">\n<g transform="scale(1, -1) translate(0,-420)">',
                                'postfix':'</g>\n</svg>\n',
                                'mode':'svg',
                                'group':False,
                                'forcestepdown':1000,
                                'mirror_backs':False,
                                'overview':True,
                                'hide_cuts':False,
                                'z_overshoot':0,
                                'label':True,
                                'zero':False,
                                'cuttingMode':False,   
                                
                        }


                }
                self.tools={
                "1/4_endmill":{
                        "id":4,
                        "diameter":6.35,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":1,
                },
                "1/4_straight":{
                        "id":4,
                        "diameter":6.35,
                        "endcut":0,
                        "sidecut":1,
                        "flutes":2,
                },
                "1/8_endmill":{
                        "id":3,
                        "diameter":3.127,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":1,
                },
                "16mm_endmill":{
                        "id":5,
                        "diameter":16.0,
                        "endcut":1,

                        "sidecut":1,
                        "flutes":2,
                },
                "18mm_endmill":{
                        "id":30,
                        "diameter":18.0,
                        "endcut":1,

                        "sidecut":1,
                        "flutes":2,
                },
                "22mm_endmill":{
                        "id":22,
                        "diameter":22.0,
                        "endcut":1,

                        "sidecut":1,
                        "flutes":2,
                },
                "6mm_endmill":{
                        "id":2,
                        "diameter":6.0,
                        "endcut":1,

                        "sidecut":1,
                        "flutes":1,
                },
                "2mm_endmill":{
                        "id":8,
                        "diameter":2.0,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":1,
                },
                "9.4mm_endmill":{
                        "id":21,
                        "diameter":9.4,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":2,
                },
                "3mm_endmill":{
                        "id":1,
                        "diameter":3.0,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":2,
                },
                "4mm_endmill":{
                        "id":9,
                        "diameter":4.0,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":1,
                },
                "8mm_endmill":{
                        "id":7,
                        "diameter":8.0,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":2,
                },
                "1mm_endmill":{
                        "id":10,
                        "diameter":1.0,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":2,
                        },
                "0.5mm_endmill":{
                        "id":11,
                        "diameter":0.5,

                        "endcut":1,
                        "sidecut":1,
                        "flutes":2,
                },
                "countersink25":{
                        "id":20,
                        "diameter":20,
                        "endcut":1,
                        "sidecut":1,
                        "min_diameter":2.0,
                        "angle":45,
                        "flutes":2,
                },
                "countersink":{
                        "id":6,
                        "diameter":13.0,
                        "endcut":1,
                        "sidecut":1,
                        "min_diameter":2.0,
                        "angle":45,
                        "flutes":2,
                },
                "1mm_drill":{
                        "id":12,
                        "diameter":1.0,
                        "endcut":1,
                        "sidecut":0,
                },
               "0.5mm_drill":{
                        "id":13,
                        "diameter":0.5,
                        "endcut":1,
                        "sidecut":0,
                },
               "0.8mm_drill":{
                        "id":14,
                        "diameter":0.8,
                        "endcut":1,
                        "sidecut":0,
                },
                "1.54mm_drill":{
                        "id":16,
                        "diameter":1.54,
                        "endcut":1,
                        "sidecut":0,
                },
                "1.5mm_drill":{
                        "id":16,
                        "diameter":1.5,
                        "endcut":1,
                        "sidecut":0,
                },
                "2.5mm_drill":{
                        "id":19,
                        "diameter":2.5,
                        "endcut":1,
                        "sidecut":0,
                },
                "ovolo":{
                        "id":18,
                        "diameter":10.0,
                        "endcut":1,
                        "sidecut":1,
                },
                "bevel_trim":{
                        "id":17,
                        "diameter":6.35,
                        "endcut":0,
                        "sidecut":1,
                        "angle":17.0/2,
                        "sidestep":0.5,
                        "flutes":2,
                },
                "3mm_ballmill":{
                        "id":21,
                        "diameter":3.0,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":2,
                },
                "6mm_ballmill":{
                        "id":22,
                        "diameter":6.0,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":2,
                },
                "engraving":{
                        "id":23,
                        "diameter":1.2,
                        "endcut":0,
                        "sidecut":1,
                        "flutes":2,
                },

                "laser":{
                        "id":100,
                        "diameter":0.05,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":1,
                },
                "latheBoring":{
                        "id":50,
                        "diameter":4,
                        "endcut":1,
                        "sidecut":1,
			"forcestepdown":1000,
			"handedness":-1,
                        "type":"lathe",
                },
                "latheParting":{
                        "id":52,
                        "diameter":4,
                        "endcut":1,
                        "sidecut":0,
			"forcestepdown":1000,
			"handedness":1,
                        "type":"lathe",
                },
                "latheTurning":{
                        "id":51,
                        "diameter":4,#this way sidefeed is not changed
                        "endcut":1,
                        "sidecut":1,
			"forcestepdown":1000,
			"handedness":1,
                        "type":"lathe",
                },
                "on":{
                        "id":101,
                        "diameter":0,
                        "endcut":1,
                        "sidecut":1,
                        "flutes":1,
                },
                }
# feeds and stepdown are definined for 4mm cutter, and scaled linearly by cutterrad
                self.materials = {
                "plywood":{
                        "vertfeed":200,
                        "sidefeed":1100,
                        "stepdown":5.0,
                        "kress_setting":4.0,
                        "spring":0.3,
                        "surface_speed":650*300, # mm/min
                        "chip_loading":{
                            'low':{3.16:	0.1016	,6.32:	0.2794	,9.48:	0.4318	,12.64:	0.5334},
                            'high':{3.16:	0.1524	,6.32:	0.3302	,9.48:	0.508	,12.64:	0.5842},
                            },
                            
                },
                "mdf":{
                        "vertfeed":200,
                        "sidefeed":1000,
                        "stepdown":3.5,
                        "kress_setting":4.0,
                        "spring":0.3,
                        "surface_speed":650*300, # mm/min
                        "chip_loading":{
                            'low':{ 3.16:	0.1016	,6.32:	0.3302	,9.48:	0.508	,12.64:0.635},
                            'high':{3.16:	0.1778	,6.32:	0.4064	,9.48:	0.5842	,12.64:0.6858 },
                            },

                },

                "perspex":{
                        "vertfeed":120,
                        "sidefeed":600,
                        "stepdown":2.0,
                        "kress_setting":2.0,
                        "surface_speed":500*300, # mm/min
                #	"mill_dir":'down',
                        "chip_loading":{
                            'low':{3.16:	0.0762	,6.32:	0.2032	,9.48:	0.254	,12.64:	0.3048 },
                            'high':{ 3.16:	0.127	,6.32:	0.254	,9.48:	0.3048	,12.64:	0.381},
                            },
                },
                "polycarbonate":{
                        "vertfeed":120,
                        "sidefeed":700,
                        "stepdown":2.0,
                        "kress_setting":2.0,
                        "surface_speed":500*300, # mm/min
                        "chip_loading":{ # from acrylic 
                            'low':{3.16:	0.0762	,6.32:	0.2032	,9.48:	0.254	,12.64:	0.3048 },
                            'high':{ 3.16:	0.127	,6.32:	0.254	,9.48:	0.3048	,12.64:	0.381},
                            },

                },
                "delrin":{
                        "vertfeed":120,
                        "sidefeed":1000,
                        "stepdown":3.0,
                        "kress_setting":2.0,
                        "mill_dir":'down',
                        "surface_speed":500*300, # mm/min
                        "chip_loading":{
                            'low':{3.16:	0.0508	,6.32:	0.1524	,9.48:	0.2032	,12.64:	0.254},
                            'high':{3.16:	0.1016	,6.32:	0.2286	,9.48:	0.254	,12.64:	0.3048},
                            },
                },
                "tufnol":{
                        "vertfeed":100,
                        "sidefeed":900,
                        "stepdown":1.5,
                        "kress_setting":2.0,
                        "surface_speed":400*300, # mm/min
                        "chip_loading":{ # from Al
                            'low':{3.16:	0.0762	,6.32:	0.127	,9.48:	0.1524	,12.64:	0.2032},
                            'high':{3.16:	0.1016	,6.32:	0.1778	,9.48:	0.2032	,12.64:	0.254},
                            },
               },
                "HIPS":{
                        "vertfeed":100,
                        "sidefeed":500,
                        "stepdown":3.0,
                        "kress_setting":1.5,
                        "surface_speed":450*300, # mm/min
               },
                "aluminium":{
                        "vertfeed":30,
                        "sidefeed":950,
                        "stepdown":0.6,
                        "kress_setting":1,
                        "mill_dir":'down',
                        "K":{
                            'bending':{1:0.33, 3:0.4, 10:0.5},
                            'bottoming':{1:0.42, 3:0.46, 10:0.5},
                            'coining':{1:0.38, 3:0.44, 10:0.5},
                        },
                        "surface_speed":250*300, # mm/min
                        "chip_loading":{ # from Al
                            'low':{3.16:	0.0762	,6.32:	0.127	,9.48:	0.1524	,12.64:	0.2032},
                            'high':{3.16:	0.1016	,6.32:	0.1778	,9.48:	0.2032	,12.64:	0.254},
                            },
               },
                
                "copper":{
                        "vertfeed":20,
                        "sidefeed":500,
                        "stepdown":0.2,
                        "kress_setting":3,
                        "mill_dir":'down',
                        "surface_speed":300*300, # mm/min
               },
                "brass":{
                        "vertfeed":20,
                        "sidefeed":500,
                        "stepdown":0.2,
                        "kress_setting":3,
                        "mill_dir":'down',
                        "K":{
                            'bending':{1:0.38, 3:0.43, 10:0.5},
                            'bottoming':{1:0.44, 3:0.47, 10:0.5},
                            'coining':{1:0.41, 3:0.46, 10:0.5},
                        },
                        "surface_speed":200*300, # mm/min
               },
                "steel":{
                        "vertfeed":20,
                        "sidefeed":500,
                        "stepdown":0.2,
                        "kress_setting":3,
                        "mill_dir":'down',
                        "K":{
                            'bending':{1:0.4, 3:0.45, 10:0.5},
                            'bottoming':{1:0.46, 3:0.48, 10:0.5},
                            'coining':{1:0.44, 3:0.47, 10:0.5},
                        },
                        "surface_speed":110*300, # mm/min
                        "chip_loading":{
                            'low':{ 3.16:	0.01016	,6.32:	0.03302	,9.48:	0.0508	,12.64:0.0635},
                            'high':{3.16:	0.01778	,6.32:	0.04064	,9.48:	0.05842	,12.64:0.06858 },
                            },
               },
                "polypropelene":{
                        "vertfeed":100,
                        "sidefeed":700,
                        "stepdown":2.0,
                        "kress_setting":1.5,
                        "mill_dir":'up',
                        "surface_speed":450*300, # mm/min
               },
                "plastazote":{
                        "vertfeed":700,
                        "sidefeed":2000,
                        "stepdown":15.0,
                        "kress_setting":1.5,
                        "mill_dir":'up',
               },
                "polyethene":{
                        "vertfeed":100,
                        "sidefeed":1000,
                        "stepdown":2.0,
                        "kress_setting":1.5,
			            "mill_dir":'down',
                        "surface_speed":450*300, # mm/min
                        "chip_loading":{  
                            'low':{3.16:	0.0762	,0.25:	0.1778	,9.48:	0.254	,12.64:	0.3048},
                            'high':{3.16:	0.1524	,0.25:	0.254	,9.48:	0.3048	,12.64:	0.4064},
                            },
               },
                "polythene":{
                        "vertfeed":100,
                        "sidefeed":1000,
                        "stepdown":15.0,
                        "kress_setting":1.5,
			            "mill_dir":'down',
                        "surface_speed":450*300, # mm/min
                        "chip_loading":{  
                            'low':{3.16:	0.0762	,0.25:	0.1778	,9.48:	0.254	,12.64:	0.3048},
                            'high':{3.16:	0.1524	,0.25:	0.254	,9.48:	0.3048	,12.64:	0.4064},
                            },
               },
                "pvc":{
                        "vertfeed":100,
                        "sidefeed":700,
                        "stepdown":3.0,
                        "kress_setting":1.5,
                        "mill_dir":'up',
                        "surface_speed":350*300, # mm/min
                        "chip_loading":{ # from polythene 
                            'low':{3.16:	0.0762	,0.25:	0.1778	,9.48:	0.254	,12.64:	0.3048},
                            'high':{3.16:	0.1524	,0.25:	0.254	,9.48:	0.3048	,12.64:	0.4064},
                            },
               },
                "abs":{
                        "vertfeed":100,
                        "sidefeed":900,
                        "stepdown":2.0,
                        "kress_setting":1.5,
                        "surface_speed":350*300, # mm/min
               },
                "petg":{
                        "vertfeed":100,
                        "sidefeed":900,
                        "stepdown":2.0,
                        "kress_setting":1.5,
                        "surface_speed":350*300, # mm/min
               },
                "pla":{
                        "vertfeed":100,
                        "sidefeed":900,
                        "stepdown":2.0,
                        "kress_setting":1.5,
                        "surface_speed":350*300, # mm/min
               },
               "pcb":{
                        "vertfeed":100,
                        "sidefeed":300,
                        "stepdown":2.0,
                        "kress_setting":3.0,
                        "surface_speed":650*300, # mm/min
               },
               "paper":{
                        "vertfeed":100,
                        "sidefeed":300,
                        "stepdown":2.0,
                        "kress_setting":3.0,
               },
                "piezo":{
                        "vertfeed":20,
                        "sidefeed":12,
                        "stepdown":0.2,
                        "kress_setting":3,
                        "mill_dir":'down',
               },
                "glass":{
                        "vertfeed":100,
                        "sidefeed":200,
                        "stepdown":0.2,
                        "kress_setting":3,
                        "mill_dir":'down',
               },
        }
                self.bolts={
                'M2.5':{
                        'diam':2.5,
                        'tap':2.1,
                        'clearance':3.18,
                        'allen':{
                                'head_d':4.7,
                                'head_l':2.5,
                        },
                        'button':{
                                'head_d':5,
                                'head_l':1.65,
                        },
                        'cs':{
                            'head_d':4.7,
                            'head_l':1.5,
                        },
                },
                'M3':{
                        'diam':3.0,
                        'tap':2.5,
                        'clearance':3.5,
                        'allen':{
                                'head_d':5.5,
                                'head_l':3.0,
                        },
                        'button':{
                                'head_d':5.7,
                                'head_l':1.65,
                        },
                        'cs':{
                            'head_d':5.5,
                            'head_l':1.7,
                        },
                },
                'M4':{
                        'diam':4.0,
                        'tap':3.3,
                        'clearance':5.0,
                        'allen':{
                                'head_d':7.0,
                                'head_l':4.0,
                        },
                        'button':{
                                'head_d':7.6,
                                'head_l':2.2,
                        },
                        'cs':{
                            'head_d':7.6,
                            'head_l':2.6,
                        },
                },
                'M5':{
                        'diam':5.0,
                        'tap':4.2,
                        'clearance':6.0,
                        'allen':{
                                'head_d':8.5,
                                'head_l':5.0,
                        },
                        'button':{
                                'head_d':9.5,
                                'head_l':2.75,
                        },
                        'cs':{
                            'head_d':8.9,
                            'head_l':3.1,
                        },
                },
                'M6':{
                        'diam':6.0,
                        'tap':5.0,
                        'clearance':7.0,
                        'allen':{
                                'head_d':10,
                                'head_l':6.0
                        },
                        'button':{
                                'head_d':10.5,
                                'head_l':3.3,
                        },
                        'hex':{
                                'head_d':10.0,
                                'head_l':4.3,
                        },
                        'cs':{
                            'head_d':11.2,
                            'head_l':3.6,
                        },
                },
                'M8':{
                        'diam':8.0,
                        'tap':6.5,
                        'clearance':9.0,
                        'allen':{
                                'head_d':13,
                                'head_l':8.0
                        },
                        'button':{
                                'head_d':14,
                                'head_l':4.4,
                        },
                        'hex':{
                                'head_d':13.0,
                                'head_l':5.6,
                        },
                        'cs':{
                            'head_d':14.7,
                            'head_l':4.5,
                        },
                },
                'M10':{
                        'diam':10.0,
                        'tap':8.4,
                        'clearance':11.0,
                        'hex':{
                                'head_d':16.0,
                                'head_l':10.0,
                        },
                        'button':{
                                'head_d':17.5,
                                'head_l':5.5,
                        },
                        'cs':{
                            'head_d':18.3,
                            'head_l':6.0,
                        },
                },
                'M12':{
                        'diam':12.0,
                        'tap':10.3,
                        'clearance':13.0,
                        'hex':{
                                'head_d':18.0,
                                'head_l':12.0,
                        },
                        'button':{
                                'head_d':21.0,
                                'head_l':6.6,
                        },
                        'hex':{
                                'head_d':19.0,
                                'head_l':8.0,
                        },
                },
                'M14':{
                        'diam':14.0,
                        'tap':12.0,
                        'clearance':15.0,
                        'hex':{
                                'head_d':21.0,
                                'head_l':14.0,
                        },
                },
                'M16':{
                        'diam':16.0,
                        'tap':13.0,
                        'clearance':19.0,
                        'hex':{
                                'head_d':24.0,
                                'head_l':16.0,
                        },
                        'button':{
                                'head_d':28.0,
                                'head_l':8.8,
                        },
                },
                'M20':{
                        'diam':20.0,
                        'tap':17.5,
                        'clearance':21.0,
                        'hex':{
                                'head_d':30.0,
                                'head_l':20.0,
                        },
                },
                '1/4BSP':{
                        'diam':13.0,
                        'tap':11.6,
                        'hex':{
                                'head_d':19.3,
                                'head_sl':6.0
                        },
                        'shoulder':{
                                'diam':18,
                                'length':1.8,
                        },
                },
                '#10-32':{
                        'diam':4.915,
                        'tap':4.04,
                        'clearance':5.3,
                },
                'RMS':{
                        'diam':20.32,
                        'tap':19.6,
                        'clearance':21.0,
                },

        }
                self.inserts={
                'M2.5':{
                        "diams":[4/2],
                        "depths":[False],

                },
                "M3":{
                        "diams":[5,4.5/2],
                        "depths":[-0.1,False],
                        'plastic':{
                            'diams':4.0,
                            'depths':False
                        },
                },
                "M3.5":{
                        "diams":5.1/2,
                        "depths":False,
                },
                "M4":{
                        "diams":[5,3.05],
                        "depths":[-1,False],
                        'hammer':{
                                "diams":[14.2/2,10/2,3.05],
#					"diams":[14.2/2,10/2,3,5.7/2],
                                "depths":[-1.5,-1.5,False]
                        },
                        'headless':{
                                "diams":[3.05],
                                "depths":[False],
                        },
                        'plastic':{
                            'diams':5.9,
                            'depths':False
                        },
                },
                "M5":{
                        "diams":[5.5,3.6],
                        "depths":[-1,False],
                        'plastic':{
                            'diams':6.5,
                            'depths':False
                        },
                },
                "M6":{
                        "diams":[7,4.25], #Edited db from 6mm dia... these are also radii...
                        "depths":[-1,False],
                        'plastic':{
                            'diams':8.2,
                            'depths':False
                        },
                },
                "M8":{
                        "diams":[7.75,5.5],
                        "depths":[-1,False],
                },
                "M10":{
                        "diams":[5,3.05],
                        "depths":[-1,False],
                },

        }
