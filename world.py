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
        # self.path = Path(maxx=width, maxy=height, num_pts=5)
        

        self.makeTank()
        print 'before make fish'
        self.makeFish()
        print 'after make fish'
        self.makeDebug()

        self.makeFood()



        



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
        print 'after make tank'

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


    
           


    def generateInfo(self):
        arr = []

        for param in self.params:
            label = param['name'] + ':'
            keys = str(param['keys']).replace('\'', '')
            val =  str(param['value'])

            arr.append((keys, label, val))

        self.info = arr

    def logInfo(self):
        print "\n\nFinal parameter values:\n"
        for p in self.info:
            print p[1], p[2]




    def resize(self, width, height):
        self.width = width
        self.height = height
        self.center = Vector2D(width/2, height/2)

        self.tank.resize()




    '''

    Updating
    =================================='''

    def update(self, delta):
        self.lastDelta = delta

        if not self.paused:
            self._clock += delta

            self.fishes[0].chosenOne = True

            self.livingFishes = [f for f in self.fishes if not f.dead]
            [f.update(delta) for f in self.fishes]
            [f.update(delta) for f in self.food if not f.eaten]

            # Kill dead fishes
            self.fishes = [f for f in self.fishes if not (f.dead and f.pos.y < self.tank.box.bottom + 5)]

            # Remove food that's off the screen
            self.food = [f for f in self.food if not f.eaten]


            
    def makeFishSicker(self, dt=0):
        # Make sure sickness is enabled
        if(not self.sicknessEnabled): return

        [f.sicker() for f in self.fishes]
        # clock.schedule_once(self.makeFishSicker, self.sicknessInterval)


    def autoAddFoodAbove(self, dt=0):
        self.autoAddFood(above=True)
        # clock.schedule_once(self.autoAddFoodAbove, self.autoFeedAboveInterval)

    def autoAddFoodBelow(self, dt=0):
        self.autoAddFood(above=False)
        self.autoAddFood(above=False)
        # clock.schedule_once(self.autoAddFoodBelow, self.autoFeedBelowInterval)


    def autoAddFood(self, above = True):

        # Make sure auto food is enabled
        if(not self.autoFeed): return

        position = self.tank.randomPosition()

        # Add the food
        if(above):
            self.addFood(x = position.x)
        else:
            self.addFood(x = position.x, y = position.y)


        







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

        

        










    ''' 
    
    World logic 
    =================================='''

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
    
    Debug code 
    =================================='''

    def makeDebug(self):
        
        

        self.paused = True

        self.debug = DictWrap({
            'showInfo': False,
            'drawDebug': False,
            'drawComponentForces': False
        })

        self.params = [
            # {
            #     'name': 'wanderDistance',
            #     'keys': ('N', 'M'),
            #     'value': 2.4 * self.scale,
            #     'increment': 0.1
            # },
            {
                'name': 'wander_radius',
                'keys': ('V', 'B'),
                'value': 0.8 * self.scale,
                'increment': 0.1
            },
            {
                'name': 'wander_jitter',
                'keys': ('X', 'C'),
                'value': 8.5 * self.scale,
                'increment': 0.1
            },
            # {
            #     'name': 'wanderInfluence',
            #     'keys': ('F', 'G'),
            #     'value': 13.0,
            #     'increment': 0.1
            # },
            # {
            #     'name': 'neighbourDistance',
            #     'keys': ('W', 'E'),
            #     'value': 13.0 * self.scale,
            #     'increment': 0.1
            # },
            {
                'name': 'alignmentInfluence',
                'keys': ('K', 'L'),
                'value': 5,
                'increment': 0.1
            },
            {
                'name': 'separationInfluence',
                'keys': ('H', 'J'),
                'value': 400.0,
                'increment': 0.1
            },
            {
                'name': 'cohesionInfluence',
                'keys': ('S', 'D'),
                'value': 3.4,
                'increment': 0.1
            }
        ]

        self.params = []

        self.generateInfo()

    def syncParams(self):
        for param in self.params:
            self.updateFishParam(param['name'], param['value'])




    def keyPressed(self, symbol, modifiers):
        # Checks if any parameters' keys were pressed
        
        for param in self.params:
            keys = param['keys']
            codes = (getattr(KEY, keys[0]), getattr(KEY, keys[1]))
            

            # If we were pressed, then change the value
            # Only update the parameter that was changed
            # Might need to optimise this further

            if(symbol == codes[0]):
                param['value'] *= (1 - param['increment'])
                self.updateFishParam(param['name'], param['value'])
            elif(symbol == codes[1]):
                param['value'] *= (1 + param['increment'])
                self.updateFishParam(param['name'], param['value'])
            


    # Might be easier to just make agents look this up from the world...
    def updateFishParam(self, param, value):
        print 'Update parameter:', param, '=>', value
        self.generateInfo()
        for agent in self.fishes:
            agent.__setattr__(param, value)
