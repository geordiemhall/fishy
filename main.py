'''Autonomous Fish Movement: Seek, Arrive and Flee

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

from world import World

def toggle(variable):
    variable = not variable

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

        


        self.showInfo = True
        self.info = {
            'I': {
                'label': 'Toggle Info (reduces lag)',
                'enabled': True
            },
            'R': {
                'label': 'Reset World'
            },
            'C' : {
                'label': 'Toggle Circle of Life (and death)',
                'enabled': True
            },
            'U': {
                'label': 'Toggle Debug drawings',
                'enabled': False
            },
            'F': {
                'label': 'Toggle Draw flocking forces',
                'enabled': False
            },
            'P': {
                'label': 'Pause',
                'enabled': False
            },
            'A': {
                'label': 'Add fish'
            },
            'LMB': {
                'label': 'Add food'
            }
        }

        






    def resetWorld(self):


        # create a world for fishes
        self.world = World(self.width, self.height)
        

        # add fishes
        numFishes = 5
        self.world.addFish(numFishes)


        # unpause the world, ready for movement
        # self.world.paused = False

        self.world.paused = self.info['P']['enabled']
        self.world.debug.drawComponentForces = self.info['F']['enabled']
        self.world.debug.drawDebug = self.info['U']['enabled']
        self.world.autoFeed = self.info['C']['enabled']
        self.world.sicknessEnabled = self.info['C']['enabled']



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

            # Draw our instructions
            self.drawInfo()

            
            
            # swap the double buffer
            self.win.flip()

    def on_resize(self, width, height):
        self.width = width
        self.height = height
        self.world.resize(width, height)
        self.fps_display.label.y = self.height - 48


    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1: # left
            self.world.addFood(x=x, y=y)


    def toggleInfo(self, key):
        self.info[key]['enabled'] = not self.info[key]['enabled']

    def on_key_press(self, symbol, modifiers):

        if symbol == KEY.P:
            self.world.paused = not self.world.paused
            self.toggleInfo('P')

        elif symbol == KEY.A:
            # Add an another agent when A is pressed
            self.world.addFish()

        elif symbol == KEY.I:
            self.showInfo = not self.showInfo
            self.toggleInfo('I')

        elif symbol == KEY.R:
            self.resetWorld()
            

        elif symbol == KEY.U:
            self.world.debug.drawDebug = not self.world.debug.drawDebug
            self.toggleInfo('U')

        elif symbol == KEY.F:
            self.world.debug.drawComponentForces = not self.world.debug.drawComponentForces
            self.toggleInfo('F')

        elif symbol == KEY.C:
            print 'print circle'
            self.world.autoFeed = not self.world.autoFeed
            self.world.sicknessEnabled = not self.world.sicknessEnabled
            self.toggleInfo('C')
            

        # elif symbol == KEY.LEFT:
        #     for agent in self.world.fishes:
        #         agent.size -= 1
        #         agent.updateStats()

        # elif symbol == KEY.RIGHT:
        #     for agent in self.world.fishes:
        #         agent.size += 1
        #         agent.updateStats()

        # else:
        #     self.world.keyPressed(symbol, modifiers)



    def drawInfo(self):
        
        if not self.showInfo: return
            

        lineHeight = 24
        offset = (33, 30)


        # Draw non-info text
        egi.text_color(name='WHITE')
        
        i = 0
        for key, value in self.info.iteritems():
            # draw the key
            egi.text_color(name='GREY')
            egi.text_at_pos(offset[0] + 0, (offset[1] + i * lineHeight), key)

            # draw the label
            egi.text_color(name='WHITE')
            if('enabled' in value and value['enabled']):
                egi.text_color(name='GREEN')
            egi.text_at_pos(offset[0] + 50, (offset[1] + i * lineHeight), value['label'])
            # egi.text_at_pos(offset[0], offset[1] + i * lineHeight, inf)

            i += 1
            
        

        # offset = (20, 30)
        # i = 0
        # for key, value in self.info.iteritems():
        #     egi.text_color(name='GREY')
        #     egi.text_at_pos(offset[0] + 0, self.height - (offset[1] + i * lineHeight), p[0])
        #     egi.text_color(name='WHITE')
        #     egi.text_at_pos(offset[0] + 50, self.height - (offset[1] + i * lineHeight), p[1])
        #     # egi.text_color(name='ORANGE')
        #     # egi.text_at_pos(offset[0] + 200, self.height - (offset[1] + i * lineHeight), p[2])
        #     i += 1






if __name__ == '__main__':

    game = Game(width=900, height=700, antialiased=True)



    

    

