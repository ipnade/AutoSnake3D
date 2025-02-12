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

def draw_ui(display, show_panel, panel_offset, gear_texture):
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
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x+panel_width, panel_y)
        glVertex2f(panel_x+panel_width, panel_y+panel_height)
        glVertex2f(panel_x, panel_y+panel_height)
        glEnd()

    # Disable blending if not needed later
    glDisable(GL_BLEND)
    
    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def main():
    display = initialize_gl(config)  # Initialize pygame and set display mode
    # Now that the display is initialized, load the texture
    gear_texture, gear_w, gear_h = load_texture("textures/gear.png")
    
    clock = pygame.time.Clock()
    pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, int(config['display']['vsync']))

    game_state = GameState(config)
    renderer = Renderer(config)
    angleX = angleY = 0
    
    show_settings_panel = False
    panel_offset = 0
    panel_width = 200
    ui_slide_speed = 10
    settings_button_rect = pygame.Rect(display[0] - 50 - 10, 10, 50, 50)

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
                elif event.key == pygame.K_t:
                    game_state.snake.grow = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if settings_button_rect.collidepoint(mouse_pos):
                        show_settings_panel = not show_settings_panel

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

        if show_settings_panel and panel_offset < panel_width:
            panel_offset = min(panel_offset + ui_slide_speed, panel_width)
        elif not show_settings_panel and panel_offset > 0:
            panel_offset = max(panel_offset - ui_slide_speed, 0)

        # Pass gear_texture to draw_ui
        draw_ui(display, panel_offset > 0, panel_offset, gear_texture)
        pygame.display.flip()
        
        if config['effects']['smooth_camera']:
            angleX += config['camera']['rotation_speed']['x']
            angleY += config['camera']['rotation_speed']['y']

        glDisable(GL_DEPTH_TEST)

if __name__ == "__main__":
    main()