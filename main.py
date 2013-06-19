'''

Fish Tank
===============================

Created for HIT3046 AI for Games Distinction Project
Geordie Hall (9525742)




Simulates basic fish tank scenario, with passive hunter,
fish that eat food and grow in size, die, and hide from hunter.

Instructions are printed on the screen, though I recommend hiding them
because pyglet's horrible at rendering text.

They're all pretty self-explanatory, except one...

"Circle of Life", when enabled, makes every fish get hungrier over
time (green fish = starving), and makes food spawn automatically
throughout the tank. If fish get too hungry or swim into the hunter's
mouth then they die. Once they reach a certain size, every time 
they eat they make two children. A fish won't feed while the hunter 
is awake unless they are really hungry. The fatter a fish, the slower it is.
Disabled by default cause it gets a bit hectic.

When the hunter is red, it means he's awake. Purple is sleeping.
When fish are pink, it means they're parents.
When fish are green (or blue, if parents) it means they're hungry.

If you maximize the window you should probably reset the world so that things
are distributed nicely again.


'''

# Vendor imports
from graphics import egi, KEY, rgba
from pyglet import window, clock
from pyglet.gl import *

# Our imports
from world import World



class Game(object):
	''' The main game object ''' 
	def __init__(self, width=900, height=700, antialiased=True):
		
		self.width = width
		self.height = height
		self.antialiased = antialiased
		self.backgroundColor = rgba('1d1f21') # Dull grey


		# Create the pyglet window and context
		self.createWindow()

		# Make and clear the world
		self.resetWorld()

		# Make sure everything's in place and sized correctly
		self.on_resize(self.width, self.height)

		# Start the game loop!
		self.gameLoop()

		
	# Creates a pyglet window and set glOptions
	def createWindow(self):
		
		self.win = None
		if(self.antialiased):
			config = pyglet.gl.Config(sample_buffers=1, samples=4, double_buffer=True)
			self.win = window.Window(width=self.width, height=self.height, vsync=True, resizable=True, config=config)
		else:
			self.win = window.Window(width=self.width, height=self.height, vsync=True, resizable=True)
		
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		# needed so that egi knows where to draw
		egi.InitWithPyglet(self.win)

		# prep the fps display
		self.fps_display = clock.ClockDisplay()
		self.fps_display.label.color = rgba('fff', 0.05)

		# register key and mouse event handlers
		self.win.push_handlers(self.on_key_press)
		self.win.push_handlers(self.on_mouse_press)
		self.win.push_handlers(self.on_resize)


	# Creates a new world and sets up its initial state
	def resetWorld(self):

		# create a world for fishes!
		self.world = World(self.width, self.height)

		# Build our info state and assign it to the world
		self.makeInfo()
		
		# add initial fishies
		self.world.addFish(10)


	# Just fills the screen with a solid color
	def renderBackground(self):
		
		egi.set_pen_color(self.backgroundColor)
		egi.rect(0, self.height, self.width, 0, filled=True)
		

	def gameLoop(self):
		# Main game loop
		while not self.win.has_exit:

			# House keeping, fire events
			self.win.dispatch_events()
			glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

			# Render the background
			# Now separate from the world's rendering so that debug rendering
			# done in update() will still appear above the bg
			self.renderBackground()

			# Update and render the world
			delta = clock.tick()
			self.world.update(delta)
			
			self.world.render()

			# show nice FPS top left
			self.fps_display.draw()

			# Draw our instructions if enabled
			self.drawInfo()
			
			# swap the double buffer
			self.win.flip()


	# Window resize event
	def on_resize(self, width, height):
		# Update our dimensions
		self.width = width
		self.height = height
		
		# Resize down the view chain
		self.world.resize(width, height)

		# Updat the position of the fps display
		self.fps_display.label.y = self.height - 48


	# Mouse click
	def on_mouse_press(self, x, y, button, modifiers):
		
		if button == 1: # left
		# Just call this manually
			self.world.addFood(x=x, y=y) 


	# Key press event listener
	def on_key_press(self, symbolCode, modifiers):

		keyString = self.getKeyStringFromSymbol(symbolCode)

		if(keyString is None): return

		if('action' in self.info[keyString]):
			self.actionForKeyString(keyString)

		if('toggle' in self.info[keyString]):
			self.toggleForKeyString(keyString)


	# Returns a string representing the given symbolCode
	# Eg. 97 => 'A'
	def getKeyStringFromSymbol(self, symbolCode):

		for keyString, props in self.info.iteritems():
			if(len(keyString) == 1 and getattr(KEY, keyString) == symbolCode):
				return keyString

		return None


	# Build our info object and set its defaults in the world
	def makeInfo(self):

		# if(not hasattr(self, 'info')):
		self.info = {

			# Actions
			'LMB': {
				'label': 'Add food'
			},
			'A': {
				'label': 'Add fish',
				'action': self.world.addFish
			},
			'R': {
				'label': 'Reset world',
				'action': self.resetWorld
			},

			# Toggles
			'I': {
				'label': 'Draw instructions (laggy)',
				'enabled': True,
				'toggle': (self, 'showInfo')
			},
			'C' : {
				'label': 'Circle of Life (and death)',
				'enabled': False,
				'toggle': (self.world, 'lionKing')
			},
			'D': {
				'label': 'Draw wander info',
				'enabled': False,
				'toggle': (self.world, 'drawDebug')
			},
			'S': {
				'label': 'Hunter sleep cycle',
				'enabled': True,
				'toggle': (self.world, 'awokenHunter')
			},
			'F': {
				'label': 'Draw flocking forces',
				'enabled': False,
				'toggle': (self.world, 'drawComponentForces')
			},
			'P': {
				'label': 'Pause',
				'enabled': False,
				'toggle': (self.world, 'paused')
			},
			'H': {
				'label': 'Draw hiding spots',
				'enabled': False,
				'toggle': (self.world, 'drawHidingSpots')
			}
		}

		# Set default values for toggles
		for key, props in self.info.iteritems():
			if('toggle' in props):
				context, attr = props['toggle']
				setattr(context, attr, props['enabled'])


	# Perform the action for a specific key
	def actionForKeyString(self, keyString):

		self.info[keyString]['action']()


	# Toggle the property for a specific key
	def toggleForKeyString(self, keyString):

		# Grab our data
		keyData = self.info[keyString]
		context, attr = keyData['toggle']

		# Perform the toggle
		context.__setattr__(attr, not keyData['enabled'])
		keyData['enabled'] = not keyData['enabled']


	# Draw our key info to the screen if enabled
	def drawInfo(self):
		
		if not self.showInfo: return
		
		# Formatting
		lineHeight = 24
		offset = (33, 30)
		
		# Loop through and draw each prop
		i = 0
		for key, props in self.info.iteritems():
			# draw the key
			egi.text_color(name='GREY')
			egi.text_at_pos(offset[0] + 0, (offset[1] + i * lineHeight), key)

			# draw the label
			egi.text_color(name='WHITE')
			if('enabled' in props and props['enabled']):
				egi.text_color(name='GREEN')
			
			egi.text_at_pos(offset[0] + 50, (offset[1] + i * lineHeight), props['label'])

			i += 1




# Run the game if we're the entry point
if __name__ == '__main__':

	game = Game(width=1400, height=800)



	

	

