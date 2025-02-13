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
        """Draw the game boundary grid"""
        grid_size = 25
        grid_color = self.config['grid']['color']
        
        glBegin(GL_LINES)
        glColor3f(*grid_color)
        
        # Draw grid outline
        vertices = [
            # Front face
            (-grid_size, -grid_size, grid_size), (grid_size, -grid_size, grid_size),
            (grid_size, -grid_size, grid_size), (grid_size, grid_size, grid_size),
            (grid_size, grid_size, grid_size), (-grid_size, grid_size, grid_size),
            (-grid_size, grid_size, grid_size), (-grid_size, -grid_size, grid_size),
            
            # Back face
            (-grid_size, -grid_size, -grid_size), (grid_size, -grid_size, -grid_size),
            (grid_size, -grid_size, -grid_size), (grid_size, grid_size, -grid_size),
            (grid_size, grid_size, -grid_size), (-grid_size, grid_size, -grid_size),
            (-grid_size, grid_size, -grid_size), (-grid_size, -grid_size, -grid_size),
            
            # Connecting lines
            (-grid_size, -grid_size, -grid_size), (-grid_size, -grid_size, grid_size),
            (grid_size, -grid_size, -grid_size), (grid_size, -grid_size, grid_size),
            (grid_size, grid_size, -grid_size), (grid_size, grid_size, grid_size),
            (-grid_size, grid_size, -grid_size), (-grid_size, grid_size, grid_size)
        ]
        
        for vertex in vertices:
            glVertex3f(*vertex)
        
        glEnd()
        
    def draw_cube(self, position, size=1, color=(1, 1, 1)):
        """Draw a single cube with specified position, size and color"""
        x, y, z = position
        vertices = [
            # Front face
            [(x-size, y-size, z+size), (x+size, y-size, z+size),
             (x+size, y+size, z+size), (x-size, y+size, z+size)],
            # Back face
            [(x-size, y-size, z-size), (x-size, y+size, z-size),
             (x+size, y+size, z-size), (x+size, y-size, z-size)],
            # Top face
            [(x-size, y+size, z-size), (x-size, y+size, z+size),
             (x+size, y+size, z+size), (x+size, y+size, z-size)],
            # Bottom face
            [(x-size, y-size, z-size), (x+size, y-size, z-size),
             (x+size, y-size, z+size), (x-size, y-size, z+size)],
            # Right face
            [(x+size, y-size, z-size), (x+size, y+size, z-size),
             (x+size, y+size, z+size), (x+size, y-size, z+size)],
            # Left face
            [(x-size, y-size, z-size), (x-size, y-size, z+size),
             (x-size, y+size, z+size), (x-size, y+size, z-size)]
        ]
        
        glColor3f(*color)
        glBegin(GL_QUADS)
        for face in vertices:
            for vertex in face:
                glVertex3f(*vertex)
        glEnd()
        
    def draw_sphere(self, position, radius=1.0, color=(1, 1, 1)):
        """Draw a sphere with specified position, radius and color"""
        x, y, z = position
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(*color)
        
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluSphere(quadric, radius, 32, 32)
        
        glPopMatrix()
        
    def calculate_snake_color(self, segment_index, total_segments):
        """Calculate snake segment color based on configuration"""
        if self.config['snake']['colors']['gamer_mode']:
            # Use time to cycle through hue values with configurable speed
            import time
            cycle_speed = self.config['snake']['colors']['gamer_speed']
            hue = (time.time() * cycle_speed) % 1.0
            # Convert HSV to RGB (simplified version)
            h = hue * 6.0
            c = 1.0
            x = c * (1 - abs(h % 2 - 1))
            
            if h < 1: rgb = (c, x, 0)
            elif h < 2: rgb = (x, c, 0)
            elif h < 3: rgb = (0, c, x)
            elif h < 4: rgb = (0, x, c)
            elif h < 5: rgb = (x, 0, c)
            else: rgb = (c, 0, x)
            
            intensity = self.config['snake']['colors']['gradient_intensity']
            fade = 1.0 - (segment_index/total_segments) * intensity
            return [max(0.0, min(1.0, c * fade)) for c in rgb]
        
        # Original color logic
        if self.config['snake']['colors']['custom_color']:
            r, g, b = self.config['snake']['colors']['primary_color']
            intensity = self.config['snake']['colors']['gradient_intensity']
            fade = 1.0 - (segment_index/total_segments) * intensity
            return [max(0.0, min(1.0, c * fade)) for c in (r, g, b)]
        
        if segment_index == 0:
            return self.config['snake']['colors']['default_colors']['head']
            
        pattern = self.config['snake']['colors']['default_colors']['body_pattern']
        return pattern[segment_index % len(pattern)]

    def batch_prepare_snake(self, snake_body):
        """Prepare snake VBOs for batch rendering"""
        vertices = []
        colors = []
        
        for i, segment in enumerate(snake_body):
            scale = 1.2 if i == 0 else 1.0
            x, y, z = segment
            
            # Generate cube vertices
            cube_vertices = [
                [x + dx*scale, y + dy*scale, z + dz*scale]
                for dx, dy, dz in [
                    (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5),
                    (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
                    (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5),
                    (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)
                ]
            ]
            vertices.extend(cube_vertices)
            
            color = self.calculate_snake_color(i, len(snake_body))
            colors.extend([color] * 8)
        
        # Create or update VBOs
        if self.snake_vbo is None:
            self.snake_vbo = vbo.VBO(np.array(vertices, dtype=np.float32))
            self.snake_colors_vbo = vbo.VBO(np.array(colors, dtype=np.float32))
        else:
            self.snake_vbo.set_array(np.array(vertices, dtype=np.float32))
            self.snake_colors_vbo.set_array(np.array(colors, dtype=np.float32))

    def draw_snake(self, snake_body):
        """Render the snake using VBOs"""
        self.batch_prepare_snake(snake_body)
        
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        
        self.snake_vbo.bind()
        glVertexPointer(3, GL_FLOAT, 0, None)
        
        self.snake_colors_vbo.bind()
        glColorPointer(3, GL_FLOAT, 0, None)
        
        # Generate indices for all cubes
        indices = []
        for i in range(len(snake_body)):
            base = i * 8
            cube_indices = [
                # Front face
                base, base+1, base+2, base+2, base+3, base,
                # Back face
                base+5, base+4, base+7, base+7, base+6, base+5,
                # Right face
                base+1, base+5, base+6, base+6, base+2, base+1,
                # Left face
                base+4, base, base+3, base+3, base+7, base+4,
                # Top face
                base+3, base+2, base+6, base+6, base+7, base+3,
                # Bottom face
                base+4, base+5, base+1, base+1, base, base+4
            ]
            indices.extend(cube_indices)
        
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, 
                      np.array(indices, dtype=np.uint32))
        
        self.snake_vbo.unbind()
        self.snake_colors_vbo.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

    def setup_frame(self, display, camera_pos):
        """Setup the frame for rendering"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, (display[0]/display[1]), 0.1, 500.0)
        gluLookAt(*camera_pos, 0, 0, 0, 0, 1, 0)