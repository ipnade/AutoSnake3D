import random
import math
from OpenGL.GL import *

class Particle:
    def __init__(self, position, velocity, color, lifetime=2.0):
        self.position = list(position)
        self.velocity = list(velocity)
        self.color = list(color)
        self.initial_color = list(color)
        self.lifetime = lifetime
        self.age = 0
        self.gravity = -9.8
        self.drag = 0.98

    def update(self, dt):
        # Update position based on velocity
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.position[2] += self.velocity[2] * dt

        # Apply gravity to Y velocity
        self.velocity[1] += self.gravity * dt

        # Apply drag
        self.velocity = [v * self.drag for v in self.velocity]

        # Update age and color alpha
        self.age += dt
        fade = max(0, 1 - (self.age / self.lifetime))
        self.color = [c * fade for c in self.initial_color]

    def is_alive(self):
        return self.age < self.lifetime

    def draw(self):
        glPointSize(2.0)
        glBegin(GL_POINTS)
        glColor4f(*self.color, 1.0)
        glVertex3f(*self.position)
        glEnd()