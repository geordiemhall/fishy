'''
Guppy
'''

from fish import Fish
from vector2d import Vector2D
from graphics import egi, KEY, COLOR_NAMES, rgba
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from matrix33 import Matrix33

import copy


from util import Util, DictWrap

from path import Path

class Guppy(Fish):
	def __init__(self, world=None, scale=30.0, mass=1.0, mode='wander'):

		self.super = super(Guppy, self)
		self.super.__init__(world=world, scale=scale, mass=mass, mode=mode)

		print 'Guppy init'

		# Set up some rendering properties
		self.color = self.getColor()
		self.initShape()
		

		# Child/parent value pairs for our stats. 
		# Scales are calculated from these, mapped to the size
		self._sizes = (0.0, 20.0)
		self._stats = DictWrap({
			'body': (0.7, 4.0),
			'mass': (0.5, 10.0),
			'speed': (100, 50),
			'flockingInfluence': (0.2, 0),
			'wanderDistance': (30, 50),
			'wanderRadius': (0.6 * self.scaleValue, 2.4 * self.scaleValue),
			'neighbourDistance': (100, 300)
		})

		# Set up the states
		# Acceleratino forces will be 
		self._state = 'idle'
		self._states = DictWrap({
			'idle': {
				'speedMultiplier': 1,
				'massMultiplier': 1,
				'wanderInfluence': 0.4,
				'steering': self.idleSteer
			},
			'feeding': {
				'speedMultiplier': 1.5,
				'massMultiplier': 0.5,
				'wanderInfluence': 0.1,
				'steering': self.feedingSteer
			}
		})


		self.size = self._sizes[0]
		self.varyVelocity = False


		

		# Calculates stats based on our current size, using the 
		# child/parent scales
		self.updateStats()
		self.vehicle_shape = self.fishShape # get an initial shape just in case

	
	def getColor(self):
		colors = [
			rgba('ffae00'),
			rgba('ff8400')
		]

		print colors

		return (uniform(colors[0][0], colors[1][0]),
				uniform(colors[0][1], colors[1][1]),
				uniform(colors[0][2], colors[1][2]),
				uniform(0.8, 1.0))




	def currentState(self):
		return self._states[self._state]

	

	# Calculates the value of a stat for a particular size
	# Interpolates linearly between the two bounds
	def statForSize(self, key, size):

		sizeRange = self._sizes 	# domain
		statRange = self._stats[key]	# range

		scale = Util.linearScale(sizeRange, statRange)

		clampedSize = Util.clamp(sizeRange[0], size, sizeRange[1])

		return scale(clampedSize)


	# Shorthand for statForSize, using the current size
	def stat(self, key):
		return self.statForSize(key, self.size)


	
	# Sets stats based on our current size
	# This way we only re-interpolate when the size changes
	# TODO: Run this on setattr size
	def updateStats(self):

		# Speed
		max = self.stat('speed')
		self.maxSpeed = max

		# Flocking influence
		self.flockingInfluence = self.stat('flockingInfluence')

		# Mass
		self.mass = self.stat('mass')

		# Fish shape
		self.body = self.stat('body')

		# Bounding radius (used in collision detection)
		self.boundingRadius = self.body * 25

		# Build our outline shape, scaled to body size
		self.fishShape = self.fishShapeForScale(self.body)
		

		# Wander distance
		# Make sure it's always outside the body, to prevent helicoptering
		self.wanderDistance = self.stat('wanderDistance')
		self.wanderRadius = self.stat('wanderRadius')
		self.neighbourDistance = self.stat('neighbourDistance')

		

	def swayShape(self):

		# TODO: Optimise this somehow. 
		# At the very least cache it so that both sway functions can use it without recalculating
		sqrtSpeed = self.speedSqrt()

		# Speed up fins as we slow down, illusion of swimming harder
		frequency = sqrtSpeed * 0.4
		# The bigger the fish, the slower it should paddle
		# frequency /= (1 + self.body * 0.25)

		frequency = Util.clamp(4, frequency, 10)

		# print 'sqrtSpeed', self.speedSqrt(), 'freq', frequency

		swayAngle = sin(self.world._clock * frequency)
		# print 'frequency', frequency

		swayRange = sqrtSpeed / 80
		# print 'swayRange', swayRange

		matrix = Matrix33()
		matrix.scale_update(1 + (swayAngle * 0.2 * sqrt(swayRange)), 1)
		# self.matrix.rotate_update(swayAngle * swayRange)

		shape = copy.deepcopy(self.fishShape)
		matrix.transform_vector2d_list(shape)
		
		return shape



	def swayPosition(self):

		sqrtSpeed = self.speedSqrt()
		frequency = sqrtSpeed * 0.4
		swayRange = sqrtSpeed / 10


		offsetAngle = cos((self.world._clock) * frequency / 2)
		offset = self.side * swayRange * offsetAngle
		position = self.pos + offset
		
		return position
		

	def drawEye(self, color=None):
		egi.set_pen_color(rgba('fff', 0.5))
		egi.circle(self.renderPosition + self.side * self.body, self.body)


	def beforeRender(self):
		# Update the rotation
		

		egi.green_pen()
		# line = self.matrix.transform_vector2d(Vector2D(0, 100))
		# egi.line_by_pos(self.pos, self.pos + line )

	def calculateRenderPosition(self):


		self.renderPosition = self.swayPosition()
		self.vehicle_shape = self.swayShape()
		
	
	def centerAttraction(self):
		return self.seek(self.world.tank.center())



	def calculateAcceleration(self, delta):

		state = self.currentState()

		wanderForce = self.wander(delta) * state.wanderInfluence
		
		flockForce = self.flock(delta) * self.flockingInfluence

		# obstaclesForce = self.obstacleAvoidance(self.world.solids)

		wallForce = self.wallAvoidance(self.world.tank.walls) * 2

		distanceFromCenterSq = (self.pos - self.world.center).lengthSq()

		amount = 1 + distanceFromCenterSq * 0.00002
		# if(distanceFromCenterSq > 50):
			# print 'amount', amount
		flockForce /= amount

		centerForce = self.seek(self.world.center)
		centerForce *= amount**2.2 * 0.01



		netForce = wanderForce + flockForce + wallForce + centerForce

		# print 'self.flockingInfluence', self.flockingInfluence

		if(self.world.debug.drawDebug):
			egi.blue_pen()
			egi.line_by_pos(self.pos, self.pos + wanderForce * 5)
			egi.green_pen()
			egi.line_by_pos(self.pos, self.pos + flockForce * 5)
			egi.orange_pen()
			egi.line_by_pos(self.pos, self.pos + netForce * 5)
			egi.red_pen()
			egi.line_by_pos(self.pos, self.pos + wallForce * 5)
			egi.set_pen_color(name='BROWN')
			egi.line_by_pos(self.pos, self.pos + centerForce * 5)


		

		

		# Save for debugging purposes
		self.force = netForce

		mass = self.mass * state.massMultiplier

		

		return netForce / mass




	# Calculates velocity based on our acceleration
	def calculateVelocity(self, delta):
		# new velocity
		vel = self.vel + self.acceleration * delta
		
		# check for limits of new velocity based on current state
		max = self.maxSpeed * self.currentState().speedMultiplier
		vel.truncate(max)

		if(self.varyVelocity):
			frequency = 8


			offsetAngle = (cos((self.world._clock) * frequency / 2)) * 0.1 + 0.1
			
			vel *= (1 + offsetAngle + uniform(0, 0.1))


		return vel


	def idleSteer(self, delta):
		pass

	def feedingSteer(self, delta):
		pass




	def initShape(self):

		

		P = Vector2D
		
		# Made using BeTravis's excellent path-to-polygon tool
		# http://betravis.github.io/shape-tools/path-to-polygon/

		baseShape = [
			P(1.35, 0.23),
			P(1.09, 0.26),
			P(0.86, 0.33),
			P(0.67, 0.45),
			P(0.54, 0.60),
			P(0.01, 0.03),
			P(0.01, 1.59),
			P(0.53, 1.03),
			P(0.66, 1.19),
			P(0.85, 1.31),
			P(1.08, 1.39),
			P(1.35, 1.42),
			P(1.70, 1.37),
			P(1.98, 1.25),
			P(2.16, 1.06),
			P(2.23, 0.83),
			P(2.16, 0.59),
			P(1.98, 0.41),
			P(1.70, 0.28),
			P(1.35, 0.23)
		]

		maxX = max(baseShape, key= lambda d: d.x).x
		maxY = max(baseShape, key= lambda d: d.y).y
		minX = min(baseShape, key= lambda d: d.x).x
		minY = min(baseShape, key= lambda d: d.y).y

		w = maxX - minX
		h = maxY - minY

		desiredWidth = 3
		desiredHeight = 2


		# Reset to zero
		Util.translatePoints(baseShape, x=-minX, y = -minY)
		# Scale to height/width
		Util.scalePoints(baseShape, x = desiredWidth/w, y = desiredHeight/h)
		# Set center point to mid-tail
		# Util.translatePoints(baseShape, x=desiredWidth * -0.6, y=-desiredHeight/2)
		# Set center point to mid-head
		Util.translatePoints(baseShape, x=desiredWidth * -0.9, y=-desiredHeight/2)

		self.baseFishShape = baseShape




	# Get the fish shape based on a scale
	def fishShapeForScale(self, scale = 1):

		baseShape = copy.deepcopy(self.baseFishShape)
		points = Util.scalePoints(baseShape, scale, scale)

		return points








	def render(self):
		

		self.super.render()

		
		
		




