import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

# Initialize Pygame and OpenGL
pygame.init()
display = (1600, 900)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

# Set up the perspective
gluPerspective(45, (display[0]/display[1]), 0.1, 150.0)
glTranslatef(0.0, 0.0, -100)  # Move back to see the grid

def draw_grid():
    glBegin(GL_LINES)
    # Draw grid of 50x50x50 but with larger steps (every 5 units)
    for i in range(-25, 26, 5):  # Changed step size to 5
        for j in range(-25, 26, 5):  # Changed step size to 5
            # Draw X-Z plane lines
            glColor3f(0.2, 0.2, 0.2)
            glVertex3f(i, -25, j)
            glVertex3f(i, 25, j)
            # Draw Y-Z plane lines
            glVertex3f(-25, i, j)
            glVertex3f(25, i, j)
            # Draw X-Y plane lines
            glVertex3f(i, j, -25)
            glVertex3f(i, j, 25)
    glEnd()

# Main game loop
angleX = 0
angleY = 0
angleZ = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Rotate camera around the center
    glLoadIdentity()
    gluPerspective(45, (display[0]/display[1]), 0.1, 150.0)
    radius = 100
    
    # Calculate camera position using smooth spherical coordinates
    camX = radius * math.cos(angleX)
    camY = radius * math.sin(angleY) * 0.5  # Multiply by 0.5 to reduce vertical movement
    camZ = radius * math.sin(angleX)
    
    gluLookAt(camX, camY, camZ,  # Camera position
              0, 0, 0,           # Look at point
              0, 1, 0)           # Up vector
    
    # Draw the grid
    draw_grid()
    
    # Update display
    pygame.display.flip()
    pygame.time.wait(10)
    
    # Increment rotation angles with very small values for smooth motion
    angleX += 0.005  # Controls horizontal rotation
    angleY += 0.003  # Controls vertical oscillation