import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
from config import config
from game.renderer import Renderer
from game.game_state import GameState
from game.camera import Camera
from ui_manager import UIManager

def load_texture(image_path):
    texture_surface = pygame.image.load(image_path).convert_alpha()
    texture_data = pygame.image.tostring(texture_surface, "RGBA", True)
    width, height = texture_surface.get_width(), texture_surface.get_height()
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glBindTexture(GL_TEXTURE_2D, 0)
    return texture_id, width, height

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
    gear_texture, gear_w, gear_h = load_texture("textures/gear.png")
    
    clock = pygame.time.Clock()
    pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, int(config['display']['vsync']))

    game_state = GameState(config)
    renderer = Renderer(config)
    ui_manager = UIManager(config, display)
    camera = Camera(config)

    while True:
        clock.tick(config['display']['fps'])
        current_time = pygame.time.get_ticks()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    config['snake']['colors']['grayscale'] = not config['snake']['colors']['grayscale']
                elif event.key == pygame.K_k:
                    game_state.dying = True
                elif event.key == pygame.K_t:
                    game_state.snake.grow = True
            else:
                ui_manager.handle_event(event, game_state)

        # Update game state, camera and UI
        game_state.update(current_time)
        camera.update()
        ui_manager.update()

        # Render frame
        renderer.setup_frame(display, camera.get_position())
        glEnable(GL_DEPTH_TEST)
        
        renderer.draw_grid()
        renderer.draw_snake(game_state.get_visible_segments())
        renderer.draw_sphere(game_state.get_food_position(), 0.8, (1, 0, 0))
        
        if config['particles']['enabled']:
            game_state.particle_system.draw()
            if game_state.food_collected:
                game_state.particle_system.emit_particles(
                    position=game_state.last_food_pos, 
                    color=[1.0, 0.0, 0.0],
                    count=config['particles']['count']
                )
                game_state.food_collected = False

        glDisable(GL_DEPTH_TEST)
        ui_manager.draw(gear_texture)
        pygame.display.flip()

if __name__ == "__main__":
    main()