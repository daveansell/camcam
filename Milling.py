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


class Milling:
	def __init__(self):

		self.mode_config={
                        "dave-emc":{
                                'prefix':'M03\nG21\nG0Z10',
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
			},
			'3D':{
				'overview':False,
                                'mirror_backs':False,

			},
			'3Dall':{
				'overview':True,
                                'mirror_backs':True,

			},
                        'makespacerouter2':{
#                                'prefix':'T1M6\nG17\nG0Z10S11000M3\n',
				'prefix':'T1M6\nG17\nG0Z30S11000M3\n',
				'postfix':'M30\n',
                                'settool_prefix':'T',
                                'settool_postfix':' M6\nS100\nM03',
                                'mode':'gcode',
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
				'zero':'bottom_left',
                        },
                        'makespacerouter':{
#                                'prefix':'T1M6\nG17\nG0Z10S11000M3\n',
				'prefix':'T1M6\nG17\nG0Z30S11000M3\n',
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
				'zero':'bottom_left',
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
			},
			'dxf':{
				'forcestepdown':1000,
                                'forcecutter':'laser',
				'toolchange':'none',
				'group':False,
				'overview':False,
                                'hide_cuts':True,
				'label':False,
				'zero':False,
				'file_suffix':'.dxf',
				'mode':'dxf',
				'render_string':False,
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
				
                        }


		}
		self.tools={
		"1/4_endmill":{
                        "id":3,
                        "diameter":6.35,
                        "endcut":1,
                        "sidecut":1,
                },
                "1/8_endmill":{
                        "id":3,
                        "diameter":3.127,
                        "endcut":1,
                        "sidecut":1,
                },
                "16mm_endmill":{
                        "id":5,
                        "diameter":16.0,
                        "endcut":1,

                        "sidecut":1,
                },
                "6mm_endmill":{
                        "id":2,
                        "diameter":6.0,
                        "endcut":1,

                        "sidecut":1,
                },
                "2mm_endmill":{
                        "id":8,
                        "diameter":2.0,
                        "endcut":1,
                        "sidecut":1,
                },
                "9.4mm_endmill":{
                        "id":21,
                        "diameter":9.4,
                        "endcut":1,
                        "sidecut":1,
                },
                "3mm_endmill":{
                        "id":2,
                        "diameter":3.0,
                        "endcut":1,
                        "sidecut":1,
                },
                "4mm_endmill":{
                        "id":9,
                        "diameter":4.0,
                        "endcut":1,
                        "sidecut":1,
                },
                "8mm_endmill":{
                        "id":7,
                        "diameter":8.0,
                        "endcut":1,
                        "sidecut":1,
                },
                "1mm_endmill":{
                        "id":4,
                        "diameter":1.0,
                        "endcut":1,
                        "sidecut":1,
                        },
                "0.5mm_endmill":{
                        "id":5,
                        "diameter":0.5,

                        "endcut":1,
                        "sidecut":1,
                },
                "countersink":{
                        "id":6,
                        "diameter":13.0,
                        "endcut":1,
                        "sidecut":1,
			"min_diameter":2.0,
			"angle":45,
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
                "ovolo":{
                        "id":16,
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
		},
                "laser":{
                        "id":100,
                        "diameter":0.05,
                        "endcut":1,
                        "sidecut":1,
                },
		}
		self.materials = {
                "plywood":{
                        "vertfeed":200,
                        "sidefeed":800,
                        "stepdown":5.0,
                        "kress_setting":4.0,
                        "spring":0.3,

                },
                "mdf":{
                        "vertfeed":200,
                        "sidefeed":800,
                        "stepdown":3.5,
                        "kress_setting":4.0,
                        "spring":0.3,

                },

                "perspex":{
                        "vertfeed":120,
                        "sidefeed":600,
                        "stepdown":1.5,
                        "kress_setting":2.0,
			"mill_dir":'down',
                },
                "polycarbonate":{
                        "vertfeed":120,
                        "sidefeed":400,
                        "stepdown":2.0,
                        "kress_setting":2.0,

                },
                "delrin":{
                        "vertfeed":120,
                        "sidefeed":700,
                        "stepdown":3.0,
                        "kress_setting":2.0,
			"mill_dir":'down',
                },
                "tufnol":{
                        "vertfeed":100,
                        "sidefeed":400,
                        "stepdown":1.5,
                        "kress_setting":2.0,
               },
                "HIPS":{
                        "vertfeed":100,
                        "sidefeed":500,
                        "stepdown":3.0,
                        "kress_setting":1.5,
               },
                "aluminium":{
                        "vertfeed":50,
                        "sidefeed":950,
                        "stepdown":0.3,
                        "kress_setting":1,
               },
		
                "copper":{
                        "vertfeed":20,
                        "sidefeed":500,
                        "stepdown":0.2,
                        "kress_setting":3,
			"mill_dir":'down',
               },
                "brass":{
                        "vertfeed":20,
                        "sidefeed":500,
                        "stepdown":0.2,
                        "kress_setting":3,
			"mill_dir":'down',
               },
                "steel":{
                        "vertfeed":20,
                        "sidefeed":500,
                        "stepdown":0.2,
                        "kress_setting":3,
			"mill_dir":'down',
               },
                "polypropelene":{
                        "vertfeed":100,
                        "sidefeed":700,
                        "stepdown":2.0,
                        "kress_setting":1.5,
			"mill_dir":'up',
               },
                "polyethene":{
                        "vertfeed":100,
                        "sidefeed":700,
                        "stepdown":2.0,
                        "kress_setting":1.5,
			"mill_dir":'up',
               },
                "pvc":{
                        "vertfeed":100,
                        "sidefeed":700,
                        "stepdown":2.0,
                        "kress_setting":1.5,
			"mill_dir":'up',
               },
                "abs":{
                        "vertfeed":100,
                        "sidefeed":900,
                        "stepdown":2.0,
                        "kress_setting":1.5,
               },
               "pcb":{
                        "vertfeed":100,
                        "sidefeed":300,
                        "stepdown":2.0,
                        "kress_setting":3.0,
               },
	       "paper":{
                        "vertfeed":100,
                        "sidefeed":300,
                        "stepdown":2.0,
                        "kress_setting":3.0,
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
                },
                'M12':{
                        'diam':12.0,
                        'tap':10.0,
			'clearance':13.0,
                        'hex':{
                                'head_d':18.0,
                                'head_l':12.0,
                        },
                        'button':{
                                'head_d':21.0,
                                'head_l':6.6,
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
			}
                },
                "M5":{
                        "diams":[6.5,3.95],
                        "depths":[-1,False],
                },
		"M6":{
                        "diams":[7,4.25], #Edited db from 6mm dia... these are also radii...
                        "depths":[-1,False],
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
