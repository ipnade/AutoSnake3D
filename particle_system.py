from particle import Particle
import random
import math
from OpenGL.GL import *

class ParticleSystem:
    def __init__(self):
        self.particles = []
        glPointSize(5.0)  # Larger point size for better visibility

    def emit_particles(self, position, count=20, color=(1.0, 0.5, 0.0)):
        for _ in range(count):
            # Random velocity in sphere
            angle1 = random.uniform(0, 2 * math.pi)
            angle2 = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            
            velocity = [
                speed * math.sin(angle1) * math.cos(angle2),
                speed * math.sin(angle1) * math.sin(angle2),
                speed * math.cos(angle1)
            ]
            
            # Random variation in color
            color_variation = 0.2
            varied_color = [
                min(1.0, c + random.uniform(-color_variation, color_variation))
                for c in color
            ]
            
            self.emit_particle(position, velocity, varied_color, random.uniform(0.5, 2.0))

    def emit_particle(self, position, velocity, color, lifetime):
        self.particles.append({
            'position': list(position),
            'velocity': velocity,
            'color': color,
            'lifetime': lifetime,
            'max_lifetime': lifetime
        })

    def update(self, dt):
        for particle in self.particles:
            # Update position
            particle['position'][0] += particle['velocity'][0] * dt
            particle['position'][1] += particle['velocity'][1] * dt
            particle['position'][2] += particle['velocity'][2] * dt
            
            # Add gravity
            particle['velocity'][1] -= 25.0 * dt  # Stronger gravity effect
            
            # Update lifetime
            particle['lifetime'] -= dt
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p['lifetime'] > 0]

    def draw(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glBegin(GL_POINTS)
        for particle in self.particles:
            alpha = particle['lifetime'] / particle['max_lifetime']
            glColor4f(
                particle['color'][0],
                particle['color'][1],
                particle['color'][2],
                alpha
            )
            glVertex3f(
                particle['position'][0],
                particle['position'][1],
                particle['position'][2]
            )
        glEnd()
        
        glDisable(GL_BLEND)