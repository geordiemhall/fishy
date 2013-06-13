'''Autonomous Agent Movement: Seek, Arrive and Flee

Created for HIT3046 AI for Games, Lab 03
By Clinton Woodward cwoodward@swin.edu.au


TASK 1: Done
    - Random path following

TASK 2:
    - Wandering


KEYBOARD_SHORTCUTS:
    T - increase max_force
    G - increase max_force

    Y - increase max_speed
    H - increase max_speed

    N - increase jitter radius
    M - decrease jitter radius

    R - new random path

    W - wander

    F - follow_path

'''
from graphics import egi, KEY, rgba
from pyglet import window, clock
from pyglet.gl import *

from vector2d import Vector2D
from world import World


class Game(object):
    """The main game object"""
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

        

    def createWindow(self):
        # create a pyglet window and set glOptions
        
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






    def resetWorld(self):


        # create a world for agents
        self.world = World(self.width, self.height)
        

        # add agents
        numAgents = 5
        self.world.addAgent(numAgents)
        self.world.agents[0].chosenOne = True


        # unpause the world, ready for movement
        self.world.paused = False



    def renderBackground(self):
        # Draw background
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

            
            
            # swap the double buffer
            self.win.flip()

    def on_resize(self, width, height):
        self.width = width
        self.height = height
        self.world.resize(width, height)
        self.fps_display.label.y = self.height - 48


    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1: # left
            self.world.addFood(x=x)

    def on_key_press(self, symbol, modifiers):

        if symbol == KEY.P:
            self.world.paused = not self.world.paused




        # elif symbol in AGENT_MODES:
        #     for agent in self.world.agents:
        #         agent.mode = AGENT_MODES[symbol]
        elif symbol == KEY.A:
            # Add an another agent when A is pressed
            self.world.addAgent()
            # self.world.syncParams()

        elif symbol == KEY.I:
            self.world.debug.showInfo = not self.world.debug.showInfo

        elif symbol == KEY.U:
            self.world.debug.drawDebug = not self.world.debug.drawDebug

        elif symbol == KEY.Y:
            self.world.debug.drawComponentForces = not self.world.debug.drawComponentForces

        elif symbol == KEY.LEFT:
            for agent in self.world.agents:
                agent.size -= 1
                agent.updateStats()
        elif symbol == KEY.RIGHT:
            for agent in self.world.agents:
                agent.size += 1
                agent.updateStats()

        else:
            self.world.keyPressed(symbol, modifiers)











if __name__ == '__main__':

    game = Game(width=900, height=700, antialiased=True)



    

    

