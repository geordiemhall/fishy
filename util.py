# Util
# ==================================

from vector2d import Vector2D
import copy


class DictWrap(object):
    """ Wrap an existing dict, or create a new one, and access with either dot 
        notation or key lookup.

        The attribute _data is reserved and stores the underlying dictionary.
        When using the += operator with create=True, the empty nested dict is 
        replaced with the operand, effectively creating a default dictionary
        of mixed types.

        args:
            d({}): Existing dict to wrap, an empty dict is created by default
            create(True): Create an empty, nested dict instead of raising a KeyError

        example:
            >>>dw = DictWrap({'pp':3})
            >>>dw.a.b += 2
            >>>dw.a.b += 2
            >>>dw.a['c'] += 'Hello'
            >>>dw.a['c'] += ' World'
            >>>dw.a.d
            >>>print dw._data
            {'a': {'c': 'Hello World', 'b': 4, 'd': {}}, 'pp': 3}

    """

    def __init__(self, d=None, create=True):
        if d is None:
            d = {}
        supr = super(DictWrap, self)  
        supr.__setattr__('_data', d)
        supr.__setattr__('__create', create)

    def __getattr__(self, name):
        try:
            value = self._data[name]
        except KeyError:
            if not super(DictWrap, self).__getattribute__('__create'):
                raise
            value = {}
            self._data[name] = value

        if hasattr(value, 'items'):
            create = super(DictWrap, self).__getattribute__('__create')
            return DictWrap(value, create)
        return value

    def __setattr__(self, name, value):
        self._data[name] = value  

    def __getitem__(self, key):
        try:
            value = self._data[key]
        except KeyError:
            if not super(DictWrap, self).__getattribute__('__create'):
                raise
            value = {}
            self._data[key] = value

        if hasattr(value, 'items'):
            create = super(DictWrap, self).__getattribute__('__create')
            return DictWrap(value, create)
        return value

    def __setitem__(self, key, value):
        self._data[key] = value

    def __iadd__(self, other):
        if self._data:
            raise TypeError("A Nested dict will only be replaced if it's empty")
        else:
            return other


class Util(object):

    @staticmethod
    def translatePoints(points, x=0, y=0):

        for point in points:
            point.x += x
            point.y += y

        return points


    @staticmethod
    def scalePoints(points, x = 1.0, y = 1.0):

        for point in points:
            point.x *= x
            point.y *= y

        return points


    @staticmethod
    def scaledPoints(points, x = 1.0, y = 1.0):

        pointsCopy = copy.deepcopy(points)

        for point in pointsCopy:
            point.x *= x
            point.y *= y

        return pointsCopy

    @staticmethod
    def clamp(minimum, x, maximum):
        return max(minimum, min(x, maximum))

    #  Returns a scaling function based on tuples for domain and range
    @staticmethod
    def linearScale(domain, range):

        rise = range[1] - range[0]
        run = domain[1] - domain[0]
        
        m = rise / run
        c = range[1] - m * domain[1]

        def f(x):
            return m * x + c

        return f

    # Returns a new array of points copied
    @staticmethod
    def copyPoints(points):
        return [pt.copy() for pt in points] 

    @staticmethod
    def strPoints(points):
        return [str(pt) for pt in points]  

    @staticmethod 
    def sign(num):
        if(num >= 0.0): return 1
        return -1

    @staticmethod
    def shapeFromString(string, pointDelimiter=',', coordDelimiter=' '):
        # Grab the points
        points = [p.strip().split(coordDelimiter) for p in string.split(pointDelimiter)]
        # Convert coordinates to vectors
        points = [Vector2D(float(c[0]), float(c[1])) for c in points]

        return points

    
    
    
   






