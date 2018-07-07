from path import *
from math import *

class Node:
	def __init__(self, pos, **config):
		self.pos=pos
		if 'type' in config:
			self.type=config['type']
		else:
			self.type=PSharp(pos)
		if 'width' in config:
			self.width=config['width']
		else:
			self.width=None
		self.connections=[]

	def sort_connections(self):
		self.connections.sort(key=self.sort_func)
		i=0
		for conn in self.connections:
			conn.order=i
			i+=1
		
	def sort_func(self, connection):
		p1=self.pos
		p2=connection.other.pos
		v = p2-p1
		return math.atan2(v[0], v[1])
	
	def add(self, connection, rev=False):
		brother = Connection(self, connection.this, connection.width, connection)
		print connection
			
		if not rev:
			connection.other.add(brother, True)
		connection.brother=brother
		self.connections.append(connection)
	
class Connection(list):

	def __init__(self, this, other, width=None, brother=None):
		self.other=other
		self.this=this
		self.width=width
		self.brother = brother
		self.order = None
		self.append(this)
		self.append(other)

class NetworkPart(Part):
	def __init__(self, netlist, **config):
		self.init(config)
		for path in netlist:
			if path==netlist.border:
				self.add_border(path)
			else:
				self.add(path)

class Network(list):
	def __init__(self, defaultWidth, **config):
		#self.init(config)
		self.defaultWidth=defaultWidth
		self.nodes = []
		self.loops = []
		self.connections = []

	def add(self,node):
		self.nodes.append(node)
		return node
# gather all connections from all nodes
	def gather_connections(self):
		self.connections=[]
		for node in self.nodes:
			node.sort_connections()
			self.connections.extend(node.connections)

# Work one place around a loop
	def get_loop(self, connection, first=None):
		loop=[]
		if first==None:
			first = connection
		loop.append(connection)	
		otherNode = connection.other
		print connection.order
		print connection.brother
		print connection.brother.order
		print otherpos
		next_connection = otherNode.connections[ connection.brother.order + 1]
		if next_connection !=first:
			loop.extend(self.get_loop(next_connection, first=first))
		self.connections.remove(connection)
		return loop

# Work along all connections in self.connections forming loops. As all connections exist in two directions they should all appear twice 
	def make_loops(self):
		self.gather_connections()					
		while(len(self.connections)):
			self.loops.append(self.get_loop(self.connections.pop()))
			
	def get_width(self,connection, part):
		if connection.width is not None:
			return connection.width
		if connection[part].width is not None:
			return connection[part].width
		return self.defaultWidth

	def corner_pos(self, connection1, connection2):
		d1=(connection1[0].pos - connection1[1].pos).normalize()
		d2=(connection2[1].pos - connection1[1].pos).normalize()
		w1=self.get_width(connection1,1)/2
		w2=self.get_width(connection2,0)/2
		b = (d1[0]*d2[0]*w2 + w1*d1[0]**2 - w1*d1[1]**2 - w2*d1[1]*d2[1]) / (d1[1]*d2[0]-d1[0]*d2[1])
# rotate direction can be correct if connection1 &2 are always in same rotational order
		return connection1[1].pos + b*d2 + w2*rotate(d2,90)

	def make_path(self, loop):
		path=Path(closed=True)
		for c in range(0,len(loop)):
			connection=loop[c]
			nextConnection = loop[(c+1)%len(loop)]
			path.add_point(PSharp(connection[1].pos + self.corner_pos(connection, nextConnection)))
		return Path

	def make_paths(self):
		self.make_loops()
		for loop in self.loops:
			self.append(make_path(loop))
		self.find_border()

	def find_border(self):
		for p in range(0,len(self)):
			path = self[p]
			nextPath = self[(p+1)%len(self)]
			if path.contains(nextPath):
				path.side='out'
				self.border = path
			else:
				path.side='in'
			
