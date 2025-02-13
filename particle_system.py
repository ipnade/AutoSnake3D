import random
import math
from OpenGL.GL import *

class ParticleSystem:
    def __init__(self):
        self.particles = []
        glPointSize(5.0)

    def emit_particles(self, position, count=None, color=(1.0, 0.5, 0.0)):
        """Emit multiple particles from a position with random velocities"""
        particle_count = count if count is not None else 30
        
        for _ in range(particle_count):
            # Calculate random velocity in sphere
            angle1 = random.uniform(0, 2 * math.pi)
            angle2 = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            
            velocity = [
                speed * math.sin(angle1) * math.cos(angle2),
                speed * math.sin(angle1) * math.sin(angle2),
                speed * math.cos(angle1)
            ]
            
            # Apply color variation
            varied_color = [
                min(1.0, c + random.uniform(-0.2, 0.2))
                for c in color
            ]
            
            self.emit_particle(
                position=position, 
                velocity=velocity, 
                color=varied_color, 
                lifetime=random.uniform(0.5, 2.0)
            )

    def emit_particle(self, position, velocity, color, lifetime):
        """Create a single particle with specified properties"""
        self.particles.append({
            'position': list(position),
            'velocity': velocity,
            'color': color,
            'lifetime': lifetime,
            'max_lifetime': lifetime
        })

    def update(self, dt):
        """Update particle physics and remove dead particles"""
        for particle in self.particles:
            # Update position based on velocity
            for i in range(3):
                particle['position'][i] += particle['velocity'][i] * dt
            
            # Apply gravity
            particle['velocity'][1] -= 25.0 * dt
            particle['lifetime'] -= dt
        
        self.particles = [p for p in self.particles if p['lifetime'] > 0]

    def draw(self):
        """Render all active particles"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glBegin(GL_POINTS)
        for particle in self.particles:
            alpha = particle['lifetime'] / particle['max_lifetime']
            glColor4f(*particle['color'], alpha)
            glVertex3f(*particle['position'])
        glEnd()
        
        glDisable(GL_BLEND)

    def clear_particles(self):
        """Remove all active particles"""
        self.particles.clear()