class Milling:
	def __init__(self):

		self.mode_config={
                        "dave-emc":{
                                'prefix':'M03\nG0Z10',
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
				'z_overshoot':0.5,
				'label':False,
                        },
                        'eagle':{
                                'prefix':'GRID MM\nLAYER 21\n',
				'normal_layer':21, #tPlace
				'border_layer':20, #dimension
				'postfix':'',
                                'mode':'scr',
                                'group':False,
                                'toolchange':'none',
				'mirror_backs':False,
				'overview':False,
				'clear_height':10,
				'precut_z':1,
				'hide_cuts':True,
				'file_suffix':'.scr',
				'comments':False,
				'dosfile':True,
				'label':False,
			},
                        'makespacerouter':{
                                'prefix':'T1M6\nG17\nG0Z10S11000M3\n',
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
				'z_overshoot':0.5,
				'label':False,
                        },
                        'laser':{
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
				'label':False,
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
                        },
                        'diagram':{
                                'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n<svg width="594mm" height="420mm"\n     xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 594 420">\n<g transform="scale(1, -1) translate(0,-420)">',
                                'postfix':'</g>\n</svg>\n',
                                'mode':'svg',
				'group':False,
                                'forcestepdown':1000,
				'mirror_backs':False,
				'overview':True,
				'hide_cuts':True,
				'z_overshoot':0,
				'label':True,
                        },
                        'visualise':{
                                'prefix':'<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" \n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n<svg width="594mm" height="420mm"\n     xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 594 420">\n<g transform="scale(1, -1) translate(0,-420)">',
                                'postfix':'</g>\n</svg>\n',
                                'mode':'svg',
				'group':False,
                                'forcestepdown':1000,
				'mirror_backs':False,
				'overview':True,
				'hide_cuts':False,
				'z_overshoot':0,
				'label':True,
				
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
                "16mm_mill":{
                        "id":5,
                        "diameter":16,
                        "endcut":1,

                        "sidecut":1,
                },
                "6mm_endmill":{
                        "id":2,
                        "diameter":6,
                        "endcut":1,

                        "sidecut":1,
                },
                "2mm_endmill":{
                        "id":8,
                        "diameter":2,
                        "endcut":1,
                        "sidecut":1,
                },
                "3mm_endmill":{
                        "id":2,
                        "diameter":3,
                        "endcut":1,
                        "sidecut":1,
                },
                "4mm_endmill":{
                        "id":9,
                        "diameter":4,
                        "endcut":1,
                        "sidecut":1,
                },
                "8mm_endmill":{
                        "id":7,
                        "diameter":8,
                        "endcut":1,
                        "sidecut":1,
                },
                "1mm_endmill":{
                        "id":4,
                        "diameter":1,
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
                        "diameter":13,
                        "endcut":1,
                        "sidecut":1,
			"min_diameter":2,
			"angle":45,
                },
                "1mm_drill":{
                        "id":12,
                        "diameter":1,
                        "endcut":1,
                        "sidecut":1,
                },
               "0.5mm_drill":{
                        "id":13,
                        "diameter":0.5,
                        "endcut":1,
                        "sidecut":1,
                },
                "1.54mm_drill":{
                        "id":16,
                        "diameter":1.54,
                        "endcut":1,
                        "sidecut":1,
                },
                "ovolo":{
                        "id":16,
                        "diameter":10,
                        "endcut":1,
                        "sidecut":1,
                },
		"bevel_trim":{
			"id":17,
			"diameter":6.35,
			"endcut":0,
			"sidecut":1,
			"angle":17/2,
			"sidestep":0.5,
		}
		}
		self.materials = {
                "plywood":{
                        "vertfeed":200,
                        "sidefeed":800,
                        "stepdown":5,
                        "kress_setting":4,
                        "spring":0.3,

                },
                "mdf":{
                        "vertfeed":200,
                        "sidefeed":800,
                        "stepdown":3.5,
                        "kress_setting":4,
                        "spring":0.3,

                },

                "perspex":{
                        "vertfeed":120,
                        "sidefeed":600,
                        "stepdown":1.5,
                        "kress_setting":2,

                },
                "polycarbonate":{
                        "vertfeed":120,
                        "sidefeed":400,
                        "stepdown":2,
                        "kress_setting":2,

                },
                "delrin":{
                        "vertfeed":120,
                        "sidefeed":700,
                        "stepdown":1.5,
                        "kress_setting":2,

                },
                "tufnol":{
                        "vertfeed":100,
                        "sidefeed":400,
                        "stepdown":1.5,
                        "kress_setting":2,
               },
                "HIPS":{
                        "vertfeed":100,
                        "sidefeed":500,
                        "stepdown":3,
                        "kress_setting":1.5,
               },
                "aluminium":{
                        "vertfeed":50,
                        "sidefeed":950,
                        "stepdown":0.2,
                        "kress_setting":1,
               },
                "pvc":{
                        "vertfeed":100,
                        "sidefeed":700,
                        "stepdown":2,
                        "kress_setting":1.5,
               },
               "pcb":{
                        "vertfeed":100,
                        "sidefeed":300,
                        "stepdown":2,
                        "kress_setting":3,
               }
	}
		self.bolts={
	                'M3':{
                        'diam':3,
                        'tap':2.5,
			'clearance':4,
                        'allen':{
                                'head_d':5.5,
                                'head_l':3,
                        },
                        'button':{
                                'head_d':5.7,
                                'head_l':1.65,
                        },
                },
                'M4':{
                        'diam':4,
                        'tap':3.3,
			'clearance':5,
                        'allen':{
                                'head_d':7,
                                'head_l':4,
                        },
                        'button':{
                                'head_d':7.6,
                                'head_l':2.2,
                        },
                },
                'M5':{
                        'diam':5,
                        'tap':4.2,
			'clearance':6,
                        'allen':{
                                'head_d':8.5,
                                'head_l':5,
                        },
                        'button':{
                                'head_d':9.5,
                                'head_l':2.75,
                        },
                },
                'M6':{
                        'diam':6,
                        'tap':5,
			'clearance':7,
                        'allen':{
                                'head_d':10,
                                'head_l':6,
                        },
                        'button':{
                                'head_d':10.5,
                                'head_l':3.3,
                        },
                },
                'M8':{
                        'diam':8,
                        'tap':6.5,
			'clearance':9,
                        'allen':{
                                'head_d':13,
                                'head_l':8,
                        },
                        'button':{
                                'head_d':14,
                                'head_l':4.4,
                        },
                },
                'M10':{
                        'diam':10,
                        'tap':8.4,
			'clearance':11,
                        'hex':{
                                'head_d':16,
                                'head_l':10,
                        },
                        'button':{
                                'head_d':17.5,
                                'head_l':5.5,
                        },
                },
                'M12':{
                        'diam':12,
                        'tap':10,
			'clearance':13,
                        'hex':{
                                'head_d':18,
                                'head_l':12,
                        },
                        'button':{
                                'head_d':21,
                                'head_l':6.6,
                        },
                },
                'M14':{
                        'diam':14,
                        'tap':12,
			'clearance':15,
                        'hex':{
                                'head_d':21,
                                'head_l':14,
                        },
                },
                'M16':{
                        'diam':16,
                        'tap':13,
			'clearance':19,
                        'hex':{
                                'head_d':24,
                                'head_l':16,
                        },
                        'button':{
                                'head_d':28,
                                'head_l':8.8,
                        },
                },
                'M20':{
                        'diam':20,
                        'tap':17.5,
			'clearance':21,
                        'hex':{
                                'head_d':30,
                                'head_l':20,
                        },
                },
                '1/4BSP':{
                        'diam':13,
                        'tap':11.6,
                        'hex':{
                                'head_d':19.3,
                                'head_sl':6,
                        },
                        'shoulder':{
                                'diam':18,
                                'length':1.8,
                        },
                },

	}
		self.inserts={
		"M4":{
                        "diams":[5,3.05],
                        "depths":[-1,False],
			'hammer':{
					"diams":[14.2/2,10/2,5.7/2],
					"depths":[-1.5,-1.5,False]
				}
                },
                "M5":{
                        "diams":[6.5,3.95],
                        "depths":[-1,False],
                },
		"M6":{
                        "diams":[7,3.05],
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
