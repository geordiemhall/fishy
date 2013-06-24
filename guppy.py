'''
Guppy
'''

# Vendor imports

from math import sin, cos, sqrt, pi
from random import uniform, choice
from matrix33 import Matrix33
from graphics import egi, rgba
from copy import deepcopy
from util import Util, DictWrap
from vector2d import Vector2D

# Our imports

from fish import Fish



class Guppy(Fish):
	def __init__(self, world=None, scale=30.0, mass=1.0):

		self.super = super(Guppy, self)
		self.super.__init__(world=world, scale=scale, mass=mass)

		print 'Guppy, ' + choice(['I choose you!', 'get out there!', 'do your thang!', 'swim allll up in this!', 'not splash again!', 'evolve already! God.'])

		# Set up some rendering properties

		# Colors
		self.sickColor = rgba('2fc900')
		self.deadColor = rgba('973500')
		self.regularColors = [
			rgba('ffae00'),
			rgba('ff8400')
		]
		
		self.initShape()
		
		self._sicknessDomain = (0.0, 100.0)
		self._sickness = self._sicknessDomain[0]
		# self._sickness = 0
		self.sicknessRate = 1

		self.varyVelocity = False
		self.feedRadius = 20
		self.food = []
		self.isParent = False

		self.recalculateColor()

		# Child/parent value pairs for our stats. 
		# Scales are calculated from these, mapped to the size
		

		self._sizes = (0.0, 20.0)
		self._stats = DictWrap({
			'body': (0.7, 2.0),
			'mass': (1.2, 1.5),
			'speed': (200, 100),
			'flockingInfluence': (0.25, 0),
			'wanderDistance': (40, 50),
			'wanderRadius': (2.2 * self.scaleValue, 2.4 * self.scaleValue),
			'neighbourDistance': (100, 300)
		})

		# Set up the states
		# Acceleratino forces will be 
		self._state = 'idle'
		self._states = DictWrap({
			'idle': {
				'speedMultiplier': 0.5,
				'massMultiplier': 1,
				'wanderInfluence': 0.9,
				'feelerPercentage': 1.5, 
				'acceleration': self.idleSteer
			},
			'seekFood': {
				'speedMultiplier': 2.5,
				'massMultiplier': 0.5,
				'wanderInfluence': 0.1,
				'feelerPercentage': 0.5,
				'acceleration': self.feedingSteer
			},
			'hide': {
				'speedMultiplier': 5.5,
				'massMultiplier': 0.5,
				'wanderInfluence': 0.1,
				'feelerPercentage': 0.3,
				'acceleration': self.scaredSteer
			},
			'dead': {
				'speedMultiplier': 1.0,
				'massMultiplier': 1.0,
				'wanderInfluence': 0.1,
				'feelerPercentage': 0.5,
				'acceleration': self.deadSteer
			}
		})


		self._size = self._sizes[0]
		self.maxCenterForce = 250
		

		


		

		# Calculates stats based on our current size, using the 
		# child/parent scales
		self.updateStats()
		self.vehicle_shape = self.fishShape # get an initial shape just in case

	
	@property
	def size(self):
		return self._size


	@size.setter
	def size(self, value):
		self._size = Util.clamp(self._sizes[0], value, self._sizes[1])
		self.updateStats()


	def sicker(self):
		self.sickness += self.sicknessRate

	@property
	def sickness(self):
		return self._sickness

	
		

	@sickness.setter
	def sickness(self, value):
		self._sickness = Util.clamp(self._sicknessDomain[0], value, self._sicknessDomain[1])


		# If we are too sick, then we're dead (for now!)
		if(self._sickness > self._sicknessDomain[1] - 1):
			self.dead = True
			
		# Sickness has changed, so recalculate our color
		self.recalculateColor()


	@property
	def dead(self):
		return self._dead


	@dead.setter
	def dead(self, value):
		self._dead = value
		self.recalculateColor()
		
	
	def colorForSickness(self, sickness, colorScale):
		# Make sure it's within range
		sick = Util.clamp(self._sicknessDomain[0], sickness, self._sicknessDomain[1])
		
		# Interpolate colors
		c = colorScale
		return (c['r'](sick), c['g'](sick), c['b'](sick), c['a'](sick))





	def recalculateColor(self):
		
		if(self.dead):
			self.color = self.deadColor
			return
		
		healthyColor = self.getHealthyColor()
		sickColor = self.getSickColor()


		d = self._sicknessDomain

		colorScale = {
			'r': Util.linearScale(d, (healthyColor[0], sickColor[0])),
			'g': Util.linearScale(d, (healthyColor[1], sickColor[1])),
			'b': Util.linearScale(d, (healthyColor[2], sickColor[2])),
			'a': Util.linearScale(d, (healthyColor[3], sickColor[3]))
		}

		self.color = self.colorForSickness(self.sickness, colorScale)

	def getSickColor(self):
		parentSickColor = rgba('27c8f0')

		if(self.isParent):
			return parentSickColor

		return self.sickColor


	def getHealthyColor(self):

		parentColor = rgba('f43ca0')

		if(self.isParent):
			return parentColor

		colors = self.regularColors

		return (uniform(colors[0][0], colors[1][0]),
				uniform(colors[0][1], colors[1][1]),
				uniform(colors[0][2], colors[1][2]),
				uniform(0.8, 1.0))


	def performActions(self):
		
		self.eatNearbyFood()


	def calculateCurrentState(self):
		
		if(self.dead):
			return 'dead'

		# We're not dead!

		state = 'idle'
		
		# If there's some food in the tank...
		if(len(self.food)):
			state = 'seekFood'

		# If any hunters are awake
		if(True in [h.awake for h in self.world.hunters]):
			state = 'hide'

			# But if we're super sick, then 
			if(self.sickness > self._sicknessDomain[1] * 0.7):
				state = 'seekFood'

		return state

	def currentState(self):

		self._state = self.calculateCurrentState()

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

		# If we're pretty fat
		if(self.size > self._sizes[1] * 0.8):
			self.isParent = True



		





	'''
	Update logic
	=====================================
	'''




	def beforeUpdate(self):

		# Cache this value cause we use it twice in different methods
		self.speedSqrt = sqrt(self.speed())
		self.state = self.currentState()
		# Grab our food
		self.food = self.world.getFood(self)



	def calculateAcceleration(self, delta):

		
		self.feelerPercentage = self.state['feelerPercentage']


		# Grab the base acceleration from whatever our current state is
		stateForce = self.state['acceleration'](delta)

		# All states need to steer away from walls
		wallForce = self.wallSteer(delta)

		# Calculate the net force
		netForce = stateForce + wallForce 

		# Save for debugging purposes
		self.force = netForce

		# Calculate our mass based on our current state
		mass = self.mass * self.state['massMultiplier']

		

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










	'''
	Steering behaviours
	=====================================
	'''

	def scaredSteer(self, delta):
		hideForce =  self.hidingSteer(delta, closest=False)
		avoidHuntersForce, hunterDist = self.avoidHuntersSteer(delta)

		return hideForce + avoidHuntersForce


	def survivalSteer(self, delta):
		avoidHunters, hunterDist = self.avoidHuntersSteer(delta)
		# avoidHunters *
		hideForce =  self.hidingSteer(delta) / (hunterDist / 20000) / (avoidHunters.length() / 100)

		steer = avoidHunters + hideForce 

		if(self.chosenOne and self.world.drawHidingSpots):
			egi.green_pen()
			egi.line_by_pos(self.pos, self.pos + avoidHunters * 5)
			# print 'avoidHunters', avoidHunters
			egi.red_pen()
			egi.line_by_pos(self.pos, self.pos + hideForce * 5)
			# print 'hideForce', hideForce
			egi.orange_pen()
			# egi.line_by_pos(self.pos, self.pos + steer * 5)
			

		return steer


	


	# Simple acceleration downwards from the world's gravity
	def deadSteer(self, delta):

		return self.world.gravity * self.mass


	# Steers away from hunters, getting stronger as you get closer
	def avoidHuntersSteer(self, delta):

		hunterPositions = [h.pos for h in self.world.hunters]
		count = len(hunterPositions)

		if(count == 0):
			return Vector2D()
		
		total = reduce(lambda x, y: x + y, hunterPositions)
		avg = total / float(count)

		distance = self.pos.distanceTo(avg)
		lengthSq = distance.lengthSq()**1.1

		steer = -5000000 * distance.normalise() / lengthSq

		

		return steer, lengthSq



	# Avoids the tank walls. The force gets stronger the closer you are to them
	def wallSteer(self, delta):

		wallForce = self.wallAvoidance(self.world.tank.getWalls('vertical')) * 2

		if(self.chosenOne and self.world.drawDebug):
			egi.red_pen()
			egi.line_by_pos(self.pos, self.pos + wallForce * 5)

		return wallForce


	# Perform any collision detection we want to do
	def collisionDetection(self):
		
		self.keepInsideTank()


	# Physically prevents fish from being outside the tank bounds
	def keepInsideTank(self):
		p = self.pos

		tank = self.world.tank.box
		
		if(p.y > tank.top):
			p.y = tank.top
			self.vel.y *= -0.5

		if(p.y < tank.bottom and not self.dead):
			p.y = tank.bottom

		# Don't bother on the left and right
		# if(p.x > tank.right):
		# 	p.x = tank.right
		# 	self.vel.x *= -0.5

		# if(p.x < tank.left):
		# 	p.x = tank.left
		# 	self.vel.x *= -0.5


	def hidingSteer(self, delta, closest=True):

		hiding = self.hide(hunters=self.world.hunters, obstacles=self.world.obstacles, closest=closest)

		if(self.chosenOne and self.world.drawDebug):
			egi.red_pen()
			egi.line_by_pos(self.pos, self.pos + hiding * 5)

		return hiding


	def idleSteer(self, delta):

		wanderForce = self.wander(delta) * self.state['wanderInfluence']
		
		flockForce = self.flock(delta) * self.flockingInfluence

		# obstaclesForce = self.obstacleAvoidance(self.world.solids)
		
		
		
		percentFromCenterX = (self.pos.x - self.world.center.x) / self.world.width
		percentFromCenterY = (self.pos.y - self.world.center.y) / self.world.height

		
		
		# Square the falloff
		valueX = -Util.sign(percentFromCenterX)*(self.maxCenterForce * percentFromCenterX**2)
		valueY = -Util.sign(percentFromCenterY)*(self.maxCenterForce * percentFromCenterY**2)
		
		centerForce = Vector2D(valueX, valueY)
		
		
		survivalSteer = self.survivalSteer(delta)

		foodForce = self.foodSteer(delta) * (1 + self.sickness / 10)

		self.maxSpeed = self.stat('speed') - (self.sickness / 2)
		
		



		netForce = wanderForce + flockForce + centerForce + survivalSteer + foodForce

		# print 'self.flockingInfluence', self.flockingInfluence

		if(self.chosenOne and self.world.drawDebug):
			egi.blue_pen()
			egi.line_by_pos(self.pos, self.pos + wanderForce * 5)
			egi.green_pen()
			egi.line_by_pos(self.pos, self.pos + flockForce * 5)
			egi.orange_pen()
			egi.line_by_pos(self.pos, self.pos + netForce * 5)
			
			egi.set_pen_color(name='BROWN')
			egi.line_by_pos(self.pos, self.pos + centerForce * 5)

		return netForce

	
	# Return the distance from fish to food, projecting both velocities onto positions by default
	def distanceToFood(self, food, fish, projected=True):
		
		if(projected):
			# Times the velocity by the duration of the last frame
			return (fish.pos + fish.vel * self.world.lastDelta).distance(food.pos + food.vel * self.world.lastDelta)
		else:
			return (fish.pos).distance(food.pos)


	# Return the closest fish to a particular food, including us
	def closestFishToFood(self, food, fishes):
		# Use the projection values for distance
		return min(fishes, key=lambda fish: self.distanceToFood(food=food, fish=fish))


	# Returns the first fish to arrive at a partiular food, based on their speed and distance away
	def firstFishToFood(self, food, fishes):
		# Use the projection values for distance
		return min(fishes, key=lambda fish: self.timeAwayFromFood(food=food, fish=fish)['time'])


	# Return all fish that aren't us, and are closer to the food than us
	def closerFishToFood(self, food, fishes):
		
		return [{'fish': fish, 'distance': self.distanceToFood(food=food, fish=fish)} for fish in fishes if fish != self and self.distanceToFood(food=food, fish=fish) < self.distanceToFood(food=food, fish=self)]


	# Returns all fish that will get to a particular food before us
	def fasterFishToFood(self, food, fishes):
		
		return [{'fish': fish, 'time': self.timeAwayFromFood(food=food, fish=fish)['time']} 
			for fish 
			in fishes 
			if fish != self and self.timeAwayFromFood(food=food, fish=fish)['time'] < self.timeAwayFromFood(food=food, fish=self)['time']]


	


	def timeToCoverDistance(self, distance, fish):

		return distance / fish.maxSpeed


	def timeAwayFromFood(self, fish, food):

		pos = fish.projectedPosition(food)
		projectedDistance = fish.pos.distance(pos)
		return {
			'time': self.timeToCoverDistance(projectedDistance, fish),
			'foodPosition': pos,
			'distance': projectedDistance
		}






	# Heuristic value for a piece of food
	# Based on the difference between the average time taken for each fish 
	# closer than us to get there and our own time to get there
	def foodHeuristic(self, food, allFish):
		
		ownTime = self.timeAwayFromFood(food=food, fish=self)
		fasterFish = self.fasterFishToFood(food=food, fishes=allFish)
		


		# The time it would take each fish to get there
		timesOfFasterFish = [f['time'] for f in fasterFish]


		# Get the sum of each fish's time
		totalTimeValue = sum(timesOfFasterFish)
		count = len(timesOfFasterFish)
		if(count == 0): count = 1 
		avgTimeValue = totalTimeValue / count

		difference = ownTime['time'] - avgTimeValue

		return difference


	def findBestFood(self, foods):

		allFish = self.world.livingFishes

		foodsWithData = [{'food': food, 'data': self.timeAwayFromFood(fish=self, food=food)} for food in foods]

		foodsInRange = [f for f in foodsWithData if f['data']['foodPosition'].y > self.world.tank.box.bottom]

		# If all food will be out of bounds, then don't aim for any
		if(len(foodsInRange) == 0):
			return None 

		# Sort the food from closest to furthest, based on the time it'll take us to get there
		# Ideally we'd to it based on timeAwayFromFood(), but our maxSpeed is the same, 
		# so it's faster to not to the divide calulation at all and just use distance
		closestFoods = sorted(foodsInRange, key=lambda food: food['data']['time'])


		# Go through from closest foods to furthest
		# If someone else will get there first, see if I'm closer to the next one
		for food in closestFoods:
			# What's the closest fish to the food right now?
			firstFish = self.firstFishToFood(food=food['food'], fishes=allFish)

			# If we're already first, then just aim for this one
			if(firstFish == self):
				return food['food']

			# Otherwise look at the next piece of food
			pass


		# If we get to this point, then we won't be first to any of the foods!
		# Sad face. 
		# Now we should just aim for the least crowded food
		# That way there'll be less competition around us for the next food
		# Uses a heuristic defined above, based on time averages


		# Get the heuristics values for each food
		heuristics = [{'foodAndData': food, 'heuristicValue': self.foodHeuristic(food['food'], allFish)} for food in closestFoods]

		# Smaller is better here
		best = min(heuristics, key=lambda f: f['heuristicValue'])
		bestFood = best['foodAndData']['food']


		# Now just make peace with not being first :(
		return bestFood


	def foodSteer(self, delta):

		steeringForce = Vector2D()

		bestFood = self.findBestFood(self.food)


		if(bestFood is not None):
			steeringForce = self.pursuit(bestFood)
		# else:
		# 	steeringForce = self.idleSteer(delta)

		if(self.chosenOne and self.world.drawDebug):
			egi.orange_pen()
			egi.line_by_pos(self.pos, self.pos + steeringForce)

		return steeringForce



	def feedingSteer(self, delta):


		
		
		


		wanderForce = self.wander(delta) * self.state['wanderInfluence']
		

		
		
		avoidHuntersForce, hunterDist = self.avoidHuntersSteer(delta)

		avoidHuntersForce /= (1 + self.sickness / 20)

		self.maxSpeed = self.stat('speed') - (self.sickness / 2)
		
		
		foodForce = self.foodSteer(delta)


		netForce = foodForce + wanderForce + avoidHuntersForce
		

		return netForce


	def eatNearbyFood(self):

		if(self.dead): return
		
		[self.eat(f) for f in self.food if f.pos.distanceSq(self.pos) < (self.feedRadius + f.boundingRadius)**2]



	def spurtBaby(self, babyFish):
		babyFish.pos = self.pos.copy()

		angle = uniform(0, 2*pi)
		direction = Vector2D(cos(angle), sin(angle))

		max = babyFish.maxSpeed
		speed = uniform(max * 0.5, max)

		babyFish.vel = direction * speed


		return babyFish

	def eat(self, food):
		# Make sure no-one else has eaten the food before us
		if(food.eaten): return

		food.eaten = True
		self.size += 2
		self.sickness -= 40

		if(self.isParent):
			newFishes = self.world.addFish(2)
			[self.spurtBaby(f) for f in newFishes]



	'''
	Rendering logic
	=====================================
	'''

		

	def swayShape(self):

		# TODO: Optimise this somehow. 
		# At the very least cache it so that both sway functions can use it without recalculating
		sqrtSpeed = self.speedSqrt

		# Speed up fins as we slow down, illusion of swimming harder
		frequency = sqrtSpeed * 0.4
		
		# The bigger the fish, the slower it should paddle
		# frequency /= (1 + self.body * 0.25)

		# if(self.chosenOne):	print 'spedFreq', frequency
		frequency = Util.clamp(2, frequency, 3)
		# if(self.chosenOne):	print 'clampedFreq', frequency

		# print 'sqrtSpeed', self.speedSqrt(), 'freq', frequency

		swayAngle = sin(self.world._clock * frequency)
		# print 'frequency', frequency

		swayRange = sqrtSpeed / 80
		# print 'swayRange', swayRange

		matrix = Matrix33()
		matrix.scale_update(1 + (swayAngle * 0.2 * sqrt(swayRange)), 1)
		# self.matrix.rotate_update(swayAngle * swayRange)

		shape = deepcopy(self.fishShape)
		matrix.transform_vector2d_list(shape)
		
		return shape



	def swayPosition(self):

		sqrtSpeed = self.speedSqrt
		# frequency = sqrtSpeed * 0.4
		frequency = 0.1 * sqrtSpeed
		swayRange = 0.5 * self.size


		frequency = Util.clamp(0, frequency, 0.5)


		offsetAngle = cos((self.world._clock) * frequency / 2)
		offset = self.side * swayRange * offsetAngle
		position = self.pos + offset
		
		return position
		

	def drawEye(self, color=None):
		

		if(self.dead):
			egi.set_pen_color(self.color)
			egi.cross(self.renderPosition + self.side * self.body, self.body * 5)
		else:	
			egi.set_pen_color(rgba('fff', 0.5))
			egi.circle(self.renderPosition + self.side * self.body, self.body)


	def calculateRenderPosition(self):

		# No animation
		# self.renderPosition = self.pos.copy()
		# self.vehicle_shape = self.baseFishShape

		# Animation!
		self.renderPosition = self.pos # self.swayPosition()
		self.vehicle_shape = self.swayShape()


	def initShape(self):

		# Made the string using BeTravis's excellent path-to-polygon tool
		# http://betravis.github.io/shape-tools/path-to-polygon/

		simplifiedStr = '60.893 10.414, 24.234 27.027, 0.500 1.280, 0.500 71.728, 23.768 46.486, 60.893 63.900, 88.899 56.066, 100.500 37.159, 88.898 18.250, 60.893 10.414, 60.893 10.414'

		baseShape = Util.shapeFromString(simplifiedStr)

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
		# Set center point to mid-taixl
		# Util.translatePoints(baseShape, x=desiredWidth * -0.6, y=-desiredHeight/2)
		# Set center point to mid-head
		Util.translatePoints(baseShape, x=desiredWidth * -0.8, y=-desiredHeight/2)

		self.baseFishShape = baseShape



	# Get the fish shape based on a scale
	def fishShapeForScale(self, scale = 1):

		baseShape = deepcopy(self.baseFishShape)
		points = Util.scalePoints(baseShape, scale, scale)

		return points


	# Draw ourselves to the screen
	def render(self):
		
		egi.set_stroke(1)

		self.super.render()

		if(self.chosenOne and self.world.drawDebug):
			egi.grey_pen()
			egi.text_at_pos(self.pos.x, self.pos.y, str(self.sickness))
			egi.text_at_pos(self.world.width - 100, self.world.height - 30, str(self._state))
			

		

		
		
		




