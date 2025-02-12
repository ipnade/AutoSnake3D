import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random
from snake import Snake
from particle_system import ParticleSystem
from config import config

# Initialize Pygame and OpenGL
pygame.init()
display = (config['display']['width'], config['display']['height'])
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LESS)
gluPerspective(45, (display[0]/display[1]), 0.1, 500.0)  # Increased far plane from 150 to 500
glTranslatef(0.0, 0.0, -100)

clock = pygame.time.Clock()
pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, int(config['display']['vsync']))

def draw_grid():
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

def get_next_move(snake, food):
    head = snake.body[0]
    current_direction = snake.direction
    
    # Calculate direction to food
    food_direction = (
        food[0] - head[0],
        food[1] - head[1],
        food[2] - head[2]
    )
    
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
    
    # Find primary axis to move along
    abs_food_dir = [abs(x) for x in food_direction]
    primary_axis = abs_food_dir.index(max(abs_food_dir))
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
    
    # Try moves in priority order
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
    # Draw cube faces
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

def draw_sphere(position, radius=1.0, color=(1, 1, 1)):
    x, y, z = position
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    
    # Create a quadric object for the sphere
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric, radius, 32, 32)  # radius, slices, stacks
    
    glPopMatrix()

def draw_snake(snake_body):
    for i, segment in enumerate(snake_body):
        t = i / len(snake_body)
        
        x, y, z = segment
        offset = config['snake']['z_fighting_offset'] * i
        adjusted_pos = (x + offset, y + offset, z + offset)
        
        if config['snake']['colors']['grayscale']:
            if i == 0:
                color = config['snake']['colors']['grayscale_palette']['head']
                size = config['snake']['size']['head']
            else:
                size = config['snake']['size']['body']
                # For grayscale, we'll use a smooth gradient from light to dark
                brightness = 1.0 - (t * 0.7)  # Gradually darken from head to tail
                color = (brightness, brightness, brightness)
        else:
            if i == 0:
                color = config['snake']['colors']['head']
                size = config['snake']['size']['head']
            else:
                size = config['snake']['size']['body']
                pattern = i % len(config['snake']['colors']['body_pattern'])
                base_color = config['snake']['colors']['body_pattern'][pattern]
                
                if config['effects']['gradient_fade']:
                    color = tuple(c * (1 - t * 0.3) for c in base_color)
                else:
                    color = base_color
        
        draw_cube(adjusted_pos, size, color)

# Initialize game objects
snake = Snake()
food = spawn_food(snake.body)
game_speed = 25
last_move_time = 0
angleX = angleY = angleZ = 0
food_bob_time = 0
particle_system = ParticleSystem()

# Main game loop
while True:
    clock.tick(config['display']['fps'])
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:  # Press 'G' to toggle grayscale
                config['snake']['colors']['grayscale'] = not config['snake']['colors']['grayscale']

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluPerspective(45, (display[0]/display[1]), 0.1, 500.0)
    radius = 100
    
    # Calculate camera position
    camX = radius * math.cos(angleX)
    camY = radius * math.sin(angleY) * 0.5
    camZ = radius * math.sin(angleX)
    
    gluLookAt(camX, camY, camZ, 0, 0, 0, 0, 1, 0)
    
    current_time = pygame.time.get_ticks()
    
    if current_time - last_move_time >= game_speed:
        next_move = get_next_move(snake, food)
        snake.move(next_move)
        
        if snake.body[0] == food:
            snake.grow = True
            # Emit particles at food location
            particle_system.emit_particles(
                position=food,
                count=30,
                color=(1.0, 0.0, 0.0)  # Match food color
            )
            food = spawn_food(snake.body)
        
        if snake.check_collision():
            pygame.quit()
            quit()
            
        last_move_time = current_time

    draw_grid()
    
    # Bobbing effect for food
    food_bob_time += 0.1
    bob_offset = math.sin(food_bob_time) * 0.5
    
    draw_snake(snake.body)
    food_pos = (food[0], food[1] + bob_offset, food[2])
    draw_sphere(food_pos, 0.8, (1, 0, 0))
    
    # Update and draw particles
    if config['particles']['enabled']:
        particle_system.update(1.0/config['display']['fps'])
        particle_system.draw()
    
    pygame.display.flip()
    
    # Update camera rotation
    if config['effects']['smooth_camera']:
        angleX += config['camera']['rotation_speed']['x']
        angleY += config['camera']['rotation_speed']['y']