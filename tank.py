from vector2d import Rect
from util import DictWrap
from graphics import egi
from matrix33 import Matrix33
from random import uniform
from vector2d import Vector2D, Points
from math import sin, pi, cos
import inspect
from graphics import rgba


class Tank(object):

	def __init__(self, world = None):

		self.world = world

		# Water colors
		self.water = ('27c8f0', '1fa3ff', '0069d5')

		# Don't let fish spawn within this far of the edge
		self.padding = 0.08

		m = 1
		self.margin = DictWrap({
			'left': m,
			'top': 100,
			'right': m,
			'bottom': m
		})

		self.resize()

		

	def randomPosition(self):
		pb = self.paddedBox
		return Vector2D(uniform(pb.left, pb.right), uniform(pb.bottom, pb.top))
		

	def resize(self):
		m = self.margin
		V = Vector2D

		self.box = b = Rect({
			'left': m.left,
			'top': self.world.height - m.top,
			'right': self.world.width - m.right,
			'bottom': m.bottom
		})

		# Set up the size
		self.size = DictWrap({
			'width': self.box.right - self.box.left,
			'height': self.box.top - self.box.bottom
		})

		# Make the padded box
		p = (self.size.width * self.padding, self.size.height * self.padding)

		self.paddedBox = Rect({
			'left': self.box.left + p[0],
			'top': self.box.top - p[0],
			'right': self.box.right - p[1],
			'bottom': self.box.bottom + p[1]
		})

		
		

		# Create the shape pusing the walls
		waveHeight = 40
		self.tankShape = [
			V(b.left, b.top + waveHeight),
			V(b.left, b.bottom),
			V(b.right, b.bottom),
			V(b.right, b.top + waveHeight)
		]

		# Get the wall segments for rendering and collisions
		self._walls = {
			# The order of these pairs is important.
			# We want the normals to be pointing into the center
			# (avoids having to reverse them to face the fish later)

			# Left wall
			'left': Wall( Vector2D(b.left, b.top), Vector2D(b.left, b.bottom) ),
			# Right wall
			'right': Wall( Vector2D(b.right, b.bottom), Vector2D(b.right, b.top) ),
			# Top wall
			'top': Wall( Vector2D(b.right, b.top), Vector2D(b.left, b.top) ),
			# Bottom wall
			'bottom': Wall( Vector2D(b.left, b.bottom), Vector2D(b.right, b.bottom) )
		}

		# Shorthand prop to prevent function overhead when getting all walls
		self.walls = [
			self._walls['left'],
			self._walls['right'],
			self._walls['top'],
			self._walls['bottom']
		]

		
		
		# self.wave.append(Vector2D(500, 800))
		# print 'wave', self.wave

	def getWalls(self, which='all'):
		
		if(which == 'all'):
			return self._walls

		if(which == 'vertical'):
			return [
				self._walls['top'],
				self._walls['bottom']
			]

		if(which == 'horizontal'):
			return [
				self._walls['left'],
				self._walls['right']
			]

		return self._walls[which]


	def wavePoint(self, i, interval, seed, wavelength, amplitude, start):
		x = interval * i
		
		thetaNarrow = pi/2 * (seed + x / wavelength)
		smallWaves = amplitude * sin(thetaNarrow)

		thetaWide = pi/2 * (seed + x / wavelength / 2)
		bigWaves = amplitude * sin(thetaWide) * 1

		y = smallWaves + bigWaves

		return Vector2D(start.x + x, start.y + y)


	# Generates a line segment based on the input parameters
	# When rendered using an animated seed value, looks like a wave
	def createWave(self, width, amplitude = 50, wavelength=60, smoothness = 25, start = Vector2D(), seed = 0):





		numPoints = int(width / smoothness)
		
		interval = float(width) / float(numPoints)
		pts = []

		

		# def wave(x):
		# 	theta = x / wavelength * 2 * pi
		# 	return amplitude * sin(theta)

		pts = [self.wavePoint(i=i, interval=interval,seed=seed,wavelength=wavelength,amplitude=amplitude, start=start) for i in range(numPoints + 1)]

		
		# for i in range(numPoints + 1):
		# 	x = interval * i
			
		# 	thetaNarrow = pi/2 * (seed + x / wavelength)
		# 	smallWaves = amplitude * sin(thetaNarrow)

		# 	thetaWide = pi/2 * (seed + x / wavelength / 2)
		# 	bigWaves = amplitude * sin(thetaWide) * 1

		# 	y = smallWaves + bigWaves

		# 	pos = Vector2D(start.x + x, start.y + y)
			
		# 	pts.append(pos)

		

		return pts


	def drawWaves(self):
		egi.green_pen()
		seed = self.world._clock * 2

		water = self.water
		egi.set_stroke(2)

		egi.set_pen_color(color=rgba(water[0], 0.5))
		egi.unclosed_shape(self.createWave(seed= seed, amplitude = 7, width = self.size.width, start = Vector2D(self.box.left, self.box.top + 10) ))
		
		egi.set_pen_color(color=rgba(water[1], 0.5))
		self.mainWave = self.createWave(seed= seed/2, amplitude = 3, width = self.size.width, start = Vector2D(self.box.left, self.box.top + 0) )
		egi.unclosed_shape(self.mainWave)
		
		
		egi.set_pen_color(color=rgba(water[2], 0.5))
		egi.unclosed_shape(self.createWave(seed= seed/3, amplitude = 10, width = self.size.width, start = Vector2D(self.box.left, self.box.top + 0) ))
		


		# matrix = Matrix33()
		# matrix.translate(self.box.left, self.box.top)
		# wave.transform(matrix)

		# print wave.pts[0], wave.pts[1], wave.pts[2], wave.pts[3]

		
		

		
	def drawWalls(self):



		tank = '0e59cb'
		egi.set_pen_color(color=rgba(tank, 0.6))
		egi.set_stroke(2)

		self.tankShape[0].y = self.mainWave[0].y
		self.tankShape[-1].y = self.mainWave[-1].y

		egi.unclosed_shape(self.tankShape)

	def contains(self, point):
		b = self.box
		return point.x >= b.left and point.x <= b.right and point.y <= b.top and point.y >= b.bottom

		


	def render(self):
		
		self.drawWaves()
		self.drawWalls()
		
		egi.set_stroke(1)

		if(self.world.drawDebug):
			for wall in self.walls:
				egi.line_by_pos(wall.center, wall.center + wall.normal * 100)


class Wall(object):
	def __init__ (self, start, end):
		self.start = start
		self.end = end

		self.center = self.start + self.vector() / 2

		self.normal = self.vector().perp().normalise()
		

	def vector(self):
		return self.end - self.start

	def __str__(self):
		return str(self.start) + ' -- ' + str(self.end)


