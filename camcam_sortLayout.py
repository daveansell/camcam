#!/usr/bin/python
import json
import sys

filename=sys.argv[1]
fin=open(filename,'r')
data = json.loads(fin.read())
print data
def makeKey(a):
	print a
	return a['translate'][0]*100000 + a['translate'][1]

print data['sheets'].keys()
for s in data['sheets']:
	
	data['sheets'][s].sort(key=makeKey)
for s in data['sheets']:
	for r in data['sheets'][s]:
		print r['translate']
fout =open(filename+'.sorted', 'w')

fout.write(json.dumps(data, indent=4))
