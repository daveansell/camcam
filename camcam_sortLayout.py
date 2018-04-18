#!/usr/bin/python
import json
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-m", "--mode", dest="mode",
                  help="sort type, x, y,  centre, edge first")
(options, args) = parser.parse_args()

print args
print options
filename=args[0]
print filename
fin=open(filename,'r')
data = json.loads(fin.read())
print data
def makeKey(a):
	print options
	if options.mode == 'y':
		return a['translate'][1]*100000 + a['translate'][0]
	if options.mode == 'centre':
		return (a['translate'][0]-cx[s])**2 + (a['translate'][1]-cy[s])**2
	if options.mode == 'edge':
		return -((a['translate'][0]-cx[s])**2 + (a['translate'][1]-cy[s])**2)
	#if options['mode'] == 'x':
	return a['translate'][0]*100000 + a['translate'][1]

print data['sheets'].keys()
minx={}
maxx={}
miny={}
maxy={}
cx={}
cy={}
for s in data['sheets']:
	minx[s]=10000
	maxx[s]=-10000
	miny[s]=10000
	maxy[s]=-10000
	print s
	for r in data['sheets'][s]:
		print r
		minx[s]=min(r['translate'][0], minx[s])
		miny[s]=min(r['translate'][1], miny[s])
		maxx[s]=max(r['translate'][0], maxx[s])
		maxy[s]=max(r['translate'][1], maxy[s])
	cx[s]= (minx[s]+maxx[s])/2	
	cy[s]= (miny[s]+maxy[s])/2	

for s in data['sheets']:
	
	data['sheets'][s].sort(key=makeKey)
for s in data['sheets']:
	for r in data['sheets'][s]:
		print r['translate']
fout =open(filename+'.sorted', 'w')

fout.write(json.dumps(data, indent=4))
