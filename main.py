import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from config import config
from game.renderer import Renderer
from game.game_state import GameState
from game.camera import Camera
from game.ui_system import UISystem

def initialize_gl(config):
    pygame.init()
    pygame.display.set_caption("AutoSnake3D")
    icon = pygame.image.load("textures/snake.png")
    pygame.display.set_icon(icon)
    
    # Cache display dimensions to avoid dict lookups
    width = config['display']['width']
    height = config['display']['height'] 
    display = (width, height)
    
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    gluPerspective(45, (display[0]/display[1]), 0.1, 500.0)
    glTranslatef(0.0, 0.0, -100)
    
    if config['display'].get('vsync', True):
        pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 1)
    
    return display

def handle_keyboard_input(event, config, game_state):
    """Handle keyboard inputs for game controls."""
    # Cache config paths as constants at module level
    SNAKE_COLORS = config['snake']['colors']
    CAMERA_CONFIG = config['camera']
    
    if event.key == pygame.K_g:
        SNAKE_COLORS['grayscale'] = not SNAKE_COLORS['grayscale']
    elif event.key == pygame.K_k:
        game_state.dying = True
    elif event.key == pygame.K_t:
        game_state.snake.grow = True 
    elif event.key == pygame.K_c:
        CAMERA_CONFIG['auto_rotate'] = not CAMERA_CONFIG['auto_rotate']

def process_events(ui_system, config, game_state, mouse_state, camera):
    bounds = ui_system.get_settings_bounds()
    mouse_pos = pygame.mouse.get_pos()
    
    # More efficient bounds check
    mouse_in_ui = all([
        bounds['x'] <= mouse_pos[0] <= bounds['x'] + bounds['width'],
        bounds['y'] <= mouse_pos[1] <= bounds['y'] + bounds['height']
    ])

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

        if not mouse_in_ui:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_state['dragging'] = True
                    mouse_state['last_pos'] = event.pos
                    mouse_state['manual_speed'] = 0
                    camera.disable_auto_spin = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_state['dragging'] = False
                    camera.disable_auto_spin = False
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
    ui_system.update()

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
    display = initialize_gl(config)
    clock = pygame.time.Clock()
    pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, int(config['display']['vsync']))

    # Initialize game components
    game_state = GameState(config)
    renderer = Renderer(config)
    ui_system = UISystem(config, display)
    camera = Camera(config)
    
    # Mouse state to track dragging and speed
    mouse_state = {
        'dragging': False,
        'last_pos': (0, 0),
        'manual_speed': 0
    }

    try:
        while True:
            current_time = pygame.time.get_ticks()
            
            # Bundle related updates
            process_events(ui_system, config, game_state, mouse_state, camera)
            update_game(game_state, camera, ui_system, current_time)
            
            # Only check auto_spin when needed
            if not any([mouse_state['dragging'], mouse_state['manual_speed'] >= 0.5]):
                camera.auto_spin()
            
            # Batch render calls
            render_scene(renderer, display, camera, game_state)
            handle_particles(game_state)
            
            # Minimize state changes
            glDisable(GL_DEPTH_TEST)
            ui_system.render()
            pygame.display.flip()
            
            clock.tick(config['display']['fps'])
    finally:
        ui_system.shutdown()
        pygame.quit()

if __name__ == "__main__":
    main()