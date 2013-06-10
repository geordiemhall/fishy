from vector2d import Rect
from util import DictWrap
from graphics import egi


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
		

	def resize(self):
		m = self.margin
		bounds = DictWrap({
			'left': m.left,
			'top': self.world.height - m.top,
			'right': self.world.width - m.right,
			'bottom': m.bottom
		})

		self.box = Rect(bounds)

	def render(self):
		egi.blue_pen()
		egi.rect(*self.box.getBox())