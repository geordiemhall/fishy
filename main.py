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
from graphics import egi, KEY
from pyglet import window, clock
from pyglet.gl import *

from vector2d import Vector2D
from world import World




def on_mouse_press(x, y, button, modifiers):
    if button == 1: # left
        world.target = Vector2D(x,y)

def on_key_press(symbol, modifiers):
    if symbol == KEY.P:
        world.paused = not world.paused




    # elif symbol in AGENT_MODES:
    #     for agent in world.agents:
    #         agent.mode = AGENT_MODES[symbol]
    elif symbol == KEY.A:
        # Add an another agent when A is pressed
        world.addAgent()
        # world.syncParams()

    elif symbol == KEY.I:
        world.debug.showInfo = not world.debug.showInfo

    elif symbol == KEY.U:
        world.debug.drawDebug = not world.debug.drawDebug

    elif symbol == KEY.Y:
        world.debug.drawComponentForces = not world.debug.drawComponentForces

    elif symbol == KEY.LEFT:
        for agent in world.agents:
            agent.size -= 1
            agent.updateStats()
    elif symbol == KEY.RIGHT:
        for agent in world.agents:
            agent.size += 1
            agent.updateStats()

    else:
        world.keyPressed(symbol, modifiers)





def on_resize(width, height):
    
    world.resize(width, height)





if __name__ == '__main__':

    width = 900
    height = 700

    # create a pyglet window and set glOptions
    win = window.Window(width=width, height=height, vsync=True, resizable=True)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # needed so that egi knows where to draw
    egi.InitWithPyglet(win)
    # prep the fps display
    fps_display = clock.ClockDisplay()
    # register key and mouse event handlers
    win.push_handlers(on_key_press)
    win.push_handlers(on_mouse_press)
    win.push_handlers(on_resize)

    # create a world for agents
    world = World(width,height)
    

    # add agents
    numAgents = 3
    world.addAgent(numAgents)
    world.agents[0].chosenOne = True


    # unpause the world ready for movement
    world.paused = False

    # add a random path to the world

    while not win.has_exit:
        win.dispatch_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # show nice FPS bottom right (default)
        delta = clock.tick()
        world.update(delta)
        world.render()
        fps_display.draw()
        # swap the double buffer
        win.flip()

    world.logInfo()

