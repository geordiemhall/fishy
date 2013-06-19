'''
Hunter
'''

# Vendor imports

from graphics import egi, rgba
from math import sin, cos, sqrt
from random import uniform
from matrix33 import Matrix33
from pyglet import clock
from util import Util, DictWrap
from copy import deepcopy

# Our imports

from fish import Fish



class Hunter(Fish):
	def __init__(self, world=None, scale=30.0, mass=1.0):

		self.super = super(Hunter, self)
		self.super.__init__(world=world, scale=scale, mass=mass, )

		print 'Hunter, do your thing!'

		self._stats = {
			'body': 2,
			'mass': 5.8,
			'maxSpeed': 50,
			'wanderDistance': 520,
			'wanderRadius': 30
		}

		# Set up some rendering properties

		# Colors
		self.sleepColor = rgba('8e4bb5') # purple
		self.awakeColor = rgba('e41414') # red

		self.sleepTime = (9, 12)
		self.awakeTime = (5, 8)
		
		self.initShape()

		self.varyVelocity = False
		self.feedRadius = 30
		self.awake = True
		self.toggleAwake()

		self.sightCircle = {
			'pos': self.pos.copy(),
			'distance': 80,
			'radius': 250
		}

		self.sightCircle['radiusSq'] = self.sightCircle['radius']**2
		self.size = 50

		# Set up the states
		# Acceleratino forces will be 
		self._state = 'patrol'
		self._states = DictWrap({
			'patrol': {
				'speedMultiplier': 0.5,
				'massMultiplier': 1,
				'wanderInfluence': 0.2,
				'feelerPercentage': 2.0, 
				'acceleration': self.patrolSteer
			}
		})

		# Calculates stats based on our current size, using the 
		# child/parent scales
		self.updateStats()
		self.vehicle_shape = self.fishShape # get an initial shape just in case
		self.vel.x = -self.maxSpeed


	# Switch between sleep and awake states if enabled
	def toggleAwake(self, dt = 0):


		if(self.world.awokenHunter):
			self.awake = not self.awake
		else:
			self.awake = False

		
		if(self.awake):
			# If we just woke up
			clock.schedule_once(self.toggleAwake, uniform(*self.awakeTime))
		else:
			# We just fell asleep, sleep for 5 to 8 seconds
			clock.schedule_once(self.toggleAwake, uniform(*self.sleepTime))

	
	@property
	def awake(self):
		return self._awake


	@awake.setter
	def awake(self, value):
		self._awake = value
		
		if(self._awake):
			self.color = self.awakeColor
		else:
			self.color = self.sleepColor

		self.updateStats()
	

	# Do any actions we have at the start of update
	def performActions(self):


		self.updateState()
		self.eatNearbyFish()


	def updateState(self):

		self._state = self.calculateCurrentState()

		self.state = self._states[self._state]


	# Always be patrollin'
	def calculateCurrentState(self):
		state = 'patrol'

		return state


	

	

	
	# Sets stats based on our current size 
	# (more useless on hunter cause it doesn't change size)
	def updateStats(self):

		for key, val in self._stats.iteritems():
			self.__setattr__(key, val)

		# Calculate a few other props based on our stats
		self.fishShape = self.fishShapeForScale(self.body)
		self.boundingRadius = self.body * 25

		
		if(self.awake): self.maxSpeed *= 3
		

	# Called right at the start of update()
	# Basically just cache some frequently used variables
	def beforeUpdate(self):
		# Cache this value cause we use it twice in different methods
		self.speedSqrt = sqrt(self.speed())
		self.sightCircle['pos'] = self.pos + self.heading * self.sightCircle['distance']


	def swayShape(self):

		# TODO: Optimise this more 
		sqrtSpeed = self.speedSqrt

		# Speed up fins as we slow down, gives the illusion of swimming harder
		frequency = sqrtSpeed * 0.4

		frequency = Util.clamp(2, frequency, 2.5)
		swayAngle = sin(self.world._clock * frequency)
		swayRange = sqrtSpeed / 80

		matrix = Matrix33()
		matrix.scale_update(1 + (swayAngle * 0.2 * sqrt(swayRange)), 1)

		shape = deepcopy(self.fishShape)
		matrix.transform_vector2d_list(shape)
		
		return shape


	# Vary our position slightly from side to side, like fish do
	def swayPosition(self):

		sqrtSpeed = self.speedSqrt
		# frequency = sqrtSpeed * 0.4
		frequency = 0.1 * sqrtSpeed
		swayRange = 0.2 * sqrtSpeed


		offsetAngle = cos((self.world._clock) * frequency / 2)
		offset = self.side * swayRange * offsetAngle
		position = self.pos + offset
		
		return position
		

	# Render our eye, different depending on awake or asleep
	def drawEye(self, color=None):
		
		eyePosition = self.renderPosition + self.side * self.body * -8 - self.heading * 20

		eyeRadius = self.body * 0.8
		if(self.awake):
			egi.circle(eyePosition, eyeRadius)
		else:
			egi.line_by_pos(eyePosition, eyePosition + self.heading * eyeRadius * 2)


	# We only sway if we're awake
	def calculateRenderPosition(self):

		self.renderPosition = self.pos
		self.vehicle_shape = self.fishShape

		# Perf drops too much by transforming this many points :(
		# self.renderPosition = self.swayPosition()
		if(self.awake): self.vehicle_shape = self.swayShape()


	# Can we see a particular position?
	# TODO: Use circle/line intersection on each obstacle to determine line of sight
	def canSeePosition(self, pos):

		return self.sightCircle['pos'].distanceSq(pos) < self.sightCircle['radiusSq']
		




	def calculateAcceleration(self, delta):

		self.state = self.state
		self.feelerPercentage = self.state.feelerPercentage


		stateForce = self.state.acceleration(delta)

		wallForce = self.wallSteer(delta)

		netForce = stateForce + wallForce
		

		# Save for debugging purposes
		self.force = netForce

		mass = self.mass * self.state.massMultiplier


		return netForce / mass




	# Calculates velocity based on our acceleration
	def calculateVelocity(self, delta):

		# new velocity
		vel = self.vel + self.acceleration * delta
		
		# check for limits of new velocity based on current state
		max = self.maxSpeed * self.state.speedMultiplier
		vel.truncate(max)

		if(self.varyVelocity):
			frequency = 8


			offsetAngle = (cos((self.world._clock) * frequency / 2)) * 0.1 + 0.1
			
			vel *= (1 + offsetAngle + uniform(0, 0.1))


		return vel


	# Avoids the tank walls
	def wallSteer(self, delta):

		wallForce = self.wallAvoidance(self.world.tank.getWalls('vertical')) * 2

		if(self.chosenOne and self.world.drawDebug):
			egi.red_pen()
			egi.line_by_pos(self.pos, self.pos + wallForce * 5)

		return wallForce




	def keepInsideTank(self):
		p = self.pos

		tank = self.world.tank.box
		
		if(p.y > tank.top):
			print 'above tank'
			p.y = tank.top

		if(p.y < tank.bottom):
			p.y = tank.bottom



	def patrolSteer(self, delta):

		wanderForce = self.wander(delta) * self.state.wanderInfluence

		netForce = wanderForce

		if(self.chosenOne and self.world.drawDebug):
			egi.blue_pen()
			egi.line_by_pos(self.pos, self.pos + wanderForce * 5)
			egi.orange_pen()
			egi.line_by_pos(self.pos, self.pos + netForce * 5)

		return netForce


	# Eats any fish within our feedRadius
	def eatNearbyFish(self):
				
		[self.eat(f) for f in self.world.livingFishes if f.pos.distanceSq(self.pos) < (self.feedRadius + f.boundingRadius)**2]

	# Kill a fish
	def eat(self, fish):
		# Make sure no-one else has eaten the food before us
		if(fish.dead): return

		fish.dead = True


	# Build our shape from the poly string
	def initShape(self):
		
		# Made using BeTravis's excellent path-to-polygon tool
		# http://betravis.github.io/shape-tools/path-to-polygon/

		shapeString = '47.875 10.129, 47.091 10.429, 50.038 13.703, 51.508 16.329, 50.622 17.315, 35.019 21.192, 31.619 22.820, 26.750 27.628, 9.999 16.438, 3.670 14.198, 5.491 18.014, 7.677 19.216, 9.654 23.058, 8.750 34.379, 9.609 43.981, 8.486 49.628, 4.375 54.754, 3.142 55.663, 3.120 55.721, 3.204 55.742, 6.110 55.203, 12.442 51.855, 28.750 40.171, 31.258 42.745, 35.508 45.604, 46.636 52.190, 59.583 55.003, 70.905 54.847, 86.508 50.575, 94.915 47.442, 96.631 45.867, 95.752 45.172, 96.072 43.403, 95.389 38.601, 92.417 42.275, 91.407 42.932, 82.636 40.559, 74.775 34.371, 71.972 29.398, 84.053 31.841, 91.164 30.089, 91.912 32.935, 92.397 32.478, 93.725 30.148, 95.227 29.860, 95.796 29.545, 91.717 24.247, 89.413 23.425, 89.065 22.176, 87.670 21.576, 76.305 19.670, 74.395 18.987, 62.815 12.896, 53.604 10.500, 47.875 10.129, 47.875 10.129'

		baseShape = Util.shapeFromString(shapeString)


		maxX = max(baseShape, key= lambda d: d.x).x
		maxY = max(baseShape, key= lambda d: d.y).y
		minX = min(baseShape, key= lambda d: d.x).x
		minY = min(baseShape, key= lambda d: d.y).y

		w = maxX - minX
		h = maxY - minY

		aspect = h/w

		desiredWidth = 3
		desiredHeight = aspect * desiredWidth


		# Reset to zero
		Util.translatePoints(baseShape, x=-minX, y = -minY)
		
		# Scale to height/width
		Util.scalePoints(baseShape, x = desiredWidth/w, y = desiredHeight/h)

		# Set center point to mid-head
		Util.translatePoints(baseShape, x=desiredWidth * -0.9, y=-desiredHeight/2)

		self.baseFishShape = baseShape




	# Get the fish shape based on a scale
	def fishShapeForScale(self, scale = 1):

		baseShape = deepcopy(self.baseFishShape)
		points = Util.scalePoints(baseShape, scale, scale)

		return points







	# Draw ourselves
	def render(self):

		self.super.render()

		# Draw our sight radius
		if(self.chosenOne and self.world.drawHidingSpots):
			egi.red_pen()
			egi.circle(self.sightCircle['pos'], self.sightCircle['radius'])



		
		
		




