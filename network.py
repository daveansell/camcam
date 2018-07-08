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
		for conn in self.connections:
			print "sort="+str(conn)+"order="+str( conn.order)

	def has_connection(self, node):
		for conn in self.connections:	
			if conn.other == node:
				return conn
		return False
	
	def sort_func(self, connection):
		p1=self.pos
		p2=connection.other.pos
		v = p2-p1
		return math.atan2(v[0], v[1])
	
	def add(self, connection, rev=False):
		brother = Connection(connection.other, self, connection.width, connection)
		print "add connection "+str(connection)+" "+str(rev)+" this "+str(connection.this)+" other="+str(connection.other)
			
		if not rev and not connection.other.has_connection(self):
			connection.other.add(brother, True)
			connection.brother=brother
		if not self.has_connection(connection.other):
			self.connections.append(connection)
		else:
			self.has_connection(connection.other).brother = self		
class Connection:

	def __init__(self, this, other, width=None, brother=None):
		self.other=other
		print str(self)+'this='+str(this)+"other="+str(other)+" self.other="+str(self.other)
		self.this=this
		self.width=width
		self.brother = brother
		self.order = None
#		self.append(this)
#		self.append(other)
		assert other is not None

class NetworkPart(Part):
	def __init__(self, netlist, **config):
		self.init(config)
		self.ignore_border=True
		for path in netlist:
			print path
			print "PATH"
			for pnt in path.points:
				print pnt.pos
			if path==netlist.border:
				print "border"
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
			print "NODE="+str(node)
			node.sort_connections()
			print node.connections
			self.connections.extend(node.connections)
# Work one place around a loop
	def get_loop(self, connection, first=None):
		loop=[]
		if first==None:
			first = connection
		loop.append(connection)	
		otherNode = connection.other
		next_connection = otherNode.connections[ (connection.brother.order + 1)%len(otherNode.connections)]
		if next_connection !=first:
			loop.extend(self.get_loop(next_connection, first=first))
		if connection in self.connections:
			self.connections.remove(connection)
		return loop

# Work along all connections in self.connections forming loops. As all connections exist in two directions they should all appear twice 
	def make_loops(self):
		self.gather_connections()
		print "MAkr loops"
		print self.connections					
		while(len(self.connections)):
			self.loops.append(self.get_loop(self.connections.pop()))
		print "loops"+str(self.loops)	
	def get_width(self,connection, node):
		if connection.width is not None:
			return connection.width
		if node.width is not None:
			return connection[part].width
		return self.defaultWidth

	def corner_pos(self, connection1, connection2):
		d1=(connection1.this.pos - connection1.other.pos).normalize()
		d2=(connection2.other.pos - connection1.other.pos).normalize()
		w1=self.get_width(connection1,connection1.other)/2
		w2=self.get_width(connection2,connection2.this)/2
#		print " 1.this="+str(connection1.this.pos)+" 1.other="+str(connection1.other.pos)+" 2.this="+str(connection2.this.pos)+" 2.other="+str(connection2.other.pos)
		print "d1="+str(d1)+" d2="+str(d2) + " w1="+str(w1)+ " w2="+str(w2)
		b = (d1[0]*d2[0]*w2 + w1*d1[0]**2 - w1*d1[1]**2 - w2*d1[1]*d2[1]) / (d1[1]*d2[0]-d1[0]*d2[1])
# rotate direction can be correct if connection1 &2 are always in same rotational order
		print "b="+str(b)+" offset="+str(b*d2 + w2*rotate(d2,-90))
		return connection1.other.pos - b*d1 + w2*rotate(d1,90)

	def make_path(self, loop):
		path=Path(closed=True)
		print
		for c in range(0,len(loop)):
			connection=loop[c]
			nextConnection = loop[(c+1)%len(loop)]
			path.add_point(PSharp(connection.other.pos + self.corner_pos(connection, nextConnection)))
		return path

	def make_paths(self):
		self.make_loops()
		for loop in self.loops:
			self.append(self.make_path(loop))
		self.find_border()

	def find_border(self):
		for p in range(0,len(self)):
			path = self[p]
			nextPath = self[(p+1)%len(self)]
			print path
			print nextPath
			if path.contains(nextPath):
				path.side='out'
				self.border = path
			else:
				path.side='in'
			
