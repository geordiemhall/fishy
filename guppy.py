'''
Guppy
'''

from fish import Fish
from vector2d import Vector2D
from graphics import egi, KEY
from math import sin, cos, radians
from random import random, randrange, uniform
import copy

from util import Util, DictWrap
from path import Path

class Guppy(Fish):
	def __init__(self, world=None, scale=30.0, mass=1.0, mode='wander'):

		self.super = super(Guppy, self)
		self.super.__init__(world=world, scale=scale, mass=mass, mode=mode)

		print 'Guppy init'

		self.initRendering()
		

		# Child/parent value pairs for our stats. 
		# Scales are calculated from these, mapped to the size
		self.stats = DictWrap({
			'size': (0.0, 20.0),
			'body': (1.3, 7.0),
			'mass': (0.8, 10.0),
			'speed': (38.0 * self.scaleValue, 10.0 * self.scaleValue),
			'flocking': (1.0, 0.0)
		})

		self.size = randrange(*self.stats.size)

		

		# Scales, used when calculating stats based on the size
		

		self.updateStats()

	#  Returns a scaling function based on tuples for domain and range
	def linearScale(self, domain, range):

		rise = range[1] - range[0]
		run = domain[1] - domain[0]
		
		m = rise / run
		c = range[1] - m * domain[1]

		def f(x):
			return m * x + c

		return f


	def statForSize(self, key, size):

		sizeRange = self.stats.size # domain
		statRange = self.stats[key]	# range

		scale = self.linearScale(sizeRange, statRange)

		return scale(size)


	
	# Sets stats based on our current size
	# TODO: Run this on setattr size
	def updateStats(self):

		# Speed
		self.max_speed = self.statForSize('speed', self.size)

		# Flocking influence
		self.flockingInfluence = self.statForSize('flocking', self.size)

		# Mass
		self.mass = self.statForSize('mass', self.size)

		# Fish shape
		body = self.statForSize('body', self.size)
		self.vehicle_shape = self.fishShapeForScale(body)

		print 'vehicle shape', [ d.__str__() for d in self.vehicle_shape]


	def calculate(self, delta):

	    # self.force = self.flock(delta)
	    wanderForce = self.wander(delta)
	    flockForce = self.flock(delta)

	    netForce = wanderForce + self.flockingInfluence * flockForce

	    # For debugging purposes
	    self.force = netForce

	    return netForce / self.mass



	def initRendering(self):

		self.color = 'ORANGE'

		P = Vector2D
		
		# Made using BeTravis's excellent path-to-polygon tool
		# http://betravis.github.io/shape-tools/path-to-polygon/

		fishShape = [
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

		maxX = max(fishShape, key= lambda d: d.x).x
		maxY = max(fishShape, key= lambda d: d.y).y
		minX = min(fishShape, key= lambda d: d.x).x
		minY = min(fishShape, key= lambda d: d.y).y

		w = maxX - minX
		h = maxY - minY

		desiredWidth = 1.5
		desiredHeight = 1


		# Reset to zero
		Util.translatePoints(fishShape, x=-minX, y = -minY)
		# Scale to height/width
		Util.scalePoints(fishShape, x = desiredWidth/w, y = desiredHeight/h)
		# Set center point to mid-tail
		# Util.translatePoints(fishShape, x=desiredWidth * -0.3, y=-desiredHeight/2)
		Util.translatePoints(fishShape, x=desiredWidth / -2, y=desiredHeight*0)

		self.baseFishShape = fishShape

		print 'fishShape', [ d.__str__() for d in fishShape]



	# Get the fish shape based on a scale
	def fishShapeForScale(self, scale = 1):

		baseShape = copy.deepcopy(self.baseFishShape)
		points = Util.scalePoints(baseShape, scale, scale)

		return points








	def render(self):
		

		self.super.render()
		
		egi.white_pen()
		egi.circle(self.pos, 2)




