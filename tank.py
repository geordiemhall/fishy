from vector2d import Rect
from util import DictWrap
from graphics import egi
from random import uniform
from vector2d import Vector2D



class Tank(object):

	def __init__(self, world = None):
		self.world = world

		
		self.margin = DictWrap({
			'left': 10,
			'top': 100,
			'right': 10,
			'bottom': 10
		})

		self.resize()

	def randomPosition(self):
		return Vector2D(uniform(0, self.world.width), uniform(0, self.world.height))
		

	def resize(self):
		m = self.margin
		bounds = DictWrap({
			'left': m.left,
			'top': self.world.height - m.top,
			'right': self.world.width - m.right,
			'bottom': m.bottom
		})

		self.box = Rect(bounds)

		self.size = DictWrap({
			'width': self.box.right - self.box.left,
			'height': self.box.top - self.box.bottom
		})

	def render(self):
		egi.blue_pen()
		egi.rect(*self.box.getBox())