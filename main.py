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
from game.ui_system import UISystem  # Replace the old UIManager import

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
    pygame.display.set_caption("Auto Snake 3D")
    icon = pygame.image.load("textures/snake.png")
    pygame.display.set_icon(icon)
    
    display = (config['display']['width'], config['display']['height'])
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    gluPerspective(45, (display[0]/display[1]), 0.1, 500.0)
    glTranslatef(0.0, 0.0, -100)
    return display

def handle_keyboard_input(event, config, game_state):
    """Handle keyboard inputs for game controls."""
    if event.key == pygame.K_g:
        config['snake']['colors']['grayscale'] = not config['snake']['colors']['grayscale']
    elif event.key == pygame.K_k:
        game_state.dying = True
    elif event.key == pygame.K_t:
        game_state.snake.grow = True
    elif event.key == pygame.K_c:
        config['camera']['auto_rotate'] = not config['camera']['auto_rotate']

def process_events(ui_system, config, game_state, mouse_state, camera):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ui_system.shutdown()
            pygame.quit()
            quit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                config['particles']['enabled'] = not config['particles']['enabled']
                if not config['particles']['enabled']:
                    game_state.particle_system.clear_particles()
            handle_keyboard_input(event, config, game_state)

        ui_system.handle_event(event)

        settings_bounds = ui_system.get_settings_bounds()
        mouse_pos = pygame.mouse.get_pos()
        mouse_in_ui = (
            settings_bounds['x'] <= mouse_pos[0] <= settings_bounds['x'] + settings_bounds['width'] and
            settings_bounds['y'] <= mouse_pos[1] <= settings_bounds['y'] + settings_bounds['height']
        )

        if not mouse_in_ui:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_state['dragging'] = True
                    mouse_state['last_pos'] = event.pos
                    mouse_state['manual_speed'] = 0
                    camera.disable_auto_spin = True  # Disable auto-spin
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_state['dragging'] = False
                    camera.disable_auto_spin = False  # Re-enable auto-spin
            elif event.type == pygame.MOUSEMOTION and mouse_state['dragging']:
                current_pos = event.pos
                last_pos = mouse_state['last_pos']
                dx = current_pos[0] - last_pos[0]
                dy = current_pos[1] - last_pos[1]
                mouse_state['manual_speed'] = (abs(dx) + abs(dy)) / 2.0
                camera.manual_rotate(dx, dy)
                mouse_state['last_pos'] = current_pos

def update_game(game_state, camera, ui_system, current_time):
    """Update game state components."""
    game_state.update(current_time)
    camera.update()
    ui_system.update()  # Add UI update

def render_scene(renderer, display, camera, game_state):
    """Render the main game scene."""
    renderer.setup_frame(display, camera.get_position())
    glEnable(GL_DEPTH_TEST)
    
    renderer.draw_grid()
    renderer.draw_snake(game_state.get_visible_segments())
    renderer.draw_sphere(game_state.get_food_position(), 0.8, (1, 0, 0))

def handle_particles(game_state):
    """Handle particle system updates."""
    if not config['particles']['enabled']:
        return
        
    game_state.particle_system.draw()
    if game_state.food_collected:
        game_state.particle_system.emit_particles(
            position=game_state.last_food_pos,
            color=[1.0, 0.0, 0.0],
            count=config['particles']['count']
        )
        game_state.food_collected = False

def main():
    display = initialize_gl(config)
    gear_texture, gear_w, gear_h = load_texture("textures/gear.png")
    
    clock = pygame.time.Clock()
    pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, int(config['display']['vsync']))

    # Initialize game components
    game_state = GameState(config)
    renderer = Renderer(config)
    ui_system = UISystem(config, display)  # Replace UIManager initialization
    camera = Camera(config)
    
    # Mouse state to track dragging and speed
    mouse_state = {
        'dragging': False,
        'last_pos': (0, 0),
        'manual_speed': 0  # Track current manual rotation speed
    }

    while True:
        clock.tick(config['display']['fps'])
        current_time = pygame.time.get_ticks()
        
        process_events(ui_system, config, game_state, mouse_state, camera)
        update_game(game_state, camera, ui_system, current_time)
        
        # If not dragging and manual rotation has slowed below a threshold,
        # let the camera resume auto-spinning.
        if not mouse_state['dragging'] and mouse_state['manual_speed'] < 0.5:
            camera.auto_spin()  # Ensure Camera has an auto_spin() method
        
        # Render frame
        render_scene(renderer, display, camera, game_state)
        handle_particles(game_state)
        
        # UI rendering
        glDisable(GL_DEPTH_TEST)
        ui_system.render()  # Replace ui_manager.draw
        pygame.display.flip()

if __name__ == "__main__":
    main()