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

		print 'Tank __init__'

		self.world = world

		# Don't let fish spawn within this far of the edge
		self.padding = 50

		
		self.margin = DictWrap({
			'left': 10,
			'top': 100,
			'right': 10,
			'bottom': 10
		})

		self.resize()

		

	def randomPosition(self):
		p = self.padding
		b = self.box
		s = self.size
		return Vector2D(uniform(b.left + p, b.left + s.width - p), uniform(b.bottom + p, b.bottom + s.height - p))
		

	def resize(self):
		m = self.margin

		bounds = {
			'left': m.left,
			'top': self.world.height - m.top,
			'right': self.world.width - m.right,
			'bottom': m.bottom
		}

		self.box = Rect(bounds)

		self.size = DictWrap({
			'width': self.box.right - self.box.left,
			'height': self.box.top - self.box.bottom
		})

		self.walls = self.getWalls()

		V = Vector2D
		b = self.box
		waveHeight = 40
		self.tankShape = [
			V(b.left, b.top + waveHeight),
			V(b.left, b.bottom),
			V(b.right, b.bottom),
			V(b.right, b.top + waveHeight)
		]

		
		
		# self.wave.append(Vector2D(500, 800))
		# print 'wave', self.wave

	def getWalls(self):
		b = self.box
		return [
			# The order of these pairs is important.
			# We want the normals to be pointing into the center
			# (avoids having to reverse them to face the fish later)

			# Left wall
			Wall( Vector2D(b.left, b.top), Vector2D(b.left, b.bottom) ),
			# Right wall
			Wall( Vector2D(b.right, b.bottom), Vector2D(b.right, b.top) ),
			# Top wall
			Wall( Vector2D(b.right, b.top), Vector2D(b.left, b.top) ),
			# Bottom wall
			Wall( Vector2D(b.left, b.bottom), Vector2D(b.right, b.bottom) )
		]

	def createWave(self, width, amplitude = 50, wavelength=60, smoothness = 10, start = Vector2D(), seed = 0):





		numPoints = int(width / smoothness)
		
		interval = float(width) / float(numPoints)
		pts = []

		

		# def wave(x):
		# 	theta = x / wavelength * 2 * pi
		# 	return amplitude * sin(theta)

		
		for i in range(numPoints + 1):
			x = interval * i
			
			# y = wave(x)
			theta = pi/2 * (seed + x / wavelength)
			smallWaves = amplitude * sin(theta)

			thetaWide = pi/2 * (seed + x / wavelength / 2)
			bigWaves = amplitude * sin(thetaWide) * 1

			y = smallWaves + bigWaves
			# + (sin(seed) * 5 * sin(theta))
			pos = Vector2D(start.x + x, start.y + y)
			
			pts.append(pos)

		

		return pts


	def drawWaves(self):
		egi.green_pen()
		seed = self.world._clock * 2

		water = '27c8f0'
		egi.set_stroke(2)

		egi.set_pen_color(color=rgba(water, 0.5))
		egi.unclosed_shape(self.createWave(seed= seed, amplitude = 7, width = self.size.width, start = Vector2D(self.box.left, self.box.top + 10) ))
		
		egi.set_pen_color(color=rgba('1fa3ff', 0.5))
		egi.unclosed_shape(self.createWave(seed= seed/2, amplitude = 3, width = self.size.width, start = Vector2D(self.box.left, self.box.top + 0) ))
		
		
		egi.set_pen_color(color=rgba('0387ed', 0.5))
		egi.unclosed_shape(self.createWave(seed= seed/3, amplitude = 10, width = self.size.width, start = Vector2D(self.box.left, self.box.top + 0) ))
		


		# matrix = Matrix33()
		# matrix.translate(self.box.left, self.box.top)
		# wave.transform(matrix)

		# print wave.pts[0], wave.pts[1], wave.pts[2], wave.pts[3]

		
		

		
	def drawWalls(self):



		tank = '0e59cb'
		egi.set_pen_color(color=rgba(tank, 0.6))
		egi.set_stroke(2)

		egi.unclosed_shape(self.tankShape)

		
		


	def render(self):
		
		self.drawWalls()
		self.drawWaves()
		egi.set_stroke(1)

		if(self.world.debug.drawDebug):
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


