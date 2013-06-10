'''
Guppy
'''

from fish import Fish
from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import sin, cos, radians
from random import random, randrange, uniform

from util import Util
from path import Path

class Guppy(Fish):
	def __init__(self, world=None, scale=30.0, mass=0.5, mode='wander'):

		self.super = super(Guppy, self)
		self.super.__init__(world=world, scale=scale, mass=mass, mode=mode)

		print 'Guppy init'

		self.initRendering()


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

		desiredWidth = 3
		desiredHeight = 2

		print maxX, maxY, minX, minY

		Util.translatePoints(fishShape, x=-minX, y = -minY)
		Util.scalePoints(fishShape, x = desiredWidth/w, y = desiredHeight/h)



		Util.translatePoints(fishShape, x=desiredWidth * -0.3, y=-desiredHeight/2)

		self.vehicle_shape = fishShape



	def render(self):
		self.super.render()
		
		egi.white_pen()
		egi.circle(self.pos, 2)




