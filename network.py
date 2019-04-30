from math import *
from path import *
from shapes import *

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
		if 'radius' in config:
			self.radius=config['radius']
		else:
			self.radius=None
		if 'intRadius' in config:
			self.intRadius=config['intRadius']
		else:
			self.intRadius=None
		if 'holeRad' in config:
			self.holeRad=config['holeRad']
		else:
			self.holeRad=None
		if 'endType' in config:
			self.endType=config['endType']
		else:
			self.endType=None
		if 'note' in config:
			self.note=config['note']
		else:
			self.note=""
		self.connections=[]

	def sort_connections(self):
		self.connections.sort(key=self.sort_func)
		i=0
		for conn in self.connections:
			conn.order=i
			i+=1

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
	def add_conn( self, othernode, **config):
		self.add(Connection(self, othernode, **config))
	
	def add(self, connection, rev=False):
		assert(connection.this.pos != connection.other.pos)
		brother = Connection(connection.other, self, connection.width, connection)
			
		if not rev and not connection.other.has_connection(self):
			connection.other.add(brother, True)
			connection.brother=brother
		if not self.has_connection(connection.other):
			self.connections.append(connection)
		else:
			self.has_connection(connection.other).brother = self		
class Connection:

	def __init__(self, this, other, width=None, brother=None, **config):
		self.other=other
		self.this=this
		self.width=width
		self.brother = brother
		self.order = None
		if 'intRadius' in config:
			self.intRadius=config['intRadius']
		else:
			self.intRadius=None
#		self.append(this)
#		self.append(other)
		assert other is not None

class NetworkPart(Part):
	def __init__(self, netlist, **config):
		self.init(config)
		self.ignore_border=True
		for path in netlist:
			if path==netlist.border:
				self.add_border(path)
			else:
				self.add(path)
		for path in netlist.otherpaths:
			self.add(path)
class Network(list):
	def __init__(self, defaultWidth, **config):
		#self.init(config)
		self.defaultWidth=defaultWidth
		self.nodes = []
		self.loops = []
		self.connections = []
		if 'intRadius' in config:
			self.intRadius=config['intRadius']
		else:
			self.intRadius=None
		self.otherpaths = []
		self.border = None
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
		next_connection = otherNode.connections[ (connection.brother.order + 1)%len(otherNode.connections)]
		if next_connection !=first:
			loop.extend(self.get_loop(next_connection, first=first))
		if connection in self.connections:
			self.connections.remove(connection)
		return loop

# Work along all connections in self.connections forming loops. As all connections exist in two directions they should all appear twice 
	def make_loops(self):
		self.gather_connections()
		while(len(self.connections)):
			self.loops.append(self.get_loop(self.connections.pop()))
	def get_width(self,connection, node):
		if connection.width is not None:
			return connection.width
		if node.width is not None:
			return node.width
		return self.defaultWidth

	def get_intRadius(self,connection, node):
		if connection.intRadius is not None:
			return connection.intRadius
		if node.intRadius is not None:
			return node.intRadius
		return self.intRadius

	def corner_pos(self, connection1, connection2, lastConnection):
		"""Will work out where the corner of the cut edge should go between two adjacent connections"""
		d1=(connection1.this.pos - connection1.other.pos).normalize()
		d2=(connection2.other.pos - connection1.other.pos).normalize()
		w1=self.get_width(connection1,connection1.other)/2
		w2=self.get_width(connection2,connection2.this)/2

		if abs(d1.dot(d2) +1) < 0.0001:
			b=0
	# catch case when it is the end of a single rod
		elif abs(d1.dot(d2) -1) < 0.0001:
			b=0
			return [w2*rotate(d1,90), w2*rotate(d1,-90)]
		else:
			if (d1[1]*d2[0]-d1[0]*d2[1])==0:
				print d1
				print d2
				raise ValueError("connections in the same place"+str(connection1.this.pos )+" "+str(connection1.other.pos)+" "+str(connection2.other.pos))
			b = (d2[0]*d1[0]*w2 + w1*d1[0]**2 + w1*d1[1]**2 + w2*d1[1]*d2[1]) / (d1[1]*d2[0]-d1[0]*d2[1])
# rotate direction can be correct if connection1 &2 are always in same rotational order
		return ( b*d1 + w2*rotate(d1,90))

	def make_path(self, loop):
		"""Create a path from a single loop"""
		path=Path(closed=True)
		for c in range(0,len(loop)):
			connection=loop[c]
			nextConnection = loop[(c+1)%len(loop)]
			lastConnection = loop[(c-1)%len(loop)]
			corner_offset = self.corner_pos(connection, nextConnection, lastConnection)
	# catch case when it is the end of a single rod
			if type(corner_offset) is list:
				endpoints = corner_offset
				corner_offset = endpoints[0]
			else:
				endpoints = False
		#	print corner_offset
			print "ENDTYPE "+str(connection.this.note)+"->"+str(connection.other.note)+"Q="+str(connection.this.endType)+" "+str(connection.other.endType)+" "+str(endpoints)
			if connection.other.radius is not None and corner_offset.length() < connection.other.radius:
	# catch case when it is the end of a single rod
				if endpoints:
					para=(connection.this.pos-connection.other.pos).normalize()
					d = math.sqrt(connection.other.radius**2 - corner_offset.length()**2)
					path.add_point(PSharp(connection.other.pos + corner_offset + d*para))
					path.add_point(PArc(connection.other.pos, radius=connection.other.radius, direction='cw'))
					path.add_point(PSharp(connection.other.pos - corner_offset+d*para))
#					path.add_point(PAroundcurve(connection.other.pos + corner_offset, centre=connection.other.pos, radius=connection.other.radius, direction='cw'))
#					path.add_point(PSharp(connection.other.pos+endpoints[1]*connection.other.radius))
#					path.add_point(PAroundcurve(connection.other.pos + endpoints[2], centre=connection.other.pos, radius=connection.other.radius, direction='cw'))
					print "a"	
				else:
#					if connection.this.endType=='incurve':
#						PIncurve(connection.
					path.add_point(PAroundcurve(connection.other.pos + corner_offset, centre=connection.other.pos, radius=connection.other.radius, direction='cw'))
					print "b"
			elif self.get_intRadius(connection, connection.other) is not None:
				path.add_point(PIncurve(connection.other.pos + corner_offset, radius=self.get_intRadius(connection, connection.other)))
				path.add_point(PIncurve(connection.other.pos - corner_offset, radius=self.get_intRadius(connection, connection.other)))
				print "c"
			else:
				print "d"
				cornerpos = self.corner_pos(connection, nextConnection, lastConnection)
				print "cornerpos="+str(cornerpos)
				if type(cornerpos) is list:
					path.add_point(PSharp(connection.other.pos + cornerpos[0]))
					path.add_point(PSharp(connection.other.pos + cornerpos[1]))
				else:
					path.add_point(PSharp(connection.other.pos + self.corner_pos(connection, nextConnection, lastConnection)))
					path.add_point(PSharp(connection.other.pos - self.corner_pos(connection, nextConnection, lastConnection)))
			if connection.other.holeRad is not None:
				if type(connection.other.holeRad) is int or type(connection.other.holeRad) is float:
					self.otherpaths.append(Circle(connection.other.pos, rad=connection.other.holeRad, side='in'))
				else:
					t=copy.deepcopy(connection.other.holeRad)
					t.translate(connection.other.pos)
					self.otherpaths.append(t)
		return path

	def make_paths(self):
		self.make_loops()
		for loop in self.loops:
			self.append(self.make_path(loop))
		self.find_border()

	def find_border(self):
		if len(self)==1:
			self[0].side='out'
			self.border = self[0]

		for p in range(0,len(self)):
			path = self[p]
			nextPath = self[(p+1)%len(self)]
			if path.contains(nextPath)>0:
				path.side='out'
				self.border = path
			else:
				path.side='in'

class NetLine(Pathgroup):
	def __init__(self, points, width, **config):
		self.init(config)
		if 'rad' not in config:
			config['rad']=width/2+0.01
		self.network = Network(width)
		lastnode = False
		for p in points:
			node=self.network.add(Node(p))
			if lastnode is not False:
				node.add_conn(lastnode)
			lastnode=node
		self.network.make_paths()	
		for path in self.network:
			self.add(path)
