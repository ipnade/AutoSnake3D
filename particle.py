from OpenGL.GL import *

class Particle:
    """Represents a single particle with physics and rendering capabilities"""
    
    GRAVITY = -9.8
    DRAG = 0.98
    POINT_SIZE = 2.0
    
    def __init__(self, position, velocity, color, lifetime=2.0):
        """Initialize a new particle
        
        Args:
            position (tuple): Initial (x, y, z) position
            velocity (tuple): Initial (x, y, z) velocity
            color (tuple): RGB color values
            lifetime (float): Particle lifetime in seconds
        """
        self.position = list(position)
        self.velocity = list(velocity)
        self.color = list(color)
        self.initial_color = list(color)
        self.lifetime = lifetime
        self.age = 0

    def update(self, dt):
        """Update particle physics
        
        Args:
            dt (float): Time delta since last update
        """
        # Update position
        for i in range(3):
            self.position[i] += self.velocity[i] * dt
        
        # Apply physics
        self.velocity[1] += self.GRAVITY * dt
        self.velocity = [v * self.DRAG for v in self.velocity]
        
        # Update age and color
        self.age += dt
        fade = max(0, 1 - (self.age / self.lifetime))
        self.color = [c * fade for c in self.initial_color]

    def is_alive(self):
        """Check if particle is still active
        
        Returns:
            bool: True if particle is still alive
        """
        return self.age < self.lifetime

    def draw(self):
        """Render the particle using OpenGL"""
        glPointSize(self.POINT_SIZE)
        glBegin(GL_POINTS)
        glColor4f(*self.color, 1.0)
        glVertex3f(*self.position)
        glEnd()