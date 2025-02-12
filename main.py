import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
from config import config
from game.renderer import Renderer
from game.game_state import GameState

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

def draw_ui(display, show_panel, panel_offset, gear_texture, font):  # Add font parameter
    # Save current projection/modelview
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, display[0], display[1], 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Enable blending for proper transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Optionally, draw a black background for the button
    button_w, button_h = 50, 50
    button_x = display[0] - button_w - 10
    button_y = 10
    glColor3f(0, 0, 0)  # Black background
    glBegin(GL_QUADS)
    glVertex2f(button_x, button_y)
    glVertex2f(button_x+button_w, button_y)
    glVertex2f(button_x+button_w, button_y+button_h)
    glVertex2f(button_x, button_y+button_h)
    glEnd()

    # Draw gear texture on top (its PNG alpha will be used)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, gear_texture)
    glColor4f(1, 1, 1, 1)  # Use full brightness and the texture's alpha
    glBegin(GL_QUADS)
    # Top-left
    glTexCoord2f(0, 0)
    glVertex2f(button_x, button_y)
    # Top-right
    glTexCoord2f(1, 0)
    glVertex2f(button_x+button_w, button_y)
    # Bottom-right
    glTexCoord2f(1, 1)
    glVertex2f(button_x+button_w, button_y+button_h)
    # Bottom-left
    glTexCoord2f(0, 1)
    glVertex2f(button_x, button_y+button_h)
    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)
    
    # Draw sliding settings panel if enabled
    if show_panel:
        panel_width = 200
        panel_height = 300
        panel_x = display[0] - panel_offset
        panel_y = 70
        row_height = 30
        padding = 10

        # Draw main panel background
        glColor3f(0.2, 0.2, 0.2)  # Darker background
        glBegin(GL_QUADS)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x+panel_width, panel_y)
        glVertex2f(panel_x+panel_width, panel_y+panel_height)
        glVertex2f(panel_x, panel_y+panel_height)
        glEnd()

        # Draw first row with checkbox
        row_y = panel_y + padding
        
        # Draw row background
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(panel_x + padding, row_y)
        glVertex2f(panel_x + panel_width - padding, row_y)
        glVertex2f(panel_x + panel_width - padding, row_y + row_height - 2)
        glVertex2f(panel_x + padding, row_y + row_height - 2)
        glEnd()

        # Draw checkbox
        checkbox_size = 16
        checkbox_x = panel_x + padding + 5
        checkbox_y = row_y + (row_height - checkbox_size) / 2

        # Checkbox border
        glColor3f(0.8, 0.8, 0.8)
        glBegin(GL_LINE_LOOP)
        glVertex2f(checkbox_x, checkbox_y)
        glVertex2f(checkbox_x + checkbox_size, checkbox_y)
        glVertex2f(checkbox_x + checkbox_size, checkbox_y + checkbox_size)
        glVertex2f(checkbox_x, checkbox_y + checkbox_size)
        glEnd()

        # Fill checkbox if enabled
        if config['particles']['enabled']:
            glColor3f(0.4, 0.8, 0.4)  # Green checkmark color
            glBegin(GL_QUADS)
            glVertex2f(checkbox_x + 2, checkbox_y + 2)
            glVertex2f(checkbox_x + checkbox_size - 2, checkbox_y + 2)
            glVertex2f(checkbox_x + checkbox_size - 2, checkbox_y + checkbox_size - 2)
            glVertex2f(checkbox_x + 2, checkbox_y + checkbox_size - 2)
            glEnd()

        # Add text "Particles" next to checkbox
        text_surface = font.render("Particles", True, (200, 200, 200))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        
        glEnable(GL_TEXTURE_2D)
        text_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, text_texture)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_width, text_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        text_x = checkbox_x + checkbox_size + 10
        text_y = checkbox_y - 2
        
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        # Change texture coordinates to flip vertically
        glTexCoord2f(0, 1); glVertex2f(text_x, text_y)
        glTexCoord2f(1, 1); glVertex2f(text_x + text_width, text_y)
        glTexCoord2f(1, 0); glVertex2f(text_x + text_width, text_y + text_height)
        glTexCoord2f(0, 0); glVertex2f(text_x, text_y + text_height)
        glEnd()
        
        glBindTexture(GL_TEXTURE_2D, 0)
        glDeleteTextures([text_texture])

        # Draw remaining rows
        for i in range(1, 9):
            row_y = panel_y + (i * row_height) + padding
            if i % 2 == 0:
                glColor3f(0.3, 0.3, 0.3)
            else:
                glColor3f(0.25, 0.25, 0.25)
            glBegin(GL_QUADS)
            glVertex2f(panel_x + padding, row_y)
            glVertex2f(panel_x + panel_width - padding, row_y)
            glVertex2f(panel_x + panel_width - padding, row_y + row_height - 2)
            glVertex2f(panel_x + padding, row_y + row_height - 2)
            glEnd()

    # Disable blending if not needed later
    glDisable(GL_BLEND)
    
    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def ease_out_quad(t):
    return 1 - (1 - t) * (1 - t)

def main():
    display = initialize_gl(config)
    gear_texture, gear_w, gear_h = load_texture("textures/gear.png")
    
    # Add font initialization after pygame is initialized
    font = pygame.font.Font(None, 24)  # None uses default system font, 24 is size
    
    clock = pygame.time.Clock()
    pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, int(config['display']['vsync']))

    game_state = GameState(config)
    renderer = Renderer(config)
    angleX = angleY = 0
    
    show_settings_panel = False
    panel_offset = 0
    panel_width = 200
    panel_animation_progress = 0  # Track animation from 0 to 1
    animation_speed = 0.15  # Controls overall animation speed
    ui_slide_speed = 10
    settings_button_rect = pygame.Rect(display[0] - 50 - 10, 10, 50, 50)

    # Initialize font
    font = pygame.font.SysFont("Arial", 18)

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if settings_button_rect.collidepoint(mouse_pos):
                        show_settings_panel = not show_settings_panel
                    # Check checkbox click when panel is shown
                    elif show_settings_panel:
                        # Calculate checkbox bounds
                        checkbox_x = display[0] - panel_offset + 15
                        checkbox_y = 70 + 10 + 7  # panel_y + padding + offset
                        if (checkbox_x <= mouse_pos[0] <= checkbox_x + 16 and 
                            checkbox_y <= mouse_pos[1] <= checkbox_y + 16):
                            config['particles']['enabled'] = not config['particles']['enabled']
                            # Clear existing particles when disabled
                            if not config['particles']['enabled']:
                                game_state.particle_system.particles = []

        # Update game state
        game_state.update(current_time)

        radius = 100
        camX = radius * math.cos(angleX)
        camY = radius * math.sin(angleY) * 0.5
        camZ = radius * math.sin(angleX)
        
        renderer.setup_frame(display, (camX, camY, camZ))
        
        # Enable depth testing before 3D rendering
        glEnable(GL_DEPTH_TEST)
        
        renderer.draw_grid()
        renderer.draw_snake(game_state.get_visible_segments())
        renderer.draw_sphere(game_state.get_food_position(), 0.8, (1, 0, 0))
        
        if config['particles']['enabled']:
            game_state.particle_system.draw()
            if game_state.food_collected:
                game_state.particle_system.emit_particles(
                    position=game_state.last_food_pos, 
                    color=[1.0, 0.0, 0.0]
                )
                game_state.food_collected = False

        # Disable depth testing for UI elements
        glDisable(GL_DEPTH_TEST)
        
        # Update panel animation
        if show_settings_panel:
            panel_animation_progress = min(1, panel_animation_progress + animation_speed)
        else:
            panel_animation_progress = max(0, panel_animation_progress - animation_speed)
            
        # Apply easing function to get smooth deceleration
        eased_progress = ease_out_quad(panel_animation_progress)
        panel_offset = panel_width * eased_progress

        # Pass gear_texture and font to draw_ui
        draw_ui(display, panel_offset > 0, panel_offset, gear_texture, font)
        pygame.display.flip()
        
        if config['effects']['smooth_camera']:
            angleX += config['camera']['rotation_speed']['x']
            angleY += config['camera']['rotation_speed']['y']

        glDisable(GL_DEPTH_TEST)

if __name__ == "__main__":
    main()