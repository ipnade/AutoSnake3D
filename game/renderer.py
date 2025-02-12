from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
import numpy as np


class Renderer:
    def __init__(self, config):
        self.config = config
        self.snake_vbo = None
        self.snake_colors_vbo = None
        
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
        
    def batch_prepare_snake(self, snake_body):
        vertices = []
        colors = []
        
        for i, segment in enumerate(snake_body):
            # Make head 20% larger than body segments
            scale = 1.2 if i == 0 else 1.0
            x, y, z = segment
            cube_vertices = [
                # Front face
                [x-0.5*scale, y-0.5*scale, z+0.5*scale],
                [x+0.5*scale, y-0.5*scale, z+0.5*scale],
                [x+0.5*scale, y+0.5*scale, z+0.5*scale],
                [x-0.5*scale, y+0.5*scale, z+0.5*scale],
                # Back face
                [x-0.5*scale, y-0.5*scale, z-0.5*scale],
                [x+0.5*scale, y-0.5*scale, z-0.5*scale],
                [x+0.5*scale, y+0.5*scale, z-0.5*scale],
                [x-0.5*scale, y+0.5*scale, z-0.5*scale],
            ]
            vertices.extend(cube_vertices)
            
            # Calculate color based on position in snake
            if self.config['snake']['colors']['grayscale']:
                color = [1.0 - (i/len(snake_body))] * 3
            else:
                color = [0.0, 1.0 - (i/(2*len(snake_body))), 0.0]
            colors.extend([color] * 8)
        
        # Create VBOs if they don't exist
        if self.snake_vbo is None:
            self.snake_vbo = vbo.VBO(np.array(vertices, dtype=np.float32))
            self.snake_colors_vbo = vbo.VBO(np.array(colors, dtype=np.float32))
        else:
            # Update existing VBOs
            self.snake_vbo.set_array(np.array(vertices, dtype=np.float32))
            self.snake_colors_vbo.set_array(np.array(colors, dtype=np.float32))

    def draw_snake(self, snake_body):
        self.batch_prepare_snake(snake_body)
        
        # Enable vertex arrays
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        
        # Bind VBOs and specify data
        self.snake_vbo.bind()
        glVertexPointer(3, GL_FLOAT, 0, None)
        
        self.snake_colors_vbo.bind()
        glColorPointer(3, GL_FLOAT, 0, None)
        
        # Draw all cubes at once
        indices = []
        for i in range(len(snake_body)):
            base = i * 8
            cube_indices = [
                base, base+1, base+2, base+2, base+3, base,  # Front face
                base+5, base+4, base+7, base+7, base+6, base+5,  # Back face
                base+1, base+5, base+6, base+6, base+2, base+1,  # Right face
                base+4, base, base+3, base+3, base+7, base+4,  # Left face
                base+3, base+2, base+6, base+6, base+7, base+3,  # Top face
                base+4, base+5, base+1, base+1, base, base+4   # Bottom face
            ]
            indices.extend(cube_indices)
        
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, np.array(indices, dtype=np.uint32))
        
        # Cleanup
        self.snake_vbo.unbind()
        self.snake_colors_vbo.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

    def setup_frame(self, display, camera_pos):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, (display[0]/display[1]), 0.1, 500.0)
        camX, camY, camZ = camera_pos
        gluLookAt(camX, camY, camZ, 0, 0, 0, 0, 1, 0)