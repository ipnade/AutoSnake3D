import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random
from snake import Snake

# Initialize Pygame and OpenGL
pygame.init()
display = (1600, 900)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

# Enable depth testing
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LESS)

# Set up the perspective
gluPerspective(45, (display[0]/display[1]), 0.1, 150.0)
glTranslatef(0.0, 0.0, -100)  # Move back to see the grid

# Add near the top with other initializations
clock = pygame.time.Clock()
pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 1)  # Enable VSync

def draw_grid():
    glBegin(GL_LINES)
    # Draw the cube outline only
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

def get_next_move(snake, food):
    head = snake.body[0]
    current_direction = snake.direction
    
    # Calculate direction to food
    food_direction = (
        food[0] - head[0],
        food[1] - head[1],
        food[2] - head[2]
    )
    
    # Try continuing in current direction first
    new_pos = (
        head[0] + current_direction[0],
        head[1] + current_direction[1],
        head[2] + current_direction[2]
    )
    
    # If current direction moves closer to food and is valid, keep going
    if (abs(new_pos[0]) <= 24 and abs(new_pos[1]) <= 24 and 
        abs(new_pos[2]) <= 24 and new_pos not in snake.body):
        current_distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(new_pos, food)))
        head_distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(head, food)))
        if current_distance < head_distance:
            return current_direction
    
    # Find the primary axis to move along
    abs_food_dir = [abs(x) for x in food_direction]
    primary_axis = abs_food_dir.index(max(abs_food_dir))
    
    # Create prioritized moves list
    possible_moves = []
    
    # Add move in primary axis direction first
    if food_direction[primary_axis] > 0:
        possible_moves.append(tuple(1 if i == primary_axis else 0 for i in range(3)))
    else:
        possible_moves.append(tuple(-1 if i == primary_axis else 0 for i in range(3)))
    
    # Add other possible moves as fallbacks
    for axis in range(3):
        if axis != primary_axis:
            for direction in [1, -1]:
                move = tuple(direction if i == axis else 0 for i in range(3))
                if move not in possible_moves:
                    possible_moves.append(move)
    
    # Remove 180-degree turns
    opposite_move = tuple(-x for x in current_direction)
    if opposite_move in possible_moves:
        possible_moves.remove(opposite_move)
    
    # Try moves in order of priority
    for move in possible_moves:
        new_pos = tuple(head[i] + move[i] for i in range(3))
        
        if (abs(new_pos[0]) <= 24 and abs(new_pos[1]) <= 24 and 
            abs(new_pos[2]) <= 24 and new_pos not in snake.body):
            return move
    
    return current_direction

def spawn_food(snake_body):
    while True:
        x = random.randint(-24, 24)
        y = random.randint(-24, 24)
        z = random.randint(-24, 24)
        if (x, y, z) not in snake_body:
            return (x, y, z)

def draw_cube(position, size=1, color=(1, 1, 1)):
    x, y, z = position
    glColor3f(*color)
    glBegin(GL_QUADS)
    # Front face
    glVertex3f(x-size, y-size, z+size)
    glVertex3f(x+size, y-size, z+size)
    glVertex3f(x+size, y+size, z+size)
    glVertex3f(x-size, y+size, z+size)
    # Back face
    glVertex3f(x-size, y-size, z-size)
    glVertex3f(x-size, y+size, z-size)
    glVertex3f(x+size, y+size, z-size)
    glVertex3f(x+size, y-size, z-size)
    # Top face
    glVertex3f(x-size, y+size, z-size)
    glVertex3f(x-size, y+size, z+size)
    glVertex3f(x+size, y+size, z+size)
    glVertex3f(x+size, y+size, z-size)
    # Bottom face
    glVertex3f(x-size, y-size, z-size)
    glVertex3f(x+size, y-size, z-size)
    glVertex3f(x+size, y-size, z+size)
    glVertex3f(x-size, y-size, z+size)
    # Right face
    glVertex3f(x+size, y-size, z-size)
    glVertex3f(x+size, y+size, z-size)
    glVertex3f(x+size, y+size, z+size)
    glVertex3f(x+size, y-size, z+size)
    # Left face
    glVertex3f(x-size, y-size, z-size)
    glVertex3f(x-size, y-size, z+size)
    glVertex3f(x-size, y+size, z+size)
    glVertex3f(x-size, y+size, z-size)
    glEnd()

# Initialize game objects
snake = Snake()
food = spawn_food(snake.body)
game_speed = 50  # Milliseconds between moves
last_move_time = 0  # Track the last time the snake moved

# Main game loop
angleX = 0
angleY = 0
angleZ = 0
while True:
    # Lock the framerate to monitor refresh rate
    clock.tick(60)  # 60 FPS or your monitor's refresh rate
    
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
    
    # Get current time
    current_time = pygame.time.get_ticks()
    
    # Move snake based on elapsed time
    if current_time - last_move_time >= game_speed:
        # Get AI move
        next_move = get_next_move(snake, food)
        snake.move(next_move)
        
        # Check if food eaten
        if snake.body[0] == food:
            snake.grow = True
            food = spawn_food(snake.body)
        
        # Check for game over
        if snake.check_collision():
            pygame.quit()
            quit()
            
        last_move_time = current_time

    # Draw the grid
    draw_grid()
    
    # Draw snake
    for segment in snake.body:
        draw_cube(segment, 1.0, (1, 1, 1))  # Changed size from 0.5 to 1.0
    # Draw food
    draw_cube(food, 1.0, (1, 0, 0))  # Changed size from 0.5 to 1.0
    
    # Update display
    pygame.display.flip()
    
    # Increment rotation angles with smaller values for slower rotation
    angleX += 0.002  # Changed from 0.005 to 0.002
    angleY += 0.001  # Changed from 0.003 to 0.001