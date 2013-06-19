''' 

Rock 
=================================='''

from vector2d import Vector2D
from graphics import egi, rgba
from random import uniform, randrange
from math import sqrt, sin, cos, pi
from matrix33 import Matrix33
import copy


class Rock(object):
	"""Rock object"""
	def __init__(self, world=None):
		
		self.world = world

		self.pos = Vector2D()
		self.vel = Vector2D()

		self.scale = Vector2D() * 30
		self.maxSpeed = uniform(5, 8)
		self.boundingRadius = uniform(25, 80)
		self.edges = randrange(7, 12)
		self.rotation = uniform(-0.05/3, 0.05/3)

		self.color = rgba('25a000')

		self.heading = Vector2D(0, 1)
		self.side = self.heading.perp()

		self.rockShape = self.getRockShape()



	# Rocks have a constant speed
	def calculateAcceleration(self, delta):

		accel = Vector2D()

		return accel


	# Calculates velocity based on our acceleration
	def calculateVelocity(self, delta):
		# new velocity
		vel = self.vel + self.acceleration * delta
		
		# check for limits of new velocity
		max = self.maxSpeed
		vel.truncate(max)

		return vel


	def update(self, delta):
		''' update vehicle position and orientation '''
		self.acceleration = self.calculateAcceleration(delta)

		self.vel = self.calculateVelocity(delta)
		
		
		# update position
		self.pos += self.vel * delta

		# update heading is non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()

		self.world.wrap_around(self.pos)


	# Draw ourselves
	def render(self):
		egi.set_pen_color(self.color)
		
		renderShape = self.getRenderShape()

		egi.closed_shape(renderShape)


	# Returns our base shape, appropriately rotated and translated into world space
	def getRenderShape(self):

		matrix = Matrix33()
		matrix.rotate_update(self.rotation)
		matrix.transform_vector2d_list(self.rockShape)

		renderShape = copy.deepcopy(self.rockShape)
		matrix = Matrix33()
		matrix.translate_update(self.pos.x, self.pos.y)
		matrix.transform_vector2d_list(renderShape)

		return renderShape



	def speed(self):
		return self.vel.length()


	def speedSqrt(self):
		return sqrt(self.speed())


	# Quick collision detection
	def containsPoint(self, point):
		return self.pos.distanceSq(point) < self.boundingRadius**2


	# Returns a rocky looking shape based on our boundingRadius and edges
	def getRockShape(self):

		radius = self.boundingRadius
		edges = self.edges

		angle = 2 * pi / edges

		pts = []

		variance = 0.18
		variation = (1 - variance, 1 + variance)

		for i in range(edges):
			v = Vector2D(cos(i * angle), sin(i * angle)) * radius
			v.x *= uniform(variation[0],variation[1])
			v.y *= uniform(variation[0],variation[1])
			pts.append(v)

		return pts







		
