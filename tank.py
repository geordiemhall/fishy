from vector2d import Rect
from util import DictWrap
from graphics import egi
from random import uniform
from vector2d import Vector2D

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

class Tank(object):

	def __init__(self, world = None):
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


	def render(self):
		egi.blue_pen()
		egi.rect(*self.box.getBox())

		if(self.world.debug.drawDebug):
			for wall in self.walls:
				egi.line_by_pos(wall.center, wall.center + wall.normal * 100)



		