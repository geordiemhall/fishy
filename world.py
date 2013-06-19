'''A 2d world that supports agents with steering behaviour

Created for HIT3046 AI for Games by Clinton Woodward cwoodward@swin.edu.au

'''

from vector2d import Vector2D, Rect
from matrix33 import Matrix33
from graphics import *
from pyglet import clock

from fish import Fish
from util import DictWrap
from path import Path
from hunter import Hunter
from rock import Rock
from guppy import Guppy
from util import Util
from tank import Tank
from food import Food
from random import uniform


class World(object):

    ''' 
    
    Inits 
    =================================='''

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center = Vector2D(width/2, height/2)
        

        self.obstacles = []
        self._clock = 0
        
        
        self.scale = 10
        self.gravity = Vector2D(0, -900)
        

        self.makeTank()
        
        self.makeFish()

        self.makeDebug()

        self.makeFood()

        self.makeObstacles()

        self.makeHunters()



    '''

    Setup methods
    =================================='''



    def makeFish(self):        
        self.fishes = []


    
    def makeFood(self):
        self.food = []
        self.foodDistance = 30
        self.autoFeed = True
        self.autoFeedAboveInterval = 2    # seconds
        self.autoFeedBelowInterval = 1    # seconds
        self.sicknessEnabled = True
        self.sicknessInterval = 0.1

        
        clock.schedule_interval(self.autoAddFoodAbove, self.autoFeedAboveInterval)
        clock.schedule_interval(self.autoAddFoodBelow, self.autoFeedBelowInterval)
        clock.schedule_interval(self.makeFishSicker, self.sicknessInterval)


    def makeTank(self):

        self.tank = Tank(world=self)


    def makeObstacles(self):

        self.obstacles = []

        self.addRocks(10)



    def makeHunters(self):

        self.hunters = []

        self.addHunters()


    '''

    'Add' methods
    =================================='''



    def addFood(self, x, y=None, num = 1):

        # If no y was given then use the standard food distance above the tank
        if(y is None):
            y = self.height - self.foodDistance
        else:
            y = Util.clamp(self.tank.box.bottom, y, self.height)

        # Make sure the food will go in the tank
        x = Util.clamp(self.tank.box.left, x, self.tank.box.right)

        # Add the foods
        for _ in range(num):
            newFood = Food(world=self)
            newFood.pos = Vector2D(x, y)
            self.food.append(newFood)


    def obstacleOverlapsOtherObstacles(self, obstacle):
        breathingSpace = 20
        for o in self.obstacles:
            if(o.pos.distance(obstacle.pos) - obstacle.boundingRadius - o.boundingRadius < breathingSpace):
                return True
        return False


    def addRocks(self, num=10):

        for i in range(num):
            newRock = Rock(world=self)
            
            newRock.vel = Vector2D.random(newRock.maxSpeed)
            newRock.vel.y = 0

            newRock.pos = self.tank.randomPosition()
            while(self.obstacleOverlapsOtherObstacles(newRock)):
                newRock.pos = self.tank.randomPosition()

            self.obstacles.append(newRock)
           

    def autoAddFoodAbove(self, dt=0):
        self.autoAddFood(above=True)


    def autoAddFoodBelow(self, dt=0):
        self.autoAddFood(above=False)
        self.autoAddFood(above=False)


    def autoAddFood(self, above = True):

        # Make sure auto food is enabled
        if(not self.autoFeed): return

        position = self.tank.randomPosition()

        # Add the food
        if(above):
            self.addFood(x = position.x)
        else:
            self.addFood(x = position.x, y = position.y)


    def addHunters(self, num=1):
        
        # Add the foods
        for _ in range(num):
            newHunter = Hunter(world=self)
            newHunter.pos = self.tank.randomPosition()
            self.hunters.append(newHunter)




    '''

    Updating
    =================================='''

    def update(self, delta, forced=False):
        
        self.lastDelta = delta

        if not self.paused or forced:
            self._clock += delta

            # Debug fish
            if(len(self.fishes)): self.fishes[0].chosenOne = True
            if(len(self.hunters)): self.hunters[0].chosenOne = True

            # Keep list of living fish for food calculatinons
            self.livingFishes = [f for f in self.fishes if not f.dead]

            # TODO: Calculate fish times/distances from foods for everything so it isn't
            #       recalculated by every fish * food
            # self.calculateFoodData()

            # Updates
            [f.update(delta) for f in self.fishes]
            [f.update(delta) for f in self.food if not f.eaten]
            [o.update(delta) for o in self.obstacles]
            [h.update(delta) for h in self.hunters]




            # Kill dead fishes
            self.fishes = [f for f in self.fishes if not (f.dead and f.pos.y < self.tank.box.bottom - 50)]

            # Remove food that's off the screen
            self.food = [f for f in self.food if not f.eaten]


    def makeFishSicker(self, dt=0):
        # Make sure sickness is enabled
        if(not self.sicknessEnabled): return

        [f.sicker() for f in self.fishes]    


    




    ''' 
    
    Rendering 
    =================================='''

    def render(self):

        # Draw tank first
        self.tank.render()

        # Then fish
        [f.render() for f in self.fishes]

        # Food
        [f.render() for f in self.food if not f.eaten]

        # Rocks
        [o.render() for o in self.obstacles]

        # Hunters
        [h.render() for h in self.hunters]

        

        

        










    ''' 
    
    World logic 
    =================================='''


    def resize(self, width, height):
        self.width = width
        self.height = height
        self.center = Vector2D(width/2, height/2)

        self.tank.resize()


    def addFish(self, num=1):
        if(num < 1): return

        newFishes = []
        for _ in xrange(num):
            newFish = Guppy(world=self, scale=10)
            self.fishes.append(newFish)
            newFishes.append(newFish)

        # if(num == 1)
        #     return newFishes[0]

        return newFishes


    def randomizePath(self):
        self.path.create_random_path(8, self.width/6, self.height/6, self.width*2/3 + self.width/6, self.height*2/3 + self.height/6)
        for agent in self.fishes:
                agent.path = self.path


    


    def getNeighbours(self, agent, distance=100):

        distanceSq = distance**2

        return [a for a in self.fishes if a != agent and a.pos.distanceSq(agent.pos) < distanceSq]


    def getFood(self, agent, distance=10000):

        return [f for f in self.food if not f.eaten and self.tank.contains(f.pos)]


    # Enables/disables the circle of life properties
    @property
    def lionKing(self):
        return self.autoFeed # same value for both, so just pick this one

    @lionKing.setter
    def lionKing(self, value):
        self.autoFeed = value
        self.sicknessEnabled = value







     
    ''' 

    Util 
    =================================='''


    def wrap_around(self, pos):
        ''' Treat world as a toroidal space. Updates parameter object pos '''
        max_x, max_y = self.width, self.height
        if pos.x > max_x:
            pos.x = pos.x - max_x
        elif pos.x < 0:
            pos.x = max_x - pos.x
        if pos.y > max_y:
            pos.y = pos.y - max_y
        elif pos.y < 0:
            pos.y = max_y - pos.y


    def transform_points(self, points, pos, forward, side, scale=Vector2D(1, 1)):
        ''' Transform the given list of points, using the provided position,
            direction and scale, to object world space. '''
        # make a copy of original points (so we don't trash them)
        wld_pts = Util.copyPoints(points)

        # create a transformation matrix to perform the operations
        mat = Matrix33()

        # scale,
        mat.scale_update(scale.x, scale.y)

        # rotate
        mat.rotate_by_vectors_update(forward, side)

        # and translate
        mat.translate_update(pos.x, pos.y)

        # now transform all the points (vertices)
        mat.transform_vector2d_list(wld_pts)

        # done
        return wld_pts


    def transform_point(self, point, pos, forward, side):
        ''' Transform the given single point, using the provided position,
        and direction (forward and side unit vectors), to object world space. '''
        # make a copy of the original point (so we don't trash it)
        wld_pt = point.copy()

        # create a transformation matrix to perform the operations
        mat = Matrix33()

        # rotate
        mat.rotate_by_vectors_update(forward, side)

        # and translate
        mat.translate_update(pos.x, pos.y)

        # now transform the point (in place)
        mat.transform_vector2d(wld_pt)

        # done
        return wld_pt









    ''' 
    
    Debug variables
    =================================='''

    def makeDebug(self):

        self.paused = False
        self.drawDebug = False,
        self.drawComponentForces = False
        self.drawHidingSpots = False
        self.awokenHunter = True
        