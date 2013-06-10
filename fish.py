'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for HIT3046 AI for Games by Clinton Woodward cwoodward@swin.edu.au

'''

from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import sin, cos, radians
from random import random, randrange, uniform

from path import Path



class Fish(object):

    DECELERATION_SPEEDS = { 
        ### ADD 'normal' and 'fast' speeds here
        'slow': 0.9,
        'normal': 0.7,
        'fast': 0.5
    } 

    def __init__(self, world=None, scale=30.0, mass=0.5, mode='wander'):

        print 'Fish init'

        # keep a reference to the world object
        self.world = world
        self.mode = mode
        # use the world's path initially
        self.path = world.path
        # where am i and where am i going? random
        dir = radians(random()*360)
        self.pos = Vector2D(randrange(world.width),randrange(world.height))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir),cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale,scale) # easy scaling of agent size
        self.force = Vector2D() # current steering force
        self.mass = mass

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
        self.wander_dist = 1.0 * scale # adjust
        self.wander_radius = 1.2 * scale # adjusteg something bigger than the scale 
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        self.max_force = 400
        # self.max_wander_speed = 200

        # Group dynamic variables
        self.alignmentInfluence = 100
        self.separationInfluence = 100
        self.wanderInfluence = 2
        self.cohesionInfluence = 10

        self.neighbourDistance = 8 * scale
        self.isNeighbour = False # Draw yourself a different colour cause you're a neighbour of the chosen one
        self.neighbours = []


    def flock(self, delta):

        

        wanderForce = self.wander(delta)
        alignment = self.alignment()
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

        return wanderForce + alignment + separation + cohesion


    def calculate(self, delta):

        # self.force = self.flock(delta)
        self.force = self.wander(delta)

        return self.force


    def update(self, delta):

        # Grab our neighbours
        self.neighbours = self.world.getNeighbours(self, self.neighbourDistance)  

        ''' update vehicle position and orientation '''
        acceleration = self.calculate(delta)
        
        # new velocity
        self.vel += acceleration * delta
        
        # check for limits of new velocity
        max = self.max_speed
        self.vel.truncate(max)
        
        # update position
        self.pos += self.vel * delta

        # update heading is non-zero velocity (moving)
        if self.vel.lengthSq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        
        # treat world as continuous space - wrap new position if needed
        self.world.wrap_around(self.pos)



    def render(self,color=None):

        ''' Draw the triangle agent with color'''
        egi.set_pen_color(name=self.color)

        if(self.world.debug.drawDebug):
            if(self.isNeighbour): 
                egi.set_pen_color(name='BLUE')
            elif(self.chosenOne): 
                egi.set_pen_color(name='WHITE')

        pts = self.world.transform_points(self.vehicle_shape, self.pos, self.heading, self.side, self.scale)
        # draw it!
        egi.closed_shape(pts)

        if not self.world.debug.drawDebug or not self.chosenOne:
            return

            
        egi.orange_pen()
        wnd_pos = Vector2D(0, 0)
        wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side) # draw the wander circle
        egi.circle(wld_pos, self.neighbourDistance)

        # Draw wander info
        # calculate the center of the wander circle
        wnd_pos = Vector2D(self.wander_dist, 0)
        wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side) # draw the wander circle
        egi.green_pen()
        egi.circle(wld_pos, self.wander_radius)
        # draw the wander target (little circle on the big circle)
        egi.red_pen()
        wnd_pos = (self.wander_target + Vector2D(self.wander_dist,0))
        wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
        egi.circle(wld_pos, 3)

        if self.mode == 'flee':

            egi.red_pen()
            egi.circle(self.world.target, self.fleeDistance)

        # if(self.isNeighbour):
        #     self.isNeighbour = False


    def speed(self):
        return self.vel.length()

    #--------------------------------------------------------------------------

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
        target = wt + Vector2D(self.wander_dist, 0)
        
        # project the target into world space
        wld_target = self.world.transform_point(target, self.pos, self.heading, self.side) # and steer towards it

        # wld_target = wld_target.normalise() * self.maxWanderSpeed

        force = wld_target - self.pos

        # force.truncate(self.maxWanderSpeed)

        force.truncate(self.max_force) # <-- new force limiting code... return force

        self.wandering = True
        return force * self.wanderInfluence # <-- You might want to weight this...


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
            steeringForce += toNeighbour.normalise() / toNeighbour.length()

        

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





