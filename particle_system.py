from particle import Particle
import random
import math
from OpenGL.GL import *

class ParticleSystem:
    def __init__(self):
        self.particles = []

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
            
            self.particles.append(
                Particle(
                    position=position,
                    velocity=velocity,
                    color=varied_color,
                    lifetime=random.uniform(0.5, 2.0)
                )
            )

    def update(self, dt):
        # Update all particles and remove dead ones
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update(dt)

    def draw(self):
        # Enable blending for transparent particles
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for particle in self.particles:
            particle.draw()
        
        glDisable(GL_BLEND)