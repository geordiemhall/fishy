''' 

Food 
=================================='''

from vector2d import Vector2D
from graphics import egi, rgba
from random import uniform


class Food(object):
	"""Food object"""
	def __init__(self, world=None):
		
		self.world = world

		self.pos = Vector2D()
		self.vel = Vector2D()

		self.maxAirSpeed = 500
		self.maxWaterSpeed = 50
		self.radius = uniform(5, 10)

		self.color = rgba('ecc200')


	def calculateAcceleration(self, delta):

		accel = self.world.gravity.copy()

		return accel

	# Calculates velocity based on our acceleration
	def calculateVelocity(self, delta):
		# new velocity
		vel = self.vel + self.acceleration * delta
		
		# check for limits of new velocity
		max = self.maxWaterSpeed
		if(self.pos.y > self.world.tank.box.top):
			max = self.maxAirSpeed
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

	def render(self):
		egi.set_pen_color(self.color)
		egi.circle(self.pos, self.radius)
		
