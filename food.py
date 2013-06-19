''' 

Food 
=================================='''

# Vendor imports
from vector2d import Vector2D
from graphics import egi, rgba
from random import uniform
from math import sqrt, sin


"""
Simple Food object with different physics if outside the tank

"""
class Food(object):
	
	def __init__(self, world=None):
		
		self.world = world

		self.pos = Vector2D()
		self.vel = Vector2D()

		self.maxAirSpeed = 500
		self.maxWaterSpeed = 40
		self.boundingRadius = uniform(3, 7)

		self.color = rgba('ffe400')
		self.eaten = False

		self.heading = Vector2D(0, 1)
		self.side = self.heading.perp()


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

		frequency = 5
		pulse = sin(self.world._clock * frequency)

		range = 0.2
		pulse = 1 + (pulse * range) 
		r = self.boundingRadius * pulse
		
		egi.circle(self.pos, r, filled=True)


	def speed(self):
		return self.vel.length()


	def speedSqrt(self):
		return sqrt(self.speed())




		
