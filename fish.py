'''

Base class for swimming agents.
Has some basic steering behaviours which are combined
in sub-classes to create behaviour

'''


# Vendor imports
from vector2d import Vector2D, Rect
from graphics import egi, COLOR_NAMES
from math import sin, cos, radians, sqrt, pi
from random import uniform
from transformations2d import *
from geometry import *

# Constants
BIG_FLOAT = float(32000)




class Fish(object):

	DECELERATION_SPEEDS = { 
		### ADD 'normal' and 'fast' speeds here
		'slow': 0.9,
		'normal': 0.7,
		'fast': 0.5
	} 

	def __init__(self, world=None, scale=30.0, mass=1.0):

		# Keep a reference to the world object
		self.world = world

		# Randomize our initial direction
		dir = radians(uniform(0, 360))

		# Basic properties
		self.pos = world.tank.randomPosition()
		self.vel = Vector2D()
		self.heading = Vector2D(sin(dir),cos(dir))
		self.side = self.heading.perp()
		self.scale = Vector2D(scale,scale) # easy scaling of agent size
		self.scaleValue = scale
		self.mass = mass

		# Bounding circle
		self.boundingRadius = 15

		# Limits
		self.maxSpeed = 18.0 * scale
		self.fleeDistance = 200
		self.waypointThreshold = 50
		self.waypointThresholdSq = self.waypointThreshold**2
		self.fleeUrgency = 3

		self.feelerPercentage = 1.0
		
		

		# Drawing
		self.color = COLOR_NAMES['ORANGE']
		self.vehicle_shape = [ Vector2D(-1.0, 0.6),	Vector2D( 1.0, 0.0), Vector2D(-1.0,-0.6) ]  # generic shape
		self.chosenOne = False

		# Wander
		self.wander_target = Vector2D(1,0)
		self.wanderDistance = 1.0 * scale # adjust
		self.wanderRadius = 1.2 * scale # adjusteg something bigger than the scale 
		self.wander_jitter = 10.0 * scale
		self.bRadius = scale
		self.maxForce = 400

		# Flocking
		self.alignmentInfluence = 150
		self.separationInfluence = 20000
		self.wanderInfluence = 2
		self.cohesionInfluence = 2

		self.neighbourDistance = 8 * scale
		self.isNeighbour = False # Draw yourself a different colour cause you're a neighbour of the chosen one
		self.neighbours = []

		# Collision detection
		self.minBoxLength = 15
		self.tagged = False

		# Life
		self._dead = False


	

	# Separate function for calculating acceleration
	def calculateAcceleration(self, delta):

		self.force = self.wander(delta)

		return self.force / self.mass


	# Calculates velocity based on our acceleration
	def calculateVelocity(self, delta):
		# new velocity
		vel = self.vel + self.acceleration * delta
		
		# check for limits of new velocity
		max = self.maxSpeed
		vel.truncate(max)

		return vel


	'''
	Hooks for subclasses
	===============================
	'''

	
	# Called after data loaded, but before position and state are calculated
	def performActions(self):
		pass

	# Called after position has been calculated
	def collisionDetection(self):
		pass

	# Called at the beginning of update
	def beforeUpdate(self):
		egi.set_stroke(1) # we want our debug info to be 1px


	def update(self, delta):

		self.beforeUpdate()

		# Grab our neighbours for flocking
		self.neighbours = self.world.getNeighbours(self, self.neighbourDistance) 
		
		self.performActions()



		# Update vehicle position and orientation
		self.acceleration = self.calculateAcceleration(delta)

		self.vel = self.calculateVelocity(delta)
		
		
		# update position
		self.pos += self.vel * delta

		self.collisionDetection()

		# update heading is non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()
		
		# treat world as continuous space - wrap new position if needed
		if(not self._dead): self.world.wrap_around(self.pos)


	def pointsInWorldSpace(self, points, position):

		return self.world.transform_points(points, position, self.heading, self.side, self.scale)


	def drawBody(self, color=None):
		egi.set_pen_color(color)

		if(self.world.drawDebug):
			if(self.isNeighbour): 
				egi.blue_pen()
			if(self.tagged):
				egi.green_pen()
		if(self.chosenOne): 
			if(self.world.drawDebug or self.world.drawComponentForces):
				egi.white_pen()

		pts = self.pointsInWorldSpace(self.vehicle_shape, self.renderPosition)
		# pts = self.world.transform_points(self.vehicle_shape, self.renderPosition, self.heading, self.side, self.scale)
		# draw it!
		egi.closed_shape(pts)

		self.drawEye(color)


	def beforeRender(self):
		
		pass


	def drawEye(self, color=None):

		pass


	def calculateRenderPosition(self):
		self.renderPosition = self.pos


	def render(self,color=None):

		self.calculateRenderPosition()
		
		if(color is None):
			color = self.color

		''' Draw the triangle agent with color'''
		self.drawBody(color)

		
		if(not self.world.drawDebug or not self.chosenOne):
			return
		
		# Debug stuff to draw for all agents
		

		# if not self.chosenOne:
		# 	return
		# Debug stuff to only draw for one agent

		egi.circle(self.pos, self.boundingRadius)

		egi.orange_pen()
		egi.circle(self.pos, self.boundingRadius)

		egi.grey_pen()
		wnd_pos = Vector2D(0, 0)
		
		

		# Draw wander info
		# calculate the center of the wander circle
		wnd_pos = Vector2D(self.wanderDistance, 0)
		wld_pos = self.world.transform_point(wnd_pos, self.renderPosition, self.heading, self.side) # draw the wander circle
		egi.green_pen()
		egi.circle(wld_pos, self.wanderRadius)
		# draw the wander target (little circle on the big circle)
		egi.red_pen()
		wnd_pos = (self.wander_target + Vector2D(self.wanderDistance,0))
		wld_pos = self.world.transform_point(wnd_pos, self.renderPosition, self.heading, self.side)
		egi.circle(wld_pos, 3)



		# if(self.isNeighbour):
		#     self.isNeighbour = False


	def speed(self):
		return self.vel.length()

	




	#--------------------------------------------------------------------------

	#--------------------------------------------------------------------------







	''' 
	Standard forces
	======================== '''

	def seek(self, target_pos):
		''' move towards target position '''
		desired_vel = (target_pos - self.pos).normalise() * self.maxSpeed
		return (desired_vel - self.vel)



	def steer_to(self, target):
		desired = target - self.pos # A vector pointing from the location to the target
		d = desired.length()  # Distance from the target is the magnitude of the vector

		# If the distance is greater than 0, calc steering (otherwise return zero vector)
		if d > 0:
			desired.normalise()

			# Two options for desired vector magnitude (1 -- based on distance, 2 -- maxspeed)
			if d < 100.0:
				desired *= (self.maxSpeed * ( d / 100.0 ) ) # This damping is somewhat arbitrary
			else:
				desired *= (self.maxSpeed)

			# Steering = Desired minus Velocity
			steer = desired - self.vel
			steer.truncate(self.maxForce)  # Limit to maximum steering force
		else:
			steer = Vector2D()

		return steer


	def arrive(self, target_pos, speed):
		''' this behaviour is similar to seek() but it attempts to arrive at
			the target position with a zero velocity'''
		decel_rate = self.DECELERATION_SPEEDS[speed]
		to_target = target_pos - self.pos
		dist = to_target.length()
		if dist > 0:
			# calculate the speed required to reach the target given the
			# desired deceleration rate
			speed =  dist / decel_rate # * 0.5
			# make sure the velocity does not exceed the max
			speed = min(speed, self.maxSpeed)
			# from here proceed just like Seek except we don't need to
			# normalize the to_target vector because we have already gone to the
			# trouble of calculating its length for dist.
			desired_vel =  (to_target * speed / dist)
			return (desired_vel - self.vel)
		return Vector2D(0,0)


	def projectedPosition(self, target):
		
		toEvader = target.pos - self.pos

		lookAheadTime = toEvader.length() / (self.maxSpeed + target.speed())

		lookAheadPos = target.pos + target.vel * lookAheadTime 

		return lookAheadPos


	def pursuit(self, target): 

		

		projected = self.projectedPosition(target)

		if(self.world.drawDebug and self.chosenOne):
			egi.red_pen()
			egi.cross(projected, 10)

		return self.seek(projected)
		
		# assumes that target is a Vehicle
		# toEvader = target.pos - self.pos
		# # relativeHeading = self.heading.dot(target.heading)
		
		# # simple out: if target is ahead and facing us, head straight to it
		# # if (toEvader.dot(self.heading)>0) and (relativeHeading < 0.95): 
		# # 	# acos(0.95)=18 degrees
		# # 	return self.seek(target.pos)
		
		# # time proportional to distance, inversely proportional to sum of velocities
		# lookAheadTime = toEvader.length() / (self.maxSpeed + target.speed())
		
		# # self.turnRate = 0.1
		# # # turn rate delay? dot product = 1 if ahead, -1 if behind.
		# # lookAheadTime += (1 - self.heading.dot(target.heading))*- self.turnRate
		
		# # Seek the predicted location (using look-ahead time)
		# lookAheadPos = target.pos + target.vel * lookAheadTime 

		
			

		# return self.seek(lookAheadPos)


	def wander(self, delta):
		''' random wandering using a projected jitter circle '''
		wt = self.wander_target
		
		# this behaviour is dependent on the update rate, so this line must
		# be included when using time independent framerate.
		jitter_tts = self.wander_jitter * delta # this time slice
		
		# first, add a small random vector to the target's position
		wt += Vector2D(uniform(-1,1) * jitter_tts, uniform(-1,1) * jitter_tts)

		# re-project this new vector back on to a unit circle
		wt.normalise()

		# increase the length of the vector to the same as the radius
		# of the wander circle
		wt *= self.wanderRadius

		# move the target into a position WanderDist in front of the agent
		target = wt + Vector2D(self.wanderDistance, 0)
		
		# project the target into world space
		wld_target = self.world.transform_point(target, self.pos, self.heading, self.side) # and steer towards it

		# wld_target = wld_target.normalise() * self.maxWanderSpeed

		force = wld_target - self.pos

		# force.truncate(self.maxWanderSpeed)

		force.truncate(self.maxForce) # <-- new force limiting code... return force

		self.wandering = True
		return force * self.wanderInfluence # <-- You might want to weight this...


	'''
	Flocking forces
	========================'''


	def flock(self, delta):

		
		alignment = self.alignmentForce()
		separation = self.separationForce()
		cohesion = self.cohesionForce()

		if(self.chosenOne and self.world.drawComponentForces):
			s = 0.1
			egi.green_pen()
			egi.line_with_arrow(self.pos, self.pos + alignment * s, 10)
			egi.blue_pen()
			egi.line_with_arrow(self.pos, self.pos + separation * s, 10)
			egi.red_pen()
			egi.line_with_arrow(self.pos, self.pos + cohesion * s, 10)
			egi.grey_pen()
			egi.line_with_arrow(self.pos, self.pos + self.force * s, 10)
			egi.circle(self.pos, self.neighbourDistance)

		return alignment + separation + cohesion


	def alignmentForce(self):

		steer = Vector2D()
				
		velocities = [agent.vel for agent in self.neighbours if self.pos.distanceSq(agent.pos) > 0.01]
		count = len(velocities)

		if(count > 0):
			avg = sum(velocities, steer) / float(count)
			steer = avg * self.alignmentInfluence
			return steer.truncate(self.maxForce)

		return steer



	def separationForce(self):

		avg = Vector2D()
		count = 0

		# Radius within which to steer away
		DESIRED_SEPARATION = 60
		if(self.world.drawDebug and self.chosenOne):
			egi.circle(self.pos, DESIRED_SEPARATION)

		for agent in self.neighbours:
			d = self.pos.distance(agent.pos)
			if d > 0 and d < DESIRED_SEPARATION:
				# Normalized, weighted by distance vector pointing away from the neighbour

				direction = (self.pos - agent.pos).normalise()
				# print 'direction', direction
				amount = direction / d
				
				avg += amount
				count += 1


		if(count > 0):
			avg /= float(count)

		

		avg *= 20000

		avg.truncate(self.maxForce)
		

		return avg




		steeringForce = Vector2D() 

		if(len(self.neighbours) == 0):
			return steeringForce

		

		for agent in self.neighbours:	      
			# toNeighbour = agent.pos.distanceTo(self.pos)
			toNeighbour = self.pos - agent.pos
			# scale based on inverse distance to neighbour 
			steeringForce += toNeighbour.normalise() / (toNeighbour.length() + 0.01) # prevent divide by zero

		

		# steeringForce = self.seek(-steeringForce)

		

		return steeringForce * self.separationInfluence


	def cohesionForce(self):

		steer = Vector2D()
		
		positions = [agent.pos for agent in self.neighbours if self.pos.distance(agent.pos) > 0.1]
		count = len(positions)

		if(count > 0):
			avg = sum(positions, steer) / float(count)
			return self.seek(avg) * self.cohesionInfluence

		return steer





		steeringForce = Vector2D()

		if(len(self.neighbours) == 0):
			return steeringForce

		# centre = Vector2D() 
		# count = len(self.neighbours)

		# for agent in self.neighbours:
		#     centre += agent.pos 

		#     if count > 0:
		#         centre /= float(count) 
		#         steeringForce = self.seek(centre)

		positions = map(lambda agent: agent.pos, self.neighbours)
		total = reduce(lambda x, y: x + y, positions)
		avg = total / len(self.neighbours)

		steeringForce = self.seek(avg)
		
		return steeringForce * self.cohesionInfluence



	'''
	Collision forces
	========================'''

	def tagObjectsInViewRange(self, objects, boxLength, boxWidth):

		tagged = []

		# Check each object in the list
		for obj in objects:

			if(self.chosenOne): obj.tagged = False

			# Don't check outselves
			if(obj == self):
				continue

			localPos = VectorToLocalSpace(obj.pos, self.heading, self.side)
			radius = obj.boundingRadius + boxWidth * 0.5

			
			
			# If it's behind us, or its x is further away than the box
			if(localPos.x < 0 or localPos.x - radius > boxLength):
				continue
			
			# So we're within the box's x range
			# Time to check the y

			# If its highest point is below the box, or its lowest point is above the box
			if(localPos.y - radius < -boxWidth / 2 or localPos.y + radius < boxWidth/2):
				continue

			# We must have intersected the box, so tag ourselves
			tagged.append(obj)

			if(self.chosenOne and self.world.drawDebug): 
				obj.tagged = True
				egi.circle(obj.localPos, radius)


		return tagged


	def obstacleAvoidance(self, objects):
		# calc a "Detection Box" length proportional to current speed
		boxLength = self.minBoxLength + (self.speed() / self.maxSpeed) * self.minBoxLength
		boxWidth = self.boundingRadius * 2

		# Draw the collision box
		if(self.chosenOne and self.world.drawDebug):
			box = Rect({
				'left': 0, 
				'right': boxLength, 
				'top': boxWidth/2, 
				'bottom': -boxWidth/2
			})
			boxPoints = box.getPoints()
			print 'render points...', Util.strPoints(boxPoints)

			pts = self.pointsInWorldSpace(boxPoints, self.pos)
			print 'render points...', Util.strPoints(pts)
			egi.red_pen()
			egi.closed_shape(pts)
			simple = [
				Vector2D(0, 10),
				Vector2D(10, 10),
				Vector2D(10, -10),
				Vector2D(0, -10)]
			egi.closed_shape(self.pointsInWorldSpace(simple, self.pos))
		
		# note (tag) the objects in range
		tagList = self.tagObjectsInViewRange(objects, boxLength, boxWidth)
		closestDistance = BIG_FLOAT # float('inf') 
		closestObj = None
		closestPos = None

		# Loop through the TagList and find the intersection points ... 
		# keep track of the closest object found ...
		# Calculate the steering force (if required) ...

		for obj in tagList:
			localPos = PointToLocalSpace(obj.pos, self.heading, self.side, self.pos) 
			if localPos.x >= 0:
				ExpandedRadius = obj.boundingRadius + self.boundingRadius 
				if abs(localPos.y) < ExpandedRadius:
					# line/circle intersection test, x = cX +/- sqrt(r**2 - cY**2) for y=0
					cX = localPos.x
					cY = localPos.y
					# only calc the sqrt part once (avoid repetition) 
					sqrtPart = math.sqrt(ExpandedRadius**2 - cY**2) 
					ip = cX - sqrtPart
					if ip <= 0.0: 
						ip = cX + sqrtPart
						# Keep track of the closest found so far
						if ip < closestDistance:
							closestDistance = ip 
							closestObj = obj 
							closestPos = obj.pos

		# now find the steering force
		steeringForce = Vector2D() 
		if closestObj:
			# the closer, the stronger the force needed
			multi = 1.0 + (boxLength - closestPos.x) / boxLength

			# lateral force as needed
			steeringForce.y = (closestObj.boundingRadius - closestPos.y) * multi

			# breaking force proportional to closest object
			breakingWeight = 0.2
			steeringForce.x = (closestObj.boundingRadius - closestPos.x) * breakingWeight
		
		# convert force back to world space
		return VectorToWorldSpace(steeringForce,self.heading, self.side)


	def createFeelers(self):

		feelerLength = sqrt(self.boundingRadius) * 20 + 30
		feelerLength *= self.feelerPercentage
		feelerAngle = pi/4
		feelerShorter = 0.6

		# Main center feeler
		center = self.pos + self.heading.copy() * feelerLength
		# Slightly shorter angled feelers
		left = self.pos + self.heading.copy().rotate(feelerAngle) * feelerLength * feelerShorter
		right = self.pos + self.heading.copy().rotate(-feelerAngle) * feelerLength * feelerShorter

		feelers = [center, left, right]

		if(self.chosenOne and self.world.drawDebug):
			egi.aqua_pen()
			egi.line_by_pos(self.pos, center)
			egi.line_by_pos(self.pos, left)
			egi.line_by_pos(self.pos, right)

		return feelers


	def wallAvoidance(self, walls):

		
		
		# create the feelers; centre, left and right 
		feelers = self.createFeelers() 

		distanceToClosest = BIG_FLOAT 
		
		steeringForce = Vector2D() 
		closestPoint = Vector2D()

		# for each feeler, test against all walls
		for feeler in feelers: 
			closestWall = None

			for wall in walls:
				# do an intersection test and store the result (object)
				result = LineIntersection2DDistPoint(self.pos, feeler, wall.start, wall.end) 

				if result.intersects:

					# only keep the closest intersection point (IP)
					if result.distance < distanceToClosest: 
						distanceToClosest = result.distance 
						closestWall = wall
						closestPoint = result.point
		
			# new closest intersection point?
			if closestWall:
				# calculate the penetration depth for this feeler 
				overshoot = (feeler - closestPoint).length()

				# create force in direction of the wall normal 
				norm = closestWall.normal
				
				steeringForce += norm * overshoot 


		return steeringForce



	def hide(self, hunters, obstacles, closest=True):

		hidingPlaces = []

		for hunter in hunters:
			for obstacle in obstacles:
				dir = hunter.pos.distanceTo(obstacle.pos).get_normalised()
				length = hunter.pos.distance(obstacle.pos) + obstacle.boundingRadius + self.boundingRadius
				
				# Calculate the position of the hiding spot
				place = hunter.pos + dir * length

				# If this spot isn't inside any other obstacles, then add it to the list
				if(not True in [ob.containsPoint(place) for ob in obstacles]):
					hidingPlaces.append(place)

		self.hidingPlaces = hidingPlaces # store for debugging purposes

		# Find the 'best' hiding place from our list
		self.bestPlace = self.bestHidingPlaceFromHunter(hidingPlaces=hidingPlaces, hunter=hunters[0], closest=closest)

		# print 'bestPlace', self.bestPlace

		# seek = self.seek(self.bestPlace)
		arrive = self.arrive(self.bestPlace, 'fast')

		if(self.chosenOne and self.world.drawHidingSpots):
			for place in self.hidingPlaces or []:
				egi.red_pen()
				if(place == self.bestPlace): egi.green_pen()
				egi.cross(place, 10)

		return arrive



	def bestHidingPlaceFromHunter(self, hidingPlaces, hunter, closest=True):

		

		closestPlaces = sorted(hidingPlaces, key=lambda p: p.distanceSq(self.pos))

		if(closest):
			return closestPlaces[0]
		
		# Get the closest places that are out of range of the hunter
		safePlaces = [place for place in closestPlaces if not hunter.canSeePosition(place)]

		if(self.chosenOne and self.world.drawHidingSpots):
			egi.blue_pen()
			[egi.circle(p, 10) for p in safePlaces]

		# If there actually are some safe places then choose the closest (they'll still be in order)
		if(len(safePlaces)):
			return safePlaces[0]

		# If all hiding places are close to the hunter, then just pick the furthest
		return max(hidingPlaces, key=lambda p: p.distanceSq(hunter.pos))




	



