from OpenGL.GL import *
from OpenGL.GLU import *


class Renderer:
    def __init__(self, config):
        self.config = config
        
    def draw_grid(self):
        glBegin(GL_LINES)
        glColor3f(0.2, 0.2, 0.2)
        
        # Front face outline
        glVertex3f(-25, -25, 25)
        glVertex3f(25, -25, 25)
        glVertex3f(25, -25, 25)
        glVertex3f(25, 25, 25)
        glVertex3f(25, 25, 25)
        glVertex3f(-25, 25, 25)
        glVertex3f(-25, 25, 25)
        glVertex3f(-25, -25, 25)
        
        # Back face outline
        glVertex3f(-25, -25, -25)
        glVertex3f(25, -25, -25)
        glVertex3f(25, -25, -25)
        glVertex3f(25, 25, -25)
        glVertex3f(25, 25, -25)
        glVertex3f(-25, 25, -25)
        glVertex3f(-25, 25, -25)
        glVertex3f(-25, -25, -25)
        
        # Connecting lines
        glVertex3f(-25, -25, -25)
        glVertex3f(-25, -25, 25)
        glVertex3f(25, -25, -25)
        glVertex3f(25, -25, 25)
        glVertex3f(25, 25, -25)
        glVertex3f(25, 25, 25)
        glVertex3f(-25, 25, -25)
        glVertex3f(-25, 25, 25)
        
        glEnd()
        
    def draw_cube(self, position, size=1, color=(1, 1, 1)):
        x, y, z = position
        glColor3f(*color)
        glBegin(GL_QUADS)
        # Front
        glVertex3f(x-size, y-size, z+size)
        glVertex3f(x+size, y-size, z+size)
        glVertex3f(x+size, y+size, z+size)
        glVertex3f(x-size, y+size, z+size)
        # Back
        glVertex3f(x-size, y-size, z-size)
        glVertex3f(x-size, y+size, z-size)
        glVertex3f(x+size, y+size, z-size)
        glVertex3f(x+size, y-size, z-size)
        # Top
        glVertex3f(x-size, y+size, z-size)
        glVertex3f(x-size, y+size, z+size)
        glVertex3f(x+size, y+size, z+size)
        glVertex3f(x+size, y+size, z-size)
        # Bottom
        glVertex3f(x-size, y-size, z-size)
        glVertex3f(x+size, y-size, z-size)
        glVertex3f(x+size, y-size, z+size)
        glVertex3f(x-size, y-size, z+size)
        # Right
        glVertex3f(x+size, y-size, z-size)
        glVertex3f(x+size, y+size, z-size)
        glVertex3f(x+size, y+size, z+size)
        glVertex3f(x+size, y-size, z+size)
        # Left
        glVertex3f(x-size, y-size, z-size)
        glVertex3f(x-size, y-size, z+size)
        glVertex3f(x-size, y+size, z+size)
        glVertex3f(x-size, y+size, z-size)
        glEnd()
        
    def draw_sphere(self, position, radius=1.0, color=(1, 1, 1)):
        x, y, z = position
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(*color)
        
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluSphere(quadric, radius, 32, 32)
        
        glPopMatrix()
        
    def draw_snake(self, snake_body):
        for i, segment in enumerate(snake_body):
            t = i / len(snake_body)
            
            x, y, z = segment
            offset = self.config['snake']['z_fighting_offset'] * i
            adjusted_pos = (x + offset, y + offset, z + offset)
            
            if self.config['snake']['colors']['grayscale']:
                if i == 0:
                    color = self.config['snake']['colors']['grayscale_palette']['head']
                    size = self.config['snake']['size']['head']
                else:
                    size = self.config['snake']['size']['body']
                    brightness = 1.0 - (t * 0.7)
                    color = (brightness, brightness, brightness)
            else:
                if i == 0:
                    color = self.config['snake']['colors']['head']
                    size = self.config['snake']['size']['head']
                else:
                    size = self.config['snake']['size']['body']
                    pattern = i % len(self.config['snake']['colors']['body_pattern'])
                    base_color = self.config['snake']['colors']['body_pattern'][pattern]
                    
                    if self.config['effects']['gradient_fade']:
                        color = tuple(c * (1 - t * 0.3) for c in base_color)
                    else:
                        color = base_color
            
            self.draw_cube(adjusted_pos, size, color)

    def setup_frame(self, display, camera_pos):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, (display[0]/display[1]), 0.1, 500.0)
        camX, camY, camZ = camera_pos
        gluLookAt(camX, camY, camZ, 0, 0, 0, 0, 1, 0)