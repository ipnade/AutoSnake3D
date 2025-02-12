import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
from config import config
from game.renderer import Renderer
from game.game_state import GameState

def initialize_gl(config):
    pygame.init()
    display = (config['display']['width'], config['display']['height'])
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    gluPerspective(45, (display[0]/display[1]), 0.1, 500.0)
    glTranslatef(0.0, 0.0, -100)
    return display

def main():
    display = initialize_gl(config)
    clock = pygame.time.Clock()
    pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, int(config['display']['vsync']))

    game_state = GameState(config)
    renderer = Renderer(config)
    angleX = angleY = 0

    while True:
        clock.tick(config['display']['fps'])
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    config['snake']['colors']['grayscale'] = not config['snake']['colors']['grayscale']
                elif event.key == pygame.K_k:
                    game_state.dying = True
                elif event.key == pygame.K_t:  # Add this section
                    game_state.snake.grow = True

        radius = 100
        camX = radius * math.cos(angleX)
        camY = radius * math.sin(angleY) * 0.5
        camZ = radius * math.sin(angleX)
        
        renderer.setup_frame(display, (camX, camY, camZ))
        
        if not game_state.update(pygame.time.get_ticks()):
            pygame.quit()
            quit()

        renderer.draw_grid()
        renderer.draw_snake(game_state.get_visible_segments())
        renderer.draw_sphere(game_state.get_food_position(), 0.8, (1, 0, 0))
        
        if config['particles']['enabled']:
            game_state.particle_system.draw()
        
        pygame.display.flip()
        
        if config['effects']['smooth_camera']:
            angleX += config['camera']['rotation_speed']['x']
            angleY += config['camera']['rotation_speed']['y']

if __name__ == "__main__":
    main()