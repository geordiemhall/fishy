'''A 2d world that supports agents with steering behaviour

Created for HIT3046 AI for Games by Clinton Woodward cwoodward@swin.edu.au

'''

from vector2d import Vector2D, Rect
from matrix33 import Matrix33
from graphics import egi, KEY

from fish import Fish
from util import DictWrap
from path import Path
from guppy import Guppy
from tank import Tank

class World(object):

    ''' 
    
    Inits 
    =================================='''

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center = Vector2D(width/2, height/2)

        
        
        self.scale = 10
        # self.path = Path(maxx=width, maxy=height, num_pts=5)
        

        self.makeTank()
        print 'before make fish'
        self.makeFish()
        print 'after make fish'
        self.makeDebug()

        self.makeFood()



    def makeFish(self):        
        self.agents = []

    
    def makeFood(self):
        self.food = []


    def makeTank(self):

        self.tank = Tank(world=self)
        print 'after make tank'

    


    def update(self, delta):
        if not self.paused:
            for agent in self.agents:
                agent.update(delta)


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
    
    Rendering 
    =================================='''

    def render(self):
        for agent in self.agents:
            agent.render()

        if self.debug.showInfo:
            self.drawInfo()

        self.tank.render()


    def drawInfo(self):


        lineHeight = 20
        offset = (20, 50)


        # Draw non-info text
        egi.text_color(name='WHITE')
        

        for i, inf in enumerate(self.debug.otherInfo):
            egi.text_at_pos(offset[0], offset[1] + i * lineHeight, inf)
            
        

        offset = (20, 30)
        i = 0
        for p in self.info:
            egi.text_color(name='GREY')
            egi.text_at_pos(offset[0] + 0, self.height - (offset[1] + i * lineHeight), p[0])
            egi.text_color(name='WHITE')
            egi.text_at_pos(offset[0] + 50, self.height - (offset[1] + i * lineHeight), p[1])
            egi.text_color(name='ORANGE')
            egi.text_at_pos(offset[0] + 200, self.height - (offset[1] + i * lineHeight), p[2])
            i += 1










    ''' 
    
    World logic 
    =================================='''

    def add_agent(self, num=1):
        for _ in xrange(num):
            newAgent = Guppy(world=self, scale=10)
            self.agents.append(newAgent)


    def randomize_path(self):
        self.path.create_random_path(8, self.width/6, self.height/6, self.width*2/3 + self.width/6, self.height*2/3 + self.height/6)
        for agent in self.agents:
                agent.path = self.path


    


    def getNeighbours(self, agent, distance=100):

        arr = []
        distanceSq = distance**2

        for other in self.agents:
            if(agent.chosenOne): 
                other.isNeighbour = False
            if(other != agent and other.pos.distanceSq(agent.pos) < distanceSq):
                arr.append(other)
                if(agent.chosenOne): 
                    other.isNeighbour = True

        return arr










     
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


    def transform_points(self, points, pos, forward, side, scale):
        ''' Transform the given list of points, using the provided position,
            direction and scale, to object world space. '''
        # make a copy of original points (so we don't trash them)
        wld_pts = [pt.copy() for pt in points]
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
            'drawDebug': True,
            'drawComponentForces': False,
            'otherInfo': [
                'I = Toggle info (reduces lag)',
                'U = Toggle debug drawings',
                'Y = Toggle draw component forces',
                'P = Pause',
                'A = Add agent'
            ]
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

        self.generateInfo()

    def syncParams(self):
        for param in self.params:
            self.updateAgentParam(param['name'], param['value'])




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
                self.updateAgentParam(param['name'], param['value'])
            elif(symbol == codes[1]):
                param['value'] *= (1 + param['increment'])
                self.updateAgentParam(param['name'], param['value'])
            


    # Might be easier to just make agents look this up from the world...
    def updateAgentParam(self, param, value):
        print 'Update parameter:', param, '=>', value
        self.generateInfo()
        for agent in self.agents:
            agent.__setattr__(param, value)
