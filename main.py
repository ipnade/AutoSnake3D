import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import (
    glEnable, glDepthFunc, glTranslatef, GL_DEPTH_TEST, 
    GL_LESS, glDisable
)
from OpenGL.GLU import gluPerspective
from config import config
from game.renderer import Renderer
from game.game_state import GameState
from game.camera import Camera
from game.ui_system import UISystem
import os
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def initialize_gl(config):
    """Initialize OpenGL and Pygame display settings"""
    pygame.init()
    pygame.display.set_caption("AutoSnake3D")
    
    # Use resource path resolver
    icon_path = get_resource_path("textures/snake.png")
    pygame.display.set_icon(pygame.image.load(icon_path))
    
    width = config['display']['width']
    height = config['display']['height'] 
    display = (width, height)
    
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    
    # OpenGL settings
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    gluPerspective(45, (width/height), 0.1, 500.0)
    glTranslatef(0.0, 0.0, -100)
    
    if config['display'].get('vsync', True):
        pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 1)
    
    return display

def handle_keyboard_input(event, config, game_state):
    """Process keyboard controls"""
    key_actions = {
        pygame.K_k: lambda: setattr(game_state, 'dying', True),
        pygame.K_t: lambda: setattr(game_state.snake, 'grow', True),
        pygame.K_c: lambda: toggle_camera_rotation(config),
        pygame.K_p: lambda: toggle_particles(config, game_state)
    }
    
    if event.key in key_actions:
        key_actions[event.key]()

def toggle_camera_rotation(config):
    """Toggle camera auto-rotation"""
    config['camera']['auto_rotate'] = not config['camera']['auto_rotate']

def toggle_particles(config, game_state):
    """Toggle particle system and clear existing particles"""
    config['particles']['enabled'] = not config['particles']['enabled']
    if not config['particles']['enabled']:
        game_state.particle_system.clear_particles()

def handle_mouse_input(event, mouse_state, camera, mouse_in_ui):
    """Process mouse input for camera control"""
    if mouse_in_ui:
        return
        
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_state.update({
            'dragging': True,
            'last_pos': event.pos,
            'manual_speed': 0
        })
        camera.disable_auto_spin = True
        
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        mouse_state['dragging'] = False
        camera.disable_auto_spin = False
        
    elif event.type == pygame.MOUSEMOTION and mouse_state['dragging']:
        current_pos = event.pos
        last_pos = mouse_state['last_pos']
        dx = current_pos[0] - last_pos[0]
        dy = current_pos[1] - last_pos[1]
        
        mouse_state.update({
            'manual_speed': (abs(dx) + abs(dy)) / 2.0,
            'last_pos': current_pos
        })
        camera.manual_rotate(dx, dy)

def process_events(ui_system, config, game_state, mouse_state, camera):
    """Process all game events"""
    bounds = ui_system.get_settings_bounds()
    mouse_pos = pygame.mouse.get_pos()
    
    mouse_in_ui = (bounds['x'] <= mouse_pos[0] <= bounds['x'] + bounds['width'] and
                  bounds['y'] <= mouse_pos[1] <= bounds['y'] + bounds['height'])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
            
        if event.type == pygame.KEYDOWN:
            handle_keyboard_input(event, config, game_state)
            
        ui_system.handle_event(event)
        handle_mouse_input(event, mouse_state, camera, mouse_in_ui)
    
    return True

def game_loop(display, game_state, renderer, ui_system, camera, mouse_state, clock):
    """Main game loop"""
    while True:
        current_time = pygame.time.get_ticks()
        
        if not process_events(ui_system, config, game_state, mouse_state, camera):
            break
            
        # Update game state
        game_state.update(current_time)
        camera.update()
        ui_system.update(game_state)
        
        # Update camera auto-spin
        if not mouse_state['dragging'] and mouse_state['manual_speed'] < 0.5:
            camera.auto_spin()
        
        # Render frame
        render_scene(renderer, display, camera, game_state)
        handle_particles(game_state)
        
        glDisable(GL_DEPTH_TEST)
        ui_system.render()
        pygame.display.flip()
        
        clock.tick(config['display']['fps'])

def update_game(game_state, camera, ui_system, current_time):
    """Update game state components."""
    game_state.update(current_time)
    camera.update()
    ui_system.update(game_state)

def render_scene(renderer, display, camera, game_state):
    """Render the main game scene."""
    renderer.setup_frame(display, camera.get_position())
    glEnable(GL_DEPTH_TEST)
    
    renderer.draw_grid()
    renderer.draw_snake(game_state.get_visible_segments())
    renderer.draw_sphere(game_state.get_food_position(), 0.8, (1, 0, 0))

def handle_particles(game_state):
    """Handle particle system updates."""
    # Early return if particles disabled
    if not config['particles']['enabled']:
        return
        
    particle_system = game_state.particle_system
    particle_system.draw()
    
    # Only process food collection once
    if game_state.food_collected:
        particle_system.emit_particles(
            position=game_state.last_food_pos,
            color=[1.0, 0.0, 0.0],
            count=config['particles']['count']
        )
        game_state.food_collected = False

def main():
    """Initialize and run the game"""
    display = initialize_gl(config)
    clock = pygame.time.Clock()
    
    # Initialize components
    game_state = GameState(config)
    renderer = Renderer(config)
    ui_system = UISystem(config, display)
    camera = Camera(config)
    
    mouse_state = {
        'dragging': False,
        'last_pos': (0, 0),
        'manual_speed': 0
    }

    try:
        game_loop(display, game_state, renderer, ui_system, camera, mouse_state, clock)
    finally:
        ui_system.shutdown()
        pygame.quit()

if __name__ == "__main__":
    main()