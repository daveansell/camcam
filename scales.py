from path import *
from shapes import *
from font import *
class Gauge(Pathgroup):
	def __init__(self, pos, outerrad, ticRads, startAngle, gaugeAngle, numTics, **config):
		self.init(config)
		self.translate(pos)
		if 'ticWidths' in config:
			ticWidths = config['shortTicWidth']
		else:
			ticWidths = []
			for r in ticRads:
				ticWidths.append( (float(outerrad) -r)/8 )
		if 'textRad' in config:
			textRad = config['textRad']
		else:
			textRad = False
		if 'textValues' in config:
			textValues = config['textValues']
			assert type(textValues) is dict
		else:
			textValues = {}
		if 'textScale' in config:
			textScale = config['textScale']
		else:
			textScale = 0.05
		totalTics = [1]
		for n in range(0,len(numTics)):
			for i in range(0,len(totalTics)):
				totalTics[i] *= numTics[n]
			totalTics.append(1)
		print numTics
		print totalTics
		print ticWidths
		smallStep = gaugeAngle/totalTics[0]
		for i in range(0, totalTics[0]+1):
			for t in range(0,len(totalTics)):
				 if i%totalTics[t+1]==0:
					t=self.add(Rect(V(0,(ticRads[t]+outerrad)/2), centred=True, width=ticWidths[t], height=outerrad -ticRads[t]))
					t.rotate(V(0,0), i*smallStep+startAngle)
					break
			if i in textValues:
				self.add(Text(rotate(V(0, textRad), i*smallStep+startAngle), str(textValues[i]), side='in', scale=textScale, centred=True))
		
