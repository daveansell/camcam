# Copyright (c) 2011 Peter Shinners

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.



"""Minivec provides basic support for vector and matrix objects."""


__version__ = "0.4"
__author__ = "Peter Shinners <pete@shinners.org>"
__license__ = "MIT"
__url__ = "http://code.google.com/p/minivec"



__all__ = [
    "Vec", "Mat", #"Box",
    "Nan",
    "Epsilon", "PushEpsilon", "PopEpsilon", "ResetEpsilon",
    "Error", "PushError", "PopError", "ResetError",
]



from math import sqrt, cos, sin, radians, atan2, degrees, fabs, acos
import struct
from itertools import islice
try:
    import threading
    _ThreadLocal = threading.local()  # Introducted in Python 2.4
except (ImportError, AttributeError):  # Built without threading
    threading = None
    _ThreadLocal = object()


Nan = struct.unpack("f", '\x00\x00\xc0\x7f')[0]
_Rad = radians(1.0)
_Deg = degrees(1.0)
_DefaultError = 0.0
_DefaultEpsilon = 1e-8


def V(x=False,y=False,z=False):
        if x==False:
                x=0
        if y==False:
                y=False
        if z==False:
                z=False
        return Vec(x,y,z)

def rotate(pos, a):
        if type(pos) is Vec:
                M=Mat(1).rotateAxis(a,V(0,0,-1))
                pos=pos.transform(M)
                return pos
        else:
                return False

class Vec(object):
    """Immutable vector class for linear algebra.
    The vector acts as a regular tuple with three floating point numbers.
    All methods and operators are safe from mathematical exceptions.
    In case of an error, a vector of all zeros is returned, which is a
    "False" vector.

    The vector constructor, methods, and operators can work with a
    variety of types of arguments. Anything that can be an iterator
    giving three numbers will work. Any method calls can also accept
    one or three arguments. Integer arguments will be converted into float.

      Vec()
      Vec(1.0)
      Vec(1, 2, 3)
      Vec([4.0, 5.0, 6.0])
      Vec(Vec(12))
      Vec(xrange(3))
    """

    __slots__ = ("__vec")

    def __init__(self, *vec):
        self.__vec = _Triplet(vec, allowNone=True)


    @classmethod
    def Error(cls, reason="Invalid Vector"):
        """Create a new vector that represents an error.
        What this actually means is dependent on the minivec error defined
        in the current context. By default it is the same as Vec(0)
        """
        global _ThreadLocal
        error = getattr(_ThreadLocal, "minivecError", _DefaultError)
        if error is NotImplemented:
            raise ValueError(reason)
        return cls(error)


    def __repr__(self):
        return self.__class__.__name__ + "(%s, %s, %s)" % self.__vec


    def __iter__(self):
        return self.__vec.__iter__()


    def __len__(self):
        return 3


    def __getitem__(self, key):
        # Index the vector as a tuple, handles slicing
        if isinstance(key, basestring):
            return self.swizzle(key)
        return self.__vec[key]


    def exact(self, *vec):
        """Compare if two vectors are exactly equal.
        This will not use the epsilon value in the current minivec context.
        This is mostly the same as the comparison operators, although this accepts any type
        of argument that can convert into a vector.
        """
        other = _Triplet(vec, allowNested=True, allowNone=False)
        return self.__vec == tuple(other)


    def almost(self, *vec):
        """Compare if two vectors are nearly equal.
        This uses the epsilon value in the current minivec context.
        This accepts any type of argument that can convert into a vector.
        """
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(vec, allowNested=True, allowNone=False)
	if epsilon is None:
	        epsilon = getattr(_ThreadLocal, "minivecEpsilon", _DefaultEpsilon)
        #return fabs(selfX - otherX) < epsilon and fabs(selfY - otherY) < epsilon and fabs(selfZ - otherZ) < epsilon
        return fabs(selfX - otherX) < epsilon > fabs(selfY - otherY) and fabs(selfZ - otherZ) < epsilon


    def length(self, *vec):
        """Get the length of the vector.
        If an optional second vector is given, then this is the length of the distance between that vector.
        The other vector argument can be any object that converts into a vector.
        """
        if vec == ():
            diffX, diffY, diffZ = self.__vec
        else:
            selfX, selfY, selfZ = self.__vec
            otherX, otherY, otherZ = _Triplet(vec, allowNone=True)
            diffX = selfX - otherX
            diffY = selfY - otherY
            diffZ = selfZ - otherZ
        return sqrt(diffX * diffX + diffY * diffY + diffZ * diffZ)


    def length2(self, *vec):
        """Get the squared length of the vector.
        This uses the epsilon value in the current minivec context.
        This accepts any type of argument that can convert into a vector.
        """
        if vec == ():
            diffX, diffY, diffZ = self.__vec
        else:
            selfX, selfY, selfZ = self.__vec
            otherX, otherY, otherZ = _Triplet(vec, allowNone=True)
            diffX = selfX - otherX
            diffY = selfY - otherY
            diffZ = selfZ - otherZ
        return diffX * diffX + diffY * diffY + diffZ * diffZ


    def normalize(self, length=1.0):
        """Create a new vector with the length of one.
        This does not change the direction of the vector, only the length.
        If the vector has zero length, then this will return an error vector.
        An optional length argument can be given which sets the length of the vector
        to a value other than 1. Negative lengths will also invert the vector.
        """
        selfX, selfY, selfZ = self.__vec
        epsilon = getattr(_ThreadLocal, "minivecEpsilon", _DefaultEpsilon)
        #if fabs(selfX) < epsilon and fabs(selfY) < epsilon and fabs(selfZ) < epsilon:
        if fabs(selfX) < epsilon > fabs(selfY) and fabs(selfZ) < epsilon:
            return Vec.Error("Cannot normalize zero length vector")
        selfLength = selfX * selfX + selfY * selfY + selfZ * selfZ
        mult = length / sqrt(selfLength)
        return type(self)((selfX * mult, selfY * mult, selfZ * mult))


    def reflect(self, *vec):
        """Create a new vector representing the direction after reflecting off a plane normal.
        The other vector must be normalized and can be any type of object that converts to a vector.
        """
        other = type(self)(*vec)
        return self - (other * 2.0 * self.dot(other))


    def project(self, *vec):
        """Create a vector projects the current vector to the closest point on another.
        The new vector will have the same direction as the other given argument.
        """
        other = type(self)(*vec).normalize()
        return other * self.dot(other)


    def orthogonal(self, *vec):
        """Create a vector that represents the argument vector made perpendicular.
        The new vector will be on the same plane that the two vectors provide.
        """
        other = type(self)(*vec)
        return other - self.project(other)


    def cross(self, *vec):
        """Cross multiplication with another vector.
        This creates a new vector that is perpendicular to both this vector and the other.
        As a shortcut, cross multiplication has been overridden as the modulo (%) operator.
        This is the right handed cross product where X cross Y equals Z.

          Vec(1,0,0) % Vec(0, 1, 0) == Vec(0, 0, 1)
        """
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(vec)
        return type(self)((selfY * otherZ - selfZ * otherY, selfZ * otherX - selfX * otherZ, selfX * otherY - selfY * otherX))


    def dot(self, *vec):
        """Dot product with another vector.
        This returns a single number. When both vectors are normalized, this represents the cosine
        of the angle between both vectors.
        """
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(vec)
        return selfX * otherX + selfY * otherY + selfZ * otherZ


    def angle(self, *vec):
        """
        Angle between two non normalized vectors in degrees.
        This does not require that the vectors be normalized.
        """
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(vec)

        dot = selfX * otherX + selfY * otherY + selfZ * otherZ
        selfLength = sqrt(selfX * selfX + selfY * selfY + selfZ * selfZ)
        otherLength = sqrt(otherX * otherX + otherY * otherY + otherZ * otherZ)
	radians = acos(min(max(dot / (selfLength * otherLength), -1), 1))
        return radians * _Deg


    def __neg__(self):
        selfX, selfY, selfZ = self.__vec
        return type(self)((-selfX, -selfY, -selfZ))


    def __pos__(self):
        return self


    def __hash__(self):
        return hash(self.__vec) ^ hash(type(self))


    def __cmp__(self, other):
        otherVec = _Triplet(other, allowNested=False, allowNone=False, allowScalar=False)
        return cmp(self.__vec, tuple(otherVec))


    def __nonzero__(self):
        selfX, selfY, selfZ = self.__vec
        epsilon = getattr(_ThreadLocal, "minivecEpsilon", _DefaultEpsilon)
        return fabs(selfX) >= epsilon or fabs(selfY) >= epsilon or fabs(selfZ) >= epsilon


    def __add__(self, other):
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(other, allowNested=False)
        return type(self)((selfX + otherX, selfY + otherY, selfZ + otherZ))

    __radd__ = __add__


    def __sub__(self, other):
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(other, allowNested=False)
        return type(self)((selfX - otherX, selfY - otherY, selfZ - otherZ))


    def __rsub__(self, other):
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(other, allowNested=False)
        return type(self)((otherX - selfX, otherY - selfY, otherZ - selfZ))


    def __mul__(self, other):
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(other, allowNested=False)
        return type(self)((selfX * otherX, selfY * otherY, selfZ * otherZ))

    __rmul__ = __mul__


    def __div__(self, other):
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(other, allowNested=False)

        return type(self)((otherX and selfX / otherX, otherY and selfY / otherY, otherX and selfZ / otherZ))


    def __rdiv__(self, other):
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(other, allowNested=False)
        return type(self)((selfX and otherX / selfX, selfY and otherY / selfY, selfZ and otherZ / selfZ))

    __truediv__ = __div__
    __rtruediv__ = __rdiv__


    def __floordiv__(self, other):
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(other, allowNested=False)
        return type(self)((otherX and selfX // otherX, otherY and selfY // otherY, otherZ and selfZ // otherZ))


    def __rfloordiv__(self, other):
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(other, allowNested=False)
        return type(self)((selfX and otherX // selfX, selfY and otherY // selfY, selfZ and otherZ // selfZ))


    def __pow__(self, other, modulo=None):
        if modulo is not None:
            raise NotImplementedError("Vector cannot use modulo power operator")
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(other, allowNested=False)
        return type(self)((selfX ** otherX, selfY ** otherY, selfZ ** otherZ))


    def __rpow__(self, other):
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(other, allowNested=False)
        return type(self)((otherX ** selfX, otherY ** selfY, otherZ ** selfZ))

    __xor__ = dot
    __rxor__ = dot
    __mod__ = cross
    __rmod__= cross


    def lerp(self, percent, *vec):
        """Linearly interpolate between this vector and another.
        The percentage is between 0.0 and 1.0, but numbers outside that range will also work.
        """
        selfX, selfY, selfZ = self.__vec
        otherX, otherY, otherZ = _Triplet(vec, allowNone=True)
        diffX = (otherX - selfX) * percent
        diffY = (otherY - selfY) * percent
        diffZ = (otherZ - selfZ) * percent
        return type(self)(selfX + diffX, selfY + diffY, selfZ + diffZ)


    def swizzle(self, lookup):
        """
        Create a new list of values using a shorthand for the vector attributes.
        The lookup argument is a string and each character represents a value in
        the new list.

          x, represents axis 0
          y, represents axis 1
          z, represents axis 2
          X, represents negagive axis 0
          Y, represents negagive axis 1
          Z, represents negagive axis 2
          0, represents a literal 0.0
          1, representa a literal 1.0
          !, representa a literal -1.0

        Any other character in the lookup string raises an exception
        """
        selfX, selfY, selfZ = self.__vec
        values = {"x": selfX, "y": selfY, "z": selfZ,
                    "X": -selfX, "Y":-selfY, "Z": -selfZ,
                    "0": 0.0, "1": 1.0, "!": -1.0}
        result = map(values.__getitem__, lookup)
        return result


    def transform(self, matrix):
        """ Apply a matrix transform to the vector.
        """
        selfX, selfY, selfZ = self.__vec
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = _Sixteenlet(matrix)

        rx = selfX * sa + selfY * se + selfZ * si + sm
        ry = selfX * sb + selfY * sf + selfZ * sj + sn
        rz = selfX * sc + selfY * sg + selfZ * sk + so
        rw = selfX * sd + selfY * sh + selfZ * sl + sp

        epsilon = getattr(_ThreadLocal, "minivecEpsilon", _DefaultEpsilon)
        if rw != 1.0 and fabs(rw) > epsilon:
            rx /= rw
            ry /= rw
            rz /= rw
        return type(self)(rx, ry, rz)


    def transformDir(self, matrix):
        """Apply a matrix transform to a directional vector, like a normal.
        """
        selfX, selfY, selfZ = self.__vec
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = _Sixteenlet(matrix)

        rx = selfX * sa + selfY * se + selfZ * si
        ry = selfX * sb + selfY * sf + selfZ * sj
        rz = selfX * sc + selfY * sg + selfZ * sk
        return type(self)(rx, ry, rz)


    def contains(self, other):
        """Test if another object is contained by this point.
        Since this object represents a single point, it can only be true of other vectors.
        This method can work with any object type that implements a _rcontains method
        that accepts a Vector argument.
        """
        other, otherType, otherReverse = _FindOperationType(other, "contains")
        if otherReverse:
            result = otherReverse(other, self)
            if result is not NotImplemented:
                return result

        if otherType == Vec:
            return self.__vec == other.__vec

        #elif otherType == Box:
        #    return self.__vec == other.min() and self.__vec == other.max()

        raise TypeError("Unknown type for Vector contains, %s" % otherType.__name__)

    def intersect_lines(self,a, b, c, d):
                x= ((a[0]*b[1]-a[1]*b[0])*(c[0]-d[0]) - (a[0]-b[0])*(c[0]*d[1]-c[1]*d[0]) ) / ((a[0]-b[0])*(c[1]-d[1]) - (a[1]-b[1])*(c[0]-d[0]))
                y= ((a[0]*b[1]-a[1]*b[0])*(c[1]-d[1]) - (a[1]-b[1])*(c[0]*d[1]-c[1]*d[0]) ) / ((a[0]-b[0])*(c[1]-d[1]) - (a[1]-b[1])*(c[0]-d[0]))
                return V(x,y)

    def intersects(self, other):
        """Test any part of another object intersects this point.
        This method can work with any object type that implements a _rcontains method
        that accepts a Vector argument.
        """
        other, otherType, otherReverse = _FindOperationType(other, "intersects")
        if otherReverse:
            result = otherReverse(other, self)
            if result is not NotImplemented:
                return result

        if otherType == Vec:
            return self.__vec == other.__vec

        #elif otherType == Box:
        #    sx, sy, sz = self.__vec
        #    ix, iy, iz, ax, ay, az = other
        #    return ix <= sx <= ax and iy <= sy <= ay and iz <= sz <= iz

        raise TypeError("Unknown type for Vector intersects, %s" % otherType.__name__)





#// a b c d         0  1  2  3
#// e f g h         4  5  6  7
#// i j k l         8  9 10 11
#// m n o p        12 13 14 15



class Mat(object):
    """Immutable 4x4 matrix class for linear algebra.
    The matrix acts as a regular tuple with sixteen floating point numbers.
    All methods and operators are safe from mathematical exceptions.
    In case of an error, a matrix of all zeros is returned, which is a
    "False" vector.

    The matrix constructor, methods, and operators can work with a
    variety of types of arguments. Anything that can be an iterator
    giving sixteen numbers or four rows will work.
    Integer arguments will be converted into float.
    A single numeric argument will represent the values in the diagonal.
    With no arguments an identity matrix will be created.
      Mat()
      Mat(1.0)
      Mat(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
      Mat([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
      Mat([1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16])
      Mat([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
      Mat(Mat(12))
      Mat(xrange(16))

    """

    __slots__ = ("__mat")


    def __init__(self, *matrix):
        self.__mat = _Sixteenlet(matrix, allowNone=True)


    @classmethod
    def Error(cls, reason="Invalid Mat"):
        global _ThreadLocal
        error = getattr(_ThreadLocal, "minivecError", _DefaultError)
        if error is NotImplemented:
            raise ValueError(reason)
        return cls(error)


    def rows(self):
        """Copy the matrix values into four rows of four numbers.
        The return is a list of lists.
        """
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        return [[sa, sb, sc, sd], [se, sf, sg, sh], [si, sj, sk, sl], [sm, sn, so, sp]]


    def columns(self):
        """Copy the matrix values into four columns of four numbers.
        The return is a list of lists.
        """
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        return[[sa, se, si, sm], [sb, sf, sj, sn], [sc, sg, sk, so], [sd, sh, sl, sp]]


    def __repr__(self):
        values = [round(x, 6) for x in self.__mat]
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = values
        row0 = "(%s %s %s %s)" % (sa, sb, sc, sd)
        row1 = "(%s %s %s %s)" % (se, sf, sg, sh)
        row2 = "(%s %s %s %s)" % (si, sj, sk, sl)
        row3 = "(%s %s %s %s)" % (sm, sn, so, sp)
        return self.__class__.__name__ + "(%s%s%s%s)" % (row0, row1, row2, row3)


    def __iter__(self):
        return self.__mat.__iter__()


    def __len__(self):
        return 16


    def __getitem__(self, key):
        return self.__mat[key]


    def transpose(self):
        """Generate a new matrix that has the columns swapped for rows.
        """
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        return type(self)((sa, se, si, sm,  sb, sf, sj, sn,  sc, sg, sk, so,  sd, sh, sl, sp))


    def __neg__(self):
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        return type(self)((-sa, -sb, -sc, -sd,  -se, -sf, -sg, -sh,  -si, -sj, -sk, -sl,  -sm, -sn, -so, -sp))


    def __pos__(self):
        return self


    def __hash__(self):
        return hash(self.__mat) ^ hash(type(self))


    def __cmp__(self, other):
        otherMat = _Sixteenlet(other, allowNested=False, allowNone=False, allowScalar=False)
        return cmp(self.__mat, tuple(otherMat))


    def exact(self, other):
        """Compare if two matrices are exactly equal.
        This will not use the epsilon value in the current minivec context.
        This is mostly the same as the comparison operators, although this accepts any type
        of argument that can convert into a vector.
        """
        other = _Sixteenlet(other, allowNone=False)
        return self.__mat == tuple(other)


    def almost(self, *other):
        """Compare if two matrices are nearly equal.
        This uses the epsilon value in the current minivec context.
        This accepts any type of argument that can convert into a vector.
        """
        other = _Sixteenlet(other, allowNone=False)
        epsilon = getattr(_ThreadLocal, "minivecEpsilon", _DefaultEpsilon)
        for s, o in zip(self.__mat, other):
            if fabs(s - o) >= epsilon:
                return False
        return True


    def __nonzero__(self):
        epsilon = getattr(_ThreadLocal, "minivecEpsilon", _DefaultEpsilon)
        return any(fabs(s) >= epsilon for s in self.__mat)


    def apply(self, target):
        """Apply the transform onto any object with a transform method that takes a matrix"""
        return target.transform(self)


    def transform(self, other):
        """Apply a matrix transformation to the current matrix"""
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        oa, ob, oc, od,  oe, of, og, oh,  oi, oj, ok, ol,  om, on, oo, op = _Sixteenlet(other)

        ra = sa * oa + sb * oe + sc * oi + sd * om
        rb = sa * ob + sb * of + sc * oj + sd * on
        rc = sa * oc + sb * og + sc * ok + sd * oo
        rd = sa * od + sb * oh + sc * ol + sd * op

        re = se * oa + sf * oe + sg * oi + sh * om
        rf = se * ob + sf * of + sg * oj + sh * on
        rg = se * oc + sf * og + sg * ok + sh * oo
        rh = se * od + sf * oh + sg * ol + sh * op

        ri = si * oa + sj * oe + sk * oi + sl * om
        rj = si * ob + sj * of + sk * oj + sl * on
        rk = si * oc + sj * og + sk * ok + sl * oo
        rl = si * od + sj * oh + sk * ol + sl * op

        rm = sm * oa + sn * oe + so * oi + sp * om
        rn = sm * ob + sn * of + so * oj + sp * on
        ro = sm * oc + sn * og + so * ok + sp * oo
        rp = sm * od + sn * oh + so * ol + sp * op

        return type(self)((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    __mul__ = transform


    def __rmul__(self, other):
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        oa, ob, oc, od,  oe, of, og, oh,  oi, oj, ok, ol,  om, on, oo, op = _Sixteenlet(other)

        ra = sa * oa + sb * oe + sc * oi + sd * om
        rb = sa * ob + sb * of + sc * oj + sd * on
        rc = sa * oc + sb * og + sc * ok + sd * oo
        rd = sa * od + sb * oh + sc * ol + sd * op

        re = se * oa + sf * oe + sg * oi + sh * om
        rf = se * ob + sf * of + sg * oj + sh * on
        rg = se * oc + sf * og + sg * ok + sh * oo
        rh = se * od + sf * oh + sg * ol + sh * op

        ri = si * oa + sj * oe + sk * oi + sl * om
        rj = si * ob + sj * of + sk * oj + sl * on
        rk = si * oc + sj * og + sk * ok + sl * oo
        rl = si * od + sj * oh + sk * ol + sl * op

        rm = sm * oa + sn * oe + so * oi + sp * om
        rn = sm * ob + sn * of + so * oj + sp * on
        ro = sm * oc + sn * og + so * ok + sp * oo
        rp = sm * od + sn * oh + so * ol + sp * op

        return type(self)((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    def scale(self, *vec):
        """Create a matrix with the current transform scaled on each axis by the given triplet.
        """
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        x, y, z = _Triplet(vec)
        ra = sa * x; rb = sb * x; rc = sc * x; rd = sd * x
        re = se * y; rf = sf * y; rg = sg * y; rh = sh * y
        ri = si * z; rj = sj * z; rk = sk * z; rl = sl * z
        rm = sm; rn = sn; ro = so; rp = sp
        return type(self)((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))



    def translate(self, *vec):
        """Create a matrix with the current transform translated on each axis by the given triplet.
        """
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        x, y, z = _Triplet(vec)

        ra = sa + sd * x
        rb = sb + sd * y
        rc = sc + sd * z
        rd = sd

        re = se + sh * x
        rf = sf + sh * y
        rg = sg + sh * z
        rh = sh

        ri = si + sl * x
        rj = sj + sl * y
        rk = sk + sl * z
        rl = sl

        rm = sm + sp * x
        rn = sn + sp * y
        ro = so + sp * z
        rp = sp

        return type(self)((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    def shear(self, *vec):
        """Create a matrix with the current transform sheared by the given triplet.
        Each of the three given values wil shear by different axis.
        Value 0 will shear X by the Y axis
        Value 1 will shear X by the Z axis
        Value 2 will shear Y by the Z axis
        This does not represent every possible shearing, but these are all

        the shears represented by the decompose() operation. Multiple
        rotate and shear matrices can be multiplied to shear against all axis.
        """
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        x, y, z = _Triplet(vec)

        ra = sa + sb * x + sc * y
        rb = sb + sc * z
        rc = sc
        rd = sd

        re = se + sf * x + sg * y
        rf = sf + sg * z
        rg = sg
        rh = sh

        ri = si + sj * x + sk * y
        rj = sj + sk * z
        rk = sk
        rl = sl

        rm = sm + sn * x + so * y
        rn = sn + so * z
        ro = so
        rp = sp

        return type(self)((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    def rotate(self, *vec):
        """Create a matrix with the current transform rotated by euler degrees on each axis.
        The X axis has the most significant priority, and Z has the least.
        """
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        x, y, z = _Triplet(vec)
        x *= _Rad; y *= _Rad; z *= _Rad
        cx = cos(x); cy = cos(y); cz = cos(z)
        sx = sin(x); sy = sin(y); sz = sin(z)

        oa = cz * cy
        ob = sz * cy
        oc = -sy

        oe = -sz * cx + cz * sy * sx
        of = cz * cx + sz * sy * sx
        og = cy * sx

        oi = sz * sx + cz * sy * cx
        oj = -cz * sx + sz * sy * cx
        ok = cy * cx

        ra = sa * oa + sb * oe + sc * oi
        rb = sa * ob + sb * of + sc * oj
        rc = sa * oc + sb * og + sc * ok
        rd = sd

        re = se * oa + sf * oe + sg * oi
        rf = se * ob + sf * of + sg * oj
        rg = se * oc + sf * og + sg * ok
        rh = sh

        ri = si * oa + sj * oe + sk * oi
        rj = si * ob + sj * of + sk * oj
        rk = si * oc + sj * og + sk * ok
        rl = sl

        rm = sm * oa + sn * oe + so * oi
        rn = sm * ob + sn * of + so * oj
        ro = sm * oc + sn * og + so * ok
        rp = sp

        return type(self)((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    def rotateAxis(self, angle, *axis):
        """Create a matrix with the current transform rotated around an axis in degrees.
        Axis does not need to be normalized
        """
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        # angle in degrees
        axisVec = Vec(*axis)
        if not axisVec:
            return type(self)(0.0)

        ax, ay, az = axisVec.normalize()
        angle *= _Rad

        s = sin(angle)
        c = cos(angle)
        nc = 1.0 - c

        m00 = ax * ax * nc + c
        m01 = ax * ay * nc + az * s
        m02 = ax * az * nc - ay * s
        m10 = ax * ay * nc - az * s
        m11 = ay * ay * nc + c
        m12 = ay * az * nc + ax * s
        m20 = ax * az * nc + ay * s
        m21 = ay * az * nc - ax * s
        m22 = az * az * nc + c

        ra = sa * m00 + se * m01 + se * m02
        rb = sb * m00 + sf * m01 + sj * m02
        rc = sc * m00 + sg * m01 + sk * m02
        rd = sd * m00 + sh * m01 + sl * m02

        re = sa * m10 + se * m11 + se * m12
        rf = sb * m10 + sf * m11 + sj * m12
        rg = sc * m10 + sg * m11 + sk * m12
        rh = sd * m10 + sh * m11 + sl * m12

        ri = sa * m20 + se * m21 + se * m22
        rj = sb * m20 + sf * m21 + sj * m22
        rk = sc * m20 + sg * m21 + sk * m22
        rl = sd * m20 + sh * m21 + sl * m22

        rm = sm; rn = sn; ro = so; rp = sp
        return type(self)((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    @classmethod
    def Translate(cls, *vec):
        """Create a matrix with translate on each axis by the given triplet.
        """
        x, y, z = _Triplet(vec)
        ra = 1; rb = 0; rc = 0; rd = 0
        re = 0; rf = 1; rg = 0; rh = 0
        ri = 0; rj = 0; rk = 1; rl = 0
        rm = x; rn = y; ro = z; rp = 1
        return cls((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    @classmethod
    def Scale(cls, *vec):
        """Create a matrix scaled on each axis by the given triplet.
        """
        x, y, z = _Triplet(vec)
        ra = x; rb = 0; rc = 0; rd = 0
        re = 0; rf = y; rg = 0; rh = 0
        ri = 0; rj = 0; rk = z; rl = 0
        rm = 0; rn = 0; ro = 0; rp = 1
        return cls((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    @classmethod
    def Shear(cls, *vec):
        """Create a matrix sheared by the given triplet.
        Each of the three given values wil shear by different axis.
        Value 0 will shear X by the Y axis
        Value 1 will shear X by the Z axis
        Value 2 will shear Y by the Z axis
        This does not represent every possible shearing, but these are all
        the shears represented by the decompose() operation. Multiple
        rotate and shear matrices can be multiplied to shear against all axis.
        """
        x, y, z = _Triplet(vec)
        ra = 1; rb = 0; rc = 0; rd = 0
        re = x; rf = 1; rg = 0; rh = 0
        ri = y; rj = z; rk = 1; rl = 0
        rm = 0; rn = 0; ro = 0; rp = 1
        return cls((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    @classmethod
    def Rotate(cls, *vec):
        """Create a matrix rotated by euler degrees on each axis.
        The X axis has the most significant priority, and Z has the least.
        """
        x, y, z = _Triplet(vec)
        x *= _Rad; y *= _Rad; z *= _Rad
        cx = cos(x); cy = cos(y); cz = cos(z)
        sx = sin(x); sy = sin(y); sz = sin(z)

        ra = cz * cy
        rb = sz * cy
        rc = -sy
        rd = 0.0

        re = -sz * cx + cz * sy * sx
        rf = cz * cx + sz * sy * sx
        rg = cy * sx
        rh = 0.0

        ri = sz * sx + cz * sy * cx
        rj = -cz * sx + sz * sy * cx
        rk = cy * cx
        rl = 0.0

        rm = 0.0
        rn = 0.0
        ro = 0.0
        rp = 1.0

        return cls((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    @classmethod
    def RotateAxis(cls, angle, *axis):
        """
        Create a matrix rotated around an axis in degrees.
        """
        ax, ay, az = Vec(*axis).normalize()
        angle *= _Rad

        s = sin(angle)
        c = cos(angle)
        nc = 1.0 - c

        ra = ax * ax * nc + c
        rb = ax * ay * nc + az * s
        rc = ax * az * nc - ay * s
        rd = 0

        re = ax * ay * nc - az * s
        rf = ay * ay * nc + c
        rg = ay * az * nc + ax * s
        rh = 0

        ri = ax * az * nc + ay * s
        rj = ay * az * nc - ax * s
        rk = az * az * nc + c
        rl = 0

        rm = 0
        rn = 0
        ro = 0
        rp = 1

        return cls((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    def invert(self):
        """Create a matrix that is the inverse transform.
        If the matrix is singular the returned matrix will be all zeros, which is 'False'.
        """
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat

        # Compute determinant
        d = ((sa * sf - se * sb) * (sk * sp - so * sl)
                    - (sa * sj - si * sb) * (sg * sp - so * sh)
                    + (sa * sn - sm * sb) * (sg * sl - sk * sh)
                    + (se * sj - si * sf) * (sc * sp - so * sd)
                    - (se * sn - sm * sf) * (sc * sl - sk * sd)
                    + (si * sn - sm * sj) * (sc * sh - sg * sd))

        epsilon = getattr(_ThreadLocal, "minivecEpsilon", _DefaultEpsilon)

        if fabs(d) < epsilon:
            return type(self)(0.0)

        di = 1.0 / d

        ra = di * (sf * (sk * sp - so * sl) + sj * (so * sh - sg * sp) + sn * (sg * sl - sk * sh))
        re = di * (sg * (si * sp - sm * sl) + sk * (sm * sh - se * sp) + so * (se * sl - si * sh))
        ri = di * (sh * (si * sn - sm * sj) + sl * (sm * sf - se * sn) + sp * (se * sj - si * sf))
        rm = di * (se * (sn * sk - sj * so) + si * (sf * so - sn * sg) + sm * (sj * sg - sf * sk))

        rb = di * (sj * (sc * sp - so * sd) + sn * (sk * sd - sc * sl) + sb * (so * sl - sk * sp))
        rf = di * (sk * (sa * sp - sm * sd) + so * (si * sd - sa * sl) + sc * (sm * sl - si * sp))
        rj = di * (sl * (sa * sn - sm * sb) + sp * (si * sb - sa * sj) + sd * (sm * sj - si * sn))
        rn = di * (si * (sn * sc - sb * so) + sm * (sb * sk - sj * sc) + sa * (sj * so - sn * sk))

        rc = di * (sn * (sc * sh - sg * sd) + sb * (sg * sp - so * sh) + sf * (so * sd - sc * sp))
        rg = di * (so * (sa * sh - se * sd) + sc * (se * sp - sm * sh) + sg * (sm * sd - sa * sp))
        rk = di * (sp * (sa * sf - se * sb) + sd * (se * sn - sm * sf) + sh * (sm * sb - sa * sn))
        ro = di * (sm * (sf * sc - sb * sg) + sa * (sn * sg - sf * so) + se * (sb * so - sn * sc))

        rd = di * (sb * (sk * sh - sg * sl) + sf * (sc * sl - sk * sd) + sj * (sg * sd - sc * sh))
        rh = di * (sc * (si * sh - se * sl) + sg * (sa * sl - si * sd) + sk * (se * sd - sa * sh))
        rl = di * (sd * (si * sf - se * sj) + sh * (sa * sj - si * sb) + sl * (se * sb - sa * sf))
        rp = di * (sa * (sf * sk - sj * sg) + se * (sj * sc - sb * sk) + si * (sb * sg - sf * sc))

        return type(self)((ra, rb, rc, rd,  re, rf, rg, rh,  ri, rj, rk, rl,  rm, rn, ro, rp))


    __invert__ = invert   # This is the ~ unary operator


    def determinant(self):
        """Compute the determinant of the matrix.
        This is single number that represents the scaled volume of the transform.
        This can be useful in determining if the matrix has been flipped by scaling on
        an odd number of axis.
        """
        # consider returning 0 if determinant is less than epsilon
        sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self.__mat
        return ((sa * sf - se * sb) * (sk * sp - so * sl)
                    - (sa * sj - si * sb) * (sg * sp - so * sh)
                    + (sa * sn - sm * sb) * (sg * sl - sk * sh)
                    + (se * sj - si * sf) * (sc * sp - so * sd)
                    - (se * sn - sm * sf) * (sc * sl - sk * sd)
                    + (si * sn - sm * sj) * (sc * sh - sg * sd))


    def decompose(self):
        """Decompose the matrix into vectors representing translate, rotate, shear, and scale.
        If the matrix has been built using frustum transformations the results are undefined.
        """
        translate = Vec(self[12:15])
        rotationMatrix, scale, shear = _DecomposeScaling(self)
        if not rotationMatrix:
            return scale, scale, scale, scale

        rotate = _DecomposeRotation(rotationMatrix)
        return translate, rotate, shear, scale



    @classmethod
    def Compose(cls, translate, rotate, shear, scale):
        """Create a new matrix by combining multiple vectors that represent
        translate, rotate, shear, and scale.
        This is the inverse of the decompose method.
        """
        matrix = cls.Scale(scale)
        matrix = matrix.shear(shear)
        matrix = matrix.rotate(rotate)
        matrix = matrix.translate(translate)
        return matrix


    def lerp(self, percent, *other):
        """Linearly interpolate between this matrix and another.
        The percentage is between 0.0 and 1.0, but numbers outside that range will also work.
        The rotations will be interpolated using shortest distance quaternion math.
        """
        cls = type(self)
        other = cls(*other)

        selfTranslate = Vec(self[12:15])
        rotationMatrix, selfScale, selfShear = _DecomposeScaling(self)
        if not rotationMatrix:
            return cls(0.0)
        selfQuat = _DecomposeQuat(rotationMatrix)

        otherTranslate = Vec(other[12:15])
        rotationMatrix, otherScale, otherShear = _DecomposeScaling(other)
        if not rotationMatrix:
            return cls(0.0)
        otherQuat = _DecomposeQuat(rotationMatrix)

        translate = selfTranslate.lerp(percent, otherTranslate)
        shear = selfShear.lerp(percent, otherShear)
        scale = selfScale.lerp(percent, otherScale)
        epsilon = getattr(_ThreadLocal, "minivecEpsilon", _DefaultEpsilon)
        rotate = _QuatLerp(selfQuat, otherQuat, percent, epsilon)

        matrix = cls.Scale(scale)
        matrix = matrix.shear(shear)
        rotateMatrix = _QuatToMat(rotate)
        matrix *= rotateMatrix
        matrix = matrix.translate(translate)
        return matrix



def _QuatLerp(q1, q2, t, epsilon):
    """Slerp between two quaternions
    """
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2

    # Calc angle between, if equal, return either
    cosHalfTheta = w1 * w2 + x1 * x2 + y1 * y2 + z1 * z2
    if fabs(cosHalfTheta) > 1.0 - epsilon:
        return q1

    sinHalfTheta = sqrt(1.0 - cosHalfTheta * cosHalfTheta)
    # if theta=180degrees, undefined since any axis will work
    if fabs(sinHalfTheta) < epsilon:
        w = w1 * 0.5 + w2 * 0.5
        x = x1 * 0.5 + x2 * 0.5
        y = y1 * 0.5 + y2 * 0.5
        z = z1 * 0.5 + z2 * 0.5
        return w, x, y, z

    halfTheta = acos(cosHalfTheta)
    ratioA = sin((1.0 - t) * halfTheta) / sinHalfTheta
    ratioB = sin(t * halfTheta) / sinHalfTheta
    w = w1 * ratioA + w2 * ratioB
    x = x1 * ratioA + x2 * ratioB
    y = y1 * ratioA + y2 * ratioB
    z = z1 * ratioA + z2 * ratioB
    return w, x, y, z



def _QuatToMat(q):
    """Convert quat to transform matrix
    """
    w, x, y, z = q

    ma = 1.0 - 2.0 * (y * y + z * z)
    mb = 2.0 * (x * y + z * w)
    mc = 2.0 * (z * x - y * w)
    md = 0.0

    me = 2.0 * (x * y - z * w)
    mf = 1.0 - 2.0 * (z * z + x * x)
    mg = 2.0 * (y * z + x * w)
    mh = 0.0

    mi = 2.0 * (z * x + y * w)
    mj = 2.0 * (y * z - x * w)
    mk = 1.0 - 2.0 * (y * y + x * x)
    ml = 0.0

    mm = 0.0
    mn = 0.0
    mo = 0.0
    mp = 1.0

    return ma, mb, mc, md,  me, mf, mg, mh,  mi, mj, mk, ml,  mm, mn, mo, mp



def _DecomposeScaling(self):
    """Extract the scaling and shearing components from a transform matrix
    """
    cls = type(self)
    sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self
    epsilon = getattr(_ThreadLocal, "minivecEpsilon", _DefaultEpsilon)

    # This implementation follows the technique described in the paper by
    # Spencer W. Thomas in the Graphics Gems II article: "Decomposing a
    # Mat into Simple Transformations", p. 320.

    row0 = Vec(sa, sb, sc)
    row1 = Vec(se, sf, sg)
    row2 = Vec(si, sj, sk)

    # normalize the 3x3 matrix here.
    # It was noticed that this can improve numerical stability significantly,
    # especially when many of the upper 3x3 matrix's coefficients are very
    # close to zero; we correct for this step at the end by multiplying the
    # scaling factors by maxVal at the end (shear and rotation are not
    # affected by the normalization).
    maxVal = max(map(fabs, (sa, sb, sc, se, sf, sg, si, sj, sk)))
    if maxVal > 1.0 - epsilon:
        maxVal = 0.0
    if fabs(maxVal) >= epsilon:
        maxInverse = 1.0 / maxVal
        row0 *= maxInverse
        row1 *= maxInverse
        row2 *= maxInverse

    # Compute X scale factor and normalize
    scaleX = row0.length()
    if scaleX < epsilon:
        return (cls(0.0), Vec(0.0), Vec(0.0))
    row0 /= scaleX

    # An XY shear factor will shear the X coord. as the Y coord. changes.
    # There are 6 combinations (XY, XZ, YZ, YX, ZX, ZY), although we only
    # extract the first 3 because we can effect the last 3 by shearing in
    # XY, XZ, YZ combined rotations and scales.
    # shear matrix <   1,  YX,  ZX,  0,
    #                 XY,   1,  ZY,  0,
    #                 XZ,  YZ,   1,  0,
    #                  0,   0,   0,  1 >

    # Compute XY shear factor and make 2nd row orthogonal to 1st.
    shearX  = row0.dot(row1);
    row1 -= row0 * shearX;

    # Compute Y scale.
    scaleY = row1.length();
    if scaleY < epsilon:
        return (cls(0.0), Vec(0.0), Vec(0.0))

    # Normalize 2nd row and correct the XY shear factor for Y scaling.
    row1 /= scaleY
    shearX /= scaleY

    # Compute XZ and YZ shears, orthogonalize 3rd row.
    shearY  = row0.dot(row2)
    row2 -= row0 * shearY
    shearZ  = row1.dot(row2)
    row2 -= row1 * shearZ

    # Get Z scale.
    scaleZ = row2.length()
    if scaleZ < epsilon:
        return (cls(0.0), Vec(0.0), Vec(0.0))

    # Normalize 3rd row and correct the XZ and YZ shear factors for Z scaling.
    row2 /= scaleZ
    shearY /= scaleZ
    shearZ /= scaleZ

    scale = Vec(scaleX, scaleY, scaleZ)
    shear = Vec(shearX, shearY, shearZ)
    # At this point, the upper 3x3 matrix in mat is orthonormal.
    # Check for a coordinate system flip. If the determinant
    # is less than zero, then negate the matrix and the scaling factors.
    if row0.dot(row1.cross(row2)) < 0:
        scale = -scale
        row0 = -row0
        row1 = -row1
        row2 = -row2

    row0 = row0.normalize()
    row1 = row1.normalize()
    row2 = row2.normalize()
    # Copy over the orthonormal rows into the returned matrix.
    # The upper 3x3 matrix in mat is now a rotation matrix.
    ra, rb, rc = row0
    re, rf, rg = row1
    ri, rj, rk = row2
    mat = type(self)(ra, rb, rc, 0.0, re, rf, rg, 0.0, ri, rj, rk, 0.0, 0.0, 0.0, 0.0, 1.0)

    # Correct the scaling factors for the normalization step that we
    # performed above; shear and rotation are not affected by the
    # normalization.
    if maxVal:
        scale *= maxVal

    return mat, scale, shear



def _DecomposeRotation(self):
    """Find the euler rotations for a transform matrix.
    The rotations will be in XYZ order.
    Assume this already has scale/shear extracted and rows are normalized
    """
    sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self

    rotateX = atan2(sg, sk) * _Deg

    # Remove the x rotation from M, so that the remaining rotation, N
    # is only around two axes, and gimbal lock cannot occur.
    justX = self.Rotate(-rotateX, 0.0, 0.0)
    N = justX * self

    sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = N
    cy = sqrt(sa * sa + sb * sb)
    rotateY = atan2(-sc, cy) * _Deg
    rotateZ = atan2(-se, sf) * _Deg

    return Vec(rotateX, rotateY, rotateZ)



def _DecomposeQuat(self):
    """Find the quaternion rotations for a transform matrix.
    Assume this already has scale/shear extracted and rows are normalized
    """
    sa, sb, sc, sd,  se, sf, sg, sh,  si, sj, sk, sl,  sm, sn, so, sp = self

    tr = sa + sf + sk
    if tr > 0.0:
        s = sqrt(tr + 1.0)

        quatR = s / 2.0
        s = 0.5 / s

        quatX = (sg - sj) * s
        quatY = (si - sc) * s
        quatZ = (sb - se) * s
        return quatR, quatX, quatY, quatZ

    # Diagonal is negative, do work by maximum axis
    i = 0
    if sf > sa:
        if sk > sf:
            i = 2
        else:
            i = 1
    elif sk > sa:
        i = 2

    nxt = [1, 2, 0]
    j = nxt[i]
    k = nxt[j]

    mat = self
    s = sqrt((mat[i * 4 + i] - (mat[j * 4 + j] + mat[k * 4 + k])) + 1.0)

    q = [0.0, 0.0, 0.0]
    q[i] = s * 0.5
    if s:
        s = 0.5 / s

    quatR = mat[j * 4 + k] - mat[k * 4 + j] * s
    q[j] = mat[i * 4 + j] + mat[j * 4 + i] * s
    q[k] = mat[i * 4 + k] + mat[k * 4 + i] * 2

    return quatR, q[0], q[1], q[2]



def Epsilon():
    """Get the current epsilon value used in this minivec context.
    This value will be unique per thread. Many comparisons inside minivec objects will use the
    epsilon as a threshold for comparing floating point values. The default is 10e-8.
    """
    global _ThreadLocal, _DefaultEpsilon
    epsilon = getattr(_ThreadLocal, "minivecEpsilon", _DefaultEpsilon)
    return epsilon



def ResetEpsilon():
    """Reset the epsilon value and all pushed values back to the default.
    This value will be unique per thread. Many comparisons inside minivec objects will use the
    epsilon as a threshold for comparing floating point values. The default is 10e-8.
    """
    global _ThreadLocal
    if hasattr(_ThreadLocal, "minivecEpsilon"):
        delattr(_ThreadLocal, "minivecEpsilon")
    if hasattr(_ThreadLocal, "minivecEpsilonStack"):
        delattr(_ThreadLocal, "minivecEpsilonStack")



def PushEpsilon(value):
    """Set the minimum threshold for different floating point values.
    This will create a Python context that can be used by the with operator. If a context
    is not used, it is recommended to pop the epsilon value when no longer needed.
    This value will be unique per thread. Many comparisons inside minivec objects will use the
    epsilon as a threshold for comparing floating point values. The default is 10e-8.
    """
    global _ThreadLocal, _DefaultEpsilon
    previous = getattr(_ThreadLocal, "minivecEpsilon", _DefaultEpsilon)
    stack = getattr(_ThreadLocal, "minivecEpsilonStack", None)
    if stack is None:
        _ThreadLocal.minivecEpsilonStack = [previous]
    else:
        stack.append(previous)
    if value < 0.0:
        value = 0.0
    _ThreadLocal.minivecEpsilon = value
    return _EpsilonPopContext()



def PopEpsilon():
    """Restore the previously set epsilon value.
    This will raise an exception if there are no values to be popped.
    This value will be unique per thread. Many comparisons inside minivec objects will use the
    epsilon as a threshold for comparing floating point values.
    """
    global _ThreadLocal
    stack = getattr(_ThreadLocal, "minivecEpsilonStack", None)
    if not stack:
        raise RuntimeError("No epsilon values to pop")

    epsilon = _ThreadLocal.minivecEpsilon = stack.pop()
    return epsilon



class _EpsilonPopContext(object):
    def __enter__(self):
        pass  # Confession, we've already set the state


    def __exit__(self, _t, _v, _tb):
        PopEpsilon()


    def __repr__(self):
        return "_EpsilonPopContext()"



def Error():
    """Get the current error value used to construct minivec objects.
    This will usually be zero, nan. When error is set to the special NotImplemented object
    minivec will raise exceptions when creating error objects.
    This value will be unique per thread. The default is 0.0.
    """
    global _ThreadLocal, _DefaultError
    error = getattr(_ThreadLocal, "minivecError", _DefaultError)
    return error



def ResetError():
    """Reset the error value and all pushed values back to the default.
    This will usually be zero, nan. When error is set to the special NotImplemented object
    minivec will raise exceptions when creating error objects.
    This value will be unique per thread. The default is 0.0.
    """
    global _ThreadLocal
    if hasattr(_ThreadLocal, "minivecError"):
        delattr(_ThreadLocal, "minivecError")
    if hasattr(_ThreadLocal, "minivecErrorStack"):
        delattr(_ThreadLocal, "minivecErrorStack")



def PushError(value):
    """Set the error value used for creating minivec objects with errors.
    This will create a Python context that can be used by the with operator. If a context
    is not used, it is recommended to pop the error value when no longer needed.
    This will usually be zero, nan. When error is set to the special NotImplemented object
    minivec will raise exceptions when creating error objects.
    This value will be unique per thread. The default is 0.0.
    """
    global _ThreadLocal, _DefaultError
    previous = getattr(_ThreadLocal, "minivecError", _DefaultError)
    stack = getattr(_ThreadLocal, "minivecErrorStack", None)
    if stack is None:
        _ThreadLocal.minivecErrorStack = [previous]
    else:
        _ThreadLocal.minivecErrorStack.append(previous)
    _ThreadLocal.minivecError = value
    return _ErrorPopContext()



def PopError():
    """Restore the previously set error value.
    This will usually be zero, nan. When error is set to the special NotImplemented object
    minivec will raise exceptions when creating error objects.
    This value will be unique per thread.
    """
    global _ThreadLocal, _DefaultEpsilon
    stack = getattr(_ThreadLocal, "minivecErrorStack", None)
    if not stack:
        raise RuntimeError("No error values to pop")

    error = _ThreadLocal.minivecError = stack.pop()
    return error



class _ErrorPopContext(object):
    def __enter__(self):
        pass  # Confession, we've already set the state


    def __exit__(self, _t, _v, _tb):
        PopError()


    def __repr__(self):
        return "_ErrorPopContext()"



def _Triplet(obj, allowNone=False, allowNested=True, allowScalar=True):
    if Vec in obj.__class__.__mro__:
        return tuple(obj)
    num, seq = _FloatOrSequence(obj, iterMax=4)
    if num is not None:
        if allowScalar:
            return num, num, num
        raise TypeError("Number type not valid for vector operation")
    seqLen = len(seq)
    if allowNone and not seqLen:
        return 0.0, 0.0, 0.0
    if allowNested and seqLen == 1:
        return _Triplet(seq[0], allowNested=False)
    elif seqLen == 3:
        return _TupleOfFloats(seq)
    raise TypeError("Unknown data type for vector argument")



def _Quadlet(obj):
    num, seq = _FloatOrSequence(obj, iterMax=5)
    if num is not None:
        raise TypeError("Number type not valid for vector operation")
    seqLen = len(seq)
    if seqLen == 4:
        return _TupleOfFloats(seq)
    raise TypeError("Unknown data type for vector argument")



def _Sixteenlet(obj, allowNone=False, allowNested=True, allowScalar=True):
    if Mat in obj.__class__.__mro__:
        return tuple(obj)
    num, seq = _FloatOrSequence(obj, iterMax=17)
    if num is not None:
        if allowScalar:
            return (num, 0.0, 0.0, 0.0,  0.0, num, 0.0, 0.0,  0.0, 0.0, num, 0.0,  0.0, 0.0, 0.0, num)
        raise TypeError("Number type not valid for matrix operation")
#    if seq is None:
#        raise TypeError("Unknown data type for matrix argument")
    seqLen = len(seq)
    if allowNone and not seqLen:
        return (1.0, 0.0, 0.0, 0.0,  0.0, 1.0, 0.0, 0.0,  0.0, 0.0, 1.0, 0.0,  0.0, 0.0, 0.0, 1.0)
    if allowNested and seqLen == 1:
        return _Sixteenlet(seq[0], allowNested=False)
    elif seqLen == 16:
        return _TupleOfFloats(seq)
    elif seqLen == 4:
        a, b, c, d = map(_Quadlet, seq)
        return a + b + c + d
    raise TypeError("Unknown data type for matrix argument")



def _FloatOrSequence(val, _int=int, _float=float, _list=list, _tuple=tuple, iterMax=None):
    # Passing several builtins as defaults to avoid looking them up
    mro = val.__class__.__mro__
    if _int in mro or _float in mro:
        return val + 0.0, None
    if _tuple in mro or _list in mro:
        return None, val
    if Vec in mro:
        return None, val

    if iterMax:
        # slicing iterator avoids expanding a humungous iterator
        seq = _tuple(islice(val, 0, iterMax))
    else:
        seq = _tuple(val)
    return None, seq



def _TupleOfFloats(seq, _int=int, _float=float, _len=len):
    # Passing several builtins as defaults to avoid looking them up
    values = [0.0] * _len(seq)
    for i, val in enumerate(seq):
        mro = val.__class__.__mro__
        if _int in mro or _float in mro:
            values[i] = val + 0.0
        else:
            raise TypeError("Unknown data type for number argument")
    return tuple(values)



def _FindOperationType(obj, operationName):
    global _MappedTypes
    mro = obj.__class__.__mro__
    for objType in mro:
        if objType == Vec or objType == Mat: # or objType == Box:
            return obj, objType, None
    else:
        try:
            vec = Vec(obj)
            return vec, Vec, None

        except (TypeError, ValueError):
            reverse = getattr(obj, "_r" + operationName, None)
            return obj, mro[0], reverse

