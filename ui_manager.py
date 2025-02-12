import pygame
import config
from OpenGL.GL import *
from OpenGL.GLU import *

class UIManager:
    def __init__(self, config, display):
        self.config = config
        self.display = display
        self.show_settings_panel = False
        self.panel_width = 200
        self.panel_height = 300
        self.padding = 10
        self.row_height = 30
        self.panel_animation_progress = 0
        self.animation_speed = 0.15
        self.panel_offset = 0
        self.dragging_slider = False
        self.settings_button_rect = pygame.Rect(display[0] - 50 - 10, 10, 50, 50)
        self.font = pygame.font.SysFont("Arial", 18)

    def ease_out_quad(self, t):
        return 1 - (1 - t) * (1 - t)

    def handle_event(self, event, game_state):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                if self.settings_button_rect.collidepoint(mouse_pos):
                    self.show_settings_panel = not self.show_settings_panel
                elif self.show_settings_panel:
                    self.handle_panel_click(mouse_pos, game_state)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_slider = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_slider and self.show_settings_panel:
                self.handle_slider_drag(event.pos)

    def handle_panel_click(self, mouse_pos, game_state):
        header_x = self.display[0] - self.panel_offset + self.padding
        header_y = 70 + self.padding

        # Check category header click
        if (header_x <= mouse_pos[0] <= header_x + self.panel_width - 2*self.padding and 
            header_y <= mouse_pos[1] <= header_y + self.row_height):
            self.config['ui_particles_expanded'] = not self.config.get('ui_particles_expanded', False)
        
        # Check checkbox click if category is expanded
        elif self.config.get('ui_particles_expanded', False):
            checkbox_x = self.display[0] - self.panel_offset + self.padding + 20
            checkbox_y = header_y + self.row_height + (self.row_height - 16) / 2
            if (checkbox_x <= mouse_pos[0] <= checkbox_x + 16 and 
                checkbox_y <= mouse_pos[1] <= checkbox_y + 16):
                self.config['particles']['enabled'] = not self.config['particles']['enabled']
                if not self.config['particles']['enabled']:
                    game_state.particle_system.particles = []
            
            # Check slider click
            checkbox_row_y = header_y + self.row_height
            slider_y = checkbox_row_y + self.row_height + 25
            slider_x = self.display[0] - self.panel_offset + self.padding + 20
            slider_width = self.panel_width - 2 * self.padding - 60

            if (slider_x <= mouse_pos[0] <= slider_x + slider_width and
                slider_y - 8 <= mouse_pos[1] <= slider_y + 20):
                self.dragging_slider = True
                self.update_particle_count(mouse_pos[0], slider_x, slider_width)

    def handle_slider_drag(self, mouse_pos):
        slider_x = self.display[0] - self.panel_offset + self.padding + 20
        slider_width = self.panel_width - 2 * self.padding - 60
        self.update_particle_count(mouse_pos[0], slider_x, slider_width)

    def update_particle_count(self, mouse_x, slider_x, slider_width):
        normalized_pos = max(0, min(1, (mouse_x - slider_x) / slider_width))
        self.config['particles']['count'] = int(
            self.config['particles']['min_count'] + 
            normalized_pos * (self.config['particles']['max_count'] - self.config['particles']['min_count'])
        )

    def update(self):
        if self.show_settings_panel:
            self.panel_animation_progress = min(1, self.panel_animation_progress + self.animation_speed)
        else:
            self.panel_animation_progress = max(0, self.panel_animation_progress - self.animation_speed)
        
        eased_progress = self.ease_out_quad(self.panel_animation_progress)
        self.panel_offset = self.panel_width * eased_progress

    def draw(self, gear_texture):
        # Save current projection/modelview
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display[0], self.display[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Enable blending for proper transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Draw settings button
        button_w, button_h = 50, 50
        button_x = self.display[0] - button_w - 10
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
        if self.panel_offset > 0:
            panel_width = 200
            panel_height = 300
            panel_x = self.display[0] - self.panel_offset
            panel_y = 70
            row_height = 30
            padding = 10
            border_thickness = 2  # Add border thickness

            # Draw border
            glColor3f(0.4, 0.4, 0.4)  # Light gray border
            glBegin(GL_QUADS)
            # Left border
            glVertex2f(panel_x - border_thickness, panel_y - border_thickness)
            glVertex2f(panel_x, panel_y - border_thickness)
            glVertex2f(panel_x, panel_y + panel_height + border_thickness)
            glVertex2f(panel_x - border_thickness, panel_y + panel_height + border_thickness)
            # Top border
            glVertex2f(panel_x - border_thickness, panel_y - border_thickness)
            glVertex2f(panel_x + panel_width + border_thickness, panel_y - border_thickness)
            glVertex2f(panel_x + panel_width + border_thickness, panel_y)
            glVertex2f(panel_x - border_thickness, panel_y)
            # Right border
            glVertex2f(panel_x + panel_width, panel_y - border_thickness)
            glVertex2f(panel_x + panel_width + border_thickness, panel_y - border_thickness)
            glVertex2f(panel_x + panel_width + border_thickness, panel_y + panel_height + border_thickness)
            glVertex2f(panel_x + panel_width, panel_y + panel_height + border_thickness)
            # Bottom border
            glVertex2f(panel_x - border_thickness, panel_y + panel_height)
            glVertex2f(panel_x + panel_width + border_thickness, panel_y + panel_height)
            glVertex2f(panel_x + panel_width + border_thickness, panel_y + panel_height + border_thickness)
            glVertex2f(panel_x - border_thickness, panel_y + panel_height + border_thickness)
            glEnd()

            # Draw main panel background
            glColor3f(0.2, 0.2, 0.2)  # Darker background
            glBegin(GL_QUADS)
            glVertex2f(panel_x, panel_y)
            glVertex2f(panel_x+panel_width, panel_y)
            glVertex2f(panel_x+panel_width, panel_y+panel_height)
            glVertex2f(panel_x, panel_y+panel_height)
            glEnd()

            # Draw category header
            row_y = panel_y + padding
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_QUADS)
            glVertex2f(panel_x + padding, row_y)
            glVertex2f(panel_x + panel_width - padding, row_y)
            glVertex2f(panel_x + panel_width - padding, row_y + row_height - 2)
            glVertex2f(panel_x + padding, row_y + row_height - 2)
            glEnd()

            # Draw arrow (triangle)
            arrow_size = 8
            arrow_x = panel_x + padding + 5
            arrow_y = row_y + (row_height - arrow_size) / 2
            
            glColor3f(0.8, 0.8, 0.8)
            glBegin(GL_TRIANGLES)
            if self.config.get('ui_particles_expanded', False):
                # Down arrow
                glVertex2f(arrow_x, arrow_y)
                glVertex2f(arrow_x + arrow_size, arrow_y)
                glVertex2f(arrow_x + arrow_size/2, arrow_y + arrow_size)
            else:
                # Right arrow
                glVertex2f(arrow_x, arrow_y)
                glVertex2f(arrow_x + arrow_size, arrow_y + arrow_size/2)
                glVertex2f(arrow_x, arrow_y + arrow_size)
            glEnd()

            # Draw "Particles" category text
            text_surface = self.font.render("Particles", True, (200, 200, 200))
            text_data = pygame.image.tostring(text_surface, "RGBA", True)
            text_width = text_surface.get_width()
            text_height = text_surface.get_height()
            
            text_x = arrow_x + arrow_size + 10
            text_y = row_y + (row_height - text_height) / 2
            
            # Render text using texture
            glEnable(GL_TEXTURE_2D)
            text_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, text_texture)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_width, text_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
            
            glColor4f(1, 1, 1, 1)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(text_x, text_y)
            glTexCoord2f(1, 1); glVertex2f(text_x + text_width, text_y)
            glTexCoord2f(1, 0); glVertex2f(text_x + text_width, text_y + text_height)
            glTexCoord2f(0, 0); glVertex2f(text_x, text_y + text_height)
            glEnd()
            
            glBindTexture(GL_TEXTURE_2D, 0)
            glDeleteTextures([text_texture])

            # Draw checkbox contents if category is expanded
            if self.config.get('ui_particles_expanded', False):
                checkbox_row_y = row_y + row_height
                
                # Draw checkbox row background
                glColor3f(0.25, 0.25, 0.25)
                glBegin(GL_QUADS)
                glVertex2f(panel_x + padding + 15, checkbox_row_y)
                glVertex2f(panel_x + panel_width - padding, checkbox_row_y)
                glVertex2f(panel_x + panel_width - padding, checkbox_row_y + row_height - 2)
                glVertex2f(panel_x + padding + 15, checkbox_row_y + row_height - 2)
                glEnd()

                # Draw enable/disable checkbox
                checkbox_size = 16
                checkbox_x = panel_x + padding + 20
                checkbox_y = checkbox_row_y + (row_height - checkbox_size) / 2

                # Checkbox border and fill
                glColor3f(0.8, 0.8, 0.8)
                glBegin(GL_LINE_LOOP)
                glVertex2f(checkbox_x, checkbox_y)
                glVertex2f(checkbox_x + checkbox_size, checkbox_y)
                glVertex2f(checkbox_x + checkbox_size, checkbox_y + checkbox_size)
                glVertex2f(checkbox_x, checkbox_y + checkbox_size)
                glEnd()

                if self.config['particles']['enabled']:
                    glColor3f(0.4, 0.8, 0.4)
                    glBegin(GL_QUADS)
                    glVertex2f(checkbox_x + 2, checkbox_y + 2)
                    glVertex2f(checkbox_x + checkbox_size - 2, checkbox_y + 2)
                    glVertex2f(checkbox_x + checkbox_size - 2, checkbox_y + checkbox_size - 2)
                    glVertex2f(checkbox_x + 2, checkbox_y + checkbox_size - 2)
                    glEnd()

                # Draw "Enabled" text
                text_surface = self.font.render("Enabled", True, (200, 200, 200))
                text_data = pygame.image.tostring(text_surface, "RGBA", True)
                text_width = text_surface.get_width()
                text_height = text_surface.get_height()
                
                text_x = checkbox_x + checkbox_size + 10
                text_y = checkbox_y + (checkbox_size - text_height) / 2
                
                glEnable(GL_TEXTURE_2D)
                text_texture = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, text_texture)
                glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_width, text_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
                
                glColor4f(1, 1, 1, 1)
                glBegin(GL_QUADS)
                glTexCoord2f(0, 1); glVertex2f(text_x, text_y)
                glTexCoord2f(1, 1); glVertex2f(text_x + text_width, text_y)
                glTexCoord2f(1, 0); glVertex2f(text_x + text_width, text_y + text_height)
                glTexCoord2f(0, 0); glVertex2f(text_x, text_y + text_height)
                glEnd()
                
                glBindTexture(GL_TEXTURE_2D, 0)
                glDeleteTextures([text_texture])

                # Add slider for particle density
                slider_y = checkbox_row_y + row_height + 25  # Increased from +5 to +25 for more spacing
                slider_width = panel_width - 2 * padding - 60  # Make slider shorter
                slider_height = 4
                
                # Draw slider label
                text_surface = self.font.render("Particle Density", True, (200, 200, 200))
                text_data = pygame.image.tostring(text_surface, "RGBA", True)
                text_width = text_surface.get_width()
                text_height = text_surface.get_height()
                
                text_x = panel_x + padding + 20
                text_y = slider_y - text_height - 5
                
                glEnable(GL_TEXTURE_2D)
                text_texture = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, text_texture)
                glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_width, text_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
                
                glColor4f(1, 1, 1, 1)
                glBegin(GL_QUADS)
                glTexCoord2f(0, 1); glVertex2f(text_x, text_y)
                glTexCoord2f(1, 1); glVertex2f(text_x + text_width, text_y)
                glTexCoord2f(1, 0); glVertex2f(text_x + text_width, text_y + text_height)
                glTexCoord2f(0, 0); glVertex2f(text_x, text_y + text_height)
                glEnd()
                
                glBindTexture(GL_TEXTURE_2D, 0)
                glDeleteTextures([text_texture])

                # Draw particle count value
                value_text = str(self.config['particles']['count'])
                text_surface = self.font.render(value_text, True, (200, 200, 200))
                text_data = pygame.image.tostring(text_surface, "RGBA", True)
                text_width = text_surface.get_width()
                text_height = text_surface.get_height()
                
                # Position the number to the right of the slider
                text_x = panel_x + padding + 20 + slider_width + 10
                text_y = slider_y - text_height/2
                
                glEnable(GL_TEXTURE_2D)
                text_texture = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, text_texture)
                glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_width, text_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
                
                glColor4f(1, 1, 1, 1)
                glBegin(GL_QUADS)
                glTexCoord2f(0, 1); glVertex2f(text_x, text_y)
                glTexCoord2f(1, 1); glVertex2f(text_x + text_width, text_y)
                glTexCoord2f(1, 0); glVertex2f(text_x + text_width, text_y + text_height)
                glTexCoord2f(0, 0); glVertex2f(text_x, text_y + text_height)
                glEnd()
                
                glBindTexture(GL_TEXTURE_2D, 0)
                glDeleteTextures([text_texture])
                
                # Draw slider track
                glColor3f(0.3, 0.3, 0.3)
                glBegin(GL_QUADS)
                glVertex2f(panel_x + padding + 20, slider_y)
                glVertex2f(panel_x + padding + 20 + slider_width, slider_y)
                glVertex2f(panel_x + padding + 20 + slider_width, slider_y + slider_height)
                glVertex2f(panel_x + padding + 20, slider_y + slider_height)
                glEnd()
                
                # Draw slider handle
                handle_width = 10
                handle_height = 16
                value_range = self.config['particles']['max_count'] - self.config['particles']['min_count']
                normalized_value = (self.config['particles']['count'] - self.config['particles']['min_count']) / value_range
                handle_x = panel_x + padding + 20 + (slider_width - handle_width) * normalized_value
                
                glColor3f(0.8, 0.8, 0.8)
                glBegin(GL_QUADS)
                glVertex2f(handle_x, slider_y - handle_height/4)
                glVertex2f(handle_x + handle_width, slider_y - handle_height/4)
                glVertex2f(handle_x + handle_width, slider_y + handle_height)
                glVertex2f(handle_x, slider_y + handle_height)
                glEnd()

        # Disable blending if not needed later
        glDisable(GL_BLEND)
        
        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
