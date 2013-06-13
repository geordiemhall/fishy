'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for HIT3046 AI for Games by Clinton Woodward cwoodward@swin.edu.au

'''

from vector2d import Vector2D, Point2D, Rect
from graphics import egi
from math import sin, cos, radians, sqrt, pi
from random import random, randrange, uniform

from transformations2d import *
from geometry import *
from util import *
# from path import Path

BIG_FLOAT = float(32000)



class Fish(object):

	DECELERATION_SPEEDS = { 
		### ADD 'normal' and 'fast' speeds here
		'slow': 0.9,
		'normal': 0.7,
		'fast': 0.5
	} 

	def __init__(self, world=None, scale=30.0, mass=1.0, mode='wander'):

		print 'Fish init'

		# keep a reference to the world object
		self.world = world
		self.mode = mode
		# use the world's path initially
		# self.path = world.path
		# where am i and where am i going? random
		dir = radians(random()*360)
		self.pos = world.tank.randomPosition()
		self.vel = Vector2D()
		self.heading = Vector2D(sin(dir),cos(dir))
		self.side = self.heading.perp()
		self.scale = Vector2D(scale,scale) # easy scaling of agent size
		self.scaleValue = scale
		self.force = Vector2D() # current steering force
		self.mass = mass
		
		self.radius = 15

		# limits?
		self.max_speed = 18.0 * scale
		self.fleeDistance = 200
		self.waypointThreshold = 50
		self.waypointThresholdSq = self.waypointThreshold**2
		self.fleeUrgency = 3
		
		

		# data for drawing this agent
		self.color = 'ORANGE'
		self.vehicle_shape = [
			Point2D(-1.0, 0.6),
			Point2D( 1.0, 0.0),
			Point2D(-1.0,-0.6)
		]
		self.chosenOne = False

		# NEW WANDER INFO
		self.wander_target = Vector2D(1,0)
		self.wanderDistance = 1.0 * scale # adjust
		self.wander_radius = 1.2 * scale # adjusteg something bigger than the scale 
		self.wander_jitter = 10.0 * scale
		self.bRadius = scale
		self.max_force = 400
		# self.max_wander_speed = 200

		# Group dynamic variables
		self.alignmentInfluence = 13
		self.separationInfluence = 500
		self.wanderInfluence = 2
		self.cohesionInfluence = 11

		self.neighbourDistance = 8 * scale
		self.isNeighbour = False # Draw yourself a different colour cause you're a neighbour of the chosen one
		self.neighbours = []


		# Collision detection
		self.minBoxLength = 15
		self.tagged = False


	


	def calculateAcceleration(self, delta):

		# self.force = self.flock(delta)
		self.force = self.wander(delta)

		return self.force / self.mass


	# Calculates velocity based on our acceleration
	def calculateVelocity(self, delta):
		# new velocity
		vel = self.vel + self.acceleration * delta
		
		# check for limits of new velocity
		max = self.max_speed
		vel.truncate(max)

		return vel


	def update(self, delta):

		

		# Grab our neighbours
		self.neighbours = self.world.getNeighbours(self, self.neighbourDistance)  

		''' update vehicle position and orientation '''
		self.acceleration = self.calculateAcceleration(delta)

		self.vel = self.calculateVelocity(delta)
		
		
		# update position
		self.pos += self.vel * delta

		# update heading is non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()
		
		# treat world as continuous space - wrap new position if needed
		self.world.wrap_around(self.pos)


	def pointsInWorldSpace(self, points, position):

		return self.world.transform_points(points, position, self.heading, self.side, self.scale)


	def drawBody(self, color=None):
		egi.set_pen_color(name=self.color)

		if(self.world.debug.drawDebug):
			if(self.isNeighbour): 
				egi.blue_pen()
			if(self.tagged):
				egi.green_pen()
			if(self.chosenOne): 
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
		
		

		''' Draw the triangle agent with color'''
		self.drawBody(color)
		
		if(not self.world.debug.drawDebug):
			return
		
		# Debug stuff to draw for all agents
		egi.circle(self.pos, self.boundingRadius)

		if not self.chosenOne:
			return
		# Debug stuff to only draw for one agent


		egi.grey_pen()
		egi.circle(self.pos, self.boundingRadius)

		egi.orange_pen()
		wnd_pos = Vector2D(0, 0)
		wld_pos = self.world.transform_point(wnd_pos, self.renderPosition, self.heading, self.side) # draw the wander circle
		egi.circle(wld_pos, self.neighbourDistance)

		# Draw wander info
		# calculate the center of the wander circle
		wnd_pos = Vector2D(self.wanderDistance, 0)
		wld_pos = self.world.transform_point(wnd_pos, self.renderPosition, self.heading, self.side) # draw the wander circle
		egi.green_pen()
		egi.circle(wld_pos, self.wander_radius)
		# draw the wander target (little circle on the big circle)
		egi.red_pen()
		wnd_pos = (self.wander_target + Vector2D(self.wanderDistance,0))
		wld_pos = self.world.transform_point(wnd_pos, self.renderPosition, self.heading, self.side)
		egi.circle(wld_pos, 3)



		# if(self.isNeighbour):
		#     self.isNeighbour = False


	def speed(self):
		return self.vel.length()

	def speedSqrt(self):
		return sqrt(self.speed())




	#--------------------------------------------------------------------------

	#--------------------------------------------------------------------------







	''' 
	Standard forces
	======================== '''

	def seek(self, target_pos):
		''' move towards target position '''
		desired_vel = (target_pos - self.pos).normalise() * self.max_speed
		return (desired_vel - self.vel)


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
			speed = min(speed, self.max_speed)
			# from here proceed just like Seek except we don't need to
			# normalize the to_target vector because we have already gone to the
			# trouble of calculating its length for dist.
			desired_vel =  (to_target * speed / dist)
			return (desired_vel - self.vel)
		return Vector2D(0,0)


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
		wt *= self.wander_radius

		# move the target into a position WanderDist in front of the agent
		target = wt + Vector2D(self.wanderDistance, 0)
		
		# project the target into world space
		wld_target = self.world.transform_point(target, self.pos, self.heading, self.side) # and steer towards it

		# wld_target = wld_target.normalise() * self.maxWanderSpeed

		force = wld_target - self.pos

		# force.truncate(self.maxWanderSpeed)

		force.truncate(self.max_force) # <-- new force limiting code... return force

		self.wandering = True
		return force * self.wanderInfluence # <-- You might want to weight this...


	'''
	Flocking forces
	========================'''


	def flock(self, delta):

		
		alignment = self.alignment()
		separation = self.separationForce()
		cohesion = self.cohesionForce()

		if(self.chosenOne and self.world.debug.drawComponentForces):
			s = 0.1
			egi.green_pen()
			egi.line_with_arrow(self.pos, self.pos + alignment * s, 10)
			egi.blue_pen()
			egi.line_with_arrow(self.pos, self.pos + separation * s, 10)
			egi.red_pen()
			egi.line_with_arrow(self.pos, self.pos + cohesion * s, 10)
			egi.grey_pen()
			egi.line_with_arrow(self.pos, self.pos + self.force * s, 10)

		return alignment + separation + cohesion


	def alignment(self):

		steeringForce = Vector2D() 
	
		if(len(self.neighbours) == 0):
			return steeringForce

		headings = map(lambda agent: agent.heading, self.neighbours)
		total = reduce(lambda x, y: x + y, headings)
		avg = total / len(self.neighbours)

		steeringForce = self.seek(avg)

		return steeringForce * self.alignmentInfluence



	def separationForce(self):

		steeringForce = Vector2D() 

		if(len(self.neighbours) == 0):
			return steeringForce

		

		for agent in self.neighbours:           
			toNeighbour = agent.pos.distanceTo(self.pos)
			# scale based on inverse distance to neighbour 
			steeringForce += toNeighbour.normalise() / (toNeighbour.length() + 0.1)

		

		# steeringForce = self.seek(-steeringForce)

		return steeringForce * self.separationInfluence


	def cohesionForce(self):

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

			if(self.chosenOne): 
				obj.tagged = True
				egi.circle(obj.localPos, radius)


		return tagged


	def obstacleAvoidance(self, objects):
		# calc a "Detection Box" length proportional to current speed
		boxLength = self.minBoxLength + (self.speed() / self.max_speed) * self.minBoxLength
		boxWidth = self.boundingRadius * 2

		# Draw the collision box
		if(self.chosenOne and self.world.debug.drawDebug):
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
		feelerAngle = pi/4
		feelerShorter = 0.6

		# Main center feeler
		center = self.pos + self.heading.copy() * feelerLength
		# Slightly shorter angled feelers
		left = self.pos + self.heading.copy().rotate(feelerAngle) * feelerLength * feelerShorter
		right = self.pos + self.heading.copy().rotate(-feelerAngle) * feelerLength * feelerShorter

		feelers = [center, left, right]

		if(self.world.debug.drawDebug):
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


	



